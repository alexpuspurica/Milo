import streamlit as st
from utils.auth import require_login, render_sidebar_user
from utils.db import get_weekly_plan, save_weekly_plan, save_plan_exercise
from utils.api import search_exercises

require_login()
render_sidebar_user()

st.title("Settings")

USER_ID = st.session_state["user_id"]

WORKOUT_OPTIONS = ["Rest", "Push", "Pull", "Legs", "Upper", "Lower", "Full Body", "Cardio"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ---- Weekly schedule ----
st.subheader("Weekly Schedule")
st.write("Assign a workout type to each day of the week.")

current_plan = get_weekly_plan(USER_ID)

with st.form("schedule_form"):
    new_plan = {}
    for day in DAYS:
        current = current_plan.get(day, "Rest")
        default_index = WORKOUT_OPTIONS.index(current) if current in WORKOUT_OPTIONS else 0
        new_plan[day] = st.selectbox(day, WORKOUT_OPTIONS, index=default_index, key=f"day_{day}")

    save_schedule = st.form_submit_button("Save Schedule")

if save_schedule:
    ok = save_weekly_plan(USER_ID, new_plan)
    if ok:
        st.success("Schedule saved.")
    else:
        st.error("Could not save schedule. Please try again.")

st.divider()

# ---- Exercise search ----
st.subheader("Exercise Library")
st.write("Search for an exercise to add it to your library.")

query = st.text_input("Search exercises (e.g. bench press, squat, curl)")

if query:
    results = search_exercises(query)

    if not results:
        st.warning("No exercises found. Try a different search term.")
    else:
        st.write(f"Found {len(results)} result(s):")

        for ex in results:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{ex['name']}** — {ex['muscle_group']} ({ex['category']})")
            with col2:
                if st.button("Add", key=f"add_{ex['id']}"):
                    st.session_state["prefill_exercise"] = ex["name"]
                    st.rerun()

st.divider()

# ---- Add exercise manually ----
st.subheader("Add Exercise to Plan")
st.write("Set the target sets, reps, and weight for an exercise.")

with st.form("add_exercise_form"):
    prefill       = st.session_state.pop("prefill_exercise", "")
    exercise_name = st.text_input("Exercise name", value=prefill)
    col1, col2, col3 = st.columns(3)
    with col1:
        sets = st.number_input("Sets", min_value=1, max_value=10, value=3)
    with col2:
        reps = st.number_input("Reps", min_value=1, max_value=50, value=8)
    with col3:
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=500.0, value=60.0, step=2.5)

    day_for_exercise = st.selectbox("Add to day", DAYS)
    add_btn = st.form_submit_button("Add to Plan")

if add_btn:
    if exercise_name.strip() == "":
        st.warning("Please enter an exercise name.")
    else:
        ok = save_plan_exercise(USER_ID, day_for_exercise, exercise_name.strip(), sets, reps, weight)
        if ok:
            st.success(f"Added **{exercise_name}** ({sets} × {reps} @ {weight} kg) to {day_for_exercise}.")
        else:
            st.error("Could not save exercise. Please try again.")
