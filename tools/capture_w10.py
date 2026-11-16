#!/usr/bin/env python3
"""Validate the PRIVATE row-level Week 10 2026 injury transcription and derive PUBLIC aggregates.

Private raw layer (git-ignored): private/captures/nfl_injuries_w10_2026_reg10.psv
Public derived layer (committed): data/capture_summary_w10_2026.json  (counts only, no player names)

The script fails (exit 1) on any schema problem, so a missing field cannot publish as a blank.
Run:  python3 tools/capture_w10.py           # validate + write public summary
      python3 tools/capture_w10.py --check   # validate only (CI-safe when private/ is absent: exits 0 with a SKIP note)
"""
import hashlib
import json
import pathlib
import sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "private" / "captures" / "nfl_injuries_w10_2026_reg10.psv"
OUT = ROOT / "data" / "capture_summary_w10_2026.json"
SOURCE_URL = "https://www.nfl.com/injuries/league/2026/reg10"

PRACTICE_OK = {
    "Full Participation in Practice",
    "Limited Participation in Practice",
    "Did Not Participate In Practice",
    "",
}
GAME_OK = {"Out", "Doubtful", "Questionable", ""}

# Expected shape declared before the check ran (from the official page: 14 games, 28 clubs).
EXPECTED_GAMES = 14
EXPECTED_TEAMS = 28
EXPECTED_BYE_TEAMS = 4  # 32 - 28


def load(path):
    rows, errors = [], []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) != 7:
            errors.append(f"line {n}: expected 7 fields, got {len(parts)}")
            continue
        game, team, player, pos, injury, practice, status = parts
        if not player.strip() or not pos.strip() or not team.strip():
            errors.append(f"line {n}: blank player/team/position")
        if practice not in PRACTICE_OK:
            errors.append(f"line {n}: unexpected practice status {practice!r}")
        if status not in GAME_OK:
            errors.append(f"line {n}: unexpected game status {status!r}")
        rows.append(dict(line=n, game=game, team=team, player=player, pos=pos,
                         injury=injury, practice=practice, status=status))
    return rows, errors


LEGACY = ROOT / "data" / "injuries_w10_2026.json"   # earlier public table, captured 2026-11-14 (superseded; see Flagged F-R2)


def delta_vs_earlier_table(rows):
    """Counts only. Compares the 2026-11-16 transcription with the earlier 2026-11-14 public table.
    Club codes: the earlier table uses ARI for the Cardinals; the official page uses AZ."""
    legacy = json.loads(LEGACY.read_text(encoding="utf-8"))["rows"]
    norm = lambda t: "AZ" if t == "ARI" else t
    old = {(norm(r["team"]), r["player"]): r for r in legacy}
    cur = {(r["team"], r["player"]): r for r in rows}
    desig_now = {k for k, r in cur.items() if r["status"]}
    added = sorted(k for k in desig_now if k not in old)
    removed_or_undesignated = sorted(k for k in old if k in cur and not cur[k]["status"])
    status_changed = sorted(k for k in old if k in cur and cur[k]["status"] and old[k]["game_status"] != cur[k]["status"])
    added_clubs = sorted({t for t, _ in added})
    clubs_absent_from_earlier = sorted({t for t in {r["team"] for r in rows} if not any(norm(r["team"]) == t for r in legacy)})
    cnt = lambda rs, st: sum(1 for r in rs if r["game_status"] == st)
    return {
        "earlier_table_rows": len(legacy),
        "earlier_out": cnt(legacy, "Out"),
        "earlier_doubtful": cnt(legacy, "Doubtful"),
        "earlier_questionable": cnt(legacy, "Questionable"),
        "rows_designated_now_not_in_earlier_table": len(added),
        "clubs_with_no_section_in_earlier_table": clubs_absent_from_earlier,
        "rows_added_clubs": added_clubs,
        "earlier_rows_no_longer_designated": len(removed_or_undesignated),
        "earlier_rows_status_changed": len(status_changed),
        "reading": ("Most of the difference is coverage, not change: the earlier table has no section for the clubs "
                    "listed above (both play on Monday 16 Nov). One earlier designation no longer appears as designated "
                    "on the 16 Nov page. Changes are counted, not named, on the public layer."),
    }


def main():
    check_only = "--check" in sys.argv
    if not RAW.exists():
        print("SKIP: private raw layer absent (expected in CI). Nothing validated; no public output written.")
        return 0

    rows, errors = load(RAW)
    games = sorted({r["game"] for r in rows})
    teams = sorted({r["team"] for r in rows})
    by_team = defaultdict(list)
    for r in rows:
        by_team[r["team"]].append(r)

    # Structural expectations declared up front (fail closed on a mismatch).
    if len(games) != EXPECTED_GAMES:
        errors.append(f"expected {EXPECTED_GAMES} games, found {len(games)}")
    if len(teams) != EXPECTED_TEAMS:
        errors.append(f"expected {EXPECTED_TEAMS} clubs with sections, found {len(teams)}")
    dup = Counter((r["team"], r["player"]) for r in rows)
    for (t, p), c in dup.items():
        if c > 1:
            errors.append(f"duplicate player row: {t} {p} x{c}")

    if errors:
        print("FAIL: capture validation")
        for e in errors:
            print("  -", e)
        return 1

    sha = hashlib.sha256(RAW.read_bytes()).hexdigest()
    per_team = {}
    for t in teams:
        rs = by_team[t]
        per_team[t] = {
            "rows_listed": len(rs),
            "game_status_out": sum(1 for r in rs if r["status"] == "Out"),
            "game_status_doubtful": sum(1 for r in rs if r["status"] == "Doubtful"),
            "game_status_questionable": sum(1 for r in rs if r["status"] == "Questionable"),
            "injury_text_rows": sum(1 for r in rs if r["injury"]),
            "no_injury_no_status_rows": sum(1 for r in rs if not r["injury"] and not r["status"]),
        }

    totals = {k: sum(v[k] for v in per_team.values()) for k in next(iter(per_team.values()))}
    # Sections in which no player carries any injury text or game status.
    sections_no_designation = sorted(t for t, v in per_team.items()
                                     if v["injury_text_rows"] == 0 and v["game_status_out"] + v["game_status_doubtful"] + v["game_status_questionable"] == 0)

    # Per-game counts (public: aggregates only).
    per_game = {}
    for g in games:
        rs = [r for r in rows if r["game"] == g]
        per_game[g] = {
            "rows_listed": len(rs),
            "flagged": sum(1 for r in rs if r["injury"] or r["status"]),
            "out": sum(1 for r in rs if r["status"] == "Out"),
            "doubtful": sum(1 for r in rs if r["status"] == "Doubtful"),
            "questionable": sum(1 for r in rs if r["status"] == "Questionable"),
        }

    delta = delta_vs_earlier_table(rows)

    summary = {
        "as_of_utc": "2026-11-16T01:32:00Z",
        "season": 2026,
        "week": 10,
        "source_url": SOURCE_URL,
        "source_title": "Official NFL Injury Report for Players - Week 10 of the 2026 Season | NFL.com",
        "capture_method": "fetch_page tool, chunks 0-7 of 8 read 2026-11-16; transcribed row by row into a private, git-ignored file. Raw fetch bytes were not retained (the tool returns processed markdown), so the hash below is of the transcription, not of the page.",
        "private_file_sha256": sha,
        "games": len(games),
        "clubs_with_sections": len(teams),
        "clubs_without_section": EXPECTED_BYE_TEAMS,
        "player_rows_total": totals["rows_listed"],
        "game_status_out": totals["game_status_out"],
        "game_status_doubtful": totals["game_status_doubtful"],
        "game_status_questionable": totals["game_status_questionable"],
        "rows_with_injury_text": totals["injury_text_rows"],
        "rows_with_no_injury_and_no_status": totals["no_injury_no_status_rows"],
        "sections_with_no_injury_text_or_status": sections_no_designation,
        "rows_flagged_injury_text_or_status": sum(1 for r in rows if r["injury"] or r["status"]),
        "per_game": per_game,
        "per_club": per_team,
        "delta_vs_earlier_table_2026_11_14": delta,
        "publication_rule": "Public layer = aggregate counts and links only. Player names and row-level values stay in private/ (git-ignored) per the private/public split. Designation counts are reproducible from the official page at the source_url.",
    }
    if check_only:
        print(f"OK (check only): {len(rows)} rows, {len(games)} games, {len(teams)} clubs, sha256 {sha[:12]}")
        return 0
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: {len(rows)} rows, {len(games)} games, {len(teams)} clubs -> {OUT.relative_to(ROOT)}")
    print(f"    Out {totals['game_status_out']} | Doubtful {totals['game_status_doubtful']} | Questionable {totals['game_status_questionable']}")
    print(f"    sections with no injury text or status: {sections_no_designation or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
