import sqlite3

def init_db():
    # Connect to SQLite database
    connection = sqlite3.connect("student.db")
    cursor = connection.cursor()

    # Drop existing table if needed
    cursor.execute("DROP TABLE IF EXISTS STUDENT")

    # Create new detailed STUDENT table
    table_info = """
    CREATE TABLE STUDENT(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME VARCHAR(255),
        AGE INTEGER,
        GENDER VARCHAR(10),
        CLASS VARCHAR(100),
        SECTION VARCHAR(10),
        ROLL_NO VARCHAR(20),
        MARKS INTEGER,
        EMAIL VARCHAR(100),
        PHONE VARCHAR(15),
        ADDRESS TEXT,
        ADMISSION_DATE DATE,
        ATTENDANCE_PCT FLOAT,
        SCHOLARSHIP BOOLEAN
    );
    """
    cursor.execute(table_info)

    # Sample student entries
    students = [
        ("Krishna Verma", 21, "Male", "Data Science", "A", "DS202301", 90, "krishna@email.com", "9876543210", "Delhi", "2022-08-01", 92.5, True),
        ("Aanya Sharma", 20, "Female", "Data Science", "A", "DS202302", 85, "aanya@email.com", "9876501234", "Mumbai", "2022-08-01", 89.0, True),
        ("Raghav Singh", 22, "Male", "Computer Vision", "B", "CV202301", 88, "raghav@email.com", "9876511111", "Chennai", "2021-07-15", 76.0, False),
        ("Mehak Gupta", 21, "Female", "AI & ML", "C", "AI202301", 93, "mehak@email.com", "9876522222", "Kolkata", "2023-01-10", 96.4, True),
        ("Arjun Rawat", 23, "Male", "Cyber Security", "A", "CS202301", 70, "arjun@email.com", "9876533333", "Hyderabad", "2020-09-12", 68.0, False),
        ("Sarah Ali", 20, "Female", "UI/UX Design", "B", "UX202301", 95, "sarah@email.com", "9876544444", "Bengaluru", "2023-06-18", 99.9, True),
        ("Devansh Mehta", 21, "Male", "Full Stack", "D", "FS202301", 88, "devansh@email.com", "9876555555", "Jaipur", "2022-04-10", 90.0, False)
    ]

    cursor.executemany("""
        INSERT INTO STUDENT(NAME, AGE, GENDER, CLASS, SECTION, ROLL_NO, MARKS, EMAIL, PHONE, ADDRESS, ADMISSION_DATE, ATTENDANCE_PCT, SCHOLARSHIP)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, students)

    connection.commit()
    connection.close()
