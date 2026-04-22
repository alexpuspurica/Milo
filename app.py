"""
app.py — Milo Streamlit entry point
====================================
This is the root file Streamlit runs (`streamlit run app.py`).  It configures
the global page settings (title, icon, layout) and renders the home / welcome
screen.

Navigation is handled automatically by Streamlit's native multi-page feature:
any Python file placed in the `pages/` directory is discovered and added to the
sidebar in alphabetical order.  Files are prefixed with a number (e.g.
`1_Overview.py`) so they appear in the intended order.

Pages
-----
1_Overview.py  — today's workout snapshot + ML recommendation
2_Log.py       — log actual sets/reps vs planned
3_Progress.py  — charts showing strength progression over time
4_Settings.py  — configure the weekly training plan and exercises
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Global page configuration
# Must be the first Streamlit call in the script.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Milo",          # browser tab title
    page_icon="🏋️",             # dumbbell emoji as favicon
    layout="centered",          # keep content readable on wide screens
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Home / welcome content
# ---------------------------------------------------------------------------
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

# Show a friendly callout if the user lands here with no data yet
st.info(
    "Getting started: go to **Settings** to set up your weekly plan, "
    "then head to **Log** after your first session."
)
