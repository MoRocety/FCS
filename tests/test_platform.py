import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app import create_app
from fcs.calendar_export import calendar_text


class PlatformTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.a = self.app.test_client()
        self.b = self.app.test_client()
        self.source = self.app.extensions["catalog"].load()
        self.section = self.source["sections"][0]
        self.register(self.a, "student_a")
        self.register(self.b, "student_b")

    def call(self, client, method, path, data=None):
        token = client.get("/api/v1/me").json["csrf_token"]
        return client.open(
            "/api/v1" + path, method=method, json=data, headers={"X-CSRF-Token": token}
        )

    def register(self, client, username):
        result = self.call(
            client,
            "POST",
            "/accounts/register",
            {
                "username": username,
                "display_name": username,
                "password": "test-password-long",
            },
        )
        self.assertEqual(result.status_code, 201)
        return result.json["user"]

    def draft(self, section=None):
        identity = (section or self.section)["id"]
        return {
            "version": 2,
            "term": self.source["term"],
            "section_ids": [identity],
            "shortlist_ids": [identity],
            "rules": {"op": "and", "children": []},
            "credit_range": {"min": 3, "max": 18},
        }

    def schedule(self):
        response = self.call(
            self.a,
            "POST",
            "/library",
            {"name": "Morning option", "draft": self.draft()},
        )
        self.assertEqual(response.status_code, 201)
        return response.json["id"]

    def review(self, client=None):
        response = self.call(
            client or self.a,
            "PUT",
            "/reviews",
            {
                "kind": "course",
                "subject_key": self.section["course_key"],
                "rating": 4,
                "difficulty": 3,
                "body": "Test review describing a useful course learning experience.",
            },
        )
        self.assertEqual(response.status_code, 200)
        return self.a.get(
            f"/api/v1/reviews?kind=course&subject={self.section['course_key']}"
        ).json["reviews"][0]["id"]

    def thread(self, kind="discussion"):
        response = self.call(
            self.a,
            "POST",
            "/threads",
            {
                "course_key": self.section["course_key"],
                "kind": kind,
                "title": "A useful course question",
                "body": "Test discussion content about preparing for this course.",
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.json["id"]

    def test_csrf_and_anonymous_private_boundaries(self):
        anonymous = self.app.test_client()
        self.assertEqual(anonymous.get("/api/v1/library").status_code, 401)
        self.assertEqual(
            self.a.post("/api/v1/library", json={"name": "bad"}).status_code, 403
        )
        self.assertEqual(
            self.call(
                anonymous,
                "POST",
                "/watches",
                {"term": self.source["term"], "section_id": self.section["id"]},
            ).status_code,
            401,
        )
        self.assertEqual(
            self.a.post(
                "/api/v1/library", json={"name": "bad"}, headers={"X-CSRF-Token": "é"}
            ).status_code,
            403,
        )
        self.assertEqual(anonymous.get("/campus").status_code, 200)

    def test_login_logout_and_no_role_escalation(self):
        self.assertEqual(self.a.get("/api/v1/me").json["user"]["role"], "student")
        self.assertEqual(self.a.get("/api/v1/moderation/reports").status_code, 403)
        self.call(self.a, "POST", "/accounts/logout")
        self.assertIsNone(self.a.get("/api/v1/me").json["user"])
        self.assertEqual(
            self.call(
                self.a,
                "POST",
                "/accounts/login",
                {"username": "student_a", "password": "wrong"},
            ).status_code,
            401,
        )
        self.assertEqual(
            self.call(
                self.a,
                "POST",
                "/accounts/login",
                {"username": "student_a", "password": "test-password-long"},
            ).status_code,
            200,
        )

    def test_library_ownership_and_version_conflicts(self):
        identity = self.schedule()
        self.assertEqual(self.b.get(f"/api/v1/library/{identity}").status_code, 404)
        self.assertEqual(
            self.call(self.b, "DELETE", f"/library/{identity}").status_code, 404
        )
        data = {"name": "Renamed option", "draft": self.draft(), "version": 1}
        self.assertEqual(
            self.call(self.a, "PUT", f"/library/{identity}", data).status_code, 200
        )
        self.assertEqual(
            self.call(self.a, "PUT", f"/library/{identity}", data).status_code, 409
        )
        saved = self.a.get(f"/api/v1/library/{identity}").json
        self.assertEqual(saved["version"], 2)
        self.assertEqual(saved["draft"]["credit_range"], {"min": 3, "max": 18})

    def test_share_is_snapshot_private_preferences_excluded_and_revocable(self):
        identity = self.schedule()
        share = self.call(self.a, "POST", f"/library/{identity}/shares").json
        token = share["token"]
        anonymous = self.app.test_client()
        snapshot = anonymous.get(f"/api/v1/shares/{token}").json
        self.assertEqual(snapshot["sections"][0]["id"], self.section["id"])
        self.assertNotIn("rules", snapshot)
        self.assertNotIn("owner_id", snapshot)
        self.assertNotIn("draft", snapshot)
        self.call(
            self.a,
            "PUT",
            f"/library/{identity}",
            {
                "name": "New name",
                "draft": self.draft(self.source["sections"][1]),
                "version": 1,
            },
        )
        self.assertEqual(
            anonymous.get(f"/api/v1/shares/{token}").json["name"], "Morning option"
        )
        self.assertEqual(
            self.call(self.b, "DELETE", f"/shares/{token}").status_code, 404
        )
        self.assertEqual(
            self.call(self.a, "DELETE", f"/shares/{token}").status_code, 200
        )
        self.assertEqual(anonymous.get(f"/api/v1/shares/{token}").status_code, 404)
        self.assertEqual(anonymous.get(f"/s/{token}").status_code, 404)

    def test_deleting_saved_draft_revokes_links(self):
        identity = self.schedule()
        token = self.call(self.a, "POST", f"/library/{identity}/shares").json["token"]
        self.call(self.a, "DELETE", f"/library/{identity}")
        self.assertEqual(self.b.get(f"/api/v1/shares/{token}").status_code, 404)

    def test_library_rejects_unknown_and_preserves_incomplete_editor(self):
        draft = self.draft()
        draft["section_ids"] = ["missing"]
        self.assertEqual(
            self.call(
                self.a, "POST", "/library", {"name": "bad", "draft": draft}
            ).status_code,
            400,
        )
        draft = self.draft()
        draft["rules"] = {
            "op": "and",
            "children": [{"op": "course", "course_key": "", "present": True}],
        }
        self.assertEqual(
            self.call(
                self.a, "POST", "/library", {"name": "Unfinished plan", "draft": draft}
            ).status_code,
            201,
        )
        draft["credit_range"] = {"min": float("nan"), "max": 18}
        self.assertEqual(
            self.call(
                self.a, "POST", "/library", {"name": "bad", "draft": draft}
            ).status_code,
            400,
        )

    def test_review_upsert_and_cross_user_delete(self):
        identity = self.review()
        self.review()
        data = self.a.get(
            f"/api/v1/reviews?kind=course&subject={self.section['course_key']}"
        ).json
        self.assertEqual(data["summary"]["count"], 1)
        self.assertEqual(
            self.call(self.b, "DELETE", f"/reviews/{identity}").status_code, 404
        )
        self.review(self.b)
        data = self.a.get(
            f"/api/v1/reviews?kind=course&subject={self.section['course_key']}"
        ).json
        self.assertEqual(data["summary"]["count"], 2)

    def test_instructor_review_and_invalid_ratings(self):
        teacher = self.a.get("/api/v1/community/subjects").json["instructor"][0]
        payload = {
            "kind": "instructor",
            "subject_key": teacher["key"],
            "rating": 5,
            "difficulty": 2,
            "body": "Test teacher feedback about clarity and useful learning support.",
        }
        self.assertEqual(self.call(self.a, "PUT", "/reviews", payload).status_code, 200)
        payload["rating"] = True
        self.assertEqual(self.call(self.a, "PUT", "/reviews", payload).status_code, 400)

    def test_reporting_moderation_and_republication_protection(self):
        identity = self.review()
        report = self.call(
            self.b,
            "POST",
            "/reports",
            {
                "target_type": "review",
                "target_id": identity,
                "reason": "Test moderation report for this example content.",
            },
        )
        self.assertEqual(report.status_code, 201)
        self.assertEqual(self.a.get("/api/v1/moderation/reports").status_code, 403)
        user_id = self.b.get("/api/v1/me").json["user"]["id"]
        with self.app.extensions["database"].connect() as connection:
            connection.execute(
                "UPDATE users SET role='moderator' WHERE id=?", (user_id,)
            )
        report_id = self.b.get("/api/v1/moderation/reports").json["reports"][0]["id"]
        self.assertEqual(
            self.call(
                self.b,
                "POST",
                f"/moderation/reports/{report_id}",
                {
                    "action": "hide",
                    "note": "Test moderation decision with an audit record.",
                },
            ).status_code,
            200,
        )
        self.assertEqual(
            self.a.get(
                f"/api/v1/reviews?kind=course&subject={self.section['course_key']}"
            ).json["summary"]["count"],
            0,
        )
        self.call(self.a, "DELETE", f"/reviews/{identity}")
        self.assertEqual(
            self.call(
                self.a,
                "PUT",
                "/reviews",
                {
                    "kind": "course",
                    "subject_key": self.section["course_key"],
                    "rating": 4,
                    "difficulty": 3,
                    "body": "Attempt to republish a moderated example review.",
                },
            ).status_code,
            409,
        )
        with self.app.extensions["database"].connect() as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT count(*) FROM moderation_actions"
                ).fetchone()[0],
                1,
            )

    def test_thread_comments_membership_and_visibility(self):
        identity = self.thread("study_group")
        self.assertEqual(
            self.call(self.b, "POST", f"/threads/{identity}/membership").status_code,
            200,
        )
        self.call(self.b, "POST", f"/threads/{identity}/membership")
        self.assertEqual(
            len(self.a.get(f"/api/v1/threads/{identity}").json["members"]), 1
        )
        self.call(
            self.b,
            "POST",
            f"/threads/{identity}/comments",
            {"body": "A useful test reply."},
        )
        comment = self.a.get(f"/api/v1/threads/{identity}").json["comments"][0]
        self.assertEqual(
            self.call(self.a, "DELETE", f'/comments/{comment["id"]}').status_code, 404
        )
        self.assertEqual(
            self.call(self.b, "DELETE", f'/comments/{comment["id"]}').status_code, 200
        )
        self.call(self.b, "DELETE", f"/threads/{identity}/membership")
        self.assertEqual(
            len(self.a.get(f"/api/v1/threads/{identity}").json["members"]), 0
        )
        self.call(self.a, "DELETE", f"/threads/{identity}")
        self.assertEqual(self.b.get(f"/api/v1/threads/{identity}").status_code, 404)
        self.assertEqual(
            self.call(
                self.b,
                "POST",
                f"/threads/{identity}/comments",
                {"body": "After deletion"},
            ).status_code,
            404,
        )

    def test_bad_report_target_is_validation_error(self):
        response = self.call(
            self.a,
            "POST",
            "/reports",
            {"target_type": [], "target_id": 1, "reason": "Invalid target example"},
        )
        self.assertEqual(response.status_code, 400)

    def test_no_membership_on_regular_discussion(self):
        self.assertEqual(
            self.call(
                self.b, "POST", f"/threads/{self.thread()}/membership"
            ).status_code,
            404,
        )

    def changed_catalog(self, available, revision, missing=False):
        data = copy.deepcopy(self.source)
        data["revision"] = revision
        if missing:
            data["sections"] = data["sections"][1:]
        else:
            data["sections"][0]["available_seats"] = available
        return data

    def test_seat_transition_deduplication_reopening_and_account_isolation(self):
        with patch.object(
            self.app.extensions["catalog"],
            "load",
            return_value=self.changed_catalog(0, "closed"),
        ):
            self.assertEqual(
                self.call(
                    self.a,
                    "POST",
                    "/watches",
                    {"term": self.source["term"], "section_id": self.section["id"]},
                ).status_code,
                201,
            )
        with patch.object(
            self.app.extensions["catalog"],
            "load",
            return_value=self.changed_catalog(3, "open"),
        ):
            first = self.a.get("/api/v1/notifications").json
            self.assertEqual(first["unread"], 1)
            self.assertEqual(
                len(self.a.get("/api/v1/notifications").json["notifications"]), 1
            )
            self.assertEqual(self.b.get("/api/v1/notifications").json["unread"], 0)
        with patch.object(
            self.app.extensions["catalog"],
            "load",
            return_value=self.changed_catalog(0, "closed"),
        ):
            self.a.get("/api/v1/notifications")
        with patch.object(
            self.app.extensions["catalog"],
            "load",
            return_value=self.changed_catalog(3, "open"),
        ):
            self.assertEqual(self.a.get("/api/v1/notifications").json["unread"], 2)
            self.call(self.a, "POST", "/notifications/read")
            self.assertEqual(self.a.get("/api/v1/notifications").json["unread"], 0)

    def test_stale_catalog_reader_cannot_create_false_reopening(self):
        closed = self.changed_catalog(0, "closed")
        closed["source_mtime_ns"] = 10
        opened = self.changed_catalog(3, "open")
        opened["source_mtime_ns"] = 20
        with patch.object(self.app.extensions["catalog"], "load", return_value=closed):
            self.call(
                self.a,
                "POST",
                "/watches",
                {"term": self.source["term"], "section_id": self.section["id"]},
            )
        with patch.object(self.app.extensions["catalog"], "load", return_value=opened):
            self.assertEqual(self.a.get("/api/v1/notifications").json["unread"], 1)
        with patch.object(self.app.extensions["catalog"], "load", return_value=closed):
            self.a.get("/api/v1/notifications")
        with patch.object(self.app.extensions["catalog"], "load", return_value=opened):
            self.assertEqual(self.a.get("/api/v1/notifications").json["unread"], 1)

    def test_version_one_catalog_heads_upgrade_without_losing_rows(self):
        import sqlite3
        from fcs.database import Database

        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "old.sqlite3")
            with sqlite3.connect(path) as connection:
                connection.executescript(
                    "CREATE TABLE catalog_runs(id INTEGER PRIMARY KEY,term TEXT,revision TEXT,observed_at TEXT); CREATE TABLE catalog_heads(term TEXT PRIMARY KEY,revision TEXT,run_id INTEGER REFERENCES catalog_runs(id)); INSERT INTO catalog_runs VALUES(1,'2027SP','older','2026-10-13'); INSERT INTO catalog_heads VALUES('2027SP','older',1); PRAGMA user_version=1;"
                )
            connection.close()
            database = Database(path)
            with database.connect() as connection:
                self.assertEqual(
                    connection.execute("PRAGMA user_version").fetchone()[0], 3
                )
                self.assertEqual(
                    connection.execute("SELECT revision FROM catalog_heads").fetchone()[
                        0
                    ],
                    "older",
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT source_mtime_ns FROM catalog_heads"
                    ).fetchone()[0],
                    0,
                )

    def test_watch_open_section_does_not_backdate_alert_and_ownership(self):
        self.call(
            self.a,
            "POST",
            "/watches",
            {"term": self.source["term"], "section_id": self.section["id"]},
        )
        self.assertEqual(self.a.get("/api/v1/notifications").json["unread"], 0)
        identity = self.a.get("/api/v1/watches").json["watches"][0]["id"]
        self.assertEqual(
            self.call(self.b, "DELETE", f"/watches/{identity}").status_code, 404
        )
        self.assertEqual(
            self.call(self.a, "DELETE", f"/watches/{identity}").status_code, 200
        )
        self.assertEqual(
            self.call(
                self.a,
                "POST",
                "/watches",
                {"term": self.source["term"], "section_id": []},
            ).status_code,
            400,
        )

    def test_calendar_export_and_date_validation(self):
        payload = {"draft": self.draft(), "start": "2027-01-01", "end": "2027-05-31"}
        response = self.call(self.a, "POST", "/calendar-export", payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("BEGIN:VCALENDAR", response.text)
        self.assertIn("TZID:Asia/Karachi", response.text)
        self.assertIn("RRULE:FREQ=WEEKLY;", response.text)
        self.assertTrue(
            all(len(line.encode()) <= 75 for line in response.text.split("\r\n"))
        )
        payload["end"] = "2026-01-01"
        self.assertEqual(
            self.call(self.a, "POST", "/calendar-export", payload).status_code, 400
        )

    def test_file_database_persists_accounts(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "test.sqlite3")
            app = create_app({"TESTING": True, "DATABASE": path})
            client = app.test_client()
            self.register(client, "persistent_user")
            fresh = create_app({"TESTING": True, "DATABASE": path}).test_client()
            self.assertEqual(
                self.call(
                    fresh,
                    "POST",
                    "/accounts/login",
                    {"username": "persistent_user", "password": "test-password-long"},
                ).status_code,
                200,
            )


class CalendarTests(unittest.TestCase):
    def test_alternate_meetings_weekends_and_escaping(self):
        section = {
            "id": "CS:101:A",
            "department": "CS",
            "number": "101",
            "section": "A",
            "name": "Course, with; punctuation\\",
            "instructor": "Teacher\nAnother line",
            "meetings": [
                {"days": ["M"], "start": "09:00", "end": "10:00", "room": "A1"},
                {"days": ["S"], "start": "14:00", "end": "16:00", "room": "Lab"},
            ],
        }
        text = calendar_text([section], "2027-01-01", "2027-01-31")
        self.assertEqual(text.count("BEGIN:VEVENT"), 2)
        self.assertIn("20270102T140000", text)
        self.assertIn("Course\\, with\\; punctuation\\\\", text)
        self.assertIn("Teacher\\nAnother line", text)
