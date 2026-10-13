"""Catalog transition observations, per-user seat watches, and in-app notifications."""

from flask import Blueprint, jsonify
from .identity import db, now, current_user, require_user, json_body
from .services import catalog, owned

availability_api = Blueprint("availability", __name__)


@availability_api.errorhandler(ValueError)
def invalid(exc):
    return jsonify(error=str(exc)), 400


def observe_catalog(data):
    """Atomically record an observation and deliver each watched opening once."""
    with db().connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        head = connection.execute(
            "SELECT revision,source_mtime_ns FROM catalog_heads WHERE term=?",
            (data["term"],),
        ).fetchone()
        source_mtime = data.get("source_mtime_ns", 0)
        if head and source_mtime < head["source_mtime_ns"]:
            return
        if head and head["revision"] == data["revision"]:
            if source_mtime > head["source_mtime_ns"]:
                connection.execute(
                    "UPDATE catalog_heads SET source_mtime_ns=? WHERE term=?",
                    (source_mtime, data["term"]),
                )
            return
        timestamp = now()
        run = connection.execute(
            "INSERT INTO catalog_runs(term,revision,observed_at) VALUES(?,?,?)",
            (data["term"], data["revision"], timestamp),
        ).lastrowid
        before = {
            row["section_id"]: row["available"]
            for row in connection.execute(
                "SELECT section_id,available FROM current_seats WHERE term=?",
                (data["term"],),
            )
        }
        watchers = {}
        for row in connection.execute(
            "SELECT owner_id,section_id FROM watches WHERE term=?", (data["term"],)
        ):
            watchers.setdefault(row["section_id"], []).append(row["owner_id"])
        for section in data["sections"]:
            if (
                section["id"] in before
                and before[section["id"]] <= 0
                and section["available_seats"] > 0
            ):
                message = f"{section['department']} {section['number']} / {section['section']} now has {section['available_seats']} available seat(s) in the latest observed snapshot."
                for owner in watchers.get(section["id"], []):
                    connection.execute(
                        "INSERT OR IGNORE INTO notifications(owner_id,term,section_id,run_id,message,created_at) VALUES(?,?,?,?,?,?)",
                        (owner, data["term"], section["id"], run, message, timestamp),
                    )
        connection.execute("DELETE FROM current_seats WHERE term=?", (data["term"],))
        connection.executemany(
            "INSERT INTO current_seats(term,section_id,available) VALUES(?,?,?)",
            [(data["term"], s["id"], s["available_seats"]) for s in data["sections"]],
        )
        connection.execute(
            "INSERT INTO catalog_heads(term,revision,run_id,source_mtime_ns) VALUES(?,?,?,?) ON CONFLICT(term) DO UPDATE SET revision=excluded.revision,run_id=excluded.run_id,source_mtime_ns=excluded.source_mtime_ns",
            (data["term"], data["revision"], run, source_mtime),
        )


@availability_api.get("/api/v1/watches")
@require_user
def watches():
    source = catalog()
    observe_catalog(source)
    lookup = {s["id"]: s for s in source["sections"]}
    with db().connect() as connection:
        rows = [
            {
                **dict(row),
                "section": (
                    lookup.get(row["section_id"])
                    if row["term"] == source["term"]
                    else None
                ),
            }
            for row in connection.execute(
                "SELECT * FROM watches WHERE owner_id=? ORDER BY id DESC",
                (current_user()["id"],),
            )
        ]
    return jsonify(watches=rows)


@availability_api.post("/api/v1/watches")
@require_user
def watch():
    data = json_body()
    source = catalog()
    section_id = data.get("section_id")
    if (
        not isinstance(section_id, str)
        or data.get("term") != source["term"]
        or section_id not in {s["id"] for s in source["sections"]}
    ):
        raise ValueError("Choose a section from the current term")
    observe_catalog(source)
    with db().connect() as connection:
        count = connection.execute(
            "SELECT count(*) FROM watches WHERE owner_id=?", (current_user()["id"],)
        ).fetchone()[0]
        if (
            count >= 50
            and not connection.execute(
                "SELECT id FROM watches WHERE owner_id=? AND term=? AND section_id=?",
                (current_user()["id"], source["term"], section_id),
            ).fetchone()
        ):
            raise ValueError("You can watch up to 50 sections")
        connection.execute(
            "INSERT OR IGNORE INTO watches(owner_id,term,section_id,created_at) VALUES(?,?,?,?)",
            (current_user()["id"], source["term"], section_id, now()),
        )
    return jsonify(success=True), 201


@availability_api.delete("/api/v1/watches/<int:identity>")
@require_user
def unwatch(identity):
    with db().connect() as connection:
        owned(connection, "watches", identity)
        connection.execute("DELETE FROM watches WHERE id=?", (identity,))
    return jsonify(success=True)


@availability_api.get("/api/v1/notifications")
@require_user
def notifications():
    observe_catalog(catalog())
    with db().connect() as connection:
        rows = [
            dict(row)
            for row in connection.execute(
                "SELECT * FROM notifications WHERE owner_id=? ORDER BY id DESC LIMIT 100",
                (current_user()["id"],),
            )
        ]
        unread = connection.execute(
            "SELECT count(*) FROM notifications WHERE owner_id=? AND read_at IS NULL",
            (current_user()["id"],),
        ).fetchone()[0]
    return jsonify(notifications=rows, unread=unread)


@availability_api.post("/api/v1/notifications/read")
@require_user
def mark_read():
    with db().connect() as connection:
        connection.execute(
            "UPDATE notifications SET read_at=? WHERE owner_id=? AND read_at IS NULL",
            (now(), current_user()["id"]),
        )
    return jsonify(success=True)
