"""
pages/2_Log.py — Session logging
=================================
This page lets the user record what they actually did in today's workout,
comparing it against the planned sets, reps, and target weight.

For each exercise in today's plan the user will see a row showing:
    - The planned prescription  (e.g. "4 × 8 @ 80 kg")
    - Number input fields for the actual reps and weight they completed
    - A checkbox to mark the exercise as fully completed

When the user clicks **Save Session**, all entered data is validated and
written to the SQLite database via `utils/db.save_session()`.

UI components planned:
    st.form            — wraps all inputs so they submit together
    st.number_input    — actual reps / weight per set
    st.checkbox        — mark exercise complete
    st.button          — "Save Session" submit trigger
    st.success         — confirmation message after a successful save
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("Log")

# ---------------------------------------------------------------------------
# Placeholder content — real form with today's exercises will appear here
# once utils/db.get_today_workout() and utils/db.save_session() are wired up.
# ---------------------------------------------------------------------------
st.info("Coming soon — log your sets, reps, and weights for today's session here.")
