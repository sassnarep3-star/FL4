# COORDINATION.md — shared task board

Repo: `sassnarep3-star/FL4` · Current Arena branch: `arena/121f05ad-fl4` (branched from `ade1d5d`; branch is fixed by Arena)
Live site: https://sassnarep3-star.github.io/FL4/

Statuses: `unclaimed` · `in progress` · `done` · `needs review` (flags do not block publication).

> PRs #1–#6 have already integrated the evidence-first dashboard and a separate, verified `signals/` origination section. This branch must not create another site or edit `signals/*`, `data/signals/*`, or its generator. The current follow-up is limited to distinct improvements in the original root dashboard: a blank 2nd/3rd/4th-string tracker, precise fair-price/joint-probability formulas, browser-local suggestion selection, source/privacy corrections, and a stricter root-page row audit. Historical session boards remain below.

## Current task board

| Task | Status | Owner (Arena session) | File scope | Sources / verification | Irregularities |
|---|---|---|---|---|---|
| T12 Root dashboard quality follow-up (no duplicate Signals section) | in progress | `121f05ad`, `arena/121f05ad-fl4` | Root `data/{sources,strategies,questions,requirements,suggestions,flags,injuries_w10_2026,repo_review}.json`, new `data/replacement_tiers.json`, `tools/{build_site,validate}.py`, `assets/{app.js,style.css}`, `decision-lab.html`, generated root pages, README; explicitly not `signals/*` or `data/signals/*` | NFL Week 10 report, NFL Next Gen Stats / stats / Game Books / team directory / terms; NIST and scikit-learn docs; PRs #3–#6 already provide the main origination framework | Keep depth slots blank/unverified. No licensed historical odds, fitted model, measured correlations, or strategy results. Do not change the Pages publishing workflow; existing `verify.yml` and `pages.yml` already cover both site sections. |
| T13 Integration, PR/merge, Pages confirmation | pending | same | repo-wide | Complete root build/row audit, HTTP smoke test, fetch/rebase before push, PR, CI, merge, verify deployment via Actions/Pages API and HTTPS | Stay on Arena branch `arena/121f05ad-fl4`; no new branch. |

## Log

- 2026-11-14 — Inspected the repository and `main` after another session's work had already merged as PR #2 (`388414f`). PR #1 and PR #2 are both merged; GitHub Pages is configured at `https://sassnarep3-star.github.io/FL4/`. The Pages deployment run for `388414f` completed successfully (run `43549635924`, workflow `Publish site to GitHub Pages`); `gh api repos/sassnarep3-star/FL4/pages/builds/latest` reported `built`; the published URL fetch returned the site. No open PRs existed. Do not replace that integrated, feature-rich site with a smaller duplicate static app.
- 2026-11-14 — `origin/main` advanced from `388414f` to `ce7b73e` while this branch was in progress. PRs #3–#6 from session `94107c0d` added the independently verified Signals & origination section, 16 strategy hypotheses, 15 gates, an 11-pair correlation protocol, 26 questions, 16 review flags, a cross-capture injury parser, and build checks. Its Pages publish and verification runs passed. This session now avoids duplicating that section and limits follow-up to root-dashboard affordances that remain distinct.
- Official methodology sources verified for the strategy specification:
  - NFL Football Operations, Next Gen Stats: https://operations.nfl.com/game-operations-logistics/technology/performance-tracking-data-next-gen-stats — official description of tracking-derived fields; this does not establish that raw tracking data is public or licensed here.
  - NFL player statistics: https://www.nfl.com/stats/player-stats/ — official navigation/source, not treated as a saved statistical dataset.
  - NFL Game Books support: https://support.nfl.com/hc/en-us/articles/35869678028180-Game-Books — official description of Game Book PDF access in game centers.
  - NFL injury report: https://www.nfl.com/injuries/ — official report index; direct `/league/2026` route returned 404, while the index/week selector and `/league/2026/reg10` resolved. The 2025 Week 8 report body/title mismatch remains flagged in session notes; no such records copied.
  - NFL roster page: https://www.nfl.com/teams/new-england-patriots/roster — official roster view but no explicit depth ordering, so a roster is not treated as a depth chart.
  - NFL 2026 Rulebook: https://operations.nfl.com/rules-officiating/2026-nfl-rulebook — official rules reference; no rule-based numeric model values inferred.
  - NIST correlation glossary: https://www.itl.nist.gov/div898/handbook/glossary.htm — correlation definition; a coefficient is not a joint parlay probability or a causal effect.
  - NIST bootstrap guidance: https://www.itl.nist.gov/div898/handbook/eda/section3/bootplot.htm — uncertainty estimation via resampling, subject to assumptions.
  - scikit-learn chronological split: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html — chronological evaluation prevents training on future observations and testing on past observations.
  - scikit-learn Brier score: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html — proper scoring loss reference; it is not a return or profitability proof.
- Sources are method/discovery references only. No new odds, injuries, depth tiers, results, rankings, forecasts, correlation estimates, legal conclusions, or reward values were inferred or added.

## Prior integrated work and historical logs

- PR #2 merged to `main` at `388414f`, following PR #1; both prior source-session boards are retained verbatim below. Their task records describe the evidence-first site that is now the base for T10.
- PR #2 Pages workflow run: https://github.com/sassnarep3-star/FL4/actions/runs/43549635924 — completed successfully on 2026-11-14; commit `388414fb881d18a6c1b88fc0e667e37512f56fe6`.
- PRs #3–#6 (Signals & origination, integrity fixes, and rendering corrections) are merged to `main`; the latest build of `ce7b73e` is `built`. `gh run list` reports the Pages publish, verification, and deployment runs successful (latest Pages publish run `43551740148`; Pages API commit `ce7b73e70dcb87469a5ad1077256d50ff705fe83`).
- Public root and Signals pages reviewed at: https://sassnarep3-star.github.io/FL4/ and https://sassnarep3-star.github.io/FL4/signals/.

---

## Earlier session board (merged from main, PR #2 — preserved verbatim)

# COORDINATION.md — shared task board

Repo: `sassnarep3-star/FL4` · Working branch: `arena/ce31a137-fl4` (base `ade1d5d`, `main`)
Live site: https://sassnarep3-star.github.io/FL4/

Statuses: `unclaimed` · `in progress` · `done` · `needs review` (published on the Flagged for Review page; does not block anything).

> **Branch note (R-04):** the coordination rules ask for `session-<id>/<task>` branches. The Arena session rules fix this session to the single branch `arena/ce31a137-fl4`, so all tasks live on that branch and are separated by file scope.

## Task board

| Task | Status | Owner (session) | File scope | Sources / verification | Irregularities |
|---|---|---|---|---|---|
| T1 Repo review (line by line, official links) | done | ce31a137 | `data/repo_review.json`, `pages/repo-review.html` | git log/ls-tree, `gh api repos/.../pages`; links to the commit and files checked (S15, S16) | R-02 README is one line; R-03 no code/CI/.gitignore; R-04 branch rule conflict; R-05 Pages config OK but live content unverified at baseline |
| T2 Injury tracking — NFL Week 10 2026 official report | done (manual transcription; F-18) | ce31a137 | `data/injuries_w10_2026.json`, `pages/injuries.html` | NFL.com injury report text fetched 2026-11-14 (S01); 160 flagged rows, each linked to its nfl.com player page; game times from S01/S02 | F-01, F-02, F-03 (team placement), F-04 (Full practice + Out), F-06 (Nacua report vs news), F-07 (slug), F-18 (manual transcription) |
| T3 Defence/offence depth & backup replacements | done (partial; Q-10 open) | ce31a137 | `data/depth_news.json`, injuries page sections 2 and 4 | Unit absences computed from T2 rows; headlines read on S01 (headline level only) | Depth charts NOT ingested; starter/backup status unverified |
| T4 Strategy leaderboard, validation gates, correlation | done (framework; 0 strategies) | ce31a137 | `data/strategies.json`, `pages/strategies.html` | Bet-type definitions; NFL prop-category memo via ESPN (S08), flagged | No odds data (Q-01); gates G0-G8 are proposals; correlations blank (UNVERIFIED) |
| T5 Executive summary | done | ce31a137 | `pages/executive-summary.html`, `index.html` | Numbers computed by `tools/build_site.py` from T2 data | Decisions listed for owner |
| T6 Requirements + Questions (info gaps) | done | ce31a137 | `data/requirements.json`, `data/questions.json`, pages | Legal: S05 (Ley Federal de Juegos y Sorteos, official text, Art. 1, 3, 4, 8, 12), S06 (ficha) | 16 open questions; Q-03 legal status unresolved |
| T7 Suggestions (decision board; nothing implemented) | done | ce31a137 | `data/suggestions.json`, `pages/suggestions.html` | — | 9 suggestions pending the owner's choice |
| T8 Site build, Flagged for Review page, link check | done | ce31a137 | `tools/build_site.py`, `tools/validate.py`, `assets/*`, `pages/flagged.html`, `data/flags.json`, `data/sources.json`, `README.md`, `.nojekyll` | `python3 tools/validate.py` passes (links, placeholders, JSON, sourced rows) | Auto-flags: rows with no official source are listed on the Flagged page |
| T9 Integration: merge, re-verify, PR to main, merge, Pages check | done (PR #2 → main; see Log) | ce31a137 | repo-wide (final step) | — | — |

## Log

- **2026-11-14 ce31a137** — Claimed T1–T9 and pushed the claim (`bb6d515`).
- **2026-11-14 ce31a137** — Completed T1–T8 on `arena/ce31a137-fl4`. Data files written from official NFL.com and Chamber of Deputies pages; site generated by `tools/build_site.py`; `tools/validate.py` passes.
- Verification notes: injury rows were transcribed by hand from the fetched NFL.com text (F-18). Totals are computed from the file. Legal and NFL-policy items that rely on secondary sources are flagged (F-09, F-11, F-12, F-13).
- Sources not reachable from the sandbox (bash allows only github/npm/pypi): the live GitHub Pages URL was not fetched by bash.

- **2026-11-14 ce31a137** — T9: integration checks run (`tools/build_site.py`, `tools/validate.py` OK; local serve 200 on 12 files). PR opened: https://github.com/sassnarep3-star/FL4/pull/2 (base main ← arena/ce31a137-fl4). Merge and Pages check follow.

## Handoffs

- None.

## Merge conflict log (session ce31a137)

- **2026-11-14** — PR #2 was conflicting because `main` gained PR #1 (session `arena/7e07d4cb-fl4`, "Build evidence-first NFL decision dashboard"). Conflicts: `index.html` (add/add), `COORDINATION.md` (add/add), `README.md` (content).
- **Resolution (nothing discarded):**
  - `index.html` = this session's dashboard. The other session's page is preserved byte-for-byte as `decision-lab.html` (same folder, so its `styles.css` and `app.js` links still work). The dashboard links to it.
  - `COORDINATION.md` = this board first, then the other session's board kept verbatim under "Earlier session board".
  - `README.md` = other session's README kept first, this session's section appended.
- **Flag ID collision:** the other session's flags F-01..F-06 (on `decision-lab.html`) and this session's flags F-01..F-18 (on `pages/flagged.html`) share IDs. Refer to the other session's flags as DL-F-01..DL-F-06.
- **Pages:** `main` is set to legacy Pages (branch `main`, path `/`) and `.github/workflows/pages.yml` (other session) deploys via Actions on push to `main`. Both paths publish the same root. Deployment check is recorded below after merge.

---

## Earlier session board (merged from main, PR #1 — preserved verbatim)

> Section below is the other Arena session's board, kept unchanged. Its flag IDs F-01..F-06 are on decision-lab.html; our flag IDs F-01..F-18 are on pages/flagged.html. The two numbering schemes collide, so refer to theirs as DL-F-xx.

# Coordination board

This repository had no coordination board or existing claims when inspected on 2026-11-14. Arena assigns this session to the active branch `arena/7e07d4cb-fl4`; the session cannot create or switch to a separate session branch. Work was therefore done only on that active branch. No other session claims were visible at inspection.

| Task | Status | Owner | File scope |
|---|---|---|---|
| Establish NFL decision-support site, executive summary, research framework, questions, and review flags | done | Arena session `arena/7e07d4cb-fl4` | `index.html`, `styles.css`, `app.js`, `README.md`, `COORDINATION.md`, `.github/workflows/pages.yml` |

## Verification log

- Initial repository review: only a five-byte `README.md` and initial commit were present; no site or data existed.
- Official source links used: NFL.com injury reports (`https://www.nfl.com/injuries/`), inactives (`https://www.nfl.com/inactives/`), team directory (`https://www.nfl.com/teams/`), schedules (`https://www.nfl.com/schedules/`), NFL.com terms (`https://www.nfl.com/terms`), NFL GSIS (`https://www.nflgsis.com/`), and NFL Football Operations analytics (`https://operations.nfl.com/gameday/analytics/`). These are linked as verification/discovery points, not as evidence for fabricated metrics.
- Web search confirmed the official NFL injury report page is active and presents player, position, injury, practice status, and game status fields. No individual reported injury was copied into this static blueprint.
- Static HTML validation: 7 section IDs, 27 links, 28 table rows; all in-page anchors resolve and no href is empty. `styles.css`, `app.js`, and Pages workflow exist. `git diff --check` passed.
- The review flags state the key irregularities: absent data/results, historical market prices and timestamps, archived injury snapshots, measured correlations, data licensing, and leaderboard reward governance. All unknown values are blank or explicitly unverified.
- No strategy is claimed validated or profitable. The strategy, validation gates, leaderboard and suggestions are research proposals.
- GitHub Pages workflow was added, but live deployment, GitHub Actions checks, PR, and merge have not been executed/verified in this session. Publication requires merge to `main` and repository Pages configuration. This is not marked as done.

## Irregularities / follow-up

- Official NFL public sources may not supply all historical play-by-play, injury-status, player-prop line, or sportsbook market data needed to estimate strategy correlations or isolate skill. The applicable data rights and provider terms have not been reviewed.
- Multi-agent separate-branch coordination and final integration could not be performed from this single active Arena branch. No other claimed work existed to integrate.
- Before making picks or rewarding strategies, source data rights, market feeds, settlement rules, test protocol, legal/compliance requirements, and governance must be resolved.

---

# Session 94107c0d board — signals & origination section (added 2026-11-14)

Branch `arena/94107c0d-fl4` (base `ade1d5d`). Scope: `signals/`, `signals_assets/`, `data/signals/*`,
`tools/build_signals.py`, `tools/check_signals.py`, `tools/fetch_injuries.py`, `tools/testdata/*`,
`REQUIREMENTS.md`, `.github/workflows/verify.yml`. No file owned by another session was edited, with
the two integration exceptions logged below.

## Verification policy applied (binding)

1. Every published row carries `source_url` + `as_of`.
2. Tiers: **T1** league/club/regulator owns the fact (only tier this section publishes values from);
   **T2** corroborates, never originates; **T3** recorded as a lead, never as a number.
3. Never infer. If it cannot be read from the source it is blank, and the blank is a flagged row.
4. Anything a human must decide is recorded as a question with a stated default, not assumed.
5. Volatile data carries a TTL and a freshness statement rendered on the page.

## Task board

| # | Task | Status | Owner | Sources / verification performed | Irregularities |
|---|---|---|---|---|---|
| 1 | Repo review + requirements register | done | 94107c0d | `git log`/`ls-tree` at `ade1d5d`; `REQUIREMENTS.md` (38 rows) | I-1 repo held 1 file / 5 bytes at start |
| 2 | Question bank | done | 94107c0d | `data/signals/questions.json`, 26 questions / 6 groups, each with known-unknown-resolve-default | 18 marked blocking |
| 3 | Suggestions backlog + review control | done | 94107c0d | `data/signals/suggestions.json`, 21 items, 5-phase path; `status` field is the control | nothing auto-approved on silence |
| 4 | Official injury capture (Wk 10 2026) | done | 94107c0d | `data/signals/injuries_week10_2026.json`: 76 Out/Doubtful rows, 14 games, 28 clubs from nfl.com/injuries/ (8/8 chunks read); parse rule re-implemented in `tools/fetch_injuries.py` and cross-checked against the published dataset (5/5 fixture rows matched, 0 field mismatches) | F-10 (filing cadence), F-14 (player-club pairings) |
| 5 | Availability / depth-deficiency analysis | done (bounded) | 94107c0d | `signals/depth.html`, unit mapping derived from the captured rows | **replacement names not published**: the official report has no depth field (F-02) |
| 6 | Line-origination strategy catalogue | done | 94107c0d | `data/signals/strategies.json`: 16 strategies, each with hypothesis, signal, inputs, vetoes, stake, falsification, "how it loses" | every `edge_claim` null by design (F-01) |
| 7 | Validation gates | done | 94107c0d | `data/signals/gates.json`: 15 gates; pass rules mechanical; fail-closed on missing thresholds | 5 thresholds reviewer-set (F-05) |
| 8 | Correlation reference | done (protocol only) | 94107c0d | `data/signals/correlations.json`: 11 pairs, phi + excess joint prob + bootstrap, n>=300 | all `measured_value` null; no ledger to measure (F-11) |
| 9 | Leaderboard + rewards | done (rules), empty (data) | 94107c0d | `data/signals/leaderboard.json`: CLV-primary score, 5 tiers, 6 anti-gaming rules, non-cash rewards, synthetic worked example labelled as such | board empty by design |
| 10 | Executive summary | done | 94107c0d | `signals/index.html`, `signals/methodology.html` | — |
| 11 | Site scaffold + generator | done | 94107c0d | `tools/build_signals.py` (14 pages, 10 build-time checks, all PASS) | — |
| 12 | Source register | done | 94107c0d | `data/signals/sources.json`: 15 entries incl. sources deliberately *not* relied on | 3 sources marked not-read/unverified |
| 13 | Flagged for Review | done | 94107c0d | `data/signals/flagged.json`: 16 flags with type, action, links | none block the merge |
| 14 | Integration: merge main, re-verify, PR, merge, Pages | done | 94107c0d | PR #3 (`a2a30a2`) and PR #4 (`bbc932e`) merged to `main`; CI `verify` + `Publish site to GitHub Pages` + `pages build and deployment` all success; live pages re-fetched over HTTPS to confirm rendering | conflict log below; one transcription omission found and fixed by cross-capture check 10 |

## Integration actions performed by this session (shared outputs)

1. **File collisions resolved by relocation, not overwriting.** `data/questions.json`,
   `data/sources.json`, `data/strategies.json`, `data/suggestions.json` and `tools/build_site.py`
   exist on `main` (session ce31a137). Main's copies were kept **unchanged**; this session's copies
   moved to `data/signals/` and `tools/build_signals.py`, and generated pages moved from `site/` to
   `signals/`. Nothing was deleted from either side.
2. **Nav + tile entry added to the dashboard generator** (`tools/build_site.py`, one line in `NAV`
   and one tile on the landing page) so the sections interlink and survive a rebuild. This is the
   only edit made inside another session's file; it is additive and `tools/validate.py` passes.
3. **This session's publishing workflow was deleted.** Main's `pages.yml` uploads the repo root,
   which already contains `signals/`; a second Pages workflow would have raced it for the same
   deployment. Replacement: `.github/workflows/verify.yml` (no deploy).
4. Cross-links: `signals/*` → `../index.html` and `../decision-lab.html`; checked by
   `tools/check_signals.py` (0 broken internal links).

## Merge conflict log (session 94107c0d)

- `git pull --rebase origin main` on 2026-11-14 found `main` had advanced from `ade1d5d` to
  `388414f` (PR #1 `arena/7e07d4cb-fl4`, PR #2 `arena/ce31a137-fl4`). The rebase hit an add/add
  conflict on `COORDINATION.md` and was **aborted**, not forced, so no commit was rewritten.
- Replaced with `git merge origin/main`. Conflicts: `COORDINATION.md`, `README.md`,
  `data/{questions,sources,strategies,suggestions}.json`, `tools/build_site.py` (7 files, all add/add
  or content).
- Resolution: main's version adopted for all five data/tool files; this session's versions relocated
  (`data/signals/`, `tools/build_signals.py`, `signals/`); `README.md` and `COORDINATION.md`
  concatenated with main's text first and this section appended. No content from either session was
  discarded, and both builders were re-run after the merge to prove the tree still generates cleanly.
- Post-merge verification: `tools/build_site.py` → no drift vs committed `index.html`/`pages/`;
  `tools/validate.py` → OK (11 pages); `tools/build_signals.py --fail-on-warn` → 10/10 checks pass;
  `tools/check_signals.py` → 14 pages, 0 broken links.

## Handoffs

- 2026-11-14 94107c0d → any session: the flag ID namespace is per-section. This section's flags are
  `F-01..F-16` **on `signals/flagged.html`**, and they collide on purpose-of-numbering with
  ce31a137's `F-01..F-18` on `pages/flagged.html` and with `DL-F-01..DL-F-06` on `decision-lab.html`.
  When citing, prefix with the page: `signals:F-01`, `pages:F-02`, `DL-F-01`.
- 2026-11-14 94107c0d → ce31a137: consider folding `data/signals/injuries_week10_2026.json` into
  `data/injuries_w10_2026.json`. Two independent captures of the same official page now exist
  (this one filtered by a stated rule to 76 Out/Doubtful rows; theirs 160 flagged rows, marked
  manual transcription / F-18). A parser with the rule as code exists at `tools/fetch_injuries.py`,
  which would clear their F-18. Do not merge the two row sets without deciding which rule wins.
- `arena/121f05ad-fl4` exists on the remote with no PR at the time of writing. It has not been read
  or touched by this session. If it adds root-level `index.html`/`pages/` content, the collision
  pattern above (relocate into a namespaced section) is the proven resolution.

## Post-merge log (session 94107c0d)

- 2026-11-14 — PR #3 opened and merged to `main` (`a2a30a2`). Checks on the merge commit:
  `Verify data, generators and both site sections` **success**; `Publish site to GitHub Pages`
  **success**; `pages build and deployment` **success**.
- Live verification after deploy (fetched over HTTPS, not assumed): `…/FL4/` serves the dashboard and
  its tile list now includes **Signals & origination** → `…/FL4/signals/index.html`, which renders the
  executive summary, the 10 build-time checks (all PASS) and the Week 10 fixture table.
- **Two rendering defects found by that live read and fixed in a follow-up PR:** (1) `[label](page.html)`
  links written in prose were displayed as literal text because the renderer had no markdown-link rule —
  `inline()` now stashes links before escaping so URLs inside `href` are never re-linked; (2) a
  `&middot;` entity embedded in a data string was escaped and displayed raw — replaced with the
  character. Both generators re-run, `check_signals.py` and `validate.py` pass, and a scan for
  `None`/`[]`/`&amp;amp;`/`**` leaks across all 14 pages returns only one legitimate prose hit
  (`games[]` in a field name).
- Lesson recorded for other sessions: verifying a deployed page and verifying the build are different
  checks. The build was green while two cosmetic defects were live.

- 2026-11-14 — PR #5 (`2c2de03`) merged; CI verify + Pages publish + pages build/deploy all success on
  `main`. Live re-reads of `signals/injuries.html` and `signals/strategies.html` found one more defect
  class: the player table's Club-name column asked for a key the rows did not carry, so 76 rows rendered
  an empty column. Fixed, and `table()` now fails the build on any column key no row carries. Deliberately
  placed in the builder, not the link checker: only the builder can distinguish an intentional blank
  (`measured_value: null`, `edge_claim: null`) from a generator bug. Verified by planting the bug
  (exit 1, names the column and the available keys) and removing it (exit 0).

## Completion record (all 14 tasks) — 2026-11-14, session 94107c0d

- **Published:** https://sassnarep3-star.github.io/FL4/signals/ (14 pages), reachable from the
  dashboard nav and landing tile at https://sassnarep3-star.github.io/FL4/
- **PRs:** #3 (feature + integration) and #4 (rendering fixes + cross-validation guard), both merged.
- **Sources used (all read in-session, T1):** nfl.com/injuries/ (8/8 chunks), nfl.com/standings/
  (2/2), nfl.com/schedules/2026/week-10, one game result page, 8 linked news items. Secondary pages
  consulted and deliberately *not* relied on are registered in `data/signals/sources.json` with
  `verifies: nothing`.
- **Verification performed:** 10 build-time checks (all PASS) + `check_signals.py` (0 broken links,
  no leaked `None`, no fabricated edge/correlation value) + dashboard `validate.py` (11 pages OK)
  + CI on `main` (verify, Pages publish, pages build/deploy) + post-deploy HTTPS reads of
  `signals/index.html` and `signals/strategies.html`.
- **Corrections made after publishing:** two rendering defects (prose markdown links, an escaped
  entity) and one data omission (an Out row dropped in transcription) — all found by *reading the
  deployed page* and by *reconciling two independent captures of the same source*, not by the build.
- **Irregularities flagged:** 16 (`signals/flagged.html`). None blocked the merge. The one that
  blocks progress is `signals:F-01`: no market-price feed exists here, so no CLV, no backtest and no
  originated line can be reported honestly.

## Open items for the owner (do not block the merge)

- 18 blocking questions in `signals/questions.html`; 5 numeric gate thresholds unset (`signals:F-05`).
- No price feed ⇒ no CLV, no backtest, no originated line, empty leaderboard (`signals:F-01`).
- Depth source unresolved ⇒ absences are published, replacements are not (`signals:F-02`).
