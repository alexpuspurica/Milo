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
├── app.py                  # Streamlit entry point + sidebar navigation
├── pages/
│   ├── overview.py
│   ├── log.py
│   ├── progress.py
│   └── settings.py
├── db.py                   # SQLite read/write helpers
├── api.py                  # wger exercise API + WHOOP API calls
├── ml.py                   # load model, run prediction
├── data_cleaning.ipynb     # cleans OpenPowerlifting data
├── models.ipynb            # trains and compares all ML models
├── data/
│   ├── raw/
│   │   └── openpowerlifting_filtered.csv
│   ├── milo_model.pkl      # saved best model
│   └── feature_columns.pkl
├── privacy_policy.html
└── requirements.txt
```

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
