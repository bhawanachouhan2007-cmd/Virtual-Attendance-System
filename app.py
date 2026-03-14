import streamlit as st
import sqlite3 as sql
from datetime import datetime
import random
import qrcode
import pandas as pd

# session state for OTP
if "current_otp" not in st.session_state:
    st.session_state.current_otp = None

# database connection
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
    Status TEXT
)
""")

conn.commit()

st.title("Virtual Attendance System")

menu = st.sidebar.selectbox(
    "Select Role",
    ["Teacher", "Student"]
)

# ---------------- TEACHER PANEL ----------------

if menu == "Teacher":

    password = st.text_input("Enter Teacher Password", type="password")

    if password == "teacher123":

        st.success("Login Successful")

        option = st.selectbox(
            "Select Action",
            ["Add Student", "Generate QR", "View Attendance", "Total Students"]
        )

        # ADD STUDENT
        if option == "Add Student":

            roll = st.number_input("Enter Roll Number", step=1)
            name = st.text_input("Enter Name")

            if st.button("Add Record"):
                cursor.execute(
                    "INSERT INTO students VALUES (?,?)",
                    (roll, name)
                )
                conn.commit()
                st.success("Student Added Successfully")

        # GENERATE QR
        elif option == "Generate QR":

            if st.button("Generate OTP QR"):

                num = random.randint(1000, 9999)
                st.session_state.current_otp = num

                qr = qrcode.make(num)
                qr.save("qrcode.png")

                st.image("qrcode.png")
                st.success(f"OTP Generated: {num}")

        # VIEW ATTENDANCE
        elif option == "View Attendance":

            date = st.text_input("Enter Date (dd-mm-yyyy)")

            if st.button("Show Attendance"):

                cursor.execute(
                    "SELECT * FROM attendance WHERE Date=? ORDER BY Roll_no.",
                    (date,Roll_no)
                )

                records = cursor.fetchall()

                if not records:
                    st.warning("No Attendance Found")

                else:
                    df = pd.DataFrame(records,
                    columns=["Roll No.", "Name", "Date", "Time", "Status"])
                    st.dataframe(df)

        # COUNT STUDENTS
        elif option == "Total Students":

            date = st.text_input("Enter Date")

            if st.button("Show Count"):

                cursor.execute(
                    "SELECT COUNT(Roll_no) FROM attendance WHERE Date=?",
                    (date,)
                )

                total = cursor.fetchone()

                st.write("Students Present:", total[0])

    else:
        st.warning("Enter Correct Password")


# ---------------- STUDENT PANEL ----------------

elif menu == "Student":

    roll = st.number_input("Enter Roll Number", step=1)
    otp = st.number_input("Enter OTP", step=1)

    if st.button("Mark Attendance"):

        cursor.execute(
            "SELECT * FROM students WHERE Roll_no=?",
            (roll,)
        )

        student = cursor.fetchone()

        if student is None:
            st.error("Student Not Registered")

        else:

            if otp != st.session_state.current_otp:
                st.error("Invalid OTP")

            else:

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

                else:

                    cursor.execute(
                        "INSERT INTO attendance VALUES (?,?,?,?,?)",
                        (roll, name, date, time, "Present")
                    )

                    conn.commit()

                    st.success("Attendance Marked Successfully")
