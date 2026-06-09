import sqlite3
import os

DB_FOLDER = "database"
DB_PATH = os.path.join(DB_FOLDER, "attendance.db")

os.makedirs(DB_FOLDER, exist_ok=True)

def get_connection():
    print("DB PATH =", os.path.abspath(DB_PATH))
    return sqlite3.connect(DB_PATH)
def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        name TEXT NOT NULL,
        roll_no TEXT NOT NULL,
        photo_path TEXT,
        embedding BLOB
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        name TEXT NOT NULL,
        roll_no TEXT NOT NULL,
        attendance_date TEXT NOT NULL,
        attendance_time TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()