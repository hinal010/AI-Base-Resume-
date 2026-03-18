import sqlite3

conn = sqlite3.connect("users.db")
cur = conn.cursor()

# ==============================
# 1. INSERT DEGREES
# ==============================
degrees = [
    ("High School",),
    ("Bachelor",),
    ("Master",),
    ("Diploma",),
    ("PhD",)
]

cur.executemany(
    "INSERT INTO degree_master (degree_name) VALUES (?)",
    degrees
)

# ==============================
# 2. GET DEGREE IDS (SMART WAY)
# ==============================
cur.execute("SELECT id, degree_name FROM degree_master")
degree_rows = cur.fetchall()

degree_map = {name: id for (id, name) in degree_rows}

# ==============================
# 3. INSERT COURSES (FULL LIST)
# ==============================
courses = [

    # High School
    ("Science", degree_map["High School"]),
    ("Commerce", degree_map["High School"]),
    ("Arts", degree_map["High School"]),

    # Bachelor
    ("BCA", degree_map["Bachelor"]),
    ("BCom", degree_map["Bachelor"]),
    ("BBA", degree_map["Bachelor"]),
    ("BSc", degree_map["Bachelor"]),
    ("BA", degree_map["Bachelor"]),
    ("BTech", degree_map["Bachelor"]),

    # Master
    ("MCA", degree_map["Master"]),
    ("MBA", degree_map["Master"]),
    ("MCom", degree_map["Master"]),
    ("MSc", degree_map["Master"]),
    ("MA", degree_map["Master"]),
    ("MTech", degree_map["Master"]),

    # Diploma
    ("Diploma in Computer Engineering", degree_map["Diploma"]),
    ("Diploma in Mechanical Engineering", degree_map["Diploma"]),
    ("Diploma in Civil Engineering", degree_map["Diploma"]),

    # PhD
    ("PhD in Computer Science", degree_map["PhD"]),
    ("PhD in Management", degree_map["PhD"]),
    ("PhD in Commerce", degree_map["PhD"]),
    ("PhD in Architecture", degree_map["PhD"])
]

cur.executemany(
    "INSERT INTO course_master (course_name, degree_id) VALUES (?, ?)",
    courses
)

# ==============================
# 4. GET COURSE IDS (SMART WAY)
# ==============================
cur.execute("SELECT id, course_name FROM course_master")
course_rows = cur.fetchall()

course_map = {name: id for (id, name) in course_rows}

# ==============================
# 5. INSERT INSTITUTES
# ==============================
institutes = [
    
    # --- Science Stream ---
    ("St. Xavier's High School, Loyola Hall", course_map["Science"]),
    ("Sheth C.N. Vidyalaya", course_map["Science"]),
    ("Nirma Vidhyavihar", course_map["Science"]),
    ("Kendriya Vidyalaya (IIT Gandhinagar/SAC)", course_map["Science"]),
    ("Maharaja Agrasen Vidyalaya", course_map["Science"]),

    # --- Commerce Stream ---
    ("H.L. Higher Secondary School", course_map["Commerce"]),
    ("Udgam School for Children", course_map["Commerce"]),
    ("Delhi Public School (DPS) Bopal", course_map["Commerce"]),
    ("Zydus School for Excellence", course_map["Commerce"]),
    ("The New High School", course_map["Commerce"]),

    # --- Arts Stream ---
    ("Mount Carmel High School", course_map["Arts"]),
    ("Ahmedabad International School (AIS)", course_map["Arts"]),
    ("Redbricks School", course_map["Arts"]),
    ("Ankur High School", course_map["Arts"]),
    ("Eklavya School", course_map["Arts"]),

    # --- Bachelor Degrees ---
    ("St. Xavier's College", course_map["BCA"]),
    ("L.D. College of Engineering", course_map["BTech"]), # Referred to as B.E locally
    ("H.L. College of Commerce", course_map["BCom"]),
    ("Nirma University", course_map["BBA"]),
    ("Ahmedabad University", course_map["BSc"]),
    ("L.D. Arts College", course_map["BA"]),
    ("Silver Oak University", course_map["BTech"]),

    # --- Master Degrees ---
    ("B.K. School of Business Management", course_map["MBA"]),
    ("IIM Ahmedabad", course_map["MBA"]),
    ("Nirma University", course_map["MCA"]),
    ("Gujarat University", course_map["MCom"]),
    ("St. Xavier's College", course_map["MSc"]),
    ("L.D. College of Engineering", course_map["MTech"]), # Referred to as M.E
    ("Ahmedabad University", course_map["MA"]),

    # --- Diploma Programs ---
    ("Government Polytechnic Ahmedabad", course_map["Diploma in Computer Engineering"]),
    ("Government Polytechnic Ahmedabad", course_map["Diploma in Mechanical Engineering"]),
    ("L.J. Polytechnic", course_map["Diploma in Civil Engineering"]),
    ("R.C. Technical Institute", course_map["Diploma in Computer Engineering"]),

    # --- PhD Programs ---
    ("Gujarat University", course_map["PhD in Computer Science"]),
    ("Nirma University", course_map["PhD in Management"]),
    ("Ahmedabad University", course_map["PhD in Commerce"]),
    ("CEPT University", course_map["PhD in Architecture"])
]

cur.executemany(
    "INSERT INTO institute_master (institute_name, course_id) VALUES (?, ?)",
    institutes
)

# ==============================
# SAVE
# ==============================
conn.commit()
conn.close()

print("✅ All data inserted successfully!")