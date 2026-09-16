import bcrypt
from datetime import datetime
from db import get_db_conn
import sqlite3

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def verify_password(password: str, password_hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash)

def create_user(username: str, email: str, password: str, role="user"):
    conn = get_db_conn()
    cur = conn.cursor()
    try:
        ph = hash_password(password)
        cur.execute("INSERT INTO users (username, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
                    (username, email, ph, role, datetime.now().isoformat()))
        conn.commit()
        return True, "User registered successfully!"
    except sqlite3.IntegrityError as e:
        if "email" in str(e):
            return False, "Email already exists"
        else:
            return False, "Username already exists"
    finally:
        conn.close()

def authenticate_user(username: str, password: str):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False, "User not found"
    if verify_password(password, row["password_hash"]):
        return True, dict(row)
    return False, "Incorrect password"

def reset_password(email: str, new_password: str):
    from db import get_db_conn
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, "Email not found"
    ph = hash_password(new_password)
    cur.execute("UPDATE users SET password_hash = ? WHERE email = ?", (ph, email))
    conn.commit()
    conn.close()
    return True, "Password reset successfully! Please login with new password."