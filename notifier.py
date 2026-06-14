import smtplib
from email.mime.text import MIMEText
from datetime import date
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_FILE = "planner.db"
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_APP_PASSWORD")


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def send_email(receiver_email, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print(f"📧 Email sent to {receiver_email}")

    except Exception as e:
        print(f"❌ Email error for {receiver_email}: {e}")


def check_deadlines():
    conn = get_connection()
    cur = conn.cursor()

    today = date.today().isoformat()

    # Get all users
    cur.execute("SELECT id, email FROM users")
    users = cur.fetchall()

    for user in users:
        user_id = user["id"]
        user_email = user["email"]

        # Get tasks due today for this user
        cur.execute("""
            SELECT id, name FROM tasks
            WHERE user_id = ?
            AND deadline = ?
            AND completed = 0
            AND notified = 0
        """, (user_id, today))

        due_tasks = cur.fetchall()

        if due_tasks:
            body = f"Hi {user_email},\n\nThe following tasks are due today:\n\n"
            body += "\n".join(f"- {t['name']}" for t in due_tasks)
            body += "\n\nStay productive! 🚀\n— AI Smart Day Planner"

            send_email(user_email, "⚠️ Task Deadline Reminder", body)

            # Mark tasks as notified
            task_ids = [t["id"] for t in due_tasks]
            cur.executemany(
                "UPDATE tasks SET notified = 1 WHERE id = ?",
                [(tid,) for tid in task_ids]
            )
            conn.commit()
        else:
            print(f"No tasks due today for {user_email}")

    conn.close()


if __name__ == "__main__":
    print("🚀 Checking task deadlines...")
    check_deadlines()
    print("✅ Done.")