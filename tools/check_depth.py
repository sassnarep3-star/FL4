#!/usr/bin/env python3
"""Integrity checks for the depth-route census and slot model (session f51d93e6).

Fails closed (exit 1) on any violation. Gate counts are recomputed from the
rows, so a hand-edited count cannot pass.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CENSUS = ROOT / "data/depth/route_census.json"
MODEL = ROOT / "data/depth/slot_model.json"
FLAGS = ROOT / "data/depth/flags.json"

CLUBS = {"ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN", "DET", "GB",
         "HOU", "IND", "JAX", "KC", "LV", "LAC", "LAR", "MIA", "MIN", "NE", "NO", "NYG",
         "NYJ", "PHI", "PIT", "SF", "SEA", "TB", "TEN", "WAS"}
AUTHORITY = {"official_club_labelled", "publisher_labels_unofficial", "club_news_says_unofficial",
             "no_label_seen_chunk0", "no_label_seen", "unverified"}
UNITS = {"offense", "defense", "special_teams"}

errors = []


def err(msg):
    errors.append(msg)


def main():
    census = json.loads(CENSUS.read_text())
    model = json.loads(MODEL.read_text())
    flags = json.loads(FLAGS.read_text())

    rows = census["rows"]
    abbrs = [r["abbr"] for r in rows]
    if len(rows) != 32 or set(abbrs) != CLUBS or len(set(abbrs)) != 32:
        err(f"census must have exactly the 32 clubs once each; got {len(rows)} rows")

    checked = 0
    html_text = 0
    unofficial = 0
    official = 0
    for r in rows:
        a = r["abbr"]
        if r["authority"] not in AUTHORITY:
            err(f"{a}: unknown authority {r['authority']!r}")
        if r["check"] == "checked":
            checked += 1
            if not r.get("source_url", "").startswith("https://"):
                err(f"{a}: checked row has no https source_url")
            if r.get("format") and str(r["format"]).startswith("HTML"):
                html_text += 1
        elif r["check"] == "not_checked":
            if r.get("depth_url") or r.get("source_url") or r["authority"] != "unverified":
                err(f"{a}: not_checked row carries a value; must be blank/unverified")
        else:
            err(f"{a}: unknown check state {r['check']!r}")
        if r["authority"] == "publisher_labels_unofficial":
            unofficial += 1
        if r["authority"] == "official_club_labelled":
            official += 1

    gate = census["gate"]
    expected = {
        "clubs_checked": checked,
        "clubs_html_text": html_text,
        "clubs_publisher_labels_unofficial": unofficial,
        "clubs_verified_official": official,
    }
    for k, v in expected.items():
        if gate.get(k) != v:
            err(f"gate.{k} is {gate.get(k)!r} but rows give {v}")
    open_ = official == 32
    if (gate["status"] == "open") != open_:
        err("gate.status disagrees with the rows")
    if gate["status"] != ("open" if open_ else "closed"):
        err("gate must be 'closed' until all 32 clubs are verified official")

    # Slot model: rules present, store valid if populated.
    rule_ids = {r["id"] for r in model["rules"]}
    for needed in ["DS-1", "DS-2", "DS-3", "DS-4", "DS-5", "DS-7", "DS-8"]:
        if needed not in rule_ids:
            err(f"slot model missing rule {needed}")
    slots = model["store"]["slots"]
    for s in slots:
        sid = s.get("slot_id", "?")
        if s.get("club") not in CLUBS:
            err(f"slot {sid}: unknown club")
        if s.get("unit") not in UNITS:
            err(f"slot {sid}: unit must be one of {sorted(UNITS)}")
        if s.get("authority") not in AUTHORITY:
            err(f"slot {sid}: unknown authority")
        if s.get("authority") == "official_club_labelled" and s.get("club") not in abbrs:
            err(f"slot {sid}: no census row")
        if not str(s.get("source_url", "")).startswith("https://"):
            err(f"slot {sid}: no https source_url (DS-6)")
        players = s.get("players", [])
        if s.get("shared") and len(players) < 2:
            err(f"slot {sid}: shared=true needs 2+ players (DS-2)")
        if s.get("empty") and players:
            err(f"slot {sid}: empty=true but players present (DS-3)")
        if not s.get("empty") and not players:
            err(f"slot {sid}: no players and not marked empty (DS-3)")
        for p in players:
            if "raw_cell" not in p or "name" not in p:
                err(f"slot {sid}: player missing raw_cell/name (DS-5)")
            elif p["name"] != p["raw_cell"].lstrip("0123456789 ").strip() and p.get("jersey_number_stripped") is not None:
                err(f"slot {sid}: name is not raw_cell minus leading jersey number (DS-5)")

    # Flags must reference the route gate.
    if not any(f["id"] == "DF-1" for f in flags["flags"]):
        err("flags.json must carry DF-1 (route gate)")

    print(f"census: {len(rows)} clubs, {checked} checked, {html_text} HTML text, "
          f"{unofficial} labelled unofficial, {official} verified official")
    print(f"gate {gate['id']}: {gate['status']} ({official}/32 verified)")
    print(f"slot store: {len(slots)} rows")
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("PASS: depth census and slot model checks")


if __name__ == "__main__":
    main()
