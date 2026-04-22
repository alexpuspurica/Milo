import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.auth import require_login, render_sidebar_user
from utils.db import get_all_exercises, get_exercise_history, get_exercise_id

require_login()
render_sidebar_user()

st.title("Progress")

USER_ID = st.session_state["user_id"]

exercises = get_all_exercises(USER_ID)

if not exercises:
    st.info("No exercises found. Add exercises in Settings first.")
    st.stop()

selected    = st.selectbox("Select exercise", exercises)
exercise_id = get_exercise_id(USER_ID, selected)
history     = get_exercise_history(USER_ID, exercise_id) if exercise_id else pd.DataFrame()

if history.empty:
    st.info(f"No session data yet for {selected}. Log some sessions first.")
    st.stop()

st.divider()

# ---- Weight over time ----
st.subheader("Weight over time")

fig1, ax1 = plt.subplots(figsize=(8, 3))
ax1.plot(history["date"], history["planned_weight_kg"], marker="o", label="Planned", linestyle="--", color="steelblue")
ax1.plot(history["date"], history["actual_weight_kg"],  marker="o", label="Actual",  linestyle="-",  color="darkorange")
ax1.set_xlabel("Date")
ax1.set_ylabel("Weight (kg)")
ax1.set_title(f"{selected} — weight progression")
ax1.legend()
plt.xticks(rotation=30)
plt.tight_layout()
st.pyplot(fig1)

st.divider()

# ---- Planned vs actual reps ----
st.subheader("Planned vs actual reps")

x = range(len(history))
width = 0.35

fig2, ax2 = plt.subplots(figsize=(8, 3))
ax2.bar([i - width/2 for i in x], history["planned_reps"], width=width, label="Planned", color="steelblue")
ax2.bar([i + width/2 for i in x], history["actual_reps"],  width=width, label="Actual",  color="darkorange")
ax2.set_xticks(list(x))
ax2.set_xticklabels(history["date"], rotation=30)
ax2.set_ylabel("Reps")
ax2.set_title(f"{selected} — planned vs actual reps per session")
ax2.legend()
plt.tight_layout()
st.pyplot(fig2)

st.divider()

# ---- Completion rate ----
st.subheader("Completion rate")

planned_sets_total = len(history) * history["sets_completed"].max()
completed_sets = history["sets_completed"].sum()
max_sets = history["sets_completed"].max()
completion_pct = round((history["sets_completed"] / max_sets).mean() * 100, 1)

st.metric("Average sets completed", f"{completion_pct}%")
st.bar_chart(history.set_index("date")["sets_completed"])
