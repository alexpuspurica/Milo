"""
utils/auth.py — Session-based authentication helpers
=====================================================
Call require_login() at the top of every page that should be protected.
Call render_sidebar_user() after that to show the logged-in username and a
logout button in the sidebar.
"""

import streamlit as st


def require_login() -> None:
    """Redirect to the login screen (app.py) if the user is not authenticated."""
    if not st.session_state.get("logged_in"):
        st.switch_page("app.py")
        st.stop()


def render_sidebar_user() -> None:
    """Render username + logout button in the sidebar."""
    with st.sidebar:
        st.divider()
        st.caption(f"Signed in as **{st.session_state.get('username', '')}**")
        if st.button("Log Out", use_container_width=True):
            st.session_state.clear()
            st.switch_page("app.py")
