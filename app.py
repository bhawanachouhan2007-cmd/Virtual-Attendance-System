import streamlit as st
import sqlite3 as sql
from datetime import datetime
import random
import qrcode
from streamlit_qr_scanner import qr_scanner

# Database connection
conn = sql.connect("attendance.db", check_same_thread=False)
cursor = conn.cursor()

# Tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
Roll_no INTEGER PRIMARY KEY,
Name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
Roll_no INTEGER,
Name TEXT,
Date TEXT,
Time TEXT,
Status TEXT
)
""")

conn.commit()

# Store OTP
if "otp" not in st.session_state:
    st.session_state.otp = None


# -------------------
# Add Student
# -------------------

def add_record():

    st.subheader("Add Student")

    roll = st.number_input("Roll Number", step=1)
    name = st.text_input("Student Name")

    if st.button("Add Student"):

        cursor.execute(
            "INSERT INTO students VALUES (?,?)",
            (roll, name)
        )

        conn.commit()
        st.success("Record Added Successfully")


# -------------------
# Mark Attendance
# -------------------

def mark_attendance(roll):

    cursor.execute(
        "SELECT * FROM students WHERE Roll_no = ?",
        (roll,)
    )

    student = cursor.fetchone()

    if student is None:
        st.error("Student Not Registered")
        return

    name = student[1]

    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%H:%M:%S")

    cursor.execute(
        "SELECT * FROM attendance WHERE Roll_no=? AND Date=?",
        (roll, date)
    )

    if cursor.fetchone():
        st.warning("Attendance Already Marked")
        return

    cursor.execute(
        "INSERT INTO attendance VALUES (?,?,?,?,?)",
        (roll, name, date, time, "Present")
    )

    conn.commit()

    st.success("Attendance Marked Successfully")


# -------------------
# View Attendance
# -------------------

def see_attendance():

    st.subheader("Attendance List")

    cursor.execute("SELECT * FROM attendance")

    data = cursor.fetchall()

    if data:
        st.table(data)
    else:
        st.info("No Attendance Yet")


# -------------------
# Generate QR
# -------------------

def generate_QR():

    otp = random.randint(1000, 9999)

    st.session_state.otp = str(otp)

    img = qrcode.make(str(otp))
    img.save("qr_code.png")

    st.image("qr_code.png")

    st.success(f"OTP Generated: {otp}")


# -------------------
# Teacher Panel
# -------------------

def teacher_panel():

    st.title("Teacher Panel")

    menu = st.sidebar.selectbox(
        "Options",
        ["Add Student", "Generate QR Code", "Attendance List"]
    )

    if menu == "Add Student":
        add_record()

    elif menu == "Generate QR Code":
        generate_QR()

    elif menu == "Attendance List":
        see_attendance()


# -------------------
# Student Panel
# -------------------

def student_panel():

    st.title("Student Attendance")

    roll = st.number_input("Enter Roll Number", step=1)

    st.write("Scan QR from board")

    qr_data = qr_scanner()

    if qr_data:

        if qr_data == st.session_state.otp:

            mark_attendance(roll)

        else:
            st.error("Invalid QR")


# -------------------
# Main Menu
# -------------------

st.sidebar.title("Menu")

role = st.sidebar.selectbox(
    "Select Role",
    ["Teacher", "Student"]
)

if role == "Teacher":

    password = st.sidebar.text_input(
        "Enter Password",
        type="password"
    )

    if password == "teacher123":
        teacher_panel()

    elif password != "":
        st.error("Wrong Password")

else:
    student_panel()
