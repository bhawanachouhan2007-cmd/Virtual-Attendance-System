import streamlit as st
import pandas as pd
import sqlite3 as sql
from datetime import datetime
import random
import qrcode
from streamlit_qrcode_scanner import qrcode_scanner

current_otp = None

conn = sql.connect("attendance.db", check_same_thread=False)
cursor = conn.cursor()

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


# ---------------- TEACHER FUNCTIONS ----------------

def add_record(rol, name):
    cursor.execute("INSERT INTO students VALUES (?,?)",(rol,name))
    conn.commit()
    st.success("Record Added Successfully")


def generate_QR():
    global current_otp

    num = random.randint(1000,9999)
    current_otp = num

    img = qrcode.make(num)
    img.save("qrcode.png")

    st.image("qrcode.png")
    st.success(f"OTP Generated : {num}")


def see_attendance():
    cursor.execute("SELECT * FROM attendance")
    data = cursor.fetchall()

    df = pd.DataFrame(data,columns=["Roll","Name","Date","Time","Status"])
    st.dataframe(df)


# ---------------- STUDENT FUNCTION ----------------

def mark_attendance(Roll_no,entered_otp):

    cursor.execute("SELECT * FROM students WHERE Roll_no = ?",(Roll_no,))
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
    (Roll_no,date)
    )

    if entered_otp != current_otp:
        st.error("Invalid OTP")
        return

    if cursor.fetchone():
        st.warning("Attendance Already Marked")
        return

    cursor.execute(
    "INSERT INTO attendance VALUES (?,?,?,?,?)",
    (Roll_no,Name,date,time,"Present")
    )

    conn.commit()

    st.success("Attendance Marked Successfully")


# ---------------- STREAMLIT UI ----------------

st.title("Virtual Attendance System")

menu = st.sidebar.selectbox("Select User",["Teacher","Student"])

# ----------- TEACHER PANEL -----------

if menu == "Teacher":

    password = st.text_input("Enter Password",type="password")

    if password == "teacher123":

        option = st.selectbox("Select Option",
        ["Add Student","Generate QR","Attendance List"])

        if option == "Add Student":

            rol = st.number_input("Enter Roll Number",step=1)
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


# ----------- STUDENT PANEL -----------

elif menu == "Student":

    st.header("Student Attendance")

    roll = st.number_input("Enter Roll Number",step=1)

    st.write("Scan QR from Board")

    qr_data = qrcode_scanner()

    if qr_data:
        st.success("QR Detected")

        entered_otp = int(qr_data)

        if st.button("Mark Attendance"):
            mark_attendance(roll,entered_otp)
