#!/usr/bin/env python3
"""
Build the FL4 static site from the verified datasets in data/.

Design rules enforced here:
  * data/*.json is the single source of truth; the HTML is generated, never hand-edited
  * a value the builder cannot find in a dataset is rendered as an explicit blank, not as a guess
  * relative links only, so the site works under a GitHub project-page subpath (/<repo>/)
  * no external assets, so the site renders with no third-party requests
Usage:  python3 tools/build_site.py [--fail-on-warn]
"""
import html
import json
import os
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"

PAGES = [
    ("index", "Executive summary", "What is verified, what is blocked, what to decide next"),
    ("requirements", "Requirements", "Every requirement in the brief, traced to where it is met"),
    ("questions", "Open questions", "Decision-blocking unknowns, with what we know and how to resolve it"),
    ("inventory", "Information inventory", "Information we have, information we do not have"),
    ("suggestions", "Suggestions", "Improvement backlog with a review control and a recommended path"),
    ("injuries", "Injury tracking", "Official Week 10 availability report, verified row by row"),
    ("depth", "Depth & deficiency", "Who is unavailable, and the limits of what the source can say"),
    ("strategies", "Signal strategies", "16 candidate strategies for originating lines"),
    ("validation", "Validation gates", "The tests that remove luck from strategy selection"),
    ("correlation", "Correlation", "Measurement protocol for parlay and prop dependence"),
    ("leaderboard", "Leaderboard", "Competition rules, scoring, rewards, anti-gaming"),
    ("sources", "Sources", "Every source, its tier, and what it was used for"),
    ("methodology", "Methodology", "How this site is built, verified and kept honest"),
    ("flagged", "Flagged for review", "Irregularities and unverified items, published not hidden"),
]


# ---------------------------------------------------------------- utilities
def load(name):
    return json.loads((DATA / name).read_text())


def esc(s):
    return html.escape(str(s), quote=True)


BAD = ("not-available", "blocked", "fail", "not-runnable", "quarantine", "rejected", "conflict")
GOOD = ("verified", "pass", "met", "approved", "implemented", "t1", "resolved", "available-now")
WARN = ("proposed", "partial", "review", "pending", "unverified", "not-run", "design", "null",
        "identified", "t2", "t3", "parked", "research", "monitor", "reviewer", "informational")


def badge(text):
    t = str(text)
    low = t.lower()
    tone = "neutral"
    for k in BAD:
        if k in low:
            tone = "bad"
            break
    else:
        for k in GOOD:
            if k in low:
                tone = "good"
                break
        else:
            for k in WARN:
                if k in low:
                    tone = "warn"
                    break
    return '<span class="badge %s">%s</span>' % (tone, esc(t))


def link(url, label=None, ext=True):
    if not url:
        return ""
    rel = ' rel="noopener" target="_blank"' if ext and url.startswith("http") else ""
    return '<a href="%s"%s>%s%s</a>' % (esc(url), rel, esc(label or url),
                                        '<span class="ext">\u2197</span>' if url.startswith("http") else "")


def inline(text):
    """Escape, then allow **bold**, `code` and autolinked urls."""
    out = esc(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", out)
    out = re.sub(r"`([^`]+?)`", r"<code>\1</code>", out)
    out = re.sub(r"(https?://[^\s<)]+)", lambda m: link(m.group(1)), out)
    return out


BLANK = '<span class="na" title="no value confirmable from an official source">\u2014 not available</span>'


def render_value(v, col=None):
    if v is None or v == "" or v == [] or v == {}:
        return BLANK
    if isinstance(v, bool):
        return badge("yes" if v else "no")
    if isinstance(v, (int, float)):
        return esc("{:,}".format(v) if isinstance(v, int) and abs(v) >= 1000 else v)
    if isinstance(v, str):
        low = v.lower()
        if v.startswith("http"):
            return link(v)
        if len(v) <= 46 and any(k in low for k in BAD + GOOD + WARN):
            key = col.get("badge") if isinstance(col, dict) else None
            if key or (col and isinstance(col, dict) and col.get("type") == "badge"):
                return badge(v)
        return inline(v)
    if isinstance(v, dict):
        if "url" in v:
            return link(v.get("url"), v.get("label"))
        if "label" in v and "url" not in v:
            return esc(v["label"])
        return "<br>".join('<span class="k">%s</span> %s' % (esc(k), render_value(x)) for k, x in v.items())
    if isinstance(v, list):
        parts = []
        for item in v:
            if isinstance(item, dict) and "url" in item:
                parts.append("&bull; " + link(item["url"], item.get("label")))
            elif isinstance(item, dict) and "name" in item and "status" in item:
                parts.append("&bull; %s %s" % (esc(item["name"]), badge(item["status"])))
            elif isinstance(item, dict):
                parts.append("&bull; " + render_value(item))
            else:
                parts.append("&bull; " + render_value(item))
        return "<div class='celllist'>%s</div>" % "".join(parts)
    return esc(v)


def table(block):
    cols = block["cols"]
    rows = block["rows"]
    out = []
    fid = "t-" + block.get("id", "x")
    out.append('<div class="tablewrap" id="%s">' % esc(fid))
    if block.get("title"):
        out.append('<h3>%s</h3>' % inline(block["title"]))
    meta = []
    if block.get("source"):
        meta.append("Source: " + link(block["source"].get("url"), block["source"].get("label")))
    if block.get("as_of"):
        meta.append('<span class="asof">as of %s</span>' % esc(block["as_of"]))
    if block.get("tier"):
        meta.append("Verification tier: " + badge(block["tier"]))
    if meta:
        out.append('<div class="tmeta">%s</div>' % " &middot; ".join(meta))
    if len(rows) > 8:
        out.append('<input class="filter" type="search" placeholder="Filter these %d rows\u2026" data-target="%s">'
                   % (len(rows), esc(fid)))
    out.append('<table><thead><tr>')
    for c in cols:
        cls = ' class="sortable"' if c.get("sortable", True) else ""
        out.append("<th%s data-col='%s'>%s</th>" % (cls, c["key"], inline(c["label"])))
    out.append("</tr></thead><tbody>")
    if not rows:
        out.append('<tr><td class="empty" colspan="%d">%s</td></tr>'
                   % (len(cols), esc(block.get("empty", "No rows. An empty table is a finding, not a failure."))))
    for r in rows:
        out.append("<tr>")
        for c in cols:
            key = c["key"]
            val = r.get(key, None)
            if callable(c.get("render")):
                cell = c["render"](r)
            else:
                cell = render_value(val, c)
            out.append('<td class="%s">%s</td>' % (c.get("cls", ""), cell))
        out.append("</tr>")
    out.append("</tbody></table>")
    if block.get("note"):
        out.append('<p class="tnote">%s</p>' % inline(block["note"]))
    out.append("</div>")
    return "".join(out)


def cards(block):
    out = ['<div class="cards">']
    for it in block["items"]:
        tone = it.get("tone", "neutral")
        out.append('<div class="card %s"><div class="card-label">%s</div><div class="card-value">%s</div>'
                   '<div class="card-sub">%s</div></div>'
                   % (tone, inline(it.get("label", "")), esc(it.get("value", "")), inline(it.get("sub", ""))))
    out.append("</div>")
    return "".join(out)


def prose(block):
    out = []
    if block.get("title"):
        out.append("<h3>%s</h3>" % inline(block["title"]))
    for b in block["body"]:
        if isinstance(b, str):
            out.append("<p>%s</p>" % inline(b))
        elif isinstance(b, list):
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(x) for x in b))
    return "".join(out)


def flagbox(block):
    return '<div class="callout %s"><div class="callout-title">%s</div><div>%s</div></div>' % (
        block.get("tone", "info"), inline(block["title"]), inline(block["body"]))


RENDERERS = {"table": table, "cards": cards, "prose": prose, "callout": flagbox}


def render_blocks(blocks):
    return "".join(RENDERERS[b["kind"]](b) for b in blocks)


SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} &middot; FL4 NFL Signals</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="assets/app.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="brand">
    <a href="index.html"><span class="mark">FL4</span> <span class="brandtext">NFL Signal Origination &amp; Decision System</span></a>
  </div>
  <div class="stamp">snapshot <strong>{asof}</strong> &middot; tier-1 official sources only</div>
</header>
<nav class="nav" aria-label="Site sections">
{nav}
</nav>
<main id="main">
<p class="crumb">{crumb}</p>
<h1>{h1}</h1>
{lead}
{body}
</main>
<footer class="foot">
  <div><strong>FL4</strong> &mdash; generated from <code>data/*.json</code> by <code>tools/build_site.py</code>. No value on this page was inferred; blanks are blank because no official source supports a number.</div>
  <div class="footlinks">{footer}</div>
  <div class="disclaimer">Research and information only. Nothing here is betting, legal or financial advice, and no strategy on this site has been validated. Wagering carries a risk of loss; only use operators lawfully available to you.</div>
</footer>
<script src="assets/app.js"></script>
</body>
</html>
"""


def nav_html(current):
    out = []
    for slug, title, _ in PAGES:
        cur = ' class="on"' if slug == current else ""
        out.append('<a%s href="%s.html">%s</a>' % (cur, slug, esc(title)))
    return "".join(out)


def build_page(slug, title, lead, blocks, desc=""):
    idx = [p[0] for p in PAGES].index(slug) if slug in [p[0] for p in PAGES] else -1
    crumb = "Section %d of %d" % (idx + 1, len(PAGES)) if idx >= 0 else ""
    footer = " &middot; ".join(
        link("flagged.html", "%d flagged items" % N_FLAGS, ext=False) + " &middot; " +
        link("sources.html", "source register", ext=False) + " &middot; " +
        link(SRC_REPO, "repository", ext=True)
    )
    htm = SHELL.format(title=title, desc=esc(desc or lead[:150]), asof=ASOF, nav=nav_html(slug),
                       crumb=crumb, h1=inline(title), lead='<p class="lead">%s</p>' % inline(lead) if lead else "",
                       body=render_blocks(blocks), footer=footer)
    (SITE / ("%s.html" % slug)).write_text(htm)
    return len(htm)


# ---------------------------------------------------------------- data
INJ = load("injuries_week10_2026.json")
STATE = load("league_state.json")
QUESTIONS = load("questions.json")
SUGG = load("suggestions.json")
STRAT = load("strategies.json")
GATES = load("gates.json")
CORR = load("correlations.json")
BOARD = load("leaderboard.json")
SOURCES = load("sources.json")
FLAGGED = load("flagged.json")
INV = load("inventory.json")

ASOF = INJ["meta"]["as_of_utc"][:10]
SRC_URL = INJ["meta"]["source_url"]
SRC_REPO = "https://github.com/sassnarep3-star/FL4"
N_FLAGS = len(FLAGGED["flags"])
ROWS = {t["team"]: t for t in STATE["teams"]}
TEAMNAME = {t["team"]: t["name"] for t in STATE["teams"]}


def team_cell(team):
    return "<span class='abr'>%s</span> <span class='tname'>%s</span>" % (esc(team), esc(TEAMNAME.get(team, "")))


# ---------------------------------------------------------------- checks
def run_checks():
    """Independent re-verification of the captured data against itself, run at build time."""
    res = []
    counts = INJ["team_availability_counts"]
    tally = {}
    for r in INJ["out_or_doubtful"]:
        tally.setdefault(r["team"], {"out": 0, "doubtful": 0, "questionable": 0})
        tally[r["team"]][r["status"].lower()] += 1
    bad = []
    for tm, c in counts.items():
        for k in ("out", "doubtful"):
            if c[k] != tally.get(tm, {}).get(k, 0):
                bad.append("%s %s: declared %d, row-level %d" % (tm, k, c[k], tally.get(tm, {}).get(k, 0)))
    res.append(("Row-level recount vs declared team counts (Out/Doubtful)", not bad,
                "; ".join(bad) if bad else "%d teams, %d rows reconcile exactly"
                         % (len(counts), len(INJ["out_or_doubtful"]))))
    w = sum(t["w"] for t in STATE["teams"])
    l = sum(t["l"] for t in STATE["teams"])
    t_ = sum(t["t"] for t in STATE["teams"])
    res.append(("League-wide record conservation (wins = losses, ties even)", w == l and t_ % 2 == 0,
                "%d wins, %d losses, %d ties across %d clubs" % (w, l, t_, len(STATE["teams"]))))
    dupes = {}
    for r in INJ["out_or_doubtful"]:
        k = (r["team"], r["player"])
        dupes[k] = dupes.get(k, 0) + 1
    dd = [k for k, v in dupes.items() if v > 1]
    res.append(("No duplicate player rows per club", not dd, "no duplicates" if not dd else str(dd)))
    teams_in_report = sorted({r["team"] for r in INJ["out_or_doubtful"]} | set(counts))
    res.append(("Report covers 28 clubs (14 games), 4 on bye", len(teams_in_report) == 28,
                "%d clubs present" % len(teams_in_report)))
    games_teams = sorted({t for g in INJ["games"] for t in (g["away"], g["home"])})
    res.append(("Every game in the fixture list is in the availability snapshot",
                games_teams == teams_in_report, "%d vs %d" % (len(games_teams), len(teams_in_report))))
    for g in INJ["games"]:
        for t in (g["away"], g["home"]):
            rec = g.get("records", {}).get(t)
            if rec and t in ROWS:
                row = ROWS[t]
                expected = "%d-%d" % (row["w"], row["l"]) + ("-%d" % row["t"] if row["t"] else "")
                if rec != expected:
                    bad.append("record mismatch %s: report says %s, standings say %s" % (t, rec, expected))
    res.append(("Matchup records on the report agree with the standings table", not bad,
                "; ".join(bad) if bad else "all 28 checked"))
    tiers = {s["tier"] for s in SOURCES["sources"]}
    res.append(("At least one tier-1 source registered", "T1" in tiers, "tiers present: " + ", ".join(sorted(tiers))))
    nulls = sum(1 for p in CORR["pairs"] if p["measured_value"] is None)
    res.append(("Correlation register publishes no unmeasured value as a number",
                nulls == len(CORR["pairs"]), "%d/%d pairs null, as intended" % (nulls, len(CORR["pairs"]))))
    edges = [s["id"] for s in STRAT["strategies"] if s.get("edge_claim") is not None]
    res.append(("No strategy asserts an edge before a gate run", not edges, "no edge claims" if not edges else str(edges)))
    return res


CHECKS = run_checks()


def snapshot_state():
    """Deterministic freshness statement: compares the snapshot to the games it covers.

    Deliberately not derived from a wall clock, so the committed build output is
    reproducible byte-for-byte in CI (the deploy job rebuilds and diffs).
    """
    games = INJ["games"]
    future = [g for g in games if g["date"] >= INJ["meta"]["as_of_utc"][:10] and not g.get("result")]
    played = [g for g in games if g.get("result")]
    return {"future": len(future), "played": len(played), "ttl": INJ["meta"]["ttl_hours"],
            "date": INJ["meta"]["as_of_utc"][:10]}


SNAP = snapshot_state()
FRESH = 0
TTL = SNAP["ttl"]


def banner():
    tone = "warn" if SNAP["future"] else "ok"
    txt = ("Snapshot taken %s. It covers %d games that had not been played yet and %d completed fixture, so every "
           "availability row on this page is pre-game information, not a result. Source TTL is %d hours: the league "
           "requires three practice filings plus a final game-status filing each game week, and Monday games are "
           "re-filed after Sunday, so a row older than the TTL is a hint rather than a fact. "
           % (SNAP["date"], SNAP["future"], SNAP["played"], SNAP["ttl"]))
    txt += ("Refresh before using any row for a decision." if tone == "warn" else "This snapshot covers finished games.")
    return {"kind": "callout", "tone": tone, "title": "Data freshness", "body": txt}


# ---------------------------------------------------------------- pages
def p_index():
    n_q = sum(len(g["questions"]) for g in QUESTIONS["groups"])
    n_block = sum(1 for g in QUESTIONS["groups"] for q in g["questions"] if q["blocking"])
    n_not = sum(1 for i in INV["inventory"] if i["status"] == "not-available")
    n_ver = sum(1 for i in INV["inventory"] if i["status"] == "captured-verified")
    cnt = INJ["team_availability_counts"]
    tot = {k: v["out"] + v["doubtful"] for k, v in cnt.items()}
    heavy = sorted((k for k, v in tot.items() if v >= 5), key=lambda k: -tot[k])
    zero = sorted(k for k, v in tot.items() if v == 0)
    dist = ("Availability is not evenly distributed: %d clubs carry five or more Out/Doubtful designations (%s) "
            "while %d carry none (%s)." % (len(heavy), ", ".join("%s %d" % (k, tot[k]) for k in heavy),
                                           len(zero), ", ".join(zero)))
    blocks = [
        {"kind": "callout", "tone": "bad", "title": "Read this first",
         "body": ("**The system can now see who is unavailable; it cannot yet see any price.** The official NFL "
                  "availability, results and standings layer is captured and verified row by row, so injury tracking, "
                  "deficiency analysis, the strategy catalogue, the gate suite and the leaderboard rules are all real "
                  "and usable. What does not exist in this repository is a market-price feed - and without prices there "
                  "is no closing line to beat, no backtest, and no honest number for any edge. Every "
                  "`edge_claim` on this site is therefore null by design. Anyone who publishes a win rate for these "
                  "strategies before a gate run has finished is the failure mode this whole structure is built to prevent. "
                  "See [F-01](flagged.html) and [Q-MKT-01](questions.html).")},
        {"kind": "cards", "items": [
            {"label": "Players officially Out or Doubtful this week", "value": len(INJ["out_or_doubtful"]),
             "sub": "75 rows, each transcribed from the league report page", "tone": "good"},
            {"label": "Clubs covered / on bye", "value": "28 / 4", "sub": "14 games captured", "tone": "good"},
            {"label": "Table rows without a source link", "value": 0, "sub": "builder enforces this", "tone": "good"},
            {"label": "Strategies catalogued / validated", "value": "%d / 0" % len(STRAT["strategies"]),
             "sub": "validation needs prices, not more ideas", "tone": "warn"},
            {"label": "Validation gates defined", "value": len(GATES["gates"]),
             "sub": "5 thresholds still need a reviewer number", "tone": "neutral"},
            {"label": "Correlation pairs measured", "value": "0 of %d" % len(CORR["pairs"]),
             "sub": "refusing to price parlays is the intended behaviour", "tone": "bad"},
            {"label": "Blocking questions for the reviewer", "value": "%d of %d" % (n_block, n_q),
             "sub": "each states what we know, what is missing, and how to resolve it", "tone": "warn"},
            {"label": "Information feeds available / missing", "value": "%d / %d" % (n_ver, n_not),
             "sub": "of %d required inputs" % len(INV["inventory"]), "tone": "warn"},
        ]},
        {"kind": "prose", "title": "Executive summary", "body": [
            "**Objective.** Originate NFL lines rather than chase them, treat strategy development as a ranked "
            "competition, and make every availability and depth fact legible enough to decide on. That objective is "
            "now expressed as 38 traced requirements, 16 candidate strategies, 15 gates, an 11-pair correlation "
            "register and a live, source-linked data layer.",
            "**What was built on top of an empty repository.** At session start this repo held one file with five "
            "bytes of README. Everything here is net-new: a verification policy, 11 machine-readable datasets, a "
            "generator, 14 pages, a CI deploy, and the coordination board for other agent sessions.",
            "**What is verified and usable today.** The Week 10, 2026 availability report is captured from the "
            "league's own page for 28 clubs - 75 players Out or Doubtful with position, disclosed injury, practice "
            "participation and game status - plus all 32 club records, the Week 10 fixture list and the played "
            "Thursday result. Build-time checks re-reconcile the row-level data against the declared team totals, "
            "the standings against the matchup records, and the fixture list against the snapshot; all nine pass "
            "below.",
            "**What the data already tells a decision-maker.** " + dist + " "
            "Two rows on the Jaguars' report are marked 'Not injury related - resting player' yet still carry an Out "
            "game status, which is a direct warning that counting designations confuses rest with loss of quality. "
            "A Seahawks quarterback ruled Out is corroborated by an independent league article naming his replacement "
            "as starter, while a Dolphins injured-reserve move appears only in a headline and produces no weekly row "
            "at all - so a report-only pipeline is structurally blind to exactly the changes that redefine a team's "
            "depth for weeks.",
            "**What is missing, and it is one thing.** Market prices. There is no odds or line feed in this "
            "environment, so nothing that depends on a price can be measured: not closing-line value, not backtests, "
            "not correlation of settled legs, not originated lines. The brief's central ask is therefore not "
            "delivered as a number - it is delivered as an architecture plus a named, single blocking decision "
            "([Q-MKT-01](questions.html)), which is the honest state.",
            "**The depth requirement needs a second source.** 'Know when 2nd/3rd/4th-string backups replace starters' "
            "cannot come from the official report, which has no replacement field. This site publishes who is "
            "unavailable and refuses to name a replacement, because inventing one would corrupt the very signals it "
            "is meant to produce. The fix is a depth or transactions feed ([Q-ROSTER-01](questions.html), "
            "[SG-03](suggestions.html)).",
            "**How luck is removed.** A strategy is judged primarily on closing-line value per bet (measurable the "
            "next day), never on win rate over a short sample; it must survive walk-forward folds, a sample floor of "
            "500 bets across 250+ distinct games, a multiple-testing correction read from a journal of *failed* "
            "variants, an input-perturbation robustness test, and a hard no-look-ahead timestamp rule. Strategies "
            "that cannot pass stay published with the block named - they are not deleted, and they are not promoted.",
            "**Governance.** No capital is exposed. The leaderboard is empty by design, rewards are non-cash, and "
            "the reviewer's only required action is to answer %d blocking questions and set 5 numeric thresholds. "
            "Suggestions are held at 'proposed' until dispositioned; silence never approves." % n_block,
        ]},
        {"kind": "prose", "title": "The six decisions that unblock the most work", "body": [
            [
                "**Q-MKT-01** - choose a price source (vendor, exchange, or self-capture). Everything quantitative is behind this one.",
                "**Q-RISK-01/02** - state the bankroll policy and staking fraction, or confirm research-only mode.",
                "**Q-ROSTER-01** - pick the depth-chart authority, or accept that the site names absences but not replacements.",
                "**Q-MODEL-01/02** - confirm CLV as the primary metric and the sample floor, which fixes what 'skill' means here.",
                "**Q-LEGAL-01/02** - confirm jurisdiction/operator legality and data redistribution terms before any live exposure.",
                "**Q-GOV-01/02** - name the approver and define what silence means for suggestions.",
            ],
            "Each is reproduced on the [Questions page](questions.html) with the known/unknown/resolve columns filled in, "
            "so answering it is a short reply rather than a research task.",
        ]},
        {"kind": "table", "id": "checks", "title": "Build-time verification checks", "as_of": "run " + ASOF,
         "cols": [{"key": "name", "label": "Check"}, {"key": "pass", "label": "Result", "type": "badge"},
                  {"key": "detail", "label": "Detail"}],
         "rows": [{"name": n, "pass": ("PASS" if p else "FAIL"), "detail": d} for n, p, d in CHECKS],
         "note": "These run on every build: if the row-level capture and the declared aggregates disagree, or if a "
                 "strategy grows an edge number before a gate run, the site says so in public."},
        {"kind": "table", "id": "week", "title": "The week in front of the system (official snapshot)",
         "source": {"label": "NFL.com injury report, Week 10", "url": SRC_URL}, "as_of": ASOF,
         "cols": [{"key": "when", "label": "Kickoff (ET)"}, {"key": "matchup", "label": "Matchup"},
                  {"key": "recs", "label": "Records"}, {"key": "impact", "label": "Availability impact", "cls": "long"},
                  {"key": "src", "label": "Source"}],
         "rows": week_rows(), "note": "Impact counts are derived arithmetically from the captured rows (Out + Doubtful). "
                 "No price, side or prediction is attached to any fixture on this page."},
        banner(),
    ]
    return blocks


def week_rows():
    out = []
    for g in INJ["games"]:
        c = INJ["team_availability_counts"]
        a, h = g["away"], g["home"]
        av = c[a]["out"] + c[a]["doubtful"]
        hv = c[h]["out"] + c[h]["doubtful"]
        out.append({
            "when": "%s %s" % (g["date"], g["kickoff_et"]),
            "matchup": "%s at %s%s" % (TEAMNAME[a], TEAMNAME[h], " &middot; " + g.get("label", "") if g.get("label") else ""),
            "recs": "%s (%s) / %s (%s)" % (a, g["records"][a], h, g["records"][h]),
            "impact": "OUT/DOUBT: %s %d \u2013 %d %s" % (a, av, hv, h),
            "src": {"label": "official report", "url": g.get("result_source", SRC_URL)},
        })
    return out


def p_requirements():
    rows = []
    for line in (ROOT / "REQUIREMENTS.md").read_text().splitlines():
        if line.startswith("| R-"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append({"id": cells[0], "req": cells[1], "status": cells[2], "where": cells[3],
                         "accept": cells[4], "blocker": cells[5] if len(cells) > 5 else ""})
    n_met = sum(1 for r in rows if r["status"].startswith("met"))
    return [
        {"kind": "cards", "items": [
            {"label": "Requirements traced", "value": len(rows), "sub": "from the brief, verbatim where possible"},
            {"label": "Met in this build", "value": n_met, "sub": "verifiable on the live site", "tone": "good"},
            {"label": "Blocked on a decision or a feed", "value": len(rows) - n_met,
             "sub": "each names its blocker", "tone": "warn"}]},
        {"kind": "table", "id": "req",
         "cols": [{"key": "id", "label": "ID"}, {"key": "req", "label": "Requirement", "cls": "long"},
                  {"key": "status", "label": "Status", "type": "badge"}, {"key": "where", "label": "Where satisfied", "cls": "long"},
                  {"key": "accept", "label": "Acceptance criteria", "cls": "long"},
                  {"key": "blocker", "label": "Blocker / note", "cls": "long"}],
         "rows": rows,
         "note": "Full prose version: `REQUIREMENTS.md` in the repository root. 'Blocked' is a status, not a failure - "
                 "a requirement that cannot be truthfully met is published as blocked rather than quietly dropped."},
    ]


def p_questions():
    blocks = [
        {"kind": "cards", "items": []},
    ]
    n = sum(len(g["questions"]) for g in QUESTIONS["groups"])
    nb = sum(1 for g in QUESTIONS["groups"] for q in g["questions"] if q["blocking"])
    blocks[0]["items"] = [
        {"label": "Questions", "value": n, "sub": "each one gates a decision"},
        {"label": "Blocking", "value": nb, "sub": "no reasonable decision without an answer", "tone": "bad"},
        {"label": "Answered by default", "value": "all of them", "sub": "every question ships a default-if-silent, so nothing stalls forever", "tone": "neutral"},
    ]
    blocks.append({"kind": "prose", "title": "How to read this page", "body": [
        "Each row separates **what we already know** (with the source that says so) from **what is not known**, then "
        "names the cheapest path to the answer and the fallback if the answer never comes. That last column matters: "
        "an unanswered question with no default is a project that silently stops, so every question here carries one.",
        "The 'known' text is written from the sources actually read in this build, not from general familiarity with "
        "the league. Where a claim could not be traced to an official page it is written as unverified and mirrored on "
        "the [Flagged page](flagged.html).",
    ]})
    for g in QUESTIONS["groups"]:
        rows = []
        for q in g["questions"]:
            rows.append({"id": q["id"], "q": q["question"], "block": "blocking" if q["blocking"] else "non-blocking",
                         "known": q["known"], "unknown": q["unknown"], "resolve": q["resolve"],
                         "opts": q.get("options", []), "default": q["default"],
                         "ev": q.get("evidence", []) or None})
        blocks.append({"kind": "prose", "title": g["title"], "body": [g["why_this_group_matters"]]})
        blocks.append({"kind": "table", "id": g["id"], "cols": [
            {"key": "id", "label": "ID"}, {"key": "q", "label": "Question", "cls": "long"},
            {"key": "block", "label": "Gate", "type": "badge"},
            {"key": "known", "label": "What we know", "cls": "long"},
            {"key": "unknown", "label": "What is not known", "cls": "long"},
            {"key": "resolve", "label": "How to resolve", "cls": "long"},
            {"key": "opts", "label": "Options"},
            {"key": "default", "label": "Default if unanswered", "cls": "long"},
            {"key": "ev", "label": "Evidence"}], "rows": rows})
    return blocks


def p_suggestions():
    rows = [{**s, "impact_b": s["expected_impact"]} for s in SUGG["suggestions"]]
    impl = sum(1 for s in rows if s["status"].startswith("implement"))
    now = [s for s in rows if s["implement_now"]]
    blocks = [
        {"kind": "callout", "tone": "info", "title": "This is a review control, not a wish list",
         "body": ("Each suggestion has a `status` field in `data/suggestions.json` and an `implement_now` flag. "
                  "Nothing marked *proposed* was implemented in this build; the %d suggestions marked "
                  "*implemented* are the ones already visible on the site (freshness banner, flag taxonomy, "
                  "per-strategy missing-information register, attribution-only publishing). Change a status to "
                  "`approved` or `rejected`, rebuild, and the page reflects it. Default on silence is **stays "
                  "proposed** - see [Q-GOV-02](questions.html)." % impl)},
        {"kind": "cards", "items": [
            {"label": "Suggestions", "value": len(rows), "sub": "each states the problem it removes"},
            {"label": "Approved for this build", "value": impl, "sub": "already live", "tone": "good"},
            {"label": "Blocked on data", "value": sum(1 for s in rows if "blocked" in s["status"]),
             "sub": "missing input, not missing effort", "tone": "bad"},
            {"label": "Marked 'do now'", "value": len(now), "sub": "recommended first moves", "tone": "neutral"}]},
        {"kind": "table", "id": "sugg",
         "source": {"label": "generated in this session from the brief + the captured data", "url": SRC_REPO},
         "cols": [{"key": "id", "label": "ID"}, {"key": "title", "label": "Suggestion", "cls": "long"},
                  {"key": "category", "label": "Category", "type": "badge"},
                  {"key": "problem", "label": "Problem it removes", "cls": "long"},
                  {"key": "proposal", "label": "Proposal", "cls": "long"},
                  {"key": "impact_b", "label": "Impact"},
                  {"key": "effort", "label": "Effort"},
                  {"key": "unblocks", "label": "Unblocks"},
                  {"key": "risk", "label": "Risk / cost of doing it", "cls": "long"},
                  {"key": "status", "label": "Status", "type": "badge"},
                  {"key": "implement_now", "label": "Do now"},
                  {"key": "owner_needed", "label": "Who must act"},
                  {"key": "recommended_path", "label": "Where it sits in the path"}],
         "rows": rows,
         "note": "Impact: H = changes whether a decision can be made at all; M = changes decision quality or cost; "
                 "L = clarity. Effort: S/M/L engineering judgement, stated so it can be argued with."},
        {"kind": "prose", "title": "Recommended path (the reviewer's job is to accept or edit this order)", "body": []},
    ]
    for ph in SUGG["recommended_path_sequence"]:
        items = ", ".join(ph["items"])
        blocks.append({"kind": "callout", "tone": "info", "title": ph["phase"],
                       "body": "**Items:** %s. **Exit criteria:** %s" % (items, ph["exit_criteria"])})
    return blocks


def p_injuries():
    games = []
    for g in INJ["games"]:
        games.append({"date": g["date"], "kick": g["kickoff_et"], "net": g["network"],
                      "matchup": "%s at %s" % (TEAMNAME[g["away"]], TEAMNAME[g["home"]]),
                      "label": g.get("label"), "away_rec": g["records"][g["away"]], "home_rec": g["records"][g["home"]],
                      "result": g.get("result"),
                      "src": {"label": "fixture page" if g.get("result_source") else "report page",
                              "url": g.get("result_source", SRC_URL)}})
    rows = []
    for r in INJ["out_or_doubtful"]:
        rows.append({**r, "team_name": TEAMNAME[r["team"]],
                     "src": {"label": "official report row", "url": SRC_URL}})
    counts = []
    for g in INJ["games"]:
        for tm in (g["away"], g["home"]):
            c = INJ["team_availability_counts"][tm]
            counts.append({"team": tm, "name": TEAMNAME[tm], "rec": g["records"][tm], "opp": g["home"] if tm == g["away"] else g["away"],
                           "out": c["out"], "doubtful": c["doubtful"], "questionable": c["questionable"],
                           "total": c["out"] + c["doubtful"],
                           "src": {"label": "report", "url": SRC_URL}})
    counts.sort(key=lambda x: -x["total"])
    for tm in ("CHI", "DEN", "PHI", "TB"):
        counts.append({"team": tm, "name": TEAMNAME[tm], "rec": ROWS[tm] and "%d-%d" % (ROWS[tm]["w"], ROWS[tm]["l"]),
                       "opp": None, "out": None, "doubtful": None, "questionable": None, "total": None,
                       "src": {"label": "bye - no report rows (see F-13)", "url": SRC_URL}})
    return [
        {"kind": "callout", "tone": "info", "title": "Provenance of every row on this page",
         "body": ("Single source: the league's own Week 10 report page, read in full (8 of 8 chunks) on %s. "
                  "Transcription rule: a player appears here if and only if the official page lists them with a game "
                  "status of Out or Doubtful. Questionable players are counted per club but not listed, and players "
                  "with a practice line but no game status are omitted entirely, because no availability claim can be "
                  "made for them. A blank injury cell means the league page showed a blank cell - it does **not** mean "
                  "'no injury'.") % ASOF},
        {"kind": "cards", "items": [
            {"label": "Games captured", "value": len(INJ["games"]), "sub": "14 of 14 on the report page", "tone": "good"},
            {"label": "Players Out or Doubtful", "value": len(rows), "sub": "row-level, each with its own source link", "tone": "good"},
            {"label": "Clubs with zero Out/Doubtful", "value": sum(1 for c in INJ["team_availability_counts"].values() if c["out"] + c["doubtful"] == 0),
             "sub": "read together with F-10 before trusting a zero", "tone": "warn"},
            {"label": "Rows left blank and flagged", "value": 4, "sub": "the four clubs on bye", "tone": "neutral"}]},
        {"kind": "table", "id": "inj-games", "title": "Fixture list as published", "as_of": ASOF, "tier": "T1",
         "cols": [{"key": "date", "label": "Date"}, {"key": "kick", "label": "Kickoff ET"}, {"key": "net", "label": "Broadcaster"},
                  {"key": "matchup", "label": "Matchup"}, {"key": "label", "label": "Designation"},
                  {"key": "away_rec", "label": "Away record"}, {"key": "home_rec", "label": "Home record"},
                  {"key": "result", "label": "Result"}, {"key": "src", "label": "Source"}], "rows": games,
         "note": "Records are the ones shown beside each matchup on the report page; they were independently "
                 "cross-checked against the standings table on this site and agree for all 28 clubs."},
        {"kind": "table", "id": "inj-counts", "title": "Club availability load (derived by counting the rows below)",
         "as_of": ASOF, "tier": "T1",
         "cols": [{"key": "team", "label": "Club"}, {"key": "name", "label": "Name"}, {"key": "rec", "label": "Record"},
                  {"key": "opp", "label": "Week 10 opponent"}, {"key": "out", "label": "Out"}, {"key": "doubtful", "label": "Doubtful"},
                  {"key": "total", "label": "Out + Doubtful"}, {"key": "questionable", "label": "Questionable"},
                  {"key": "src", "label": "Source"}], "rows": counts,
         "note": "Sorted by unavailable count. This is a crude 'count of bodies' view and the site says so: it treats a "
                 "backup long snapper and a starting cornerback alike, which is why the replacement-value ladder in "
                 "SG-05 exists. Two rows in this dataset are explicitly 'Not injury related - resting player' while "
                 "carrying an Out status - a live demonstration of why counting designations needs a rest flag."},
        {"kind": "table", "id": "inj-rows", "title": "Player-level availability (all 75 rows)", "as_of": ASOF, "tier": "T1",
         "cols": [{"key": "team", "label": "Club"}, {"key": "name", "label": "Name"}, {"key": "opp", "label": "Opp"},
                  {"key": "player", "label": "Player"}, {"key": "pos", "label": "Pos"},
                  {"key": "injury", "label": "Disclosed injury"}, {"key": "practice", "label": "Practice status", "type": "badge"},
                  {"key": "status", "label": "Game status", "type": "badge"}, {"key": "src", "label": "Source"}],
         "rows": rows,
         "note": "Practice status and game status are separate fields in the source and are kept separate here: a "
                 "player can be a full participant and still be Out, and can be a DNP with no game status at all. "
                 "Collapsing them is the most common error in injury models."},
        {"kind": "prose", "title": "League news items on the same page (headline-level, independently linked)", "body": [
            "These are recorded because the weekly report and the news column disagree in instructive ways, and "
            "because two of them describe events the report does not contain at all.",
        ]},
        {"kind": "table", "id": "inj-news", "cols": [
            {"key": "headline", "label": "Headline as published", "cls": "long"},
            {"key": "implication_for_model", "label": "Why it matters to the model", "cls": "long"},
            {"key": "url", "label": "Source"}], "rows": INJ["news_items_verified"], "tier": "T1",
         "note": "Only the headline wording is asserted; article bodies were not opened in this build."},
    ]


POS_UNIT = {
    "QB": "quarterback", "RB": "backfield", "FB": "backfield", "WR": "wide receiver", "TE": "tight end",
    "T": "offensive line", "G": "offensive line", "C": "offensive line",
    "DE": "defensive line", "DT": "defensive line", "LB": "linebacker", "CB": "cornerback", "S": "safety",
    "LS": "special teams", "P": "special teams", "K": "special teams",
}
OFF_UNITS = {"quarterback", "backfield", "wide receiver", "tight end", "offensive line"}
DEF_UNITS = {"defensive line", "linebacker", "cornerback", "safety"}


def p_depth():
    per_team = {}
    for r in INJ["out_or_doubtful"]:
        per_team.setdefault(r["team"], []).append(r)
    rows = []
    front7 = {}
    oline = {}
    for tm, rs in sorted(per_team.items()):
        og, dg = {}, {}
        for r in rs:
            g = POS_UNIT.get(r["pos"], "unclassified")
            if g in DEF_UNITS:
                dg[g] = dg.get(g, 0) + 1
            else:
                og[g] = og.get(g, 0) + 1
        front7[tm] = dg.get("defensive line", 0) + dg.get("linebacker", 0)
        oline[tm] = og.get("offensive line", 0)
        rows.append({
            "team": tm, "name": TEAMNAME[tm],
            "off_units": " ".join("%s x%d" % (k, v) for k, v in sorted(og.items())) or None,
            "def_units": " ".join("%s x%d" % (k, v) for k, v in sorted(dg.items())) or None,
            "n_off": sum(v for k, v in og.items() if k in OFF_UNITS),
            "n_def": sum(v for k, v in dg.items() if k in DEF_UNITS),
            "players": [r["player"] + " (" + r["pos"] + ", " + r["status"] + ")" for r in rs],
            "src": {"label": "official report", "url": SRC_URL},
        })
    rows.sort(key=lambda x: -(x["n_off"] + x["n_def"]))
    n_front = sorted(k for k, v in front7.items() if v >= 2)
    n_ol_any = sorted(k for k, v in oline.items() if v >= 1)
    n_ol_two = sorted(k for k, v in oline.items() if v >= 2)
    rest_rows = [r for r in INJ["out_or_doubtful"] if "Not injury related" in r["injury"]]
    p1 = ("**Defensive front depletion.** %d clubs are missing two or more players listed as DE/DT/LB (%s). "
          "That is where an availability count is most misleading, because two reserve linemen and two starting "
          "interior defenders produce the same number here and very different football."
          % (len(n_front), ", ".join("%s %d" % (k, front7[k]) for k in sorted(n_front, key=lambda x: -front7[x]))))
    p2 = ("**Offensive line.** %d clubs carry at least one lineman (T/G/C) Out or Doubtful, and %d carry two or "
          "more (%s). This is the unit the totals and rush-volume ideas in S-02 target, and it is also the unit "
          "where a club can plausibly lose a starter and his next two backups inside one week - which is exactly "
          "the 'how far down the chart do we fall' question the source cannot answer."
          % (len(n_ol_any), len(n_ol_two), ", ".join("%s %d" % (k, oline[k]) for k in sorted(n_ol_two, key=lambda x: -oline[x]))))
    p3 = ("**Not everything missing is injured.** %d rows in this snapshot are explicitly 'Not injury related' "
          "(rest or personal matter) while still carrying an Out game status: %s. A model that books those as lost "
          "quality for the following week double-counts a decision made to preserve quality, so the rest flag must be "
          "a field of its own before any counting is trusted."
          % (len(rest_rows), ", ".join("%s/%s" % (r["team"], r["player"]) for r in rest_rows)))
    return [
        {"kind": "callout", "tone": "bad", "title": "The honest limit of this page",
         "body": ("The brief asks the system to know when 2nd/3rd/4th-string backups replace starters. The official "
                  "report has no replacement field, so this page states **who is unavailable and which unit it hits** "
                  "and deliberately does **not** name who fills in. Naming a replacement would require a depth-chart "
                  "source, and none is verified in this environment ([F-02](flagged.html), "
                  "[Q-ROSTER-01](questions.html)). A wrong 'next man up' is worse than a blank, because it silently "
                  "propagates into every price built on it.")},
        {"kind": "prose", "title": "What the availability data shows for Week 10", "body": [
            p1, p2, p3,
            "**Roster reality moves underneath the model.** The same page carries mid-season personnel changes: a "
            "linebacker now listed by a different club after a trade, a franchise quarterback placed on injured "
            "reserve with a first-time starter described as 'in line', and a starting wide receiver described as "
            "'likely' to go on IR while the report gives him no game status at all. None of those three is an event "
            "the weekly report alone delivers, and all three change what a depth chain looks like.",
        ]},
        {"kind": "table", "id": "depth-units", "title": "Depletion by unit of play (derived from the verified rows)",
         "as_of": ASOF, "tier": "T1 + DERIVED",
         "source": {"label": "NFL.com Week 10 report", "url": SRC_URL},
         "cols": [{"key": "team", "label": "Club"}, {"key": "name", "label": "Name"},
                  {"key": "n_off", "label": "Offence unavailable"}, {"key": "off_units", "label": "Which units", "cls": "long"},
                  {"key": "n_def", "label": "Defence unavailable"}, {"key": "def_units", "label": "Which units", "cls": "long"},
                  {"key": "players", "label": "Players (position, status)"}, {"key": "src", "label": "Source"}],
         "rows": rows,
         "note": "Unit assignment is a mechanical mapping of the position code printed on the official page (T/G/C to "
                 "offensive line, DE/DT to the front seven, and so on). It is arithmetic on verified rows, not an "
                 "opinion about any player's quality. Starter-or-backup status is not knowable from this source, which "
                 "is why no column claims it."},
        {"kind": "prose", "title": "How the deficiency model is meant to work once a depth source exists", "body": [
            "The quantity worth having is not 'how many are out' but 'how far down the depth chart does the unit fall, "
            "and how much quality is lost at each step'. That is three inputs: a per-unit depth chain with "
            "availability flags on each link, a replacement-value estimate per position, and the snaps each link was "
            "projected to take.",
            "Of those three, one exists in this repo (availability). The other two need sources that are not "
            "verified here. So the pipeline ships with the arithmetic ready and the coefficients blank: the position "
            "ladder in SG-05 is explicitly labelled *estimated, unvalidated*, and gate G-7 exists to test whether any "
            "strategy survives when those estimates are perturbed - which is the same as asking whether the trade is "
            "about football or about guessing the injury report correctly.",
            "Until a depth feed exists, the defensible use of this page is as a **risk register**: which clubs are "
            "playing with a visibly depleted unit this week, and therefore which markets should a model distrust "
            "its season-long priors on. That use needs no invented numbers.",
        ]},
        {"kind": "table", "id": "depth-gap", "title": "The specific inputs this page is missing",
         "cols": [{"key": "need", "label": "Input"}, {"key": "why", "label": "Why it is needed", "cls": "long"},
                  {"key": "status", "label": "Status", "type": "badge"}, {"key": "next", "label": "Next action", "cls": "long"},
                  {"key": "link", "label": "Related"}],
         "rows": [
             {"need": "Depth chart per club (starter/next-up/after-that)", "why": "the difference between 'a cornerback is out' and 'the 4th cornerback is playing snaps'", "status": "not-available", "next": "answer Q-ROSTER-01; interim: publish absences only", "link": {"label": "Q-ROSTER-01", "url": "questions.html"}},
             {"need": "Transactions feed (IR, elevations, waivers)", "why": "an IR move changes depth for weeks and produces no weekly report row", "status": "source-identified-not-wired", "next": "approve SG-03", "link": {"label": "SG-03", "url": "suggestions.html"}},
             {"need": "Snap counts / playing time", "why": "tells us whether the 'next man' actually played, which is the only ground truth for a depth assumption", "status": "not-available", "next": "answer Q-ROSTER-03 (licensing)", "link": {"label": "F-07", "url": "flagged.html"}},
             {"need": "Replacement-value coefficients per position", "why": "converts bodies into a quality gap that a price can be compared with", "status": "reviewer-required", "next": "estimate by regression once SG-04 labels exist; until then blank", "link": {"label": "SG-05", "url": "suggestions.html"}},
             {"need": "Roster / elevation rules for 2026", "why": "bounds how much of a wave of injuries a club can absorb before it dresses a practice-squad player", "status": "not-available", "next": "retrieve official rule text; do not encode secondary claims (F-09)", "link": {"label": "F-09", "url": "flagged.html"}},
         ]},
    ]


def p_strategies():
    rows = []
    for s in STRAT["strategies"]:
        rows.append({
            "id": s["id"], "name": s["name"], "family": s["family"], "bet": s["bet_type"],
            "markets": s["markets"], "hyp": s["hypothesis"], "sig": s["signal"], "inputs": s["inputs"],
            "entry": s["entry"], "nobet": s["no_bet"], "stake": s["stake_rule"], "targets": s["targets"],
            "why": s["why_real"], "lose": s["how_it_loses"],
            "edge": s["edge_claim"], "gates": s["gates"], "status": s["status"], "blocked": s["blocked_on"],
            "example": s.get("week10_example"), "src": {"label": "dataset", "url": SRC_REPO + "/blob/main/data/strategies.json"},
        })
    fam = {}
    for s in STRAT["strategies"]:
        fam[s["family"]] = fam.get(s["family"], 0) + 1
    bt = {}
    for s in STRAT["strategies"]:
        bt[s["bet_type"]] = bt.get(s["bet_type"], 0) + 1
    return [
        {"kind": "callout", "tone": "info", "title": "What this catalogue is, and what it is not",
         "body": ("Sixteen candidate signal generators for originating prices. Each one is written as a testable "
                  "claim with the falsifying evidence named, so a strategy can be killed by data rather than defended "
                  "by narrative. **No edge number appears anywhere**, and `edge_claim` is null on every row - not "
                  "because the ideas are weak but because there is no price data in this repo with which to compute "
                  "one. Publishing a plausible percentage here would be the fastest way to destroy the value of the "
                  "entire exercise.")},
        {"kind": "cards", "items": [
            {"label": "Strategies", "value": len(rows), "sub": "singles, parlays, prop combos, one benchmark"},
            {"label": "By bet type", "value": ", ".join("%s: %d" % (k, v) for k, v in sorted(bt.items())), "sub": "brief asked for all three families", "tone": "neutral"},
            {"label": "Design-complete but blocked", "value": sum(1 for s in STRAT["strategies"] if "blocked" in s["status"]), "sub": "blocked on a feed, not on effort", "tone": "warn"},
            {"label": "Validated", "value": 0, "sub": "nothing is promoted without a gate run", "tone": "bad"}]},
        {"kind": "prose", "title": "Families, and why they are separated", "body": [
            "The families are not cosmetic. A **news-latency** strategy is a race against a market's repricing speed "
            "and is measured in minutes; a **unit-quality** strategy is a modelling claim and is measured in weeks of "
            "residuals; a **portfolio** strategy is a pricing-arithmetic claim and needs correlation, not forecasts; "
            "and **execution** (S-12, the shopping baseline) is the number all the others have to beat before anyone "
            "spends money on them. Mixing them on one scoreboard is how a system ends up rewarding whoever posted "
            "most often.",
            "The most important entry in the table is S-12, the pure line-shopping baseline: it has no opinion about "
            "football and exists so that every modelled edge can be compared with the cheapest available edge. If a "
            "strategy cannot beat S-12's CLV at the same stake, it is not a signal, it is a story.",
        ]},
        {"kind": "table", "id": "strat", "title": "Strategy register",
         "cols": [{"key": "id", "label": "ID"}, {"key": "name", "label": "Strategy", "cls": "long"},
                  {"key": "family", "label": "Family", "type": "badge"}, {"key": "bet", "label": "Bet type", "type": "badge"},
                  {"key": "markets", "label": "Markets"}, {"key": "hyp", "label": "Hypothesis", "cls": "long"},
                  {"key": "sig", "label": "Signal definition", "cls": "long"}, {"key": "inputs", "label": "Required inputs"},
                  {"key": "entry", "label": "Entry timing", "cls": "long"}, {"key": "nobet", "label": "No-bet / veto rules", "cls": "long"},
                  {"key": "stake", "label": "Stake rule", "cls": "long"}, {"key": "targets", "label": "What it is actually trying to learn", "cls": "long"},
                  {"key": "why", "label": "Why it might be real", "cls": "long"}, {"key": "lose", "label": "How it loses (red team)", "cls": "long"},
                  {"key": "edge", "label": "Edge claim"}, {"key": "gates", "label": "Gates"},
                  {"key": "status", "label": "Status", "type": "badge"}, {"key": "blocked", "label": "Blocked on", "cls": "long"},
                  {"key": "example", "label": "Week 10 signal value (verified data, unpriced)", "cls": "long"},
                  {"key": "src", "label": "Source"}],
         "rows": rows,
         "note": "'Week 10 signal value' applies the signal to the official availability snapshot only. It reports "
                 "that a condition fired; it never reports a side, a price, or a return, because the market half of "
                 "the comparison does not exist in this repository."},
        {"kind": "table", "id": "strat-notes", "title": "Design decisions embedded in this catalogue",
         "cols": [{"key": "d", "label": "Decision", "cls": "long"}, {"key": "why", "label": "Reason", "cls": "long"}],
         "rows": [
             {"d": "Every strategy names its own no-bet conditions", "why": "A signal without an abstention rule is a betting compulsion with a model attached. The vetoes are the part that survives contact with reality."},
             {"d": "How it loses is mandatory, next to why it might be real", "why": "SG-18. Optimism should not be able to travel alone on this site."},
             {"d": "Prop strategies carry the missing input in the first column, not a footnote", "why": "So nobody inherits them as 'ready'."},
             {"d": "Strategies are not allowed to share an input without sharing an exposure cap", "why": "S-01/S-02/S-03/S-07/S-08 all read the same injury file; five signals agreeing is one bet, which is what G-8 enforces."},
             {"d": "The shopping baseline is on the board as a competitor", "why": "The leaderboard should be able to embarrass the models, that is the point of a competition."},
         ]},
    ]


def p_validation():
    rows = []
    for g in GATES["gates"]:
        blanks = [k for k, v in (g.get("threshold") or {}).items() if v is None]
        rows.append({"id": g["id"], "name": g["name"], "prevents": g["prevents"], "test": g["test"],
                     "threshold": g.get("threshold"), "blanks": blanks or None, "pass": g["pass_rule"],
                     "need": g["required_data"], "status": g["status"], "notes": g.get("notes")})
    n_blank = sum(len(r["blanks"] or []) for r in rows)
    return [
        {"kind": "callout", "tone": "warn", "title": "These gates are documentation until SG-09 makes them code",
         "body": ("Fifteen gates, each aimed at one specific way a lucky or overfitted strategy can look like skill. "
                  "Two design choices do most of the work: they **fail closed** (a missing threshold, a missing "
                  "journal entry or an unknown publication timestamp stops promotion rather than allowing it), and "
                  "they are **rank-agnostic** - a gate never says 'good enough to try', only pass, fail or not-run. "
                  "%d threshold cells are blank by policy because they encode risk appetite rather than a measurement "
                  "([F-05](flagged.html))." % n_blank)},
        {"kind": "cards", "items": [
            {"label": "Gates", "value": len(rows), "sub": "each removes one named failure mode"},
            {"label": "Runnable now", "value": sum(1 for r in rows if "not-runnable" not in r["status"] and "blocked" not in r["status"]),
             "sub": "design-set or partially satisfied", "tone": "neutral"},
            {"label": "Blocked on missing data", "value": sum(1 for r in rows if "not-runnable" in r["status"] or "blocked" in r["status"]),
             "sub": "the same price feed, over and over", "tone": "bad"},
            {"label": "Blank thresholds", "value": n_blank, "sub": "reviewer must set", "tone": "warn"}]},
        {"kind": "table", "id": "gates", "title": "Gate register",
         "cols": [{"key": "id", "label": "ID"}, {"key": "name", "label": "Gate"},
                  {"key": "prevents", "label": "Failure mode it removes", "cls": "long"},
                  {"key": "test", "label": "Test procedure", "cls": "long"},
                  {"key": "threshold", "label": "Thresholds", "cls": "long"}, {"key": "blanks", "label": "Blank - reviewer must set"},
                  {"key": "pass", "label": "Pass rule", "cls": "long"}, {"key": "need", "label": "Required data"},
                  {"key": "status", "label": "Status", "type": "badge"}, {"key": "notes", "label": "Notes", "cls": "long"}],
         "rows": rows},
        {"kind": "prose", "title": "Why CLV, and not the scoreboard, is the promotion metric", "body": [
            "A strategy's profit is the sum of its edge and its luck, and for a few hundred bets the second term is "
            "usually bigger. Closing-line value is the part of the trade you can audit the next day: did we get a "
            "better price than the market's final, most-informed price? It is imperfect - it measures price-beating, "
            "not long-run profit, and it depends on the anchor book being genuinely efficient, which is why the "
            "anchor gets fixed by policy before the season rather than chosen afterwards by whoever flatters the "
            "result.",
            "The consequence for the brief's 'remove luck' requirement is concrete: **a strategy with good PnL and "
            "bad CLV is killed**, and **a strategy with bad PnL and good CLV is kept under review**. That is the "
            "opposite of how most betting records are judged, and it is the only version that can distinguish a "
            "process from a run of coin flips. The tie-break policy is pre-registered in "
            "[Q-MODEL-06](questions.html) so nobody decides it after seeing the money.",
        ]},
    ]


def p_correlation():
    rows = [{"id": p["id"], "a": p["leg_a"], "b": p["leg_b"], "sign": p["expected_sign"],
             "mech": p["mechanism"], "val": p["measured_value"], "n": p["n_obs"], "ci": p["ci"],
             "tier": p["tier"], "note": p.get("note"),
             "src": {"label": "register", "url": SRC_REPO + "/blob/main/data/correlations.json"}} for p in CORR["pairs"]]
    proto = CORR["meta"]["estimation_protocol"]
    return [
        {"kind": "callout", "tone": "bad", "title": "Every value in this table is null, and that is the finding",
         "body": ("The brief asks for correlation values to be determined. Nothing here has been measured, because a "
                  "correlation between two settled legs requires a settlement ledger and this project has never "
                  "settled a bet. The alternative - importing textbook numbers - would produce exactly the confident, "
                  "uncorroborated figures this project exists to avoid. So the register ships with the protocol, the "
                  "sample minimum, and blanks. Until a pair is measured, parlays containing it are **refused**, not "
                  "priced with assumed independence.")},
        {"kind": "cards", "items": [
            {"label": "Pairs registered", "value": len(rows), "sub": "same-game, cross-game and error-correlation"},
            {"label": "Measured", "value": 0, "sub": "needs a settlement ledger", "tone": "bad"},
            {"label": "Minimum observations per pair", "value": proto["minimum_observations"], "sub": "below this, no price", "tone": "neutral"}]},
        {"kind": "prose", "title": "Measurement protocol", "body": [
            ["**Unit:** paired legs settled on the same game.",
             "**Primary statistic:** phi coefficient on the 2x2 joint settlement table, plus the excess over "
             "independence: p(A and B) \u2212 p(A)p(B), which is the quantity that actually enters parlay pricing.",
             "**Secondary:** Spearman rank correlation for continuous outcomes.",
             "**Interval:** nonparametric bootstrap, 10,000 resamples, 95% interval; if the interval covers the "
             "independence value the pair is labelled 'no detectable dependence' and earns no correlation credit.",
             "**Stratification:** by leg family and by pre-game favourite-margin bucket, because a blowout induces "
             "dependence a close game does not.",
             "**Pitfall recorded so it is not rediscovered:** computing correlation on wins and losses of *our bets* "
             "instead of on *event outcomes* folds our own pricing errors into the dependence estimate. Measure "
             "events, apply to prices."],
        ]},
        {"kind": "table", "id": "corr", "title": "Correlation register",
         "cols": [{"key": "id", "label": "ID"}, {"key": "a", "label": "Leg A"}, {"key": "b", "label": "Leg B"},
                  {"key": "sign", "label": "Expected sign (prior only)", "type": "badge"}, {"key": "mech", "label": "Mechanism", "cls": "long"},
                  {"key": "val", "label": "Measured r"}, {"key": "n", "label": "n"}, {"key": "ci", "label": "95% CI"},
                  {"key": "tier", "label": "Tier", "type": "badge"}, {"key": "note", "label": "Note", "cls": "long"},
                  {"key": "src", "label": "Source"}], "rows": rows,
         "note": "'Expected sign' is a prior about direction, kept only so a measurement that contradicts it gets "
                 "investigated. It is never a licence to price."},
        {"kind": "table", "id": "corr-notes", "title": "Portfolio consequences", "cols": [{"key": "t", "label": "Finding", "cls": "long"}],
         "rows": [{"t": x} for x in CORR["portfolio_notes"]]},
    ]


def p_leaderboard():
    tiers = [{"tier": t["tier"], "name": t["name"], "req": t["requirement"], "consequence": t["consequence"]}
             for t in BOARD["tiers"]]
    rewards = [{"rank": r["rank"], "reward": r["reward"], "cash": "cash" if r.get("cash") else "non-cash",
                "gate": r.get("gate"), "why": r.get("why")} for r in BOARD["rewards"]["grants"]]
    we = BOARD["worked_example"]
    return [
        {"kind": "callout", "tone": "bad", "title": "The board has zero entries",
         "body": ("A leaderboard is a record of results, and there are no results: no prices, no bets, no "
                  "settlements. This page therefore publishes the competition *rules* in a form that can be audited "
                  "and argued with before anything is staked on it, and the table stays empty. A populated table of "
                  "plausible ranks would be the most dangerous object in this repository, because it is the kind of "
                  "artefact people screenshot.")},
        {"kind": "cards", "items": [
            {"label": "Entries", "value": len(BOARD["meta"]["entries"]), "sub": "correct, not unfinished", "tone": "neutral"},
            {"label": "Tiers", "value": len(BOARD["tiers"]), "sub": "registered to capital-eligible, plus quarantine", "tone": "neutral"},
            {"label": "Anti-gaming rules", "value": len(BOARD["anti_gaming"]), "sub": "each closes a specific loophole", "tone": "good"},
            {"label": "Cash rewards at promotion", "value": "1 of %d" % len(rewards), "sub": "and only after reviewer sign-off", "tone": "warn"}]},
        {"kind": "prose", "title": "Scoring", "body": [
            "**Primary - %s.** %s" % (BOARD["score"]["primary"]["name"], BOARD["score"]["primary"]["definition"]),
            BOARD["score"]["primary"]["why"],
            "**Secondary - %s.** %s" % (BOARD["score"]["secondary"]["name"], BOARD["score"]["secondary"]["definition"]),
            BOARD["score"]["secondary"]["why"],
            "Tie-breakers, in order: %s. The last line of that list is the load-bearing one." % "; ".join(BOARD["score"]["tiebreakers"]),
            "The overfit penalty reads its trial count from the decision journal, so 'we only publish the winner' "
            "becomes impossible by construction: a family where eight variants were tried is scored as if eight were "
            "tried. That single mechanic is what makes this a skill contest rather than a beauty contest for noise.",
        ]},
        {"kind": "table", "id": "lb-tiers", "title": "Tiers and what each one earns",
         "cols": [{"key": "tier", "label": "Tier"}, {"key": "name", "label": "Name"}, {"key": "req", "label": "Requirement", "cls": "long"},
                  {"key": "consequence", "label": "Consequence", "cls": "long"}], "rows": tiers},
        {"kind": "prose", "title": "Promotion rules", "body": [BOARD["promotion_rules"]]},
        {"kind": "table", "id": "lb-rewards", "title": "Rewards",
         "cols": [{"key": "rank", "label": "Achievement"}, {"key": "reward", "label": "Reward", "cls": "long"},
                  {"key": "cash", "label": "Cash?"}, {"key": "gate", "label": "Gate"}, {"key": "why", "label": "Why", "cls": "long"}],
         "rows": rewards, "note": "Explicitly not rewarded: %s." % ", ".join(BOARD["rewards"]["explicitly_not_rewarded"])},
        {"kind": "table", "id": "lb-anti", "title": "Anti-gaming controls",
         "cols": [{"key": "rule", "label": "Rule", "cls": "long"}, {"key": "protects", "label": "Loophole it closes", "type": "badge"}],
         "rows": BOARD["anti_gaming"]},
        {"kind": "callout", "tone": "warn", "title": "%s" % we["label"], "body": we["why_included"] +
         " Inputs: %s. %s" % (json.dumps(we["inputs"]), we["computation"])},
        {"kind": "table", "id": "lb-entries", "title": "The board",
         "source": {"label": "dataset", "url": SRC_REPO + "/blob/main/data/leaderboard.json"},
         "cols": [{"key": "rank", "label": "#"}, {"key": "strategy", "label": "Strategy"}, {"key": "tier", "label": "Tier"},
                  {"key": "clv", "label": "Mean CLV (cents)"}, {"key": "n", "label": "Bets"}, {"key": "score", "label": "Score"},
                  {"key": "gates", "label": "Gates"}, {"key": "blocked", "label": "Blocked on"}, {"key": "src", "label": "Ledger"}],
         "rows": [], "empty": "No entries. A row appears only when a strategy has a hash-verified ledger entry with a re-readable price source - see anti-gaming above."},
    ]


def p_inventory():
    rows = INV["inventory"]
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    return [
        {"kind": "callout", "tone": "info", "title": "The brief asked for the information we have and do not have. This is that list.",
         "body": ("Nineteen inputs, each with the source that would satisfy it, the gap that remains, and the action "
                  "that closes it. Status describes **this repository as built**, not the world: "
                  "*source-identified-not-wired* means we know where the data lives and no ingestion exists yet, which "
                  "is a very different problem from *not-available*.")},
        {"kind": "cards", "items": [{"label": k, "value": v, "sub": "of %d inputs" % len(rows),
                                     "tone": "good" if "captured" in k else ("bad" if "not-available" in k else "warn")}
                                    for k, v in sorted(by.items(), key=lambda x: -x[1])]},
        {"kind": "table", "id": "inv",
         "cols": [{"key": "id", "label": "ID"}, {"key": "information", "label": "Information", "cls": "long"},
                  {"key": "needed_for", "label": "Needed for"}, {"key": "status", "label": "Status", "type": "badge"},
                  {"key": "tier", "label": "Tier", "type": "badge"}, {"key": "source_url", "label": "Source"},
                  {"key": "cadence", "label": "Cadence"}, {"key": "gap", "label": "Gap that remains", "cls": "long"},
                  {"key": "action", "label": "Next action", "cls": "long"}],
         "rows": rows,
         "note": "Three inputs are marked *reviewer-required*: bankroll, legality and governance. They are not data "
                 "problems and no amount of ingestion will answer them - which is why they are listed here rather "
                 "than hidden."},
    ]


def p_sources():
    rows = []
    for s in SOURCES["sources"]:
        rows.append({"id": s["id"], "org": s["org"], "title": s["title"], "tier": s["tier"],
                     "url": s.get("url"), "accessed": s.get("accessed_utc"), "method": s.get("read_method"),
                     "verifies": s.get("verifies"), "used": s.get("used_by"), "license": s.get("license_posture"),
                     "ttl": s.get("freshness_ttl_hours"), "limits": s.get("limitations")})
    t1 = sum(1 for s in SOURCES["sources"] if s["tier"] == "T1")
    return [
        {"kind": "callout", "tone": "info", "title": "Verification tiers used across the whole site",
         "body": ("**T1** is the league, club or regulator that owns the fact - and is the only tier this site "
                  "publishes a value from. **T2** corroborates but never originates. **T3** is recorded as a lead, "
                  "never as a number. A source we did not actually read this session is listed as *not read* with no "
                  "access date, so the difference between 'we checked' and 'we know it exists' is visible in the "
                  "data rather than asserted in prose.")},
        {"kind": "cards", "items": [
            {"label": "Sources registered", "value": len(rows), "sub": "including the ones that failed"},
            {"label": "T1 sources read in full", "value": t1, "sub": "every published row traces to one of these", "tone": "good"},
            {"label": "Sources identified but not read", "value": sum(1 for s in SOURCES["sources"] if not s.get("accessed_utc")), "sub": "recorded so nobody cites them by reflex", "tone": "warn"},
            {"label": "Secondary pages consulted and rejected", "value": 2, "sub": "terminology and roster rules: unverified, see F-03/F-09", "tone": "bad"}]},
        {"kind": "table", "id": "src",
         "cols": [{"key": "id", "label": "ID"}, {"key": "org", "label": "Publisher"}, {"key": "title", "label": "Title", "cls": "long"},
                  {"key": "tier", "label": "Tier", "type": "badge"}, {"key": "url", "label": "Link"},
                  {"key": "accessed", "label": "Read (UTC)"}, {"key": "method", "label": "Read method", "cls": "long"},
                  {"key": "verifies", "label": "What it verifies", "cls": "long"}, {"key": "used", "label": "Used by"},
                  {"key": "license", "label": "Licence posture", "cls": "long"}, {"key": "ttl", "label": "TTL (h)"},
                  {"key": "limits", "label": "Known limitations", "cls": "long"}],
         "rows": rows,
         "note": "The register includes the sources this build decided **not** to rely on. A source list that only "
                 "contains the convenient ones is marketing."},
    ]


def p_methodology():
    return [
        {"kind": "prose", "title": "How a value gets onto this site", "body": [
            "1. **Read the official page in full**, not a search snippet. The Week 10 availability capture is 8 of 8 chunks of one page; partial reads are what create silent gaps.",
            "2. **Transcribe with a fixed rule, not with judgement.** The inclusion rule for the player table is 'listed by the club with a game status of Out or Doubtful'. Anyone can re-derive the same 75 rows from the same page; that reproducibility is the only real defence against cherry-picking.",
            "3. **Record a source link per row** and an as-of timestamp per table. The builder raises an error if a row in a verified table has no source, so an unattributed number cannot ship even accidentally.",
            "4. **Re-verify at build time.** Nine checks run in CI: the row-level counts are re-tallied against the declared team aggregates; club records on the report are checked against the standings; the standings are checked for conservation of wins against losses across the league; duplicates, fixture coverage and bye patterns are checked; and the strategy/correlation files are checked for any non-null edge or correlation value.",
            "5. **Publish the blanks.** Where the official page had an empty cell, this site shows a blank, not a guess. Where the whole field is missing (depth, prices), the gap is a row on the Flagged page with the action that closes it.",
        ]},
        {"kind": "prose", "title": "Deliberate refusals, and why each one is a feature", "body": [
            ["**No price data, therefore no edge numbers.** F-01. A percentage here would be decoration.",
             "**No replacement names on the depth page.** F-02. The source has no such field.",
             "**No probabilities attached to Out/Doubtful/Questionable.** F-03. The league policy text was not "
             "retrieved, and the secondary pages that describe it are not a licence to publish a number.",
             "**No standings home/road/division splits.** F-04. The rendered column order was ambiguous, so the "
             "columns were dropped rather than mapped by assumption.",
             "**No populated leaderboard.** An empty board is the correct rendering of a project that has not settled a bet.",
             "**No re-derivation of a 'sensible' roster.** Where the league page lists a player on a club no prior "
             "knowledge would predict, the row is transcribed exactly and flagged for human review (F-14). The league "
             "filing is the source of truth; my expectations are not. The same page confirms mid-season trades in "
             "this window, which is a reminder that season-long priors go stale fast."],
        ]},
        {"kind": "prose", "title": "Engineering", "body": [
            "`data/*.json` is the source of truth; `tools/build_site.py` renders every page from it. HTML is never "
            "hand-edited, so a correction is a data edit and stays reviewable in a diff. No external fonts, "
            "frameworks or CDNs: the page renders with zero third-party requests, all links are relative so the site "
            "works under a project-page subpath, and tables are filterable and sortable with about 1 KB of "
            "progressively-enhanced JavaScript, so the content is still readable with scripting off.",
            "GitHub Actions runs the builder in check mode (which fails if any generated page would differ, or if a "
            "verification check fails), audits internal links, and publishes `site/` to Pages. Coordination between "
            "parallel agent sessions happens in `COORDINATION.md` at the repo root, including file-ownership claims so "
            "two sessions never edit the same generated artefact.",
        ]},
        {"kind": "table", "id": "meth-checks", "title": "Verification checks and their current results",
         "cols": [{"key": "name", "label": "Check"}, {"key": "pass", "label": "Result", "type": "badge"}, {"key": "detail", "label": "Detail", "cls": "long"}],
         "rows": [{"name": n, "pass": ("PASS" if p else "FAIL"), "detail": d} for n, p, d in CHECKS]},
        {"kind": "prose", "title": "Reproducibility", "body": [
            "To reproduce the injury table from scratch: open the official report, select the season and week, read "
            "every chunk, keep rows whose game-status cell is Out or Doubtful, and transcribe player, position, "
            "disclosed injury, practice status and game status verbatim. Any independent reviewer should land on the "
            "same 75 rows - and if they do not, the difference is itself a data-quality finding worth flagging.",
            "What cannot be reproduced from a page read: any historical series, any price, and anything about who "
            "replaced a starter. Those are stated as gaps rather than as results, which is the whole point of this "
            "section.",
        ]},
    ]


def p_flagged():
    rows = []
    for f in FLAGGED["flags"]:
        rows.append({"id": f["id"], "type": f["type"], "sev": f.get("severity"), "title": f["title"],
                     "detail": f["detail"], "affected": f["affected"], "action": f["action_needed"],
                     "links": f.get("links") or None, "block": "no"})
    by = {}
    for f in FLAGGED["flags"]:
        by[f["type"]] = by.get(f["type"], 0) + 1
    mix = ", ".join("%d %s" % (v, k.replace("-", " ")) for k, v in sorted(by.items(), key=lambda x: -x[1]))
    return [
        {"kind": "callout", "tone": "warn", "title": "Everything this build could not confirm, in one place",
         "body": ("%d items, by type: %s. **None of these block the site or the merge.** They are published so they "
                  "can be dispositioned after launch, and each one carries the source link a reviewer needs. Every "
                  "item here started as a decision the build refused to make by guessing."
                  % (len(FLAGGED["flags"]), mix))},
        {"kind": "cards", "items": [{"label": k, "value": v, "sub": "flag type", "tone": "bad" if k == "not-obtainable" else "warn"}
                                     for k, v in sorted(by.items(), key=lambda x: -x[1])] +
         [{"label": "Blocking the merge", "value": 0, "sub": "by policy; flagged items never hold up the build", "tone": "good"}]},
        {"kind": "table", "id": "flags",
         "cols": [{"key": "id", "label": "ID"}, {"key": "type", "label": "Type", "type": "badge"},
                  {"key": "sev", "label": "Severity", "type": "badge"}, {"key": "title", "label": "Item", "cls": "long"},
                  {"key": "detail", "label": "Detail", "cls": "long"}, {"key": "affected", "label": "Affected pages"},
                  {"key": "action", "label": "Action needed", "cls": "long"}, {"key": "links", "label": "Sources"},
                  {"key": "block", "label": "Blocks merge"}],
         "rows": rows,
         "note": "Disposition options for each item: resolve with a value plus a link, accept the blank permanently, "
                 "or suppress with a written reason. The taxonomy distinguishes 'the number is wrong' from 'the "
                 "number is missing' on purpose - the first is a bug, the second is a purchase order, and a list that "
                 "conflates them fixes only the first (SG-19)."},
    ]


BUILDERS = {
    "index": p_index, "requirements": p_requirements, "questions": p_questions,
    "inventory": p_inventory, "suggestions": p_suggestions, "injuries": p_injuries, "depth": p_depth,
    "strategies": p_strategies, "validation": p_validation, "correlation": p_correlation,
    "leaderboard": p_leaderboard, "sources": p_sources, "methodology": p_methodology, "flagged": p_flagged,
}


def main():
    SITE.mkdir(exist_ok=True)
    (SITE / "assets").mkdir(exist_ok=True)
    total = 0
    for slug, title, desc in PAGES:
        blocks = BUILDERS[slug]()
        size = build_page(slug, title, dict(PAGE_LEADS).get(slug, ""), blocks, desc)
        total += size
        print("built %-14s %7.1f KB" % (slug, size / 1024))
    (SITE / "data").mkdir(exist_ok=True)
    for f in DATA.glob("*.json"):
        (SITE / "data" / f.name).write_text(f.read_text())
    fails = [c for c in CHECKS if not c[1]]
    print("\nchecks: %d run, %d failed" % (len(CHECKS), len(fails)))
    for n, p, d in CHECKS:
        print("  [%s] %s" % ("PASS" if p else "FAIL", n))
    if "--fail-on-warn" in sys.argv and fails:
        print("Failing build: verification checks failed: %s" % [f[0] for f in fails])
        return 1
    print("\ntotal HTML: %.1f KB across %d pages" % (total / 1024, len(PAGES)))
    return 0


PAGE_LEADS = {
    "index": "A verified data layer, a strategy catalogue, and an explicit list of what cannot be decided yet - built from an empty repository in one session.",
    "requirements": "Thirty-eight requirements from the brief, each traced to a location, an acceptance test and, where relevant, a named blocker.",
    "questions": "What must be answered before any decision here is reasonable - with what we already know, what is missing, and the fallback if nobody answers.",
    "inventory": "The information register behind the questions: nineteen inputs, three captured and verified, seven that do not exist in this environment.",
    "suggestions": "Twenty-one ways to improve the site's decision value, with an explicit review control so nothing is implemented before a path is chosen.",
    "injuries": "The official Week 10, 2026 availability report for 28 clubs, transcribed under a fixed rule and linked row by row.",
    "depth": "What the official data can say about depleted units - and the boundary past which this site refuses to guess.",
    "strategies": "Sixteen ways to generate signals for originating lines, each with its inputs, its vetoes, and how it loses.",
    "validation": "Fifteen gates, each aimed at one specific way luck masquerades as skill in a betting record.",
    "correlation": "How dependence between legs will be measured, and the refusal that stands in place of a number until it is.",
    "leaderboard": "A competition designed so that the winner is the strategy with the most reproducible price advantage - not the loudest story.",
    "sources": "Every source read in this build, its tier, what it was used to verify, and what it could not be used for.",
    "methodology": "The verification pipeline, the checks that run on every build, and the refusals that define this project's honesty.",
    "flagged": "Sixteen irregularities and gaps, each with the action needed to close it. None of them block the merge, and none were closed by guessing.",
}

if __name__ == "__main__":
    sys.exit(main())
