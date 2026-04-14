# 🗓️ AI Meeting Scheduler

An intelligent meeting scheduler that finds the optimal time slot for a group of participants using **Constraint Satisfaction Problem (CSP)** solving and **heuristic state space search**.

> Built by **Harshith**

---

## ✨ How It Works

You add participants and their available time windows. The AI finds the best meeting slot that satisfies the most constraints.

**AI Techniques used:**
- **CSP (Constraint Satisfaction Problem)** — each participant's availability is a constraint
- **State Space Search** — generates all candidate time slots as states
- **Heuristic Scoring** — scores each state by how many participants it satisfies
- **Greedy Best-First Selection** — picks the globally optimal slot + top 4 alternatives

---

## 🚀 Quick Start

### Step 1 — Install dependencies

```bash
pip install flask
```

### Step 2 — Run the app

```bash
python app.py
```

### Step 3 — Open in browser

```
http://127.0.0.1:5000
```

That's it — no API keys, no config needed.

---

## 🎮 How to Use

1. Click **+ add participant** for each person
2. Enter their name
3. Add their available time windows (e.g. start: `9`, end: `12` = 9am to 12pm)
4. Set the meeting duration in hours
5. Click **Find optimal slot**

The AI will show:
- ✅ The best time slot with coverage %
- 👥 Who is available / unavailable
- 📊 Visual availability timeline
- 🔁 Top 4 alternative slots

---

## 📁 Project Structure

```
meeting_scheduler/
├── app.py              # Flask backend + CSP search algorithm
└── templates/
    └── index.html      # Frontend UI
```

---

## 🤖 AI Algorithm (app.py)

| Function | Role |
|----------|------|
| `build_domain()` | Generates all candidate time slots (state space) |
| `satisfies_constraint()` | CSP constraint checker per participant |
| `heuristic_score()` | Scores each slot by participants matched |
| `search_best_slot()` | Iterates state space, returns optimal + alternatives |

---

## ⚠️ Troubleshooting

**Flask not found?**
```bash
pip install flask
```

**Port already in use?**
```bash
python app.py --port 5001
```

**Page not loading?**
→ Make sure `app.py` is running and visit `http://127.0.0.1:5000`
