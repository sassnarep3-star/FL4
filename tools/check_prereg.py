#!/usr/bin/env python3
"""Pre-registration ledger, leaderboard guard, results-feed and price-store checks.

Usage (repo root):
  python3 tools/check_prereg.py --register   # (re)write data/prereg.json hashes; do this ONCE, then commit
  python3 tools/check_prereg.py              # verify: fails if any registered definition changed, or any guard is broken

Rules enforced:
  * Every strategy in data/signals/strategies.json is registered with a SHA-256 of its canonical JSON.
    Editing a strategy after registration fails the check. A changed rule needs a NEW registration
    (new id), recorded in COORDINATION.md, so results cannot be re-fitted to a rule that has already been seen.
  * The gate file data/signals/gates.json is hashed the same way.
  * Leaderboard entries must reference a registered strategy and be prospective. Backtest numbers are barred:
    any entry whose evidence_type is not 'prospective' fails the build.
  * data/results_feed.json: a row marked Final must carry both scores; a non-final row must carry null scores.
  * data/price_snapshots.json: any row must carry open/close timestamps, a source, and a prereg_id.
  * Public layer privacy: data/capture_summary_w10_2026.json must not contain player-level keys.
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data"
PREREG = D / "prereg.json"
STRAT = ROOT / "data" / "signals" / "strategies.json"
GATES = ROOT / "data" / "signals" / "gates.json"
LEADERBOARD = ROOT / "data" / "signals" / "leaderboard.json"


def canon_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_entries():
    strategies = json.loads(STRAT.read_text(encoding="utf-8"))["strategies"]
    return [{"id": s["id"], "name": s["name"], "bet_type": s.get("bet_type", ""), "sha256": canon_hash(s)} for s in strategies]


def register():
    prev = json.loads(PREREG.read_text(encoding="utf-8")) if PREREG.exists() else {}
    doc = {
        "as_of": "2026-11-16",
        "registry": "Pre-registration of strategy definitions, gates and evaluation windows",
        "rule": "Hashes below are SHA-256 of canonical JSON (sorted keys, no whitespace). The commit that first adds this file is the registration. Any later change to a registered definition fails tools/check_prereg.py.",
        "sample_window": "NOT SET - reviewer decision (Q-06). No evaluation window has been opened.",
        "evaluation_window": "NOT OPENED",
        "registration_commit": prev.get("registration_commit", "PENDING - recorded in COORDINATION.md after the first commit"),
        "gates_file": "data/signals/gates.json",
        "gates_sha256": file_hash(GATES),
        "strategies_file": "data/signals/strategies.json",
        "strategies": current_entries(),
    }
    PREREG.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"registered {len(doc['strategies'])} strategies + gates file -> {PREREG.relative_to(ROOT)}")
    return 0


def check():
    errors = []
    if not PREREG.exists():
        print("FAIL: data/prereg.json missing")
        return 1
    reg = json.loads(PREREG.read_text(encoding="utf-8"))

    if file_hash(GATES) != reg.get("gates_sha256"):
        errors.append("gate file changed after registration (data/signals/gates.json): re-register under a new id")
    reg_by_id = {e["id"]: e for e in reg.get("strategies", [])}
    for cur in current_entries():
        r = reg_by_id.get(cur["id"])
        if r is None:
            errors.append(f"strategy {cur['id']} is not registered")
        elif r["sha256"] != cur["sha256"]:
            errors.append(f"strategy {cur['id']} changed after registration; a changed rule needs a new registration id")
    cur_ids = {c["id"] for c in current_entries()}
    for rid in reg_by_id:
        if rid not in cur_ids:
            errors.append(f"registered strategy {rid} no longer exists in strategies.json (retirement must be logged, not deleted)")

    # Leaderboard guard: backtest numbers may never appear on the leaderboard.
    lb_doc = json.loads(LEADERBOARD.read_text(encoding="utf-8"))
    lb = lb_doc.get("entries", [])
    if not isinstance(lb, list):
        errors.append("data/signals/leaderboard.json 'entries' must be a list")
        lb = []
    # The file's worked_example is labelled synthetic arithmetic. Report its presence; never quote it as a result.
    worked = lb_doc.get("worked_example", {})
    if isinstance(worked, dict) and worked.get("synthetic") is not True:
        errors.append("leaderboard worked_example must be labelled synthetic=true")
    for i, row in enumerate(lb):
        if row.get("evidence_type") != "prospective":
            errors.append(f"leaderboard row {i}: evidence_type must be 'prospective' (backtests are barred from the leaderboard)")
        if row.get("prereg_id") not in reg_by_id:
            errors.append(f"leaderboard row {i}: prereg_id is not registered")

    # Results feed.
    rf = json.loads((D / "results_feed.json").read_text(encoding="utf-8"))
    for r in rf.get("rows", []):
        is_final = r.get("state") == "Final"
        has_scores = r.get("away_score") is not None and r.get("home_score") is not None
        if is_final and not has_scores:
            errors.append(f"results_feed {r.get('game_id')}: Final without both scores")
        if not is_final and (r.get("away_score") is not None or r.get("home_score") is not None):
            errors.append(f"results_feed {r.get('game_id')}: non-final row carries a score")
        if r.get("source") != "S32":
            errors.append(f"results_feed {r.get('game_id')}: source must be S32 (the schedule page actually read)")

    # Price snapshots.
    ps = json.loads((D / "price_snapshots.json").read_text(encoding="utf-8"))
    for i, row in enumerate(ps.get("rows", [])):
        for key in ("open_ts_utc", "close_ts_utc", "price_source", "prereg_id"):
            if not row.get(key):
                errors.append(f"price_snapshots row {i}: missing {key}")

    # Privacy: the public capture summary holds counts only.
    cap = D / "capture_summary_w10_2026.json"
    if cap.exists():
        def walk(o, path=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k.lower() in ("player", "players", "player_url", "name"):
                        errors.append(f"public capture summary has a player-level key at {path}/{k}")
                    walk(v, f"{path}/{k}")
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, f"{path}[{i}]")
        walk(json.loads(cap.read_text(encoding="utf-8")))

    if errors:
        print("FAIL: pre-registration and guard checks")
        for e in errors:
            print("  -", e)
        return 1
    print(f"OK: {len(reg_by_id)} strategies match their registration; gates unchanged; "
          f"leaderboard rows {len(lb)} (all prospective and registered); results feed {len(rf.get('rows', []))} rows; "
          f"price store {len(ps.get('rows', []))} rows; no player-level keys in the public capture summary.")
    return 0


if __name__ == "__main__":
    if "--register" in sys.argv:
        sys.exit(register())
    sys.exit(check())
