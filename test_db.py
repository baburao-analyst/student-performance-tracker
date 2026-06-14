import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vijay",
    database="student_tracker"
)

print("Connected successfully!")

conn.close()