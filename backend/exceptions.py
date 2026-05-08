from __future__ import annotations


class EnrollmentError(Exception):
    """Base exception for enrollment backend errors."""


class ValidationError(EnrollmentError):
    """Raised when a business validation rule fails."""


class InvalidEnrollmentKeyError(ValidationError):
    """Raised when a provided enrollment key is invalid."""


class DatabaseError(EnrollmentError):
    """Raised when a database operation fails."""
