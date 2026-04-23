"""
app.py — Milo Streamlit entry point
====================================
This is the root file Streamlit runs (``streamlit run app.py``).

Responsibilities
----------------
1. ``st.set_page_config`` — must be the very first Streamlit call; sets the
   browser tab title, emoji favicon, layout, and sidebar default state.
2. ``inject_styles()`` — injects the Milo CSS design system (Google Fonts,
   colour overrides, card / button styles) into the home page.
3. ``sidebar_brand()`` — renders the Milo logo strip in the sidebar.
4. Home page content — a brief welcome screen and navigation guide shown when
   the user first opens the app.

Multi-page navigation
---------------------
Streamlit's native multi-page feature auto-discovers every ``*.py`` file in
the ``pages/`` directory and adds it to the sidebar.  Files are named with a
numeric prefix (e.g. ``1_Overview.py``) to control the display order.  No
manual routing code is required.

Pages
-----
    1_Overview.py — today's workout at a glance + ML recommendation
    2_Log.py      — log actual sets/reps vs planned
    3_Progress.py — charts showing strength progression over time
    4_Settings.py — configure the weekly training plan and exercises
"""

import streamlit as st
from streamlit_cookies_controller import CookieController

from utils.styles import inject_styles, sidebar_brand
from utils.auth import render_sidebar_user
from utils.db import (init_db, verify_user, create_user,
                      create_session_token, validate_session_token)

# ---------------------------------------------------------------------------
# Bootstrap — create DB tables on first run
# ---------------------------------------------------------------------------
init_db()

# ---------------------------------------------------------------------------
# Page configuration — must be the FIRST Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Milo",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()
sidebar_brand()

# ---------------------------------------------------------------------------
# Restore session from cookie on every load
# ---------------------------------------------------------------------------
_cookies = CookieController()
if not st.session_state.get("logged_in"):
    _attempts = st.session_state.get("_cookie_attempts", 0)
    try:
        _token = _cookies.get("milo_session")
        st.session_state.pop("_cookie_attempts", None)
    except TypeError:
        # CookieController's internal dict isn't ready yet (JS not resolved).
        # Rerun up to 5 times until it is.
        if _attempts < 5:
            st.session_state["_cookie_attempts"] = _attempts + 1
            st.rerun()
        _token = None
    if _token:
        _user = validate_session_token(_token)
        if _user:
            st.session_state["logged_in"]     = True
            st.session_state["user_id"]       = _user["user_id"]
            st.session_state["username"]      = _user["username"]
            st.session_state["session_token"] = _token

logged_in = st.session_state.get("logged_in", False)

# ---------------------------------------------------------------------------
# Home page content
# Shown when the user opens the root URL ("/" or the app entry point).
# Each page in pages/ renders its own content when navigated to.
# ---------------------------------------------------------------------------
if not logged_in:
    st.title("Milo")
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
                    token = create_session_token(user["user_id"])
                    st.session_state["logged_in"]     = True
                    st.session_state["user_id"]       = user["user_id"]
                    st.session_state["username"]      = user["username"]
                    st.session_state["session_token"] = token
                    _cookies.set("milo_session", token, max_age=30 * 24 * 3600)
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

st.title("Welcome to Milo")

st.markdown(
    "<p style='color:#C4B5DC; font-family:IBM Plex Sans; "
    "margin-top:-0.4rem; font-size:1.05rem;'>"
    "Your data-driven workout companion</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# Two-column intro layout: description left, quick-start guide right
col_about, col_start = st.columns([3, 2], gap="large")

with col_about:
    st.subheader("What is Milo?")
    st.markdown(
        """
        **Milo** helps strength athletes train smarter by combining session
        logging with machine-learning recommendations.

        After each workout, Milo inspects your recent performance and today's
        recovery score, then tells you whether you're ready to add weight
        — or whether another week at the same load will serve you better.

        The ML model is trained on the
        [OpenPowerlifting](https://openpowerlifting.org) dataset: over 700 000
        real competition results from Raw SBD meets from 2015 onwards.
        """
    )

with col_start:
    st.subheader("Getting started")
    st.markdown(
        """
        1. Go to **Settings** — build your weekly training schedule and
           add exercises to your library.
        2. Open **Log** after each session to record your actual
           sets, reps, and weights.
        3. Check **Progress** to see your strength trajectory over time.
        4. Each day, visit **Overview** to see today's plan and your
           personalised Milo recommendation.
        """
    )

st.markdown("---")

# Feature highlight row — three metrics-style tiles
st.subheader("Key features")
f1, f2, f3 = st.columns(3)
#we should put in a variable instead of manual in f3 where it gets updated based on if you have whoop connected
with f1:
    st.metric(label="ML Model", value="Random Forest",
              delta="Trained on 714 k lifts")
with f2:
    st.metric(label="Exercise API", value="wger REST",
              delta="Searchable database")
with f3:
    st.metric(label="Recovery", value="Manual",
              delta="0–100 scale")

# Friendly onboarding nudge at the bottom
st.info(
    "**First time here?** Head to **Settings** to set up your weekly plan, "
    "then return to **Log** after your first session."
)
