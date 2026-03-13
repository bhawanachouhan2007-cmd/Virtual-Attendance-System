import streamlit as st
import sqlite3 as sql
from datetime import datetime
import random
import qrcode
import pandas as pd
import cv2
from pyzbar.pyzbar import decode

# -------------------
# Database
# -------------------

conn = sql.connect("attendance.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
Roll_no INTEGER PRIMARY KEY,
Name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
Roll_no INTEGER,
Name TEXT,
Date TEXT,
Time TEXT,
Status TEXT
)
""")

conn.commit()

# -------------------
# Session OTP
# -------------------

if "current_otp" not in st.session_state:
    st.session_state.current_otp = None


# -------------------
# Add Student
# -------------------

def add_record():

    st.subheader("Add Student")

    rol = st.number_input("Enter Roll No", step=1)
    name = st.text_input("Enter Name")

    if st.button("Add Record"):

        cursor.execute(
            "INSERT INTO students VALUES (?,?)",
            (rol, name)
        )

        conn.commit()

        st.success("Record Added Successfully")


# -------------------
# Generate QR
# -------------------

def generate_QR():

    num = random.randint(1000, 9999)

    st.session_state.current_otp = num

    img = qrcode.make(num)
    img.save("qrcode.png")

    st.image("qrcode.png")

    st.success(f"OTP Generated: {num}")


# -------------------
# Mark Attendance
# -------------------

def mark_attendance(Roll_no, entered_otp):

    cursor.execute(
        "SELECT * FROM students WHERE Roll_no=?",
        (Roll_no,)
    )

    student = cursor.fetchone()

    if student is None:
        st.error("Student Not Registered")
        return

    Name = student[1]

    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%H:%M:%S")

    cursor.execute(
        "SELECT * FROM attendance WHERE Roll_no=? AND Date=?",
        (Roll_no, date)
    )

    if entered_otp != st.session_state.current_otp:
        st.error("Invalid OTP")
        return

    if cursor.fetchone():
        st.warning("Attendance Already Marked")
        return

    cursor.execute(
        "INSERT INTO attendance VALUES (?,?,?,?,?)",
        (Roll_no, Name, date, time, "Present")
    )

    conn.commit()

    st.success("Attendance Marked Successfully")


# -------------------
# See Attendance
# -------------------

def see_attendance():

    cursor.execute("SELECT * FROM attendance")

    data = cursor.fetchall()

    df = pd.DataFrame(
        data,
        columns=["Roll No", "Name", "Date", "Time", "Status"]
    )

    st.dataframe(df)


# -------------------
# QR Scanner
# -------------------

def scan_qr():

    st.subheader("Scan QR")

    img_file = st.camera_input("Scan QR Code")

    if img_file is not None:

        file_bytes = bytearray(img_file.read())

        np_arr = cv2.imdecode(
            np.frombuffer(file_bytes, np.uint8),
            cv2.IMREAD_COLOR
        )

        decoded = decode(np_arr)

        for obj in decoded:

            otp = obj.data.decode("utf-8")

            return int(otp)

    return None


# -------------------
# Teacher Panel
# -------------------

def teacher_panel():

    st.title("Teacher Panel")

    option = st.sidebar.selectbox(
        "Options",
        ["Add Record", "Generate QR Code", "Attendance List"]
    )

    if option == "Add Record":
        add_record()

    elif option == "Generate QR Code":
        generate_QR()

    elif option == "Attendance List":
        see_attendance()


# -------------------
# Student Panel
# -------------------

def student_panel():

    st.title("Student Attendance")

    roll = st.number_input("Enter Roll Number", step=1)

    otp = st.number_input("Enter OTP (or Scan QR)", step=1)

    if st.button("Mark Attendance"):

        mark_attendance(roll, otp)


# -------------------
# Main Menu
# -------------------

st.sidebar.title("Login")

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
