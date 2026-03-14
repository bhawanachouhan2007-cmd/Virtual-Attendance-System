import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import random
import qrcode

# ---------------- DATABASE ---------------- #

conn = sqlite3.connect("attendance.db", check_same_thread=False)
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
    Subject TEXT,
    Status TEXT
)
""")

conn.commit()

# --------------- OTP STORAGE ---------------- #

if "otp" not in st.session_state:
    st.session_state.otp = None

# ---------------- FUNCTIONS ---------------- #

def add_student(roll,name):
    cursor.execute("INSERT INTO students VALUES (?,?)",(roll,name))
    conn.commit()

def generate_qr():

    otp = random.randint(1000,9999)
    st.session_state.otp = otp

    qr = qrcode.make(str(otp))
    qr.save("qrcode.png")

    st.success(f"OTP Generated : {otp}")
    st.image("qrcode.png")

def mark_attendance(roll,entered_otp,subject):

    cursor.execute("SELECT * FROM students WHERE Roll_no=?",(roll,))
    student = cursor.fetchone()

    if student is None:
        st.error("Student Not Registered")
        return

    if entered_otp != st.session_state.otp:
        st.error("Invalid OTP")
        return

    name = student[1]

    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%H:%M:%S")

    cursor.execute(
        "SELECT * FROM attendance WHERE Roll_no=? AND Date=? AND Subject=?",
        (roll,date,subject)
    )

    if cursor.fetchone():
        st.warning("Attendance Already Marked")
        return

    cursor.execute(
        "INSERT INTO attendance VALUES (?,?,?,?,?,?)",
        (roll,name,date,time,subject,"Present")
    )

    conn.commit()
    st.success("Attendance Marked Successfully")

def view_attendance(date,subject):

    cursor.execute(
        "SELECT * FROM attendance WHERE Date=? AND Subject=?",
        (date,subject)
    )

    records = cursor.fetchall()

    if not records:
        st.warning("No Records Found")
        return

    df = pd.DataFrame(records,
        columns=["Roll No","Name","Date","Time","Subject","Status"]
    )

    st.dataframe(df)

def subject_attendance(subject):

    cursor.execute(
        "SELECT * FROM attendance WHERE Subject=? ORDER BY Roll_no",
        (subject,)
    )

    records = cursor.fetchall()

    if not records:
        st.warning("No Records Found")
        return

    df = pd.DataFrame(records,
        columns=["Roll No","Name","Date","Time","Subject","Status"]
    )

    st.dataframe(df)

# ---------------- UI ---------------- #

st.title("Virtual Attendance System")

role = st.sidebar.selectbox(
    "Select Role",
    ["Teacher","Student"]
)

# ---------------- TEACHER PANEL ---------------- #

if role == "Teacher":

    password = st.sidebar.text_input("Enter Password",type="password")

    if password == "teacher123":

        st.sidebar.success("Login Successful")

        menu = st.sidebar.selectbox(
            "Menu",
            ["Add Student","Generate QR","View Attendance","Subject Attendance"]
        )

        if menu == "Add Student":

            st.header("Add Student")

            roll = st.number_input("Roll Number",step=1)
            name = st.text_input("Student Name")

            if st.button("Add Student"):
                add_student(roll,name)
                st.success("Student Added Successfully")

        elif menu == "Generate QR":

            st.header("Generate OTP QR")

            if st.button("Generate QR Code"):
                generate_qr()

        elif menu == "View Attendance":

            st.header("View Attendance")

            date = st.text_input("Enter Date (dd-mm-yyyy)")
            subject = st.selectbox(
                "Select Subject",
                ["DBMS","Web Technology"]
            )

            if st.button("Show Attendance"):
                view_attendance(date,subject)

        elif menu == "Subject Attendance":

            st.header("Subject Wise Attendance")

            subject = st.selectbox(
                "Select Subject",
                ["DBMS","Web Technology"]
            )

            if st.button("Show Subject Attendance"):
                subject_attendance(subject)

    else:
        st.sidebar.warning("Enter Correct Password")

# ---------------- STUDENT PANEL ---------------- #

elif role == "Student":

    st.header("Mark Attendance")

    roll = st.number_input("Enter Roll Number",step=1)
    otp = st.number_input("Enter OTP",step=1)

    subject = st.selectbox(
        "Select Subject",
        ["DBMS","Web Technology"]
    )

    if st.button("Mark Attendance"):
        mark_attendance(roll,otp,subject)
