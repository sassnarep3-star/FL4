#!/usr/bin/env python3
"""Check the built site: every internal link/src resolves, no placeholders remain,
every data row that carries a source has one, and every JSON file parses.

Run from the repo root after tools/build_site.py:  python3 tools/validate.py
Exit code 1 on any failure.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors, warnings = [], []

# 1. JSON parses
for f in sorted((ROOT / "data").glob("*.json")):
    try:
        json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        errors.append(f"JSON parse error in {f.name}: {e}")

# 2. Internal links and placeholders in generated HTML
html_files = [ROOT / "index.html", ROOT / "decision-lab.html"] + sorted((ROOT / "pages").glob("*.html"))
ref_re = re.compile(r'(?:href|src)="([^"]+)"')
for page in html_files:
    text = page.read_text(encoding="utf-8")
    if "__FLAGCOUNT__" in text:
        errors.append(f"placeholder left in {page.relative_to(ROOT)}")
    for ref in ref_re.findall(text):
        if ref.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = (page.parent / ref.split("#")[0]).resolve()
        if not target.exists():
            errors.append(f"broken link in {page.relative_to(ROOT)}: {ref}")

# 3. Every page exists and has a nav
for page in html_files:
    if page.name == "decision-lab.html":  # other session's page, kept verbatim; uses its own nav markup
        continue
    if '<nav>' not in page.read_text(encoding="utf-8"):
        errors.append(f"no nav in {page.relative_to(ROOT)}")

# 4. Every data row with a 'source' field has a non-empty one
for f in sorted((ROOT / "data").glob("*.json")):
    data = json.loads(f.read_text(encoding="utf-8"))
    rows = data.get("rows") if isinstance(data, dict) else None
    if rows is None and isinstance(data, dict):
        rows = data.get("sources") or []
    for i, r in enumerate(rows or []):
        if "source" in r and not str(r.get("source", "")).strip():
            errors.append(f"{f.name} row {i}: empty source")

if warnings:
    print("WARNINGS:")
    for w in warnings:
        print(" -", w)
if errors:
    print("FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"OK: {len(html_files)} pages, links resolve, no placeholders, all JSON valid, all rows sourced")
