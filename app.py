import streamlit as st
from datetime import datetime
import time

st.set_page_config(page_title="SmartQueue", page_icon="🎟️")

# ----------------------------
# Initialize system
# ----------------------------
if "init" not in st.session_state:

    st.session_state.departments = [
        "Student Section",
        "Accounts Section",
        "Bus Line",
        "Canteen"
    ]

    st.session_state.queue = {}

    for d in st.session_state.departments:
        st.session_state.queue[d] = {
            "current": 1,
            "last": 0,
            "paused": False,
            "avg_time": 2
        }

    st.session_state.students = {}

    st.session_state.page = "home"
    st.session_state.logged = False
    st.session_state.user = None
    st.session_state.role = None

    st.session_state.slots = {
        "Slot 1": "8:30 - 10:30",
        "Slot 2": "11:00 - 1:00",
        "Slot 3": "2:00 - 4:30"
    }

    st.session_state.init = True


# ----------------------------
# Helper Functions
# ----------------------------
def next_token(dept):
    st.session_state.queue[dept]["last"] += 1
    return st.session_state.queue[dept]["last"]


def people_ahead(dept, token):
    q = st.session_state.queue[dept]
    return max(token - q["current"], 0)


def waiting_time(dept, token):
    ahead = people_ahead(dept, token)
    avg = st.session_state.queue[dept]["avg_time"]
    return ahead * avg


def logout():
    st.session_state.logged = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.page = "home"
    st.rerun()


# ----------------------------
# HOME PAGE
# ----------------------------
if not st.session_state.logged:

    st.title("🎟️ Smart College Queue System")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Student Portal"):
            st.session_state.page = "student_login"
            st.rerun()

    with col2:
        if st.button("Admin Portal"):
            st.session_state.page = "admin_login"
            st.rerun()

# ----------------------------
# STUDENT LOGIN
# ----------------------------
    if st.session_state.page == "student_login":

        st.header("Student Login")

        sid = st.text_input("Student ID")

        if st.button("Login"):

            st.session_state.logged = True
            st.session_state.role = "student"
            st.session_state.user = sid

            if sid not in st.session_state.students:
                st.session_state.students[sid] = {
                    "tokens": []
                }

            st.rerun()

# ----------------------------
# ADMIN LOGIN
# ----------------------------
    if st.session_state.page == "admin_login":

        st.header("Admin Login")

        aid = st.text_input("Admin ID")

        if st.button("Enter Admin Panel"):

            st.session_state.logged = True
            st.session_state.role = "admin"
            st.session_state.user = aid
            st.rerun()

# ----------------------------
# STUDENT DASHBOARD
# ----------------------------
else:

    if st.session_state.role == "student":

        sid = st.session_state.user

        st.title("👨‍🎓 Student Dashboard")

        if st.button("Logout"):
            logout()

        dept = st.selectbox("Select Department", st.session_state.departments)

        slot = st.selectbox("Select Time Slot", list(st.session_state.slots.keys()))

        if st.button("Generate Token"):

            token = next_token(dept)

            booking = {
                "department": dept,
                "token": token,
                "slot": slot,
                "time": datetime.now().strftime("%H:%M")
            }

            st.session_state.students[sid]["tokens"].append(booking)

            st.success(f"Token {token} generated for {dept}")

        st.divider()

        st.subheader("📜 Booking History")

        history = st.session_state.students[sid]["tokens"]

        if history:

            for h in reversed(history):

                dept = h["department"]
                token = h["token"]

                ahead = people_ahead(dept, token)
                wait = waiting_time(dept, token)

                st.write(
                    f"🏢 {dept} | 🎟 Token {token} | ⏰ {h['slot']} | "
                    f"👥 Ahead: {ahead} | ⏳ Wait: {wait} min"
                )

        else:
            st.info("No bookings yet.")

        time.sleep(5)
        st.rerun()

# ----------------------------
# ADMIN DASHBOARD
# ----------------------------
    if st.session_state.role == "admin":

        st.title("⚙️ Admin Dashboard")

        if st.button("Logout"):
            logout()

        dept = st.selectbox("Department", st.session_state.departments)

        q = st.session_state.queue[dept]

        st.subheader(f"{dept}")

        st.write("Current Token:", q["current"])
        st.write("Last Token:", q["last"])
        st.write("Waiting:", q["last"] - q["current"])

        st.divider()

        speed = st.radio(
            "Service Speed",
            ["Fast", "Normal", "Slow"]
        )

        if speed == "Fast":
            q["avg_time"] = 1

        if speed == "Normal":
            q["avg_time"] = 2

        if speed == "Slow":
            q["avg_time"] = 4

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button("NEXT"):

                if not q["paused"] and q["current"] < q["last"]:
                    q["current"] += 1
                    st.rerun()

        with col2:

            if st.button("STOP"):
                q["paused"] = True

        with col3:

            if st.button("RESUME"):
                q["paused"] = False

        if q["paused"]:
            st.warning("Queue Paused")
        else:
            st.success("Queue Running")