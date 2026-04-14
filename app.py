from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder="templates")


# ─────────────────────────────────────────────
# CSP + Search Algorithm Core
# ─────────────────────────────────────────────

def build_domain(schedules, duration):
    """
    State Space: generate all candidate time slots (states) from participants' windows.
    Each slot is a tuple (start, end) with 30-minute granularity.
    """
    times = set()
    for windows in schedules.values():
        for (s, e) in windows:
            t = s
            while t < e:
                times.add(round(t, 1))
                t += 0.5
    domain = []
    for t in sorted(times):
        slot = (t, round(t + duration, 1))
        if slot[1] <= 24:
            domain.append(slot)
    return domain


def satisfies_constraint(slot, person_windows):
    """
    CSP Constraint Check: does slot fit inside ANY of the person's available windows?
    """
    for (s, e) in person_windows:
        if slot[0] >= s and slot[1] <= e:
            return True
    return False


def heuristic_score(slot, schedules):
    """
    Heuristic / scoring function: count participants whose constraints are satisfied.
    Returns (score, matched_names, missed_names).
    """
    matched, missed = [], []
    for name, windows in schedules.items():
        if satisfies_constraint(slot, windows):
            matched.append(name)
        else:
            missed.append(name)
    return len(matched), matched, missed


def search_best_slot(schedules, duration):
    """
    State Space Search: iterate over all candidate slots (states),
    apply heuristic, return the globally optimal slot.
    Also returns a ranked list of top-5 alternatives.
    """
    domain = build_domain(schedules, duration)
    best_slot = None
    best_score = -1
    best_matched = []
    best_missed = []
    all_scored = []

    for slot in domain:
        score, matched, missed = heuristic_score(slot, schedules)
        all_scored.append((score, slot, matched, missed))
        if score > best_score:
            best_score = score
            best_slot = slot
            best_matched = matched
            best_missed = missed

    # Sort descending by score for alternatives
    all_scored.sort(key=lambda x: (-x[0], x[1][0]))
    alternatives = []
    seen = set()
    for score, slot, matched, missed in all_scored:
        key = (slot[0], slot[1])
        if key != (best_slot[0] if best_slot else None, best_slot[1] if best_slot else None) and key not in seen:
            seen.add(key)
            alternatives.append({
                "start": slot[0], "end": slot[1],
                "score": score,
                "matched": matched,
                "total": len(schedules)
            })
        if len(alternatives) >= 4:
            break

    return best_slot, best_score, best_matched, best_missed, alternatives


def fmt(h):
    hh = int(h)
    mm = int(round((h - hh) * 60))
    return f"{hh:02d}:{mm:02d}"


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/schedule", methods=["POST"])
def schedule():
    data = request.get_json()
    try:
        duration = float(data.get("duration", 1))
        participants = data.get("participants", [])

        if not participants:
            return jsonify({"error": "No participants provided."}), 400

        schedules = {}
        for p in participants:
            name = p.get("name", "").strip() or "Unnamed"
            windows = []
            for w in p.get("windows", []):
                s, e = float(w["start"]), float(w["end"])
                if 0 <= s < e <= 24:
                    windows.append((s, e))
            if not windows:
                return jsonify({"error": f"Participant '{name}' has no valid availability windows."}), 400
            schedules[name] = windows

        slot, score, matched, missed, alternatives = search_best_slot(schedules, duration)

        if not slot:
            return jsonify({"error": "No valid time slot found for the given constraints."}), 200

        total = len(schedules)
        return jsonify({
            "best": {
                "start": slot[0],
                "end": slot[1],
                "label": f"{fmt(slot[0])} – {fmt(slot[1])}",
                "score": score,
                "total": total,
                "coverage": round(score / total * 100),
                "matched": matched,
                "missed": missed,
            },
            "alternatives": alternatives,
            "schedules": {name: [{"start": s, "end": e} for s, e in wins] for name, wins in schedules.items()}
        })

    except Exception as ex:
        return jsonify({"error": f"Server error: {str(ex)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)