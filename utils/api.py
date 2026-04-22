"""
utils/api.py — External API helpers
=====================================
This module handles all outbound HTTP calls to third-party services:

1. **wger Exercise API** (https://wger.de/api/v2/)
   Open-source exercise database.  No authentication required for read-only
   endpoints.  Used on the Settings page to let users search for exercises by
   name and retrieve muscle group / category metadata.

2. **WHOOP API** (https://developer.whoop.com/)
   Returns the user's latest recovery score (0–100) as measured by their
   WHOOP wearable device.  Access requires OAuth2 approval which is pending
   for this project; until then, `get_whoop_recovery` returns None so the UI
   falls back to the manual recovery slider.

Both functions return **hardcoded fake data** for now so the UI can be built
and tested without live network access.  Replace the return statements with
real `requests` calls when credentials / network access is available.

Dependencies (add to requirements.txt when implementing):
    requests
"""


# ---------------------------------------------------------------------------
# wger Exercise API
# ---------------------------------------------------------------------------

def search_exercises(query: str) -> list:
    """
    Search the wger exercise database for exercises matching a keyword.

    Returns list of dicts with keys: id, name, muscle_group, category.
    Falls back to an empty list on any network or parse error.
    """
    import requests

    try:
        resp = requests.get(
            "https://wger.de/api/v2/exercise/search/",
            params={"term": query, "language": "english", "format": "json"},
            timeout=6,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    results = []
    for suggestion in data.get("suggestions", []):
        ex = suggestion.get("data", {})
        results.append({
            "id":           ex.get("id", 0),
            "name":         suggestion.get("value", ""),
            "muscle_group": ex.get("muscle_list", ""),
            "category":     ex.get("category_list", ""),
        })
    return results


# ---------------------------------------------------------------------------
# WHOOP API
# ---------------------------------------------------------------------------

def get_whoop_recovery(user_id: int):
    """
    Fetch the user's most recent WHOOP recovery score.

    WHOOP recovery scores range from 0 (very poor) to 100 (peak readiness).
    In Milo, this score is passed to `utils/predict.predict_increase()` as a
    feature so the ML model can account for fatigue when making its
    recommendation.

    Parameters
    ----------
    user_id : int
        The Milo user ID.  Used to look up the stored WHOOP OAuth2 token for
        this user (tokens will be stored encrypted in the database).

    Returns
    -------
    int | None
        Recovery score (0–100) if the WHOOP API is available and the user
        has connected their device.  Returns None if the API is unavailable,
        the user has not connected WHOOP, or the token has expired — so the
        caller can fall back to the manual slider.

    Notes
    -----
    Real implementation (requires WHOOP API approval):
        1. Load the user's stored OAuth2 access token from the database.
        2. GET https://api.prod.whoop.com/developer/v1/recovery/
           with Authorization: Bearer <token>
        3. Parse response["records"][0]["score"]["recovery_score"]
        4. Handle 401 (refresh token) and 403 (not connected) gracefully.

    WHOOP developer docs: https://developer.whoop.com/
    """
    # --- STUB: return None to signal "WHOOP not connected" ---
    # The Overview page will show the manual recovery slider in this case.
    return None
