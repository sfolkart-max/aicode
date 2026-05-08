from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Course:
    course_id: str
    course_name: str
    instructor: str
    enrollment_key: str


@dataclass
class EnrollmentRecord:
    enrollment_id: int
    user_id: str
    email: str
    course_id: str
    course_name: str
    instructor: str
    status: str
    enrolled_at: str


@dataclass
class Student:
    user_id: str
    name: str
    email: str


@dataclass
class EnrollmentSummary:
    total_records: int
    enrolled: int
    unenrolled: int

    def to_dict(self) -> dict[str, int]:
        return {
            "total_records": self.total_records,
            "enrolled": self.enrolled,
            "unenrolled": self.unenrolled,
        }
