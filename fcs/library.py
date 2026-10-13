"""Private, versioned schedules, revocable snapshot links, and calendar export."""

import json
import secrets
from flask import Blueprint, jsonify, request, render_template, abort, Response
from .identity import db, now, current_user, require_user, json_body, text_field
from .services import catalog, owned
from .rules import validate_rule
from .calendar_export import calendar_text

library_api = Blueprint("library", __name__)


@library_api.errorhandler(ValueError)
def invalid(exc):
    return jsonify(error=str(exc)), 400


def validated_draft(data):
    source = catalog()
    if (
        not isinstance(data, dict)
        or data.get("version") != 2
        or data.get("term") != source["term"]
    ):
        raise ValueError("Save a version 2 draft from the current term")
    lookup = {s["id"]: s for s in source["sections"]}
    result = {"version": 2, "term": source["term"]}
    for field in ("section_ids", "shortlist_ids"):
        ids = data.get(field)
        if (
            not isinstance(ids, list)
            or len(ids) > 60
            or any(not isinstance(s, str) or s not in lookup for s in ids)
        ):
            raise ValueError("Saved drafts allow up to 60 current catalog sections")
        result[field] = list(dict.fromkeys(ids))
    credit_range = data.get("credit_range", {"min": 12, "max": 18})
    if (
        not isinstance(credit_range, dict)
        or any(type(credit_range.get(k)) not in (int, float) for k in ("min", "max"))
        or not 0 <= credit_range["min"] <= credit_range["max"] <= 30
    ):
        raise ValueError("Invalid saved credit range")
    result["credit_range"] = {"min": credit_range["min"], "max": credit_range["max"]}
    result["rules"] = validate_rule(
        data.get("rules", {"op": "and", "children": []}),
        {s["course_key"] for s in source["sections"]},
        allow_incomplete=True,
    )
    return result, [lookup[identity] for identity in result["section_ids"]]


@library_api.get("/api/v1/library")
@require_user
def library():
    with db().connect() as connection:
        schedules = [
            dict(row)
            for row in connection.execute(
                "SELECT id,name,term,version,created_at,updated_at FROM schedules WHERE owner_id=? ORDER BY updated_at DESC",
                (current_user()["id"],),
            )
        ]
    return jsonify(schedules=schedules)


@library_api.post("/api/v1/library")
@require_user
def save_schedule():
    data = json_body()
    name = text_field(data, "name", 1, 80)
    draft, sections = validated_draft(data.get("draft"))
    with db().connect() as connection:
        count = connection.execute(
            "SELECT count(*) FROM schedules WHERE owner_id=?", (current_user()["id"],)
        ).fetchone()[0]
        if count >= 50:
            raise ValueError("You can save up to 50 named schedules")
        timestamp = now()
        identity = connection.execute(
            "INSERT INTO schedules(owner_id,name,term,draft,sections,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
            (
                current_user()["id"],
                name,
                draft["term"],
                json.dumps(draft),
                json.dumps(sections),
                timestamp,
                timestamp,
            ),
        ).lastrowid
    return jsonify(id=identity, version=1), 201


@library_api.get("/api/v1/library/<int:identity>")
@require_user
def get_schedule(identity):
    with db().connect() as connection:
        row = owned(connection, "schedules", identity)
        result = dict(row)
        result["draft"] = json.loads(result["draft"])
        result["sections"] = json.loads(result["sections"])
        result["shares"] = [
            dict(r)
            for r in connection.execute(
                "SELECT token,created_at,revoked_at FROM shares WHERE schedule_id=? ORDER BY created_at DESC",
                (identity,),
            )
        ]
    return jsonify(**result)


@library_api.put("/api/v1/library/<int:identity>")
@require_user
def update_schedule(identity):
    data = json_body()
    name = text_field(data, "name", 1, 80)
    draft, sections = validated_draft(data.get("draft"))
    with db().connect() as connection:
        row = owned(connection, "schedules", identity)
        if type(data.get("version")) is not int or data["version"] != row["version"]:
            return jsonify(error="This schedule changed. Reload it before saving."), 409
        cursor = connection.execute(
            "UPDATE schedules SET name=?,draft=?,sections=?,version=version+1,updated_at=? WHERE id=? AND version=?",
            (
                name,
                json.dumps(draft),
                json.dumps(sections),
                now(),
                identity,
                data["version"],
            ),
        )
        if not cursor.rowcount:
            return jsonify(error="This schedule changed. Reload it before saving."), 409
    return jsonify(id=identity, version=row["version"] + 1)


@library_api.delete("/api/v1/library/<int:identity>")
@require_user
def delete_schedule(identity):
    with db().connect() as connection:
        owned(connection, "schedules", identity)
        connection.execute("DELETE FROM schedules WHERE id=?", (identity,))
    return jsonify(success=True)


@library_api.post("/api/v1/library/<int:identity>/shares")
@require_user
def create_share(identity):
    with db().connect() as connection:
        row = owned(connection, "schedules", identity)
        count = connection.execute(
            "SELECT count(*) FROM shares WHERE schedule_id=? AND revoked_at IS NULL",
            (identity,),
        ).fetchone()[0]
        if count >= 10:
            raise ValueError("Revoke a link before creating more than 10 active links")
        snapshot = {
            "name": row["name"],
            "term": row["term"],
            "sections": json.loads(row["sections"]),
        }
        token = secrets.token_urlsafe(24)
        connection.execute(
            "INSERT INTO shares(token,schedule_id,snapshot,created_at) VALUES(?,?,?,?)",
            (token, identity, json.dumps(snapshot), now()),
        )
    return jsonify(token=token, url=f"/s/{token}"), 201


@library_api.delete("/api/v1/shares/<token>")
@require_user
def revoke_share(token):
    with db().connect() as connection:
        row = connection.execute(
            "SELECT sh.token FROM shares sh JOIN schedules sc ON sc.id=sh.schedule_id WHERE token=? AND sc.owner_id=?",
            (token, current_user()["id"]),
        ).fetchone()
        if not row:
            abort(404)
        connection.execute(
            "UPDATE shares SET revoked_at=? WHERE token=?", (now(), token)
        )
    return jsonify(success=True)


def share_snapshot(token):
    with db().connect() as connection:
        row = connection.execute(
            "SELECT snapshot FROM shares WHERE token=? AND revoked_at IS NULL", (token,)
        ).fetchone()
    if not row:
        abort(
            404,
            description="This shared schedule is unavailable or its link was revoked",
        )
    return json.loads(row["snapshot"])


@library_api.get("/s/<token>")
def public_schedule(token):
    snapshot = share_snapshot(token)
    return render_template("shared.html", schedule=snapshot, token=token)


@library_api.get("/api/v1/shares/<token>")
def share_data(token):
    return jsonify(**share_snapshot(token))


@library_api.post("/api/v1/calendar-export")
def calendar_export():
    data = json_body()
    draft, sections = validated_draft(data.get("draft"))
    if not sections:
        raise ValueError("Add courses to your schedule before exporting")
    content = calendar_text(sections, data.get("start"), data.get("end"))
    return Response(
        content,
        mimetype="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="fcs-{draft["term"]}.ics"'
        },
    )
