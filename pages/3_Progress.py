"""
pages/3_Progress.py — Strength progression visualisation
=========================================================
This page lets the user explore how their performance on any exercise has
evolved over time.  All charts use Plotly with the Milo dark theme so they
blend seamlessly into the app's colour palette.

Layout (top → bottom)
---------------------
1. Page header — "Progress" title + instruction subtitle.
2. Exercise selector — ``st.selectbox`` populated from
   ``utils.db.get_all_exercises()``.
3. Summary metric row — three ``st.metric`` tiles showing personal best,
   total sessions logged, and overall completion rate for the chosen exercise.
4. Weight over Time chart — Plotly line chart with two traces:
       • Planned weight (dashed, muted)
       • Actual weight  (solid, Iris accent)
5. Planned vs Actual Reps — Plotly grouped bar chart showing planned reps
   (muted bar) vs actual reps (accent bar) per session date.
6. Sets Completed — Plotly bar chart showing how many sets were completed
   each session vs the planned target.

Data source
-----------
    utils.db.get_all_exercises(user_id)          → list[str]
    utils.db.get_exercise_history(user_id, ex_id) → pd.DataFrame
        Columns: date, planned_weight_kg, actual_weight_kg,
                 planned_reps, actual_reps, sets_completed

Notes
-----
The exercise_id passed to get_exercise_history() is hardcoded to 0 in the
stub phase; once exercises have real database IDs those will be used.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.styles import inject_styles, sidebar_brand, PLOTLY_CONFIG, PLOTLY_LAYOUT, PLOTLY_COLORS
from utils.db     import get_all_exercises, get_exercise_history

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------
inject_styles()
sidebar_brand()

# Hardcoded demo user
USER_ID = 1

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("📊 Progress")

st.markdown(
    "<p style='color:#C4B5DC; font-size:1rem; margin-top:-0.5rem;'>"
    "Track how your strength has evolved over time for any exercise.</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Exercise selector
# Fetch the full exercise library and let the user pick which one to inspect.
# ---------------------------------------------------------------------------
exercises = get_all_exercises(USER_ID)   # list[str] from db stub

selected_exercise = st.selectbox(
    label       = "Select exercise",
    options     = exercises,
    index       = 0,               # default to the first exercise
    help        = "Choose an exercise from your library to view its history.",
)

st.markdown("<br>", unsafe_allow_html=True)  # visual gap before metrics

# ---------------------------------------------------------------------------
# Load history for the selected exercise
# exercise_id=0 is a placeholder; the real app resolves the int ID from the
# exercise name via a lookup in the exercises table.
# ---------------------------------------------------------------------------
history: pd.DataFrame = get_exercise_history(
    user_id     = USER_ID,
    exercise_id = 0,          # TODO: resolve from selected_exercise name
)

# ---------------------------------------------------------------------------
# Derived summary statistics
# These are computed from the stub DataFrame; replace with real SQL aggregates
# once the database is implemented.
# ---------------------------------------------------------------------------

# Personal best — maximum actual weight lifted
personal_best = history["actual_weight_kg"].max()

# Previous personal best — second-highest unique weight (for delta display)
unique_weights = sorted(history["actual_weight_kg"].unique())
prev_best = unique_weights[-2] if len(unique_weights) >= 2 else personal_best
pb_delta  = personal_best - prev_best

# Total sessions logged for this exercise
total_sessions = len(history)

# Completion rate — percentage of sessions where sets_completed == planned sets
# The planned set count is constant (4) in the stub; real implementation
# joins plan_exercises to get the target per session.
PLANNED_SETS = 4   # stub constant; real value comes from the DB join
completed_sessions = (history["sets_completed"] >= PLANNED_SETS).sum()
completion_rate    = int(100 * completed_sessions / total_sessions) if total_sessions else 0

# ---------------------------------------------------------------------------
# Summary metric row
# ---------------------------------------------------------------------------
col_pb, col_sessions, col_rate = st.columns(3, gap="medium")

with col_pb:
    st.metric(
        label = "Personal Best",
        value = f"{personal_best:.1f} kg",
        delta = f"+{pb_delta:.1f} kg vs prev",
    )

with col_sessions:
    st.metric(
        label = "Sessions Logged",
        value = total_sessions,
        delta = "for this exercise",
    )

with col_rate:
    st.metric(
        label = "Completion Rate",
        value = f"{completion_rate}%",
        delta = "sets completed",
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Chart 1: Weight over Time
# Two traces: planned (dashed, muted) vs actual (solid, Iris).
# ---------------------------------------------------------------------------
st.subheader("Weight Over Time")

fig_weight = go.Figure()

# Trace 1 — planned weight (dashed line, muted colour)
fig_weight.add_trace(go.Scatter(
    x    = history["date"],
    y    = history["planned_weight_kg"],
    name = "Planned",
    mode = "lines+markers",
    line = dict(
        color = PLOTLY_COLORS[1],   # muted iris-light (#C4B5DC)
        width = 2,
        dash  = "dot",              # dashed to distinguish from actual
    ),
    marker = dict(size=6, symbol="circle-open"),
))

# Trace 2 — actual weight (solid line, Iris accent)
fig_weight.add_trace(go.Scatter(
    x    = history["date"],
    y    = history["actual_weight_kg"],
    name = "Actual",
    mode = "lines+markers",
    line = dict(
        color = PLOTLY_COLORS[0],   # Iris (#8B4FCC)
        width = 3,
    ),
    marker = dict(size=8, color=PLOTLY_COLORS[0]),
    # Fill area under the actual weight trace for visual emphasis
    fill      = "tozeroy",
    fillcolor = "rgba(139, 79, 204, 0.10)",
))

# Apply the shared Milo dark layout tokens
fig_weight.update_layout(
    **PLOTLY_LAYOUT,
    title     = dict(text=f"{selected_exercise} — kg over sessions", x=0),
    xaxis     = dict(PLOTLY_LAYOUT["xaxis"], title="Session Date"),
    yaxis     = dict(PLOTLY_LAYOUT["yaxis"], title="Weight (kg)"),
    height    = 320,
    hovermode = "x unified",
)

st.plotly_chart(fig_weight, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")

# ---------------------------------------------------------------------------
# Chart 2: Planned vs Actual Reps (grouped bar chart)
# Lets the user see whether they hit their rep targets each session.
# ---------------------------------------------------------------------------
st.subheader("Planned vs Actual Reps")

fig_reps = go.Figure()

# Bar 1 — planned reps (lighter colour)
fig_reps.add_trace(go.Bar(
    name      = "Planned",
    x         = history["date"],
    y         = history["planned_reps"],
    marker_color = PLOTLY_COLORS[2],            # #A97DD4
    opacity      = 0.7,
))

# Bar 2 — actual reps (accent colour)
fig_reps.add_trace(go.Bar(
    name      = "Actual",
    x         = history["date"],
    y         = history["actual_reps"],
    marker_color = PLOTLY_COLORS[0],            # Iris
))

fig_reps.update_layout(
    **PLOTLY_LAYOUT,
    barmode   = "group",                        # side-by-side bars
    title     = dict(text=f"{selected_exercise} — reps per session", x=0),
    xaxis     = dict(PLOTLY_LAYOUT["xaxis"], title="Session Date"),
    yaxis     = dict(PLOTLY_LAYOUT["yaxis"], title="Reps"),
    height    = 280,
    hovermode = "x unified",
)

st.plotly_chart(fig_reps, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")

# ---------------------------------------------------------------------------
# Chart 3: Sets Completed per Session (horizontal bar / column chart)
# Shows the absolute count of sets completed vs the planned target line.
# ---------------------------------------------------------------------------
st.subheader("Sets Completed per Session")

fig_sets = go.Figure()

# Bar — sets completed each session (coloured by whether target was hit)
bar_colours = [
    PLOTLY_COLORS[0] if s >= PLANNED_SETS else "#F14668"   # Iris if complete, red if not
    for s in history["sets_completed"]
]

fig_sets.add_trace(go.Bar(
    name         = "Sets Completed",
    x            = history["date"],
    y            = history["sets_completed"],
    marker_color = bar_colours,
    text         = history["sets_completed"],  # show number on top of each bar
    textposition = "outside",
    textfont     = dict(color="#F2EBFF", size=11),
))

# Horizontal reference line at the planned set count
fig_sets.add_hline(
    y          = PLANNED_SETS,
    line_dash  = "dot",
    line_color = PLOTLY_COLORS[1],
    annotation_text  = f"Target ({PLANNED_SETS} sets)",
    annotation_position = "top right",
    annotation_font  = dict(color="#C4B5DC", size=11),
)

fig_sets.update_layout(
    **PLOTLY_LAYOUT,
    title   = dict(text=f"{selected_exercise} — sets completed", x=0),
    xaxis   = dict(PLOTLY_LAYOUT["xaxis"], title="Session Date"),
    yaxis   = dict(PLOTLY_LAYOUT["yaxis"], title="Sets", range=[0, PLANNED_SETS + 1.5]),
    height  = 260,
    showlegend = False,
)

st.plotly_chart(fig_sets, use_container_width=True, config=PLOTLY_CONFIG)

# ---------------------------------------------------------------------------
# Footer note
# ---------------------------------------------------------------------------
st.markdown(
    "<p style='color:#C4B5DC; font-size:0.78rem;'>"
    "Charts update automatically after each session is saved in <b>Log</b>.  "
    "Data shown is from the stub layer — real history will appear once the "
    "SQLite database is connected.</p>",
    unsafe_allow_html=True,
)
