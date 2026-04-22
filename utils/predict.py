"""
utils/predict.py — ML model inference
"""

import os
import pickle
import datetime

import numpy as np
import pandas as pd

from utils.db import get_exercise_history

_MODULE_DIR    = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT  = os.path.dirname(_MODULE_DIR)
_MODEL_PATH    = os.path.join(_PROJECT_ROOT, "ml", "data", "milo_model.pkl")
_FEATURES_PATH = os.path.join(_PROJECT_ROOT, "ml", "data", "feature_columns.pkl")

# F1-optimised threshold from models.ipynb
_BASE_THRESHOLD = 0.39

# Load once at import time — small LogReg model, negligible overhead
with open(_MODEL_PATH, "rb") as _f:
    _model = pickle.load(_f)
with open(_FEATURES_PATH, "rb") as _f:
    _feature_cols: list = pickle.load(_f)


# --- band helper functions ---

def _days_band(days):
    if days < 30:   return "under_30"
    if days < 90:   return "30_to_90"
    if days < 180:  return "90_to_180"
    if days < 365:  return "180_to_365"
    return "over_365"  # reference — all-False row

def _bw_band(change):
    if change < -5: return "lost_5plus"
    if change < -2: return "lost_2_to_5"
    if change < 2:  return "stable"      # reference
    if change < 5:  return "gained_2_to_5"
    return "gained_5plus"

def _total_band(total):
    if total < 300: return "under_300"
    if total < 450: return "300_to_450"
    if total < 600: return "450_to_600"
    if total < 750: return "600_to_750"
    return "over_750"  # reference

def _squat_band(w):
    if w < 100: return "sq_under_100"
    if w < 150: return "sq_100_to_150"
    if w < 200: return "sq_150_to_200"
    if w < 250: return "sq_200_to_250"
    return "sq_over_250"  # reference

def _bench_band(w):
    if w < 60:  return "bp_under_60"
    if w < 90:  return "bp_60_to_90"
    if w < 120: return "bp_90_to_120"
    if w < 150: return "bp_120_to_150"
    return "bp_over_150"  # reference

def _dl_band(w):
    if w < 120: return "dl_under_120"
    if w < 175: return "dl_120_to_175"
    if w < 230: return "dl_175_to_230"
    if w < 280: return "dl_230_to_280"
    return "dl_over_280"  # reference

def _age_band(age):
    if age < 20: return "under_20"
    if age < 25: return "20_to_25"
    if age < 30: return "25_to_30"
    if age < 35: return "30_to_35"
    if age < 45: return "35_to_45"
    return "over_45"  # reference


def predict_increase(user_id: int, exercise_id: int, recovery_score: int) -> dict:
    """
    Predict whether the user should increase weight next session.

    Returns a dict with keys:
        "recommendation"  str    "increase" or "hold"
        "confidence"      float  model probability (0.0–1.0)
        "suggested_kg"    float  recommended weight for next session
    """
    # pull exercise history to derive days since last session and recent weight
    history = get_exercise_history(user_id, exercise_id)

    if not history.empty:
        last_date     = pd.to_datetime(history["date"].iloc[-1])
        days_since    = max((datetime.datetime.today() - last_date).days, 0)
        recent_weight = float(history["actual_weight_kg"].iloc[-1])
    else:
        days_since    = 7      # sensible default: assume one week rest
        recent_weight = 60.0   # mid-range default

    # estimate the three main lift values from the single tracked exercise
    # user can map exercises to squat/bench/deadlift in a future settings update
    squat_est = recent_weight
    bench_est = recent_weight * 0.75
    dl_est    = recent_weight * 1.2
    total_est = squat_est + bench_est + dl_est

    # user profile defaults — can be extended via settings page
    age       = 25
    is_female = False

    # build feature row — all False, then flip the relevant band to True
    row = {col: False for col in _feature_cols}
    row["is_female"] = is_female

    for prefix, band in [
        ("days_band",               _days_band(days_since)),
        ("bodyweight_change_band",  _bw_band(0.0)),          # assume stable
        ("prev_total_band",         _total_band(total_est)),
        ("prev_squat_band",         _squat_band(squat_est)),
        ("prev_bench_band",         _bench_band(bench_est)),
        ("prev_deadlift_band",      _dl_band(dl_est)),
        ("age_band",                _age_band(age)),
    ]:
        key = f"{prefix}_{band}"
        if key in row:
            row[key] = True

    X    = pd.DataFrame([row])[_feature_cols]
    prob = float(_model.predict_proba(X)[0][1])

    # Shift the decision threshold based on recovery score.
    # Recovery was not a training feature, so we apply it post-hoc:
    # feeling great → lower the bar for "increase"; feeling rough → raise it.
    if   recovery_score >= 80: threshold = _BASE_THRESHOLD - 0.08
    elif recovery_score >= 60: threshold = _BASE_THRESHOLD
    elif recovery_score >= 40: threshold = _BASE_THRESHOLD + 0.10
    else:                      threshold = _BASE_THRESHOLD + 0.20
    threshold = max(0.10, min(0.90, threshold))

    if prob >= threshold:
        recommendation = "increase"
        suggested_kg   = round(recent_weight + 2.5, 1)
    else:
        recommendation = "hold"
        suggested_kg   = recent_weight

    return {
        "recommendation": recommendation,
        "confidence":     round(prob, 2),
        "suggested_kg":   suggested_kg,
    }
