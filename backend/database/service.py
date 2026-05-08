from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from ..config import AVAILABLE_COURSE_KEYS, DB_PATH, SAMPLE_ENROLLMENTS


class DatabaseService:
    def __init__(self, path: Path = DB_PATH) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def create_tables(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS courses (
                    course_id TEXT PRIMARY KEY,
                    course_name TEXT NOT NULL,
                    instructor TEXT NOT NULL,
                    enrollment_key TEXT NOT NULL UNIQUE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS enrollments (
                    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    email TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'enrolled',
                    enrolled_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, course_id),
                    FOREIGN KEY(course_id) REFERENCES courses(course_id)
                )
                """
            )

    def seed_sample_data(self) -> None:
        with self.connect() as connection:
            connection.executemany(
                """
                INSERT OR IGNORE INTO courses (
                    course_id, course_name, instructor, enrollment_key
                ) VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        course["course_id"],
                        course["course_name"],
                        course["instructor"],
                        course["enrollment_key"],
                    )
                    for course in AVAILABLE_COURSE_KEYS
                ],
            )
            connection.executemany(
                """
                INSERT OR IGNORE INTO enrollments (user_id, email, course_id, status)
                VALUES (?, ?, ?, ?)
                """,
                SAMPLE_ENROLLMENTS,
            )
