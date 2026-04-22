"""
utils/predict.py — ML model inference
=======================================
This module is responsible for loading the trained scikit-learn model and
running single-session predictions that power the Milo recommendation on the
Overview page.

Model background
----------------
The model is trained in `ml/models.ipynb` on the OpenPowerlifting dataset
(714 k competition results filtered to Raw SBD meets from 2015 onwards).

Task: binary classification — predict whether a lifter will **improve** their
total in the next session (1) or not (0).

Features used at inference time (mirrors training features):
    - recent_weight_kg      : the weight the user has been lifting recently
    - sessions_this_week    : how many sessions they have done this week
    - days_since_last       : rest days since the last session
    - recovery_score        : 0–100 from WHOOP or 10-point manual slider
                              (scaled to 0–100 if entered manually)
    - sets_completed_ratio  : sets completed / sets planned in last session

The model file lives at `ml/milo_model.pkl` and the expected feature order is
stored in `ml/feature_columns.pkl` (both produced by `models.ipynb`).

The stub below returns **hardcoded fake data** so the Overview page can show
the recommendation UI before the real model is trained.  Replace the return
statement in `predict_increase()` with a real joblib.load + model.predict_proba
call when the pkl files are available.
"""

# ---------------------------------------------------------------------------
# Imports (real implementation will also need: joblib, numpy)
# ---------------------------------------------------------------------------
import os


# ---------------------------------------------------------------------------
# Model path constants
# These point to the pkl files produced by ml/models.ipynb.
# Using os.path so the module works regardless of where `streamlit run` is
# invoked from.
# ---------------------------------------------------------------------------
_MODULE_DIR    = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT  = os.path.dirname(_MODULE_DIR)
_MODEL_PATH    = os.path.join(_PROJECT_ROOT, "ml", "milo_model.pkl")
_FEATURES_PATH = os.path.join(_PROJECT_ROOT, "ml", "feature_columns.pkl")


# ---------------------------------------------------------------------------
# Public inference function
# ---------------------------------------------------------------------------

def predict_increase(user_id: int, exercise_id: int, recovery_score: int) -> dict:
    """
    Predict whether the user should increase their training weight next session.

    The function queries recent session history (via utils/db), assembles a
    feature vector, and passes it through the trained scikit-learn classifier.
    A probability threshold of 0.60 is used to recommend "increase"; below
    that threshold the recommendation is "hold".

    Parameters
    ----------
    user_id : int
        Identifies the user whose history to look up.
    exercise_id : int
        The specific exercise being evaluated (e.g. Bench Press).
    recovery_score : int
        0–100 recovery score for today (from WHOOP or manual slider).
        If the slider is 1–10, the caller should multiply by 10 before
        passing it here so the scale matches the training data.

    Returns
    -------
    dict
        Keys:
            "recommendation" (str)   — "increase" or "hold"
            "confidence"     (float) — model probability for the predicted class
                                       (range 0.0–1.0, rounded to 2 d.p.)
            "suggested_kg"   (float) — if recommendation is "increase", the
                                       suggested new weight in kg; otherwise
                                       the current weight unchanged.

    Notes
    -----
    Real implementation outline:
        1. Call utils.db.get_exercise_history(user_id, exercise_id) to get
           recent sessions as a DataFrame.
        2. Derive feature values from the last 3–5 rows of that DataFrame.
        3. Load the model: clf = joblib.load(_MODEL_PATH)
        4. Load feature order: cols = joblib.load(_FEATURES_PATH)
        5. Build a single-row numpy array in the correct column order.
        6. probability = clf.predict_proba(X)[0][1]  # P(improve)
        7. Determine recommendation and suggested_kg (add 2.5 kg if increase).
        8. Return the result dict.

    The 2.5 kg increment matches standard strength training progression for
    upper-body lifts; lower-body lifts typically use 5 kg increments (can be
    made exercise-specific in a future iteration).
    """
    # --- STUB: return a fixed positive recommendation ---
    # Simulates a user who had a good recovery (score ≥ 70) and three
    # consistent sessions at 80 kg — the model would predict improvement.

    # Fake "current weight" that the suggested increase is based on.
    current_weight_kg = 80.0

    # Fake probability from the classifier.
    fake_probability = 0.78

    # Apply the 0.60 threshold: above → increase, below → hold.
    if fake_probability >= 0.60:
        recommendation = "increase"
        # Standard 2.5 kg upper-body progression increment.
        suggested_kg = current_weight_kg + 2.5
    else:
        recommendation = "hold"
        suggested_kg = current_weight_kg

    return {
        "recommendation": recommendation,
        "confidence":     round(fake_probability, 2),
        "suggested_kg":   suggested_kg,
    }
