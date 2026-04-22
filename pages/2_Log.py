"""
pages/2_Log.py — Session logging
=================================
This page lets the user record what they actually completed during today's
workout, comparing each set against the planned prescription.

Layout (top → bottom)
---------------------
1. Page header — "Log" title + today's workout name subtitle.
2. Session form — wrapped in ``st.form`` so all inputs submit atomically.
       For each exercise in today's plan, one row is rendered with:
           • Exercise name (text label)
           • Planned prescription (read-only label, e.g. "4 × 8 @ 80 kg")
           • Actual weight number input (pre-filled with the planned weight)
           • Actual reps number input (pre-filled with the planned reps)
           • Completed checkbox (tick if the exercise is done)
3. Save Session button — submits the form and calls
   ``utils.db.save_session()`` for each exercise.  Shows a success or error
   message depending on the return value.

Data sources
------------
    utils.db.get_today_workout(user_id) → dict   (exercises to log)
    utils.db.save_session(...)          → bool   (write to database)

Input validation
----------------
Weights must be ≥ 0 and reps must be ≥ 0.  Streamlit's ``number_input``
enforces the minimum at the widget level.  Additional validation (e.g.
checking that weight ≤ 500 kg) will be added to ``db.save_session`` in
the real implementation.
"""

import streamlit as st
from datetime import datetime

from utils.styles import inject_styles, sidebar_brand, card
from utils.db     import get_today_workout, save_session

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------
inject_styles()
sidebar_brand()

# Hardcoded demo user — replace with session_state["user_id"] in production
USER_ID = 1

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("📋 Log")

# Fetch today's workout so we can show it in the subtitle and build the form
workout      = get_today_workout(USER_ID)
workout_name = workout["workout_name"]
exercises    = workout["exercises"]

# Date + workout name subtitle
today    = datetime.now()
day_name = today.strftime("%A")
st.markdown(
    f"<p style='color:#C4B5DC; font-size:1rem; margin-top:-0.5rem;'>"
    f"{day_name} — <b style='color:#F2EBFF;'>{workout_name}</b></p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Column header row (visual label, not a real table header)
# ---------------------------------------------------------------------------
hdr_ex, hdr_plan, hdr_kg, hdr_reps, hdr_done = st.columns(
    [3, 2, 2, 2, 1], gap="small"
)
# Render small-caps column labels matching the design's muted text style
_label_style = (
    "font-family:'IBM Plex Sans',sans-serif; font-size:0.7rem; "
    "font-weight:600; text-transform:uppercase; letter-spacing:0.1em; "
    "color:#C4B5DC;"
)
hdr_ex  .markdown(f"<span style='{_label_style}'>Exercise</span>",  unsafe_allow_html=True)
hdr_plan.markdown(f"<span style='{_label_style}'>Planned</span>",   unsafe_allow_html=True)
hdr_kg  .markdown(f"<span style='{_label_style}'>Actual kg</span>", unsafe_allow_html=True)
hdr_reps.markdown(f"<span style='{_label_style}'>Actual reps</span>",unsafe_allow_html=True)
hdr_done.markdown(f"<span style='{_label_style}'>✓</span>",         unsafe_allow_html=True)

st.markdown("<div style='border-top:1px solid rgba(139,79,204,0.25); margin:0.25rem 0 0.5rem;'></div>",
            unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session form
# All inputs are inside a single st.form so they submit together when the
# user clicks "Save Session".  This prevents premature database writes
# caused by Streamlit re-runs on every widget interaction.
# ---------------------------------------------------------------------------
with st.form(key="session_form", clear_on_submit=False):

    # session_data accumulates the dict we will pass to save_session()
    # after the form is submitted.
    session_data = []   # list[dict] — one entry per exercise

    for ex in exercises:
        # Planned prescription label — shown in the "Planned" column
        planned_label = f"{ex['sets']} × {ex['reps']} @ {ex['weight_kg']:.0f} kg"

        # One row per exercise: 5 columns matching the header above
        col_ex, col_plan, col_kg, col_reps, col_done = st.columns(
            [3, 2, 2, 2, 1], gap="small"
        )

        with col_ex:
            # Exercise name — displayed as styled text, not an input
            st.markdown(
                f"<p style='font-family:IBM Plex Sans; font-weight:500; "
                f"color:#F2EBFF; padding-top:0.6rem; font-size:0.95rem;'>"
                f"{ex['name']}</p>",
                unsafe_allow_html=True,
            )

        with col_plan:
            # Read-only planned prescription label
            st.markdown(
                f"<p style='font-family:IBM Plex Sans; font-size:0.85rem; "
                f"color:#C4B5DC; padding-top:0.7rem;'>{planned_label}</p>",
                unsafe_allow_html=True,
            )

        with col_kg:
            # Actual weight — pre-filled from the plan so the user only needs
            # to edit if they lifted more or less than planned.
            actual_kg = st.number_input(
                label    = f"kg_{ex['name']}",     # unique key
                label_visibility = "collapsed",     # hide label; header row acts as label
                min_value= 0.0,
                max_value= 500.0,
                value    = float(ex["weight_kg"]),  # default = planned weight
                step     = 2.5,                     # standard plate increment
                format   = "%.1f",
                key      = f"kg_{ex['name']}",
            )

        with col_reps:
            # Actual reps — pre-filled from the plan
            actual_reps = st.number_input(
                label    = f"reps_{ex['name']}",
                label_visibility = "collapsed",
                min_value= 0,
                max_value= 100,
                value    = int(ex["reps"]),         # default = planned reps
                step     = 1,
                key      = f"reps_{ex['name']}",
            )

        with col_done:
            # Completion checkbox — the user ticks this when all sets are done
            completed = st.checkbox(
                label = "done",
                label_visibility = "collapsed",
                value = False,                      # unchecked by default
                key   = f"done_{ex['name']}",
            )

        # Accumulate this exercise's data for the batch save call
        session_data.append({
            "exercise_name": ex["name"],
            "planned_sets":  ex["sets"],
            "planned_reps":  ex["reps"],
            "planned_kg":    ex["weight_kg"],
            "actual_kg":     actual_kg,
            "actual_reps":   actual_reps,
            "completed":     completed,
        })

        # Visual separator between exercise rows
        st.markdown(
            "<div style='border-top:1px solid rgba(139,79,204,0.12); "
            "margin:0.1rem 0;'></div>",
            unsafe_allow_html=True,
        )

    # ── Submit button ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)  # small vertical gap before button

    submitted = st.form_submit_button(
        label="💾  Save Session",
        use_container_width=False,
    )

# ---------------------------------------------------------------------------
# Handle form submission
# Runs only after the user clicks "Save Session".
# ---------------------------------------------------------------------------
if submitted:
    # Track whether all saves succeeded so we can show the right message
    all_ok = True

    for item in session_data:
        # Build the sets_data format expected by save_session().
        # In the real implementation, one dict per set would be passed;
        # for now we treat the whole exercise as a single "set" entry.
        sets_payload = [
            {
                "set_number": 1,
                "reps":       item["actual_reps"],
                "weight_kg":  item["actual_kg"],
                "completed":  item["completed"],
            }
        ]

        # Call the database write helper.
        # exercise_id=0 is a placeholder until exercises have real DB IDs.
        ok = save_session(
            user_id     = USER_ID,
            exercise_id = 0,     # TODO: resolve real exercise_id from name
            sets_data   = sets_payload,
        )

        if not ok:
            # One exercise failed to save — flag and continue the loop
            all_ok = False
            st.error(f"Failed to save {item['exercise_name']}. Please try again.")

    if all_ok:
        # All exercises saved — show success banner
        st.success(
            "✅ Session saved!  Great work.  Head to **Progress** to see "
            "your updated charts, or check back on **Overview** tomorrow."
        )

# ---------------------------------------------------------------------------
# Bottom hint for the user
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<p style='color:#C4B5DC; font-size:0.78rem;'>"
    "💡 <b>Tip:</b> Tick the ✓ checkbox for each exercise you completed all "
    "planned sets of.  Only edit the kg or reps fields if your actual "
    "performance differed from the plan.</p>",
    unsafe_allow_html=True,
)
