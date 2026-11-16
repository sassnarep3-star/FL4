# COORDINATION.md — shared task board

Repo: `sassnarep3-star/FL4` · Current Arena branch: `arena/810f9f1f-fl4` (branched from `62afd1b` of `main`; status `active`)
Live site: https://sassnarep3-star.github.io/FL4/

Statuses: `unclaimed` · `in progress` · `done` · `needs review` (flags do not block publication).

# ACTIVE BOARD — session `61ebd543` (branch `arena/61ebd543-fl4`, base `62afd1b`)

Claimed 2026-11-16. `origin/main` = `62afd1b` (PR #7 merged) at claim time. Root `index.html`,
`pages/`, `data/*.json`, `tools/build_site.py`, `tools/validate.py`, `signals/`, `data/signals/`,
`tools/build_signals.py`, `tools/check_signals.py`, `prereg/` and `data/readiness*.json` are
**owned by other sessions and are not modified by this session.** The additive root nav entry
named in the original claim was **not taken**: `main` advanced through PRs #13–#17 while this
session worked, and root `index.html` / `tools/build_site.py` are now contested shared outputs.
The lab section is reachable from its own URL and links back to every other section; adding the
one root nav entry is left to the integration pass (recorded as L-F-18).

**This session's scope = a new, namespaced section `lab/` ("Decision Lab")** plus its own data
(`data/lab/*.json`), builder (`tools/build_lab.py`) and checker (`tools/check_lab.py`). It adds
the requirement register for the full brief, the decision-readiness table, the verified results
feed, the availability capture, the depth/deficiency view, the model specification, the
leaderboard, the correlation protocol, the price policy, the questions and suggestions boards,
the repo review, the sources register and the flagged register. 16 pages, no external
dependencies, all links relative.

| Task | Status | Owner (session) | File scope | Sources / verification | Irregularities |
|---|---|---|---|---|---|
| T20 Claim + branch hygiene | done | `61ebd543` | `COORDINATION.md` | claim pushed before work started; `git pull --rebase` before each push | none |
| T21 Official capture: Week 10 2026 injury report (full recapture, all clubs, all rows) | done (commit `3d6249a`) | `61ebd543` | `data/lab/injuries_week10_2026.json`, `lab/availability.html` | https://www.nfl.com/injuries/league/2026/reg10 (8/8 chunks, captured 2026-11-16) | 347 rows / 28 clubs; 171 carry a game status; Out 70, Questionable 90, Doubtful 11, blank 176. One IND row (Jonathan Taylor) truncated at a chunk boundary — all three of its fields are null (L-F-02). Three row sets for the same page now exist (L-F-01, L-F-16). |
| T22 Official capture: 2026 results feed, weeks 1–10 (verified final scores) | done (commit `27dd699`) | `61ebd543` | `data/lab/results_2026.json`, `lab/results.html` | https://www.nfl.com/schedules/2026/by-week/week-N (weeks 1–10); 11 game centres re-checked | 150 rows = **148 FINAL** (136 weeks 1–9 + 12 week 10) + 2 not-FINAL (steelers-at-bengals LIVE, chargers-at-ravens not kicked off), stored blank (L-F-05). An earlier draft of the register said 149/13; corrected. |
| T23 Official capture: Week 10 venue/stadium/Game Book from the game centre | done (commit `b82f820`) | `61ebd543` | `data/lab/fixtures_week10_2026.json`, `lab/fixtures.html` | https://www.nfl.com/games/<game_id>-2026-reg-10 for all 14 fixtures | 12 of 14 publish a Game Book PDF link; 2 null (L-F-11, links are Cloudinary-signed and will expire). Game-centre injury cards use coarser practice wording than the report; the report wins (L-F-08). |
| T24 Requirement register for the full brief + decision-readiness table | done | `61ebd543` | `data/lab/requirements.json`, `lab/index.html` | 78 rows (R-01…R-70 + M-71…M-78); each names its blocking gate and the number that clears it | 37 met / 23 partial / 18 blocked. Every `where_published` target is checked to exist by `tools/check_lab.py`. |
| T25 Price-data policy + snapshot/ledger design (drift alarms, immutability, cadence) | done | `61ebd543` | `data/lab/price_policy.json`, `lab/price-policy.html` | https://www.nfl.com/legal/terms/ section 1.3 quoted verbatim (page updated May 16 2024); §§15–18 not read and not characterised | policy default POL-A (derived analysis only) chosen as the strictest default, not by the owner. No price, odds, line or CLV exists anywhere in the repo (L-F-13). |
| T26 Model spec: side→total→ML, probability+inputs, two totals, ablations, priors | done | `61ebd543` | `data/lab/models.json`, `lab/models.html` | 2026 rulebook changes 6-1-3, 6-1-5, 6-1-6, 19-2 quoted from https://operations.nfl.com/rules-officiating/2026-nfl-rulebook | no model fitted; every coefficient and every regime prior is null. Ablations by refit, never a fixed point penalty. |
| T27 Leaderboard: proper-score divisions, two-stage escrow, control baselines, demotion gate, pre-registration | done | `61ebd543` | `data/lab/leaderboard.json`, `lab/leaderboard.html` | board empty by design; one shadow baseline B0 registered | **Defers to `prereg/REGISTRATION.md` on main** (L-F-19): this section restates governance another session already froze. Where they disagree, the frozen registration wins. |
| T28 Question bank (known / unknown / needed to decide) | done | `61ebd543` | `data/lab/questions.json`, `lab/questions.html` | 21 questions; 12 blocking | every gate named in `requirements.json` is defined here (checked by `tools/check_lab.py`). Q-GOV-01 is defined but not yet referenced by a requirement. |
| T29 Suggestions review board with selectable paths | done | `61ebd543` | `data/lab/suggestions.json`, `lab/suggestions.html` | browser-local selection only; nothing auto-approved on silence | 18 suggestions; approval requires editing `status` in the JSON and naming an approver |
| T30 Repo review line by line with official links + irregularity flags | done | `61ebd543` | `data/lab/repo_review.json`, `lab/repo-review.html` | 85 tracked files listed with a blob link each; 8 findings | reviewed against `origin/main` at `4d76668`; link points at main where the file exists there, otherwise at this branch |
| T31 Sources register + flagged-for-review page | done | `61ebd543` | `data/lab/sources.json`, `data/lab/flagged.json`, `lab/sources.html`, `lab/flagged.html` | 12 sources (L-S01…L-S12); only 6 marked `read` | 19 flags (L-F-01…L-F-19), each with an https source link. A source marked `not-read` verifies nothing. |
| T32 Builder + checker | done | `61ebd543` | `tools/build_lab.py`, `tools/check_lab.py` | `build_lab.py --fail-on-warn` and `check_lab.py` both pass | builder fails on a leaked `None`, on a column no row carries, and on any price-derived value reaching a page; checker fails on a sourced row with no official link |
| T33 Integration: rebase, link check, PR, merge, Pages | done (PR #18 merged `fa0ac93`; PR #19 `edbd9d5`; Pages built for both; lab/ verified live) | `61ebd543` | repo-wide (additive only) | rebase onto `origin/main`, rebuild, run both checkers, PR, merge, confirm Pages | root nav entry deliberately not taken (see header) |

## Log — session `61ebd543`

- 2026-11-16 — PR #21 (https://github.com/sassnarep3-star/FL4/pull/21) merged as `9990583`; Pages build **built**. It corrects two stale counts that were printed on the live page: R-22 said the readiness table had 86 rows (it publishes 78) and R-16 said the luck panel had 4 tests (it has 8).
- 2026-11-16 — Final state of this session: PRs #18 (`fa0ac93`), #19 (`edbd9d5`), #20 (`f256672`) and #21 (`9990583`) are all merged to `main`, with a `built` Pages build for each. The section is live at https://sassnarep3-star.github.io/FL4/lab/. Remaining work for a future session, all named on the site: the root nav entry (L-F-18), moving raw captures out of the published tree (SG-06 / Q-STORE-01), the depth source (SG-03 / Q-DEPTH-01), the snapshot runner (SG-02 / Q-SNAPSHOT-01), Game Book parsing (SG-04 / Q-BOOKS-01) and the price decision (SG-01 / Q-PRICE-01).

- 2026-11-16 — **Merged and published.** PR #18 (https://github.com/sassnarep3-star/FL4/pull/18, `arena/61ebd543-fl4` -> `main`) merged as `fa0ac93` after `verify.yml` passed on the PR head (run 43790543497, 7s). Pages build for `fa0ac93`: **built**. Live at https://sassnarep3-star.github.io/FL4/lab/ — the landing page, the readiness table and `lab/depth.html` were fetched over HTTPS and render.
- 2026-11-16 — PR #19 (https://github.com/sassnarep3-star/FL4/pull/19) merged as `edbd9d5`; Pages build **built**. It fixes one live defect found by fetching the deployed page: the readiness table rendered `where_published` as `lab/x.html` from inside `lab/index.html`, which resolved to `/FL4/lab/lab/x.html`. Lesson for the next session: a green build is not a verified deploy — fetch the published URL.
- 2026-11-16 — PR #20 (https://github.com/sassnarep3-star/FL4/pull/20) fixes two cosmetic rendering defects found the same way: a literal `&mdash;` in a table header and duplicated step numbers in the suggestions workflow list.
- 2026-11-16 — Verification before the merge: `tools/build_lab.py --fail-on-warn` (14 pages, 0 price-derived values, 0 auto-flagged rows); `tools/check_lab.py` (0 failures, 0 warnings across 78 requirement rows, 21 questions, 19 flags, 12 sources, 115 reviewed files); `tools/build_site.py` + `tools/validate.py` PASS (489 rows in 20 tables); `tools/build_signals.py --fail-on-warn` + `tools/check_signals.py` PASS; `tools/capture_w10.py --check` and the injury-parser fixture pass in `verify.yml`.

- 2026-11-16 — **Merge conflict resolved without discarding anyone's work.** Rebasing this branch onto `origin/main` (`4d76668`) conflicted in `COORDINATION.md`, because other sessions had rewritten the top of the file while this session worked. Resolution: both boards are kept — this session's board at the top, the other sessions' board below under a heading. No task row, log entry or handoff from any other session was removed. Other sessions' files (`prereg/`, `data/readiness.json`, `tools/capture_w10.py`, `data/flags.json` F-27…F-31, `data/repo_review.json` R-08…R-12) are untouched by this branch.
- 2026-11-16 — Claimed T20–T33 with scope `lab/`, `data/lab/`, `tools/build_lab.py`, `tools/check_lab.py`. `git ls-remote` showed PR #7 as the only merged PR at claim time; PRs #13–#17 from other sessions merged into `main` while this session worked, so this branch is rebased onto `origin/main` before the final push.
- 2026-11-16 — Week 10 injury report re-read in 8/8 chunks and transcribed verbatim (347 rows, 28 clubs). Earlier sessions' captures of the same page (160-row manual set, 76-row Out/Doubtful set) are retained and not merged; the count difference is a rule difference plus a live-document difference, published as L-F-01 rather than reconciled away.
- 2026-11-16 — Results feed: 150 rows. Count corrected from an earlier draft's "149 FINAL (136 + 13)" to **148 FINAL (136 weeks 1–9 + 12 week 10)** after the two non-FINAL week 10 games were confirmed from the official schedule page and the game centres. `49ers-at-cowboys` verified FINAL 46–40 against its game centre.
- 2026-11-16 — All 14 week 10 venue/stadium/Game Book links transcribed from the official game centres. Two fixtures have no Game Book (one LIVE, one not kicked off); both are null, not guessed.
- 2026-11-16 — Built the section: 16 pages + `data/lab/*.json` (14 files) + builder + checker. `tools/build_lab.py --fail-on-warn` reports 0 price-derived values and 0 auto-flags; `tools/check_lab.py` reports 0 failures and 0 warnings across 14 pages, 78 requirement rows, 21 questions, 19 flags and 12 sources.
- 2026-11-16 — Correction: an early draft of `requirements.json` cited `tools/build_lab.py` and 13 `lab/*.html` pages that did not exist. All `where_published` targets now exist and are verified by the checker at build time.
- 2026-11-16 — Correction: an early draft of `flagged.json` (L-F-05) said week 10 contributed 13 FINAL games. Corrected to 12 of 14, with the season total at 148.
- 2026-11-16 — Deference recorded: `main` carries `prereg/REGISTRATION.md`, which freezes the signals section's strategies, gates, leaderboard and correlation protocol with hash checks. This section's leaderboard rules are a parallel restatement and are flagged (L-F-19) rather than presented as new.

---


# OTHER BOARDS — sessions `810f9f1f` / `c7c287d6` / `c75aedbd` / `6eca50ae` / `f54713e3` / `121f05ad` (already on `main`)

> PRs #1–#6 have already integrated the evidence-first dashboard and a separate, verified `signals/` origination section. This branch must not create another site or alter that section's methodology/data. The current follow-up is limited to distinct root-dashboard improvements: a blank 2nd/3rd/4th-string tracker, precise fair-price/joint-probability formulas, browser-local suggestion selection, source/privacy corrections, and a stricter root-page row audit. One narrowly scoped privacy correction is also claimed for the completed Signals section: remove an Arena-provided session-location observation from `Q-LEGAL-01` and regenerate only `signals/questions.html`. Historical session boards remain below.

## Current task board

| Task | Status | Owner (Arena session) | File scope | Sources / verification | Irregularities |
|---|---|---|---|---|---|
| T12 Root dashboard quality follow-up + targeted privacy correction | done (implementation) | `121f05ad`, `arena/121f05ad-fl4` | Root `data/{sources,strategies,questions,requirements,suggestions,flags,injuries_w10_2026,repo_review}.json`, new `data/replacement_tiers.json`, `tools/{build_site,validate}.py`, `assets/{app.js,style.css}`, `decision-lab.html`, generated root pages, README; one Signals privacy-only edit to `data/signals/questions.json` and generated `signals/questions.html` | NFL Week 10 report, NFL Next Gen Stats / stats / Game Books / team directory / terms; NIST and scikit-learn docs; 423 source/evidence rows audited; PRs #3–#6 supply the main origination framework | Keep depth slots blank/unverified. No licensed historical odds, fitted model, measured correlations, or strategy results. F-19 flags the NFL odds-widget / 2026 partnership-list discrepancy. Signals change only removes an environment-location observation; no methodology or injury data changes. Existing Pages workflow is preserved. |
| T13 Integration, PR/merge, Pages confirmation | done | arena/f54713e3-fl4 | repo-wide | Root build (10 pages, 423 sourced rows) + validate PASS; Signals build (14 pages, 10 checks) + check_signals PASS; PR #7 merged to main at 62afd1b; GitHub Pages status `built` for commit 62afd1b, HTTPS enforced, live at https://sassnarep3-star.github.io/FL4/ and /signals/ | Session f54713e3 ran build_site.py, validate.py, build_signals.py --fail-on-warn, check_signals.py, gh Pages API; fetched live homepage to confirm rendering |
| T14 Decision-readiness table, injury-scope and count reconciliation, unverifiable-reference flags | done (PR #8 merged to `main` at `1c018cc`; Pages build `built`, deploy success; F-20–F-23 published) | Arena session `6eca50ae`, branch `arena/6eca50ae-fl4` (fixed by Arena; `session-<id>/<task>` branches are not used in this session) | `data/readiness.json` (new), `data/flags.json` (append F-20–F-23 only), `tools/build_site.py` (index section only), generated `index.html` and `pages/flagged.html` | Official NFL Week 10 2026 injury page https://www.nfl.com/injuries/league/2026/reg10 (fetched 2026-11-16; chunks 0–1 of 8); repo files; no other official pages | Full 8-chunk recapture NOT completed this session; 254/279 counts not reproduced; VR-/VQ- references not found in repo |
| T15 Session verification + PR/merge + Pages confirmation | in progress | `arena/810f9f1f-fl4` | `COORDINATION.md` only — claim, verification log, PR and merge | `tools/build_site.py` + `tools/validate.py`; `tools/build_signals.py --fail-on-warn` + `tools/check_signals.py`; official spot-checks (see Log) | None — all unknowns already blank and flagged (F-01 price feed, F-02 depth source); nothing fabricated |
| T16 Pre-registration freeze, two-sided strategy fields, leaderboard divisions / demotion gate / controls / removal-of-luck panel, decision-readiness table, Week 10 re-verification and correction, depth-route check | done (scope-limited; blocked items flagged on the signals Flagged page as F-19 to F-25; root Flagged page F-24 to F-26) | `c7c287d6`, `arena/c7c287d6-fl4` (single branch fixed by Arena; the brief's `session-<id>/<task>` branches were not created) | `prereg/` (new), `data/readiness.json` (new), `data/injuries_w10_2026.json`, `data/signals/{strategies,gates,leaderboard,injuries_week10_2026,flagged}.json`, `data/flags.json`, `REQUIREMENTS.md` (one line), `tools/{build_site,build_signals,validate}.py`, generated `index.html`, `pages/*.html`, `signals/*.html`, `signals/data/*.json`, `COORDINATION.md` | Official Week 10 2026 report read in 8/8 chunks on 2026-11-16 (`https://www.nfl.com/injuries/league/2026/reg10`); per-club status tallies for all 28 clubs re-derived from that read; NFL Terms Section 1.3 (`https://www.nfl.com/legal/terms/`) read; depth-chart URL tested (`https://www.nfl.com/teams/seattle-seahawks/depth-chart`, 404) | Corrections: 12 LAC/BAL rows added, 1 unsupported IND row removed, LAC @ BAL game note fixed, IND Questionable 2 to 1 (signals F-17, F-18; root F-24). Not done (blocked; flags carry the reason): automated multi-day captures (signals F-19, root F-25: NFL terms); full listed-player row count (signals F-23); depth source for any club (signals F-20, root F-26); snap counts, inactive lists, reserve list, venues, price data, results feed, 136-game log (signals F-25). Registration commit: `b5d9623`. PR: https://github.com/sassnarep3-star/FL4/pull/13 (to `main`; merge recorded in the follow-up log entry). |
| T18 Week 10 private-layer reconciliation: private 347-row transcription vs public files, counts-only summary, capture validator | done (PR #14 merged to `main` at `d6e137d`; verify run 43788134399 success; Pages build and deploy success for `d6e137d`) | `c75aedbd`, `arena/c75aedbd-fl4` | `tools/capture_w10.py`, `data/capture_summary_w10_2026.json`, `private/` (git-ignored, not published), `data/flags.json` (F-27 to F-31 only), `data/repo_review.json` (R-08 to R-12 only), `data/sources.json` (S32 only), `.github/workflows/verify.yml` (one capture step) | nfl.com/injuries/league/2026/reg10 read in 8 chunks on 2026-11-16 (transcription); nfl.com/schedules/2026/reg10 (S32) | Private file matches public `data/injuries_w10_2026.json` on all 171 designated rows after ARI/AZ normalisation. `data/injuries_week10_2026.json` omits 6 designated rows (F-31). Public row-level tables still published (F-27, reviewer decision). |

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
