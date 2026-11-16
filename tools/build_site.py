#!/usr/bin/env python3
"""Build the static GitHub Pages site from data/*.json.

Run from the repo root:  python3 tools/build_site.py

Rules enforced here (from the project brief):
  * Every table row gets a source column. A row whose source has no official
    link (nfl.com, operations.nfl.com, diputados.gob.mx, gob.mx, github.com) is
    marked UNVERIFIED and added to the Flagged for Review page automatically.
  * Values are never inferred. Empty values stay blank and are flagged.
"""
import html
import json
import pathlib
import re
from collections import Counter, defaultdict
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
AS_OF = "2026-11-14"
OFFICIAL_HOSTS = ("nfl.com", "nflgsis.com", "operations.nfl.com", "diputados.gob.mx", "gob.mx",
                  "github.com", "sassnarep3-star.github.io", "juegosysorteos.gob.mx",
                  "nist.gov", "scikit-learn.org")

NAV = [
    ("Dashboard", "index.html"),
    ("Executive summary", "pages/executive-summary.html"),
    ("Injuries & depth", "pages/injuries.html"),
    ("Strategies", "pages/strategies.html"),
    ("Questions", "pages/questions.html"),
    ("Requirements", "pages/requirements.html"),
    ("Suggestions", "pages/suggestions.html"),
    ("Repo review", "pages/repo-review.html"),
    ("Sources", "pages/sources.html"),
    ("Flagged for Review", "pages/flagged.html"),
    ("Decision Lab (blueprint)", "decision-lab.html"),
    ("Signals & origination", "signals/index.html"),
]

UNIT = {"QB": "QB", "RB": "RB", "FB": "RB", "WR": "WR", "TE": "TE",
        "T": "OL", "G": "OL", "C": "OL", "DE": "DL", "DT": "DL", "LB": "LB",
        "CB": "DB", "S": "DB", "K": "ST", "P": "ST", "LS": "ST"}
UNIT_ORDER = ["QB", "RB", "WR", "TE", "OL", "DL", "LB", "DB", "ST"]

AUTO_FLAGS = []  # (page, id, reason, source) populated while rendering


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


SOURCES = {s["id"]: s for s in load("sources.json")["sources"]}
URL_RE = re.compile(r"https?://[^\s;,)\]]+")
SID_RE = re.compile(r"\bS\d{2}\b")


def esc(v):
    return html.escape("" if v is None else str(v), quote=True)


def host_kind(url):
    host = urlparse(url).hostname or ""
    if any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS):
        return "official"
    return "secondary"


def resolve_sources(text):
    """Return list of (url, kind, label) found in a source string (URLs or S-ids)."""
    found, seen = [], set()
    for sid in SID_RE.findall(text or ""):
        if sid in SOURCES and SOURCES[sid]["url"] not in seen:
            url = SOURCES[sid]["url"]
            seen.add(url)
            found.append((url, SOURCES[sid]["type"] if host_kind(url) == "secondary" else "official", sid))
    for url in URL_RE.findall(text or ""):
        url = url.rstrip(".")
        if url not in seen:
            seen.add(url)
            found.append((url, host_kind(url), urlparse(url).hostname))
    return found


def source_cell(text, page, row_id, flag_if_missing=True):
    """Render a source cell; flag automatically when no official link exists."""
    links = resolve_sources(text)
    official = [l for l in links if l[1] == "official"]
    if not links:
        if "user brief" in (text or "").lower():
            return '<span class="badge brief">User brief (scope/requirement; not an external fact)</span>'
        if flag_if_missing:
            AUTO_FLAGS.append((page, row_id, "No source link", text or ""))
        return '<span class="badge unverified">UNVERIFIED - no source</span>'
    parts = []
    for url, kind, label in links:
        cls = "badge official" if kind == "official" else "badge secondary"
        tag = "official" if kind == "official" else "secondary"
        parts.append(f'<a class="{cls}" href="{esc(url)}" target="_blank" rel="noopener">{esc(label)} ({tag})</a>')
    if not official and flag_if_missing:
        AUTO_FLAGS.append((page, row_id, "Secondary source only", text or ""))
        parts.append('<span class="badge unverified">needs official check</span>')
    return " ".join(parts)


def status_badge(s):
    s = s or ""
    cls = {"Out": "out", "Doubtful": "doubt", "Questionable": "quest"}.get(s, "")
    return f'<span class="badge {cls}">{esc(s)}</span>' if s else ""


def table(cols, rows, tid, filterable=False, status_key=None):
    """cols: list of (header, key_or_callable). rows: list of dicts (each has '_src' html)."""
    head = "".join(f"<th>{esc(h)}</th>" for h, _ in cols)
    body = []
    for r in rows:
        attrs = f' data-status="{esc(r.get(status_key, ""))}"' if status_key else ""
        cells = []
        for _, key in cols:
            v = key(r) if callable(key) else r.get(key, "")
            raw = callable(key) or str(key).startswith("_")
            cells.append(f"<td>{v if raw else esc(v)}</td>")
        body.append(f"<tr{attrs}>{''.join(cells)}</tr>")
    filt = ""
    if filterable:
        opts = ""
        if status_key:
            opts = ('<select data-filter="%s"><option value="">All statuses</option>'
                    '<option>Out</option><option>Doubtful</option><option>Questionable</option></select>' % tid)
        filt = (f'<div class="filters"><input type="search" data-filter="{tid}" '
                f'placeholder="Search player, team, injury, source..." aria-label="Search table">{opts}</div>')
    return (f'{filt}<div class="table-wrap"><table id="{tid}"><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def page_shell(title, body, prefix, active):
    nav = "".join(
        f'<a href="{prefix}{href}" class="{"active" if href == active else ""}">{esc(label)}</a>'
        for label, href in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | NFL Lines Research</title>
<link rel="stylesheet" href="{prefix}assets/style.css">
</head><body>
<header class="top"><div class="brand"><a href="{prefix}index.html">NFL Lines Research</a><span>Data as of {AS_OF}</span></div>
<nav>{nav}</nav></header>
<main>
<h1>{esc(title)}</h1>
{body}
</main>
<footer><p>Informational research only. Not betting advice. Every value links to a source; values that could not be confirmed are marked UNVERIFIED and listed on the <a href="{prefix}pages/flagged.html">Flagged for Review</a> page.
Legal status of betting in Mexico is an open question (Q-03).</p>
<p>Source repository: <a href="https://github.com/sassnarep3-star/FL4">github.com/sassnarep3-star/FL4</a> (GitHub Pages publishes the integrated main branch).</p></footer>
<script src="{prefix}assets/app.js"></script>
</body></html>
"""


def kpi(label, value, note=""):
    return f'<div class="kpi"><div class="kpi-v">{esc(value)}</div><div class="kpi-l">{esc(label)}</div><div class="kpi-n">{esc(note)}</div></div>'


def callout(text, kind="info"):
    return f'<div class="callout {kind}">{text}</div>'


# ---------- derived injury statistics (computed, not typed) ----------
INJ = load("injuries_w10_2026.json")
ROWS = INJ["rows"]
for r in ROWS:
    r["unit"] = UNIT.get(r["position"], "?")
    r["_src"] = source_cell(r["source"], "injuries", r["player"] + " (" + r["team"] + ")")
    r["_status"] = status_badge(r["game_status"])
    r["_player_link"] = f'<a href="{esc(r["player_url"])}" target="_blank" rel="noopener">{esc(r["player"])}</a>'
    r["_fl"] = r.get("flag", "")
COUNTS = Counter(r["game_status"] for r in ROWS)
N_ROWS = len(ROWS)
N_OUT, N_DOUBT, N_QUEST = COUNTS["Out"], COUNTS["Doubtful"], COUNTS["Questionable"]

team_stats = defaultdict(lambda: Counter())
unit_players = defaultdict(list)
for r in ROWS:
    team_stats[r["team"]][r["game_status"]] += 1
    team_stats[r["team"]]["flagged"] += 1
    if r["game_status"] in ("Out", "Doubtful"):
        unit_players[(r["team"], r["unit"])].append(f'{r["player"]} ({r["game_status"]})')
        team_stats[r["team"]]["unit_" + r["unit"]] += 1
TEAM_RANK = sorted(team_stats.items(), key=lambda kv: (-(kv[1]["Out"] + kv[1]["Doubtful"]), kv[0]))
TOP_TEAMS = [(t, s["Out"], s["Doubtful"]) for t, s in TEAM_RANK[:5]]
REPORT_URL = INJ["report_url"]

# ---------- other datasets ----------
QUESTIONS = load("questions.json")["rows"]
REQS = load("requirements.json")["rows"]
SUGG = load("suggestions.json")["rows"]
STRAT = load("strategies.json")
REPO = load("repo_review.json")["rows"]
FLAGS = load("flags.json")["rows"]
NEWS = load("depth_news.json")["rows"]
REPLACEMENTS = load("replacement_tiers.json")["rows"]
SOURCE_ROWS = load("sources.json")["sources"]
OPEN_Q = sum(1 for q in QUESTIONS if q["status"].lower().startswith("open"))
PENDING_SG = sum(1 for s in SUGG if s["decision"].lower().startswith("pending"))

OUTPUTS = {}

# ---------- Injuries page ----------
team_rows = []
for t, s in TEAM_RANK:
    units = [u for u in UNIT_ORDER if s["unit_" + u]]
    team_rows.append({"team": t, "flagged": s["flagged"], "Out": s["Out"], "Doubtful": s["Doubtful"],
                      "Questionable": s["Questionable"],
                      "units": ", ".join(f'{u} {s["unit_" + u]}' for u in units) or "-",
                      "_src": source_cell(REPORT_URL, "injuries", "team " + t)})
unit_rows = []
for (t, u), players in sorted(unit_players.items(), key=lambda kv: (kv[0][0], UNIT_ORDER.index(kv[0][1]))):
    unit_rows.append({"team": t, "unit": u, "count": len(players), "players": "; ".join(players),
                      "_src": source_cell(REPORT_URL, "injuries", f"unit {t} {u}")})
news_rows = []
for n in NEWS:
    news_rows.append({"date": n["date"], "team": n["team"], "headline": n["headline"],
                      "type": n["type"], "in_report": n["in_report_as_out"],
                      "_src": source_cell(n["source"], "injuries-news", n["headline"][:40])})
game_rows = []
for g in INJ["games"]:
    n_flag = sum(1 for r in ROWS if r["game"] == g["id"])
    game_rows.append({"game": g["id"], "kickoff": g["kickoff"], "network": g["network"],
                      "result": g["result"], "flagged": n_flag,
                      "_src": source_cell(g["source"], "injuries", "game " + g["id"])})
replacement_rows = [
    dict(r, _src=source_cell(r["source"], "replacement-tiers", r["id"]))
    for r in REPLACEMENTS
]

inj_body = f"""
<p class="lead">Official NFL injury report, Week 10 of the 2026 season, as published on NFL.com ({esc(INJ['report_title'])}). Read on {AS_OF}. Source: <a href="{REPORT_URL}" target="_blank" rel="noopener">nfl.com/injuries</a> (official).</p>
<div class="kpis">
{kpi("Players flagged", N_ROWS, "injury or game status")}
{kpi("Out", N_OUT)}
{kpi("Doubtful", N_DOUBT)}
{kpi("Questionable", N_QUEST)}
{kpi("Games in report", len(INJ['games']), "incl. 1 final (Thu)")}
</div>
{callout("<b>What this shows:</b> the report tells us who is out, doubtful or questionable and who did not practise. It does <b>not</b> say who is a starter or a backup. Counts by unit use our position grouping (see below). Starter/backup status needs depth charts, which are not yet ingested (suggestion SG-02, question Q-10). Headline-level starter changes are in section 4.", "info")}

<h2>1. Teams with the most Out or Doubtful players</h2>
{table([("Team", "team"), ("Flagged", "flagged"), ("Out", "Out"), ("Doubtful", "Doubtful"), ("Questionable", "Questionable"), ("Units with Out/Doubtful", "units"), ("Source", "_src")], team_rows, "tbl-teams")}

<h2>2. Absences by unit (Out or Doubtful)</h2>
<p class="note">Unit grouping is ours, not an NFL classification: QB; RB (incl. FB); WR; TE; OL (T, G, C); DL (DE, DT); LB; DB (CB, S); ST (K, P, LS). Counts come from the report rows only.</p>
{table([("Team", "team"), ("Unit", "unit"), ("Count", "count"), ("Players (status)", "players"), ("Source", "_src")], unit_rows, "tbl-units")}

<h2>3. All flagged players - Week 10 2026</h2>
<p class="note">Each player name links to the NFL.com player page the official report uses. Search or filter by status.</p>
{table([("Game", "game"), ("Team", "team"), ("Player", "_player_link"), ("Pos", "position"), ("Injury", "injury"), ("Practice", "practice"), ("Game status", "_status"), ("Flag", "_fl"), ("Source", "_src")], ROWS, "tbl-players", filterable=True, status_key="game_status")}

<h2>4. Starter changes reported in NFL.com headlines (headline level only)</h2>
<p class="note">Read from headlines on the official report page. Article bodies were not opened, so no snap counts or depth positions are claimed.</p>
{table([("Date", "date"), ("Team", "team"), ("Headline", "headline"), ("Type", "type"), ("In Week 10 report?", "in_report"), ("Source", "_src")], news_rows, "tbl-news")}

<h2>5. Starter replacement chain — tracking schema only</h2>
<p class="note">The six rows below are blank field templates for both offense and defense, through second-, third-, and fourth-string tiers. Create one record per team, game/week, and position/unit only when a primary source verifies the role; these are not player observations. An NFL roster page or injury report alone is not a depth chart. Verify participation separately in official game books. Effects remain blank until sourced, timestamped, and evaluated out of sample. Source links are review routes, not evidence that a player or tier is confirmed.</p>
{table([("Side", "side"), ("Tier to verify", "tier_to_verify"), ("Team", "team"), ("Game / week", "game_or_week"), ("Position / unit", "position_or_unit"), ("Absent starter / role", "absent_starter_or_role"), ("Starter status at cutoff", "starter_status_at_cutoff"), ("Replacement player", "replacement_player"), ("Replacement injury / availability", "replacement_injury_or_availability"), ("Forecast cutoff (UTC)", "forecast_cutoff_utc"), ("Observed participation / snaps", "observed_participation_or_snaps"), ("Impact estimate", "impact_estimate"), ("Status", "status"), ("Official source to review", "_src")], replacement_rows, "tbl-replacements")}

<h2>6. Games in the report</h2>
{table([("Game", "game"), ("Kickoff (ET)", "kickoff"), ("Network", "network"), ("Result", "result"), ("Flagged players", "flagged"), ("Source", "_src")], game_rows, "tbl-games")}
"""
OUTPUTS["pages/injuries.html"] = ("NFL injuries and depth - Week 10 2026", inj_body, "../", "pages/injuries.html")

# ---------- Depth status note (in injuries page section 2) ----------

# ---------- Executive summary ----------
exec_body = f"""
<p class="lead">Summary as of {AS_OF}. Every number below is computed from the data files, and each has a source on its page.</p>
<div class="kpis">
{kpi("Flagged players, Week 10", N_ROWS)}
{kpi("Out / Doubtful", f"{N_OUT} / {N_DOUBT}")}
{kpi("Validated strategies", 0, "none built or tested")}
{kpi("Open questions", OPEN_Q)}
{kpi("Flags for review", "__FLAGCOUNT__")}
</div>
<h2>Key findings</h2>
<ol class="findings">
<li><b>Injury picture (official):</b> the NFL's Week 10 report lists {N_ROWS} flagged players across {len(INJ['games'])} games: {N_OUT} Out, {N_DOUBT} Doubtful, {N_QUEST} Questionable. Teams with the most Out or Doubtful players: {", ".join(f"{t} ({o} Out, {d} Doubtful)" for t, o, d in TOP_TEAMS)}. <a href="injuries.html">Injuries page</a>. Source: <a href="{REPORT_URL}" target="_blank" rel="noopener">NFL.com</a>.</li>
<li><b>Starter replacements (headline level, NFL.com):</b> Seahawks QB Sam Darnold ruled out for Week 10; Drew Lock expected to start. Dolphins placed QB Malik Willis on injured reserve with Kyle McCord in line for his first start. Ravens placed Lamar Jackson on injured reserve; Tyler Huntley reported out for the season. Browns (Deshaun Watson) and Cardinals (Carson Beck) start-headlines are from the Nov 11 roundup and may be out of date. <a href="injuries.html">Section 4</a>.</li>
<li><b>Depth charts are still the evidence gap:</b> a blank tracker now reserves offense and defense slots for second-, third-, and fourth-string replacements. No player, tier, injury-to-role mapping, snap share, or impact value is populated; official depth evidence and participation checks remain open (Q-10, SG-02).</li>
<li><b>Line generation remains a blueprint:</b> the Strategies page specifies score-distribution, fair-price, player-prop, joint-combo, and skill-versus-luck methods, but no model or line has been fitted. Historical odds / prop prices are absent (Q-01, Q-02), no threshold is selected (Q-06), and all correlation values remain blank.</li>
<li><b>Legal status is unresolved:</b> the official Mexican federal law (Ley Federal de Juegos y Sorteos, 1947) prohibits betting games unless SEGOB permits them (Art. 1, 3, 4). Whether and how online sports betting is authorised is not confirmed from an official source (Q-03, flag F-09). NFL personnel are barred from betting on NFL games; this is reported in secondary sources (F-11).</li>
<li><b>Repository history:</b> the initial review of the base commit found only a one-line README; the integrated main branch now contains the dashboard, sourced registries, build/link verification, and Pages workflow. <a href="repo-review.html">Repo review</a>.</li>
</ol>

<h2>Decisions needed from you</h2>
<ul class="findings">
<li>Scope: research only, paper trading, or real money (Q-04, SG-09). Real money is blocked until the legal question (Q-03) is answered.</li>
<li>What counts as a useful signal, and the thresholds for the gates (Q-06, SG-05).</li>
<li>What a "reward" for top strategies is (Q-05).</li>
<li>Whether to collect multi-season injury history (SG-01) and depth charts (SG-02) next.</li>
<li>Whether Pages deployment should be gated on both verification workflows (Q-13, SG-07). No automated NFL data fetch is configured.</li>
</ul>

<h2>How this summary was checked</h2>
<p>Injury rows were read from the official NFL.com report text on {AS_OF}. Each row links to the player page in that report. Legal points were checked against the official text of the 1947 federal law on the Chamber of Deputies site. NFL policy statements are second-hand (reported by ESPN, the Inquirer and MLive) and are flagged. Items that could not be confirmed are listed on the <a href="flagged.html">Flagged for Review</a> page.</p>
"""
OUTPUTS["pages/executive-summary.html"] = ("Executive summary", exec_body, "../", "pages/executive-summary.html")

# ---------- Strategies ----------
bet_rows = [dict(r, _src=source_cell(r["source"], "strategies", r["type"])) for r in STRAT["bet_types"]]
gate_rows = [dict(g, threshold=g["threshold"] if not g["threshold"].startswith("UNVERIFIED") else "UNVERIFIED (blank)",
                  _src=source_cell(g["source"], "strategies", g["id"]))
             for g in STRAT["gates"]]
corr_rows = [dict(c, value=c["value"] or "", _src=source_cell(c["source"], "strategies", c["pair"])) for c in STRAT["correlation"]]
lb_rows = STRAT["leaderboard"]
line_cards = []
for section in STRAT.get("line_generation", []):
    citations = source_cell(section["source"], "strategies-method", section["id"], flag_if_missing=False)
    line_cards.append(
        '<article class="model-card">'
        f'<p class="model-step">{esc(section["id"])}</p>'
        f'<h3>{esc(section["title"])}</h3>'
        f'<p>{esc(section["body"])}</p>'
        f'<pre class="formula">{esc(section["formula"])}</pre>'
        f'<p class="note">Method / official review links: {citations}</p>'
        '</article>'
    )
line_blueprint_html = '<div class="model-grid">' + ''.join(line_cards) + '</div>'
strat_body = f"""
<p class="lead">{esc(STRAT['status'])}</p>
{callout("<b>Leaderboard:</b> empty. A strategy appears here only after it passes every gate, with its source link. No rewards are defined yet (question Q-05).", "warn")}
<h2>1. Bet types in scope</h2>
<p class="note">These rows define project scope from the brief; they are not claims about an available book, a lawful market, or a licensed data feed.</p>
{table([("Type", "type"), ("Examples", "examples"), ("Needs", "needs"), ("Source / scope", "_src")], bet_rows, "tbl-bets")}
<h2>2. How an NFL line would be generated (blueprint only)</h2>
{callout("The following is a proposed calculation design, not a fitted model. No probabilities, fair prices, picks, player estimates, or model correlations have been generated. Official NFL links are discovery/verification routes; they do not establish historical data access or reuse rights.", "info")}
{line_blueprint_html}
<h2>3. Validation gates (proposals; thresholds not set)</h2>
<p class="note">These gates are research-design choices, not empirical facts. Numerical thresholds remain blank until the target metric and decision protocol are pre-registered (Q-06).</p>
{table([("ID", "id"), ("Gate", "name"), ("Rule", "rule"), ("Threshold", "threshold"), ("Status", "status"), ("Source / method reference", "_src")], gate_rows, "tbl-gates")}
<h2>4. Leaderboard</h2>
{table([(c, "") for c in STRAT["leaderboard_columns"]], [], "tbl-leader")}
<p class="note">No rows yet. Rewards, eligibility, and governance are not defined (Q-05); no strategy has passed validation.</p>
<h2>5. Correlation values</h2>
<p class="note">No values are computed. The NIST reference defines correlation as association; it is not a joint parlay probability. Values stay blank until licensed, timestamped historical outcomes are verified (Q-15).</p>
{table([("Pair", "pair"), ("Value", "value"), ("Status", "status"), ("Source / method reference", "_src")], corr_rows, "tbl-corr")}
"""
OUTPUTS["pages/strategies.html"] = ("Strategies, line generation and validation", strat_body, "../", "pages/strategies.html")

# ---------- Questions ----------
def src_only(q):
    return source_cell(q["source"], "questions", q["id"])
qrows = [dict(q, _src=src_only(q)) for q in QUESTIONS]
q_body = f"""
<p class="lead">Questions and information gaps to close before a decision. Each row says what is known (with sources), what is missing, and how to find it out.</p>
{callout(f"<b>{OPEN_Q} of {len(QUESTIONS)} questions remain open.</b> Decision blockers: Q-01 (odds data), Q-02 (prop-policy review), Q-03 (legal scope), Q-06 (success metric). Q-12 also blocks automated NFL data collection until express written consent is obtained.", "warn")}
{table([("ID", "id"), ("Area", "area"), ("Question", "question"), ("Known (sourced)", "known"), ("Missing", "missing"), ("How to discover", "how_to_discover"), ("Source", "_src"), ("Status", "status")], qrows, "tbl-questions", filterable=True)}
"""
OUTPUTS["pages/questions.html"] = ("Questions and information gaps", q_body, "../", "pages/questions.html")

# ---------- Requirements ----------
rrows = [dict(r, _src=source_cell(r["source"], "requirements", r["id"], flag_if_missing=False)) for r in REQS]
for r in rrows:
    if r["source"] == "User brief":
        r["_src"] = '<span class="badge brief">User brief - a requirement, not a data value</span>'
        AUTO_FLAGS.append(("requirements", r["id"], "Requirement from brief - no external source (not a factual value)", "User brief"))
req_body = f"""
<p class="lead">Each requirement from the brief, its status, and how it was addressed. Requirements are restated from the brief; they are not factual claims, so their source is the brief itself.</p>
{table([("ID", "id"), ("Requirement", "requirement"), ("Status", "status"), ("How addressed", "how_addressed"), ("Source", "_src")], rrows, "tbl-reqs", filterable=True)}
"""
OUTPUTS["pages/requirements.html"] = ("Requirements", req_body, "../", "pages/requirements.html")

# ---------- Suggestions ----------
def suggestion_control(s):
    if s.get("decision", "").lower().startswith("implemented"):
        return '<span class="badge done">Implemented in this task</span>'
    options = ['<option value="">Choose A, B, C, or defer</option>']
    for option in s["options"]:
        key = option.split(":", 1)[0].strip().upper()
        options.append(f'<option value="{esc(key)}">{esc(option)}</option>')
    options.append('<option value="defer">Defer for now</option>')
    return (f'<select class="suggestion-choice" data-suggestion-choice="{esc(s["id"])}" '
            f'aria-label="Select a review choice for {esc(s["id"])}">{"".join(options)}</select>')

srows = []
for s in SUGG:
    srows.append(dict(s, options=" / ".join(s["options"]), _src=source_cell(s["source"], "suggestions", s["id"]),
                      _dec=suggestion_control(s)))
sg_body = f"""
<p class="lead">Review each suggestion and select A, B, C, or defer. Choices are saved only in this browser; they do not change the code, authorize data collection, or affect other visitors.</p>
{callout(f"<b>{PENDING_SG} of {len(SUGG)} suggestions remain open.</b> Both site sections have CI verification; SG-07 asks whether Pages publication should depend on those checks. All choices on this page are local review notes only.", "info")}
<div class="suggestion-tools"><button type="button" class="secondary-button" data-clear-suggestion-choices>Clear choices saved in this browser</button><span class="note" data-suggestion-feedback aria-live="polite">Selections are stored locally on this device only.</span></div>
{table([("ID", "id"), ("Suggestion", "suggestion"), ("Closes gap", "closes_gap"), ("Benefit", "benefit"), ("Cost", "cost"), ("Options", "options"), ("Source / review route", "_src"), ("Your local choice", "_dec")], srows, "tbl-sugg", filterable=True)}
"""
OUTPUTS["pages/suggestions.html"] = ("Suggestions - review and select", sg_body, "../", "pages/suggestions.html")

# ---------- Repo review ----------
repo_rows = [dict(r, _src=source_cell(r["source"], "repo-review", r["id"])) for r in REPO]
repo_body = f"""
<p class="lead">Line-by-line review of the repository as of {AS_OF}. Each finding was checked with git or the GitHub API in the sandbox and links to the object checked.</p>
{table([("ID", "id"), ("Item", "item"), ("Finding", "finding"), ("Evidence", "evidence"), ("Severity", "severity"), ("Status", "status"), ("Source", "_src")], repo_rows, "tbl-repo", filterable=True)}
"""
OUTPUTS["pages/repo-review.html"] = ("Repository review", repo_body, "../", "pages/repo-review.html")

# ---------- Sources ----------
src_rows = []
for s in SOURCE_ROWS:
    url_kind = host_kind(s["url"])
    src_rows.append({"_id": f'<span id="{s["id"]}">{s["id"]}</span>', "title": s["title"],
                     "publisher": s["publisher"],
                     "_type": f'<span class="badge {url_kind}">{url_kind}</span>',
                     "used_for": s["used_for"],
                     "_link": f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["url"])}</a>'})
src_body = f"""
<p class="lead">Sources reviewed {AS_OF}. Official primary sources include the NFL, Mexican government, GitHub, and the named NIST/scikit-learn methodology documentation. Secondary reports are labelled and used only for review flags. A linked official page is a review route, not proof of data access or reuse rights.</p>
{table([("ID", "_id"), ("Title", "title"), ("Publisher", "publisher"), ("Type", "_type"), ("Used for", "used_for"), ("Link", "_link")], src_rows, "tbl-sources", filterable=True)}
"""
OUTPUTS["pages/sources.html"] = ("Sources", src_body, "../", "pages/sources.html")

# ---------- Flagged for review ----------
flag_rows = []
for f in FLAGS:
    flag_rows.append(dict(f, _src=source_cell(f["source"], "flagged", f["id"], flag_if_missing=False)))
auto_rows = []
for page, rid, reason, src in AUTO_FLAGS:
    auto_rows.append({"page": page, "row": rid, "reason": reason, "source": src})
fl_body = f"""
<p class="lead"><b>Flagged for Review.</b> These items are published so you can review them after the site is live. They do not block the merge. Each item links to the source to check.</p>
{callout("Unverified values were left blank or marked, not filled in. Secondary-source items are the main risk: the NFL policy text and the Mexican legal position are not yet confirmed from primary text.", "warn")}
<h2>1. Flags (irregularities and unverified items)</h2>
{table([("ID", "id"), ("Area", "area"), ("Item", "item"), ("Why flagged", "why"), ("Status", "status"), ("Source", "_src")], flag_rows, "tbl-flags", filterable=True)}
<h2>2. Rows flagged automatically by the build</h2>
<p class="note">Any table row whose source has no official link appears here. Requirement rows from the brief are listed as an expected exception.</p>
{table([("Page", "page"), ("Row", "row"), ("Reason", "reason"), ("Source text", "source")], auto_rows, "tbl-auto", filterable=True)}
"""
OUTPUTS["pages/flagged.html"] = ("Flagged for Review", fl_body, "../", "pages/flagged.html")

# ---------- Decision readiness and removal-of-luck panel (landing page) ----------
N_OD = N_OUT + N_DOUBT
_LBS = json.loads((DATA / "signals" / "leaderboard.json").read_text(encoding="utf-8"))
_GATES = json.loads((DATA / "signals" / "gates.json").read_text(encoding="utf-8"))
_STRATS = json.loads((DATA / "signals" / "strategies.json").read_text(encoding="utf-8"))["strategies"]
_G1 = next(g for g in _GATES["gates"] if g["id"] == "G-1")["threshold"]


LUCK_HTML = f"""
<h2 id="luck">Removal-of-luck panel</h2>
<p class="lead">Nothing on this panel is a result. It shows how far the evidence is from the minimum needed before any skill claim is possible.</p>
<div class="kpis">
{kpi("Settled prospective bets", "%d of %d" % (_LBS["removal_of_luck_panel"]["current_n"], _G1["min_bets"]), "minimum for any claim (G-1)")}
{kpi("Distinct games", "0 of %d" % _G1["min_distinct_games"], "G-1 minimum")}
{kpi("Strategies qualifying at stage 1", "0 of %d" % len(_STRATS), "proper-score lower bound not computed")}
{kpi("Control-baseline runs", 0, "random, favourites-only, shopping")}
{kpi("Backtest figures on the leaderboard", 0, "excluded by rule and by the build")}
</div>
<p class="note">Registered: <code>prereg/REGISTRATION.md</code> (commit recorded in COORDINATION.md). Leaderboard rules and demotion gate: <a href="signals/leaderboard.html">signals/leaderboard.html</a>.</p>
"""

# ---------- Index / dashboard ----------
READINESS = load("readiness.json")["rows"]
READY_COUNTS = Counter(r["status"] for r in READINESS)
ready_rows = [dict(r, _where=f'{esc(r["where"])} (User brief status; not an external fact)') for r in READINESS]
ready_html = table([("Area", "area"), ("Status", "status"), ("Blocking gate", "gate"), ("Number that clears it", "clears"), ("Current number", "current"), ("Evidence (where)", "_where")], ready_rows, "tbl-readiness", filterable=True)
idx_body = f"""
<p class="lead">A simple dashboard for the NFL research project: official injury data, questions to answer, suggestions to choose from, and a strategy leaderboard that stays empty until a strategy passes every gate.</p>
<div class="kpis">
{kpi("Flagged players, Week 10", N_ROWS, "official NFL report")}
{kpi("Out / Doubtful", f"{N_OUT} / {N_DOUBT}")}
{kpi("Open questions", OPEN_Q)}
{kpi("Suggestions awaiting you", PENDING_SG)}
{kpi("Validated strategies", 0)}
</div>
<h2>Decision readiness</h2>
<p class="note">One row per requirement area from the 2026-11-16 brief. Status counts: {", ".join(f"{k} {v}" for k, v in READY_COUNTS.most_common())}. A row is Met only when its deliverable exists on this site. Project status, not an official NFL value, so no source link applies; the gate and the official evidence are on the linked page.</p>
{ready_html}
<div class="tiles">
<a class="tile" href="pages/executive-summary.html"><b>Executive summary</b><span>Key findings and decisions needed</span></a>
<a class="tile" href="pages/injuries.html"><b>Injuries &amp; depth</b><span>Official Week 10 report, absences, headline checks, and blank offense/defense replacement slots through fourth string</span></a>
<a class="tile" href="pages/strategies.html"><b>Strategies</b><span>Line-generation blueprint, validation gates, blank correlations, leaderboard (empty)</span></a>
<a class="tile" href="pages/questions.html"><b>Questions</b><span>What we know, what is missing, how to find out</span></a>
<a class="tile" href="pages/requirements.html"><b>Requirements</b><span>Every requirement from the brief and its status</span></a>
<a class="tile" href="pages/suggestions.html"><b>Suggestions</b><span>Review recommendations and record choices locally</span></a>
<a class="tile" href="pages/repo-review.html"><b>Repo review</b><span>Line-by-line checks with links</span></a>
<a class="tile" href="pages/sources.html"><b>Sources</b><span>Official and secondary sources used</span></a>
<a class="tile" href="decision-lab.html"><b>Decision Lab (blueprint)</b><span>Earlier session's evidence-first framework, kept as built</span></a>
<a class="tile" href="signals/index.html"><b>Signals &amp; origination</b><span>Line-origination strategy catalogue, validation gates, correlation protocol and a second verified Week 10 availability capture (session 94107c0d)</span></a>
<a class="tile warn" href="pages/flagged.html"><b>Flagged for Review</b><span>__FLAGCOUNT__ items to check</span></a>
</div>
{LUCK_HTML}
"""
OUTPUTS["index.html"] = ("Dashboard", idx_body, "", "index.html")

# ---------- write ----------
def write_all():
    total_flags = len(FLAGS) + len(AUTO_FLAGS)
    written = []
    for rel, (title, body, prefix, active) in OUTPUTS.items():
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        text = page_shell(title, body.replace("__FLAGCOUNT__", str(total_flags)), prefix, active)
        out.write_text(text, encoding="utf-8")
        written.append(rel)
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    return written, total_flags


if __name__ == "__main__":
    files, total = write_all()
    print("wrote", len(files), "pages;", "flags:", total, "(curated", len(FLAGS), "+ auto", len(AUTO_FLAGS), ")")
    for f in files:
        print(" -", f)
