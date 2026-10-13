import io
import json
import tempfile
import unittest
import subprocess
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import imageio_ffmpeg
from app import create_app


def photo():
    output = io.BytesIO()
    image = Image.new("RGB", (128, 96), "#869a63")
    exif = image.getexif()
    exif[270] = "private metadata"
    exif[315] = "private author"
    image.save(output, "JPEG", exif=exif)
    return output.getvalue()


class MediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.app = create_app({"TESTING": True, "MEDIA_ROOT": str(self.root)})
        self.a, self.b = self.app.test_client(), self.app.test_client()
        for client, name in ((self.a, "media_a"), (self.b, "media_b")):
            self.call(
                client,
                "POST",
                "/accounts/register",
                {
                    "username": name,
                    "display_name": name,
                    "password": "testing-password-123",
                },
            )
        self.course = self.app.extensions["catalog"].load()["sections"][0]["course_key"]

    def call(self, client, method, path, data=None):
        token = client.get("/api/v1/me").json["csrf_token"]
        return client.open(
            "/api/v1" + path, method=method, json=data, headers={"X-CSRF-Token": token}
        )

    def upload(self, client=None, raw=None, **fields):
        client = client or self.a
        token = client.get("/api/v1/me").json["csrf_token"]
        data = {
            "body": "A campus project worth sharing.",
            "category": "study",
            "course_key": self.course,
            "descriptions": json.dumps(["A green test image"]),
            "media": (io.BytesIO(photo() if raw is None else raw), "../../photo.html"),
        }
        data.update(fields)
        response = client.post(
            "/api/v1/media/posts", data=data, headers={"X-CSRF-Token": token}
        )
        self.addCleanup(response.close)
        response.request.environ["wsgi.input"].close()
        return response

    def post(self):
        result = self.upload()
        self.assertEqual(result.status_code, 201, result.json)
        return self.a.get("/api/v1/media/posts").json["posts"][0]

    def test_public_feed_validates_decodes_and_strips_metadata(self):
        post = self.post()
        asset = post["assets"][0]
        self.assertEqual(post["course_key"], self.course)
        self.assertNotIn("filename", asset)
        response = self.app.test_client().get(asset["url"])
        self.addCleanup(response.close)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/webp")
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        with Image.open(io.BytesIO(response.data)) as image:
            self.assertEqual(image.size, (128, 96))
            self.assertFalse(image.getexif())
            self.assertNotIn("private", str(image.info))
        self.assertFalse((self.root.parent / "photo.html").exists())

    def test_requires_account_csrf_and_real_media(self):
        guest = self.app.test_client()
        self.assertEqual(self.upload(guest).status_code, 401)
        self.assertEqual(self.a.post("/api/v1/media/posts", data={}).status_code, 403)
        for raw in (
            b'<svg onload="alert(1)"></svg>',
            b"<html>bad</html>",
            b"",
            b"\x1aE\xdf\xa3fake",
            b"0000ftypfake",
        ):
            self.assertEqual(self.upload(raw=raw).status_code, 400)
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertEqual(self.a.get("/api/v1/media/posts").json["posts"], [])

    def test_descriptions_categories_course_and_count_validation(self):
        for fields in (
            {"descriptions": "not-json"},
            {"descriptions": "{}"},
            {"descriptions": "[1]"},
            {"descriptions": '["x"]'},
            {"category": "bad"},
            {"course_key": "missing"},
        ):
            with self.subTest(fields=fields):
                self.assertIn(self.upload(**fields).status_code, (400, 404))
        token = self.a.get("/api/v1/me").json["csrf_token"]
        response = self.a.post(
            "/api/v1/media/posts",
            data={"body": "A caption", "descriptions": "[]"},
            headers={"X-CSRF-Token": token},
        )
        self.assertEqual(response.status_code, 400)

    def test_atomic_multi_file_failure_and_quota(self):
        self.assertEqual(
            self.upload(
                descriptions=json.dumps(["A photo", "Bad file"]),
                media=[(io.BytesIO(photo()), "a.jpg"), (io.BytesIO(b"bad"), "b.png")],
            ).status_code,
            400,
        )
        self.assertEqual(list(self.root.iterdir()), [])
        self.app.config["MEDIA_USER_QUOTA"] = 1
        self.assertEqual(self.upload().status_code, 400)
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertFalse(self.a.get("/api/v1/media/posts").json["posts"])

    def test_ownership_likes_comments_and_removal_gate(self):
        post = self.post()
        identity = post["id"]
        self.assertEqual(
            self.call(self.b, "DELETE", f"/media/posts/{identity}").status_code, 404
        )
        for _ in range(2):
            result = self.call(self.b, "PUT", f"/media/posts/{identity}/like")
            self.assertEqual(result.json["like_count"], 1)
        self.assertTrue(self.b.get("/api/v1/media/posts").json["posts"][0]["liked"])
        self.assertFalse(self.a.get("/api/v1/media/posts").json["posts"][0]["liked"])
        self.assertEqual(
            self.call(self.b, "DELETE", f"/media/posts/{identity}/like").json[
                "like_count"
            ],
            0,
        )
        comment = self.call(
            self.b,
            "POST",
            f"/media/posts/{identity}/comments",
            {"body": "This looks great"},
        ).json["id"]
        self.assertEqual(
            self.call(self.a, "DELETE", f"/media/comments/{comment}").status_code, 404
        )
        self.assertEqual(
            self.call(self.b, "DELETE", f"/media/comments/{comment}").status_code, 200
        )
        self.assertFalse(
            self.a.get(f"/api/v1/media/posts/{identity}/comments").json["comments"]
        )
        self.call(self.a, "DELETE", f"/media/posts/{identity}")
        self.assertEqual(self.a.get(post["assets"][0]["url"]).status_code, 404)
        self.assertEqual(
            self.call(
                self.b,
                "POST",
                f"/media/posts/{identity}/comments",
                {"body": "No longer visible"},
            ).status_code,
            404,
        )
        self.assertEqual(
            self.call(self.b, "PUT", f"/media/posts/{identity}/like").status_code, 404
        )
        self.assertFalse(self.a.get("/api/v1/media/posts").json["posts"])

    def test_media_reports_and_moderation_block_direct_asset(self):
        post = self.post()
        identity = post["id"]
        self.call(
            self.b,
            "POST",
            "/reports",
            {
                "target_type": "media_post",
                "target_id": identity,
                "reason": "Please review this post",
            },
        )
        self.assertEqual(self.a.get("/api/v1/moderation/reports").status_code, 403)
        with self.app.extensions["database"].connect() as connection:
            connection.execute(
                "UPDATE users SET role='moderator' WHERE username='media_a'"
            )
        reports = self.a.get("/api/v1/moderation/reports").json["reports"]
        self.assertEqual(len(reports[0]["target"]["assets"]), 1)
        self.call(
            self.a,
            "POST",
            f"/moderation/reports/{reports[0]['id']}",
            {"action": "hide", "note": "Removed after review"},
        )
        self.assertEqual(
            self.a.get(
                post["assets"][0]["url"], headers={"Range": "bytes=0-100"}
            ).status_code,
            404,
        )
        self.assertFalse(self.a.get("/api/v1/media/posts").json["posts"])
        self.assertEqual(
            self.call(self.a, "PUT", f"/media/posts/{identity}/like").status_code, 404
        )

    def test_media_comment_reports(self):
        post = self.post()
        comment = self.call(
            self.b,
            "POST",
            f"/media/posts/{post['id']}/comments",
            {"body": "A comment to review"},
        ).json["id"]
        self.assertEqual(
            self.call(
                self.a,
                "POST",
                "/reports",
                {
                    "target_type": "media_comment",
                    "target_id": comment,
                    "reason": "Review this comment",
                },
            ).status_code,
            201,
        )
        with self.app.extensions["database"].connect() as c:
            c.execute("UPDATE users SET role='moderator' WHERE username='media_a'")
        report = self.a.get("/api/v1/moderation/reports").json["reports"][0]
        self.call(
            self.a,
            "POST",
            f"/moderation/reports/{report['id']}",
            {"action": "hide", "note": "Reviewed and hidden"},
        )
        self.assertFalse(
            self.a.get(f"/api/v1/media/posts/{post['id']}/comments").json["comments"]
        )

    def test_keyset_feed_and_category_course_filtering(self):
        with self.app.extensions["database"].connect() as c:
            user = c.execute("SELECT id FROM users LIMIT 1").fetchone()[0]
            for i in range(15):
                c.execute(
                    "INSERT INTO media_posts(owner_id,body,category,term,created_at,course_key) VALUES(?,?,'campus','2027SP','2026-10-13',?)",
                    (user, str(i), self.course),
                )
        first = self.a.get("/api/v1/media/posts").json
        self.assertEqual(len(first["posts"]), 12)
        second = self.a.get(f"/api/v1/media/posts?before={first['next_before']}").json
        self.assertEqual(len(second["posts"]), 3)
        self.assertFalse(
            set(p["id"] for p in first["posts"]) & set(p["id"] for p in second["posts"])
        )
        self.assertIsNone(second["next_before"])
        self.assertFalse(self.a.get("/api/v1/media/posts?category=study").json["posts"])
        self.assertEqual(
            len(self.a.get(f"/api/v1/media/posts?course={self.course}").json["posts"]),
            12,
        )
        for cursor in ("bad", "0", "-1", "9" * 30):
            self.assertEqual(
                self.a.get(f"/api/v1/media/posts?before={cursor}").status_code, 400
            )

    def test_comment_pagination(self):
        post = self.post()
        with self.app.extensions["database"].connect() as c:
            for i in range(55):
                c.execute(
                    "INSERT INTO media_comments(post_id,owner_id,body,created_at) VALUES(?,?,?,'2026-10-13')",
                    (post["id"], post["owner_id"], str(i)),
                )
        first = self.a.get(f"/api/v1/media/posts/{post['id']}/comments").json
        self.assertEqual(len(first["comments"]), 50)
        second = self.a.get(
            f"/api/v1/media/posts/{post['id']}/comments?after={first['next_after']}"
        ).json
        self.assertEqual(len(second["comments"]), 5)
        self.assertIsNone(second["next_after"])

    def test_multipart_body_limit(self):
        self.assertEqual(self.upload(raw=b"x" * (34 * 1024 * 1024)).status_code, 413)

    def test_actual_video_transcode_and_rejection(self):
        source = self.root / "fixture.mp4"
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-y",
                "-f",
                "lavfi",
                "-i",
                "color=c=green:s=160x120:d=1",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(source),
            ],
            capture_output=True,
            check=True,
        )
        raw = source.read_bytes()
        source.unlink()
        result = self.upload(
            raw=raw, descriptions=json.dumps(["A green video test frame"])
        )
        self.assertEqual(result.status_code, 201, result.json)
        asset = self.a.get("/api/v1/media/posts").json["posts"][0]["assets"][0]
        self.assertEqual(asset["mime"], "video/mp4")
        self.assertAlmostEqual(asset["duration"], 1, delta=0.1)
        with self.a.get(asset["url"], headers={"Range": "bytes=0-99"}) as response:
            self.assertEqual(response.status_code, 206)
        with patch(
            "fcs.media_processing.run_video",
            return_value="Duration: 00:01:01.00\nVideo: h264, 160x120",
        ):
            self.assertEqual(self.upload(raw=raw).status_code, 400)
        with patch(
            "fcs.media_processing.run_video",
            side_effect=ValueError("Processing failed"),
        ):
            self.assertEqual(self.upload(raw=raw).status_code, 400)
        self.assertFalse(list(self.root.glob("*.upload")))
        self.assertEqual(len(list(self.root.glob("*.mp4"))), 1)

    def test_image_pixel_limit_and_animation_rejection(self):
        with patch("fcs.media_processing.MAX_PIXELS", 10):
            self.assertEqual(self.upload().status_code, 400)
        output = io.BytesIO()
        frames = [Image.new("RGB", (20, 20), c) for c in ["red", "blue"]]
        frames[0].save(
            output, "WEBP", save_all=True, append_images=frames[1:], duration=100
        )
        self.assertEqual(self.upload(raw=output.getvalue()).status_code, 400)
