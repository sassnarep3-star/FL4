# FL4 · NFL Decision Lab

A static, evidence-first NFL research site for injury/availability review, strategy hypotheses, validation gates, line-origination design, correlation analysis, and decision tracking. It includes a dated, source-linked Week 10 2026 availability snapshot and a separate Signals & origination section. It does **not** provide a live injury feed, priced betting picks, market prices, or measured strategy performance; no historical odds feed or validated model results are connected.

## Preview locally

Open `index.html` directly, or run a static server from the repository root, for example:

```sh
python3 -m http.server 8000
```

## Publish with GitHub Pages

The workflow in `.github/workflows/pages.yml` publishes the static site when changes land on the repository's default branch or when manually dispatched. In repository settings, ensure Pages uses GitHub Actions if not already configured.

## Evidence and limits

Official NFL links in the site are source discovery/review links, not evidence for computed values. Factual table rows include a primary-source link; rows that describe user requirements or build diagnostics are explicitly non-factual. The injury report is a dated snapshot, not a live/current status feed. No verified depth-chart tiers, market prices, measured correlations, or validated strategy results are asserted. See **Flagged for review** for absent data, licensing, market prices, correlations, and governance questions.

The recommendations are research proposals, not claims that a strategy is profitable or that NFL data access/reuse is authorized. Confirm the applicable official source and terms before collection or redistribution.

## Dashboard built on 2026-11-14 (session ce31a137)

Live site (GitHub Pages): https://sassnarep3-star.github.io/FL4/

## What is here

- `index.html`, `pages/*.html` - static site: dashboard, executive summary, injuries and depth,
  strategies and leaderboard, questions, requirements, suggestions (decision board), repo review,
  sources, and Flagged for Review.
- `data/*.json` - the data behind every table. Each factual row carries a source link.
- `data/replacement_tiers.json` - blank offense/defense tracking slots for second-, third-, and fourth-string research. It assigns no players or depth order.
- `tools/build_site.py` - regenerates the HTML from `data/*.json`. Run: `python3 tools/build_site.py`
- `tools/validate.py` - checks source IDs, HTTPS/local links, and official sources on factual root-dashboard table rows. Run: `python3 tools/validate.py`
- `COORDINATION.md` - shared task board, log, and handoffs.

## Rules

- Every factual value needs a source. Primary sources include nfl.com, operations.nfl.com, diputados.gob.mx, gob.mx and GitHub; NIST/scikit-learn citations support general methods only.
- If a value cannot be confirmed from an official source it is left blank and flagged (Flagged for Review page).
- Unapproved suggestions stay proposed. Choices on the root Suggestions page are local to that browser; they do not modify code or trigger data collection.
- Informational research only. Not betting advice.

---

## Signals & origination section (session 94107c0d, 2026-11-14)

Published at **https://sassnarep3-star.github.io/FL4/signals/** — a self-contained 14-page section
reachable from the dashboard nav and tiles. It covers the line-origination half of the brief: the
strategy catalogue, validation gates, the correlation protocol, the leaderboard rules, the question
bank, the information inventory and a second, independently captured Week 10 availability snapshot.

| Path | What it is |
|---|---|
| `signals/` | generated static section (14 pages), published by the root Pages workflow |
| `signals_assets/` | the section's CSS/JS source; the builder copies it into `signals/assets/` so a clean checkout regenerates everything |
| `data/signals/*.json` | its datasets (11 files); every row carries `source_url` and `as_of` |
| `tools/build_signals.py` | renders every page from `data/signals/`, runs 10 verification checks, fails closed |
| `tools/check_signals.py` | integrity: links, assets, orphans, leaked `None`, fabricated edge/correlation values |
| `tools/fetch_injuries.py` | capture pipeline with the parse rule as code (`keep iff Game Status is Out or Doubtful`) |
| `tools/testdata/report_sample.md` | parser fixture; CI asserts it yields "5 kept as Out/Doubtful across 4 clubs" |
| `REQUIREMENTS.md` | 38 requirements traced to status and blocker |
| `.github/workflows/verify.yml` | verifies both sections on push/PR; deliberately does not publish, so it never races `pages.yml` |

### Rules enforced by this section

1. **No inference.** Unconfirmable values stay blank and get a flag. Worked example: the standings'
   split-record columns were dropped rather than mapped by guess (`F-04`).
2. **No edge numbers before a gate run.** `edge_claim` is null on all 16 strategies because this
   environment has no price feed — the binding constraint (`F-01`), stated on every page rather than papered over.
3. **Blanks fail closed.** A gate with an unset threshold refuses to run instead of defaulting.
4. **Reproducible transcription.** The published availability table is regenerable from the source
   page by the rule in `tools/fetch_injuries.py`.

### Rebuild

```bash
python3 tools/build_signals.py --fail-on-warn
python3 tools/check_signals.py
python3 tools/fetch_injuries.py --raw tools/testdata/report_sample.md -o /tmp/parsed.json
```

Research and information only — not betting, legal or financial advice. No strategy here is validated.
