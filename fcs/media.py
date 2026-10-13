"""Public chronological campus feed with account-owned media and interactions."""

import json
from pathlib import Path
from flask import Blueprint, abort, current_app, jsonify, request, send_file
from .identity import (
    db,
    now,
    current_user,
    require_user,
    text_field,
    json_body,
    throttle,
)
from .services import catalog, subject, owned
from .community import limited_posts
from .media_processing import normalize, VIDEO_LIMIT

media_api = Blueprint("media", __name__)
CATEGORIES = ("campus", "study", "events", "clubs")


def prepare_upload():
    if request.path == "/api/v1/media/posts" and request.method == "POST":
        request.max_content_length = 33 * 1024 * 1024
        request.max_form_memory_size = 32 * 1024
        request.max_form_parts = 12


@media_api.errorhandler(FileNotFoundError)
def unavailable_catalog(exc):
    return (
        jsonify(error="The course catalog is unavailable. Try posting again later."),
        503,
    )


@media_api.errorhandler(ValueError)
def invalid(exc):
    return jsonify(error=str(exc)), 400


def cursor_arg(key):
    raw = request.args.get(key)
    if raw is None:
        return None
    if not raw.isascii() or not raw.isdecimal() or len(raw) > 18 or int(raw) < 1:
        raise ValueError("Invalid page cursor")
    return int(raw)


def published(connection, identity):
    row = connection.execute(
        "SELECT * FROM media_posts WHERE id=? AND status='published'", (identity,)
    ).fetchone()
    if not row:
        abort(404)
    return row


def asset_dict(row):
    result = dict(row)
    result.pop("filename", None)
    result["url"] = f"/api/v1/media/assets/{row['id']}"
    return result


def post_dict(connection, row):
    post = dict(row)
    post["assets"] = [
        asset_dict(asset)
        for asset in connection.execute(
            "SELECT * FROM media_assets WHERE post_id=? ORDER BY position", (row["id"],)
        )
    ]
    post["like_count"] = connection.execute(
        "SELECT count(*) FROM media_likes WHERE post_id=?", (row["id"],)
    ).fetchone()[0]
    post["comment_count"] = connection.execute(
        "SELECT count(*) FROM media_comments WHERE post_id=? AND status='published'",
        (row["id"],),
    ).fetchone()[0]
    post["liked"] = bool(
        current_user()
        and connection.execute(
            "SELECT 1 FROM media_likes WHERE post_id=? AND user_id=?",
            (row["id"], current_user()["id"]),
        ).fetchone()
    )
    return post


@media_api.get("/api/v1/media/posts")
def feed():
    before = cursor_arg("before")
    category, course = request.args.get("category", ""), request.args.get("course", "")
    if category and category not in CATEGORIES:
        raise ValueError("Choose a campus feed category")
    conditions, values = ["p.status='published'"], []
    for condition, value in (
        ("p.id<?", before),
        ("p.category=?", category),
        ("p.course_key=?", course),
    ):
        if value:
            conditions.append(condition)
            values.append(value)
    with db().connect() as connection:
        rows = connection.execute(
            "SELECT p.*,u.display_name,u.username FROM media_posts p JOIN users u ON u.id=p.owner_id WHERE "
            + " AND ".join(conditions)
            + " ORDER BY p.id DESC LIMIT 13",
            values,
        ).fetchall()
        posts = [post_dict(connection, row) for row in rows[:12]]
    return jsonify(posts=posts, next_before=posts[-1]["id"] if len(rows) > 12 else None)


@media_api.post("/api/v1/media/posts")
@require_user
def create_post():
    if throttle(f"media:{current_user()['id']}", limit=8, seconds=600):
        abort(429, description="Upload limit reached. Try again in ten minutes.")
    if not request.mimetype == "multipart/form-data":
        raise ValueError("Upload media using a multipart form")
    body = text_field(request.form, "body", 2, 2000)
    category = request.form.get("category", "campus")
    if category not in CATEGORIES:
        raise ValueError("Choose a campus feed category")
    course = request.form.get("course_key", "").strip()
    course_name = subject("course", course)["name"] if course else None
    term = catalog()["term"]
    files = request.files.getlist("media")
    if not 1 <= len(files) <= 4:
        raise ValueError("Choose one clip or up to four photos")
    try:
        descriptions = json.loads(request.form.get("descriptions", "[]"))
    except (ValueError, TypeError) as exc:
        raise ValueError("Describe each photo or clip") from exc
    if (
        not isinstance(descriptions, list)
        or len(descriptions) != len(files)
        or any(
            not isinstance(d, str) or not 2 <= len(d.strip()) <= 240
            for d in descriptions
        )
    ):
        raise ValueError("Describe each photo or clip in 2–240 characters")
    root, assets = Path(current_app.config["MEDIA_ROOT"]), []
    try:
        for file, description in zip(files, descriptions):
            raw = file.stream.read(VIDEO_LIMIT + 1)
            if not raw or len(raw) > VIDEO_LIMIT:
                raise ValueError("Each upload must be nonempty and 20 MB or smaller")
            assets.append(normalize(raw, root, description.strip()))
        if any(a["kind"] == "video" for a in assets) and len(assets) != 1:
            raise ValueError("Post one clip or up to four photos, rather than a mix")
        with db().connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            used = connection.execute(
                "SELECT coalesce(sum(a.bytes),0) FROM media_assets a JOIN media_posts p ON p.id=a.post_id WHERE p.owner_id=?",
                (current_user()["id"],),
            ).fetchone()[0]
            if (
                used + sum(a["bytes"] for a in assets)
                > current_app.config["MEDIA_USER_QUOTA"]
            ):
                raise ValueError("Your media storage limit has been reached")
            result = connection.execute(
                "INSERT INTO media_posts(owner_id,body,category,course_key,course_name,term,created_at) VALUES(?,?,?,?,?,?,?)",
                (
                    current_user()["id"],
                    body,
                    category,
                    course or None,
                    course_name,
                    term,
                    now(),
                ),
            )
            identity = result.lastrowid
            for position, asset in enumerate(assets):
                connection.execute(
                    "INSERT INTO media_assets(post_id,filename,kind,mime,description,bytes,width,height,duration,position) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        identity,
                        asset["filename"],
                        asset["kind"],
                        asset["mime"],
                        asset["description"],
                        asset["bytes"],
                        asset["width"],
                        asset["height"],
                        asset["duration"],
                        position,
                    ),
                )
        return jsonify(id=identity), 201
    except Exception:
        for asset in assets:
            (root / asset["filename"]).unlink(missing_ok=True)
        raise


@media_api.get("/api/v1/media/assets/<int:identity>")
def asset(identity):
    with db().connect() as connection:
        row = connection.execute(
            "SELECT a.* FROM media_assets a JOIN media_posts p ON p.id=a.post_id WHERE a.id=? AND p.status='published'",
            (identity,),
        ).fetchone()
    if not row:
        abort(404)
    path = Path(current_app.config["MEDIA_ROOT"]) / row["filename"]
    if not path.is_file():
        abort(404)
    response = send_file(path, mimetype=row["mime"], conditional=True, max_age=0)
    # Every request must re-check moderation, including cached and byte-range playback.
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'none'; sandbox"
    return response


@media_api.delete("/api/v1/media/posts/<int:identity>")
@require_user
def remove_post(identity):
    with db().connect() as connection:
        owned(connection, "media_posts", identity)
        connection.execute(
            "UPDATE media_posts SET status='deleted' WHERE id=?", (identity,)
        )
    return jsonify(success=True)


@media_api.route("/api/v1/media/posts/<int:identity>/like", methods=["PUT", "DELETE"])
@require_user
def like(identity):
    with db().connect() as connection:
        published(connection, identity)
        if request.method == "PUT":
            connection.execute(
                "INSERT OR IGNORE INTO media_likes(post_id,user_id) VALUES(?,?)",
                (identity, current_user()["id"]),
            )
        else:
            connection.execute(
                "DELETE FROM media_likes WHERE post_id=? AND user_id=?",
                (identity, current_user()["id"]),
            )
        count = connection.execute(
            "SELECT count(*) FROM media_likes WHERE post_id=?", (identity,)
        ).fetchone()[0]
    return jsonify(like_count=count, liked=request.method == "PUT")


@media_api.get("/api/v1/media/posts/<int:identity>/comments")
def comments(identity):
    after = cursor_arg("after") or 0
    with db().connect() as connection:
        published(connection, identity)
        rows = connection.execute(
            "SELECT c.*,u.display_name,u.username FROM media_comments c JOIN users u ON u.id=c.owner_id WHERE c.post_id=? AND c.status='published' AND c.id>? ORDER BY c.id LIMIT 51",
            (identity, after),
        ).fetchall()
    return jsonify(
        comments=[dict(row) for row in rows[:50]],
        next_after=rows[49]["id"] if len(rows) > 50 else None,
    )


@media_api.post("/api/v1/media/posts/<int:identity>/comments")
@require_user
def add_comment(identity):
    limited_posts()
    body = text_field(json_body(), "body", 2, 2000)
    with db().connect() as connection:
        published(connection, identity)
        result = connection.execute(
            "INSERT INTO media_comments(post_id,owner_id,body,created_at) VALUES(?,?,?,?)",
            (identity, current_user()["id"], body, now()),
        )
    return jsonify(id=result.lastrowid), 201


@media_api.delete("/api/v1/media/comments/<int:identity>")
@require_user
def remove_comment(identity):
    with db().connect() as connection:
        owned(connection, "media_comments", identity)
        connection.execute(
            "UPDATE media_comments SET status='deleted' WHERE id=?", (identity,)
        )
    return jsonify(success=True)
