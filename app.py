import streamlit as st
import sqlite3 as sql
from datetime import datetime

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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    ["Student", "Teacher"]
)

# ---------------- TEACHER ----------------

if menu == "Teacher":

    password = st.sidebar.text_input("Enter Teacher Password", type="password")

    if password == "teacher123":

        option = st.selectbox(
            "Teacher Panel",
            ["Add Student", "View Attendance"]
        )

        if option == "Add Student":

            roll = st.number_input("Enter Roll Number", step=1)
            name = st.text_input("Enter Student Name")

            if st.button("Add Student"):
                cursor.execute(
                    "INSERT INTO students VALUES (?,?)",
                    (roll, name)
                )
                conn.commit()
                st.success("Student Added Successfully")

        elif option == "View Attendance":

            cursor.execute("SELECT * FROM attendance")
            data = cursor.fetchall()

            st.write("Attendance Records")
            st.table(data)

    elif password != "":
        st.error("Wrong Password")

# ---------------- STUDENT ----------------

elif menu == "Student":

    st.subheader("Mark Attendance")

    roll = st.number_input("Enter Roll Number", step=1)

    if st.button("Mark Attendance"):

        cursor.execute(
            "SELECT * FROM students WHERE Roll_no = ?",
            (roll,)
        )

        student = cursor.fetchone()

        if student is None:
            st.error("Student Not Registered")
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
                st.warning("Attendance Already Marked Today")

            else:

                cursor.execute(
                    "INSERT INTO attendance (Roll_no,Name,Date,Time,Status) VALUES (?,?,?,?,?)",
                    (roll, name, date, time, "Present")
                )

                conn.commit()

                st.success("Attendance Marked Successfully")
