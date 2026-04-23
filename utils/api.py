"""
utils/api.py — External API helpers
=====================================
This module handles outbound HTTP calls to third-party services:

1. **wger Exercise API** (https://wger.de/api/v2/)
   Open-source exercise database.  No authentication required for read-only
   endpoints.  Used on the Settings page to let users search for exercises by
   name and retrieve muscle group / category metadata.

2. **WHOOP API** (https://developer.whoop.com/api/)
   OAuth2 authorization code flow. Provides profile, body measurements, and
   recovery scores. Tokens are stored in the database and auto-refreshed.
"""

import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

WHOOP_BASE      = "https://api.prod.whoop.com/developer"
WHOOP_AUTH_URL  = "https://api.prod.whoop.com/oauth/oauth2/auth"
WHOOP_TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
WHOOP_SCOPES    = "read:profile read:body_measurement read:recovery"


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
# WHOOP OAuth2
# ---------------------------------------------------------------------------

def get_whoop_auth_url(client_id: str, redirect_uri: str) -> str:
    params = {
        "client_id":     client_id,
        "redirect_uri":  redirect_uri,
        "scope":         WHOOP_SCOPES,
        "response_type": "code",
    }
    return f"{WHOOP_AUTH_URL}?{urlencode(params)}"


def exchange_whoop_code(client_id: str, client_secret: str,
                        code: str, redirect_uri: str) -> dict:
    import requests
    resp = requests.post(
        WHOOP_TOKEN_URL,
        data={
            "grant_type":    "authorization_code",
            "code":          code,
            "client_id":     client_id,
            "client_secret": client_secret,
            "redirect_uri":  redirect_uri,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _refresh_if_needed(tokens: dict) -> dict:
    """Return tokens, refreshing the access token if it expires within 60 s."""
    import requests
    expires_at = tokens.get("expires_at") or 0
    if time.time() < expires_at - 60:
        return tokens
    resp = requests.post(
        WHOOP_TOKEN_URL,
        data={
            "grant_type":    "refresh_token",
            "refresh_token": tokens["refresh_token"],
            "client_id":     tokens["client_id"],
            "client_secret": tokens["client_secret"],
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    tokens["access_token"]  = data["access_token"]
    tokens["refresh_token"] = data.get("refresh_token", tokens["refresh_token"])
    tokens["expires_at"]    = time.time() + data.get("expires_in", 3600)
    return tokens


def _whoop_get(path: str, tokens: dict, params: dict = None):
    import requests
    tokens = _refresh_if_needed(tokens)
    resp = requests.get(
        f"{WHOOP_BASE}{path}",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json(), tokens


# ---------------------------------------------------------------------------
# WHOOP data endpoints
# ---------------------------------------------------------------------------

def get_whoop_profile(tokens: dict) -> tuple[dict, dict]:
    """Returns (profile_dict, updated_tokens)."""
    data, tokens = _whoop_get("/v2/user/profile/basic", tokens)
    return data, tokens


def get_whoop_body_measurement(tokens: dict) -> tuple[dict, dict]:
    """Returns (body_dict, updated_tokens). Keys: height_meter, weight_kilogram, max_heart_rate."""
    data, tokens = _whoop_get("/v2/user/measurement/body", tokens)
    return data, tokens


def get_whoop_recovery(tokens: dict, days: int = 2) -> tuple[list, dict]:
    """Returns (list of recovery records newest-first, updated_tokens)."""
    start = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    data, tokens = _whoop_get("/v2/recovery", tokens, params={"start": start, "limit": days})
    records = data.get("records", [])
    return records, tokens
