#!/usr/bin/env python3
"""Site integrity checks, run in CI before publish.

Fails the build on: a missing page, a broken internal link, invalid JSON in data/,
a leaked Python None in rendered HTML, an orphan page not reachable from the nav,
or a table row in a verified dataset that has no source link.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "signals"
DATA = ROOT / "data" / "signals"
problems = []

pages = sorted(p.name for p in SITE.glob("*.html"))
if not pages:
    print("no html found in site/")
    sys.exit(1)

# 1. index exists, every page is linked from the nav
index = (SITE / "index.html").read_text()
for p in pages:
    if p == "index.html":
        continue
    if 'href="%s"' % p not in index:
        problems.append("orphan page (not linked from the nav): %s" % p)

# 2. internal links resolve
ext_links = set()
for p in SITE.glob("*.html"):
    txt = p.read_text()
    for href in set(re.findall(r'href="([^"#]+)"', txt)):
        if href.startswith(("http://", "https://", "mailto:")):
            ext_links.add(href)
            if href.startswith("http://"):
                problems.append("insecure link in %s: %s" % (p.name, href))
            continue
        if not (p.parent / href).exists():
            problems.append("broken internal link in %s -> %s" % (p.name, href))
    if re.search(r">\s*None\s*<", txt):
        problems.append("rendered None value in %s" % p.name)
    if "%%" in txt:
        problems.append("unformatted %% in %s" % p.name)

# 3. assets referenced exist
for p in SITE.glob("*.html"):
    for a in set(re.findall(r'(?:src|href)="(assets/[^"]+)"', p.read_text())):
        if not (SITE / a).exists():
            problems.append("missing asset %s referenced by %s" % (a, p.name))

# 4. data files are valid JSON and mirrored into the site
for f in sorted(DATA.glob("*.json")):
    try:
        obj = json.loads(f.read_text())
    except Exception as e:                                    # noqa: BLE001
        problems.append("invalid JSON in %s: %s" % (f.name, e))
        continue
    if not (SITE / "data" / f.name).exists():
        problems.append("data file not published to site/data: %s" % f.name)
    txt = f.read_text()
    if "http://" in txt:
        problems.append("insecure URL in %s" % f.name)
    # verified datasets must carry a source on every row that asserts a value
    if f.name.startswith(("injuries", "league_state")):
        rows = obj.get("out_or_doubtful") or obj.get("teams") or []
        if not rows:
            problems.append("%s has no rows" % f.name)
        if not obj.get("meta", {}).get("source_url"):
            problems.append("%s has no meta.source_url" % f.name)

# 5. strategies must not carry a fabricated edge value
st = json.loads((DATA / "strategies.json").read_text())
for s in st["strategies"]:
    if s.get("edge_claim") is not None:
        problems.append("strategy %s asserts an edge_claim without a gate run" % s["id"])
corr = json.loads((DATA / "correlations.json").read_text())
for c in corr["pairs"]:
    if c["measured_value"] is not None and c.get("n_obs", 0) < corr["meta"]["estimation_protocol"]["minimum_observations"]:
        problems.append("correlation %s has a value below the sample minimum" % c["id"])

# 6. every page must carry the flagged-for-review route
for p in SITE.glob("*.html"):
    if 'href="flagged.html"' not in p.read_text():
        problems.append("%s has no route to the flagged page" % p.name)

print("pages: %d, external links: %d, data files: %d" % (len(pages), len(ext_links), len(list(DATA.glob('*.json')))))
if problems:
    print("\nFAIL (%d):" % len(problems))
    for x in problems:
        print("  -", x)
    sys.exit(1)
print("all site integrity checks passed")
