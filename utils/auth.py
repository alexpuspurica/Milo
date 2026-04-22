"""
utils/auth.py — Session-based authentication helpers
=====================================================
Call require_login() at the top of every page that should be protected.
Call render_sidebar_user() after that to show the logged-in username and a
logout button in the sidebar.
"""

import streamlit as st
from utils.db import validate_session_token, delete_session_token


def require_login() -> None:
    """Redirect to login if not authenticated. Also tries auto-login from token."""
    if not st.session_state.get("logged_in"):
        token = st.query_params.get("session")
        if token:
            user = validate_session_token(token)
            if user:
                st.session_state["logged_in"]     = True
                st.session_state["user_id"]       = user["user_id"]
                st.session_state["username"]      = user["username"]
                st.session_state["session_token"] = token
                st.rerun()
        st.switch_page("app.py")
        st.stop()


def render_sidebar_user() -> None:
    """Render username + logout button in the sidebar."""
    with st.sidebar:
        st.divider()
        st.caption(f"Signed in as **{st.session_state.get('username', '')}**")
        if st.button("Log Out", use_container_width=True):
            token = st.session_state.get("session_token")
            if token:
                delete_session_token(token)
            st.session_state.clear()
            st.query_params.clear()
            st.switch_page("app.py")
