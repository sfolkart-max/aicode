# Analysis of enrollment_starter.py

## Overview
This Python file implements a basic student enrollment system for a course management application. It's designed as a starter template for Module 8, intentionally procedural to allow students to refactor it into object-oriented code later. The system uses SQLite for data persistence and focuses on core enrollment functionality.

## Architecture and Structure

### Database Design
- **Tables**: Two main tables - `courses` and `enrollments`
- **Courses table**: Stores course information including ID, name, instructor, and enrollment key
- **Enrollments table**: Tracks student enrollments with user ID, email, course ID, status, and timestamp
- **Relationships**: Foreign key constraint between enrollments and courses
- **Soft unenroll**: Uses status field ("enrolled"/"unenrolled") instead of hard deletes

### Code Organization
The code is organized into logical sections:
1. **Constants and Configuration**: Database paths, current student data, status constants, sample data
2. **Database Connection**: `connect()` function with row factory for dict-like access
3. **Schema Setup**: Table creation and data seeding functions
4. **Data Retrieval**: Functions to fetch courses and enrollment records
5. **Enrollment Operations**: Enroll and unenroll functionality
6. **Utilities**: Data conversion, summaries, and export
7. **Main Runner**: Terminal-based testing interface

## Key Functions Analysis

### Database Operations
- `connect()`: Establishes SQLite connection with Row factory for easier data access
- `create_tables()`: Creates schema with proper constraints (PRIMARY KEY, UNIQUE, FOREIGN KEY)
- `seed_sample_data()`: Populates initial data using INSERT OR IGNORE to avoid duplicates

### Data Access Layer
- `get_available_course_keys()`: Returns all courses with enrollment keys
- `get_course_by_key()`: Validates enrollment keys (case-insensitive)
- `get_student_enrollments()`: Active enrollments only (status = "enrolled")
- `get_student_enrollment_history()`: All records including unenrolled
- `get_student_course_record()`: Specific enrollment record

### Business Logic
- `enroll_with_key()`: Handles enrollment with conflict resolution (reactivates if previously unenrolled)
- `soft_unenroll_student()`: Changes status to "unenrolled" instead of deleting
- Uses UPSERT pattern (INSERT ... ON CONFLICT DO UPDATE) for enrollment

### Utilities
- `rows_to_dicts()`: Converts SQLite Row objects to dictionaries
- `get_student_summary()`: Aggregates enrollment counts by status
- `export_database_snapshot()`: Exports current state to JSON for inspection

## Design Patterns and Best Practices

### Good Practices
- **Context Managers**: All database operations use `with connect()` for automatic cleanup
- **Type Hints**: Comprehensive typing with `from __future__ import annotations`
- **Parameterized Queries**: Prevents SQL injection
- **Input Validation**: Basic checks for required fields and email format
- **Docstrings**: Clear documentation for all functions
- **Constants**: Status values and paths defined as constants
- **Error Handling**: Graceful returns (None/False) instead of exceptions

### Areas for Improvement/Refactoring
- **Procedural Structure**: Functions are standalone, could be grouped into classes (EnrollmentManager, DatabaseService)
- **No Exception Handling**: Uses return values for errors, could benefit from custom exceptions
- **Hardcoded Data**: Sample data is global, could be configurable
- **No Logging**: No audit trail for operations
- **Limited Validation**: Basic email check, no comprehensive input validation
- **No Transactions**: Multi-statement operations could use explicit transactions

## Data Flow
1. **Setup**: Create tables and seed initial data
2. **Enrollment**: Student provides enrollment key → validate key → insert/update enrollment record
3. **Retrieval**: Query enrollments with JOINs to get course details
4. **Unenrollment**: Update status to "unenrolled"
5. **Export**: Generate JSON snapshot of current state

## Testing and Development
- **Main Function**: Provides terminal-based testing workflow
- **Sample Data**: Includes realistic test data for development
- **JSON Export**: Allows inspection of database state without direct SQL access

## Future Refactoring Path
The code is structured to facilitate refactoring into:
1. **EnrollmentManager Class**: Group enrollment-related functions
2. **Database Layer**: Separate data access concerns
3. **Service Layer**: Business logic abstraction
4. **UI Integration**: Connect to Streamlit dashboard

## Dependencies and Requirements
- **SQLite3**: Built-in Python library
- **Pathlib**: Modern path handling
- **JSON**: Data export functionality
- **Typing**: Type annotations for better IDE support

This starter code provides a solid foundation for understanding database-driven enrollment systems while remaining simple enough for educational purposes.
