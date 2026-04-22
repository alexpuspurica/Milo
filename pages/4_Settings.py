"""
pages/4_Settings.py — Weekly plan and exercise library
=======================================================
This page is where the user configures everything before they start training.

**Weekly Schedule section**
The user assigns a workout type (Push / Pull / Legs / Rest / etc.) to each
day of the week.  The schedule is saved via `utils/db.save_weekly_plan()`.

**Exercise Builder section**
The user can search for exercises by name using the wger REST API
(`utils/api.search_exercises()`), select one from the results, and add it to a
workout day with a target prescription (sets × reps @ weight).

The full exercise list is also retrieved from `utils/db.get_all_exercises()`
so the user can edit or remove existing entries.

UI components planned:
    st.selectbox    — day-of-week workout type selector
    st.text_input   — exercise search box (queries wger API on change)
    st.number_input — target sets, reps, and weight
    st.button       — "Save Plan" and "Add Exercise"
    st.data_editor  — editable table of the current exercise library
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("Settings")

# ---------------------------------------------------------------------------
# Placeholder content — weekly schedule builder and exercise library will
# appear here once utils/db.get_weekly_plan() / save_weekly_plan() and
# utils/api.search_exercises() are wired up.
# ---------------------------------------------------------------------------
st.info("Coming soon — configure your weekly training plan and exercise library here.")
