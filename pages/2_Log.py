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
# Session form — one card per exercise
# ---------------------------------------------------------------------------
with st.form(key="session_form", clear_on_submit=False):

    row_data = []

    for ex in exercises:
        planned_str = f"{ex['sets']} x {ex['reps']} @ {ex['weight_kg']:.0f} kg"

        # Card wrapper
        st.markdown(
            f"""
            <div style="
                background: rgba(61,10,107,0.40);
                border: 1px solid rgba(139,79,204,0.30);
                border-radius: 10px;
                padding: 0.9rem 1.1rem 0.4rem;
                margin-bottom: 0.75rem;
            ">
                <div style="display:flex; justify-content:space-between;
                            align-items:baseline; margin-bottom:0.6rem;">
                    <span style="font-family:'Syne',sans-serif; font-size:1rem;
                                 font-weight:700; color:#F2EBFF;">{ex['name']}</span>
                    <span style="font-family:'IBM Plex Sans',sans-serif;
                                 font-size:0.8rem; color:#C4B5DC;">
                        Planned: {planned_str}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Inputs sit outside the card HTML (Streamlit can't mix widgets + HTML)
        col_kg, col_reps, col_done = st.columns([3, 3, 1], gap="medium")

        with col_kg:
            actual_kg = st.number_input(
                label     = "Actual weight (kg)",
                min_value = 0.0,
                max_value = 500.0,
                value     = float(ex["weight_kg"]),
                step      = 2.5,
                format    = "%.1f",
                key       = f"kg_{ex['name']}",
            )

        with col_reps:
            actual_reps = st.number_input(
                label     = "Actual reps",
                min_value = 0,
                max_value = 100,
                value     = int(ex["reps"]),
                step      = 1,
                key       = f"reps_{ex['name']}",
            )

        with col_done:
            st.markdown("<div style='height:1.65rem;'></div>", unsafe_allow_html=True)
            completed = st.checkbox(
                label = "Done",
                value = False,
                key   = f"done_{ex['name']}",
            )

        row_data.append({
            "name":              ex["name"],
            "planned_weight_kg": float(ex["weight_kg"]),
            "planned_reps":      int(ex["reps"]),
            "actual_weight_kg":  actual_kg,
            "actual_reps":       actual_reps,
            "completed":         completed,
        })

        st.markdown("<div style='height:0.25rem;'></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Save Session", use_container_width=False)

# ---------------------------------------------------------------------------
# Handle submission
# ---------------------------------------------------------------------------
if submitted:
    ok = save_session(user_id=USER_ID, sets_data=row_data)
    if ok:
        st.success(
            "Session saved. Head to Progress to see your updated charts."
        )
    else:
        st.error("Failed to save session. Please try again.")

st.markdown("---")
st.markdown(
    "<p style='color:#C4B5DC; font-size:0.78rem;'>"
    "<b>Tip:</b> Tick Done for each exercise you completed all planned sets of. "
    "Only change kg or reps if your actual performance differed from the plan.</p>",
    unsafe_allow_html=True,
)
