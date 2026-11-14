# FL4 - NFL research and lines project

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
