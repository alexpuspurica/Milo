"""
pages/1_Overview.py — Today's workout snapshot + ML recommendation
===================================================================
This is the daily landing screen for Milo.  It gives the user a complete
picture of what they should do today before they start training.

Layout (top → bottom)
---------------------
1. Page header — "Overview" title + today's date subtitle.
2. Two-column section:
       Left  — Today's Workout card: workout name badge + exercise list
               showing planned sets × reps @ weight for each movement.
       Right — Recovery Score: either the live WHOOP score (if connected)
               or a manual 1–10 slider the user adjusts.
3. Milo Recommendation banner — the ML model's verdict rendered by
   ``utils.styles.recommendation_card()``.  Shows "Increase" or "Hold"
   with a confidence percentage and a brief explanation.

Data sources (all stubs for now)
---------------------------------
    utils.db.get_today_workout(user_id)       → dict  (today's plan)
    utils.api.get_whoop_recovery(user_id)     → int|None (WHOOP score)
    utils.predict.predict_increase(...)       → dict  (ML result)

The hardcoded ``USER_ID = 1`` simulates a logged-in user.  In the final
app this will come from Streamlit session state after the auth flow.
"""

import streamlit as st
from datetime import datetime

# ---------------------------------------------------------------------------
# Shared utilities — path resolution
# Streamlit adds the project root to sys.path automatically when the app is
# launched with `streamlit run app.py`, so these imports resolve correctly.
# ---------------------------------------------------------------------------
from utils.styles  import inject_styles, sidebar_brand, card, recommendation_card
from utils.db      import get_today_workout
from utils.api     import get_whoop_recovery
from utils.predict import predict_increase

# ---------------------------------------------------------------------------
# Design system — must be called at the top of every page
# ---------------------------------------------------------------------------
inject_styles()
sidebar_brand()

# ---------------------------------------------------------------------------
# Hardcoded demo user
# Replace with st.session_state["user_id"] once auth is implemented.
# ---------------------------------------------------------------------------
USER_ID = 1

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🏠 Overview")

# Date subtitle — formatted as "Tuesday, April 22 2026"
today    = datetime.now()
day_name = today.strftime("%A")
date_str = today.strftime("%B %d, %Y")

st.markdown(
    f"<p style='color:#C4B5DC; font-family:IBM Plex Sans; font-size:1rem; "
    f"margin-top:-0.5rem;'>{day_name} — {date_str}</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Section 1: Today's Workout (left) + Recovery Score (right)
# ---------------------------------------------------------------------------
col_workout, col_recovery = st.columns([3, 2], gap="large")

# ── LEFT COLUMN: today's workout ─────────────────────────────────────────
with col_workout:
    st.subheader("Today's Workout")

    # Fetch the planned workout from the database layer.
    # Returns {"workout_name": str, "exercises": list[dict]}
    workout = get_today_workout(USER_ID)
    workout_name = workout["workout_name"]
    exercises    = workout["exercises"]

    # Workout name badge — styled pill using inline HTML
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
        ">🏋️ {workout_name}</div>
        """,
        unsafe_allow_html=True,
    )

    # Exercise list — one row per movement in the plan
    for ex in exercises:
        # Build the prescription string, e.g. "4 × 8 @ 80 kg"
        prescription = f"{ex['sets']} × {ex['reps']} @ {ex['weight_kg']:.0f} kg"

        # Render each exercise as a card-like row
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
                    font-weight: 500;
                    color: #F2EBFF;
                    font-size: 0.95rem;
                ">{ex['name']}</span>
                <span style="
                    font-family: 'IBM Plex Sans', sans-serif;
                    font-size: 0.85rem;
                    color: #C4B5DC;
                ">{prescription}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── RIGHT COLUMN: recovery score ─────────────────────────────────────────
with col_recovery:
    st.subheader("Recovery Score")

    # Try to get an automatic score from the WHOOP API.
    # Returns None if the user hasn't connected WHOOP yet.
    whoop_score = get_whoop_recovery(USER_ID)

    if whoop_score is not None:
        # WHOOP is connected — show the score as a metric and derive the
        # 1–10 scale used by the ML model (WHOOP gives 0–100).
        st.metric(
            label="WHOOP Recovery",
            value=f"{whoop_score}%",
            delta="auto-synced",
        )
        # Convert 0–100 WHOOP score → 0–100 for the ML model
        recovery_for_model = whoop_score
        recovery_display   = whoop_score // 10  # display as /10 for user context

        # Show which 1–10 bucket the WHOOP score falls into
        st.caption(f"Score band: {recovery_display}/10")

    else:
        # WHOOP not connected — ask the user to enter their score manually.
        st.caption("WHOOP not connected — enter your recovery manually (1 = exhausted, 10 = peak).")

        # Manual slider: 1 (poor) → 10 (excellent), default 7
        recovery_display = st.slider(
            label="Recovery Score",
            min_value=1,
            max_value=10,
            value=7,
            help="How recovered do you feel today? "
                 "Consider sleep quality, soreness, and stress.",
        )

        # Scale the 1–10 manual score up to 0–100 for the ML model,
        # so it matches the range the model was trained on.
        recovery_for_model = recovery_display * 10

    # Small visual indicator of the recovery zone
    if recovery_display >= 8:
        zone_colour, zone_label = "#48C78E", "🟢 High"
    elif recovery_display >= 5:
        zone_colour, zone_label = "#FFBD44", "🟡 Moderate"
    else:
        zone_colour, zone_label = "#F14668", "🔴 Low"

    st.markdown(
        f"<p style='color:{zone_colour}; font-size:0.85rem; "
        f"font-weight:600; margin-top:0.5rem;'>Recovery zone: {zone_label}</p>",
        unsafe_allow_html=True,
    )

    # Separator + WHOOP connect prompt
    st.markdown("---")
    st.markdown(
        "<p style='color:#C4B5DC; font-size:0.78rem;'>"
        "Connect your WHOOP device in <b>Settings</b> to enable automatic "
        "recovery tracking.</p>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Section 2: ML Recommendation
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Milo Recommendation")

# Call the prediction model.
# exercise_id=192 is the wger ID for Bench Press (used as the primary lift
# proxy until the user configures their "main lift" in Settings).
# recovery_for_model is already on the 0–100 scale that the model expects.
result = predict_increase(
    user_id       = USER_ID,
    exercise_id   = 192,
    recovery_score= recovery_for_model,
)

# Render the colour-coded recommendation banner
recommendation_card(result)

# Additional context below the banner
st.markdown(
    """
    <p style="color:#C4B5DC; font-size:0.78rem; margin-top:0.5rem;">
    Milo's recommendation is based on your last 3 sessions and today's
    recovery score.  It uses a Random Forest model trained on the
    OpenPowerlifting dataset.  Log your session afterwards so the model
    can learn from your actual performance.
    </p>
    """,
    unsafe_allow_html=True,
)
