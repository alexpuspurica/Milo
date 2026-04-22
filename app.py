"""
app.py — Milo entry point and login gate
=========================================
When the user is NOT authenticated this page renders the login form.
Once authenticated it shows the welcome / home screen.

Navigation to the other pages is handled by Streamlit's native multi-page
feature: any .py file in pages/ is added to the sidebar automatically.
Every page calls require_login() from utils/auth.py to enforce the gate.

Pages
-----
1_Overview.py  — today's workout snapshot + ML recommendation
2_Log.py       — log actual sets/reps vs planned
3_Progress.py  — charts showing strength progression over time
4_Settings.py  — configure the weekly training plan and exercises
"""

import streamlit as st

from utils.auth import render_sidebar_user
from utils.db import init_db, verify_user, create_user

# ---------------------------------------------------------------------------
# Bootstrap — create DB tables on first run
# ---------------------------------------------------------------------------
init_db()

# ---------------------------------------------------------------------------
# Global page configuration
# Must be the first Streamlit call in the script.
# ---------------------------------------------------------------------------
logged_in = st.session_state.get("logged_in", False)

st.set_page_config(
    page_title="Milo",
    page_icon="🏋️",
    layout="centered",
    initial_sidebar_state="expanded" if logged_in else "collapsed",
)

# ---------------------------------------------------------------------------
# Login gate
# ---------------------------------------------------------------------------
if not logged_in:
    st.title("🏋️ Milo")
    st.write("")

    tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        with st.form("login_form"):
            username  = st.text_input("Username")
            password  = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", use_container_width=True)

        if submitted:
            if not username or not password:
                st.warning("Please enter both a username and password.")
            else:
                user = verify_user(username.strip(), password)
                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"]   = user["user_id"]
                    st.session_state["username"]  = user["username"]
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

    with tab_signup:
        with st.form("signup_form"):
            new_username = st.text_input("Choose a username")
            new_password = st.text_input("Choose a password", type="password")
            confirm      = st.text_input("Confirm password", type="password")
            signup_btn   = st.form_submit_button("Create Account", use_container_width=True)

        if signup_btn:
            if not new_username or not new_password:
                st.warning("Please fill in all fields.")
            elif len(new_username.strip()) < 3:
                st.error("Username must be at least 3 characters.")
            elif new_password != confirm:
                st.error("Passwords do not match.")
            else:
                ok = create_user(new_username.strip(), new_password)
                if ok:
                    st.success("Account created! Switch to Sign In to log in.")
                else:
                    st.error("That username is already taken.")

    st.stop()  # nothing below renders when not logged in

# ---------------------------------------------------------------------------
# Home / welcome screen (authenticated users only)
# ---------------------------------------------------------------------------
render_sidebar_user()

st.title("🏋️ Welcome to Milo")
st.subheader("Your data-driven workout companion")

st.markdown(
    """
    **Milo** helps strength athletes train smarter by combining simple workout
    logging with machine-learning recommendations.  After each session, Milo
    looks at your recent performance and your recovery score to tell you whether
    you are ready to increase the weight — or whether you should hold steady for
    another week.

    ---
    ### What Milo does
    - **Overview** — see today's planned workout and your Milo recommendation
      at a glance
    - **Log** — record actual sets, reps, and weights completed each session
    - **Progress** — visualise your strength gains over time with interactive
      charts
    - **Settings** — build your weekly training schedule and exercise library

    ---
    Use the **sidebar** on the left to navigate between pages.
    """
)

st.info(
    "Getting started: go to **Settings** to set up your weekly plan, "
    "then head to **Log** after your first session."
)
