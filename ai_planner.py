from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_plan(tasks):
    pending = [task["name"] for task in tasks if not task["completed"]]

    if not pending:
        return "## 🎉 No pending tasks!\nYou're all caught up. Enjoy your free time!"

    prompt = f"""
You are an AI Productivity Assistant.

Analyze these tasks and generate a beautiful plan.

Return in Markdown format.

## 🔴 High Priority
- task

## 🟡 Medium Priority
- task

## 🟢 Low Priority
- task

## 🕒 Suggested Timetable
09:00 - 10:00 Task

## 💡 Productivity Tips
- Tip 1
- Tip 2

## 🔥 Daily Motivation
One motivational quote.

Tasks:
{pending}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return (
            "## ⚠️ AI Plan Unavailable\n"
            "You've hit the daily request limit for the free Gemini API tier "
            "(20 requests/day). Please try again later, or upgrade your plan.\n\n"
            f"_Error details: {str(e)}_"
        )