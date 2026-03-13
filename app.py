import streamlit as st
import pandas as pd
import sqlite3 as sql
from datetime import datetime
import random
import qrcode

# ---------------- OTP ----------------
if "current_otp" not in st.session_state:
    st.session_state.current_otp = None


# ---------------- Database ----------------

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


# ---------------- FUNCTIONS ----------------

def add_record(rol,name):

    cursor.execute(
        "INSERT INTO students VALUES (?,?)",
        (rol,name)
    )

    conn.commit()

    st.success("Record Added Successfully")


def generate_QR():

    num = random.randint(1000,9999)

    st.session_state.current_otp = num

    img = qrcode.make(num)

    img.save("qrcode.png")

    st.image("qrcode.png")

    st.success(f"OTP Generated : {num}")


def mark_attendance(roll,otp):

    cursor.execute(
    "SELECT * FROM students WHERE Roll_no=?",
    (roll,)
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
    (roll,date)
    )

    if otp != st.session_state.current_otp:

        st.error("Invalid OTP")

        return

    if cursor.fetchone():

        st.warning("Attendance Already Marked")

        return

    cursor.execute(
    "INSERT INTO attendance VALUES (?,?,?,?,?)",
    (roll,Name,date,time,"Present")
    )

    conn.commit()

    st.success("Attendance Marked Successfully")


def see_attendance():

    cursor.execute("SELECT * FROM attendance")

    data = cursor.fetchall()

    df = pd.DataFrame(
        data,
        columns=["Roll","Name","Date","Time","Status"]
    )

    st.dataframe(df)


# ---------------- STREAMLIT UI ----------------

st.title("Virtual Attendance System")

menu = st.sidebar.selectbox(
"Select User",
["Teacher","Student"]
)


# ---------------- TEACHER ----------------

if menu == "Teacher":

    password = st.text_input(
    "Enter Password",
    type="password"
    )

    if password == "teacher123":

        option = st.selectbox(
        "Select Option",
        ["Add Student","Generate QR","Attendance List"]
        )

        if option == "Add Student":

            rol = st.number_input(
            "Enter Roll Number",
            step=1
            )

            name = st.text_input("Enter Name")

            if st.button("Add Record"):

                add_record(rol,name)


        elif option == "Generate QR":

            if st.button("Generate QR Code"):

                generate_QR()


        elif option == "Attendance List":

            see_attendance()

    elif password != "":
        st.error("Wrong Password")


# ---------------- STUDENT ----------------

if menu == "Student":

    st.header("Student Attendance")

    roll = st.number_input(
    "Enter Roll Number",
    step=1
    )

    otp = st.number_input(
    "Enter OTP from QR",
    step=1
    )

    if st.button("Mark Attendance"):

        mark_attendance(roll,otp)
