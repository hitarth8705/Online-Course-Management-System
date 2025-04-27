import streamlit as st
import json
import os
from datetime import datetime

# # File paths
COURSES_FILE = "courses.json"
ENROLLMENTS_FILE = "enrollments.json"
FEEDBACK_FILE = "feedback.json"

def initialize_feedback_file():
    if not os.path.exists(FEEDBACK_FILE):
        save_data(FEEDBACK_FILE, [])


# Course Deadlines
COURSE_DEADLINES = {
    1: datetime(2025, 3, 5),
    2: datetime(2025, 3, 6),
    3: datetime(2025, 3, 7),
    4: datetime(2025, 3, 8),
}


def load_data(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as file:
        
        return json.load(file)

def save_data(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def calculate_remaining_days(course_id):
    deadline = COURSE_DEADLINES.get(course_id)
    if deadline:
        remaining_days = (deadline - datetime.now()).days
        return max(remaining_days, 0)
    return None
def send_reminder(student_name, course_title):
    enrollments = load_data(ENROLLMENTS_FILE)
    enrollment = next((e for e in enrollments if e["student_name"] == student_name), None)
    if enrollment:
        if 'reminders' not in enrollment:
            enrollment['reminders'] = []
        enrollment['reminders'].append(f"Reminder to complete {course_title}!")
        save_data(ENROLLMENTS_FILE, enrollments)
        return f"Reminder sent to {student_name} to complete the course: {course_title}!"
    return "Student not found."

def initialize_files():
 
    if not os.path.exists(COURSES_FILE):
        courses = [
            {"course_id": 1, "title": "Python Programming", "description": "Learn Python from scratch.", "instructor": "John Doe", "photo_url": "python.jpg"},
            {"course_id": 2, "title": "Data Science", "description": "Learn data analysis and visualization.", "instructor": "Jane Smith", "photo_url": "data_science.jpg"},
            {"course_id": 3, "title": "Java", "description": "Learn Java programming.", "instructor": "Alice Brown", "photo_url": "java.jpg"},
            {"course_id": 4, "title": "Full Stack Development", "description": "Master front-end and back-end development.", "instructor": "Bob Green", "photo_url": "fullstack.jpg"}
        ]
        save_data(COURSES_FILE, courses)
    if not os.path.exists(ENROLLMENTS_FILE):
        save_data(ENROLLMENTS_FILE, [])

st.title("Online Course Management System")
initialize_files()
initialize_feedback_file()

role = st.sidebar.selectbox("Select Role", ["Student", "Admin"])

if role == "Student":
    menu = st.sidebar.selectbox("Menu", ["Browse Courses", "Enroll", "Track Progress", "View Notifications", "Feedback"])

    if menu == "Browse Courses":
        st.subheader("Available Courses")
        courses = load_data(COURSES_FILE)
        for course in courses:
            remaining_days = calculate_remaining_days(course["course_id"])
            st.image(course['photo_url'], width=300, caption=f"{course['title']} by {course['instructor']}")
            st.write(f"**Title:** {course['title']}")
            st.write(f"**Description:** {course['description']}")
            st.write(f"**Instructor:** {course['instructor']}")
            st.write(f"**Deadline:** {COURSE_DEADLINES[course['course_id']].strftime('%d %B %Y')} "
                     f"({remaining_days} days left)")
            st.write("---")
    elif menu == "Enroll":
        st.subheader("Enroll in a Course")
        student_name = st.text_input("Enter your name:")
        course_id = st.number_input("Enter Course ID to Enroll:", min_value=1, step=1)

        if st.button("Enroll"):
            if not student_name.strip():  
                st.error("Name cannot be empty!")
            else:
                courses = load_data(COURSES_FILE)
                course = next((c for c in courses if c["course_id"] == course_id), None)

                if course:
                    enrollments = load_data(ENROLLMENTS_FILE)
                    existing_enrollment = next(
                    (e for e in enrollments if e["student_name"] == student_name and e["course_id"] == course_id), None
                )

                    if existing_enrollment:
                        st.error("You are already enrolled in this course!")
                    else:
                        enrollments.append({"student_name": student_name, "course_id": course_id, "progress": 0, "grade": None})
                        save_data(ENROLLMENTS_FILE, enrollments)
                        st.success(f"Enrolled in {course['title']} successfully!")
                else:
                    st.error("Invalid Course ID.")
    elif menu == "Track Progress":
        st.subheader("Track and Complete Your Progress")
        student_name = st.text_input("Enter your name:")
        course_id = st.number_input("Enter Course ID:", min_value=1, step=1)

        if st.button("Load Progress"):
            enrollments = load_data(ENROLLMENTS_FILE)
            enrollment = next((e for e in enrollments if e["student_name"] == student_name and e["course_id"] == course_id), None)

            if enrollment:
                st.session_state.enrollment = enrollment
                st.success("Progress loaded successfully!")
            else:
                st.error("Enrollment not found.")

        if "enrollment" in st.session_state:
            enrollment = st.session_state.enrollment
            st.write(f"**Current Progress:** {enrollment['progress']}%")

            tasks = [
                "Introduction", "Basics", "Intermediate Concepts", "Advanced Concepts", "Final Project"
            ]

            for i, task in enumerate(tasks, start=1):
                if enrollment["progress"] < i * 20:
                    if st.button(f"Complete {task}", key=f"task_{i}"):
                        enrollment["progress"] = min(enrollment["progress"] + 20, 100)
                        save_data(ENROLLMENTS_FILE, load_data(ENROLLMENTS_FILE))  # Update only relevant data
                        st.session_state.enrollment = enrollment
                        st.success(f"{task} completed. Progress: {enrollment['progress']}%")
                        if enrollment["progress"] == 100:
                            st.balloons()
                            st.success("🎉 Course Completed! 🎉")
                        break

            if enrollment is not None and enrollment["progress"] == 100:

                st.balloons()
                st.success("🎉 Course Completed! 🎉")

    

    elif menu == "View Notifications":
        st.subheader("Your Notifications")
        student_name = st.text_input("Enter your name:")
        if st.button("View Notifications"):
        
            enrollments = load_data(ENROLLMENTS_FILE)
            student_enrollments = [e for e in enrollments if e["student_name"] == student_name]
        
            if student_enrollments:
                reminders = []
                for enrollment in student_enrollments:
                    reminders.extend(enrollment.get('reminders', []))
            
                if reminders:
                    st.subheader("Notifications:")
                    for reminder in reminders:
                        st.write(f"- {reminder}")
                else:
                    st.info("No notifications available.")
            else:
                st.error("Student not found.")
    elif menu == "Feedback":
        st.subheader("Submit Feedback")

        student_name = st.text_input("Enter your name:")
    
    # Load enrollments to check if the student exists
        enrollments = load_data(ENROLLMENTS_FILE)
        student_enrollments = [e["course_id"] for e in enrollments if e["student_name"] == student_name]

        if not student_enrollments:
            st.error("You are not enrolled in any courses.")
        else:
            course_id = st.selectbox("Select Course for Feedback:", student_enrollments)  # Only show enrolled courses
            feedback_text = st.text_area("Write your feedback:")

            if st.button("Submit Feedback"):
                feedback_data = load_data(FEEDBACK_FILE)

            # Prevent duplicate feedback
                existing_feedback = next((f for f in feedback_data if f["student_name"] == student_name and f["course_id"] == course_id), None)

                if existing_feedback:
                    st.warning("You have already submitted feedback for this course.")
                else:
                    feedback_data.append({"student_name": student_name, "course_id": course_id, "feedback": feedback_text})
                    save_data(FEEDBACK_FILE, feedback_data)
                    st.success("Your feedback has been submitted successfully!")

elif role == "Admin":
    menu = st.sidebar.selectbox("Menu", ["View Student Progress", "Send Reminder", "Generate Certificate", "Assign Grade","View Feedback"])

    if menu == "View Student Progress":
        st.subheader("Student Progress")
        enrollments = load_data(ENROLLMENTS_FILE)
        for enrollment in enrollments:
            courses = load_data(COURSES_FILE)
            course = next((c for c in courses if c["course_id"] == enrollment["course_id"]), None)
            if course:
                st.write(f"Student: {enrollment['student_name']}")
                st.write(f"Course: {course['title']}")
                st.write(f"Progress: {enrollment['progress']}%")
                st.write(f"Grade: {enrollment['grade'] or 'Not Assigned'}")
                st.write("---")
    elif menu == "Send Reminder":
        st.subheader("Send Reminder")
    
        student_name = st.text_input("Enter student name:")
    
    # Load enrollments and find courses where progress is < 100%
        enrollments = load_data(ENROLLMENTS_FILE)
        student_courses = [e for e in enrollments if e["student_name"] == student_name and e["progress"] < 100]

        if not student_courses:
            st.error("This student is either not enrolled in any course or has completed all enrolled courses.")
        else:
        # Show only courses where progress < 100%
            course_options = {e["course_id"]: e["course_id"] for e in student_courses}
            course_id = st.selectbox("Select Course:", list(course_options.keys()))

            if st.button("Send Reminder"):
                courses = load_data(COURSES_FILE)
                course_title = next((course["title"] for course in courses if course["course_id"] == course_id), None)

                if course_title:
                    message = send_reminder(student_name, course_title)
                    st.success(message)
                else:
                    st.error("Course not found.")


    # Generate Certificate for a student whose progress is 100%
    elif menu == "Generate Certificate":
        st.subheader("Generate Certificate")
        student_name = st.text_input("Enter student name:")
        course_id = st.number_input("Enter Course ID:", min_value=1, step=1)
        if st.button("Generate Certificate"):
            enrollments = load_data(ENROLLMENTS_FILE)
            enrollment = next((e for e in enrollments if e["student_name"] == student_name and e["course_id"] == course_id), None)
            if enrollment is None:
                st.error("Enrollment not found.")
            elif enrollment and enrollment["progress"] == 100:
                st.success(f"Certificate: {student_name} has successfully completed the course!")
            else:
                st.error("Course not completed or progress is less than 100%.")

# Assign grade only to those who have completed the course and Enrolled
    elif menu == "Assign Grade":
        st.subheader("Assign Grade")
        student_name = st.text_input("Enter student name:")
        course_id = st.number_input("Enter Course ID:", min_value=1, step=1)
        grade = st.text_input("Enter Grade (A, B, C, etc.):")
        if st.button("Assign Grade"):

            enrollments = load_data(ENROLLMENTS_FILE)
            enrollment = next((e for e in enrollments if e["student_name"] == student_name and e["course_id"] == course_id), None)
        
            if not enrollment:
                st.error("Enrollment not found.")
            elif enrollment["progress"] < 60:
                st.error("Cannot assign a grade. The student must complete at least 60% of the course!")
            else:
                enrollment["grade"] = grade
                save_data(ENROLLMENTS_FILE, enrollments)
                st.success(f"Grade {grade} assigned to {student_name} for course ID {course_id}.")
    #    View feedback    
    elif menu == "View Feedback":
        st.subheader("Feedback Notifications")
        feedback_data = load_data(FEEDBACK_FILE)
        if feedback_data:
            for feedback in feedback_data:
                student_name = feedback["student_name"]
                course_id = feedback["course_id"]
                feedback_message = feedback["feedback"]

            # Retrieve course title
                courses = load_data(COURSES_FILE)
                course_title = next((c["title"] for c in courses if c["course_id"] == course_id), "Unknown Course")

                st.write(f"📩 Feedback from **{student_name}** for course **{course_title} (ID: {course_id})**:")
                st.write(f"> {feedback_message}")
                st.write("---")
        else:
            st.info("No feedback received yet.")

