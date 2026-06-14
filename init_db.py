import sqlite3

conn = sqlite3.connect("student_tracker.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    roll_number TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number TEXT,
    subject TEXT,
    marks REAL,
    FOREIGN KEY (roll_number)
        REFERENCES students(roll_number)
)
""")

conn.commit()
conn.close()

print("Database created successfully!")