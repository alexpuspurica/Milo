import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.styles import inject_styles, sidebar_brand, PLOTLY_CONFIG, PLOTLY_LAYOUT, PLOTLY_COLORS
from utils.auth   import require_login, render_sidebar_user
from utils.db     import get_exercise_history_by_name

inject_styles()
sidebar_brand()
require_login()
render_sidebar_user()

USER_ID = st.session_state["user_id"]

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("Progress")

st.markdown(
    "<p style='color:#C4B5DC; font-size:1rem; margin-top:-0.5rem;'>"
    "Search for an exercise to view your logged history and strength trend.</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Search bar
# ---------------------------------------------------------------------------
search_query = st.text_input(
    label       = "Search exercise",
    placeholder = "e.g. bench press, squat, deadlift...",
    help        = "Type part of the exercise name to find your logged sessions.",
    key         = "progress_search",
)

if not search_query or len(search_query.strip()) < 2:
    st.markdown(
        "<p style='color:#C4B5DC; font-size:0.9rem;'>"
        "Enter at least 2 characters to search your history.</p>",
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------------------------------------------------------------------
# Load raw set-level data
# ---------------------------------------------------------------------------
raw: pd.DataFrame = get_exercise_history_by_name(USER_ID, search_query.strip())

if raw.empty:
    st.info(f'No logged sessions found for "{search_query}". Log a workout in the Log page first.')
    st.stop()

# ---------------------------------------------------------------------------
# Mark PRs (rows where actual_kg == overall max)
# ---------------------------------------------------------------------------
overall_max = raw["actual_kg"].max()
raw["PR"] = raw["actual_kg"] == overall_max

# ---------------------------------------------------------------------------
# Data table — every logged set
# ---------------------------------------------------------------------------
st.subheader(f'Session log — "{search_query}"')

display_df = raw[["date", "exercise", "set", "planned_kg", "actual_kg",
                   "planned_reps", "actual_reps", "completed", "PR"]].copy()
display_df.columns = [
    "Date", "Exercise", "Set", "Plan kg", "Actual kg",
    "Plan reps", "Actual reps", "Completed", "PR",
]
display_df["Completed"] = display_df["Completed"].map({1: "Yes", 0: "No", True: "Yes", False: "No"})
display_df["PR"] = display_df["PR"].map({True: "PR", False: ""})

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Line chart — max actual weight per session date
# ---------------------------------------------------------------------------
st.subheader("Weight over time")

session_agg = (
    raw.groupby("date")
    .agg(
        actual_kg    = ("actual_kg",    "max"),
        planned_kg   = ("planned_kg",   "mean"),
        actual_reps  = ("actual_reps",  "mean"),
    )
    .reset_index()
    .sort_values("date")
)

if len(session_agg) < 2:
    st.caption("Log more sessions to see a trend line.")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x    = session_agg["date"],
    y    = session_agg["planned_kg"],
    name = "Planned",
    mode = "lines+markers",
    line = dict(color=PLOTLY_COLORS[1], width=2, dash="dot"),
    marker = dict(size=6, symbol="circle-open"),
))

fig.add_trace(go.Scatter(
    x         = session_agg["date"],
    y         = session_agg["actual_kg"],
    name      = "Actual",
    mode      = "lines+markers",
    line      = dict(color=PLOTLY_COLORS[0], width=3),
    marker    = dict(size=8, color=PLOTLY_COLORS[0]),
    fill      = "tozeroy",
    fillcolor = "rgba(139, 79, 204, 0.10)",
))

fig.update_layout(
    **PLOTLY_LAYOUT,
    title     = dict(text=f"{search_query} — kg over sessions", x=0),
    xaxis     = dict(PLOTLY_LAYOUT["xaxis"], title="Session Date"),
    yaxis     = dict(PLOTLY_LAYOUT["yaxis"], title="Weight (kg)"),
    height    = 320,
    hovermode = "x unified",
)

st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
