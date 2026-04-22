import streamlit as st
from datetime import datetime

from utils.styles import inject_styles, sidebar_brand
from utils.auth   import require_login, render_sidebar_user
from utils.db     import get_today_workout, save_session

inject_styles()
sidebar_brand()
require_login()
render_sidebar_user()

USER_ID = st.session_state["user_id"]

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("Log")

workout      = get_today_workout(USER_ID)
workout_name = workout["workout_name"]
exercises    = workout["exercises"]

today    = datetime.now()
day_name = today.strftime("%A")
st.markdown(
    f"<p style='color:#C4B5DC; font-size:1rem; margin-top:-0.5rem;'>"
    f"{day_name} — <b style='color:#F2EBFF;'>{workout_name}</b></p>",
    unsafe_allow_html=True,
)

st.markdown("---")

if not exercises:
    st.info("No exercises planned for today. Set up your schedule in Settings.")
    st.stop()

# ---------------------------------------------------------------------------
# Column header row
# ---------------------------------------------------------------------------
hdr_ex, hdr_plan, hdr_kg, hdr_reps, hdr_done = st.columns(
    [3, 2, 2, 2, 1], gap="small"
)
_label_style = (
    "font-family:'IBM Plex Sans',sans-serif; font-size:0.7rem; "
    "font-weight:600; text-transform:uppercase; letter-spacing:0.1em; "
    "color:#C4B5DC;"
)
hdr_ex  .markdown(f"<span style='{_label_style}'>Exercise</span>",   unsafe_allow_html=True)
hdr_plan.markdown(f"<span style='{_label_style}'>Planned</span>",    unsafe_allow_html=True)
hdr_kg  .markdown(f"<span style='{_label_style}'>Actual kg</span>",  unsafe_allow_html=True)
hdr_reps.markdown(f"<span style='{_label_style}'>Actual reps</span>",unsafe_allow_html=True)
hdr_done.markdown(f"<span style='{_label_style}'>Done</span>",       unsafe_allow_html=True)

st.markdown(
    "<div style='border-top:1px solid rgba(139,79,204,0.25); "
    "margin:0.25rem 0 0.5rem;'></div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session form
# ---------------------------------------------------------------------------
with st.form(key="session_form", clear_on_submit=False):

    row_data = []  # one dict per exercise

    for ex in exercises:
        planned_label = f"{ex['sets']} x {ex['reps']} @ {ex['weight_kg']:.0f} kg"

        col_ex, col_plan, col_kg, col_reps, col_done = st.columns(
            [3, 2, 2, 2, 1], gap="small"
        )

        with col_ex:
            st.markdown(
                f"<p style='font-family:IBM Plex Sans; font-weight:500; "
                f"color:#F2EBFF; padding-top:0.6rem; font-size:0.95rem;'>"
                f"{ex['name']}</p>",
                unsafe_allow_html=True,
            )

        with col_plan:
            st.markdown(
                f"<p style='font-family:IBM Plex Sans; font-size:0.85rem; "
                f"color:#C4B5DC; padding-top:0.7rem;'>{planned_label}</p>",
                unsafe_allow_html=True,
            )

        with col_kg:
            actual_kg = st.number_input(
                label            = f"kg_{ex['name']}",
                label_visibility = "collapsed",
                min_value        = 0.0,
                max_value        = 500.0,
                value            = float(ex["weight_kg"]),
                step             = 2.5,
                format           = "%.1f",
                key              = f"kg_{ex['name']}",
            )

        with col_reps:
            actual_reps = st.number_input(
                label            = f"reps_{ex['name']}",
                label_visibility = "collapsed",
                min_value        = 0,
                max_value        = 100,
                value            = int(ex["reps"]),
                step             = 1,
                key              = f"reps_{ex['name']}",
            )

        with col_done:
            completed = st.checkbox(
                label            = "done",
                label_visibility = "collapsed",
                value            = False,
                key              = f"done_{ex['name']}",
            )

        row_data.append({
            "name":              ex["name"],
            "planned_weight_kg": float(ex["weight_kg"]),
            "planned_reps":      int(ex["reps"]),
            "actual_weight_kg":  actual_kg,
            "actual_reps":       actual_reps,
            "completed":         completed,
        })

        st.markdown(
            "<div style='border-top:1px solid rgba(139,79,204,0.12); "
            "margin:0.1rem 0;'></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    submitted = st.form_submit_button(
        label="Save Session",
        use_container_width=False,
    )

# ---------------------------------------------------------------------------
# Handle submission — call save_session once with all exercises
# ---------------------------------------------------------------------------
if submitted:
    ok = save_session(user_id=USER_ID, sets_data=row_data)
    if ok:
        st.success(
            "Session saved. Head to Progress to see your updated charts, "
            "or check back on Overview tomorrow."
        )
    else:
        st.error("Failed to save session. Please try again.")

# ---------------------------------------------------------------------------
# Footer tip
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<p style='color:#C4B5DC; font-size:0.78rem;'>"
    "<b>Tip:</b> Tick the Done checkbox for each exercise you completed all "
    "planned sets of. Only edit kg or reps if your actual performance "
    "differed from the plan.</p>",
    unsafe_allow_html=True,
)
