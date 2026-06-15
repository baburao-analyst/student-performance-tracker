import sqlite3

conn = sqlite3.connect("student_tracker.db")
cursor = conn.cursor()

print("\n===== STUDENTS TABLE =====")

cursor.execute("SELECT * FROM students")

for row in cursor.fetchall():
    print(f"Roll Number: {row[0]} | Name: {row[1]}")

print("\n===== GRADES TABLE =====")

cursor.execute("SELECT * FROM grades")

for row in cursor.fetchall():
    print(
        f"ID: {row[0]} | Roll: {row[1]} | Subject: {row[2]} | Marks: {row[3]}"
    )

conn.close()