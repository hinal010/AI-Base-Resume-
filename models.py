from database import conn

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    full_name TEXT,
    email TEXT UNIQUE,
    hashed_password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    username TEXT,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    location TEXT,
    profile_image TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    degree TEXT,
    course TEXT,
    institution TEXT,
    start_year TEXT,
    end_year TEXT,
    grade TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS degree_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    degree_name TEXT 
);
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS course_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL,
    degree_id INTEGER,
    FOREIGN KEY (degree_id) REFERENCES degree_master(id) ON DELETE CASCADE
);
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS institute_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    institute_name TEXT NOT NULL,
    course_id INTEGER,
    FOREIGN KEY (course_id) REFERENCES course_master(id) ON DELETE CASCADE
);
""")
cur.execute("""
CREATE TABLE  IF NOT EXISTS experience_type_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL
);
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS job_title_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT NOT NULL
);
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    experience_type INTEGER,
    job_title_id INTEGER,
    custom_job_title TEXT,
    company_name TEXT,
    start_year TEXT,
    end_year TEXT,
    current_job INTEGER DEFAULT 0,
    responsibilities TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (experience_type) REFERENCES experience_type_master(id),
    FOREIGN KEY (job_title_id) REFERENCES job_title_master(id)
);
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS certification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    certification_name TEXT NOT NULL,
    organization TEXT NOT NULL,
    cert_date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")
conn.commit()

