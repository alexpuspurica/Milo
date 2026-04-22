"""
utils/styles.py — Global CSS injection and shared UI helpers
=============================================================
This module is the single source of truth for Milo's visual design system.

Every page imports and calls ``inject_styles()`` as its first statement
(after ``set_page_config``) so that fonts, colours, and component overrides
are applied consistently across the entire app.

Design tokens
-------------
    Iris   #8B4FCC  — primary accent (buttons, slider thumb, active states)
    Abyss  #1C0435  — deepest background (app canvas)
    Violet #3D0A6B  — elevated surface (sidebar, cards, input backgrounds)
    Frost  #F2EBFF  — primary text
    Muted  #C4B5DC  — secondary / label text
    Iris-L #A97DD4  — light iris for hover states and subtle accents

Typography
----------
    Syne          — display / heading font (weights 600, 700, 800)
    IBM Plex Sans — body / UI font (weights 300, 400, 500, 600)
    Both loaded from Google Fonts via @import inside the injected <style>.

Helper functions
----------------
    inject_styles()        — injects the full CSS blob + Google Font import
    sidebar_brand()        — renders the Milo logo strip in the sidebar
    card(title, body, ...)  — renders a styled purple card via st.markdown
    recommendation_card()  — renders the ML recommendation banner
"""

import base64
import os

import streamlit as st

_MODULE_DIR   = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_MODULE_DIR)


def _logo_b64() -> str:
    logo_path = os.path.join(_PROJECT_ROOT, "logo.png")
    try:
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

# ---------------------------------------------------------------------------
# CSS blob
# All rules live here so they can be reviewed and edited in one place.
# ---------------------------------------------------------------------------

_CSS = """
<style>

/* ================================================================
   1. GOOGLE FONTS
   Import Syne (headings) and IBM Plex Sans (body) from Google CDN.
   ================================================================ */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

/* ================================================================
   2. CSS CUSTOM PROPERTIES (design tokens)
   Referenced throughout the rest of this file for consistency.
   ================================================================ */
:root {
    --iris:       #8B4FCC;   /* primary accent */
    --iris-light: #A97DD4;   /* hover / subtle accent */
    --iris-glow:  rgba(139, 79, 204, 0.35);
    --abyss:      #1C0435;   /* deepest background */
    --violet:     #3D0A6B;   /* elevated surface */
    --frost:      #F2EBFF;   /* primary text */
    --muted:      #C4B5DC;   /* secondary / label text */
    --border:     rgba(139, 79, 204, 0.28);
    --card-bg:    rgba(61, 10, 107, 0.55);
    --shadow:     0 4px 28px rgba(0, 0, 0, 0.45);
    --radius:     12px;
    --radius-sm:  8px;
}

/* ================================================================
   3. GLOBAL BODY & TYPOGRAPHY
   ================================================================ */

/* Apply IBM Plex Sans to every element by default */
html, body, [class*="css"], .stApp, .stMarkdown, p, span, label,
input, textarea, button, select, [data-testid] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    color: var(--frost);
}

/* App canvas background */
.stApp {
    background-color: var(--abyss) !important;
}

/* Content area — generous padding, capped width for readability */
.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 960px !important;
}

/* ================================================================
   4. HEADINGS — Syne font
   ================================================================ */

h1, h2, h3, h4,
.stMarkdown h1, .stMarkdown h2,
.stMarkdown h3, .stMarkdown h4 {
    font-family: 'Syne', sans-serif !important;
    color: var(--frost) !important;
    letter-spacing: -0.02em;
    line-height: 1.2;
}

h1, .stMarkdown h1 {
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    margin-bottom: 0.1rem !important;
}

h2, .stMarkdown h2 {
    font-size: 1.45rem !important;
    font-weight: 700 !important;
}

h3, .stMarkdown h3 {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
}

/* ================================================================
   5. SIDEBAR
   ================================================================ */

/* Main sidebar panel — deep violet gradient */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2E0A55 0%, var(--violet) 60%, #1C0435 100%) !important;
    border-right: 1px solid var(--border) !important;
}

/* All text inside the sidebar */
section[data-testid="stSidebar"] * {
    color: var(--frost) !important;
}

/* Nav link items */
section[data-testid="stSidebar"] a {
    border-radius: var(--radius-sm) !important;
    transition: background 0.18s ease !important;
    display: block;
}

section[data-testid="stSidebar"] a:hover {
    background: rgba(139, 79, 204, 0.22) !important;
    text-decoration: none !important;
}

/* Active page — left accent bar + background highlight */
section[data-testid="stSidebar"] [aria-selected="true"],
section[data-testid="stSidebar"] .st-emotion-cache-eczf2b {
    background: rgba(139, 79, 204, 0.32) !important;
    border-left: 3px solid var(--iris) !important;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0 !important;
}

/* ================================================================
   6. TOP HEADER BAR
   ================================================================ */

header[data-testid="stHeader"] {
    background: var(--abyss) !important;
    border-bottom: 1px solid var(--border) !important;
}

/* Hide the Streamlit default deploy/menu button area clutter */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

/* ================================================================
   7. BUTTONS
   ================================================================ */

/* Primary / default buttons */
div.stButton > button,
button[kind="primary"] {
    background: linear-gradient(135deg, var(--iris) 0%, #6B2FA8 100%) !important;
    color: var(--frost) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.6rem !important;
    transition: opacity 0.18s ease, transform 0.12s ease,
                box-shadow 0.18s ease !important;
    box-shadow: 0 2px 14px rgba(139, 79, 204, 0.45) !important;
    letter-spacing: 0.02em;
}

div.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(139, 79, 204, 0.55) !important;
}

div.stButton > button:active {
    transform: translateY(0) !important;
    opacity: 1 !important;
}

/* Form submit button — same gradient */
[data-testid="stForm"] button[type="submit"],
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, var(--iris) 0%, #6B2FA8 100%) !important;
    color: var(--frost) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 14px rgba(139, 79, 204, 0.45) !important;
}

/* ================================================================
   8. METRIC CARDS
   ================================================================ */

[data-testid="metric-container"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem 1.25rem !important;
    box-shadow: var(--shadow) !important;
}

/* Metric label — small caps, muted colour */
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* Metric value — large Syne number */
[data-testid="stMetricValue"] > div,
[data-testid="stMetricValue"] {
    color: var(--frost) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
}

/* Metric delta (positive = green, negative = red) */
[data-testid="stMetricDelta"] svg { display: none; }
[data-testid="stMetricDelta"] > div {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* ================================================================
   9. FORM INPUTS
   ================================================================ */

/* Text and number inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
textarea {
    background: rgba(61, 10, 107, 0.45) !important;
    color: var(--frost) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
textarea:focus {
    border-color: var(--iris) !important;
    box-shadow: 0 0 0 2px var(--iris-glow) !important;
    outline: none !important;
}

/* Input labels */
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label {
    color: var(--muted) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* Selectbox container */
[data-testid="stSelectbox"] > div > div {
    background: rgba(61, 10, 107, 0.45) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--frost) !important;
}

/* Slider thumb + track */
[data-testid="stSlider"] .st-bx,
[data-testid="stSlider"] [role="slider"] {
    background: var(--iris) !important;
}

/* Checkbox */
[data-testid="stCheckbox"] label {
    color: var(--frost) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* ================================================================
   10. ALERT / INFO BOXES
   ================================================================ */

[data-testid="stAlert"],
.stAlert {
    background: rgba(61, 10, 107, 0.50) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--frost) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* Specific variants */
[data-testid="stAlert"][data-baseweb="notification"] {
    background: rgba(61, 10, 107, 0.50) !important;
}

/* ================================================================
   11. DIVIDERS
   ================================================================ */

hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    opacity: 0.6 !important;
    margin: 1.25rem 0 !important;
}

/* ================================================================
   12. DATAFRAMES / TABLES
   ================================================================ */

[data-testid="stDataFrame"],
[data-testid="stDataEditor"] {
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
}

/* ================================================================
   13. EXPANDER
   ================================================================ */

[data-testid="stExpander"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ================================================================
   14. TABS
   ================================================================ */

[data-testid="stTabs"] button {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--iris) !important;
    border-bottom-color: var(--iris) !important;
}

</style>
"""

# ---------------------------------------------------------------------------
# Plotly dark theme configuration
# Imported by pages that render charts so all charts share the same look.
# ---------------------------------------------------------------------------

PLOTLY_CONFIG = {
    # Passed as the `config` argument to st.plotly_chart — hides the default
    # toolbar for a cleaner look.
    "displayModeBar": False,
    "responsive": True,
}

PLOTLY_LAYOUT = {
    # Applied via fig.update_layout(**PLOTLY_LAYOUT) on every chart.
    "paper_bgcolor": "rgba(0,0,0,0)",          # transparent — shows card bg
    "plot_bgcolor":  "rgba(61, 10, 107, 0.30)",# faint violet grid area
    "font": {
        "family": "IBM Plex Sans, sans-serif",
        "color":  "#F2EBFF",
        "size":   13,
    },
    "xaxis": {
        "gridcolor":  "rgba(139, 79, 204, 0.18)",
        "linecolor":  "rgba(139, 79, 204, 0.30)",
        "tickcolor":  "#C4B5DC",
        "showgrid":   True,
        "zeroline":   False,
    },
    "yaxis": {
        "gridcolor":  "rgba(139, 79, 204, 0.18)",
        "linecolor":  "rgba(139, 79, 204, 0.30)",
        "tickcolor":  "#C4B5DC",
        "showgrid":   True,
        "zeroline":   False,
    },
    "legend": {
        "bgcolor":     "rgba(28, 4, 53, 0.7)",
        "bordercolor": "rgba(139, 79, 204, 0.3)",
        "borderwidth": 1,
        "font":        {"color": "#F2EBFF"},
    },
    "margin": {"l": 10, "r": 10, "t": 36, "b": 10},
    "hoverlabel": {
        "bgcolor":    "#3D0A6B",
        "bordercolor":"#8B4FCC",
        "font":       {"family": "IBM Plex Sans", "color": "#F2EBFF"},
    },
}

# Brand colour sequence for chart series
PLOTLY_COLORS = ["#8B4FCC", "#C4B5DC", "#A97DD4", "#6B2FA8", "#F2EBFF"]


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def inject_styles() -> None:
    """
    Inject the Milo CSS design system into the current Streamlit page.

    Call this as the **first** statement inside every page (after
    ``st.set_page_config`` in app.py, or at the top of each page file).
    The CSS is injected via ``st.markdown(..., unsafe_allow_html=True)``.

    The injection is idempotent — calling it multiple times on the same page
    does no harm (the browser deduplicates identical ``<style>`` blocks).
    """
    # Inject the CSS blob defined at the top of this module.
    # unsafe_allow_html=True is required for raw <style> tags.
    st.markdown(_CSS, unsafe_allow_html=True)


def sidebar_brand() -> None:
    """Render the Milo logo and tagline at the top of the sidebar."""
    logo_b64 = _logo_b64()
    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" '
        f'style="width:56px; height:56px; object-fit:contain; margin-bottom:0.4rem;">'
        if logo_b64 else ""
    )
    st.sidebar.markdown(
        f"""
        <div style="
            padding: 1rem 0.5rem 1.5rem;
            text-align: center;
            border-bottom: 1px solid rgba(139, 79, 204, 0.30);
            margin-bottom: 0.75rem;
        ">
            {logo_html}
            <div style="
                font-family: 'Syne', sans-serif;
                font-size: 1.9rem;
                font-weight: 800;
                color: #F2EBFF;
                letter-spacing: -0.03em;
            ">Milo</div>
            <p style="
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.68rem;
                color: #C4B5DC;
                letter-spacing: 0.14em;
                text-transform: uppercase;
                margin: 0.3rem 0 0;
            ">Workout Tracker</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, body: str, variant: str = "default") -> None:
    """
    Render a styled purple card using an HTML block.

    Parameters
    ----------
    title : str
        Short overline label shown above the body in small-caps muted text
        (e.g. "Today's Workout", "Recovery Score").
    body : str
        HTML string for the main card content.  May contain ``<b>``, ``<br>``,
        ``<span>``, etc.
    variant : str, optional
        Visual variant controlling the border and background:
            "default"  — subtle violet card (default)
            "accent"   — iris-tinted border + slightly lighter background
            "success"  — green-tinted border for positive recommendations
            "warning"  — amber-tinted border for "hold" recommendations

    Notes
    -----
    Uses ``st.markdown(..., unsafe_allow_html=True)`` internally.
    Cards are pure HTML so they can hold any inline content without being
    constrained by Streamlit component layouts.
    """
    # Map variant to border/background colours
    _variants = {
        "default": {
            "border": "rgba(139, 79, 204, 0.28)",
            "bg":     "rgba(61, 10, 107, 0.55)",
            "title":  "#C4B5DC",
        },
        "accent": {
            "border": "#8B4FCC",
            "bg":     "rgba(139, 79, 204, 0.18)",
            "title":  "#A97DD4",
        },
        "success": {
            "border": "rgba(72, 199, 142, 0.55)",
            "bg":     "rgba(72, 199, 142, 0.08)",
            "title":  "#48C78E",
        },
        "warning": {
            "border": "rgba(255, 189, 68, 0.55)",
            "bg":     "rgba(255, 189, 68, 0.08)",
            "title":  "#FFBD44",
        },
    }
    # Fallback to default if an unknown variant is passed
    v = _variants.get(variant, _variants["default"])

    html = f"""
    <div style="
        background:    {v['bg']};
        border:        1px solid {v['border']};
        border-radius: 12px;
        padding:       1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow:    0 4px 28px rgba(0, 0, 0, 0.45);
    ">
        <p style="
            font-family:    'IBM Plex Sans', sans-serif;
            font-size:      0.7rem;
            font-weight:    600;
            color:          {v['title']};
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin:         0 0 0.6rem 0;
        ">{title}</p>
        <div style="
            font-family: 'IBM Plex Sans', sans-serif;
            color:       #F2EBFF;
            line-height: 1.6;
        ">{body}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def recommendation_card(result: dict) -> None:
    """
    Render the Milo ML recommendation as a prominent banner card.

    Parameters
    ----------
    result : dict
        The dict returned by ``utils.predict.predict_increase()``.  Expected
        keys:
            "recommendation" (str)   — "increase" or "hold"
            "confidence"     (float) — 0.0–1.0
            "suggested_kg"   (float) — suggested weight for next session

    The card is green ("success" variant) when the recommendation is
    "increase" and amber ("warning") when it is "hold".  Confidence is shown
    as a percentage.
    """
    rec        = result["recommendation"]
    confidence = int(result["confidence"] * 100)
    kg         = result["suggested_kg"]

    if rec == "increase":
        variant  = "success"
        badge_bg = "rgba(72,199,142,0.20)"
        badge_fg = "#48C78E"
        badge    = "INCREASE"
        headline = "Ready to Increase"
        detail   = (
            f"Based on your recent sessions and today's recovery score, "
            f"Milo recommends pushing to <b>{kg} kg</b> this session. "
            f"You've been consistent — make it count."
        )
    else:
        variant  = "warning"
        badge_bg = "rgba(255,189,68,0.20)"
        badge_fg = "#FFBD44"
        badge    = "HOLD"
        headline = "Hold This Week"
        detail   = (
            f"Your recovery or recent completion rate suggests staying at "
            f"<b>{kg} kg</b> for now. Consistency at this load will build "
            f"the base for your next increase."
        )

    body = f"""
    <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.75rem;">
        <span style="
            font-family:'IBM Plex Sans',sans-serif; font-size:0.7rem;
            font-weight:700; letter-spacing:0.12em; color:{badge_fg};
            background:{badge_bg}; padding:0.2rem 0.6rem;
            border-radius:4px; border:1px solid {badge_fg};
        ">{badge}</span>
        <span style="font-family:'Syne',sans-serif; font-size:1.3rem;
                     font-weight:700; color:#F2EBFF;">{headline}</span>
        <span style="
            margin-left:auto;
            font-family:'IBM Plex Sans',sans-serif;
            font-size:0.78rem;
            color:#C4B5DC;
            background:rgba(61,10,107,0.6);
            padding:0.25rem 0.7rem;
            border-radius:99px;
            border:1px solid rgba(139,79,204,0.3);
        ">Confidence {confidence}%</span>
    </div>
    <p style="margin:0; font-size:0.95rem; color:#E8DCFF;">{detail}</p>
    """
    card("Milo Recommendation", body, variant=variant)
