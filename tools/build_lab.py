#!/usr/bin/env python3
"""Build the Decision Lab static section (lab/*.html) from data/lab/*.json.

Run from the repo root:  python3 tools/build_lab.py
                          python3 tools/build_lab.py --fail-on-warn

Rules enforced here (from the project brief and the session instructions):

  * Every table row carries a Source column. A row whose source cell has no
    official-host link is rendered UNVERIFIED and appended to the Flagged page.
  * Nothing is inferred. A value that could not be confirmed is rendered blank
    and flagged; the string "None" must never reach the page (checked below).
  * A column declared in a table must be carried by at least one row, and every
    rendered row must carry every declared column. Missing keys fail the build.
  * No performance number may be published. The builder counts and prints the
    number of price-derived values it rendered, and that number must be 0.
"""
import html
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "lab"
OUT = ROOT / "lab"
ASSETS = OUT / "assets"
AS_OF = "2026-11-16"

OFFICIAL_HOSTS = ("nfl.com", "nflgsis.com", "operations.nfl.com", "static.www.nfl.com",
                  "github.com", "sassnarep3-star.github.io", "weather.gov",
                  "nist.gov", "scikit-learn.org")

REPO = "https://github.com/sassnarep3-star/FL4"
BRANCH = "arena/61ebd543-fl4"

NAV = [
    ("Lab home", "index.html"),
    ("Decision readiness", "index.html#readiness"),
    ("Results feed", "results.html"),
    ("Availability", "availability.html"),
    ("Depth & deficiency", "depth.html"),
    ("Models", "models.html"),
    ("Leaderboard", "leaderboard.html"),
    ("Correlations", "correlations.html"),
    ("Price policy", "price-policy.html"),
    ("Fixtures", "fixtures.html"),
    ("Questions", "questions.html"),
    ("Suggestions", "suggestions.html"),
    ("Repo review", "repo-review.html"),
    ("Sources", "sources.html"),
    ("Flagged for Review", "flagged.html"),
]

AUTO_FLAGS = []
URL_RE = re.compile(r"https?://[^\s;,\)\]]+")
# A performance NUMBER is a price-derived token with a numeric value attached. A bare column
# name (the leaderboard lists roi and stake_size as display-only columns) is not a value.
PRICE_RE = re.compile(r"\b(american_price|closing_line_value|clv|roi|stake_size|edge_value)\b[^<>{}\n]{0,12}?[-+]?\d")


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def esc(v):
    return html.escape("" if v is None else str(v), quote=True)


def host_kind(url):
    host = (urlparse(url).hostname or "")
    return "official" if any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS) else "secondary"


def source_cell(text, page, row_id, flag_if_missing=True):
    """Render a source cell from a URL-bearing string. Empty -> blank + flagged."""
    text = "" if text is None else str(text)
    urls = [u.rstrip(".") for u in URL_RE.findall(text)]
    if not urls:
        if flag_if_missing:
            AUTO_FLAGS.append((page, row_id, "No source link", text))
        return '<span class="badge unverified">UNVERIFIED &mdash; no source</span>'
    parts = []
    official = False
    for url in urls:
        kind = host_kind(url)
        official = official or kind == "official"
        cls = "official" if kind == "official" else "secondary"
        label = (urlparse(url).hostname or url).replace("www.", "")
        parts.append(f'<a class="badge {cls}" href="{esc(url)}" target="_blank" rel="noopener">{esc(label)} ({kind})</a>')
    if not official and flag_if_missing:
        AUTO_FLAGS.append((page, row_id, "Secondary source only", text))
        parts.append('<span class="badge unverified">needs official check</span>')
    return " ".join(parts)


def blank(reason=""):
    """Render an intentionally empty value. Never a dash, never 'None', never 0."""
    r = f' title="{esc(reason)}"' if reason else ""
    return f'<span class="blank"{r}></span>'


def table(cols, rows, tid, filterable=False, selects=None, search_ph="Search table…"):
    """cols: [(header, key)] where key is a dict key or a callable returning HTML.

    A callable result, or a key starting with '_', is emitted raw; everything
    else is escaped. Fails the build if a declared key is absent from every row.
    """
    present = {k: False for _, k in cols if not callable(k)}
    for r in rows:
        for _, k in cols:
            if not callable(k) and k in r and r[k] not in (None, ""):
                present[k] = True
    dead = [k for k, ok in present.items() if not ok]
    if dead:
        raise SystemExit(f"FATAL [{tid}]: column(s) no row carries: {dead}")

    head = "".join(f"<th>{esc(h)}</th>" for h, _ in cols)
    body = []
    for r in rows:
        cells = []
        for _, k in cols:
            v = k(r) if callable(k) else r.get(k, "")
            raw = callable(k) or str(k).startswith("_")
            cells.append(f"<td>{v if raw else esc(v)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    filt = ""
    if filterable:
        opts = "".join(
            f'<select data-filter="{tid}" data-col="{esc(name)}" aria-label="Filter {esc(name)}">'
            f'<option value="">All {esc(name).lower()}</option>'
            + "".join(f'<option>{esc(v)}</option>' for v in vals) + "</select>"
            for name, vals in (selects or []))
        filt = (f'<div class="filters"><input type="search" data-filter="{tid}" '
                f'placeholder="{esc(search_ph)}" aria-label="Search table">{opts}</div>')
    return (f'{filt}<div class="table-wrap"><table id="{tid}"><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def rows_from(doc, key="rows"):
    cols = doc["columns"]
    return [dict(zip(cols, r)) for r in doc[key]]


def json_block(obj):
    return f'<pre class="json">{esc(json.dumps(obj, indent=1))}</pre>'


def callout(text, kind="info"):
    return f'<div class="callout {kind}">{text}</div>'


def kpi(value, label, note=""):
    return (f'<div class="kpi"><div class="kpi-v">{esc(value)}</div>'
            f'<div class="kpi-l">{esc(label)}</div><div class="kpi-n">{esc(note)}</div></div>')


def page(title, body, active, lead=""):
    nav = "".join(
        f'<a href="{esc(href)}" class="{"active" if href == active else ""}">{esc(label)}</a>'
        for label, href in NAV)
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | NFL Decision Lab</title>
<link rel="stylesheet" href="assets/style.css">
</head><body>
<header class="top">
  <div class="brand"><a href="index.html">NFL Decision Lab</a><span>Data as of {AS_OF}</span></div>
  <nav>{nav}</nav>
</header>
<main>
<h1>{esc(title)}</h1>
{lead_html}
{body}
</main>
<footer>
<p>Informational research only. Nothing here is betting advice. No market price exists in this
environment, so this section publishes no odds, no edge, no closing-line value and no return number.
Every row links to a source; values that could not be confirmed are left blank and listed on the
<a href="flagged.html">Flagged for Review</a> page.</p>
<p>Other sections of this repository: <a href="../index.html">Dashboard</a> &middot;
<a href="../decision-lab.html">Decision Lab blueprint</a> &middot;
<a href="../signals/index.html">Signals &amp; origination</a>.</p>
<p>Source repository: <a href="{REPO}">{esc(REPO)}</a>. Commit hashes cited are those present in
this checkout at review time.</p>
</footer>
<script src="assets/app.js"></script>
</body></html>
"""


# --------------------------------------------------------------------------
# load datasets
# --------------------------------------------------------------------------
RESULTS = load("results_2026.json")
INJ = load("injuries_week10_2026.json")
FIX = load("fixtures_week10_2026.json")
REQS = load("requirements.json")
QDOC = load("questions.json")
SGDOC = load("suggestions.json")
SRCDOC = load("sources.json")
FLAGDOC = load("flagged.json")
MODELS = load("models.json")
BOARD = load("leaderboard.json")
CORR = load("correlations.json")
DEPTH = load("depth.json")
POLICY = load("price_policy.json")
REVIEW = load("repo_review.json")

GAMES = RESULTS["games"]
FINAL = [g for g in GAMES if g["status"] == "FINAL"]
NOTFINAL = [g for g in GAMES if g["status"] != "FINAL"]
INJ_ROWS = INJ["rows"]
REQ_ROWS = rows_from(REQS)
Q_ROWS = rows_from(QDOC)
SG_ROWS = rows_from(SGDOC)
FL_ROWS = rows_from(FLAGDOC)
SRC_ROWS = SRCDOC["sources"]

STATUS_COUNT = Counter(r["status"] for r in REQ_ROWS)
GATES = sorted({r["blocking_gate"] for r in REQ_ROWS
                if r["blocking_gate"] and not r["blocking_gate"].lower().startswith("none")})
BLOCKED_GATES = sorted({r["blocking_gate"] for r in REQ_ROWS if r["status"] == "blocked"
                        and r["blocking_gate"] and not r["blocking_gate"].lower().startswith("none")})

PAGES = {}


# --------------------------------------------------------------------------
# index.html - landing page with the decision-readiness table
# --------------------------------------------------------------------------
def build_index():
    met = STATUS_COUNT["met"] + STATUS_COUNT["met at merge"]
    partial = STATUS_COUNT["partial"]
    blocked = STATUS_COUNT["blocked"]
    kpis = "".join([
        kpi(len(FINAL), "FINAL games captured",
            "2026 weeks 1-10, each linked to its official game centre"),
        kpi(len(INJ_ROWS), "injury-report rows",
            f'{INJ["week"] and "week " + str(INJ["week"])} across '
            f'{len({r["club"] for r in INJ_ROWS})} clubs'),
        kpi(sum(1 for r in INJ_ROWS if r["game_status"] in ("Out", "Doubtful")),
            "Out or Doubtful", "the only statuses the report defines as unlikely to play"),
        kpi(f'{met}/{len(REQ_ROWS)}', "requirements met",
            f'{partial} partial, {blocked} blocked, each with a named gate'),
        kpi(len(BLOCKED_GATES), "blocking gates open",
            "every one is a question with an owner decision, not a technical task"),
        kpi("0", "performance numbers published",
            "no price exists, so no edge, CLV or return is shown anywhere"),
    ])

    luck_rows = [
        {"test": "Benchmark-relative Brier skill score", "value": None,
         "needs": "settled forecasts with a benchmark", "status": "blocked by Q-PRICE-01"},
        {"test": "Beat the random-picks control (CTL-RAND)", "value": None,
         "needs": "one scored window", "status": "blocked by Q-PRICE-01"},
        {"test": "Beat the favourites-only control (CTL-FAV)", "value": None,
         "needs": "a market line for every bet", "status": "blocked by Q-PRICE-01"},
        {"test": "Game-cluster lower bound above zero", "value": None,
         "needs": "enough distinct games to cluster", "status": "not computable"},
        {"test": "Multiplicity adjustment across variants tried", "value": None,
         "needs": "a journal of all variants, including failures", "status": "no variants yet"},
        {"test": "Input-perturbation robustness", "value": None,
         "needs": "a fitted model to perturb", "status": "blocked by Q-MODEL-03"},
        {"test": "Prospective closing-line value", "value": None,
         "needs": "stored opening and closing prices", "status": "blocked by Q-PRICE-01"},
        {"test": "Calibration on the trailing window", "value": None,
         "needs": "forecast/outcome pairs over time", "status": "not computable"},
    ]
    luck_tbl = table(
        [("Test", "test"),
         ("Value", lambda r: blank(r["status"]) if r["value"] is None else esc(r["value"])),
         ("What it needs", "needs"),
         ("Why it is blank", "status"),
         ("Source", lambda r: source_cell(
             "https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html",
             "index", "luck-" + r["test"]))],
        luck_rows, "luck", filterable=True)

    readiness = []
    for r in REQ_ROWS:
        cls = {"met": "met", "met at merge": "met", "partial": "partial", "blocked": "blocked"}[r["status"]]
        readiness.append({
            "id": r["id"], "group": r["group"], "req": r["requirement"],
            "_status": f'<span class="badge {cls}">{esc(r["status"])}</span>',
            "_where": (f'<a href="{esc(r["where_published"][4:])}">{esc(r["where_published"])}</a>'
                       if r["where_published"].startswith("lab/") else esc(r["where_published"])),
            "_gate": (esc(r["blocking_gate"]) if r["blocking_gate"].lower().startswith("none")
                      else f'<a class="badge gate" href="questions.html">{esc(r["blocking_gate"])}</a>'),
            "clears": r["number_that_clears_it"],
            "evidence": r["evidence"],
        })
    ready_tbl = table(
        [("#", "id"), ("Group", "group"), ("Requirement", "req"), ("Status", "_status"),
         ("Where published", "_where"), ("Blocking gate", "_gate"),
         ("Number that clears it", "clears"), ("Evidence / current state", "evidence")],
        readiness, "readiness", filterable=True,
        selects=[("Status", ["met", "met at merge", "partial", "blocked"]),
                 ("Group", sorted({r["group"] for r in REQ_ROWS}))],
        search_ph="Search requirement, gate, evidence…")

    body = f"""
{callout("This section is one answer to a question the brief keeps asking: <strong>what can we actually decide today, and what are we pretending to decide?</strong> "
         "Everything below is published whether or not it flatters the project. Where a value could not be confirmed from an official source it is blank, and "
         'the blank is listed on the <a href="flagged.html">Flagged for Review</a> page with the reason and a link.', "warn")}
<h2>Executive summary &mdash; the important details</h2>
<ol class="summary">
<li><strong>The verified layer is complete for 2026 weeks 1&ndash;10.</strong> {len(FINAL)} FINAL games, each linked to its official
game centre, plus {len(INJ_ROWS)} rows of the official Week 10 injury report across 28 clubs and venue/stadium/Game&nbsp;Book links for
all 14 Week 10 fixtures. Every one of those rows carries a source link to nfl.com or operations.nfl.com.</li>
<li><strong>The performance layer is empty, and that is the finding rather than the gap.</strong> No odds, line, closing number or
book exists anywhere in this environment. Closing-line value, backtests, ROI, correlations of settled legs and originated residuals are
all specified and all unmeasurable. This site publishes no edge number, and the builder fails if one ever reaches a page.</li>
<li><strong>{len(BLOCKED_GATES)} blocking gates are open, and most of them are one question.</strong>
{PRICE_GATES} of the {len(BLOCKED_GATES)} are the same issue from different angles &mdash; where a price comes from, what the terms permit,
and what may be kept. They are decisions, not tasks, and each one has a named default if it is never answered.</li>
<li><strong>Depth is the largest unmet requirement.</strong> 0 of 32 clubs have a verified depth source, so 0 replacements are named
anywhere on this site and the Offense vs Defense Matchup Deficiency Matrix ships with every cell blank. It is published empty on
purpose: filling it from jersey number, experience or salary is explicitly rejected, and an empty grid makes the cost visible.</li>
<li><strong>Two rejections are recorded as standing rules, not preferences.</strong> Depth order is never derived from jersey number,
experience or salary, and strategies are never ranked by season-long ROI. Both are the fastest ways to fill a column and the most
reliable ways to be confidently wrong.</li>
<li><strong>The governance layer is published before there is anything to govern.</strong> The pre-registration schema, the two-stage
qualification, the control baselines, the demotion triggers and the anti-gaming rules all exist with thresholds deliberately unset, so
every gate fails closed. A threshold chosen after the first result is not a gate.</li>
<li><strong>Three things are known to be wrong and are published rather than fixed silently.</strong> Three captures of the same
official injury report disagree on row counts; the injury capture has one truncated row; and raw capture data currently sits in the
tree GitHub Pages publishes. All three are on the <a href="flagged.html">Flagged for Review</a> page with links.</li>
<li><strong>Nothing here is betting advice and no money is involved.</strong> Rewards are non-cash, no capital is exposed at any
stage, and the leaderboard can only score bets registered before the settlement they are scored against.</li>
</ol>

<h2>Where this stands</h2>
<div class="kpis">{kpis}</div>
<p>Read in one sentence: the descriptive layer is verified and complete for 2026 weeks 1&ndash;10, and the performance layer is empty
because there is no market price anywhere in this environment. Those two facts are not in tension &mdash; the second is why the first
is trustworthy. {PRICE_GATES} of the {len(BLOCKED_GATES)} blocking gates below are the same question asked from different angles:
<em>where does a price come from, and what are we allowed to keep?</em></p>

<h2 id="readiness">Decision readiness &mdash; one row per requirement</h2>
<p>Every requirement stated in the brief, in the order the brief states it, plus the meta-requirements from the session instructions
(M-71 onward). Status: <span class="badge met">met</span> published and checkable now;
<span class="badge partial">partial</span> the mechanism or schema exists but a named input is missing;
<span class="badge blocked">blocked</span> cannot be completed truthfully until a gate clears. A gate is not a task &mdash; it is a
question, and <a href="questions.html">each one has an owner decision attached</a>. Rows are requirements rather than external facts,
so their evidence cell cites the page or file that discharges them.</p>
{ready_tbl}

<h2>The tests a result will have to pass &mdash; published before any result exists</h2>
{callout("This panel is deliberately blank. It is published now, before any strategy has run, so that the tests cannot be chosen after "
         "seeing which ones pass. A test selected after the result is not a test, it is a story.", "info")}
{luck_tbl}

<h2>How this section differs from the others in this repository</h2>
<div class="table-wrap"><table>
<thead><tr><th>Section</th><th>What it is</th><th>Flag namespace</th><th>Link</th></tr></thead>
<tbody>
<tr><td>Dashboard</td><td>the original root site: injuries, strategies, requirements, repo review</td><td>F-*</td>
<td><a href="../index.html">../index.html</a></td></tr>
<tr><td>Decision Lab blueprint</td><td>the design blueprint with flags DL-F-01&hellip;DL-F-06</td><td>DL-F-*</td>
<td><a href="../decision-lab.html">../decision-lab.html</a></td></tr>
<tr><td>Signals &amp; origination</td><td>an independent signals section built by an earlier session</td><td>F-* (signals)</td>
<td><a href="../signals/index.html">../signals/index.html</a></td></tr>
<tr><td>Decision Lab (this section)</td><td>decision-first: what is verified, what is blocked, and by which gate</td><td>L-F-*</td>
<td><a href="index.html">lab/index.html</a></td></tr>
</tbody></table></div>
<p>The duplication is recorded as <a href="flagged.html">L-F-18</a> and <a href="repo-review.html">RV-1</a>. It is the cost of
parallel sessions working to non-overlapping file scopes, and the fix is an integration pass, not a deletion.</p>
"""
    return page("Decision readiness", body, "index.html",
                "What is verified, what is blocked, and the gate that blocks it. Nothing on this page is inferred.")


# --------------------------------------------------------------------------
# results.html
# --------------------------------------------------------------------------
def build_results():
    sp = RESULTS["meta"]
    split = MODELS["data_split"]
    rows = []
    for g in GAMES:
        fin = g["status"] == "FINAL"
        margin = g["home_margin"] if g["home_margin"] is not None else None
        rows.append({
            "week": g["week"], "date": g["date"],
            "away": g["away"], "away_points": g["away_points"] if fin else None,
            "home": g["home"], "home_points": g["home_points"] if fin else None,
            "_margin": esc(margin) if margin is not None else blank("no final score published"),
            "_total": esc(g["total_points"]) if g["total_points"] is not None else blank("no final score published"),
            "_status": f'<span class="badge {"met" if fin else "blocked"}">{esc(g["status"])}</span>',
            "note": g.get("note", ""),
            "intl": g.get("international_game_location") or "",
            "_src": source_cell(g["source_url"], "results", g["game_id"]),
        })
    wk = Counter(g["week"] for g in FINAL)
    week_rows = [{"week": w, "final": wk[w],
                  "not_final": sum(1 for g in GAMES if g["week"] == w and g["status"] != "FINAL"),
                  "games": sum(1 for g in GAMES if g["week"] == w),
                  "split": ("train" if w <= 5 else "validation" if w <= 8 else "holdout"),
                  "_src": source_cell("https://www.nfl.com/schedules/2026/by-week/week-%d" % w,
                                      "results", "week " + str(w))}
                 for w in sorted(wk)]
    bye_rows = [{"week": w, "clubs": ", ".join(c),
                 "_src": source_cell("https://www.nfl.com/schedules/2026/by-week/week-" + w,
                                     "results", "byes week " + w)}
                for w, c in sorted(RESULTS["meta"]["byes_published_by_week"].items(), key=lambda kv: int(kv[0]))]
    split_rows = [
        {"set": "train", "weeks": "1-5", "games": split["train_games"], "used_for": "fitting"},
        {"set": "validation", "weeks": "6-8", "games": split["validation_games"], "used_for": "model choice and gate runs"},
        {"set": "holdout", "weeks": "9-10", "games": split["holdout_games"], "used_for": "one use only"},
    ]
    intl = [g for g in GAMES if g.get("international_game_location")]

    body = f"""
{callout("Every row below was transcribed from the official NFL schedule page for that week. Only games the official page marks "
         "FINAL are recorded with scores. The two games that were not FINAL at capture are stored with blank scores and a per-row note "
         '&mdash; not with a zero, and not with a guess. Flagged as <a href="flagged.html">L-F-05</a>.', "info")}
<h2>At a glance</h2>
<div class="kpis">
{kpi(len(GAMES), "games in the feed", "2026 weeks 1-10")}
{kpi(len(FINAL), "FINAL", f'{sum(1 for g in FINAL if g["week"] <= 9)} in weeks 1-9 + '
     f'{sum(1 for g in FINAL if g["week"] == 10)} in week 10')}
{kpi(len(NOTFINAL), "not FINAL at capture", "scores left blank, flagged L-F-05")}
{kpi(len(intl), "international games", "transcribed from the official schedule page")}
{kpi(0, "rows with an inferred value", "a value that is not published is blank")}
</div>

<h2>Games</h2>
{table([("Wk", "week"), ("Date", "date"), ("Away", "away"), ("Away pts", "away_points"),
        ("Home", "home"), ("Home pts", "home_points"), ("Home margin", "_margin"), ("Total", "_total"),
        ("Status", "_status"), ("International venue", "intl"), ("Note", "note"), ("Source", "_src")],
       rows, "results", filterable=True,
       selects=[("Status", ["FINAL", "NOT FINAL AT CAPTURE"]),
                ("Week", [str(w) for w in sorted({g["week"] for g in GAMES})])],
       search_ph="Search club, date, note…")}

<h2>By week</h2>
{table([("Week", "week"), ("Games", "games"), ("FINAL", "final"), ("Not FINAL", "not_final"),
        ("Split", "split"), ("Source", "_src")], week_rows, "weeks")}

<h2>Data split</h2>
{callout(esc(split["limitation"]) + ' Flagged as <a href="flagged.html">L-F-15</a>.', "warn")}
{table([("Set", "set"), ("Weeks", "weeks"), ("Games", "games"), ("Used for", "used_for")], split_rows, "split")}
<p>Holdout discipline: {esc(MODELS["data_split"].get("holdout_discipline", ""))}</p>

<h2>Teams on bye, by week</h2>
{callout("The 'Teams on Bye' block on a completed week's schedule page shows each club's <strong>current</strong> record, not its "
         "record as of that week &mdash; Week 5's block lists CAR 4-5 and KC 7-2. It is therefore transcribed as club identities only. "
         'Flagged as <a href="flagged.html">L-F-09</a>.', "warn")}
{table([("Week", "week"), ("Clubs on bye", "clubs"), ("Source", "_src")], bye_rows, "byes")}
"""
    return page("Results feed", body, "results.html",
                "148 FINAL games, 2026 weeks 1-10, transcribed from the official NFL schedule pages and re-checked against the official game centres.")


# --------------------------------------------------------------------------
# availability.html
# --------------------------------------------------------------------------
def build_availability():
    inj_rows = []
    for r in INJ_ROWS:
        gs = r["game_status"] or ""
        cls = {"Out": "blocked", "Doubtful": "partial", "Questionable": "met"}.get(gs, "")
        inj_rows.append({
            "club": r["club"], "player": r["player"], "pos": r["position"],
            "injury": r["injury"] or "",
            "practice": r["practice_status"] or "",
            "_game": f'<span class="badge {cls}">{esc(gs)}</span>' if gs else blank("no game status published on the official report"),
            "_src": source_cell(r["report_url"], "availability", r["player"] + " (" + r["club"] + ")"),
        })
    gs_count = Counter(r["game_status"] or "(blank)" for r in INJ_ROWS)
    club_rows = []
    by_club = defaultdict(Counter)
    for r in INJ_ROWS:
        by_club[r["club"]][r["game_status"] or "(blank)"] += 1
    for club, c in sorted(by_club.items(), key=lambda kv: (-(kv[1]["Out"] + kv[1]["Doubtful"]), kv[0])):
        club_rows.append({
            "club": club, "rows": sum(c.values()), "out": c["Out"], "doubtful": c["Doubtful"],
            "questionable": c["Questionable"], "blank": c["(blank)"],
            "_src": source_cell(INJ["report_url"], "availability", "club " + club),
        })
    status_rows = [{"status": s or "(blank)", "count": n,
                    "meaning": {"Out": "the club has ruled the player out",
                                "Doubtful": "unlikely to play",
                                "Questionable": "uncertain",
                                "(blank)": "no game status published on the official report"}.get(s, ""),
                    "_src": source_cell(INJ["report_url"], "availability", "status " + (s or "blank"))}
                   for s, n in sorted(gs_count.items(), key=lambda kv: -kv[1])]
    diff_rows = [{"field": f, "_value": blank("requires two snapshots of the same player-week"),
                  "why": "The official report is a live document; a delta is only definable between two captures.",
                  "_src": source_cell("", "availability", "diff-" + f, flag_if_missing=False)}
                 for f in ("Designation change (Out -> Questionable)", "New appearance on the report",
                           "Removed from the report", "Practice upgrade", "Practice downgrade")]

    body = f"""
{callout("Captured " + esc(INJ["captured_at"]) + " from the official NFL injury report. "
         + esc(INJ["capture_rule"]), "info")}
{callout("<strong>Absence is not availability.</strong> A player on injured reserve produces no row on the weekly report at all, so "
         "&lsquo;no row&rsquo; is typed <em>unknown</em>, never <em>available</em>. Reading silence as health biases every feature in the "
         'same direction and leaves no trace in the table. Flagged as <a href="flagged.html">L-F-03</a>.', "warn")}
<h2>At a glance</h2>
<div class="kpis">
{kpi(len(INJ_ROWS), "rows captured", f'{len({r["club"] for r in INJ_ROWS})} clubs')}
{kpi(gs_count["Out"], "Out", "ruled out by the club")}
{kpi(gs_count["Doubtful"], "Doubtful", "unlikely to play")}
{kpi(gs_count["Questionable"], "Questionable", "uncertain")}
{kpi(gs_count["(blank)"], "no game status", "blank on the official report, not filled in")}
{kpi(0, "replacements named", "the official report has no depth field")}
</div>

<h2>By club &mdash; week 10</h2>
{table([("Club", "club"), ("Rows", "rows"), ("Out", "out"), ("Doubtful", "doubtful"),
        ("Questionable", "questionable"), ("No status", "blank"), ("Source", "_src")],
       club_rows, "clubs", filterable=True, search_ph="Search club…")}

<h2>Status distribution</h2>
{table([("Game status", "status"), ("Rows", "count"), ("Meaning", "meaning"), ("Source", "_src")],
       status_rows, "statuses")}

<h2>Every row</h2>
{table([("Club", "club"), ("Player", "player"), ("Pos", "pos"), ("Injury", "injury"),
        ("Practice status", "practice"), ("Game status", "_game"), ("Source", "_src")],
       inj_rows, "inj", filterable=True,
       selects=[("Game status", ["Out", "Doubtful", "Questionable"])],
       search_ph="Search player, club, injury…")}

<h2>Week-over-week movement</h2>
{callout("This table is intentionally empty. One capture exists, so every delta is undefined. The injury-as-surprise signal, the "
         "timestamped series and the point-in-time ledger all need at least two observations of the same player-week. "
         'Blocked by <a class="badge gate" href="questions.html">Q-SNAPSHOT-01</a>; see suggestion SG-02.', "warn")}
{table([("Field", "field"), ("Value", "_value"), ("Why it is blank", "why"), ("Source", "_src")],
       diff_rows, "diff")}

<h2>Fixtures covered by this report</h2>
<div class="table-wrap"><table><thead><tr><th>Away</th><th>Home</th><th>Kickoff (ET, on the report)</th><th>Network</th><th>Source</th></tr></thead><tbody>
{"".join(f'<tr><td>{esc(f["away"])}</td><td>{esc(f["home"])}</td><td>{esc(f.get("kickoff_local_on_report", ""))}</td><td>{esc(f.get("network", ""))}</td><td>{source_cell(INJ["report_url"], "availability", f["away"] + "@" + f["home"])}</td></tr>' for f in INJ["fixtures"])}
</tbody></table></div>
"""
    return page("Availability", body, "availability.html",
                "The official Week 10 2026 injury report, transcribed verbatim, plus the movement series that one capture cannot support.")


# --------------------------------------------------------------------------
# depth.html
# --------------------------------------------------------------------------
def build_depth():
    cov = DEPTH["coverage"]
    strings = ["1st string", "2nd string", "3rd string", "4th string"]
    matrix_rows = []
    for o in strings:
        row = {"off": o}
        for i, d in enumerate(strings):
            row["_c" + str(i)] = blank("no verified depth source (Q-DEPTH-01)")
        matrix_rows.append(row)
    slot_rows = [{"field": f, "value": v} for f, v in [
        ("Clubs with a verified depth source", f'{cov["clubs_with_a_verified_depth_source"]} of 32'),
        ("Depth register rows", str(cov["depth_register_rows"])),
        ("Replacements named on this site", str(cov["replacements_named_on_this_site"])),
        ("Snap counts captured", str(cov["snap_counts_captured"])),
        ("Games with Game Books parsed", str(cov["games_with_game_books_parsed"])),
    ]]
    rej_rows = [{"id": r["id"], "rejected": r["rejected"], "reason": r["reason"], "status": r["status"]}
                for r in DEPTH["rejections"]]
    fail_rows = [{"club": f["club"], "failure": f["failure"], "fix": f["proposed_fix"], "status": f["status"]}
                 for f in DEPTH["known_parse_failures"]]
    team_rows = [{"column": c["column"],
                  "_status": f'<span class="badge {"met" if c["status"] == "populated" else "blocked"}">{esc(c["status"])}</span>',
                  "reason": c.get("reason") or c.get("note") or ("populated from the official report (L-S01)" if c["status"] == "populated" else "")}
                 for c in DEPTH["per_team_view"]["columns"]]

    body = f"""
{callout(esc(cov["statement"]), "warn")}
<h2>Coverage</h2>
<div class="kpis">
{kpi(f'{cov["clubs_with_a_verified_depth_source"]}/32', "clubs with a verified depth source", "the gate behind most of this section")}
{kpi(cov["replacements_named_on_this_site"], "replacements named", "deliberately zero")}
{kpi(cov["snap_counts_captured"], "snap counts captured", "the starter proxy is specified but unused")}
{kpi(cov["games_with_game_books_parsed"], "Game Books parsed", "12 of 14 week 10 PDFs are linked and unparsed (L-F-11)")}
</div>
{table([("Field", "field"), ("Value", "value")], slot_rows, "coverage")}

<h2>Offense vs Defense Matchup Deficiency Matrix</h2>
{callout("The grid below is <strong>empty on purpose</strong>. It is published in its final shape so the cost of the depth gap is visible. "
         "Filling it from inferred depth would hide the single largest open risk in this project. Blocked by "
         '<a class="badge gate" href="questions.html">Q-DEPTH-01</a>. See <a href="suggestions.html">SG-03</a> and '
         '<a href="flagged.html">L-F-10</a>.', "warn")}
{table([("Offense / Defense", "off")] + [(s, "_c" + str(i)) for i, s in enumerate(strings)],
       matrix_rows, "matrix")}

<h2>Per-team decision view</h2>
{table([("Column", "column"), ("Status", "_status"), ("Note", "reason")], team_rows, "team")}

<h2>Standing rejections</h2>
{callout("These are recorded so the shortcut cannot be re-proposed during a schedule crunch. Depth order is never derived from jersey "
         "number, experience or salary &mdash; each is a proxy for something other than the club's current intent, and each is wrong in "
         "the direction that matters most.", "info")}
{table([("#", "id"), ("Rejected", "rejected"), ("Why", "reason"), ("Status", "status")], rej_rows, "rej")}

<h2>Slot model</h2>
<p>{esc(DEPTH["slot_model"]["rule"])} {esc(DEPTH["slot_model"]["why"])}</p>
<ul>
<li><strong>Shared slot</strong> &mdash; {esc(DEPTH["slot_model"]["shared_slot"])}</li>
<li><strong>Empty slot</strong> &mdash; {esc(DEPTH["slot_model"]["empty_slot"])}</li>
<li><strong>Raw string</strong> &mdash; {esc(DEPTH["slot_model"]["raw_string"])}</li>
</ul>

<h2>Known parse failures</h2>
{table([("Club", "club"), ("Failure", "failure"), ("Proposed fix", "fix"), ("Status", "status")],
       fail_rows, "fails")}

<h2>Snap-count proxy</h2>
<p>{esc(DEPTH["snap_count_proxy"]["rule"])} Source: <a href="{esc(DEPTH["snap_count_proxy"]["source"])}">{esc(DEPTH["snap_count_proxy"]["source"])}</a>
({esc(DEPTH["snap_count_proxy"]["source_id"])}). {esc(DEPTH["snap_count_proxy"]["source_note"])}</p>
<p>Threshold: {blank("must be set before the first transcription (Q-DEPTH-02)")} &mdash; {esc(DEPTH["snap_count_proxy"]["why_threshold_is_null"])}</p>

<h2>Staleness check</h2>
<p>{esc(DEPTH["staleness_check"]["rule"])} Status: {esc(DEPTH["staleness_check"]["status"])} {esc(DEPTH["staleness_check"]["why_it_matters"])}</p>

<h2>Announced-starter field</h2>
<p>{esc(DEPTH["announced_starter_field"]["rule"])} {esc(DEPTH["announced_starter_field"]["note"])} Rows populated: {esc(DEPTH["announced_starter_field"]["populated_rows"])}</p>
"""
    return page("Depth &amp; deficiency", body, "depth.html",
                "Who is officially unavailable, and why this site refuses to name who replaces them.")


# --------------------------------------------------------------------------
# models.html
# --------------------------------------------------------------------------
def build_models():
    oc = MODELS["output_contract"]
    rows = [{"field": f, "status": "required on every output row"} for f in oc["required_fields"]]
    rule_rows = [{"order": i + 1, "market": m} for i, m in enumerate(
        ["side", "total", "moneyline"])]
    tt_rows = [{"id": e["id"], "name": e["name"], "desc": e["description"], "status": e["status"]}
               for e in MODELS["total_estimators"]["estimators"]]
    ab_rows = [{"step": s} for s in MODELS["ablations"]["design"]]
    fc_rows = [{"field": f["field"], "source": f["source"], "status": f["status"],
                "_src": source_cell(MODELS["origination_order"].get("_src", "https://www.nfl.com/schedules/2026/by-week/week-10"),
                                    "models", "fixture-" + f["field"])}
               for f in MODELS["fixture_context_features"]["fields"]]
    reg_rows = [{"rule": r["rule"], "text": r["text"],
                 "_src": source_cell(r["source"], "models", "rule-" + r["rule"])}
                for r in MODELS["regime_priors"]["confirmed_official_basis"]]

    body = f"""
{callout("<strong>No model has been fitted.</strong> This page publishes the specification &mdash; the order markets are originated in, "
         "the output contract, the estimator design, the ablation protocol and the signal form &mdash; so that the specification exists "
         "before the first number does. Fitting before the split is frozen is how lookahead enters a backtest.", "warn")}

<h2>Origination order</h2>
<p>{esc(MODELS["origination_order"]["rule"])} <strong>Why:</strong> {esc(MODELS["origination_order"]["why"])}
Consequence if violated: {esc(MODELS["origination_order"]["consequence_if_violated"])}
Frozen: <span class="badge met">{esc(MODELS["origination_order"]["frozen"])}</span></p>
{table([("Order", "order"), ("Market", "market")], rule_rows, "order")}

<h2>Output contract</h2>
<p>{esc(oc["rule"])} {esc(oc["why_the_inputs_are_stored"])}</p>
{callout("<strong>Two-sided.</strong> " + esc(oc["two_sided_field"]), "info")}
{table([("Required field", "field"), ("Status", "status")], rows, "contract")}

<h2>Publication columns</h2>
<p>{esc(MODELS["publication_columns"]["rule"])} <strong>Why separate:</strong> {esc(MODELS["publication_columns"]["why_separate"])}</p>
<div class="table-wrap"><table><thead><tr>
{"".join(f"<th>{esc(c)}</th>" for c in MODELS["publication_columns"]["columns"])}
</tr></thead><tbody><tr>
{"".join(f"<td>{blank('no price and no model output exist')}</td>" for _ in MODELS["publication_columns"]["columns"])}
</tr></tbody></table></div>

<h2>Total estimators &mdash; both, until one wins</h2>
<p>{esc(MODELS["total_estimators"]["rule"])} {esc(MODELS["total_estimators"]["collapse_rule"])}</p>
{table([("#", "id"), ("Estimator", "name"), ("Description", "desc"), ("Status", "status")], tt_rows, "tot")}

<h2>Ablations, not fixed penalties</h2>
<p>{esc(MODELS["ablations"]["rule"])} {esc(MODELS["ablations"]["why_not_fixed_penalties"])} Status: {esc(MODELS["ablations"]["status"])}</p>
{table([("Step", "step")], ab_rows, "ab")}

<h2>Injury signal form</h2>
<p>{esc(MODELS["injury_signal_form"]["rule"])}</p>
<p>{esc(MODELS["injury_signal_form"]["definition"])}</p>
<p><strong>Why a level fails:</strong> {esc(MODELS["injury_signal_form"]["why_a_level_fails"])}</p>
<p>Status: {esc(MODELS["injury_signal_form"]["status"])}</p>

<h2>Fixture-context features</h2>
<p>{esc(MODELS["fixture_context_features"]["rule"])} <strong>Excluded:</strong> {esc(MODELS["fixture_context_features"]["excluded"])}</p>
{table([("Field", "field"), ("Source", "source"), ("Status", "status"), ("Source link", "_src")],
       fc_rows, "fx")}

<h2>2026 regime priors</h2>
{callout(esc(MODELS["regime_priors"]["rule"]) + " The regime change is confirmed from the official rulebook; the <em>rates</em> under it are "
         "not measured, so every prior is null rather than carried over from a season played under different rules. Flagged as "
         '<a href="flagged.html">L-F-15</a> and gated on <a class="badge gate" href="questions.html">Q-MODEL-04</a>.', "warn")}
{table([("Rule", "rule"), ("Official text", "text"), ("Source", "_src")], reg_rows, "reg")}
<p>Measured prior values: {blank("not yet measured from 2026 results")} &mdash; {esc(MODELS["regime_priors"]["why_null"])}</p>
<p>{esc(MODELS["regime_priors"]["measurement_plan"])}</p>

<h2>Weather</h2>
<p>{esc(MODELS["weather_features"]["rule"])} Roof status: <strong>{esc(MODELS["weather_features"]["roof_status"])}</strong>.
{esc(MODELS["weather_features"]["why_blank"])} Source: <a href="{esc(MODELS["weather_features"]["weather_source"])}">{esc(MODELS["weather_features"]["weather_source"])}</a>.
Values published: {esc(MODELS["weather_features"]["values_published"])}</p>

<h2>Data split</h2>
{callout(esc(MODELS["data_split"]["limitation"]) + ' Blocked by <a class="badge gate" href="questions.html">Q-MODEL-05</a>.', "warn")}
<p>{esc(MODELS["data_split"]["holdout_discipline"])}</p>
"""
    return page("Models", body, "models.html",
                "Specification only. Nothing has been fitted, so nothing here is a probability.")


# --------------------------------------------------------------------------
# leaderboard.html
# --------------------------------------------------------------------------
def build_leaderboard():
    div_rows = [{"id": d["id"], "name": d["name"], "eligible": d["eligible"],
                 "_rank": ('<span class="badge met">rankable</span>' if d["rankable_now"]
                           else f'<span class="badge blocked">closed &mdash; {esc(d.get("blocked_by", ""))}</span>'),
                 "entries": d["entries"]} for d in BOARD["divisions"]]
    s1 = [{"test": t} for t in BOARD["two_stage"]["stage_1"]["entry_tests"]]
    s2 = [{"test": t} for t in BOARD["two_stage"]["stage_2"]["entry_tests"]]
    ctl = [{"id": c["id"], "name": c["name"], "desc": c["description"], "purpose": c["purpose"]}
           for c in BOARD["control_baselines"]["controls"]]
    dem = [{"id": t["id"], "name": t["name"], "test": t["test"],
            "_thr": blank("must be set before the first live run (Q-GOV-02)") if t["threshold"] is None else esc(t["threshold"])}
           for t in BOARD["demotion_gate"]["triggers"]]
    ag = [{"id": a["id"], "rule": a["rule"], "enforced": a["enforced"]} for a in BOARD["anti_gaming"]]
    reg = [{"id": r["id"], "name": r["name"], "rule": r["rule_text"], "window": r["sample_window"],
            "gates": ", ".join(r["gates"]), "status": r["status"], "note": r.get("note", "")}
           for r in BOARD["pre_registration"]["registered"]]
    DEFER = callout("<strong>Deference:</strong> " + esc(BOARD['pre_registration']['canonical']) + ' Flagged as <a href="flagged.html">L-F-19</a>.', "info")
    tiers = [{"tier": t["tier"], "name": t["name"], "test": t["test"], "reward": t["reward"]}
             for t in BOARD["rewards"]["tiers"]]

    body = f"""
{callout(esc(BOARD["board_status"]), "warn")}
<div class="kpis">
{kpi(len(BOARD["divisions"]), "divisions", "1 open, 3 closed on the joint-evidence gate")}
{kpi(0, "registered strategies", "one shadow baseline is registered (B0)")}
{kpi(0, "settled bets", "no price, so nothing can be settled")}
{kpi(0, "backtest numbers", "backtest results can never appear on this board")}
</div>

<h2>Divisions</h2>
{table([("#", "id"), ("Division", "name"), ("Eligible", "eligible"), ("Rankable now", "_rank"), ("Entries", "entries")],
       div_rows, "divs")}

<h2>Joint-evidence gate &mdash; currently closed</h2>
<p>{esc(BOARD["joint_evidence_gate"]["rule"])}</p>
{callout("<strong>Prohibited:</strong> " + esc(BOARD["joint_evidence_gate"]["prohibited"]) + " " + esc(BOARD["joint_evidence_gate"]["why"]), "warn")}
<p>Status: {esc(BOARD["joint_evidence_gate"]["status"])}</p>

<h2>Ranking</h2>
<p>Rank key: <strong>{esc(BOARD["ranking"]["rank_key"])}</strong></p>
<ul>
<li><strong>Not win rate</strong> &mdash; {esc(BOARD["ranking"]["why_not_win_rate"])}</li>
<li><strong>Not ROI</strong> &mdash; {esc(BOARD["ranking"]["why_not_roi"])}</li>
<li><strong>Uncertainty</strong> &mdash; {esc(BOARD["ranking"]["uncertainty"])}</li>
<li><strong>Multiplicity</strong> &mdash; {esc(BOARD["ranking"]["multiplicity"])}</li>
</ul>
<p>Display-only columns, which cannot move the rank: {esc(", ".join(BOARD["ranking"]["display_only_columns"]))}.
{esc(BOARD["ranking"]["note_on_display_only"])}</p>

<h2>Signal vs staking</h2>
<p>{esc(BOARD["signal_vs_staking"]["rule"])} {esc(BOARD["signal_vs_staking"]["why"])} Enforcement: {esc(BOARD["signal_vs_staking"]["enforcement"])}</p>

<h2>Two-stage qualification</h2>
<h3>Stage 1 &mdash; {esc(BOARD["two_stage"]["stage_1"]["name"])}</h3>
<p>{esc(BOARD["two_stage"]["stage_1"]["purpose"])} Runnable without prices: <span class="badge met">{esc(BOARD["two_stage"]["stage_1"]["runnable_without_prices"])}</span></p>
{table([("Entry test", "test")], s1, "s1")}
<h3>Stage 2 &mdash; {esc(BOARD["two_stage"]["stage_2"]["name"])}</h3>
<p>{esc(BOARD["two_stage"]["stage_2"]["purpose"])} Runnable without prices: <span class="badge blocked">{esc(BOARD["two_stage"]["stage_2"]["runnable_without_prices"])}</span>
&mdash; blocked by <a class="badge gate" href="questions.html">{esc(BOARD["two_stage"]["stage_2"]["blocked_by"])}</a></p>
{table([("Entry test", "test")], s2, "s2")}

<h2>Control baselines</h2>
<p>{esc(BOARD["control_baselines"]["rule"])} {esc(BOARD["control_baselines"]["note"])}</p>
{table([("#", "id"), ("Control", "name"), ("What it is", "desc"), ("Purpose", "purpose")], ctl, "ctl")}

<h2>Demotion gate</h2>
<p>{esc(BOARD["demotion_gate"]["rule"])}</p>
{table([("#", "id"), ("Trigger", "name"), ("Test", "test"), ("Threshold", "_thr")], dem, "dem")}
<p>{esc(BOARD["demotion_gate"]["on_demotion"])}</p>

<h2>Pre-registration</h2>
<p>{esc(BOARD["pre_registration"]["rule"])} Required fields: {esc(", ".join(BOARD["pre_registration"]["required_fields"]))}</p>
{table([("#", "id"), ("Strategy", "name"), ("Rule", "rule"), ("Window", "window"), ("Gates", "gates"),
        ("Status", "status"), ("Note", "note")], reg, "reg") if reg else
 "<p>No strategy is registered except the shadow baseline B0, which is registered above.</p>"}
<p>{esc(BOARD["pre_registration"]["note"])}</p>
{DEFER}

<h2>Anti-gaming</h2>
{table([("#", "id"), ("Rule", "rule"), ("Enforced by", "enforced")], ag, "ag")}

<h2>Rewards</h2>
{callout(esc(BOARD["rewards"]["note"]), "info")}
{table([("Tier", "tier"), ("Name", "name"), ("Test", "test"), ("Reward", "reward")], tiers, "tiers")}
"""
    return page("Leaderboard", body, "leaderboard.html",
                "Empty by design. The board publishes the rules it will be judged by before there is anything to judge.")


# --------------------------------------------------------------------------
# correlations.html
# --------------------------------------------------------------------------
def build_correlations():
    pol = CORR["policy"]
    est = [{"id": e["id"], "name": e["name"], "use": e["use"], "formula": e["formula_note"],
            "_value": blank("no settled bets exist (Q-PRICE-01)")} for e in CORR["estimators"]]
    pairs = []
    for p in CORR["pairs"]:
        pairs.append({
            "id": p["id"], "a": p["leg_a"], "b": p["leg_b"],
            "same": "same game" if p["same_game"] else "different games",
            "why": p["why_it_matters"],
            "_n": esc(p["n"]),
            "_v": blank("not measured"),
            "_lo": blank("not measured"),
            "_hi": blank("not measured"),
            "status": p["status"],
        })
    plan = [{"step": s} for s in CORR["measurement_plan"]]

    body = f"""
{callout(esc(CORR["status"]), "warn")}
<h2>Policy</h2>
<p>{esc(pol["rule"])}</p>
<ul>
<li><strong>What counts as an official input</strong> &mdash; {esc(pol["what_counts_as_official_input"])}</li>
<li><strong>Why n is published</strong> &mdash; {esc(pol["why_n_is_published"])}</li>
<li><strong>Minimum n</strong> &mdash; {esc(pol["minimum_n"])} ({esc(pol["minimum_n_status"])})</li>
<li><strong>Clustering</strong> &mdash; {esc(pol["clustering"])}</li>
<li><strong>What a correlation is not</strong> &mdash; {esc(pol["what_a_correlation_is_not"])}</li>
</ul>

<h2>Estimators</h2>
{table([("#", "id"), ("Estimator", "name"), ("Use", "use"), ("Formula note", "formula"), ("Value", "_value")],
       est, "est")}

<h2>Pairs registered</h2>
{table([("#", "id"), ("Leg A", "a"), ("Leg B", "b"), ("Scope", "same"), ("Why it matters", "why"),
        ("n", "_n"), ("Phi", "_v"), ("Excess joint", "_lo"), ("Interval", "_hi"), ("Status", "status")],
       pairs, "pairs", filterable=True, search_ph="Search pair, leg, note…")}

<h2>Measurement plan</h2>
{table([("Step", "step")], plan, "plan")}
"""
    return page("Correlations", body, "correlations.html",
                "Eleven pairs registered, zero measured. The combo divisions stay closed until the joint evidence exists.")


# --------------------------------------------------------------------------
# price-policy.html
# --------------------------------------------------------------------------
def build_price_policy():
    lb = POLICY["legal_basis"]
    pol_rows = [{"id": p["id"], "name": p["name"], "effect": p["effect"], "unblocks": p["unblocks"],
                 "blocks": p["blocks"], "cost": p["cost"], "risk": p["risk"]}
                for p in POLICY["policy_options"]]
    spec = POLICY["snapshot_store_spec"]
    spec_rows = [{"field": k, "value": v if isinstance(v, str) else ", ".join(v)}
                 for k, v in spec.items() if k != "why_the_definitions_are_frozen_first"]
    steps = [{"step": s} for s in POLICY["vig_free_decomposition_spec"]["steps"]]
    drift = [{"parser": d["parser"], "pin": d["pin"], "status": d["status"]}
             for d in POLICY["drift_alarm_spec"]["applied_to"]]
    sched = POLICY["residual_publication_schedule"]

    body = f"""
{callout("This page exists because most of the brief is blocked behind one question. It states the legal basis verbatim, the policy "
         "options, the store specification and the publication schedule &mdash; all of which can be published before a single price "
         "exists, and none of which are useful if they are written after one arrives.", "info")}

<h2>Legal basis, quoted verbatim</h2>
<p>Source: <a href="{esc(lb["source"])}">{esc(lb["source"])}</a> (page states &ldquo;Updated: {esc(lb["page_updated"])}&rdquo;), registered as {esc(lb["source_id"])}.</p>
<blockquote>{esc(lb["quoted"])}</blockquote>
{callout("<strong>Not legal advice.</strong> " + esc(lb["not_stated"]), "warn")}
<h3>What this site does because of it</h3>
<ul>{"".join(f"<li>{esc(x)}</li>" for x in lb["what_this_site_does_because_of_it"])}</ul>

<h2>Policy options</h2>
{table([("#", "id"), ("Option", "name"), ("Effect", "effect"), ("Unblocks", "unblocks"),
        ("Blocks", "blocks"), ("Cost", "cost"), ("Risk", "risk")], pol_rows, "polopts")}
<p><strong>Current policy: {esc(POLICY["current_policy"])}</strong></p>
{callout(esc(POLICY["owner_decision_field"]), "warn")}

<h2>Price-snapshot store specification</h2>
<p>Purpose: {esc(spec["purpose"])}</p>
{table([("Field", "field"), ("Specification", "value")], spec_rows, "store")}
<p><strong>Why the definitions are frozen first:</strong> {esc(spec["why_the_definitions_are_frozen_first"])}</p>
<p>Status: {esc(spec["status"])}</p>

<h2>Vig-free decomposition</h2>
<p>{esc(POLICY["vig_free_decomposition_spec"]["purpose"])}</p>
{table([("Step", "step")], steps, "vig")}
<p><strong>What is not done:</strong> {esc(POLICY["vig_free_decomposition_spec"]["what_is_not_done"])}</p>
{callout("<strong>Failure mode guarded:</strong> " + esc(POLICY["vig_free_decomposition_spec"]["failure_mode_guarded"]), "info")}

<h2>Residual publication schedule</h2>
<p>{esc(sched["requirement"])}</p>
<p>{esc(sched["schedule_spec"])}</p>
<p>Status: {esc(sched["status"])}</p>
{callout("<strong>Day-one rule:</strong> " + esc(sched["day_one_rule"]), "warn")}

<h2>Drift alarm</h2>
<p>{esc(POLICY["drift_alarm_spec"]["rule"])}</p>
{table([("Parser", "parser"), ("Pin", "pin"), ("Status", "status")], drift, "drift")}
<p>{esc(POLICY["drift_alarm_spec"]["not_applied_to"])}</p>
"""
    return page("Price policy", body, "price-policy.html",
                "The legal basis, the policy options and the store specification &mdash; published before any price exists.")


# --------------------------------------------------------------------------
# fixtures.html
# --------------------------------------------------------------------------
def build_fixtures():
    venues = FIX["venues"]
    rows = []
    for gid, v in sorted(venues.items()):
        m = re.match(r"([a-z0-9]+)-at-([a-z0-9]+)-(\d{4})-reg-(\d+)", gid)
        rows.append({
            "gid": gid,
            "away": (m.group(1).upper() if m else "?"),
            "home": (m.group(2).upper() if m else "?"),
            "loc": v.get("location") or "",
            "stadium": v.get("stadium") or "",
            "_book": (f'<a class="badge official" href="{esc(v["game_book_url"])}" target="_blank" rel="noopener">Game Book PDF</a>'
                      if v.get("game_book_url") else blank("no Game Book published for this fixture yet")),
            "_src": source_cell("https://www.nfl.com/games/" + gid, "fixtures", gid),
        })
    nb = sum(1 for v in venues.values() if v.get("game_book_url"))
    body = f"""
{callout(esc(FIX["note"]), "info")}
{callout("<strong>Irregularity:</strong> " + esc(FIX["irregularity"]) + ' Flagged as <a href="flagged.html">L-F-08</a>.', "warn")}
<div class="kpis">
{kpi(len(venues), "week 10 fixtures", "venue and stadium transcribed from the official game centre")}
{kpi(nb, "with a Game Book PDF", "2 fixtures had not finished or not kicked off at capture")}
{kpi(0, "Game Books parsed", "links only; no starter, inactive or snap count is claimed")}
{kpi(0, "roof designations", "no official per-game roof source was located (L-F-07)")}
</div>
{table([("Game id", "gid"), ("Away", "away"), ("Home", "home"), ("Location", "loc"), ("Stadium", "stadium"),
        ("Game Book", "_book"), ("Game centre (source)", "_src")], rows, "fx", filterable=True,
       search_ph="Search club, city, stadium…")}
{callout("Game Book links are Cloudinary-signed and will expire. They are published as captured, not rewritten, and the expiry is a "
         'known liveness risk recorded on the <a href="flagged.html">Flagged for Review</a> page.', "warn")}
"""
    return page("Fixtures", body, "fixtures.html",
                "Venue, stadium and the official Game Book link for all 14 Week 10 fixtures, transcribed from the NFL game centre.")


# --------------------------------------------------------------------------
# questions.html
# --------------------------------------------------------------------------
def build_questions():
    rows = []
    for q in Q_ROWS:
        rows.append({
            "id": q["id"], "group": q["group"], "q": q["question"],
            "known": q["known"], "unknown": q["unknown"], "why": q["why_it_matters"],
            "route": q["resolution_route"], "options": q["options"],
            "_default": f'<span class="badge partial">default: {esc(q["default_if_unanswered"])}</span>',
            "_block": ('<span class="badge blocked">blocking</span>' if q["blocking"]
                       else '<span class="badge met">not blocking</span>'),
        })
    nb = sum(1 for q in Q_ROWS if q["blocking"])
    body = f"""
{callout(esc(QDOC["note"]), "info")}
<div class="kpis">
{kpi(len(Q_ROWS), "open questions", f'{nb} blocking, {len(Q_ROWS) - nb} not blocking')}
{kpi(len(GATES), "distinct gates", "named once and reused across the readiness table")}
{kpi(0, "answered on the owner's behalf", "a default is not an answer; it is what happens if no answer comes")}
</div>
{table([("#", "id"), ("Group", "group"), ("Question", "q"), ("What is already known", "known"),
        ("What is still unknown", "unknown"), ("Why it matters", "why"), ("Route to resolve", "route"),
        ("Options", "options"), ("If it is never answered", "_default"), ("Blocking", "_block")],
       rows, "qs", filterable=True,
       selects=[("Group", sorted({q["group"] for q in Q_ROWS})),
                ("Blocking", ["blocking", "not blocking"])],
       search_ph="Search question, gate, option…")}
"""
    return page("Questions", body, "questions.html",
                "What must be decided before any of this can produce a number, and what each one blocks.")


# --------------------------------------------------------------------------
# suggestions.html
# --------------------------------------------------------------------------
def build_suggestions():
    rows = []
    for s in SG_ROWS:
        cls = {"approved": "met", "proposed": "partial", "rejected": "blocked"}.get(s["status"].split(" ")[0], "partial")
        opts = [o for o in s["options"] if o]
        rows.append({
            "id": s["id"], "title": s["title"], "problem": s["problem"],
            "_opts": '<ol class="opts">' + "".join(
                f'<li><label><input type="radio" name="sg-{esc(s["id"])}" value="{esc(o.split(")")[0])}"> '
                f'{esc(o)}</label></li>' for o in opts) +
                f'<li><label><input type="radio" name="sg-{esc(s["id"])}" value="own"> '
                f'My own path:</label> <input type="text" class="own" data-sg="{esc(s["id"])}" '
                f'placeholder="write your own option" aria-label="Own option for {esc(s["id"])}"></li></ol>',
            "rec": s["recommended_path"], "depends": s["depends_on"], "effort": s["effort"], "risk": s["risk"],
            "_status": f'<span class="badge {cls}">{esc(s["status"])}</span>',
            "discovers": s["discovers"],
        })
    ap = sum(1 for s in SG_ROWS if s["status"].startswith("approved"))
    body = f"""
{callout(esc(SGDOC["note"]), "info")}
<h2>How to review this board</h2>
<ol class="workflow">{"".join(f"<li>{esc(x)}</li>" for x in SGDOC["review_workflow"])}</ol>
{callout("The selection controls below are stored in your browser only. They do not change any code, do not start a capture and are not "
         "sent anywhere. To make a choice binding, set <code>status</code> for that row in "
         "<code>data/lab/suggestions.json</code> and name the approver &mdash; that edit is the only thing that changes what the project does.", "warn")}
<div class="kpis">
{kpi(len(SG_ROWS), "suggestions", f'{ap} approved, {len(SG_ROWS) - ap} awaiting a decision')}
{kpi(sum(1 for s in SG_ROWS if s["risk"].startswith("high")), "carry high risk if reversed", "these are the rejections worth protecting")}
{kpi(0, "auto-approved by silence", "silence leaves a row proposed")}
</div>
<div class="actions">
<button type="button" id="save-all">Save my choice</button>
<button type="button" id="clear-all">Clear saved choices</button>
<button type="button" id="export-all">Copy my choices</button>
<span id="save-note" role="status"></span>
</div>
{table([("#", "id"), ("Suggestion", "title"), ("Problem", "problem"), ("Options - choose one", "_opts"),
        ("Recommended path", "rec"), ("Depends on", "depends"), ("Effort", "effort"), ("Risk", "risk"),
        ("Status", "_status"), ("What it discovers", "discovers")],
       rows, "sg", filterable=True,
       selects=[("Status", ["approved", "proposed", "rejected"])],
       search_ph="Search suggestion, problem, risk…")}
"""
    return page("Suggestions", body, "suggestions.html",
                "A decision board, not a work log. Nothing here is approved until you approve it; silence never approves.")


# --------------------------------------------------------------------------
# repo-review.html
# --------------------------------------------------------------------------
def build_repo_review():
    files = [{"path": f["path"], "bytes": f["bytes"], "lines": f["lines"],
              "_link": source_cell(f["link"], "repo-review", f["path"])}
             for f in REVIEW["files"]]
    find = [{"id": f["id"], "area": f["area"], "finding": f["finding"], "evidence": f["evidence"],
             "assessment": f["assessment"], "rec": f["recommended"],
             "_src": source_cell(f["link"], "repo-review", f["id"])}
            for f in REVIEW["findings"]]
    body = f"""
{callout(esc(REVIEW["method"]), "info")}
<div class="kpis">
{kpi(REVIEW["files_reviewed"], "files reviewed", "every tracked file was opened")}
{kpi(len(REVIEW["findings"]), "findings", "each linked to the file it came from")}
{kpi(REVIEW["origin_main_head_at_review"].split()[0], "main head at review", esc(REVIEW["origin_main_head_at_review"]))}
{kpi(REVIEW["branch_base_commit"].split()[0], "this branch's base", esc(REVIEW["branch_base_commit"]))}
</div>

<h2>Findings</h2>
{table([("#", "id"), ("Area", "area"), ("Finding", "finding"), ("Evidence", "evidence"),
        ("Assessment", "assessment"), ("Recommended", "rec"), ("Source", "_src")],
       find, "findings", filterable=True,
       selects=[("Area", sorted({f["area"] for f in REVIEW["findings"]}))],
       search_ph="Search finding, file, area…")}

<h2>Every file in the tree</h2>
{table([("Path", "path"), ("Bytes", "bytes"), ("Lines", "lines"), ("Source", "_link")],
       files, "files", filterable=True, search_ph="Search path…")}
"""
    return page("Repo review", body, "repo-review.html",
                "Line-by-line review of the working tree, with a review link for every file.")


# --------------------------------------------------------------------------
# sources.html
# --------------------------------------------------------------------------
def build_sources():
    rows = []
    for s in SRC_ROWS:
        cls = {"read": "met", "link-verified-only": "partial", "not-read": "blocked",
               "not-read-this-session": "blocked"}.get(s["status"], "partial")
        rows.append({
            "id": s["id"], "name": s["name"],
            "_url": source_cell(s["url"], "sources", s["id"]) + f' <a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["url"])}</a>',
            "_status": f'<span class="badge {cls}">{esc(s["status"])}</span>',
            "chunks": s.get("chunks_read", ""),
            "verifies": s["verifies"], "caveat": s.get("caveat", ""),
        })
    read = sum(1 for s in SRC_ROWS if s["status"] == "read")
    body = f"""
{callout('Only sources marked <span class="badge met">read</span> support any claim on this site. A source marked '
         '<span class="badge partial">link-verified-only</span> was confirmed to exist at that URL but no content was parsed; '
         'a source marked <span class="badge blocked">not-read</span> verifies nothing and is registered only as a candidate for '
         "future work. Registering a source is not the same as reading it, and the distinction is the whole point of this page.", "info")}
<div class="kpis">
{kpi(len(SRC_ROWS), "sources registered", "L-S01 … L-S12")}
{kpi(read, "actually read this session", "these are the only ones any claim rests on")}
{kpi(sum(1 for s in SRC_ROWS if s["status"] == "link-verified-only"), "link-verified only", "exists, not parsed")}
{kpi(sum(1 for s in SRC_ROWS if s["status"].startswith("not-read")), "not read", "registered as candidates; no claim made")}
</div>
{table([("#", "id"), ("Source", "name"), ("URL", "_url"), ("Status", "_status"), ("Chunks read", "chunks"),
        ("What it verifies", "verifies"), ("Caveat", "caveat")], rows, "srcs", filterable=True,
       selects=[("Status", ["read", "link-verified-only", "not-read", "not-read-this-session"])],
       search_ph="Search source, url, caveat…")}
"""
    return page("Sources", body, "sources.html",
                "Registered sources, with the status of each. Only the ones marked read support a claim.")


# --------------------------------------------------------------------------
# flagged.html (includes auto-flags raised during the build)
# --------------------------------------------------------------------------
def build_flagged():
    rows = []
    for f in FL_ROWS:
        rows.append({"id": f["id"], "type": f["type"], "what": f["what"], "detail": f["detail"],
                     "affected": f["affected"], "action": f["action"],
                     "_src": source_cell(f["source"], "flagged", f["id"])})
    for pg, rid, reason, text in AUTO_FLAGS:
        rows.append({"id": "AUTO", "type": "auto-flagged by the builder", "what": reason,
                     "detail": f'Raised while rendering {pg} for row {rid}. Source text: {text or "(empty)"}',
                     "affected": pg, "action": "Attach an official source link, or confirm the value should stay blank and flagged.",
                     "_src": '<span class="badge unverified">no official link</span>'})
    body = f"""
{callout(esc(FLAGDOC["note"]), "warn")}
<div class="kpis">
{kpi(len(FL_ROWS), "flagged items", "each with a reason and a source link")}
{kpi(len(AUTO_FLAGS), "auto-flagged by the builder", "rows rendered without an official-host link")}
{kpi(sum(1 for f in FL_ROWS if f["type"] in ("absent data", "unused authoritative source", "unset threshold", "incomplete data")),
     "missing inputs", "the honest count of what the brief asks for and this environment lacks")}
</div>
{table([("#", "id"), ("Type", "type"), ("What", "what"), ("Detail", "detail"),
        ("Where it shows up", "affected"), ("Action", "action"), ("Source", "_src")],
       rows, "flags", filterable=True,
       selects=[("Type", sorted({f["type"] for f in FL_ROWS}))],
       search_ph="Search flag, page, reason…")}
"""
    return page("Flagged for Review", body, "flagged.html",
                "Known gaps, conflicts and irregularities. None of these blocks the merge; all of them are stated.")


# --------------------------------------------------------------------------
def write_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "style.css").write_text(CSS, encoding="utf-8")
    (ASSETS / "app.js").write_text(JS, encoding="utf-8")


CSS = """
:root{--bg:#0f1216;--panel:#161b22;--line:#262d36;--fg:#dfe6ee;--dim:#93a1b1;--acc:#58a6ff;
--met:#2ea043;--part:#d29922;--block:#f85149;--gate:#a371f7}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc)}
header.top{background:var(--panel);border-bottom:1px solid var(--line);padding:10px 16px;position:sticky;top:0;z-index:5}
.brand{display:flex;gap:12px;align-items:baseline;margin-bottom:6px}
.brand a{font-weight:700;font-size:17px;color:var(--fg);text-decoration:none}
.brand span{color:var(--dim);font-size:12px}
nav{display:flex;flex-wrap:wrap;gap:4px}
nav a{font-size:12.5px;padding:4px 8px;border-radius:5px;text-decoration:none;color:var(--dim)}
nav a:hover,nav a.active{background:#1f2630;color:var(--fg)}
main{max-width:1400px;margin:0 auto;padding:20px 16px 60px}
h1{font-size:24px;margin:0 0 4px}
h2{font-size:18px;margin:32px 0 10px;padding-top:14px;border-top:1px solid var(--line)}
h3{font-size:15px;margin:20px 0 8px;color:var(--dim)}
p.lead{color:var(--dim);max-width:95ch;margin:0 0 8px}
p{max-width:110ch}
.callout{border:1px solid var(--line);border-left:3px solid var(--acc);background:var(--panel);
padding:10px 14px;border-radius:6px;margin:14px 0;max-width:120ch}
.callout.warn{border-left-color:var(--part)}
.callout.info{border-left-color:var(--acc)}
.kpis{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 14px;min-width:170px;flex:1}
.kpi-v{font-size:22px;font-weight:700}
.kpi-l{font-size:12px;color:var(--fg);margin-top:2px}
.kpi-n{font-size:11px;color:var(--dim);margin-top:2px}
.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:8px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#1b222b;position:sticky;top:0;font-size:12px;text-transform:uppercase;letter-spacing:.03em;color:var(--dim)}
tbody tr:hover{background:#1a2029}
td{color:var(--fg)}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.filters input[type=search]{flex:1;min-width:220px;padding:7px 10px;border-radius:6px;border:1px solid var(--line);
background:#0e1319;color:var(--fg)}
.filters select{padding:6px 8px;border-radius:6px;border:1px solid var(--line);background:#0e1319;color:var(--fg)}
.badge{display:inline-block;font-size:11px;padding:2px 7px;border-radius:20px;border:1px solid var(--line);
background:#1f2630;color:var(--fg);text-decoration:none;white-space:nowrap}
.badge.official{border-color:#1f6feb55;color:#79c0ff}
.badge.secondary{border-color:#d2992255;color:#e3b341}
.badge.unverified{border-color:var(--block);color:#ff9b95}
.badge.met{background:#12261a;border-color:#2ea04366;color:#56d364}
.badge.partial{background:#2b2311;border-color:#d2992266;color:#e3b341}
.badge.blocked{background:#2b1416;border-color:#f8514966;color:#ff7b72}
.badge.gate{background:#221a2e;border-color:var(--gate);color:#d2b8ff}
.blank{display:inline-block;min-width:90px;border-bottom:1px dashed #3d4753}
.blank::after{content:"(blank)";font-size:11px;color:#6e7d8d}
.opts{margin:0;padding-left:18px;max-width:64ch}
.opts li{margin-bottom:6px}
.opts label{display:block;cursor:pointer}
input.own{width:100%;margin-top:4px;padding:5px 7px;border-radius:5px;border:1px solid var(--line);background:#0e1319;color:var(--fg)}
.actions{display:flex;gap:8px;align-items:center;margin:12px 0;flex-wrap:wrap}
.actions button{padding:7px 12px;border-radius:6px;border:1px solid var(--line);background:#1f2630;color:var(--fg);cursor:pointer}
.actions button:hover{border-color:var(--acc)}
#save-note{font-size:12px;color:var(--dim)}
ol.workflow{max-width:110ch;color:var(--dim)}
ol.summary{max-width:120ch}
ol.summary li{margin-bottom:9px}
blockquote{border-left:3px solid var(--acc);margin:10px 0;padding:8px 14px;background:var(--panel);
font-style:italic;max-width:110ch}
pre.json{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px;overflow:auto;font-size:12px}
footer{border-top:1px solid var(--line);padding:18px 16px;color:var(--dim);font-size:12px;max-width:1400px;margin:0 auto}
footer p{max-width:120ch}
"""

JS = """
(function () {
  // ---- table filtering -------------------------------------------------
  function filterTables() {
    var tables = {};
    document.querySelectorAll('input[type=search][data-filter]').forEach(function (input) {
      var id = input.getAttribute('data-filter');
      var table = document.getElementById(id);
      if (!table) return;
      tables[id] = {
        input: input,
        table: table,
        selects: Array.prototype.slice.call(document.querySelectorAll('select[data-filter="' + id + '"]'))
      };
    });

    function colFor(select, heads) {
      var want = select.getAttribute('aria-label').replace(/^filter /i, '').trim().toLowerCase();
      for (var i = 0; i < heads.length; i++) {
        if (heads[i].textContent.trim().toLowerCase() === want) return i;
      }
      return -1;
    }

    function apply(cfg) {
      var q = cfg.input.value.toLowerCase().trim();
      var heads = Array.prototype.slice.call(cfg.table.querySelectorAll('thead th'));
      var rows = Array.prototype.slice.call(cfg.table.tBodies[0].rows);
      rows.forEach(function (row) {
        var ok = !q || row.textContent.toLowerCase().indexOf(q) !== -1;
        if (ok) {
          cfg.selects.forEach(function (sel) {
            if (!ok) return;
            var v = sel.value.trim();
            if (!v) return;
            var ci = colFor(sel, heads);
            if (ci < 0) return;
            var cell = row.cells[ci];
            if (!cell || cell.textContent.trim() !== v) ok = false;
          });
        }
        row.style.display = ok ? '' : 'none';
      });
    }

    Object.keys(tables).forEach(function (id) {
      var cfg = tables[id];
      cfg.input.addEventListener('input', function () { apply(cfg); });
      cfg.selects.forEach(function (sel) {
        sel.addEventListener('change', function () { apply(cfg); });
      });
    });
  }

  // ---- suggestion review board (stored in this browser only) -----------
  var KEY = 'fl4-lab-suggestions-v1';

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { return {}; }
  }

  function persist(data) {
    try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) {}
  }

  function applySaved(data) {
    Object.keys(data).forEach(function (id) {
      var v = data[id] || {};
      if (v.option) {
        var r = document.querySelector('input[name="sg-' + id + '"][value="' + v.option + '"]');
        if (r) r.checked = true;
      }
      var own = document.querySelector('input.own[data-sg="' + id + '"]');
      if (own && v.own) own.value = v.own;
    });
  }

  function collect() {
    var data = load();
    document.querySelectorAll('input[type=radio][name^="sg-"]').forEach(function (r) {
      if (!r.checked) return;
      var id = r.getAttribute('name').slice(3);
      data[id] = data[id] || {};
      data[id].option = r.value;
    });
    document.querySelectorAll('input.own[data-sg]').forEach(function (i) {
      var id = i.getAttribute('data-sg');
      data[id] = data[id] || {};
      data[id].own = i.value;
    });
    return data;
  }

  var note = document.getElementById('save-note');
  var saveBtn = document.getElementById('save-all');
  var clearBtn = document.getElementById('clear-all');
  var exportBtn = document.getElementById('export-all');

  if (saveBtn) saveBtn.addEventListener('click', function () {
    var d = collect();
    persist(d);
    var n = Object.keys(d).length;
    if (note) note.textContent = 'Saved ' + n + ' choice(s) in this browser only. To make one binding, set status in data/lab/suggestions.json.';
  });

  if (clearBtn) clearBtn.addEventListener('click', function () {
    try { localStorage.removeItem(KEY); } catch (e) {}
    document.querySelectorAll('input[type=radio][name^="sg-"]').forEach(function (r) { r.checked = false; });
    document.querySelectorAll('input.own[data-sg]').forEach(function (i) { i.value = ''; });
    if (note) note.textContent = 'Cleared saved choices from this browser.';
  });

  if (exportBtn) exportBtn.addEventListener('click', function () {
    var d = collect();
    var lines = Object.keys(d).sort().map(function (id) {
      return id + ': ' + (d[id].option || '(none)') + (d[id].own ? ' | ' + d[id].own : '');
    }).join('\\n');
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(lines).then(function () {
        if (note) note.textContent = 'Copied ' + Object.keys(d).length + ' choice(s) to the clipboard.';
      }, function () { if (note) note.textContent = 'Copy failed. Choices: ' + lines; });
    } else if (note) {
      note.textContent = 'Clipboard unavailable. Choices: ' + lines;
    }
  });

  filterTables();
  applySaved(load());
})();
"""


# --------------------------------------------------------------------------
PRICE_GATES = len([g for g in BLOCKED_GATES if g.startswith("Q-PRICE") or g.startswith("Q-LEGAL") or g.startswith("Q-STORE")])


PAGE_FNS = [
    ("index.html", build_index),
    ("results.html", build_results),
    ("availability.html", build_availability),
    ("depth.html", build_depth),
    ("models.html", build_models),
    ("leaderboard.html", build_leaderboard),
    ("correlations.html", build_correlations),
    ("price-policy.html", build_price_policy),
    ("fixtures.html", build_fixtures),
    ("questions.html", build_questions),
    ("suggestions.html", build_suggestions),
    ("repo-review.html", build_repo_review),
    ("sources.html", build_sources),
]


def main():
    fail_on_warn = "--fail-on-warn" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAGE_FNS:
        PAGES[name] = fn()
    # flagged page last, so builder-raised flags are included
    PAGES["flagged.html"] = build_flagged()

    warnings = []
    price_values = 0
    for name, doc in sorted(PAGES.items()):
        leaked = [m.group(0) for m in re.finditer(r">\s*None\s*<", doc)]
        if leaked:
            raise SystemExit(f"FATAL [{name}]: leaked None in a table cell: {leaked[:3]}")
        for m in PRICE_RE.finditer(doc):
            price_values += 1
        (OUT / name).write_text(doc, encoding="utf-8")
    write_assets()

    print(f"wrote {len(PAGES)} pages to {OUT.relative_to(ROOT)}/ and 2 assets")
    print(f"  requirements: {len(REQ_ROWS)} rows "
          f"({STATUS_COUNT['met'] + STATUS_COUNT['met at merge']} met, "
          f"{STATUS_COUNT['partial']} partial, {STATUS_COUNT['blocked']} blocked)")
    print(f"  gates named: {len(GATES)} ({len(BLOCKED_GATES)} currently blocking something)")
    print(f"  games: {len(GAMES)} ({len(FINAL)} FINAL, {len(NOTFINAL)} not final at capture)")
    print(f"  injury rows: {len(INJ_ROWS)} across {len({r['club'] for r in INJ_ROWS})} clubs")
    print(f"  sources: {len(SRC_ROWS)} registered, "
          f"{sum(1 for s in SRC_ROWS if s['status'] == 'read')} read this session")
    print(f"  flags: {len(FL_ROWS)} published + {len(AUTO_FLAGS)} auto-raised by the builder")
    print(f"  price-derived values rendered: {price_values}")
    if price_values:
        warnings.append("a price-derived value reached the page; no price exists in this environment")
    if warnings:
        for w in warnings:
            print("WARN:", w)
        print(f"{len(warnings)} warning(s)")
        if fail_on_warn:
            sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
