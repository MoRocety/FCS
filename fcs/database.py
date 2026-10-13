"""Small transactional persistence layer for the single-host FCS application."""

import sqlite3
import weakref
from contextlib import contextmanager
from pathlib import Path
from threading import RLock

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, display_name TEXT NOT NULL,
 password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'student', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS schedules (
 id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id), name TEXT NOT NULL,
 term TEXT NOT NULL, draft TEXT NOT NULL, sections TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS shares (
 token TEXT PRIMARY KEY, schedule_id INTEGER NOT NULL REFERENCES schedules(id) ON DELETE CASCADE,
 snapshot TEXT NOT NULL, created_at TEXT NOT NULL, revoked_at TEXT);
CREATE TABLE IF NOT EXISTS reviews (
 id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id), kind TEXT NOT NULL,
 subject_key TEXT NOT NULL, subject_name TEXT NOT NULL, term TEXT NOT NULL,
 rating INTEGER NOT NULL, difficulty INTEGER NOT NULL, body TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'published', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
 UNIQUE(owner_id, kind, subject_key, term));
CREATE TABLE IF NOT EXISTS threads (
 id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id), course_key TEXT NOT NULL,
 term TEXT NOT NULL, kind TEXT NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'published', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS comments (
 id INTEGER PRIMARY KEY, thread_id INTEGER NOT NULL REFERENCES threads(id),
 owner_id INTEGER NOT NULL REFERENCES users(id), body TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'published', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS memberships (
 thread_id INTEGER NOT NULL REFERENCES threads(id), user_id INTEGER NOT NULL REFERENCES users(id),
 joined_at TEXT NOT NULL, PRIMARY KEY(thread_id,user_id));
CREATE TABLE IF NOT EXISTS reports (
 id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id), target_type TEXT NOT NULL,
 target_id INTEGER NOT NULL, reason TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open',
 created_at TEXT NOT NULL, UNIQUE(owner_id,target_type,target_id));
CREATE TABLE IF NOT EXISTS moderation_actions (
 id INTEGER PRIMARY KEY, moderator_id INTEGER NOT NULL REFERENCES users(id), report_id INTEGER NOT NULL REFERENCES reports(id),
 action TEXT NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS watches (
 id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id), term TEXT NOT NULL,
 section_id TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(owner_id,term,section_id));
CREATE TABLE IF NOT EXISTS catalog_runs (
 id INTEGER PRIMARY KEY, term TEXT NOT NULL, revision TEXT NOT NULL, observed_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS catalog_heads (
 term TEXT PRIMARY KEY, revision TEXT NOT NULL, run_id INTEGER NOT NULL REFERENCES catalog_runs(id), source_mtime_ns INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS current_seats (
 term TEXT NOT NULL, section_id TEXT NOT NULL, available INTEGER NOT NULL, PRIMARY KEY(term,section_id));
CREATE TABLE IF NOT EXISTS notifications (
 id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id), term TEXT NOT NULL,
 section_id TEXT NOT NULL, run_id INTEGER NOT NULL REFERENCES catalog_runs(id), message TEXT NOT NULL,
 created_at TEXT NOT NULL, read_at TEXT, UNIQUE(owner_id,section_id,run_id));
CREATE TABLE IF NOT EXISTS throttle (
 key TEXT PRIMARY KEY, count INTEGER NOT NULL, started REAL NOT NULL);
CREATE TABLE IF NOT EXISTS media_posts (
 id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id), body TEXT NOT NULL,
 category TEXT NOT NULL, course_key TEXT, course_name TEXT, term TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'published', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS media_assets (
 id INTEGER PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES media_posts(id),
 filename TEXT NOT NULL UNIQUE, kind TEXT NOT NULL, mime TEXT NOT NULL,
 description TEXT NOT NULL, bytes INTEGER NOT NULL, width INTEGER, height INTEGER,
 duration REAL, position INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS media_comments (
 id INTEGER PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES media_posts(id),
 owner_id INTEGER NOT NULL REFERENCES users(id), body TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'published', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS media_likes (
 post_id INTEGER NOT NULL REFERENCES media_posts(id), user_id INTEGER NOT NULL REFERENCES users(id),
 PRIMARY KEY(post_id,user_id));
CREATE INDEX IF NOT EXISTS media_feed ON media_posts(status,id);
CREATE INDEX IF NOT EXISTS media_asset_post ON media_assets(post_id,position);
CREATE INDEX IF NOT EXISTS media_comment_post ON media_comments(post_id,status,id);
CREATE INDEX IF NOT EXISTS review_subject ON reviews(kind,subject_key,status);
CREATE INDEX IF NOT EXISTS thread_course ON threads(course_key,term,status);
CREATE INDEX IF NOT EXISTS comments_thread ON comments(thread_id,status);
CREATE INDEX IF NOT EXISTS notification_owner ON notifications(owner_id,id);
"""


class Database:
    def __init__(self, path):
        self.path = str(path)
        self.lock = RLock()
        self.memory = None
        if self.path == ":memory:":
            self.memory = sqlite3.connect(":memory:", check_same_thread=False)
            weakref.finalize(self, self.memory.close)
        else:
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            if connection.execute("PRAGMA user_version").fetchone()[0] > 3:
                raise ValueError("This database was created by a newer FCS version")
            connection.executescript(SCHEMA)
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(catalog_heads)")
            }
            if "source_mtime_ns" not in columns:
                connection.execute(
                    "ALTER TABLE catalog_heads ADD COLUMN source_mtime_ns INTEGER NOT NULL DEFAULT 0"
                )
            connection.execute("PRAGMA user_version=3")
        if not self.memory:
            Path(self.path).chmod(0o600)

    @contextmanager
    def connect(self):
        with self.lock:
            connection = self.memory or sqlite3.connect(self.path, timeout=15)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            try:
                with connection:
                    yield connection
            finally:
                if not self.memory:
                    connection.close()
