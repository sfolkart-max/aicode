# Streamlit UI Plan for Student Enrollment Dashboard

## Overview
This plan outlines a two-page Streamlit application for the student enrollment system. The app assumes the student is already logged in and focuses on providing a dashboard-like experience similar to Canvas. The UI will integrate with the existing layered backend (service layer) without modifying the backend code.

## Application Structure
- **Page 1: Dashboard** - Main view showing enrolled classes, enrollment key input, and navigation
- **Page 2: Class Details** - Detailed view of a selected class after enrollment or navigation

## Page 1: Student Dashboard

### Layout and Components
- **Header**: Display current student name and user ID
- **Enrolled Classes Section**:
  - List of currently enrolled classes in cards or a grid
  - Each class card shows: course name, instructor, enrollment status
  - Clickable cards that reveal a "Go to Class" button when selected
- **Enrollment Section**:
  - Text input field for enrollment key
  - "Enroll" button
  - Success/error message area for enrollment validation
- **Summary Section**:
  - Display enrollment summary (total records, enrolled, unenrolled)

### Functionality
- Load enrolled classes using `service.get_student_enrollments(user_id)`
- Handle enrollment key submission:
  - Call `service.enroll(user_id, email, enrollment_key)`
  - Show success message and refresh enrolled classes list
  - Show error message for invalid keys
- Class selection:
  - When a class card is clicked, show "Go to Class" button
  - Button navigates to Page 2 with selected class details

## Page 2: Class Details

### Layout and Components
- **Header**: Class name, instructor, course ID
- **Class Information**:
  - Course description (if available)
  - Enrollment status
  - Enrollment date
- **Actions**:
  - "Unenroll" button (calls `service.unenroll(user_id, course_id)`)
  - "Back to Dashboard" button
- **Additional Details**:
  - Show enrollment history for this course

### Functionality
- Load class details using `service.get_student_course_record(user_id, course_id)`
- Handle unenroll:
  - Call `service.unenroll(user_id, course_id)`
  - Show confirmation and navigate back to dashboard
- Navigation back to dashboard refreshes the enrolled classes list

## Navigation and State Management

### Session State
- `current_page`: "dashboard" or "class_details"
- `selected_course_id`: ID of the selected class for Page 2
- `user_id`: Current student user ID (assumed set)
- `email`: Current student email (assumed set)
- `enrollment_message`: Success/error message for enrollment actions

### Page Switching
- Use `st.session_state` to manage page state
- Dashboard page sets `current_page = "dashboard"`
- Clicking "Go to Class" sets `current_page = "class_details"` and `selected_course_id`
- Class details page has "Back to Dashboard" button that resets to dashboard

## Integration with Backend

### Service Layer Usage
- Import `EnrollmentService` and build service instance
- Use existing methods:
  - `service.get_student_enrollments(user_id)`
  - `service.enroll(user_id, email, enrollment_key)`
  - `service.unenroll(user_id, course_id)`
  - `service.get_student_course_record(user_id, course_id)`
  - `service.get_student_summary(user_id)`

### No Backend Changes
- Do not modify service layer, domain, or repository code
- All interactions go through the `EnrollmentService` interface

## Implementation Steps

### Step 1: Create Streamlit App Structure
- Create `app.py` in project root
- Import necessary Streamlit components and backend services
- Set up session state initialization

### Step 2: Implement Dashboard Page
- Create function `show_dashboard()`
- Display student header
- Show enrolled classes as clickable cards
- Add enrollment key input and button
- Handle enrollment logic with try/catch for validation errors
- Add summary display

### Step 3: Implement Class Details Page
- Create function `show_class_details(course_id)`
- Display class information
- Add unenroll button with confirmation
- Add back to dashboard navigation

### Step 4: Main App Logic
- Check session state for current page
- Call appropriate page function
- Handle page transitions

### Step 5: Styling and UX
- Use Streamlit columns and cards for layout
- Add appropriate success/error messaging
- Ensure responsive design for class cards

## UI Components Breakdown

### Dashboard Page Components
- `st.title()` for header
- `st.columns()` for layout
- `st.button()` for "Go to Class" (conditional)
- `st.text_input()` for enrollment key
- `st.success()` / `st.error()` for messages
- Custom card components using `st.container()`

### Class Details Page Components
- `st.header()` for class title
- `st.write()` for class info display
- `st.button()` for unenroll and back navigation
- Confirmation dialog using `st.warning()` and buttons

## Data Flow

### Enrollment Flow
1. User enters enrollment key in text input
2. Clicks "Enroll" button
3. App calls `service.enroll(user_id, email, enrollment_key)`
4. If successful: show success message, refresh enrolled classes
5. If error: show error message

### Navigation Flow
1. User clicks on enrolled class card
2. "Go to Class" button appears
3. User clicks button
4. App sets session state and shows class details page

### Unenroll Flow
1. User clicks "Unenroll" on class details page
2. App calls `service.unenroll(user_id, course_id)`
3. Shows confirmation and navigates back to dashboard

## Assumptions and Constraints

### Authentication
- Student is pre-authenticated
- `user_id` and `email` are available in session state
- No login/registration UI

### Data Availability
- Backend service provides all necessary data
- Course details include name, instructor, enrollment status
- Enrollment keys are validated by service layer

### Error Handling
- Service layer raises `ValidationError` for invalid enrollment keys
- UI catches and displays user-friendly error messages

### Performance
- Assume small number of enrolled classes (dashboard-friendly)
- No caching needed beyond session state

This plan provides a clean, maintainable UI that integrates seamlessly with the existing layered backend architecture.
