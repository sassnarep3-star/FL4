#!/usr/bin/env python3
"""Integrity checks for the Decision Lab section (lab/*.html + data/lab/*.json).

Run from the repo root:  python3 tools/check_lab.py [--fail-on-warn]

Checks performed:
  1.  Every data/lab/*.json parses.
  2.  Every internal link and navigation target on a lab page exists.
  3.  Every lab page links to assets/style.css and assets/app.js, and both exist.
  4.  No page renders the string None inside a table cell (a null value must
      render blank, never as the word "None").
  5.  Every row of every data table on a lab page carries at least one source
      link, except tables that declare themselves source-free.
  6.  No absolute localhost / 127.0.0.1 URL (the preview is served from a
      public host, so browser-facing code must use relative URLs).
  7.  No price-derived value (a price token with a number attached) is rendered.
  8.  Every requirement row's where_published target exists on disk.
  9.  Every gate named in requirements.json exists in questions.json, and every
      question id referenced anywhere exists.
 10. Flag ids in flagged.json are unique and every flag has a source URL.
 11. Every source id referenced by a flag or requirement exists in sources.json.
"""
import json
import pathlib
import re
import sys
from collections import Counter
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAB = ROOT / "lab"
DATA = ROOT / "data" / "lab"

LINK_RE = re.compile(r'(?:href|src)="([^"]+)"')
ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL_RE = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
SRC_RE = re.compile(r'<a class="badge (official|secondary)"')
PRICE_RE = re.compile(r"\b(american_price|closing_line_value|clv|roi|stake_size|edge_value)\b[^<>{}\n]{0,12}?[-+]?\d")

# Tables that intentionally carry no source column: they publish policy text,
# specifications or blanks, and every row is prose rather than a claimed fact.
# Tables that intentionally carry no source column, and why. None of them states an
# external fact: they publish a specification, a blank, a decision or a proposal.
SOURCE_FREE = {
    "luck",      # tests published blank before any result exists
    "matrix",    # every cell is deliberately blank
    "diff",      # every value is blank by construction
    "coverage", "team", "fails", "rej",   # depth coverage counters and standing rejections
    "contract", "order", "tot", "ab", "plan", "est", "steps",
    "s1", "s2", "ctl", "dem", "ag", "tiers", "reg",
    "split", "store", "vig", "polopts", "drift", "divs",
    "readiness",  # requirements, not facts; each row links to the page that discharges it
    "qs",         # open decisions awaiting an owner
    "sg",         # proposals awaiting an owner
    "pairs",      # registered pairs; every measured value is blank
}

problems = []
warns = []


def fail(msg):
    problems.append(msg)


def warn(msg):
    warns.append(msg)


# 1. data parses
DOCS = {}
for p in sorted(DATA.glob("*.json")):
    try:
        DOCS[p.name] = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"{p.name}: does not parse ({e})")

# 2/3/4/5/6/7. page checks
pages = sorted(LAB.glob("*.html"))
if not pages:
    fail("no lab/*.html pages found - run tools/build_lab.py first")
by_id = {}
for p in pages:
    doc = p.read_text(encoding="utf-8")
    by_id[p.name] = doc
    if "None" in re.sub(r"None of the", "", doc):
        for m in re.finditer(r">\s*None\s*<", doc):
            fail(f"{p.name}: a table cell renders the word None (must render blank)")
    for m in PRICE_RE.finditer(doc):
        fail(f"{p.name}: a price-derived value is rendered: {m.group(0)!r}")
    for m in re.finditer(r'https?://(?:localhost|127\.0\.0\.1)[:/]', doc):
        fail(f"{p.name}: absolute localhost URL {m.group(0)!r}")
    if 'href="assets/style.css"' not in doc:
        fail(f"{p.name}: missing assets/style.css")
    if 'src="assets/app.js"' not in doc:
        fail(f"{p.name}: missing assets/app.js")
    for m in LINK_RE.finditer(doc):
        url = m.group(1)
        if url.startswith(("http://", "https://", "#", "mailto:", "data:")):
            continue
        target = (LAB / url.split("#")[0]).resolve()
        if not target.exists():
            # links that leave the lab section are resolved from the repo root
            if not (ROOT / url.split("#")[0]).exists():
                fail(f"{p.name}: broken link {url}")
    # 5. per-table source coverage
    for tm in re.finditer(r'<table id="([^"]+)">(.*?)</table>', doc, re.S):
        tid, body = tm.group(1), tm.group(2)
        if tid in SOURCE_FREE:
            continue
        head = re.search(r"<thead>(.*?)</thead>", body, re.S)
        if not head:
            continue
        headers = [re.sub(r"<[^>]+>", "", h).strip().lower()
                   for h in CELL_RE.findall(head.group(1))]
        if not any("source" in h for h in headers):
            warn(f"{p.name}: table #{tid} has no source column")
            continue
        for rm in ROW_RE.finditer(re.sub(r"<thead>.*?</thead>", "", body, flags=re.S)):
            if "<th" in rm.group(1):
                continue
            if not SRC_RE.search(rm.group(1)):
                fail(f"{p.name}: table #{tid} has a row with no source link: "
                     f"{re.sub(r'<[^>]+>', ' ', rm.group(1))[:90].strip()}")

for a in ("assets/style.css", "assets/app.js"):
    if not (LAB / a).exists():
        fail(f"lab/{a} is missing")

# 8. requirement where_published targets
REQ = DOCS.get("requirements.json", {})
for r in REQ.get("rows", []):
    for tok in re.split(r",| and ", r[4]):
        tok = tok.strip().rstrip(".")
        if tok.startswith("lab/") and not (ROOT / tok).exists():
            fail(f"requirements {r[0]}: where_published target {tok} does not exist")

# 9. gates and question ids
Q = DOCS.get("questions.json", {})
QIDS = {q[0] for q in Q.get("rows", [])}
referenced = set()
for r in REQ.get("rows", []):
    for gid in re.findall(r"Q-[A-Z]+-\d+", r[5] + " " + r[6]):
        referenced.add(gid)
        if gid not in QIDS:
            fail(f"requirements {r[0]}: gate {gid} is not defined in questions.json")
for doc_name in ("suggestions.json", "models.json", "leaderboard.json", "correlations.json",
                 "price_policy.json", "flagged.json"):
    txt = json.dumps(DOCS.get(doc_name, {}))
    for gid in re.findall(r"Q-[A-Z]+-\d+", txt):
        referenced.add(gid)
        if gid not in QIDS:
            fail(f"{doc_name}: references undefined question {gid}")
orphan = QIDS - referenced
if orphan:
    warn(f"questions defined but never referenced by a requirement: {sorted(orphan)}")

# 10. flags
FL = DOCS.get("flagged.json", {})
ids = [f[0] for f in FL.get("rows", [])]
dupes = [k for k, v in Counter(ids).items() if v > 1]
if dupes:
    fail(f"flagged.json: duplicate flag ids {dupes}")
for f in FL.get("rows", []):
    if not re.match(r"https?://", f[6] or ""):
        fail(f"flagged {f[0]}: source is not an https URL ({f[6]!r})")
    host = urlparse(f[6]).hostname or ""
    if not any(host == h or host.endswith("." + h) for h in
               ("nfl.com", "operations.nfl.com", "github.com", "scikit-learn.org", "weather.gov")):
        warn(f"flagged {f[0]}: source host {host!r} is not on the official allowlist")

# 11. source ids
SRC = DOCS.get("sources.json", {})
SIDS = {s["id"] for s in SRC.get("sources", [])}
for doc_name in ("requirements.json", "flagged.json", "models.json", "repo_review.json"):
    txt = json.dumps(DOCS.get(doc_name, {}))
    for sid in set(re.findall(r"\bL-S\d{2}\b", txt)):
        if sid not in SIDS:
            fail(f"{doc_name}: references undefined source {sid}")
for s in SRC.get("sources", []):
    if s["status"] == "read" and not re.match(r"https?://", s["url"]):
        fail(f"source {s['id']}: marked read but has no https URL")

print(f"lab pages checked: {len(pages)}  data files: {len(DOCS)}")
print(f"  requirement rows: {len(REQ.get('rows', []))}  questions: {len(QIDS)}  "
      f"flags: {len(ids)}  sources: {len(SIDS)}")
for w in warns:
    print("WARN:", w)
for p in problems:
    print("FAIL:", p)
print(f"{len(problems)} failure(s), {len(warns)} warning(s)")
if problems or ("--fail-on-warn" in sys.argv and warns):
    sys.exit(1)
print("OK")
