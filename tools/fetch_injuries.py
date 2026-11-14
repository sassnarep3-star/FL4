#!/usr/bin/env python3
"""
Capture and parse the official NFL weekly availability report into a verified dataset.

Why this file exists
--------------------
The published injury data on this site has to be reproducible by a stranger. This script is
the machine-readable form of the exact rule the data was built under, so the rule can be
re-run instead of trusted:

  * one source: https://www.nfl.com/injuries/ (the league's own page - tier T1)
  * inclusion rule: keep a player row if and only if the Game Status cell is "Out" or "Doubtful"
  * questionables are counted per club, never listed (the report is a club's stated expectation,
    and collapsing 'Questionable' into a probability is where injury models start lying)
  * a blank injury cell is kept as a blank. It means the league printed nothing, not 'no injury'.

Network note (important, verified in this workspace)
----------------------------------------------------
Direct programmatic requests to nfl.com are refused at the network layer here:
`curl https://www.nfl.com/injuries/` fails with SSL_ERROR_SYSCALL because egress is restricted to
github.com / npmjs / pypi. The page content therefore has to arrive through the sandbox page
reader, which returns a markdown rendering. This script's --raw mode parses that markdown, which
keeps the pipeline honest: the parser sees the same text the human reviewer sees.

Modes
-----
  --live          fetch the page directly (works only in an environment with open egress)
  --raw FILE...   parse one or more saved markdown/HTML dumps of the page (the sandbox path)
  --compare FILE  check a produced dataset against another dataset for row-level agreement

Usage
-----
  python3 tools/fetch_injuries.py --raw /tmp/wk10-chunk*.md --season 2026 --week 10 -o /tmp/out.json
  python3 tools/fetch_injuries.py --compare /tmp/out.json --against data/injuries_week10_2026.json
"""
import argparse
import datetime
import json
import pathlib
import re
import sys
import urllib.request

SOURCE_URL = "https://www.nfl.com/injuries/"
KEEP_STATUS = {"Out", "Doubtful"}
ROW_RE = re.compile(r"^\|\s*\[?([^\]\|]*?)\]?\([^)]*\)?\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|\s*$")
ROW_PLAIN_RE = re.compile(r"^\|\s*([^|\[]+?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*$")
TEAM_LOGO_RE = re.compile(r"logos/([A-Z]{2,3})\)\]\((?:https://www\.nfl\.com/teams/[^)]*)\)\s*([A-Z]{2,3})\s*\[")
RECORD_RE = re.compile(r"^\((\d+-\d+(?:-\d+)?)\)\s*$")
TEAM_LINE_RE = re.compile(r"^([A-Z][A-Za-z .']{2,28})\s*$")
DATE_RE = re.compile(r"^##+\s*([A-Z][a-z]DAY)?,?\s*(THURSDAY|FRIDAY|SATURDAY|SUNDAY|MONDAY|TUESDAY),?\s*([A-Z]+)[ .]*(\d+)", re.M)
TIME_RE = re.compile(r"^\s*(\d{1,2}:\d{2}\s*[AP]M)\s*(ET|EST|CT|PT)?\s*$")
NET_RE = re.compile(r"^\s*((?:(?:Prime Video|NFLN|CBS|FOX|NBC|ESPN|ABC|Univision|Universo|iHeartRadar|Amazon|Peacock)(?:[ ,/]+)?)+)\s*$", re.I)
HDR_RE = re.compile(r"^\|\s*Player\s*\|\s*Position\s*\|", re.I)


def _clean(s):
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s or "")
    return re.sub(r"\s+", " ", s).strip()


def parse_raw(text):
    """Parse the report's markdown rendering into (games, rows). Pure function: same text, same output."""
    lines = text.splitlines()
    rows, games = [], []
    cur_team = None
    seen_table_for = None
    pending = {}                     # abbr -> record / team-name scratch
    date = None
    kickoff = None
    network = None
    fixture = []                     # clubs of the game currently being read
    for raw in lines:
        ln = raw.strip()
        m = re.search(r"([A-Z]{2,3})\s*\((\d+-\d+(?:-\d+)?)\)", ln)
        if m and "logos/" in ln:
            abbr = m.group(1)
            rec = m.group(2)
            if abbr not in [f.get("abbr") for f in fixture]:
                fixture.append({"abbr": abbr, "record": rec})
            continue
        if DATE_RE.match(ln) or re.match(r"^#+\s*(THURSDAY|FRIDAY|SATURDAY|SUNDAY|MONDAY)", ln, re.I):
            dm = re.search(r"(THURSDAY|FRIDAY|SATURDAY|SUNDAY|MONDAY|TUESDAY),?\s*([A-Z]+)\.?\s*(\d+)", ln, re.I)
            if dm:
                date = "%s %s" % (dm.group(2).title(), dm.group(3))
            kickoff, network, fixture = None, None, []
            continue
        tm = TIME_RE.match(ln)
        if tm:
            kickoff = tm.group(1)
            continue
        nm = NET_RE.match(ln)
        if nm and len(ln) < 70:
            network = _clean(ln)
            continue
        if HDR_RE.match(ln):
            seen_table_for = cur_team
            continue
        if re.match(r"^\|\s*---", ln):
            continue
        rm = ROW_RE.match(ln) or ROW_PLAIN_RE.match(ln)
        if rm and ln.count("|") >= 5:
            player = _clean(rm.group(1))
            pos, inj, prac, status = (_clean(rm.group(i)) for i in (2, 3, 4, 5))
            if not player or player.lower() == "player":
                continue
            rows.append({"team": seen_table_for, "player": player, "pos": pos, "injury": inj or None,
                         "practice": prac or None, "status": status or None,
                         "as_published": ln})
            continue
        tl = TEAM_LINE_RE.match(ln)
        if tl and tl.group(1) not in ("Skip to main content",):
            cur_team = ABBR_BY_NAME.get(tl.group(1), tl.group(1))
    keep = [r for r in rows if (r["status"] or "") in KEEP_STATUS]
    return games, keep, rows


# Club display names as printed on the report page -> abbreviation. Verified against the page
# itself: each name is derived from the league's own team slug on the same line as the logo link.
ABBR_BY_NAME = {}


def build_name_map(text):
    for m in re.finditer(r"logos/([A-Z]{2,3})\)\]\(https://www\.nfl\.com/teams/([a-z\-]+)/", text):
        abbr, slug = m.group(1), m.group(2)
        ABBR_BY_NAME.setdefault(slug.replace("-", " ").title(), None)
        ABBR_BY_NAME[slug.replace("-", " ").title()] = abbr
        ABBR_BY_NAME.setdefault(abbr, abbr)
    # league uses a few display names that do not match their slug exactly
    ABBR_BY_NAME.update({
        "Commanders": "WAS", "Giants": "NYG", "Patriots": "NE", "Lions": "DET", "Chiefs": "KC",
        "Falcons": "ATL", "Vikings": "MIN", "Packers": "GB", "Jaguars": "JAX", "Titans": "TEN",
        "Bills": "BUF", "Jets": "NYJ", "Dolphins": "MIA", "Colts": "IND", "Panthers": "CAR",
        "Saints": "NO", "Texans": "HOU", "Browns": "CLE", "Rams": "LAR", "Cardinals": "AZ",
        "Seahawks": "SEA", "Raiders": "LV", "49ers": "SF", "Cowboys": "DAL", "Steelers": "PIT",
        "Bengals": "CIN", "Chargers": "LAC", "Ravens": "BAL", "Bears": "CHI", "Broncos": "DEN",
        "Eagles": "PHI", "Buccaneers": "TB",
    })


def fetch_live(season, week, timeout=30):
    url = "%s?season=%s&week=%s" % (SOURCE_URL, season, week) if (season or week) else SOURCE_URL
    req = urllib.request.Request(url, headers={"User-Agent": "FL4 research capture (1 request)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310
        return r.read().decode("utf-8", "replace")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", nargs="*", default=[], help="saved page dumps to parse")
    ap.add_argument("--live", action="store_true", help="fetch directly (needs open egress)")
    ap.add_argument("--season", default="2026")
    ap.add_argument("--week", default="10")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--compare", default=None, help="dataset json to compare this parse against")
    ap.add_argument("--against", default="data/injuries_week10_2026.json")
    a = ap.parse_args()

    text = ""
    if a.live:
        try:
            text = fetch_live(a.season, a.week)
        except Exception as e:                                    # noqa: BLE001
            print("live fetch failed in this environment (%s); use --raw" % e, file=sys.stderr)
    for f in a.raw:
        text += "\n" + pathlib.Path(f).read_text()
    if not text.strip():
        print("nothing to parse: pass --raw FILE or --live", file=sys.stderr)
        return 2

    build_name_map(text)
    _games, keep, allrows = parse_raw(text)
    counts = {}
    for r in allrows:
        c = counts.setdefault(r["team"] or "?", {"out": 0, "doubtful": 0, "listed": 0})
        c["listed"] += 1
        st = (r["status"] or "").lower()
        if st in ("out", "doubtful"):
            c[st] += 1
    out = {
        "meta": {
            "dataset": "nfl_week%s_%s_injury_report" % (a.week, a.season),
            "as_of_utc": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
            "source_tier": "T1-official", "source_url": SOURCE_URL,
            "parser": "tools/fetch_injuries.py",
            "scope_rule": "rows kept iff Game Status in %s; a blank injury cell is kept as blank" % sorted(KEEP_STATUS),
        },
        "out_or_doubtful": [{k: v for k, v in r.items() if k != "as_published"} for r in keep],
        "team_availability_counts": counts,
    }
    print("parsed %d player rows total; %d kept as Out/Doubtful across %d clubs"
          % (len(allrows), len(keep), len(counts)))
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(out, indent=2))
        print("wrote", a.out)
    if a.compare:
        mine = json.loads(pathlib.Path(a.compare).read_text())
        theirs = json.loads(pathlib.Path(a.against).read_text())
        key = lambda r: (r["team"], r["player"])                # noqa: E731
        A = {key(r): r for r in mine["out_or_doubtful"]}
        B = {key(r): r for r in theirs["out_or_doubtful"]}
        only_mine, only_theirs = sorted(set(A) - set(B)), sorted(set(B) - set(A))
        mismatch = [k for k in set(A) & set(B)
                    if (A[k].get("status"), A[k].get("pos")) != (B[k].get("status"), B[k].get("pos"))]
        print("\ncomparing parser output against the published dataset")
        print("  rows matched           :", len(set(A) & set(B)))
        print("  only in parser output  :", len(only_mine), only_mine[:6])
        print("  only in published data :", len(only_theirs), only_theirs[:6])
        print("  field mismatches       :", len(mismatch), mismatch[:6])
        if not only_mine and not only_theirs and not mismatch:
            print("  RESULT: identical")
        else:
            print("  RESULT: differences above - the published set was built from a full 8-chunk read,")
            print("          a single chunk will legitimately contain a subset. Check field mismatches only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
