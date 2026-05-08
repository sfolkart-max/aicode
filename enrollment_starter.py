"""
Module 8 Student Enrollment backend starter.

This file is intentionally procedural for the starter application. It now delegates
business rules and data access to layered backend components while preserving
existing enrollment behavior, sample seeding, and JSON export.
"""

from __future__ import annotations

from backend.config import CURRENT_STUDENT, SNAPSHOT_PATH
from backend.database.service import DatabaseService
from backend.database.repositories import CourseRepository, EnrollmentRepository
from backend.domain.enrollment_manager import EnrollmentManager
from backend.services.enrollment_service import EnrollmentService


def build_enrollment_service() -> EnrollmentService:
    database = DatabaseService()
    course_repo = CourseRepository(database)
    enrollment_repo = EnrollmentRepository(database)
    manager = EnrollmentManager(course_repo, enrollment_repo)
    return EnrollmentService(manager, course_repo, enrollment_repo)


def main() -> None:
    database = DatabaseService()
    database.create_tables()
    database.seed_sample_data()

    service = build_enrollment_service()
    user_id = CURRENT_STUDENT["user_id"]
    email = CURRENT_STUDENT["email"]

    print("Current student:")
    print(CURRENT_STUDENT)

    print("\nAvailable enrollment keys:")
    print(service.available_course_keys())

    print("\nInitial enrolled classes:")
    print(service.get_student_enrollments(user_id))

    print("\nStudent enters key DATA210-SPRING:")
    print(service.enroll(user_id, email, "DATA210-SPRING"))

    print("\nUpdated enrolled classes:")
    print(service.get_student_enrollments(user_id))

    print("\nStudent summary:")
    print(service.get_student_summary(user_id))

    service.export_snapshot()
    print(f"\nDatabase snapshot written to: {SNAPSHOT_PATH}")


if __name__ == "__main__":
    main()
