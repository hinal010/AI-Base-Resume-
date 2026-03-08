
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