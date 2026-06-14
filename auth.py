# auth.py
import bcrypt
from database import get_connection


def register_user(email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cur.fetchone():
        conn.close()
        return False, "Email already registered."

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cur.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hash))
    conn.commit()
    conn.close()
    return True, "Registration successful!"


def login_user(email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None, "No account found with this email."

    if bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return row["id"], "Login successful!"
    else:
        return None, "Incorrect password."