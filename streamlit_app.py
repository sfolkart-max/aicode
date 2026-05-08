import streamlit as st

from backend.config import CURRENT_STUDENT
from backend.database.service import DatabaseService
from backend.database.repositories import CourseRepository, EnrollmentRepository
from backend.domain.enrollment_manager import EnrollmentManager
from backend.exceptions import ValidationError
from backend.services.enrollment_service import EnrollmentService


def build_enrollment_service() -> EnrollmentService:
    database = DatabaseService()
    course_repo = CourseRepository(database)
    enrollment_repo = EnrollmentRepository(database)
    manager = EnrollmentManager(course_repo, enrollment_repo)
    return EnrollmentService(manager, course_repo, enrollment_repo)


def init_session_state() -> None:
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    if "selected_course_id" not in st.session_state:
        st.session_state.selected_course_id = None
    if "enrollment_key" not in st.session_state:
        st.session_state.enrollment_key = ""
    if "message" not in st.session_state:
        st.session_state.message = ""
    if "message_type" not in st.session_state:
        st.session_state.message_type = "info"


def clear_message() -> None:
    st.session_state.message = ""
    st.session_state.message_type = "info"


def show_message() -> None:
    if st.session_state.message:
        if st.session_state.message_type == "success":
            st.success(st.session_state.message)
        elif st.session_state.message_type == "error":
            st.error(st.session_state.message)
        else:
            st.info(st.session_state.message)


def go_to_dashboard() -> None:
    st.session_state.current_page = "dashboard"
    st.session_state.selected_course_id = None
    clear_message()


def select_class(course_id: str) -> None:
    st.session_state.selected_course_id = course_id
    st.session_state.current_page = "dashboard"
    clear_message()


def navigate_to_class(course_id: str) -> None:
    st.session_state.selected_course_id = course_id
    st.session_state.current_page = "class_details"
    clear_message()


def get_selected_course_details(service: EnrollmentService, user_id: str) -> dict[str, str] | None:
    if not st.session_state.selected_course_id:
        return None

    enrolled_courses = service.get_student_enrollments(user_id)
    selected = next(
        (course for course in enrolled_courses if course["course_id"] == st.session_state.selected_course_id),
        None,
    )
    if selected:
        return selected

    all_courses = service.available_course_keys()
    return next((course for course in all_courses if course["course_id"] == st.session_state.selected_course_id), None)


def handle_enrollment(service: EnrollmentService, user_id: str, email: str) -> None:
    enrollment_key = st.session_state.enrollment_key.strip()
    if not enrollment_key:
        st.session_state.message = "Please enter an enrollment key."
        st.session_state.message_type = "error"
        return

    try:
        service.enroll(user_id, email, enrollment_key)
        st.session_state.message = "Enrollment successful. Your dashboard has been updated."
        st.session_state.message_type = "success"
        st.session_state.enrollment_key = ""
    except ValidationError as error:
        st.session_state.message = str(error)
        st.session_state.message_type = "error"
    except Exception:
        st.session_state.message = "Unable to enroll with that key. Please check the key and try again."
        st.session_state.message_type = "error"


def handle_unenroll(service: EnrollmentService, user_id: str, course_id: str) -> None:
    success = service.unenroll(user_id, course_id)
    if success:
        st.session_state.message = "You have been unenrolled from the course."
        st.session_state.message_type = "success"
        st.session_state.selected_course_id = None
    else:
        st.session_state.message = "Unable to unenroll from that course."
        st.session_state.message_type = "error"


def show_dashboard(service: EnrollmentService, user_id: str, email: str) -> None:
    st.title("Student Dashboard")
    st.markdown(f"**Logged in as:** {CURRENT_STUDENT['name']} ({CURRENT_STUDENT['user_id']})")

    summary = service.get_student_summary(user_id)
    enrolled_courses = service.get_student_enrollments(user_id)

    st.divider()
    with st.columns([2, 1])[0]:
        st.subheader("Enroll in a course")
        st.text_input(
            "Enter enrollment key",
            value=st.session_state.enrollment_key,
            key="enrollment_key",
            placeholder="e.g. MISY350-SPRING",
            on_change=clear_message,
        )
        if st.button("Enroll"):
            handle_enrollment(service, user_id, email)
    with st.columns([2, 1])[1]:
        st.subheader("Enrollment Summary")
        st.metric("Enrolled", summary.get("enrolled", 0))
        st.metric("Unenrolled", summary.get("unenrolled", 0))
        st.metric("Total records", summary.get("total_records", 0))

    show_message()
    st.divider()

    st.subheader("Your Enrolled Classes")
    if not enrolled_courses:
        st.info("You are not enrolled in any active classes yet.")
        return

    selected_course_id = st.session_state.selected_course_id
    for course in enrolled_courses:
        course_id = course["course_id"]
        card = st.container()
        with card:
            cols = st.columns([3, 1, 1])
            cols[0].markdown(
                f"""**{course['course_name']}**  
                Instructor: {course['instructor']}  
                Course ID: {course_id}  
                Status: {course['status']}"""
            )
            if cols[1].button("Select class", key=f"select_{course_id}"):
                select_class(course_id)
            if cols[2].button("Unenroll", key=f"unenroll_{course_id}"):
                handle_unenroll(service, user_id, course_id)

    if selected_course_id:
        st.divider()
        st.info(f"Selected class: {selected_course_id}")
        if st.button("Go to Class", key="go_to_class"):
            navigate_to_class(selected_course_id)


def show_class_details(service: EnrollmentService, user_id: str) -> None:
    course_id = st.session_state.selected_course_id
    course_details = get_selected_course_details(service, user_id)
    if not course_id or not course_details:
        st.error("Selected class details are unavailable.")
        if st.button("Back to Dashboard"):
            go_to_dashboard()
        return

    st.title("Class Details")
    st.subheader(course_details.get("course_name", course_id))
    st.markdown(f"**Course ID:** {course_id}")
    st.markdown(f"**Instructor:** {course_details.get('instructor', 'N/A')}")
    st.markdown(f"**Enrollment status:** {course_details.get('status', 'N/A')}")
    st.markdown(f"**Enrolled at:** {course_details.get('enrolled_at', 'N/A')}")

    st.divider()
    if st.button("Unenroll"):
        handle_unenroll(service, user_id, course_id)

    if st.button("Back to Dashboard"):
        go_to_dashboard()


def main() -> None:
    st.set_page_config(page_title="Student Enrollment App", layout="wide")
    init_session_state()

    database = DatabaseService()
    database.create_tables()
    database.seed_sample_data()

    service = build_enrollment_service()
    user_id = CURRENT_STUDENT["user_id"]
    email = CURRENT_STUDENT["email"]

    if st.session_state.current_page == "dashboard":
        show_dashboard(service, user_id, email)
    else:
        show_class_details(service, user_id)


if __name__ == "__main__":
    main()
