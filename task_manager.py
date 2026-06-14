import sqlite3
import bcrypt

DB_FILE = "planner.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            deadline TEXT,
            notified INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()


initialize()


# ================= AUTH =================
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


# ================= TASKS =================
def load_tasks(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY id", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_task(user_id, name, deadline=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (user_id, name, completed, deadline, notified) VALUES (?, ?, 0, ?, 0)",
        (user_id, name, deadline)
    )
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def update_task(task_id, completed):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET completed = ? WHERE id = ?", (int(completed), task_id))
    conn.commit()
    conn.close()


def clear_tasks(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()