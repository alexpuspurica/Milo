import streamlit as st
import datetime

from utils.auth import require_login, render_sidebar_user
from utils.api import get_whoop_recovery
from utils.db import get_today_workout, save_session

require_login()
render_sidebar_user()

# ── CSS ───────────────────────────────────────────────────────────────────────
# Orange tap-to-edit cell buttons; purple border on active number inputs;
# hide the up/down spinner arrows so inputs look like plain cells.
st.markdown("""
<style>
/* Tap-to-edit cell buttons */
[data-testid="baseButton-secondary"] {
    background-color : #151c2e !important;
    border           : 1px solid #2e3a58 !important;
    border-radius    : 8px    !important;
    color            : #FFB347 !important;
    font-weight      : 700    !important;
    font-size        : 0.95rem !important;
}
[data-testid="baseButton-secondary"]:hover {
    border-color : #7c6afa !important;
    color        : #ffd080 !important;
}

/* Active number input (edit mode) */
input[type="number"] {
    background-color : #151c2e !important;
    border           : 2px solid #7c6afa !important;
    border-radius    : 8px !important;
    color            : #FFB347 !important;
    text-align       : center !important;
    font-weight      : 700 !important;
    font-size        : 0.95rem !important;
}

/* Hide spinner arrows */
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; }
input[type=number] { -moz-appearance: textfield; }

/* Tighten column gaps for the table rows */
[data-testid="stHorizontalBlock"] { gap: 0.4rem; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
USER_ID = st.session_state["user_id"]
COL_W   = [0.4, 1.1, 1.1, 1.7, 1.7, 0.7]   # Set | Plan kg | Plan rep | Actual kg | Reps | Done

# ── Load today's plan into session state once ─────────────────────────────────
if "log_plan" not in st.session_state:
    st.session_state["log_plan"] = get_today_workout(USER_ID)

plan     = st.session_state["log_plan"]
day_name = datetime.datetime.today().strftime("%A")

# ── Page header ───────────────────────────────────────────────────────────────
st.title(f"{day_name} — {plan['workout_name']}")

# ── Recovery-based plan adjustment ───────────────────────────────────────────
with st.expander("Change today's plan based on recovery score"):
    whoop = get_whoop_recovery(USER_ID)

    if whoop is not None:
        recovery = whoop
        st.metric("WHOOP Recovery", f"{recovery} / 100")
    else:
        recovery = (
            st.slider("How do you feel today?  (1 = exhausted · 10 = great)", 1, 10, 7) * 10
        )
        st.caption("WHOOP not connected — using manual score")

    # Determine multipliers from recovery band
    if   recovery >= 80: msg, w_mult, r_adj = "Full plan — you're ready.",          1.00,  0
    elif recovery >= 60: msg, w_mult, r_adj = "Slight deload — 95% weight.",         0.95,  0
    elif recovery >= 40: msg, w_mult, r_adj = "Moderate deload — 90% weight, −1 rep.", 0.90, -1
    elif recovery >= 20: msg, w_mult, r_adj = "Significant deload — 80% weight, −2 reps.", 0.80, -2
    else:                msg, w_mult, r_adj = "Heavy deload — 70% weight, −2 reps.", 0.70, -2

    st.info(msg)

    if st.button("Apply to today's plan", use_container_width=True, type="primary"):
        for ex in st.session_state["log_plan"]["exercises"]:
            ex["_adj_kg"]   = round(ex["weight_kg"] * w_mult / 2.5) * 2.5
            ex["_adj_reps"] = max(1, ex["reps"] + r_adj)
        # Wipe cached cell values so inputs reinitialise from the new plan
        for k in list(st.session_state.keys()):
            if k.startswith(("val_kg_", "val_rp_", "edit_kg_", "edit_rp_", "inp_kg_", "inp_rp_")):
                del st.session_state[k]
        st.rerun()

st.divider()

# ── Column header row ─────────────────────────────────────────────────────────
h = st.columns(COL_W)
for col, lbl in zip(h, ["Set", "Plan kg", "Plan rep", "Actual kg", "Reps", "Done"]):
    col.markdown(
        f"<span style='color:#555;font-size:0.8rem;font-weight:600'>{lbl}</span>",
        unsafe_allow_html=True,
    )

# ── Exercise sections ─────────────────────────────────────────────────────────
for ex in plan["exercises"]:
    name   = ex["name"]
    p_kg   = ex.get("_adj_kg",   ex["weight_kg"])
    p_reps = ex.get("_adj_reps", ex["reps"])
    n_sets = ex["sets"]

    st.markdown(f"**{name}**")

    for i in range(n_sets):
        c = st.columns(COL_W)

        # Read-only plan cells — orange
        c[0].markdown(f":orange[{i + 1}]")
        c[1].markdown(f":orange[**{p_kg:g}**]")
        c[2].markdown(f":orange[**{p_reps}**]")

        # ── Actual kg — tap to edit ───────────────────────────────────────────
        k_ev  = f"edit_kg_{name}_{i}"
        k_vv  = f"val_kg_{name}_{i}"
        k_inp = f"inp_kg_{name}_{i}"

        if k_vv not in st.session_state:
            st.session_state[k_vv] = float(p_kg)

        if st.session_state.get(k_ev):
            def _save_kg(_ke=k_ev, _kv=k_vv, _ki=k_inp):
                st.session_state[_kv] = st.session_state[_ki]
                st.session_state[_ke] = False

            c[3].number_input(
                "", min_value=0.0, max_value=500.0,
                value=st.session_state[k_vv], step=2.5,
                key=k_inp, on_change=_save_kg, label_visibility="collapsed",
            )
        else:
            v = st.session_state[k_vv]
            if c[3].button(
                f"{v:g}" if v else "—",
                key=f"btn_kg_{name}_{i}", use_container_width=True,
            ):
                st.session_state[k_ev] = True
                st.rerun()

        # ── Actual reps — tap to edit ─────────────────────────────────────────
        k_er  = f"edit_rp_{name}_{i}"
        k_vr  = f"val_rp_{name}_{i}"
        k_inr = f"inp_rp_{name}_{i}"

        if k_vr not in st.session_state:
            st.session_state[k_vr] = int(p_reps)

        if st.session_state.get(k_er):
            def _save_rp(_ke=k_er, _kv=k_vr, _ki=k_inr):
                st.session_state[_kv] = st.session_state[_ki]
                st.session_state[_ke] = False

            c[4].number_input(
                "", min_value=0, max_value=50,
                value=st.session_state[k_vr], step=1,
                key=k_inr, on_change=_save_rp, label_visibility="collapsed",
            )
        else:
            v = st.session_state[k_vr]
            if c[4].button(
                str(v) if v else "—",
                key=f"btn_rp_{name}_{i}", use_container_width=True,
            ):
                st.session_state[k_er] = True
                st.rerun()

        # ── Done checkbox ─────────────────────────────────────────────────────
        c[5].checkbox("", key=f"done_{name}_{i}", label_visibility="collapsed")

    st.divider()

# ── Submit ────────────────────────────────────────────────────────────────────
if st.button("Save Session", use_container_width=True, type="primary"):
    results = []
    for ex in plan["exercises"]:
        name   = ex["name"]
        p_kg   = ex.get("_adj_kg",   ex["weight_kg"])
        p_reps = ex.get("_adj_reps", ex["reps"])
        for i in range(ex["sets"]):
            results.append({
                "name":              name,
                "planned_weight_kg": p_kg,
                "planned_reps":      p_reps,
                "actual_weight_kg":  st.session_state.get(f"val_kg_{name}_{i}", float(p_kg)),
                "actual_reps":       st.session_state.get(f"val_rp_{name}_{i}", int(p_reps)),
                "completed":         st.session_state.get(f"done_{name}_{i}", False),
            })

    ok = save_session(USER_ID, results)
    if ok:
        st.success("Session saved! Great work today.")
        # Clear all log state so the page is fresh for the next session
        stale_prefixes = (
            "val_kg_", "val_rp_", "edit_kg_", "edit_rp_",
            "inp_kg_", "inp_rp_", "done_", "log_plan",
        )
        for k in list(st.session_state.keys()):
            if any(k.startswith(p) for p in stale_prefixes):
                del st.session_state[k]
    else:
        st.error("Something went wrong. Please try again.")
