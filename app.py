import streamlit as st
import re
from datetime import date
import extra_streamlit_components as stx

from task_manager import *
from ai_planner import generate_plan

st.set_page_config(
    page_title="AI Task Planner",
    page_icon="📝",
    layout="wide"
)

# ================= COOKIE MANAGER =================
cookie_manager = stx.CookieManager()

# ================= CUSTOM STYLE =================
st.markdown("""
<style>

html, body, .stApp {
    background: #f6f9f7 !important;
}

.stApp {
    background: linear-gradient(135deg, #f6f9f7, #eef5f1) !important;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 860px;
    margin: auto;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border-radius: 14px !important;
    border: 1px solid #dfe8e3 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 10px;
    transition: 0.2s ease-in-out;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border: 1px solid #8fc0a9 !important;
    transform: translateY(-2px);
}

.stButton > button {
    background: #4a7c59 !important;
    color: white !important;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    padding: 8px 14px;
    transition: 0.2s;
    width: 100%;
}

.stButton > button:hover {
    background: #3f6a4c !important;
    transform: scale(1.02);
}

input, textarea {
    background-color: #ffffff !important;
    color: #1f2d25 !important;
    border: 1px solid #cfe3d7 !important;
    border-radius: 8px !important;
}

.stProgress > div > div > div > div {
    background-color: #8fc0a9;
}

.stCheckbox {
    padding: 6px 0;
}

.streamlit-expanderHeader {
    font-weight: 600;
    color: #4a7c59;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2d5a3d, #4a7c59) !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] label {
    color: white !important;
    font-size: 13px !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
    color: white !important;
    font-weight: 600 !important;
    margin-top: 8px;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.25) !important;
}

section[data-testid="stSidebar"] .stButton > button *,
section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span {
    color: white !important;
}

/* ===== RESPONSIVE / MOBILE ===== */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
    }

    h1 {
        font-size: 22px !important;
    }

    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    div[data-testid="stTextInput"] {
        width: 100% !important;
    }

    section[data-testid="stSidebar"] {
        min-width: 0 !important;
    }

    div[data-testid="metric-container"] {
        padding: 8px !important;
    }

    .stButton > button {
        width: 100% !important;
        font-size: 13px !important;
        padding: 6px 8px !important;
    }
}

@media (max-width: 480px) {
    h1 {
        font-size: 18px !important;
    }

    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
}

</style>
""", unsafe_allow_html=True)


# ================= HELPERS =================
def parse_plan(text):
    sections = {}
    pattern = r"##\s*(.*?)\n(.*?)(?=\n##\s|\Z)"
    matches = re.findall(pattern, text, re.DOTALL)
    for title, content in matches:
        sections[title.strip()] = content.strip()
    return sections


def metric_card(label, value, color, text_color="#1f2d25"):
    st.markdown(f"""
    <div style="background:{color}; border-radius:12px; padding:16px;
                text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.08);">
        <div style="font-size:clamp(20px, 4vw, 28px); font-weight:800;
                    color:{text_color};">{value}</div>
        <div style="font-size:clamp(11px, 2vw, 14px); color:#3f5346;">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def priority_badge(text, bg, color):
    st.markdown(
        f'<span style="background:{bg}; color:{color}; padding:4px 12px; '
        f'border-radius:20px; font-weight:700; '
        f'font-size:clamp(11px, 2vw, 14px);">{text}</span>',
        unsafe_allow_html=True
    )


@st.dialog("📋 Your AI-Generated Plan", width="large")
def show_plan_dialog():
    raw = st.session_state["plan"]
    sections = parse_plan(raw)

    col1, col2, col3 = st.columns(3)

    with col1:
        priority_badge("🔴 High Priority", "#fde2e2", "#c0392b")
        st.write("")
        st.error(sections.get("🔴 High Priority", "No tasks"))

    with col2:
        priority_badge("🟡 Medium Priority", "#fff4d6", "#b7791f")
        st.write("")
        st.warning(sections.get("🟡 Medium Priority", "No tasks"))

    with col3:
        priority_badge("🟢 Low Priority", "#d4f4dd", "#2f855a")
        st.write("")
        st.success(sections.get("🟢 Low Priority", "No tasks"))

    with st.expander("🕒 Timetable"):
        st.markdown(sections.get("🕒 Suggested Timetable", "Not available"))

    with st.expander("💡 Tips"):
        st.markdown(sections.get("💡 Productivity Tips", "Not available"))

    st.info("🔥 " + sections.get("🔥 Daily Motivation", "Stay productive!"))


@st.dialog("📊 Productivity Dashboard", width="large")
def show_progress_dialog():
    tasks = load_tasks(st.session_state["user_id"])
    total = len(tasks)
    done = sum(t["completed"] for t in tasks)
    pending = total - done

    today = date.today().isoformat()
    due_today = sum(
        1 for t in tasks
        if t.get("deadline") == today and not t["completed"]
    )

    if total > 0:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Total", total, "#e8f0eb")
        with c2:
            metric_card("Completed", done, "#d4f4dd", "#2f855a")
        with c3:
            metric_card("Pending", pending, "#fff4d6", "#b7791f")
        with c4:
            metric_card("Due Today", due_today, "#ffe0e0", "#c0392b")

        st.write("")
        progress = done / total
        st.progress(progress)

        if progress == 1:
            st.success("🎉 Perfect day! All tasks completed!")
            st.balloons()
        elif progress > 0.5:
            st.info("💪 You're more than halfway!")
        else:
            st.warning("🚀 Start completing tasks!")

        upcoming = [
            t for t in tasks
            if t.get("deadline") and t["deadline"] > today and not t["completed"]
        ]

        st.write("")
        st.markdown("#### 📅 Upcoming Tasks")
        if upcoming:
            for t in sorted(upcoming, key=lambda x: x["deadline"]):
                st.info(f"📝 {t['name']}   📅 {t['deadline']}")
        else:
            st.success("🎉 No upcoming tasks!")

    else:
        st.info("No tasks yet.")


# ================= RESTORE SESSION FROM COOKIE =================
if "user_id" not in st.session_state:
    cookie_user_id = cookie_manager.get("user_id")
    cookie_user_email = cookie_manager.get("user_email")

    if cookie_user_id and cookie_user_email:
        st.session_state["user_id"] = int(cookie_user_id)
        st.session_state["user_email"] = cookie_user_email


# ================= AUTH SCREEN =================
if "user_id" not in st.session_state:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4a7c59, #8fc0a9);
                padding: 24px; border-radius: 16px; text-align:center;
                margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                max-width: 100%;">
        <h1 style="color:white; margin:0;
                   font-size:clamp(20px, 5vw, 36px);">
            📝 AI Smart Day Planner
        </h1>
        <p style="color:#eafaf0; margin:4px 0 0;
                  font-size:clamp(12px, 2vw, 16px);">
            Plan smarter, not harder 🚀
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔑 Login", "🆕 Register"])

    with tab1:
        with st.container(border=True):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pw")

            if st.button("Login", use_container_width=True):
                user_id, msg = login_user(email.strip(), password)
                if user_id:
                    st.session_state["user_id"] = user_id
                    st.session_state["user_email"] = email.strip()
                    cookie_manager.set("user_id", str(user_id), key="set_uid")
                    cookie_manager.set("user_email", email.strip(), key="set_uemail")
                    st.rerun()
                else:
                    st.error(msg)

    with tab2:
        with st.container(border=True):
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_pw")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_pw2")

            if st.button("Register", use_container_width=True):
                if not new_email.strip() or not new_password:
                    st.error("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, msg = register_user(new_email.strip(), new_password)
                    if success:
                        st.success(msg + " Please log in.")
                    else:
                        st.error(msg)

    st.stop()


# ================= MAIN APP =================
user_id = st.session_state["user_id"]

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:16px 8px 8px;">
        <div style="font-size:40px;">👤</div>
        <div style="color:white; font-weight:700; font-size:13px;
                    word-break:break-all; margin-top:6px;">
            {st.session_state['user_email']}
        </div>
        <hr style="border-color:rgba(255,255,255,0.2); margin:12px 0;">
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        try:
            cookie_manager.delete("user_id", key="del_uid")
            cookie_manager.delete("user_email", key="del_uemail")
        except:
            pass
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Header
st.markdown(f"""
<div style="background: linear-gradient(135deg, #4a7c59, #8fc0a9);
            padding: 16px 24px; border-radius: 16px; text-align:center;
            margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            max-width: 100%;">
    <h1 style="color:white; margin:0; font-size:clamp(18px, 4vw, 32px);">
        📝 AI Smart Day Planner
    </h1>
    <p style="color:#eafaf0; margin:4px 0 0; font-size:clamp(12px, 2vw, 16px);">
        Welcome, {st.session_state['user_email']} 🚀
    </p>
</div>
""", unsafe_allow_html=True)


# ================= INPUT SECTION =================
with st.container():
    col1, col2 = st.columns([3, 1])

    with col1:
        new_task = st.text_input("✏️ Enter a Task")

    with col2:
        deadline_date = st.date_input(
            "📅 Deadline",
            value=None,
            min_value=date.today()
        )

    if st.button("➕ Add Task", use_container_width=True):
        if new_task.strip():
            deadline_str = deadline_date.isoformat() if deadline_date else None
            add_task(user_id, new_task, deadline_str)
            st.rerun()


# ================= TASK LIST =================
tasks = load_tasks(user_id)

st.subheader("📂 Your Tasks")

if not tasks:
    st.markdown("""
    <div style="text-align:center; padding:40px; color:#7a8a82;">
        <div style="font-size:clamp(32px, 8vw, 48px);">🌱</div>
        <p style="font-size:clamp(13px, 2vw, 16px);">
            No tasks yet — add one above to get started!
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    for t in tasks:
        with st.container(border=True):
            col1, col2 = st.columns([10, 1])

            with col1:
                label = "✔️ " if t["completed"] else "⏳ "
                label += t["name"]

                if t.get("deadline"):
                    label += f"  📅 {t['deadline']}"

                completed = st.checkbox(
                    label,
                    value=bool(t["completed"]),
                    key=f"task_{t['id']}"
                )

                if completed != bool(t["completed"]):
                    update_task(t["id"], completed)
                    st.rerun()

            with col2:
                if st.button("🗑️", key=f"del{t['id']}"):
                    delete_task(t["id"])
                    st.rerun()

st.divider()

# ================= ACTION BUTTONS =================
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("🚀 Generate Plan", use_container_width=True):
        current_tasks = load_tasks(user_id)
        with st.spinner("AI is thinking... 🤖"):
            st.session_state["plan"] = generate_plan(current_tasks)
        show_plan_dialog()

with c2:
    if st.button("📊 Progress", use_container_width=True):
        show_progress_dialog()

with c3:
    if st.button("🧹 Clear All", use_container_width=True):
        clear_tasks(user_id)
        st.session_state.pop("plan", None)
        st.rerun()