from __future__ import annotations

from typing import Any, Optional

from ..config import STATUS_ENROLLED, STATUS_UNENROLLED
from ..database.repositories import CourseRepository, EnrollmentRepository
from ..exceptions import InvalidEnrollmentKeyError, ValidationError


class EnrollmentManager:
    def __init__(self, course_repo: CourseRepository, enrollment_repo: EnrollmentRepository) -> None:
        self.course_repo = course_repo
        self.enrollment_repo = enrollment_repo

    def get_student_enrollments(self, user_id: str) -> list[dict[str, Any]]:
        return self.enrollment_repo.get_student_enrollments(user_id)

    def get_student_enrollment_history(self, user_id: str) -> list[dict[str, Any]]:
        return self.enrollment_repo.get_student_enrollment_history(user_id)

    def get_student_course_record(
        self,
        user_id: str,
        course_id: str,
    ) -> Optional[dict[str, Any]]:
        return self.enrollment_repo.get_student_course_record(user_id, course_id)

    def enroll_with_key(
        self,
        user_id: str,
        email: str,
        enrollment_key: str,
    ) -> dict[str, Any]:
        if not user_id:
            raise ValidationError("user_id is required")
        if not email or "@" not in email:
            raise ValidationError("valid email is required")
        if not enrollment_key:
            raise ValidationError("enrollment key is required")

        course = self.course_repo.get_course_by_key(enrollment_key)
        if not course:
            raise InvalidEnrollmentKeyError("Invalid enrollment key")

        self.enrollment_repo.upsert_enrollment(
            user_id=user_id,
            email=email,
            course_id=course["course_id"],
            status=STATUS_ENROLLED,
        )

        record = self.enrollment_repo.get_student_course_record(user_id, course["course_id"])
        if not record:
            raise ValidationError("Failed to create enrollment record")

        return record

    def soft_unenroll_student(self, user_id: str, course_id: str) -> bool:
        if not user_id:
            raise ValidationError("user_id is required")
        if not course_id:
            raise ValidationError("course_id is required")

        rowcount = self.enrollment_repo.update_enrollment_status(
            user_id=user_id,
            course_id=course_id,
            status=STATUS_UNENROLLED,
        )
        return rowcount > 0

    def get_student_summary(self, user_id: str) -> dict[str, int]:
        history = self.enrollment_repo.get_student_enrollment_history(user_id)
        summary = {
            "total_records": 0,
            STATUS_ENROLLED: 0,
            STATUS_UNENROLLED: 0,
        }

        for record in history:
            summary["total_records"] += 1
            status = record.get("status")
            if status in summary:
                summary[status] += 1

        return summary
