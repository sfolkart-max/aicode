from __future__ import annotations

from typing import Any, Iterable, Optional

from .service import DatabaseService
from ..config import STATUS_ENROLLED


def rows_to_dicts(rows: list[Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


class CourseRepository:
    def __init__(self, database: DatabaseService) -> None:
        self.database = database

    def get_available_course_keys(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT course_id, course_name, instructor, enrollment_key
                FROM courses
                ORDER BY course_id
                """
            ).fetchall()
        return rows_to_dicts(rows)

    def get_course_by_key(self, enrollment_key: str) -> Optional[dict[str, Any]]:
        if not enrollment_key:
            return None

        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT course_id, course_name, instructor, enrollment_key
                FROM courses
                WHERE enrollment_key = ?
                """,
                (enrollment_key.strip().upper(),),
            ).fetchone()

        return dict(row) if row else None


class EnrollmentRepository:
    def __init__(self, database: DatabaseService) -> None:
        self.database = database

    def get_student_enrollments(self, user_id: str) -> list[dict[str, Any]]:
        if not user_id:
            return []

        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    e.enrollment_id,
                    e.user_id,
                    e.email,
                    e.course_id,
                    c.course_name,
                    c.instructor,
                    e.status,
                    e.enrolled_at
                FROM enrollments e
                JOIN courses c ON c.course_id = e.course_id
                WHERE e.user_id = ? AND e.status = ?
                ORDER BY c.course_id
                """,
                (user_id, STATUS_ENROLLED),
            ).fetchall()

        return rows_to_dicts(rows)

    def get_student_enrollment_history(self, user_id: str) -> list[dict[str, Any]]:
        if not user_id:
            return []

        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    e.enrollment_id,
                    e.user_id,
                    e.email,
                    e.course_id,
                    c.course_name,
                    c.instructor,
                    e.status,
                    e.enrolled_at
                FROM enrollments e
                JOIN courses c ON c.course_id = e.course_id
                WHERE e.user_id = ?
                ORDER BY c.course_id
                """,
                (user_id,),
            ).fetchall()

        return rows_to_dicts(rows)

    def get_student_course_record(
        self,
        user_id: str,
        course_id: str,
    ) -> Optional[dict[str, Any]]:
        if not user_id or not course_id:
            return None

        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT enrollment_id, user_id, email, course_id, status, enrolled_at
                FROM enrollments
                WHERE user_id = ? AND course_id = ?
                """,
                (user_id, course_id),
            ).fetchone()

        return dict(row) if row else None

    def upsert_enrollment(
        self,
        user_id: str,
        email: str,
        course_id: str,
        status: str,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO enrollments (user_id, email, course_id, status)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, course_id)
                DO UPDATE SET
                    email = excluded.email,
                    status = excluded.status,
                    enrolled_at = CURRENT_TIMESTAMP
                """,
                (user_id, email, course_id, status),
            )

    def update_enrollment_status(
        self,
        user_id: str,
        course_id: str,
        status: str,
    ) -> int:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE enrollments
                SET status = ?
                WHERE user_id = ? AND course_id = ?
                """,
                (status, user_id, course_id),
            )

        return cursor.rowcount

    def get_all_enrollment_records(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    e.enrollment_id,
                    e.user_id,
                    e.email,
                    e.course_id,
                    c.course_name,
                    c.instructor,
                    e.status,
                    e.enrolled_at
                FROM enrollments e
                JOIN courses c ON c.course_id = e.course_id
                ORDER BY e.user_id, e.course_id
                """
            ).fetchall()

        return rows_to_dicts(rows)
