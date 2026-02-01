import streamlit as st
import sqlite3
import uuid

from auth import login, register_user
from assistant import ask_ai
from db_utils import (
    save_chat,
    load_chat_history,
    get_all_users,
    get_all_documents,
    update_user,
    delete_user,
    add_document,
    update_document,
    delete_document
)

from streamlit_cookies_manager import EncryptedCookieManager


# ================= COOKIES =================
cookies = EncryptedCookieManager(
    prefix="svu_mca_",
    password="svu-mca-super-secret-key"
)

if not cookies.ready():
    st.stop()


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="SVU-MCA Assistant",
    page_icon="🎓",
    layout="centered"
)


# ================= CSS =================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stSidebar"] {width: 260px;}
</style>
""", unsafe_allow_html=True)


# ================= LOGOUT FUNCTION =================
def logout_user():
    cookies.clear()
    cookies.save()
    st.session_state.clear()
    st.rerun()


# ================= SESSION DEFAULTS =================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = str(uuid.uuid4())


# ================= RESTORE LOGIN FROM COOKIE =================
if (
    "role" not in st.session_state
    and cookies.get("user_id")
    and cookies.get("user_id") != "0"
):
    st.session_state.user_id = int(cookies["user_id"])
    st.session_state.name = cookies["name"]
    st.session_state.role = cookies["role"]
    st.session_state.course = cookies.get("course", "")
    st.session_state.year = cookies.get("year", "")


# ================= AUTH SCREENS =================
if "role" not in st.session_state:

    st.title("🎓 SVU-MCA Intelligent Student Assistant")

    choice = st.radio("Access Mode", ["Login", "Register", "Guest"])

    # ---------- LOGIN ----------
    if choice == "Login":
        mobile = st.text_input("Mobile")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login(mobile, password)
            if user:
                cookies["user_id"] = str(user[0])
                cookies["name"] = user[1]
                cookies["role"] = user[2]
                cookies["course"] = user[3]
                cookies["year"] = user[4]
                cookies.save()

                st.session_state.user_id = user[0]
                st.session_state.name = user[1]
                st.session_state.role = user[2]
                st.session_state.course = user[3]
                st.session_state.year = user[4]

                st.session_state.chat = []
                st.session_state.chat_sessions = []

                st.toast(f"Welcome {user[1]} 🎓")
                st.rerun()
            else:
                st.error("Invalid credentials")

    # ---------- REGISTER ----------
    elif choice == "Register":
        name = st.text_input("Full Name")
        mobile = st.text_input("Mobile")
        password = st.text_input("Password", type="password")
        course = st.text_input("Course", "MCA")
        year = st.selectbox("Year", ["1st", "2nd"])

        if st.button("Register"):
            if not name.strip() or not mobile.strip() or not password.strip():
                st.error("All fields required")
            elif not mobile.isdigit():
                st.error("Mobile must be numeric")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                if register_user(name, mobile, password, course, year):
                    st.success("Registered successfully. Please login.")
                else:
                    st.error("Mobile already registered")

    # ---------- GUEST ----------
    else:
        if st.button("Enter Guest Mode"):
            cookies["user_id"] = "0"
            cookies["name"] = "Guest User"
            cookies["role"] = "guest"
            cookies.save()

            st.session_state.user_id = 0
            st.session_state.name = "Guest User"
            st.session_state.role = "guest"
            st.session_state.chat = []
            st.session_state.chat_sessions = []

            st.rerun()


# ================= DASHBOARD =================
else:
    # ---------- SIDEBAR ----------
    st.sidebar.image("images/Vikram_University_logo.jpg", width=90)
    st.sidebar.markdown(f"### {st.session_state.name}")
    st.sidebar.caption(st.session_state.role.upper())
    st.sidebar.markdown("---")

    # ---------- ADMIN ----------
    if st.session_state.role == "admin":

        menu = st.sidebar.radio(
            "Admin Menu",
            ["Home", "Users", "Documents & Notices", "Chat History", "Logout"]
        )

        if menu == "Home":
            st.subheader("👋 Welcome Admin")

        elif menu == "Users":
            st.subheader("📋 User Management")
            for u in get_all_users():
                c = st.columns([3, 3, 2, 2, 2, 1])
                c[0].write(u[1])
                c[1].write(u[2])
                c[2].write(u[4])
                c[3].write(u[5])
                c[4].write(u[3])
                if c[5].button("❌", key=f"del_{u[0]}"):
                    delete_user(u[0])
                    st.rerun()

        elif menu == "Documents & Notices":
            st.subheader("📄 Documents / Notices")
            title = st.text_input("Title")
            desc = st.text_area("Description")

            if st.button("Add"):
                if title.strip() and desc.strip():
                    add_document(title, desc)
                    st.success("Added")
                    st.rerun()

            for d in get_all_documents():
                st.markdown(f"**{d[1]}** — {d[2]}")

        elif menu == "Chat History":
            st.subheader("💬 Chat History")
            conn = sqlite3.connect("college_data.db")
            cur = conn.cursor()
            cur.execute("""
                SELECT u.name, c.role, c.message, c.timestamp
                FROM chat_history c
                JOIN users u ON c.user_id = u.id
                ORDER BY c.timestamp DESC
            """)
            for r in cur.fetchall()[:50]:
                st.markdown(f"**{r[0]} ({r[1]})**: {r[2]}")
            conn.close()

        elif menu == "Logout":
            logout_user()

    # ---------- STUDENT / GUEST ----------
    else:
        # TOP BAR
        col1, col2, col3 = st.columns([6, 2, 2])

        with col2:
            if st.button("➕ New Chat"):
                if st.session_state.chat:
                    title = st.session_state.chat[0]["content"][:30]
                    st.session_state.chat_sessions.append(title)

                st.session_state.chat = []
                st.session_state.active_chat_id = str(uuid.uuid4())
                st.rerun()

        with col3:
            with st.expander("👤"):
                if st.session_state.role != "guest":
                    if st.button("Edit Profile"):
                        st.session_state.show_profile = True
                if st.button("Logout"):
                    logout_user()

        # SIDEBAR CHAT TITLES
        st.sidebar.markdown("### 💬 Chats")
        for t in st.session_state.chat_sessions:
            st.sidebar.caption(t)

        # PROFILE
        if st.session_state.get("show_profile"):
            st.subheader("👤 Profile")
            name = st.text_input("Name", st.session_state.name)
            if st.button("Save"):
                if name.strip():
                    conn = sqlite3.connect("college_data.db")
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE users SET name=? WHERE id=?",
                        (name, st.session_state.user_id)
                    )
                    conn.commit()
                    conn.close()
                    st.session_state.name = name
                    st.session_state.show_profile = False
                    st.rerun()

        # CHAT UI
        st.subheader(f"👋 Welcome {st.session_state.name}")

        for m in st.session_state.chat:
            with st.chat_message(m["role"]):
                st.write(m["content"])

        q = st.chat_input("Ask your question...")

        if q:
            st.session_state.chat.append({"role": "user", "content": q})

            docs = get_all_documents()
            context = "\n".join([d[1] + ": " + d[2] for d in docs])

            ans = ask_ai(q, context)

            st.session_state.chat.append({"role": "assistant", "content": ans})

            if st.session_state.role != "guest":
                save_chat(st.session_state.user_id, "user", q)
                save_chat(st.session_state.user_id, "assistant", ans)

            st.rerun()
