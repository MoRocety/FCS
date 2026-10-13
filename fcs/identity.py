"""Session identity and same-origin write protection."""

import hmac
import re
import secrets
import time
import sqlite3
from datetime import datetime, timezone
from functools import wraps
from flask import Blueprint, current_app, request, session, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash

identity = Blueprint("identity", __name__, url_prefix="/api/v1")


def now():
    return datetime.now(timezone.utc).isoformat()


def db():
    return current_app.extensions["database"]


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def current_user():
    if "fcs_user" not in g:
        with db().connect() as connection:
            row = connection.execute(
                "SELECT id,username,display_name,role FROM users WHERE id=?",
                (session.get("user_id"),),
            ).fetchone()
        g.fcs_user = dict(row) if row else None
    return g.fcs_user


def require_user(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        if not current_user():
            return jsonify(error="Sign in to use this feature"), 401
        return function(*args, **kwargs)

    return wrapped


def json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    return data


def text_field(data, key, minimum=1, maximum=2000):
    value = data.get(key)
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        raise ValueError(
            f'{key.replace("_", " ").capitalize()} must contain {minimum}–{maximum} characters'
        )
    return value.strip()


def throttle(key, limit=12, seconds=900):
    timestamp = time.time()
    with db().connect() as connection:
        row = connection.execute(
            "SELECT count,started FROM throttle WHERE key=?", (key,)
        ).fetchone()
        if not row or timestamp - row["started"] >= seconds:
            connection.execute(
                "INSERT INTO throttle(key,count,started) VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET count=1,started=excluded.started",
                (key, timestamp),
            )
            return False
        connection.execute("UPDATE throttle SET count=count+1 WHERE key=?", (key,))
        return row["count"] >= limit


@identity.before_app_request
def protect_writes():
    if (
        request.method in ("POST", "PUT", "PATCH", "DELETE")
        and request.path.startswith("/api/v1/")
        and request.path != "/api/v1/schedules/generate"
    ):
        expected = session.get("csrf")
        provided = request.headers.get("X-CSRF-Token")
        if (
            not expected
            or not provided
            or not provided.isascii()
            or not hmac.compare_digest(expected, provided)
        ):
            return (
                jsonify(error="Your session changed. Reload the page and try again."),
                403,
            )


@identity.get("/me")
def me():
    return jsonify(user=current_user(), csrf_token=csrf_token())


def authenticated(row):
    session.clear()
    session["user_id"] = row["id"]
    g.pop("fcs_user", None)
    return jsonify(user=current_user(), csrf_token=csrf_token())


@identity.post("/accounts/register")
def register():
    if throttle(f"auth:{request.remote_addr}"):
        return jsonify(error="Too many attempts. Try again in 15 minutes."), 429
    try:
        data = json_body()
        username = text_field(data, "username", 3, 24).lower()
        display = text_field(data, "display_name", 2, 60)
        password = data.get("password")
        if not re.fullmatch(r"[a-z0-9_]+", username):
            raise ValueError("Username can contain letters, numbers, and underscores")
        if not isinstance(password, str) or not 10 <= len(password) <= 256:
            raise ValueError("Use a password between 10 and 256 characters")
        with db().connect() as connection:
            cursor = connection.execute(
                "INSERT INTO users(username,display_name,password_hash,created_at) VALUES(?,?,?,?)",
                (username, display, generate_password_hash(password), now()),
            )
            row = {"id": cursor.lastrowid}
        return authenticated(row), 201
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except sqlite3.IntegrityError:
        return jsonify(error="This username is already taken"), 409


@identity.post("/accounts/login")
def login():
    if throttle(f"auth:{request.remote_addr}"):
        return jsonify(error="Too many attempts. Try again in 15 minutes."), 429
    try:
        data = json_body()
        username = text_field(data, "username", 3, 24).lower()
        password = data.get("password")
        if not isinstance(password, str) or len(password) > 256:
            raise ValueError("Invalid password")
        with db().connect() as connection:
            row = connection.execute(
                "SELECT id,password_hash FROM users WHERE username=?", (username,)
            ).fetchone()
        valid = check_password_hash(
            row["password_hash"] if row else current_app.config["DUMMY_PASSWORD_HASH"],
            password,
        )
        if not row or not valid:
            return jsonify(error="Username or password is incorrect"), 401
        return authenticated(row)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400


@identity.post("/accounts/logout")
def logout():
    session.clear()
    g.pop("fcs_user", None)
    return jsonify(user=None, csrf_token=csrf_token())
