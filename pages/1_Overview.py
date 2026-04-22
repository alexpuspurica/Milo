import streamlit as st
import datetime
from utils.auth import require_login, render_sidebar_user
from utils.db import get_today_workout
from utils.api import get_whoop_recovery
from utils.predict import predict_increase

require_login()
render_sidebar_user()

st.title("Overview")

USER_ID = st.session_state["user_id"]

# today's day name and workout
day_name = datetime.datetime.today().strftime("%A")
workout = get_today_workout(USER_ID)
workout_name = workout["workout_name"]
exercises = workout["exercises"]

st.subheader(f"Today — {day_name}")
st.metric("Workout", workout_name)
st.write("**Exercises:** " + ", ".join(e["name"] for e in exercises))

st.divider()

# recovery score — WHOOP if connected, manual slider otherwise
st.subheader("Recovery Score")

whoop_score = get_whoop_recovery(USER_ID)

if whoop_score is not None:
    recovery = whoop_score
    st.metric("WHOOP Recovery", f"{recovery} / 100")
else:
    recovery_slider = st.slider("How do you feel today? (1 = exhausted, 10 = great)", 1, 10, 7)
    recovery = recovery_slider * 10
    st.caption("WHOOP not connected — using manual score")

st.divider()

# ML recommendation
st.subheader("Milo Recommendation")

result = predict_increase(USER_ID, 1, recovery)

if result["recommendation"] == "increase":
    st.success(
        f"**Increase weight today.**\n\n"
        f"Based on your recent sessions and a recovery score of {recovery}/100, "
        f"Milo recommends going up to **{result['suggested_kg']} kg**.\n\n"
        f"Model confidence: {int(result['confidence'] * 100)}%"
    )
else:
    st.info(
        f"**Hold at current weight.**\n\n"
        f"Your body may need more time to adapt. Stick with your current load "
        f"today and focus on quality reps.\n\n"
        f"Model confidence: {int(result['confidence'] * 100)}%"
    )
