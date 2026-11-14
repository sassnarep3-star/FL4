# FL4 — NFL signal origination & decision system

A verified data layer, a strategy catalogue, and an explicit register of what cannot be
decided yet. Live site: **https://sassnarep3-star.github.io/FL4/**

Built from an empty repository. Everything here is generated from `data/*.json`; the HTML is
never hand-edited.

## What is in the box

| Path | What it is |
|---|---|
| `site/` | generated static site (14 pages), published to GitHub Pages from `main` |
| `data/*.json` | the source of truth: 11 machine-readable datasets, every row carrying `source_url` and `as_of` |
| `tools/build_site.py` | renders every page from `data/`, runs 9 verification checks, fails closed |
| `tools/check_links.py` | CI integrity: broken/internal links, orphans, leaked `None`, fabricated values |
| `tools/fetch_injuries.py` | capture pipeline for the official weekly availability report (see its docstring for the sandbox constraint) |
| `REQUIREMENTS.md` | 38 requirements from the brief, each traced to where it is met or why it is blocked |
| `COORDINATION.md` | shared task board for parallel agent sessions: claims, scopes, verification log |
| `.github/workflows/deploy-pages.yml` | validate → build → diff-check → link-check → publish |

## The datasets

| File | Rows | Tier | Content |
|---|---|---|---|
| `injuries_week10_2026.json` | 75 player rows, 14 games, 28 clubs | T1 official | Week 10, 2026 availability report (Out/Doubtful), plus club news items and detected anomalies |
| `league_state.json` | 32 | T1 | records, points for/against, net, streak |
| `questions.json` | 26 in 6 groups | — | decision-blocking questions: known / unknown / how to resolve / default if unanswered |
| `inventory.json` | 19 | — | information we have vs information we do not have, with the action that closes each gap |
| `suggestions.json` | 21 | — | improvement backlog + a review control + a recommended 5-phase path |
| `strategies.json` | 16 | — | signal catalogue for originating lines: singles, parlays, prop combos, a shopping baseline |
| `gates.json` | 15 | — | validation gates, each removing one named way luck looks like skill |
| `correlations.json` | 11 pairs | — | measurement protocol; every measured value is null until real legs settle |
| `leaderboard.json` | 0 entries | — | scoring, tiers, rewards, anti-gaming; empty because nothing has been settled |
| `sources.json` | 15 | T1–T3 | what was read, how, and what it may not be used for |
| `flagged.json` | 16 | — | irregularities and unverified items, published rather than hidden |

## Rules this repo enforces

1. **No inference.** A value not confirmable from an official source stays blank and gets a flag.
   Standing example: the standings split-record columns were *dropped* rather than guessed (`F-04`).
2. **Every row is linked.** The builder and `check_links.py` both object to a verified row without a source.
3. **No edge numbers before a gate run.** `edge_claim` is null on all 16 strategies because there is no
   price feed in this environment — that is the project's binding constraint (`F-01`), not an oversight.
4. **Blanks fail closed.** Gates with a reviewer-unset threshold refuse to run instead of using a default.

## Rebuild

```bash
python3 tools/build_site.py --fail-on-warn
python3 tools/check_links.py
python3 -m http.server 8080 --directory site      # preview
```

## Honest limitations

No market prices exist in this repository, so nothing here has been validated as profitable and no line has
been originated yet. The official availability report contains no depth or replacement field, so this site
names who is unavailable and refuses to name who fills in. Research and information only — not betting,
legal or financial advice.
