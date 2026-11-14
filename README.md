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
