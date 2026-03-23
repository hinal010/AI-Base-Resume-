
from database import conn
from auth import hash_password

def create_user(username: str, full_name: str, email: str, password: str):
    hashed = hash_password(password)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (username, full_name, email, hashed_password) VALUES (?, ?, ?, ?)",
        (username, full_name, email, hashed)
    )
    conn.commit()
    return get_user(username)

def get_user(username: str):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, full_name, email, hashed_password FROM users WHERE username = ?",
        (username,)
    )
    row = cur.fetchone()
    return dict(row) if row else None

def get_user_by_email(email: str):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, full_name, email, hashed_password FROM users WHERE email = ?",
        (email,)
    )
    row = cur.fetchone()
    return dict(row) if row else None


def create_user_profile(user_id, username, full_name, email, phone="", location="", profile_image=""):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_profile (user_id, username, full_name, email, phone, location, profile_image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, full_name, email, phone, location, profile_image))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e


# Fetch profile by user_id
def get_user_profile(user_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row:
        keys = ["id", "user_id", "username", "full_name", "email", "phone", "location", "profile_image"]
        return dict(zip(keys, row))
    return None


def update_user_profile(user_id, full_name=None, email=None, phone=None, location=None, profile_image=None):
    cur = conn.cursor()

    # Check if profile exists
    cur.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if row is None:
        # Insert a new profile row
        cur.execute(
            """
            INSERT INTO user_profile (user_id, full_name, email, phone, location, profile_image)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                full_name or "",
                email or "",
                phone or "",
                location or "",
                profile_image or ""
            )
        )
        conn.commit()
    else:
        # Update existing row
        updates = []
        params = []

        if full_name is not None:
            updates.append("full_name = ?")
            params.append(full_name)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if phone is not None:
            updates.append("phone = ?")
            params.append(phone)
        if location is not None:
            updates.append("location = ?")
            params.append(location)
        if profile_image is not None:
            updates.append("profile_image = ?")
            params.append(profile_image)

        if updates:
            params.append(user_id)
            query = f"UPDATE user_profile SET {', '.join(updates)} WHERE user_id = ?"
            cur.execute(query, params)
            conn.commit()

    # Return the profile
    cur.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row:
        keys = ["id", "user_id", "username", "full_name", "email", "phone", "location", "profile_image"]
        return dict(zip(keys, row))
    return None
def add_education(user_id, degree, course, institution, start_year, end_year, grade):
    
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO education
    (user_id, degree, course, institution, start_year, end_year, grade)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, degree, course, institution, start_year, end_year, grade))

    conn.commit()

def get_education(user_id):

    cur = conn.cursor()

    cur.execute("""
    SELECT 
        e.id,
        e.degree,
        e.course,
        e.institution,
        d.degree_name,
        c.course_name,
        i.institute_name,
        e.start_year,
        e.end_year,
        e.grade
    FROM education e
    JOIN degree_master d ON e.degree = d.id
    JOIN course_master c ON e.course = c.id
    JOIN institute_master i ON e.institution = i.id
    WHERE e.user_id = ?
    """, (user_id,))

    rows = cur.fetchall()
    
    return rows

def update_education(edu_id, degree,course, institution, start_year, end_year, grade):

    cur = conn.cursor()

    cur.execute("""
    UPDATE education
    SET degree = ?, course = ?,institution = ?, start_year = ?, end_year = ?, grade = ?
    WHERE id = ?
    """, (degree,course, institution, start_year, end_year, grade, edu_id))
    conn.commit()

def delete_education(edu_id,user_id):

   
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM education WHERE id = ? AND user_id = ?",
        (edu_id, user_id)
    )

    conn.commit()

def get_degrees():
    cur = conn.cursor()

    cur.execute("SELECT id, degree_name FROM degree_master")
    rows = cur.fetchall()

    

    return [{"id": r[0], "name": r[1]} for r in rows]

def get_courses_by_degree(degree_id):

    cur = conn.cursor()

    cur.execute(
        "SELECT id, course_name FROM course_master WHERE degree_id=?",
        (degree_id,)
    )

    rows = cur.fetchall()
    

    return [{"id": r[0], "name": r[1]} for r in rows]
def get_institutes_by_course(course_id):
    cur = conn.cursor()

    cur.execute(
        "SELECT id, institute_name FROM institute_master WHERE course_id=?",
        (course_id,)
    )

    rows = cur.fetchall()

    return [{"id": r[0], "name": r[1]} for r in rows]

def get_experience_types():
    cur = conn.cursor()
    cur.execute("SELECT id, type_name FROM experience_type_master")
    return cur.fetchall()

def get_job_titles():
    cur = conn.cursor()
    cur.execute("SELECT id, job_title FROM job_title_master")
    return cur.fetchall()

def add_job_title(job_title):
    cur = conn.cursor()
    cur.execute("INSERT INTO job_title_master (job_title) VALUES (?)", (job_title,))
    conn.commit()
def add_experience(user_id, experience_type, job_title_id, custom_job_title,
                   company_name, start_year, end_year, current_job, responsibilities):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO experience
        (user_id, experience_type, job_title_id, custom_job_title, company_name,
         start_year, end_year, current_job, responsibilities)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, experience_type, job_title_id, custom_job_title,
        company_name, start_year, end_year, current_job, responsibilities
    ))
    conn.commit()


def get_experience(user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT
            e.id,
            e.experience_type,
            etm.type_name,
            e.job_title_id,
            COALESCE(j.job_title, e.custom_job_title) as job_title,
            e.company_name,
            e.start_year,
            e.end_year,
            e.current_job,
            e.responsibilities
        FROM experience e
        JOIN experience_type_master etm ON e.experience_type = etm.id
        LEFT JOIN job_title_master j ON e.job_title_id = j.id
        WHERE e.user_id = ?
    """, (user_id,))
    return cur.fetchall()


def update_experience(exp_id, experience_type, job_title_id, custom_job_title,
                      company_name, start_year, end_year, current_job, responsibilities):
    cur = conn.cursor()
    cur.execute("""
        UPDATE experience
        SET experience_type = ?, job_title_id = ?, custom_job_title = ?,
            company_name = ?, start_year = ?, end_year = ?, current_job = ?,
            responsibilities = ?
        WHERE id = ?
    """, (
        experience_type, job_title_id, custom_job_title,
        company_name, start_year, end_year, current_job,
        responsibilities, exp_id
    ))
    conn.commit()


def delete_experience(exp_id, user_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM experience WHERE id = ? AND user_id = ?", (exp_id, user_id))
    conn.commit()

def add_certification(user_id, certification_name, organization, cert_date):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO certification (user_id, certification_name, organization, cert_date)
        VALUES (?, ?, ?, ?)
    """, (user_id, certification_name, organization, cert_date))
    conn.commit()


def get_certifications(user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, certification_name, organization, cert_date
        FROM certification
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))
    return cur.fetchall()


def update_certification(cert_id, certification_name, organization, cert_date):
    cur = conn.cursor()
    cur.execute("""
        UPDATE certification
        SET certification_name = ?, organization = ?, cert_date = ?
        WHERE id = ?
    """, (certification_name, organization, cert_date, cert_id))
    conn.commit()


def delete_certification(cert_id, user_id):
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM certification
        WHERE id = ? AND user_id = ?
    """, (cert_id, user_id))
    conn.commit()


def get_selected_job_titles(user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT
            ujt.id,
            ujt.job_title_id,
            COALESCE(jtm.job_title, ujt.custom_job_title) AS job_title,
            ujt.custom_job_title
        FROM user_job_titles ujt
        LEFT JOIN job_title_master jtm ON ujt.job_title_id = jtm.id
        WHERE ujt.user_id = ?
    """, (user_id,))
    return cur.fetchall()


def save_job_title_selection(user_id, job_title_id=None, custom_job_title=None, role_selection_id=None):
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM user_job_titles
        WHERE user_id = ?
    """, (user_id,))
    existing = cur.fetchone()

    if existing:
        cur.execute("""
            UPDATE user_job_titles
            SET job_title_id = ?, custom_job_title = ?
            WHERE user_id = ?
        """, (job_title_id, custom_job_title, user_id))
    else:
        cur.execute("""
            INSERT INTO user_job_titles (user_id, job_title_id, custom_job_title)
            VALUES (?, ?, ?)
        """, (user_id, job_title_id, custom_job_title))

    conn.commit()


def delete_job_title_selection(role_selection_id, user_id):
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM user_job_titles
        WHERE id = ? AND user_id = ?
    """, (role_selection_id, user_id))
    conn.commit()