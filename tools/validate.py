#!/usr/bin/env python3
"""Validate the generated research site without fetching external pages.

Run from the repository root after tools/build_site.py:
    python3 tools/validate.py

Checks JSON/source references, HTTPS external links, local links and fragments,
page navigation, and every non-empty table row that presents source/evidence
links. The source catalogue and build diagnostics are explicit exceptions;
user-brief scope/requirement rows are labelled as non-factual.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OFFICIAL_HOSTS = (
    "nfl.com", "nflgsis.com", "operations.nfl.com", "diputados.gob.mx",
    "gob.mx", "github.com", "sassnarep3-star.github.io", "juegosysorteos.gob.mx",
    "nist.gov", "scikit-learn.org",
)
SOURCE_ID_RE = re.compile(r"\bS\d{2}\b")
URL_RE = re.compile(r"https?://[^\s;,)\]]+")
errors: list[str] = []
audited_table_rows = 0
audited_tables = 0


def host_matches(host: str, base: str) -> bool:
    return host == base or host.endswith("." + base)


def is_official_host(host: str) -> bool:
    return any(host_matches(host, base) for base in OFFICIAL_HOSTS)


def add_error(message: str) -> None:
    errors.append(message)


# 1. Parse every JSON file and load the source catalogue.
json_files = sorted(DATA.glob("*.json"))
parsed: dict[str, object] = {}
for file in json_files:
    try:
        parsed[file.stem] = json.loads(file.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        add_error(f"JSON parse error in {file.relative_to(ROOT)}: {exc}")

source_data = parsed.get("sources", {})
source_rows = source_data.get("sources", []) if isinstance(source_data, dict) else []
source_by_id = {
    row.get("id"): row for row in source_rows
    if isinstance(row, dict) and row.get("id")
}
source_hosts: set[str] = set()
for row in source_rows:
    if not isinstance(row, dict):
        add_error("data/sources.json contains a non-object source entry")
        continue
    sid, url, kind = row.get("id", "?"), row.get("url", ""), row.get("type", "")
    parsed_url = urlparse(url)
    if parsed_url.scheme != "https" or not parsed_url.hostname:
        add_error(f"source {sid}: source URL must be HTTPS: {url!r}")
        continue
    source_hosts.add(parsed_url.hostname.lower())
    if kind not in {"official", "secondary"}:
        add_error(f"source {sid}: type must be 'official' or 'secondary', got {kind!r}")
    if kind == "official" and not is_official_host(parsed_url.hostname.lower()):
        add_error(f"source {sid}: host is not on the official-source allowlist: {url}")


def canonical_source_tokens(text: str) -> tuple[list[str], list[str]]:
    ids = SOURCE_ID_RE.findall(text)
    urls = [match.rstrip(".]") for match in URL_RE.findall(text)]
    return ids, urls


def validate_source_value(value: object, where: str) -> None:
    """Require data rows to resolve to at least one approved official source.

    A source that says "User brief" is only accepted as a clearly non-factual
    scope/requirement record; rendered rows must carry the brief badge.
    """
    if not isinstance(value, str) or not value.strip():
        add_error(f"{where}: missing source reference")
        return
    if "user brief" in value.lower():
        return
    ids, urls = canonical_source_tokens(value)
    if not ids and not urls:
        add_error(f"{where}: source text does not resolve to a source ID or HTTPS URL: {value!r}")
        return
    official_found = False
    for sid in ids:
        source = source_by_id.get(sid)
        if source is None:
            add_error(f"{where}: unknown source ID {sid}")
            continue
        source_url = urlparse(source.get("url", ""))
        if source.get("type") == "official" or (source_url.hostname and is_official_host(source_url.hostname.lower())):
            official_found = True
    for url in urls:
        parsed_url = urlparse(url)
        if parsed_url.scheme != "https" or not parsed_url.hostname:
            add_error(f"{where}: source URL must be HTTPS: {url!r}")
            continue
        host = parsed_url.hostname.lower()
        if not is_official_host(host) and not any(host_matches(host, known) for known in source_hosts):
            add_error(f"{where}: source URL host is not catalogued: {host}")
        if is_official_host(host):
            official_found = True
    if not official_found:
        add_error(f"{where}: factual data source list has no official/primary-source link")


# Every row-level source reference in data must resolve. Rows sourced from the
# user brief are scope/requirements, not factual claims, and are exempt above.
def walk_sources(value: object, where: str) -> None:
    if isinstance(value, dict):
        if "source" in value:
            validate_source_value(value["source"], where)
        for key, child in value.items():
            if key != "source":
                walk_sources(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_sources(child, f"{where}[{index}]")

for name, document in parsed.items():
    walk_sources(document, f"data/{name}.json")


class TableAuditParser(HTMLParser):
    """Collect table headers, body rows, source-cell links, and source badges."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[dict[str, object]] = []
        self.current_table: dict[str, object] | None = None
        self.current_row: list[dict[str, object]] | None = None
        self.current_cell: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "table":
            self.current_table = {"id": attributes.get("id", ""), "rows": []}
        elif self.current_table is not None and tag == "tr":
            self.current_row = []
        elif self.current_row is not None and tag in {"th", "td"}:
            self.current_cell = {"tag": tag, "text": [], "links": [], "classes": set()}
        elif self.current_cell is not None:
            if tag == "a" and attributes.get("href"):
                self.current_cell["links"].append(attributes["href"])
            if tag in {"span", "td"} and attributes.get("class"):
                self.current_cell["classes"].update(attributes["class"].split())

    def handle_data(self, data: str) -> None:
        if self.current_cell is not None:
            self.current_cell["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"th", "td"} and self.current_cell is not None:
            self.current_cell["text"] = " ".join(" ".join(self.current_cell["text"]).split())
            if self.current_row is not None:
                self.current_row.append(self.current_cell)
            self.current_cell = None
        elif tag == "tr" and self.current_row is not None and self.current_table is not None:
            self.current_table["rows"].append(self.current_row)
            self.current_row = None
        elif tag == "table" and self.current_table is not None:
            self.tables.append(self.current_table)
            self.current_table = None


def approved_external_url(url: str, where: str) -> bool:
    parsed_url = urlparse(url)
    if parsed_url.scheme != "https" or not parsed_url.hostname:
        add_error(f"{where}: external link must use HTTPS: {url}")
        return False
    host = parsed_url.hostname.lower()
    if is_official_host(host) or any(host_matches(host, known) for known in source_hosts):
        return True
    add_error(f"{where}: external host is not in the source catalogue: {host}")
    return False


def validate_tables(page: pathlib.Path, text: str) -> None:
    global audited_table_rows, audited_tables
    parser = TableAuditParser()
    parser.feed(text)
    parser.close()
    for number, table_data in enumerate(parser.tables, start=1):
        table_id = str(table_data.get("id") or f"table-{number}")
        rows = table_data.get("rows", [])
        if not rows:
            continue
        headers = [str(cell.get("text", "")).strip().lower() for cell in rows[0]]
        data_rows = rows[1:]
        if table_id == "tbl-auto":  # build diagnostics, not a factual data table
            continue
        if not data_rows:
            continue
        source_indices = [
            i for i, heading in enumerate(headers)
            if re.search(r"\b(source|link|evidence)\b", heading)
        ]
        if not source_indices:
            add_error(f"{page.relative_to(ROOT)}#{table_id}: non-empty table has no source/evidence/link column")
            continue
        audited_tables += 1
        audited_table_rows += len(data_rows)
        for row_number, row in enumerate(data_rows, start=1):
            index = source_indices[-1]
            if index >= len(row):
                add_error(f"{page.relative_to(ROOT)}#{table_id} row {row_number}: source cell is missing")
                continue
            cell = row[index]
            links = list(cell.get("links", []))
            classes = cell.get("classes", set())
            cell_text = str(cell.get("text", ""))
            is_brief = "brief" in classes or "user brief" in cell_text.lower()
            if table_id == "tbl-sources":
                # A source catalogue row links to the source it is describing;
                # secondary items are explicitly typed and flagged elsewhere.
                if not links:
                    add_error(f"{page.relative_to(ROOT)}#{table_id} row {row_number}: source-catalogue row has no URL")
            elif is_brief:
                pass
            else:
                official_links = [
                    link for link in links
                    if urlparse(link).hostname and is_official_host(urlparse(link).hostname.lower())
                ]
                if not official_links:
                    add_error(f"{page.relative_to(ROOT)}#{table_id} row {row_number}: factual row lacks an official HTTPS source link")
            for link in links:
                approved_external_url(link, f"{page.relative_to(ROOT)}#{table_id} row {row_number}")


# 2. Built pages, navigation, local links/fragments, secure/catalogued externals,
#    and official source links on every factual table row.
html_files = [ROOT / "index.html", ROOT / "decision-lab.html"] + sorted((ROOT / "pages").glob("*.html"))
if not html_files or not (ROOT / "index.html").exists():
    add_error("missing index.html or generated HTML pages")

for page in html_files:
    if not page.exists():
        add_error(f"missing page: {page.relative_to(ROOT)}")
        continue
    text = page.read_text(encoding="utf-8")
    if "__FLAGCOUNT__" in text:
        add_error(f"unreplaced placeholder in {page.relative_to(ROOT)}")
    if page.name != "decision-lab.html" and "<nav>" not in text:
        add_error(f"no navigation in {page.relative_to(ROOT)}")
    for href in re.findall(r'(?:href|src)="([^"]+)"', text):
        if href.startswith(("https://", "http://")):
            approved_external_url(href, str(page.relative_to(ROOT)))
            continue
        if href.startswith(("mailto:", "tel:", "data:")):
            continue
        if href.startswith("#"):
            target_page = page
            fragment = href[1:]
        else:
            path_part, _, fragment = href.partition("#")
            target_page = (page.parent / path_part).resolve()
        if not target_page.exists():
            add_error(f"broken local link in {page.relative_to(ROOT)}: {href}")
            continue
        if fragment:
            target_text = target_page.read_text(encoding="utf-8")
            ids = set(re.findall(r'\bid="([^"]+)"', target_text))
            names = set(re.findall(r'\bname="([^"]+)"', target_text))
            if fragment not in ids and fragment not in names:
                add_error(f"broken fragment in {page.relative_to(ROOT)}: {href}")
    validate_tables(page, text)

if errors:
    print("FAILED:")
    for error in errors:
        print(" -", error)
    sys.exit(1)

print(f"PASS: {len(html_files)} HTML pages checked; JSON and source IDs resolve; local links/fragments resolve.")
print(f"PASS: {audited_table_rows} rows in {audited_tables} source/evidence tables checked; factual rows link to an official source.")
print("PASS: external links use HTTPS and catalogued hosts.")
print("NOTE: source links were reviewed 2026-11-14; this offline validator does not fetch or attest to future availability or data rights.")
