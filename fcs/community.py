"""Course feedback, discussions, study groups, and moderation."""

from flask import Blueprint, jsonify, request, abort
from .identity import (
    db,
    now,
    current_user,
    require_user,
    json_body,
    text_field,
    throttle,
)
from .services import catalog, subjects, subject, owned

community_api = Blueprint("community", __name__)
REPORT_TARGETS = {
    "review": "reviews",
    "thread": "threads",
    "comment": "comments",
    "media_post": "media_posts",
    "media_comment": "media_comments",
}


def limited_posts():
    if throttle(f"posts:{current_user()['id']}", limit=30, seconds=300):
        abort(429, description="Too many posts. Try again in a few minutes.")


def public_row(row):
    return dict(row)


@community_api.errorhandler(ValueError)
def invalid(exc):
    return jsonify(error=str(exc)), 400


@community_api.get("/api/v1/community/subjects")
def get_subjects():
    result = subjects(catalog())
    with db().connect() as connection:
        stats = {
            (row["kind"], row["subject_key"]): dict(row)
            for row in connection.execute(
                "SELECT kind,subject_key,count(*) AS review_count,avg(rating) AS rating FROM reviews WHERE status='published' GROUP BY kind,subject_key"
            )
        }
    for kind, items in result.items():
        for item in items:
            stat = stats.get((kind, item["key"]), {})
            item.update(
                review_count=stat.get("review_count", 0),
                rating=round(stat["rating"], 1) if stat.get("rating") else None,
            )
    return jsonify(**result, term=catalog()["term"], term_name=catalog()["term_name"])


@community_api.get("/api/v1/reviews")
def reviews():
    kind, key = request.args.get("kind", "course"), request.args.get("subject", "")
    item = subject(kind, key)
    with db().connect() as connection:
        rows = connection.execute(
            "SELECT r.*,u.display_name,u.username FROM reviews r JOIN users u ON u.id=r.owner_id WHERE kind=? AND subject_key=? AND status='published' ORDER BY r.id DESC LIMIT 50",
            (kind, key),
        ).fetchall()
        aggregate = connection.execute(
            "SELECT count(*) AS count,avg(rating) AS rating,avg(difficulty) AS difficulty FROM reviews WHERE kind=? AND subject_key=? AND status='published'",
            (kind, key),
        ).fetchone()
    return jsonify(
        subject=item, reviews=[public_row(row) for row in rows], summary=dict(aggregate)
    )


@community_api.put("/api/v1/reviews")
@require_user
def write_review():
    limited_posts()
    data = json_body()
    kind, key = data.get("kind"), data.get("subject_key")
    item = subject(kind, key)
    body = text_field(data, "body", 20, 2000)
    rating, difficulty = data.get("rating"), data.get("difficulty")
    if (
        type(rating) is not int
        or type(difficulty) is not int
        or not 1 <= rating <= 5
        or not 1 <= difficulty <= 5
    ):
        raise ValueError("Choose ratings from 1 to 5")
    timestamp = now()
    with db().connect() as connection:
        previous = connection.execute(
            "SELECT status FROM reviews WHERE owner_id=? AND kind=? AND subject_key=? AND term=?",
            (current_user()["id"], kind, key, catalog()["term"]),
        ).fetchone()
        if previous and previous["status"] == "hidden":
            return (
                jsonify(
                    error="This review is under moderation. Contact the moderator before republishing."
                ),
                409,
            )
        connection.execute(
            "INSERT INTO reviews(owner_id,kind,subject_key,subject_name,term,rating,difficulty,body,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(owner_id,kind,subject_key,term) DO UPDATE SET rating=excluded.rating,difficulty=excluded.difficulty,body=excluded.body,updated_at=excluded.updated_at,status='published'",
            (
                current_user()["id"],
                kind,
                key,
                item["name"],
                catalog()["term"],
                rating,
                difficulty,
                body,
                timestamp,
                timestamp,
            ),
        )
    return jsonify(success=True)


@community_api.delete("/api/v1/reviews/<int:identity>")
@require_user
def remove_review(identity):
    with db().connect() as connection:
        owned(connection, "reviews", identity)
        connection.execute(
            "UPDATE reviews SET status=CASE WHEN status='hidden' THEN 'hidden' ELSE 'deleted' END WHERE id=?",
            (identity,),
        )
    return jsonify(success=True)


@community_api.get("/api/v1/threads")
def threads():
    key = request.args.get("course", "")
    subject("course", key)
    with db().connect() as connection:
        rows = connection.execute(
            "SELECT t.*,u.display_name,u.username,(SELECT count(*) FROM comments c WHERE c.thread_id=t.id AND c.status='published') AS comments_count,(SELECT count(*) FROM memberships m WHERE m.thread_id=t.id) AS members_count FROM threads t JOIN users u ON u.id=t.owner_id WHERE course_key=? AND term=? AND t.status='published' ORDER BY id DESC LIMIT 50",
            (key, catalog()["term"]),
        ).fetchall()
    return jsonify(threads=[dict(row) for row in rows])


@community_api.post("/api/v1/threads")
@require_user
def write_thread():
    limited_posts()
    data = json_body()
    subject("course", data.get("course_key"))
    kind = data.get("kind", "discussion")
    if kind not in ("discussion", "study_group"):
        raise ValueError("Choose discussion or study group")
    title, body = text_field(data, "title", 5, 120), text_field(data, "body", 10, 4000)
    with db().connect() as connection:
        identity = connection.execute(
            "INSERT INTO threads(owner_id,course_key,term,kind,title,body,created_at) VALUES(?,?,?,?,?,?,?)",
            (
                current_user()["id"],
                data["course_key"],
                catalog()["term"],
                kind,
                title,
                body,
                now(),
            ),
        ).lastrowid
    return jsonify(id=identity), 201


@community_api.get("/api/v1/threads/<int:identity>")
def get_thread(identity):
    with db().connect() as connection:
        thread = connection.execute(
            "SELECT t.*,u.display_name,u.username FROM threads t JOIN users u ON u.id=t.owner_id WHERE t.id=? AND t.status='published'",
            (identity,),
        ).fetchone()
        if not thread:
            abort(404)
        comments = connection.execute(
            "SELECT c.*,u.display_name,u.username FROM comments c JOIN users u ON u.id=c.owner_id WHERE thread_id=? AND status='published' ORDER BY id LIMIT 100",
            (identity,),
        ).fetchall()
        members = connection.execute(
            "SELECT u.id,u.display_name,u.username FROM memberships m JOIN users u ON u.id=m.user_id WHERE thread_id=? ORDER BY joined_at",
            (identity,),
        ).fetchall()
    return jsonify(
        thread=dict(thread),
        comments=[dict(c) for c in comments],
        members=[dict(m) for m in members],
    )


@community_api.post("/api/v1/threads/<int:identity>/comments")
@require_user
def comment(identity):
    limited_posts()
    body = text_field(json_body(), "body", 2, 2000)
    with db().connect() as connection:
        if not connection.execute(
            "SELECT id FROM threads WHERE id=? AND status='published'", (identity,)
        ).fetchone():
            abort(404)
        connection.execute(
            "INSERT INTO comments(thread_id,owner_id,body,created_at) VALUES(?,?,?,?)",
            (identity, current_user()["id"], body, now()),
        )
    return jsonify(success=True), 201


@community_api.delete("/api/v1/comments/<int:identity>")
@require_user
def remove_comment(identity):
    with db().connect() as connection:
        owned(connection, "comments", identity)
        connection.execute(
            "UPDATE comments SET status='deleted' WHERE id=?", (identity,)
        )
    return jsonify(success=True)


@community_api.delete("/api/v1/threads/<int:identity>")
@require_user
def remove_thread(identity):
    with db().connect() as connection:
        owned(connection, "threads", identity)
        connection.execute(
            "UPDATE threads SET status='deleted' WHERE id=?", (identity,)
        )
    return jsonify(success=True)


@community_api.route(
    "/api/v1/threads/<int:identity>/membership", methods=["POST", "DELETE"]
)
@require_user
def membership(identity):
    with db().connect() as connection:
        if not connection.execute(
            "SELECT id FROM threads WHERE id=? AND kind='study_group' AND status='published'",
            (identity,),
        ).fetchone():
            abort(404)
        if request.method == "POST":
            connection.execute(
                "INSERT OR IGNORE INTO memberships(thread_id,user_id,joined_at) VALUES(?,?,?)",
                (identity, current_user()["id"], now()),
            )
        else:
            connection.execute(
                "DELETE FROM memberships WHERE thread_id=? AND user_id=?",
                (identity, current_user()["id"]),
            )
    return jsonify(success=True)


@community_api.post("/api/v1/reports")
@require_user
def report():
    limited_posts()
    data = json_body()
    target_type, identity = data.get("target_type"), data.get("target_id")
    table = REPORT_TARGETS.get(target_type) if isinstance(target_type, str) else None
    if not table or type(identity) is not int:
        raise ValueError("Invalid report target")
    reason = text_field(data, "reason", 5, 500)
    with db().connect() as connection:
        if not connection.execute(
            f"SELECT id FROM {table} WHERE id=? AND status='published'", (identity,)
        ).fetchone():
            abort(404)
        connection.execute(
            "INSERT OR IGNORE INTO reports(owner_id,target_type,target_id,reason,created_at) VALUES(?,?,?,?,?)",
            (current_user()["id"], target_type, identity, reason, now()),
        )
    return jsonify(success=True), 201


def require_moderator():
    if not current_user() or current_user()["role"] != "moderator":
        abort(403)


@community_api.get("/api/v1/moderation/reports")
@require_user
def moderation_reports():
    require_moderator()
    with db().connect() as connection:
        rows = [
            dict(row)
            for row in connection.execute(
                "SELECT r.*,u.display_name FROM reports r JOIN users u ON u.id=r.owner_id WHERE r.status='open' ORDER BY r.id LIMIT 100"
            )
        ]
        for row in rows:
            table = REPORT_TARGETS[row["target_type"]]
            target = connection.execute(
                f"SELECT * FROM {table} WHERE id=?", (row["target_id"],)
            ).fetchone()
            row["target"] = dict(target) if target else None
            if target and row["target_type"] == "media_post":
                row["target"]["assets"] = [
                    {
                        "url": f"/api/v1/media/assets/{asset['id']}",
                        "kind": asset["kind"],
                        "description": asset["description"],
                    }
                    for asset in connection.execute(
                        "SELECT id,kind,description FROM media_assets WHERE post_id=? ORDER BY position",
                        (target["id"],),
                    )
                ]
    return jsonify(reports=rows)


@community_api.post("/api/v1/moderation/reports/<int:identity>")
@require_user
def moderate(identity):
    require_moderator()
    data = json_body()
    action = data.get("action")
    if action not in ("hide", "dismiss"):
        raise ValueError("Choose hide or dismiss")
    note = text_field(data, "note", 5, 500)
    with db().connect() as connection:
        row = connection.execute(
            "SELECT * FROM reports WHERE id=? AND status='open'", (identity,)
        ).fetchone()
        if not row:
            abort(404)
        if action == "hide":
            table = REPORT_TARGETS[row["target_type"]]
            connection.execute(
                f"UPDATE {table} SET status='hidden' WHERE id=?", (row["target_id"],)
            )
            connection.execute(
                "UPDATE reports SET status='resolved' WHERE target_type=? AND target_id=?",
                (row["target_type"], row["target_id"]),
            )
        else:
            connection.execute(
                "UPDATE reports SET status='dismissed' WHERE id=?", (identity,)
            )
        connection.execute(
            "INSERT INTO moderation_actions(moderator_id,report_id,action,note,created_at) VALUES(?,?,?,?,?)",
            (current_user()["id"], identity, action, note, now()),
        )
    return jsonify(success=True)
