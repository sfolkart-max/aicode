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

# Backend Refactor Plan

## Goal
Move the student enrollment backend from procedural functions into a layered, object-oriented design while keeping the SQLite database layer focused on row queries and updates. Preserve business meaning in the service layer for enrollment-key validation, dashboard intent, and summary counting.

## Refactor Objectives
- Keep SQLite access limited to the data layer
- Keep business rules and enrollment meaning in the service/domain layer
- Keep presentation/dashboard concepts separate from raw database operations
- Preserve the current behavior and data model
- Support future Streamlit integration without changing backend semantics

## Proposed Layers
1. **Infrastructure / Database Layer**
   - SQLite connection and row-based CRUD only
   - `DatabaseService` or similar class for `connect()`, table creation, seeding, and raw execution
   - No business rules here

2. **Repository Layer**
   - `CourseRepository`: course lookups and enrollment key queries
   - `EnrollmentRepository`: enrollment record queries, inserts, updates, history
   - Methods return plain data structures or dataclasses
   - Keep SQL and row conversion here

3. **Domain / Business Layer**
   - `EnrollmentManager`: encapsulates enrollment operations and business state
   - Contains core methods like `enroll_with_key`, `soft_unenroll_student`, `get_student_summary`
   - Applies business rules: active enrollments, reenrollment, status logic

4. **Service Layer**
   - `EnrollmentService`: orchestrates use cases for the UI/dashboard
   - Handles enrollment-key validation, dashboard-ready summaries, and export behavior
   - Converts repository results into meaningful service responses

5. **Utility Layer**
   - Export snapshot logic, summary aggregation, validation helpers
   - Could be helper services used by `EnrollmentService`

## Class and Component Sketch

### DatabaseService
- `connect()` -> sqlite3.Connection
- `create_tables()` -> create courses + enrollments
- `seed_sample_data()` -> insert sample courses and enrollments
- `execute_query()` / `fetch_rows()` helpers
- Use `row_factory = sqlite3.Row`

### Repositories
#### CourseRepository
- `get_all_courses()`
- `get_course_by_key(enrollment_key)`
- `insert_course(course)`

#### EnrollmentRepository
- `get_enrollments_for_student(user_id, active_only=True)`
- `get_enrollment_history(user_id)`
- `get_enrollment_record(user_id, course_id)`
- `upsert_enrollment(user_id, email, course_id, status)`
- `update_enrollment_status(user_id, course_id, status)`
- `get_all_enrollments()`

### Domain Model
- `Course` dataclass
- `EnrollmentRecord` dataclass
- `Student` dataclass or simple dict wrapper
- Optional: `EnrollmentStatus` constants/enums

### EnrollmentManager
- `enroll_with_key(user_id, email, enrollment_key)`
  - Validate input
  - Lookup course by key
  - Record status update or insert
  - Return enrollment record
- `soft_unenroll_student(user_id, course_id)`
  - Update status to `unenrolled`
- `get_student_enrollments(user_id)`
  - Return enrolled classroom data
- `get_student_summary(user_id)`
  - Count active and unenrolled histories
- `get_student_course_record(user_id, course_id)`
  - Return raw enrollment record

### EnrollmentService
- `dashboard_summary(user_id)`
  - Active courses + summary counts
- `available_course_keys()`
  - Course lookup for dashboard display
- `enroll(user_id, email, key)`
  - Apply service-level validation and return success/failure meaning
- `unenroll(user_id, course_id)`
  - Service-level unenroll action
- `export_snapshot(path)`
  - Build snapshot with current student, course keys, enrollment table

## Refactoring Sequence
1. **Extract DatabaseService** from existing `connect`, `create_tables`, `seed_sample_data`
2. **Extract repositories** for course and enrollment SQL operations
3. **Create dataclasses** for course and enrollment records
4. **Implement EnrollmentManager** with business semantics and repository calls
5. **Implement EnrollmentService** that returns dashboard-ready structures
6. **Move utilities** like `rows_to_dicts`, summary counting, and export into helper methods or service classes
7. **Retain original procedural functions** temporarily as adapters if needed for incremental refactor
8. **Add docstrings** and preserve the `main()` test runner until the new service layer is proven

## Design Rules
- SQLite layer only executes SQL and returns rows/dicts/dataclasses
- Business logic stays in the manager/service layer
- Validation and semantic rules belong in the service/domain layer
- No UI or dashboard concerns in SQL/repository classes
- Keep status values (`enrolled`, `unenrolled`) as shared constants
- Use explicit repository methods instead of ad-hoc SQL scattered across functions

## What to Keep in SQLite Focus
- `CREATE TABLE` statements
- row-to-dict conversion
- SELECT / INSERT / UPDATE queries
- `ON CONFLICT` upsert logic
- `ORDER BY` retrieval behavior
- sample seeding logic

## What to Move into Service Layer
- Enrollment-key normalization and validation
- Student dashboard semantics (`currently enrolled`, `history`, `summary counts`)
- Summary aggregation and count logic
- Export payload structure for snapshot
- Soft unenroll semantics

## Implementation Prompt
Use this prompt when you approve the plan and want the refactor implemented:

"Refactor `enrollment_starter.py` into a layered backend design. Create a SQLite-focused database layer with `DatabaseService` and repository classes for course and enrollment CRUD. Add a domain layer with `EnrollmentManager` for business rules like enrollment-key validation, active enrollment semantics, soft unenroll, and summary counting. Add a service layer with `EnrollmentService` for dashboard-oriented use cases and snapshot export. Keep the original procedural behavior intact during refactor and do not modify the existing database model."
