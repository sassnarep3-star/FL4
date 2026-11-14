# COORDINATION — FL4 (NFL Signal Origination & Decision System)

Shared task board for all agent sessions working on this repo. **Read this before you touch anything.**

- Repo: `sassnarep3-star/FL4`
- Default branch: `main`
- Site: GitHub Pages (published from `main` via `.github/workflows/deploy-pages.yml`)
- Session ID convention: short hash from the Arena branch name (branch `arena/<id>-*`) or `session-<id>`.
- Claim protocol: write your session ID + file scope in the row, commit, and **push the claim immediately** before doing any work.
- Takeover rule: a claim older than 60 minutes with no commits may be reclaimed by another session; note the handoff in the Log.
- `needs review` = the item is published on the **Flagged for Review** page and does **not** block anything.

## Verification policy (binding on every session)

1. Every data row carries `source_url` + `as_of` (UTC date the source was read).
2. Verification tiers:
   - **T1 — Official**: the league, team, regulator, or governing body that owns the fact (nfl.com, a team site, a state gaming regulator, a statute).
   - **T2 — Trusted secondary**: widely used reference/press that reports T1 data (pro-football-reference.com, ESPN, AP). Used to corroborate, never to originate a row marked T1.
   - **T3 — Unverified**: no source located. Value field is left **blank**, row is flagged, and it surfaces on the Flagged for Review page.
3. Never infer, interpolate, model, or "fill in" a value. If you cannot read it from the source, it is blank.
4. Anything a human decides (a number, a policy, a stake) is recorded as a **Question**, not assumed.
5. Volatile data (injuries, lines, records) must carry `as_of`; the site renders a staleness warning past its TTL.

## Task board

| # | Task | Status | Owner | File scope | Notes |
|---|------|--------|-------|-----------|-------|
| 1 | Repo review + requirements register | in progress | 94107c0d | `REQUIREMENTS.md`, `COORDINATION.md` | Repo was empty (1 file) at session start; register created from scratch. |
| 2 | Question bank (decision-blocking unknowns) | in progress | 94107c0d | `site/questions.html`, `data/questions.json` | Each question states what we know / don't know / what unlocks it. |
| 3 | Suggestions backlog + review workflow | in progress | 94107c0d | `site/suggestions.html`, `data/suggestions.json` | Reviewer picks a path; nothing is implemented until status = approved. |
| 4 | Official injury capture (Week 10, 2026) | in progress | 94107c0d | `data/injuries_wk10_2026.json`, `tools/fetch_injuries*` | NFL.com only, T1. |
| 5 | Availability-gap / depth-deficiency model | in progress | 94107c0d | `site/depth.html`, `data/depth.json` | Needs depth-chart source; flag tier honestly. |
| 6 | Line-origination strategy catalogue | in progress | 94107c0d | `site/strategies.html`, `data/strategies.json` | Singles, parlays, prop combos. |
| 7 | Validation gates (anti-luck protocol) | in progress | 94107c0d | `site/validation.html`, `data/gates.json` | CLV, walk-forward, bootstrap, drawdown, multiple testing. |
| 8 | Correlation reference for parlay/props | in progress | 94107c0d | `site/correlation.html`, `data/correlations.json` | Must cite measured values; blanks otherwise. |
| 9 | Leaderboard + rewards design | in progress | 94107c0d | `site/leaderboard.html`, `data/leaderboard.json` | Scoring rules, anti-gaming, no fabricated results. |
| 10 | Executive summary | in progress | 94107c0d | `site/index.html`, `site/summary.html` | |
| 11 | Site scaffold (Pages, nav, tables, shared renderer) | in progress | 94107c0d | `site/**`, `assets/**`, `.github/workflows/deploy-pages.yml` | |
| 12 | Source register | in progress | 94107c0d | `data/sources.json`, `site/sources.html` | |
| 13 | Flagged for Review page | in progress | 94107c0d | `site/flagged.html`, `data/flagged.json` | |
| 14 | Final integration: build, link check, PR, merge, Pages verify | pending | 94107c0d | whole repo | Integration owner may touch other scopes once their tasks are done. |

## File ownership

No other session holds a claim on this repo at the time of writing (`git ls-remote --heads origin` → `main` only). Session `94107c0d` therefore scopes itself to everything above and will keep `main` clean; all work lands on `arena/94107c0d-fl4`.

## Handoff log

| Time (UTC) | Session | Event |
|---|---|---|
| 2026-11-14 | 94107c0d | Session start. Repo contained only `README.md` (`# FL4`, 5 bytes, 1 commit `ade1d5d`). No COORDINATION.md existed → created. No other remote branches → no conflicts. |

## Irregularities flagged

| # | Item | Detail | Status |
|---|------|--------|--------|
| I-1 | Empty repository | The "review the repo" instruction had no code to review: 1 commit, 1 file, no README content, no build, no data, no history. All project structure is therefore net-new. | informational |
