# FL4 · NFL Decision Lab

A static, evidence-first NFL decision-support and research blueprint. The site organizes strategy concepts, validation gates, lineup/injury data requirements, decision questions, suggestions, and unverified items. It intentionally does **not** publish betting picks, player statuses, prices, correlations, or returns: the repository contains no verified underlying data or model results.

## Preview locally

Open `index.html` directly, or run a static server from the repository root, for example:

```sh
python3 -m http.server 8000
```

## Publish with GitHub Pages

The workflow in `.github/workflows/pages.yml` publishes the static site when changes land on the repository's default branch or when manually dispatched. In repository settings, ensure Pages uses GitHub Actions if not already configured.

## Evidence and limits

Official NFL links in the site are source discovery/review links, not evidence for computed values. Every table row includes a primary-source link; where a row describes process or requirements rather than a factual value, it points to the official source family relevant to that field. No current injuries, depth-chart ranks, odds, or statistical findings have been asserted. See **Flagged for review** for absent data, licensing, market prices, correlations, and governance questions.

The recommendations are research proposals, not claims that a strategy is profitable or that NFL data access/reuse is authorized. Confirm the applicable official source and terms before collection or redistribution.

## Dashboard built on 2026-11-14 (session ce31a137)

Live site (GitHub Pages): https://sassnarep3-star.github.io/FL4/

## What is here

- `index.html`, `pages/*.html` - static site: dashboard, executive summary, injuries and depth,
  strategies and leaderboard, questions, requirements, suggestions (decision board), repo review,
  sources, and Flagged for Review.
- `data/*.json` - the data behind every table. Each row carries a source link.
- `tools/build_site.py` - regenerates the HTML from `data/*.json`. Run: `python3 tools/build_site.py`
- `tools/validate.py` - checks JSON, internal links, and placeholders. Run: `python3 tools/validate.py`
- `COORDINATION.md` - shared task board, log, and handoffs.

## Rules

- Every value needs a source. Official sources: nfl.com, operations.nfl.com, diputados.gob.mx, gob.mx.
- If a value cannot be confirmed from an official source it is left blank and flagged (Flagged for Review page).
- Suggestions are not implemented until the owner chooses an option.
- Informational research only. Not betting advice.
