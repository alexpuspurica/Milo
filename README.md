# Milo — Workout Tracker & Performance Predictor

A data science project built for the CS course at the University of St. Gallen (HSG).  
Milo is a Streamlit web app that helps athletes track their workouts, log performance, and receive machine learning-based recommendations on when to increase training weight.

---

## Problem Statement

Athletes who train consistently struggle to know when to increase weight or back off. Training too conservatively means leaving progress on the table; training too aggressively risks injury. Milo solves this by combining workout logging with a machine learning model trained on real strength athlete data, giving users a data-driven recommendation each session.

---

## Key Features

- **Workout planning** — define your weekly training schedule with custom exercises, sets, reps, and target weights
- **Session logging** — log actual sets completed vs planned each session
- **Recovery tracking** — manual recovery score input (1–10); WHOOP API integration for automatic recovery data (pending approval)
- **ML recommendation** — predicts whether you should increase weight next session based on your past performance and recovery
- **Progress visualisation** — charts showing weight progression and planned vs actual performance per exercise
- **Exercise library** — powered by the wger REST API, giving users a searchable database of exercises

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Data | SQLite (session logs), CSV (workout plans) |
| External API | wger Exercise API, WHOOP API (pending) |
| ML | scikit-learn (Random Forest, Logistic Regression, Boosting, Neural Net) |
| Training data | OpenPowerlifting dataset (openpowerlifting.org) |
| Language | Python 3.11 |

---

## ML Model

The ML component is trained on the OpenPowerlifting dataset (714k real competition results, filtered to Raw SBD meets from 2015 onwards).

**Task:** Binary classification — predict `improved` (1 = lifter increased their total vs previous session, 0 = did not improve)

**Features:** previous performance bands (squat/bench/deadlift/total), bodyweight change, days between sessions, age group, sex

**Models compared:** Naive Bayes, Logistic Regression (plain, Lasso, Ridge), Random Forest, Gradient Boosting, Neural Network — all with threshold tuning

See `data_cleaning.ipynb` and `models.ipynb` for the full pipeline.

---

## UI Plan

The app uses a **sidebar for navigation** between four pages.

---

### Page 1 — Overview

The landing page. Shows the user what is happening today at a glance.

```
Sidebar: [Overview] [Log] [Progress] [Settings]

Main area:
┌─────────────────────────────────────────┐
│  Today — Monday                         │
│  Workout: Push (Bench, OHP, Triceps)    │
├─────────────────────────────────────────┤
│  Recovery Score                         │
│  [Slider 1–10]  or  [Connect WHOOP]    │
├─────────────────────────────────────────┤
│  Milo Recommendation                    │
│  "Based on your last 3 sessions and     │
│   recovery score of 8, you are ready   │
│   to increase weight today."           │
└─────────────────────────────────────────┘
```

**Components:** `st.metric`, `st.slider`, `st.info` / `st.success` for the recommendation box

---

### Page 2 — Log

Where the user logs the actual workout. Shows today's planned session and lets them fill in what they actually did.

```
Sidebar: [Overview] [Log] [Progress] [Settings]

Main area:
  Monday — Push
  ┌──────────────────────────────────────────────────────┐
  │ Exercise      │ Planned        │ Actual         │ ✓  │
  │ Bench Press   │ 4 × 8 @ 80kg  │ [____] [____]  │ □  │
  │ OHP           │ 3 × 10 @ 50kg │ [____] [____]  │ □  │
  │ Tricep Press  │ 3 × 12 @ 30kg │ [____] [____]  │ □  │
  └──────────────────────────────────────────────────────┘
  [Save Session]
```

**Components:** `st.data_editor` or `st.form` with `st.number_input` per row, `st.checkbox` for completion, `st.button` to save

---

### Page 3 — Progress

Data visualisation page. Shows how the user is improving over time.

```
Sidebar: [Overview] [Log] [Progress] [Settings]

Main area:
  [Dropdown: select exercise]

  Weight over time (line chart)
  ────────────────────────────
  Planned vs Actual (bar chart per session)
  ────────────────────────────
  Completion rate (% sets completed)
```

**Components:** `st.selectbox` for exercise filter, `st.line_chart` / `st.bar_chart` or matplotlib charts via `st.pyplot`

---

### Page 4 — Settings

Where the user sets up their weekly training plan.

```
Sidebar: [Overview] [Log] [Progress] [Settings]

Main area:
  Weekly Schedule
  ┌──────────────────────────────────────┐
  │ Day        │ Workout Name            │
  │ Monday     │ [Push      ▼]          │
  │ Tuesday    │ [Rest      ▼]          │
  │ Wednesday  │ [Pull      ▼]          │
  │ ...                                  │
  └──────────────────────────────────────┘

  Exercise Builder
  [+ Add Exercise]
  Exercise name: [________] (search wger API)
  Sets: [3]  Reps: [10]  Weight: [80] kg
  [Save to plan]
```

**Components:** `st.selectbox`, `st.text_input` with wger API search, `st.number_input`, `st.button`

---

## File Structure

```
Milo/
├── app.py                      # Streamlit entry point + sidebar navigation
├── requirements.txt
├── privacy_policy.html
├── README.md
│
├── pages/                      # one file per app page
│   ├── overview.py
│   ├── log.py
│   ├── progress.py
│   └── settings.py
│
├── utils/                      # shared helper modules
│   ├── db.py                   # SQLite read/write helpers
│   ├── api.py                  # wger exercise API + WHOOP API calls
│   └── predict.py              # load model, run prediction
│
└── ml/                         # all ML work lives here
    ├── data_cleaning.ipynb     # cleans OpenPowerlifting data → milo_clean.csv
    ├── models.ipynb            # trains 8 classifiers, compares, saves best model
    └── data/
        ├── raw/
        │   └── openpowerlifting_filtered.csv   # 47MB source data
        ├── milo_model.pkl      # saved best model (loaded by utils/predict.py)
        ├── feature_columns.pkl
        └── charts/
            ├── accuracy_comparison.png
            ├── f1_comparison.png
            └── feature_importance.png
```

---

## How It All Connects

### Training Phase (run once, offline)

The ML model is trained before the app is used. The two notebooks in `ml/` handle this:

```
openpowerlifting_filtered.csv
        │
        ▼
data_cleaning.ipynb
(cleans data, engineers features, bins numbers into bands)
        │
        ▼
milo_clean.csv
        │
        ▼
models.ipynb
(trains 8 classifiers, picks the best one, saves it)
        │
        ▼
milo_model.pkl        ← the only file the app needs at runtime
feature_columns.pkl
```

### App Runtime (what happens when a user opens Milo)

```
User logs workouts           User sets up profile
(Log page → SQLite)          (Settings page → SQLite)
        │                             │
        └──────────────┬──────────────┘
                       │
                       ▼
              utils/predict.py
        (reads SQLite, builds feature vector)

        days since last session  →  days_band
        bodyweight change        →  bodyweight_change_band
        recent performance       →  prev_total_band
        age (from profile)       →  age_band
        sex (from profile)       →  is_female
                       │
                       ▼
             milo_model.pkl
        (same feature format it was trained on)
                       │
                       ▼
         "Increase / Maintain / Back off"
                       │
                       ▼
            Overview page → shown to user
```

### The Exercise Problem

The training data uses powerlifting totals (squat + bench + deadlift). Milo users can track hundreds of custom exercises. The model bridges this gap because it predicts **session-level readiness**, not exercise-specific progress.

In the Settings page, users label one exercise as their squat/bench/deadlift equivalent (or a single "main lift"). `predict.py` sums those to compute a pseudo-total, bins it into the same band the model was trained on, and returns a recommendation. Every other exercise in the log uses a simple rule: if you hit all your planned sets last session, suggest increasing weight next time.

The ML sets the overall session tone. Per-exercise progressions follow the app's rule-based logic.

### Where Everything Lives

| File | Role |
|---|---|
| `utils/predict.py` | Loads model, builds feature vector from SQLite, returns recommendation |
| `utils/db.py` | All SQLite reads and writes |
| `utils/api.py` | wger exercise API + WHOOP API calls |
| `pages/overview.py` | Calls `predict.py`, shows today's recommendation |
| `pages/log.py` | Calls `db.py` to save session data |
| `pages/progress.py` | Calls `db.py` to build charts |
| `pages/settings.py` | Calls `api.py` and `db.py` for plan setup |
| `ml/data/milo_model.pkl` | Saved trained model, loaded by `predict.py` |
| `ml/data/feature_columns.pkl` | Column order the model expects |

---

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Team & Contributions

| Member | Responsibilities |
|---|---|
| Alexandru Puspurica | Project lead, ML pipeline, data cleaning, WHOOP API |
| [Teammate 2] | Streamlit UI, Log and Progress pages |
| [Teammate 3] | Settings page, wger API integration, database layer |

A full contribution matrix is included in the project submission.

---

## Data Source

[OpenPowerlifting](https://openpowerlifting.org) — open dataset of powerlifting competition results.  
Licensed under the [OpenPowerlifting Data License](https://openpowerlifting.gitlab.io/opl-csv/bulk-csv-docs.html).
