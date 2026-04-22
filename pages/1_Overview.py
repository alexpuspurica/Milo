import streamlit as st
from datetime import datetime

from utils.styles  import inject_styles, sidebar_brand, card, recommendation_card
from utils.auth    import require_login, render_sidebar_user
from utils.db      import get_today_workout, get_weekly_plan
from utils.api     import get_whoop_recovery
from utils.predict import predict_increase

inject_styles()
sidebar_brand()
require_login()
render_sidebar_user()

USER_ID = st.session_state["user_id"]

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("Overview")

today    = datetime.now()
day_name = today.strftime("%A")
date_str = today.strftime("%B %d, %Y")

st.markdown(
    f"<p style='color:#C4B5DC; font-family:IBM Plex Sans; font-size:1rem; "
    f"margin-top:-0.5rem;'>{day_name} — {date_str}</p>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Day-of-week bar
# ---------------------------------------------------------------------------
DAYS_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAYS_FULL  = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

weekly_plan = get_weekly_plan(USER_ID)

today_full = today.strftime("%A")

day_cells = []
for short, full in zip(DAYS_SHORT, DAYS_FULL):
    workout = weekly_plan.get(full, "Rest")
    is_today    = (full == today_full)
    is_training = (workout != "Rest")

    if is_today:
        bg     = "rgba(139,79,204,0.55)"
        border = "2px solid #8B4FCC"
        label_color = "#F2EBFF"
        day_color   = "#F2EBFF"
    elif is_training:
        bg     = "rgba(139,79,204,0.18)"
        border = "1px solid rgba(139,79,204,0.45)"
        label_color = "#F2EBFF"
        day_color   = "#C4B5DC"
    else:
        bg     = "rgba(28,4,53,0.5)"
        border = "1px solid rgba(139,79,204,0.15)"
        label_color = "#C4B5DC"
        day_color   = "#6B2FA8"

    day_cells.append(f"""
        <div style="
            flex:1; text-align:center; padding:0.55rem 0.25rem;
            border-radius:8px; background:{bg}; border:{border};
        ">
            <div style="font-family:'IBM Plex Sans',sans-serif; font-size:0.65rem;
                        font-weight:600; text-transform:uppercase;
                        letter-spacing:0.1em; color:{day_color};">{short}</div>
            <div style="font-family:'IBM Plex Sans',sans-serif; font-size:0.72rem;
                        font-weight:500; color:{label_color}; margin-top:0.2rem;
                        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                {workout}
            </div>
        </div>
    """)

st.markdown(
    f'<div style="display:flex; gap:0.35rem; margin-bottom:1.5rem;">{"".join(day_cells)}</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Today's Workout + Recovery Score
# ---------------------------------------------------------------------------
col_workout, col_recovery = st.columns([3, 2], gap="large")

with col_workout:
    st.subheader("Today's Workout")

    workout      = get_today_workout(USER_ID)
    workout_name = workout["workout_name"]
    exercises    = workout["exercises"]

    st.markdown(
        f"""
        <div style="
            display: inline-block;
            background: rgba(139, 79, 204, 0.25);
            border: 1px solid rgba(139, 79, 204, 0.5);
            border-radius: 99px;
            padding: 0.3rem 1rem;
            font-family: 'Syne', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            color: #F2EBFF;
            margin-bottom: 1rem;
        ">{workout_name}</div>
        """,
        unsafe_allow_html=True,
    )

    if exercises:
        for ex in exercises:
            prescription = f"{ex['sets']} x {ex['reps']} @ {ex['weight_kg']:.0f} kg"
            st.markdown(
                f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 0.65rem 1rem;
                    margin-bottom: 0.4rem;
                    background: rgba(61, 10, 107, 0.40);
                    border-left: 3px solid #8B4FCC;
                    border-radius: 0 8px 8px 0;
                ">
                    <span style="
                        font-family: 'IBM Plex Sans', sans-serif;
                        font-weight: 500; color: #F2EBFF; font-size: 0.95rem;
                    ">{ex['name']}</span>
                    <span style="
                        font-family: 'IBM Plex Sans', sans-serif;
                        font-size: 0.85rem; color: #C4B5DC;
                    ">{prescription}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            "<p style='color:#C4B5DC; font-size:0.9rem;'>Rest day — no exercises planned.</p>",
            unsafe_allow_html=True,
        )

with col_recovery:
    st.subheader("Recovery Score")

    whoop_score = get_whoop_recovery(USER_ID)

    if whoop_score is not None:
        recovery_for_model = whoop_score
        recovery_display   = whoop_score
    else:
        st.caption("WHOOP not connected — enter your recovery score manually.")
        recovery_display = st.slider(
            label="Recovery Score (0–100)",
            min_value=0,
            max_value=100,
            value=70,
            help="How recovered do you feel? 0 = exhausted, 100 = peak.",
        )
        recovery_for_model = recovery_display

    # Color based on score
    if recovery_display >= 67:
        ring_color  = "#48C78E"
        zone_label  = "High"
        zone_color  = "#48C78E"
    elif recovery_display >= 34:
        ring_color  = "#FFBD44"
        zone_label  = "Moderate"
        zone_color  = "#FFBD44"
    else:
        ring_color  = "#F14668"
        zone_label  = "Low"
        zone_color  = "#F14668"

    # SVG ring: r=48, circumference ≈ 301.59
    circumference = 301.59
    offset = circumference * (1 - recovery_display / 100)

    st.markdown(
        f"""
        <div style="display:flex; flex-direction:column; align-items:center; padding:0.5rem 0;">
            <svg viewBox="0 0 120 120" width="160" height="160">
                <circle cx="60" cy="60" r="48" fill="none"
                        stroke="rgba(61,10,107,0.9)" stroke-width="10"/>
                <circle cx="60" cy="60" r="48" fill="none"
                        stroke="{ring_color}" stroke-width="10"
                        stroke-dasharray="{circumference:.2f}"
                        stroke-dashoffset="{offset:.2f}"
                        stroke-linecap="round"
                        transform="rotate(-90 60 60)"/>
                <text x="60" y="57" text-anchor="middle"
                      font-family="Syne,sans-serif" font-size="26"
                      font-weight="700" fill="#F2EBFF">{recovery_display}</text>
                <text x="60" y="74" text-anchor="middle"
                      font-family="IBM Plex Sans,sans-serif"
                      font-size="10" fill="#C4B5DC">/ 100</text>
            </svg>
            <p style="font-family:'IBM Plex Sans',sans-serif; font-size:0.82rem;
                      font-weight:600; color:{zone_color}; margin:0.25rem 0 0;">
                {zone_label} Recovery
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "<p style='color:#C4B5DC; font-size:0.78rem;'>"
        "Connect your WHOOP device in <b>Settings</b> to enable automatic "
        "recovery tracking.</p>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# ML Recommendation
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Milo Recommendation")

result = predict_increase(
    user_id        = USER_ID,
    exercise_id    = 192,
    recovery_score = recovery_for_model,
)

recommendation_card(result)

st.markdown(
    """
    <p style="color:#C4B5DC; font-size:0.78rem; margin-top:0.5rem;">
    Milo's recommendation is based on your last 3 sessions and today's
    recovery score. It uses a Logistic Regression model trained on the
    OpenPowerlifting dataset. Log your session afterwards so the model
    can learn from your actual performance.
    </p>
    """,
    unsafe_allow_html=True,
)
