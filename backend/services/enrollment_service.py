from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..config import CURRENT_STUDENT, SNAPSHOT_PATH
from ..database.repositories import CourseRepository, EnrollmentRepository
from ..domain.enrollment_manager import EnrollmentManager


class EnrollmentService:
    def __init__(
        self,
        manager: EnrollmentManager,
        course_repo: CourseRepository,
        enrollment_repo: EnrollmentRepository,
    ) -> None:
        self.manager = manager
        self.course_repo = course_repo
        self.enrollment_repo = enrollment_repo

    def available_course_keys(self) -> list[dict[str, Any]]:
        return self.course_repo.get_available_course_keys()

    def get_student_enrollments(self, user_id: str) -> list[dict[str, Any]]:
        return self.manager.get_student_enrollments(user_id)

    def get_student_summary(self, user_id: str) -> dict[str, int]:
        return self.manager.get_student_summary(user_id)

    def enroll(self, user_id: str, email: str, enrollment_key: str) -> dict[str, Any]:
        return self.manager.enroll_with_key(user_id, email, enrollment_key)

    def unenroll(self, user_id: str, course_id: str) -> bool:
        return self.manager.soft_unenroll_student(user_id, course_id)

    def get_dashboard_data(self, user_id: str) -> dict[str, Any]:
        return {
            "current_student": CURRENT_STUDENT,
            "available_course_keys": self.available_course_keys(),
            "enrolled_courses": self.get_student_enrollments(user_id),
            "summary": self.get_student_summary(user_id),
        }

    def export_snapshot(self, path: Path = SNAPSHOT_PATH) -> None:
        snapshot = {
            "current_student": CURRENT_STUDENT,
            "available_course_keys": self.available_course_keys(),
            "enrollment_table": self.enrollment_repo.get_all_enrollment_records(),
        }
        path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
