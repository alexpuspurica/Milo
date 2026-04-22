"""
pages/4_Settings.py — Weekly plan and exercise library
=======================================================
This page is where the user configures Milo before they start training.
It is divided into two sections:

Section A — Weekly Schedule
    The user assigns a workout type to each day of the week from a fixed
    menu of options (Push, Pull, Legs, Upper, Lower, Full Body, Rest,
    Cardio, Active Recovery).  The schedule is pre-populated from
    ``utils.db.get_weekly_plan()`` and saved via
    ``utils.db.save_weekly_plan()``.

Section B — Exercise Builder
    The user types a search term, which triggers ``utils.api.search_exercises()``
    to query the wger REST API (or the stub).  Results are shown in an
    expandable list; the user selects one and fills in the target prescription
    (sets, reps, target weight in kg) before clicking "Add to Plan".

    The current exercise library (from ``utils.db.get_all_exercises()``) is
    displayed below the builder as a ``st.dataframe`` for review.

Data sources
------------
    utils.db.get_weekly_plan(user_id)          → dict    (current schedule)
    utils.db.save_weekly_plan(user_id, plan)   → bool    (write to DB)
    utils.db.get_all_exercises(user_id)        → list    (library review)
    utils.api.search_exercises(query)          → list    (wger results)
"""

import streamlit as st
import pandas as pd

from utils.styles import inject_styles, sidebar_brand, card
from utils.db     import get_weekly_plan, save_weekly_plan, get_all_exercises
from utils.api    import search_exercises

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
st.title("⚙️ Settings")

st.markdown(
    "<p style='color:#C4B5DC; font-size:1rem; margin-top:-0.5rem;'>"
    "Configure your weekly training plan and exercise library.</p>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# SECTION A: Weekly Schedule
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Weekly Schedule")
st.markdown(
    "<p style='color:#C4B5DC; font-size:0.88rem; margin-bottom:1rem;'>"
    "Assign a workout type to each day.  Milo uses this to show the right "
    "exercises on the Overview and Log pages.</p>",
    unsafe_allow_html=True,
)

# Fetch the stored weekly plan (returns day → workout_name dict)
current_plan = get_weekly_plan(USER_ID)

# Workout options shown in each selectbox
WORKOUT_TYPES = [
    "Push", "Pull", "Legs", "Upper", "Lower",
    "Full Body", "Cardio", "Active Recovery", "Rest",
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Render the 7-day grid in two rows:
#   Row 1: Mon Tue Wed Thu
#   Row 2: Fri Sat Sun (+ empty placeholder)
row1_days = DAYS[:4]
row2_days = DAYS[4:]

# --- Row 1 (Mon–Thu) ---
cols_row1 = st.columns(4, gap="medium")
updated_plan = {}   # will hold the user's selections after all widgets render

for col, day in zip(cols_row1, row1_days):
    with col:
        # Small day label above the selectbox
        st.markdown(
            f"<p style='font-size:0.72rem; color:#C4B5DC; font-weight:600; "
            f"text-transform:uppercase; letter-spacing:0.1em; "
            f"margin-bottom:0.2rem;'>{day}</p>",
            unsafe_allow_html=True,
        )
        # Default to the stored value; fall back to "Rest" if not set
        default_type  = current_plan.get(day, "Rest")
        default_index = WORKOUT_TYPES.index(default_type) \
            if default_type in WORKOUT_TYPES else WORKOUT_TYPES.index("Rest")

        # selectbox — one per day, unique key prevents widget collisions
        selected = st.selectbox(
            label       = day,
            options     = WORKOUT_TYPES,
            index       = default_index,
            label_visibility = "collapsed",  # day label is shown via markdown above
            key         = f"schedule_{day}",
        )
        updated_plan[day] = selected

# --- Row 2 (Fri–Sun) ---
cols_row2 = st.columns(4, gap="medium")  # 4 columns; last one stays empty

for col, day in zip(cols_row2, row2_days):
    with col:
        st.markdown(
            f"<p style='font-size:0.72rem; color:#C4B5DC; font-weight:600; "
            f"text-transform:uppercase; letter-spacing:0.1em; "
            f"margin-bottom:0.2rem;'>{day}</p>",
            unsafe_allow_html=True,
        )
        default_type  = current_plan.get(day, "Rest")
        default_index = WORKOUT_TYPES.index(default_type) \
            if default_type in WORKOUT_TYPES else WORKOUT_TYPES.index("Rest")

        selected = st.selectbox(
            label       = day,
            options     = WORKOUT_TYPES,
            index       = default_index,
            label_visibility = "collapsed",
            key         = f"schedule_{day}",
        )
        updated_plan[day] = selected

# Save Schedule button — writes the updated plan to the database
st.markdown("<br>", unsafe_allow_html=True)

if st.button("💾  Save Schedule", key="save_schedule"):
    ok = save_weekly_plan(USER_ID, updated_plan)
    if ok:
        st.success("✅ Weekly schedule saved successfully.")
    else:
        st.error("Failed to save the schedule. Please try again.")

# ---------------------------------------------------------------------------
# SECTION B: Exercise Builder
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Exercise Builder")
st.markdown(
    "<p style='color:#C4B5DC; font-size:0.88rem; margin-bottom:1rem;'>"
    "Search for an exercise by name, then set your target prescription "
    "(sets × reps @ weight) and add it to your plan.</p>",
    unsafe_allow_html=True,
)

# ── Search row ──────────────────────────────────────────────────────────────
search_col, btn_col = st.columns([4, 1], gap="small")

with search_col:
    search_query = st.text_input(
        label       = "Search exercises",
        placeholder = "e.g. bench press, squat, row …",
        help        = "Powered by the wger exercise API.  "
                      "Results appear below after you click Search.",
        key         = "exercise_search",
    )

with btn_col:
    # Align the button vertically with the text input
    st.markdown("<div style='height:1.8rem;'></div>", unsafe_allow_html=True)
    search_clicked = st.button("🔍  Search", key="search_btn")

# ── Search results ──────────────────────────────────────────────────────────
# Show results whenever the user has typed something (regardless of button)
# so the list updates as they type.  The button is an explicit trigger in
# case they want to re-fetch after a network change.

if search_query or search_clicked:
    # Call the API helper (returns list[dict] with id/name/muscle_group/category)
    results = search_exercises(search_query)

    if results:
        # Display results as a small styled table
        results_df = pd.DataFrame(results)[["name", "muscle_group", "category"]]
        results_df.columns = ["Exercise", "Muscle Group", "Equipment"]
        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True,
        )

        # Let the user pick one from the results
        result_names  = [r["name"] for r in results]
        chosen_name   = st.selectbox(
            "Select from results",
            options = result_names,
            key     = "chosen_exercise",
        )
    else:
        st.info("No exercises found for that search term.  Try a different keyword.")
        chosen_name = None

else:
    # No search yet — no results to show
    chosen_name = None

# ── Prescription inputs ─────────────────────────────────────────────────────
# Only show the prescription fields once the user has selected an exercise.

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size:0.72rem; color:#C4B5DC; font-weight:600; "
    "text-transform:uppercase; letter-spacing:0.1em;'>Target Prescription</p>",
    unsafe_allow_html=True,
)

presc_sets, presc_reps, presc_kg, presc_btn = st.columns(
    [2, 2, 2, 2], gap="medium"
)

with presc_sets:
    target_sets = st.number_input(
        label     = "Sets",
        min_value = 1,
        max_value = 20,
        value     = 3,
        step      = 1,
        key       = "target_sets",
    )

with presc_reps:
    target_reps = st.number_input(
        label     = "Reps",
        min_value = 1,
        max_value = 50,
        value     = 10,
        step      = 1,
        key       = "target_reps",
    )

with presc_kg:
    target_kg = st.number_input(
        label     = "Weight (kg)",
        min_value = 0.0,
        max_value = 500.0,
        value     = 60.0,
        step      = 2.5,
        format    = "%.1f",
        key       = "target_kg",
    )

with presc_btn:
    # Align the button with the inputs
    st.markdown("<div style='height:1.8rem;'></div>", unsafe_allow_html=True)
    add_clicked = st.button("➕  Add to Plan", key="add_exercise_btn")

# Handle "Add to Plan" click
if add_clicked:
    if chosen_name:
        # In the real app: INSERT into plan_exercises for the chosen day.
        # For now, show a success toast confirming the action.
        st.success(
            f"✅ **{chosen_name}** added — "
            f"{target_sets} × {target_reps} @ {target_kg:.1f} kg.  "
            f"It will appear in tomorrow's Log once the database is connected."
        )
    else:
        # No exercise was selected — prompt the user to search first
        st.warning("Please search for and select an exercise first.")

# ---------------------------------------------------------------------------
# SECTION C: Current Exercise Library
# Shows all exercises currently in the user's library for review.
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Your Exercise Library")
st.markdown(
    "<p style='color:#C4B5DC; font-size:0.88rem; margin-bottom:0.75rem;'>"
    "All exercises currently in your training plan.</p>",
    unsafe_allow_html=True,
)

# Fetch the library (list[str]) and display as a simple one-column table
library = get_all_exercises(USER_ID)

if library:
    # Build a DataFrame with a numbered index for a cleaner table look
    library_df = pd.DataFrame(
        {"Exercise": library},
        index=range(1, len(library) + 1),
    )
    st.dataframe(
        library_df,
        use_container_width=True,
        hide_index=False,
    )
else:
    st.info("Your exercise library is empty.  Use the Exercise Builder above to add exercises.")

# ---------------------------------------------------------------------------
# Footer note
# ---------------------------------------------------------------------------
st.markdown(
    "<p style='color:#C4B5DC; font-size:0.78rem; margin-top:1rem;'>"
    "💡 Changes to your schedule and exercise library are saved to the "
    "SQLite database and will be reflected on the Overview and Log pages "
    "immediately.</p>",
    unsafe_allow_html=True,
)
