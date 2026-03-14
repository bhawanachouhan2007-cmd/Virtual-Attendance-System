import streamlit as st
import sqlite3 as sql
from datetime import datetime
import random
import qrcode
import pandas as pd

# Session state
if "current_otp" not in st.session_state:
    st.session_state.current_otp = None

if "otp_time" not in st.session_state:
    st.session_state.otp_time = None

# Database connection
conn = sql.connect("attendance.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    Roll_no INTEGER PRIMARY KEY,
    Name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    Roll_no INTEGER,
    Name TEXT,
    Date TEXT,
    Time TEXT,
    Subject TEXT,
    Status TEXT
)
""")

conn.commit()

st.title("Virtual Attendance System")

menu = st.sidebar.selectbox("Select Role", ["Teacher","Student"])

# ---------------- TEACHER PANEL ----------------

if menu == "Teacher":

    password = st.text_input("Enter Teacher Password", type="password")

    if password == "teacher123":

        st.success("Login Successful")

        option = st.selectbox(
            "Select Action",
            ["Add Student","Generate QR","View Attendance","Total Students","Subject Attendance"]
        )

        # ADD STUDENT
        if option == "Add Student":

            roll = st.number_input("Enter Roll Number", step=1)
            name = st.text_input("Enter Name")

            if st.button("Add Record"):

                cursor.execute(
                    "INSERT INTO students VALUES (?,?)",
                    (roll,name)
                )

                conn.commit()

                st.success("Record Added Successfully")

        # GENERATE QR
        elif option == "Generate QR":

            if st.button("Generate QR"):

                num = random.randint(1000,9999)

                st.session_state.current_otp = num
                st.session_state.otp_time = datetime.now()

                qr = qrcode.make(num)
                qr.save("qrcode.png")

                st.image("qrcode.png")

                st.success(f"OTP Generated: {num}")
                st.info("OTP expires in 30 seconds")

        # VIEW ATTENDANCE
        elif option == "View Attendance":

            date = st.text_input("Enter Date (dd-mm-yyyy)")
            subject = st.text_input("Enter Subject").lower()

            if st.button("Show Attendance"):

                cursor.execute(
                    "SELECT * FROM attendance WHERE Date=? AND Subject=? ORDER BY Roll_no",
                    (date,subject)
                )

                records = cursor.fetchall()

                if not records:
                    st.warning("No Attendance List Found")

                else:

                    df = pd.DataFrame(
                        records,
                        columns=["Roll No","Name","Date","Time","Subject","Status"]
                    )

                    st.dataframe(df)

        # TOTAL STUDENTS
        elif option == "Total Students":

            date = st.text_input("Enter Date")

            if st.button("Show Count"):

                cursor.execute(
                    "SELECT COUNT(Roll_no) FROM attendance WHERE Date=?",
                    (date,)
                )

                total = cursor.fetchone()

                st.write("Students Present:", total[0])

        # SUBJECT ATTENDANCE
        elif option == "Subject Attendance":

            subject = st.selectbox(
                "Select Subject",
                ["DBMS","Web Technology"]
            )
            if st.button("Show Subject Attendance"):

                cursor.execute(
                    "SELECT * FROM attendance WHERE Subject=? ORDER BY Roll_no",
                    (subject,)
                )

                records = cursor.fetchall()

                if not records:
                    st.warning("No Records Found")

                else:

                    df = pd.DataFrame(
                        records,
                        columns=["Roll No","Name","Date","Time","Subject","Status"]
                    )

                    st.dataframe(df)

    else:
        st.warning("Enter Correct Password")

# ---------------- STUDENT PANEL ----------------

elif menu == "Student":

    roll = st.number_input("Enter Roll Number", step=1)
    otp = st.number_input("Enter OTP", step=1)
    subject = st.text_input("Enter Subject").lower()

    if st.button("Mark Attendance"):

        cursor.execute(
            "SELECT * FROM students WHERE Roll_no=?",
            (roll,)
        )

        student = cursor.fetchone()

        if student is None:
            st.error("Student Not Registered")
            st.stop()

        # OTP expiry check
        otp_time = st.session_state.otp_time

        if otp_time is None:
            st.error("Teacher has not generated OTP")
            st.stop()

        current_time = datetime.now()
        time_diff = (current_time - otp_time).total_seconds()

        if time_diff > 30:
            st.error("OTP Expired. Ask teacher to generate new QR.")
            st.stop()

        # OTP validation
        if otp != st.session_state.current_otp:
            st.error("Invalid OTP")
            st.stop()

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
            st.stop()

        cursor.execute(
            "INSERT INTO attendance VALUES (?,?,?,?,?,?)",
            (roll,name,date,time,subject,"Present")
        )

        conn.commit()

        st.success("Attendance Marked Successfully")
