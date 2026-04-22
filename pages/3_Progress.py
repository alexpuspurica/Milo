"""
pages/3_Progress.py — Strength progression visualisation
=========================================================
This page lets the user explore how their performance has changed over time
for any exercise in their library.

The user selects an exercise from a dropdown and sees three charts:

1. **Weight over time** (line chart) — how the load for that exercise has
   evolved across sessions, showing both planned and actual weights.
2. **Planned vs Actual** (grouped bar chart) — per-session comparison of
   the target prescription against what was actually completed.
3. **Completion rate** (metric or bar chart) — percentage of planned sets
   that were fully completed.

All data comes from `utils/db.get_exercise_history()`, which queries the
SQLite session log.

UI components planned:
    st.selectbox   — choose the exercise to inspect
    st.line_chart  — weight-over-time trend
    st.bar_chart   — planned vs actual per session
    st.metric      — overall completion rate
    st.pyplot      — fallback for more complex matplotlib/seaborn charts
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("Progress")

# ---------------------------------------------------------------------------
# Placeholder content — charts will be rendered here once
# utils/db.get_exercise_history() is wired up and real session data exists.
# ---------------------------------------------------------------------------
st.info("Coming soon — your strength progression charts will appear here.")
