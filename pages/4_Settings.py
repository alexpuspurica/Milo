import streamlit as st
import pandas as pd

from utils.styles import inject_styles, sidebar_brand
from utils.auth   import require_login, render_sidebar_user
from utils.db     import (
    get_weekly_plan, save_weekly_plan,
    get_all_exercises, save_plan_exercise,
    get_all_plan_exercises,
)
from utils.api    import search_exercises

inject_styles()
sidebar_brand()
require_login()
render_sidebar_user()

USER_ID = st.session_state["user_id"]

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("Settings")

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
    "Assign a workout type to each day. Milo uses this to show the right "
    "exercises on the Overview and Log pages.</p>",
    unsafe_allow_html=True,
)

current_plan = get_weekly_plan(USER_ID)

WORKOUT_TYPES = [
    "Push", "Pull", "Legs", "Upper", "Lower",
    "Full Body", "Cardio", "Active Recovery", "Rest",
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

row1_days = DAYS[:4]
row2_days = DAYS[4:]

updated_plan = {}

cols_row1 = st.columns(4, gap="medium")
for col, day in zip(cols_row1, row1_days):
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
            label            = day,
            options          = WORKOUT_TYPES,
            index            = default_index,
            label_visibility = "collapsed",
            key              = f"schedule_{day}",
        )
        updated_plan[day] = selected

cols_row2 = st.columns(4, gap="medium")
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
            label            = day,
            options          = WORKOUT_TYPES,
            index            = default_index,
            label_visibility = "collapsed",
            key              = f"schedule_{day}",
        )
        updated_plan[day] = selected

st.markdown("<br>", unsafe_allow_html=True)

if st.button("Save Schedule", key="save_schedule"):
    ok = save_weekly_plan(USER_ID, updated_plan)
    if ok:
        st.success("Weekly schedule saved.")
    else:
        st.error("Failed to save the schedule. Please try again.")

# ---------------------------------------------------------------------------
# SECTION B: Exercise Builder
# Requires selecting a day before the prescription fields appear.
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Exercise Builder")
st.markdown(
    "<p style='color:#C4B5DC; font-size:0.88rem; margin-bottom:1rem;'>"
    "Select a day, search for an exercise, set your prescription, and add it "
    "to your plan. Use the progression fields to auto-increment weight over time.</p>",
    unsafe_allow_html=True,
)

# --- Step 1: Day selector (required before anything else) ---
st.markdown(
    "<p style='font-size:0.72rem; color:#C4B5DC; font-weight:600; "
    "text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;'>"
    "Step 1 — Choose a day</p>",
    unsafe_allow_html=True,
)

training_days = [d for d in DAYS if updated_plan.get(d, "Rest") != "Rest"]
day_options   = training_days if training_days else DAYS  # fallback: show all

chosen_day = st.selectbox(
    label   = "Day",
    options = ["— select a day —"] + day_options,
    key     = "builder_day",
)

day_chosen = chosen_day != "— select a day —"

if not day_chosen:
    st.caption("Select a day above to unlock the exercise search and prescription fields.")

if day_chosen:
    # --- Step 2: Exercise name ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.72rem; color:#C4B5DC; font-weight:600; "
        "text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;'>"
        "Step 2 — Name the exercise</p>",
        unsafe_allow_html=True,
    )

    name_col, search_col, search_btn_col = st.columns([3, 3, 1], gap="small")

    with name_col:
        custom_name = st.text_input(
            label       = "Exercise name",
            placeholder = "e.g. Bench Press, RDL ...",
            help        = "Type directly — new names are added to your library automatically.",
            key         = "custom_exercise_name",
        )

    with search_col:
        search_query = st.text_input(
            label       = "Or search exercise database",
            placeholder = "Search wger API ...",
            key         = "exercise_search",
        )

    with search_btn_col:
        st.markdown("<div style='height:1.8rem;'></div>", unsafe_allow_html=True)
        search_clicked = st.button("Search", key="search_btn")

    if search_query or search_clicked:
        results = search_exercises(search_query)
        if results:
            results_df = pd.DataFrame(results)[["name", "muscle_group", "category"]]
            results_df.columns = ["Exercise", "Muscle Group", "Equipment"]
            st.dataframe(results_df, use_container_width=True, hide_index=True)
            result_names = [r["name"] for r in results]
            api_chosen   = st.selectbox(
                "Select to use as exercise name",
                options = ["— pick one —"] + result_names,
                key     = "chosen_exercise",
            )
            if api_chosen and api_chosen != "— pick one —":
                st.session_state["custom_exercise_name"] = api_chosen
                st.rerun()
        else:
            st.info("No results — type a custom name in the Exercise name field.")

    chosen_name = custom_name.strip() if custom_name and custom_name.strip() else None

    # --- Step 3: Prescription + Progression ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.72rem; color:#C4B5DC; font-weight:600; "
        "text-transform:uppercase; letter-spacing:0.1em;'>"
        "Step 3 — Prescription &amp; Progression</p>",
        unsafe_allow_html=True,
    )

    presc_sets, presc_reps, presc_kg, prog_n, prog_kg_col = st.columns(
        [2, 2, 2, 2, 2], gap="medium"
    )

    with presc_sets:
        target_sets = st.number_input("Sets", min_value=1, max_value=20, value=3, step=1, key="target_sets")

    with presc_reps:
        target_reps = st.number_input("Reps", min_value=1, max_value=50, value=10, step=1, key="target_reps")

    with presc_kg:
        target_kg = st.number_input(
            "Weight (kg)", min_value=0.0, max_value=500.0,
            value=60.0, step=2.5, format="%.1f", key="target_kg",
        )

    with prog_n:
        progression_n = st.number_input(
            "Every N sessions",
            min_value=0, max_value=50, value=0, step=1, key="prog_n",
            help="Auto-increase weight every N sessions. Set 0 to disable.",
        )

    with prog_kg_col:
        progression_kg = st.number_input(
            "Increase by (kg)",
            min_value=0.0, max_value=20.0, value=2.5, step=0.5,
            format="%.1f", key="prog_kg",
            help="How many kg to add when the progression triggers.",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Add to Plan", key="add_exercise_btn"):
        if chosen_name:
            ok = save_plan_exercise(
                user_id              = USER_ID,
                day                  = chosen_day,
                exercise_name        = chosen_name,
                sets                 = int(target_sets),
                reps                 = int(target_reps),
                weight_kg            = float(target_kg),
                progression_every_n  = int(progression_n),
                progression_kg       = float(progression_kg),
            )
            if ok:
                prog_note = (
                    f"  Progression: +{progression_kg:.1f} kg every {progression_n} sessions."
                    if progression_n > 0 else ""
                )
                st.success(
                    f"**{chosen_name}** added to {chosen_day} — "
                    f"{int(target_sets)} x {int(target_reps)} @ {target_kg:.1f} kg.{prog_note}"
                )
            else:
                st.error("Failed to save exercise. Please try again.")
        else:
            st.warning("Enter an exercise name in the field above before adding.")

# ---------------------------------------------------------------------------
# SECTION C: Live Plan Preview
# Shows current plan exercises as they are in the DB (updates after save).
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Plan Preview")
st.markdown(
    "<p style='color:#C4B5DC; font-size:0.88rem; margin-bottom:0.75rem;'>"
    "Current exercises in your training plan. Reload after adding exercises to see updates.</p>",
    unsafe_allow_html=True,
)

all_plan = get_all_plan_exercises(USER_ID)

if all_plan:
    plan_by_day: dict[str, list] = {}
    for ex in all_plan:
        plan_by_day.setdefault(ex["day"], []).append(ex)

    for day in DAYS:
        if day not in plan_by_day:
            continue
        workout_label = updated_plan.get(day, "")
        st.markdown(
            f"<p style='font-family:Syne,sans-serif; font-size:1rem; "
            f"font-weight:700; color:#F2EBFF; margin-bottom:0.3rem;'>"
            f"{day}"
            f"<span style='font-family:IBM Plex Sans,sans-serif; font-size:0.78rem; "
            f"font-weight:400; color:#C4B5DC; margin-left:0.75rem;'>{workout_label}</span>"
            f"</p>",
            unsafe_allow_html=True,
        )
        for ex in plan_by_day[day]:
            prog_text = (
                f" · +{ex['progression_kg']:.1f} kg / {ex['progression_every_n']} sessions"
                if ex["progression_every_n"] > 0 else ""
            )
            st.markdown(
                f"""
                <div style="
                    display:flex; justify-content:space-between; align-items:center;
                    padding:0.5rem 0.9rem; margin-bottom:0.3rem;
                    background:rgba(61,10,107,0.35);
                    border-left:3px solid #8B4FCC;
                    border-radius:0 8px 8px 0;
                ">
                    <span style="font-family:'IBM Plex Sans',sans-serif;
                                 font-weight:500; color:#F2EBFF; font-size:0.9rem;">
                        {ex['name']}
                    </span>
                    <span style="font-family:'IBM Plex Sans',sans-serif;
                                 font-size:0.8rem; color:#C4B5DC;">
                        {ex['sets']} x {ex['reps']} @ {ex['weight_kg']:.0f} kg{prog_text}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
else:
    st.info("Your plan is empty. Use the Exercise Builder above to add exercises to days.")

# ---------------------------------------------------------------------------
# SECTION D: Full Exercise Library
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Exercise Library")

library = get_all_exercises(USER_ID)

if library:
    library_df = pd.DataFrame({"Exercise": library}, index=range(1, len(library) + 1))
    st.dataframe(library_df, use_container_width=True, hide_index=False)
else:
    st.info("Your exercise library is empty. Add exercises using the builder above.")

st.markdown(
    "<p style='color:#C4B5DC; font-size:0.78rem; margin-top:1rem;'>"
    "Changes to your schedule and exercise library are saved to the "
    "database and will be reflected on the Overview and Log pages immediately.</p>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# SECTION E: WHOOP Connection
# ---------------------------------------------------------------------------
import os
from pathlib import Path

_ENV_PATH = Path(__file__).parent.parent / ".env"

def _read_whoop_env() -> dict:
    """Return stored WHOOP credentials from .env, or empty strings if not set."""
    creds = {"username": "", "password": ""}
    if _ENV_PATH.exists():
        for line in _ENV_PATH.read_text().splitlines():
            if line.startswith("USERNAMEinENV="):
                creds["username"] = line.split("=", 1)[1].strip()
            elif line.startswith("PASSWORDinENV="):
                creds["password"] = line.split("=", 1)[1].strip()
    return creds

st.markdown("---")
st.subheader("WHOOP Connection")
st.markdown(
    "<p style='color:#C4B5DC; font-size:0.88rem; margin-bottom:1rem;'>"
    "Connect your WHOOP account to enable automatic recovery tracking on the Overview page.</p>",
    unsafe_allow_html=True,
)

_stored = _read_whoop_env()
_connected = bool(_stored["username"] and _stored["password"])

if _connected:
    st.success(f"Connected as **{_stored['username']}**")
else:
    st.warning("Not connected — recovery score must be entered manually.")

with st.form("whoop_form"):
    whoop_email = st.text_input(
        "WHOOP Email",
        value=_stored["username"],
        placeholder="you@example.com",
    )
    whoop_password = st.text_input(
        "WHOOP Password",
        type="password",
        placeholder="Enter your WHOOP password",
    )
    col_save, col_clear = st.columns([3, 1])
    with col_save:
        save_whoop = st.form_submit_button("Save Credentials", use_container_width=True)
    with col_clear:
        clear_whoop = st.form_submit_button("Disconnect", use_container_width=True)

if save_whoop:
    if not whoop_email or not whoop_password:
        st.error("Please enter both email and password.")
    else:
        _ENV_PATH.write_text(
            f"USERNAMEinENV={whoop_email.strip()}\n"
            f"PASSWORDinENV={whoop_password}\n"
        )
        st.success("WHOOP credentials saved. Recovery will sync automatically on the Overview page.")
        st.rerun()

if clear_whoop:
    if _ENV_PATH.exists():
        _ENV_PATH.unlink()
    st.success("WHOOP disconnected.")
    st.rerun()
