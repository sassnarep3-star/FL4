# COORDINATION.md — shared task board

Repo: `sassnarep3-star/FL4` · Current Arena branch: `arena/810f9f1f-fl4` (branched from `62afd1b` of `main`; status `active`)
Live site: https://sassnarep3-star.github.io/FL4/

Statuses: `unclaimed` · `in progress` · `done` · `needs review` (flags do not block publication).

> PRs #1–#6 have already integrated the evidence-first dashboard and a separate, verified `signals/` origination section. This branch must not create another site or alter that section's methodology/data. The current follow-up is limited to distinct root-dashboard improvements: a blank 2nd/3rd/4th-string tracker, precise fair-price/joint-probability formulas, browser-local suggestion selection, source/privacy corrections, and a stricter root-page row audit. One narrowly scoped privacy correction is also claimed for the completed Signals section: remove an Arena-provided session-location observation from `Q-LEGAL-01` and regenerate only `signals/questions.html`. Historical session boards remain below.

## Current task board

| Task | Status | Owner (Arena session) | File scope | Sources / verification | Irregularities |
|---|---|---|---|---|---|
| T12 Root dashboard quality follow-up + targeted privacy correction | done (implementation) | `121f05ad`, `arena/121f05ad-fl4` | Root `data/{sources,strategies,questions,requirements,suggestions,flags,injuries_w10_2026,repo_review}.json`, new `data/replacement_tiers.json`, `tools/{build_site,validate}.py`, `assets/{app.js,style.css}`, `decision-lab.html`, generated root pages, README; one Signals privacy-only edit to `data/signals/questions.json` and generated `signals/questions.html` | NFL Week 10 report, NFL Next Gen Stats / stats / Game Books / team directory / terms; NIST and scikit-learn docs; 423 source/evidence rows audited; PRs #3–#6 supply the main origination framework | Keep depth slots blank/unverified. No licensed historical odds, fitted model, measured correlations, or strategy results. F-19 flags the NFL odds-widget / 2026 partnership-list discrepancy. Signals change only removes an environment-location observation; no methodology or injury data changes. Existing Pages workflow is preserved. |
| T13 Integration, PR/merge, Pages confirmation | done | arena/f54713e3-fl4 | repo-wide | Root build (10 pages, 423 sourced rows) + validate PASS; Signals build (14 pages, 10 checks) + check_signals PASS; PR #7 merged to main at 62afd1b; GitHub Pages status `built` for commit 62afd1b, HTTPS enforced, live at https://sassnarep3-star.github.io/FL4/ and /signals/ | Session f54713e3 ran build_site.py, validate.py, build_signals.py --fail-on-warn, check_signals.py, gh Pages API; fetched live homepage to confirm rendering |
| T14 Decision-readiness table, injury-scope and count reconciliation, unverifiable-reference flags | done (PR #8 merged to `main` at `1c018cc`; Pages build `built`, deploy success; F-20–F-23 published) | Arena session `6eca50ae`, branch `arena/6eca50ae-fl4` (fixed by Arena; `session-<id>/<task>` branches are not used in this session) | `data/readiness.json` (new), `data/flags.json` (append F-20–F-23 only), `tools/build_site.py` (index section only), generated `index.html` and `pages/flagged.html` | Official NFL Week 10 2026 injury page https://www.nfl.com/injuries/league/2026/reg10 (fetched 2026-11-16; chunks 0–1 of 8); repo files; no other official pages | Full 8-chunk recapture NOT completed this session; 254/279 counts not reproduced; VR-/VQ- references not found in repo |
| T15 Session verification + PR/merge + Pages confirmation | in progress | `arena/810f9f1f-fl4` | `COORDINATION.md` only — claim, verification log, PR and merge | `tools/build_site.py` + `tools/validate.py`; `tools/build_signals.py --fail-on-warn` + `tools/check_signals.py`; official spot-checks (see Log) | None — all unknowns already blank and flagged (F-01 price feed, F-02 depth source); nothing fabricated |
| T16 Pre-registration freeze, two-sided strategy fields, leaderboard divisions / demotion gate / controls / removal-of-luck panel, decision-readiness table, Week 10 re-verification and correction, depth-route check | done (scope-limited; blocked items flagged on the signals Flagged page as F-19 to F-25; root Flagged page F-24 to F-26) | `c7c287d6`, `arena/c7c287d6-fl4` (single branch fixed by Arena; the brief's `session-<id>/<task>` branches were not created) | `prereg/` (new), `data/readiness.json` (new), `data/injuries_w10_2026.json`, `data/signals/{strategies,gates,leaderboard,injuries_week10_2026,flagged}.json`, `data/flags.json`, `REQUIREMENTS.md` (one line), `tools/{build_site,build_signals,validate}.py`, generated `index.html`, `pages/*.html`, `signals/*.html`, `signals/data/*.json`, `COORDINATION.md` | Official Week 10 2026 report read in 8/8 chunks on 2026-11-16 (`https://www.nfl.com/injuries/league/2026/reg10`); per-club status tallies for all 28 clubs re-derived from that read; NFL Terms Section 1.3 (`https://www.nfl.com/legal/terms/`) read; depth-chart URL tested (`https://www.nfl.com/teams/seattle-seahawks/depth-chart`, 404) | Corrections: 12 LAC/BAL rows added, 1 unsupported IND row removed, LAC @ BAL game note fixed, IND Questionable 2 to 1 (signals F-17, F-18; root F-24). Not done (blocked; flags carry the reason): automated multi-day captures (signals F-19, root F-25: NFL terms); full listed-player row count (signals F-23); depth source for any club (signals F-20, root F-26); snap counts, inactive lists, reserve list, venues, price data, results feed, 136-game log (signals F-25). Registration commit: `b5d9623`. PR: https://github.com/sassnarep3-star/FL4/pull/13 (to `main`; merge recorded in the follow-up log entry). |
| T18 Week 10 private-layer reconciliation: private 347-row transcription vs public files, counts-only summary, capture validator | in progress (claimed 2026-11-16; branch `arena/c75aedbd-fl4`) | `c75aedbd`, `arena/c75aedbd-fl4` | `tools/capture_w10.py`, `data/capture_summary_w10_2026.json`, `private/` (git-ignored, not published), `data/flags.json` (F-27 to F-31 only), `data/repo_review.json` (R-08 to R-12 only), `data/sources.json` (S32 only), `.github/workflows/verify.yml` (one capture step) | nfl.com/injuries/league/2026/reg10 read in 8 chunks on 2026-11-16 (transcription); nfl.com/schedules/2026/reg10 (S32) | Private file matches public `data/injuries_w10_2026.json` on all 171 designated rows after ARI/AZ normalisation. `data/injuries_week10_2026.json` omits 6 designated rows (F-31). Public row-level tables still published (F-27, reviewer decision). |

## Log

- 2026-11-16 — Session `c75aedbd` on `arena/c75aedbd-fl4`. Re-scoped after `main` moved. Its T16 (PR #13, `c7c287d6`) already covers the Week 10 re-verification (same totals: 70 Out, 11 Doubtful, 90 Questionable) and the pre-registration freeze (`prereg/`). The session therefore drops its own duplicates: its registry (`data/prereg.json`, `tools/check_prereg.py`), its price-policy/price-snapshot/results-feed drafts (`data/price_policy.json`, `data/price_snapshots.json`, `data/results_feed.json`), and its readiness register (main's `data/readiness.json` stays). These files remain in history on this branch (commits `edc1ec5`, `66f953b`) and are not published. None of them is claimed; a future claim is needed before they return.
- 2026-11-16 — T18 reconciliation result (`c75aedbd`). The private 347-row transcription (`private/captures/nfl_injuries_w10_2026_reg10.psv`) and the public `data/injuries_w10_2026.json` agree on all 171 designated rows (players, statuses, injury text) after the Arizona code is normalised (public `ARI` on 9 rows; page `AZ`). `data/signals/injuries_week10_2026.json` has 81 Out or Doubtful rows, matching 70 + 11. `data/injuries_week10_2026.json` has 75 and omits 6 designated rows (GB Micah Parsons; LAC Branson Taylor, Brenen Thompson, Isas Waxter, Kendall Williamson; BAL Jaylinn Hawkins). Logged as F-31; not changed here.
- 2026-11-16 — Flags added by `c75aedbd`: F-27 (player-level public data, terms s.1.3), F-28 (page read after 12 finals), F-29 (ARI/AZ code on public rows), F-30 (private transcription integrity), F-31 (75-row Out/Doubtful list). Earlier draft flags were dropped where main already covers them (Arden Key: main removed the row on 16 Nov, which matches the page; the Signals omission: main corrected it; reserve list, 136-game corpus, depth route: covered by F-22, F-25, F-26 on main). Repo review R-08 to R-12 added after main's R-07 (R-13 dropped: registry now on main).
- 2026-11-16 — Corrections by `c75aedbd` after a second pass: (1) an early draft said row-level tables had been removed from the public injuries page. That was wrong; the public player table is still rendered (F-27). (2) Per-game links in an early results feed were built from a URL pattern and never fetched; removed from the branch. (3) Headline specifics not confirmed on the official page were not used.
- 2026-11-16 — Open for the reviewer (`c75aedbd` items): public row-level files and the player table (F-27); pre-kickoff snapshot (F-28); ARI/AZ normalisation (F-29); the 75-row list (F-31); IND Arden Key is resolved on main (row removed), no action.

- 2026-11-16 `c7c287d6` — Merge conflict (session `c7c287d6`): when T16 was about to be pushed, `origin/main` had moved to `65bca2a` (PR #12). The conflict was on `COORDINATION.md` (board rows and log), `data/flags.json` (the IDs F-20 to F-22 were used by two sessions for different items), `data/readiness.json` (same path, different content), and the generated `index.html`, `pages/executive-summary.html` and `pages/flagged.html`. Resolution: kept `main`'s readiness register, landing table and root F-18 to F-23 verbatim, with update notes; this session's task is T16 and its root flags are F-24 to F-26; updated `main`'s readiness rows that this work changed (pre-registration, Week 10 capture), leaving their status and gate logic in place; added update notes to `main`'s F-18 and F-20 where the 160-row count they cite is superseded. No other session's content was discarded. Generated pages were rebuilt from the merged sources, not hand-merged.
- 2026-11-16 `c7c287d6` — Claimed on `arena/c7c287d6-fl4` (base `62afd1b` on `main`) and pushed the claim (`d51ad1e`) before any work. The claim was first recorded as T14 and then as T15; it is T16 here because `main` already holds T14 (session `6eca50ae`) and T15 (session `810f9f1f`, verification-only). Scope is limited to what can be verified from official sources in this session; the rest of the brief is recorded as blocked, not silently dropped.
- 2026-11-16 `c7c287d6` — PR https://github.com/sassnarep3-star/FL4/pull/13 opened from `arena/c7c287d6-fl4` to `main` (head `7e20b78`). Merged without waiting for review, as the brief requires; flagged items do not block merge. Pages deploy and the merge commit are recorded in a follow-up entry.
- 2026-11-16 `c7c287d6` — **Registration.** The pre-registration is the commit that adds `prereg/` — full hash `b5d9623f682d2a3b7cd8bb4f3884cf34b2721c41` (short `b5d9623`). It freezes the four files whose SHA-256 hashes are in `prereg/registration.json`: `data/signals/{strategies,gates,leaderboard,correlations}.json`. `tools/build_signals.py` re-checks those hashes on every build. No strategy has been evaluated and no evaluation window has opened. The registration does not set the reviewer-owned thresholds.
- 2026-11-16 `c7c287d6` — **Week 10 re-verification.** Read the official report in 8/8 chunks (`https://www.nfl.com/injuries/league/2026/reg10`). Re-derived per-club Out, Doubtful and Questionable counts for all 28 clubs on the report: 70 Out, 11 Doubtful, 90 Questionable. The corrected dataset totals match exactly. Corrections: (a) the Monday LAC @ BAL game had no rows, and its game note said "no flagged players" although the page lists 10 Chargers and 2 Ravens rows; 12 rows added to the root capture and 5 Out/Doubtful rows to the signals capture. (b) Arden Key (IND) was listed Hamstring / Questionable, but the page shows no injury and no game status; row removed. (c) IND Questionable count 2 to 1. (d) An unsourced note on NFL filing deadlines was removed from the signals capture notes, and the "Avery-adjacent" wording in note A-2 was corrected.
- 2026-11-16 `c7c287d6` — **Seattle and Cincinnati.** Official table: Seattle lists 15 players, 4 with a status (all Out); Cincinnati lists 9, 4 with a status (1 Out, 3 Doubtful). The current captures match. The brief's "injury-free" display and the 254 and 279 row counts describe an earlier state that is not in this repository, so they could not be reproduced (F-23).
- 2026-11-16 `c7c287d6` — **Depth route (a).** `https://www.nfl.com/teams/seattle-seahawks/depth-chart` returned "404 - Flag on the Play." No verified per-club depth page exists. Route (b) (snap counts) has no verified official source. The backup-deficiency feature therefore remains unbuilt (F-20).
- 2026-11-16 `c7c287d6` — **Terms.** NFL.com Terms Section 1.3 prohibits systematic retrieval of data without express prior written consent (page dated May 16, 2024). Automated daily or multi-day captures are therefore not built; they need a written decision first (F-19).
- 2026-11-16 `c7c287d6` — **Built.** Two strategy fields per strategy (what would make us believe it / drop it); divisions (singles, game parlays, same-game parlays, prop combos) with a joint-evidence gate for combos; stage-1 and stage-2 ranking with signal-versus-staking separation; required control baseline; demotion gate D-1 to D-4 (thresholds null, so it fails closed); removal-of-luck panel; backtest-exclusion rule; a decision-readiness table of 30 requirement rows on the landing page. Checks: 13 build-time checks pass, including the registration hash check and prospective-only leaderboard check. `tools/validate.py` now accepts in-site relative links in table cells, and still checks HTTPS and the source allowlist for external links.
- 2026-11-16 `c7c287d6` — **Branch rule.** The brief asks for `session-<id>/<task>` branches and git worktrees. Arena fixes this session to `arena/c7c287d6-fl4`, so no other branch was created. Parallel-session safety is handled by file scope and this board.
- 2026-11-16 `c7c287d6` — **Clone note.** The checkout is shallow (`git rev-parse --is-shallow-repository` returns true). Git history beyond the visible commits was not searched. The 136-game log is not in the working tree (F-25).
- 2026-11-16 — Merge conflict (session `6eca50ae`): after PR #8 landed, `origin/main` carried another session's T13 closure (PR #9, `arena/f54713e3-fl4`). The conflict was on the task-board rows only. Resolved by keeping that session's T13 row verbatim and this session's T14 closure row; no other session's content was discarded. Branch then merged `origin/main` (includes PR #9).
- 2026-11-16 — T14 closed. PR #8 (https://github.com/sassnarep3-star/FL4/pull/8) merged with a merge commit (`1c018cc`) after `verify.yml` succeeded (run 43786847690). Pages: build and deploy succeeded for `1c018cc`; the live dashboard renders the Decision readiness table (checked at https://sassnarep3-star.github.io/FL4/?v=1c018cc; an unparameterised fetch returned a cached copy). Not done under T14: the full Week 10 recapture, the VR-/VQ- evidence, any price, depth, schedule, snapshot or model work. These remain blocked rows in the readiness table.
- 2026-11-16 — Session `6eca50ae` claimed T14 on branch `arena/6eca50ae-fl4` (the only branch this session may use; the multi-branch naming rule above is superseded by Arena's fixed-branch rule). Scope limited to the files listed. A large part of the 2026-11-16 brief (price feed, results ingest, depth charts for 32 clubs, Game Books, snap counts, multi-season archives, shadow model, daily snapshots) depends on sources or data that are not in this repository, so those items are published as blocked rows, not built.
- 2026-11-16 — Verification performed before claiming: (1) live official page https://www.nfl.com/injuries/league/2026/reg10 chunks 0–1 read; Lions rows Kerby Joseph, Cade Mays and D.J. Reed show Game Status "Out" on the live page and in `data/injuries_w10_2026.json` (the blank-cell defect described in the brief is not present in the current file); 23 sampled player rows match exactly between the live page and the local file; (2) `data/injuries_w10_2026.json` holds 160 rows (66 Out, 10 Doubtful, 84 Questionable) across 14 games; `tools/fetch_injuries.py` documents a keep-only-Out/Doubtful rule, which contradicts the data (flag F-20); (3) grep of the whole repo found no `VR-` or `VQ-` reference, so those cited items cannot be checked here (flag F-22); (4) no "what would change our mind" field, no schedule/venue dataset, and no pre-registration commit exist in the repo.
- 2026-11-16 — Session `arena/810f9f1f-fl4` claimed T15 (verification + PR/merge + Pages confirmation) on branch `arena/810f9f1f-fl4`, branched from `62afd1b` of `main` (diverged: origin/main advanced to 1c018cc/PR #8 while this session worked). Claim committed; file scope: `COORDINATION.md` claim/log only — no data or page changes needed.
- 2026-11-16 — Pre-flight verification on `62afd1b`: `tools/build_site.py` + `tools/validate.py` PASS (11 pages; 423 source/evidence rows; every factual row links to an official source). `tools/build_signals.py --fail-on-warn` + `tools/check_signals.py` PASS (14 pages; 0 broken links; no fabricated edge/correlation values). Injury-parser fixture PASS ("5 kept as Out/Doubtful across 4 clubs"). Official spot-checks reachable: `nfl.com/injuries/league/2026/reg10` (6 rows spot-verified byte-for-byte against the live official report: Patrick, Yankoff, Harrison, Joseph, Mays, Reed), `nfl.com/standings/`, `nfl.com/schedules/2026/week-10`, GitHub repo page. Re-verify on the merged tree before the PR merge.
- 2026-11-14 — Inspected the repository and `main` after another session's work had already merged as PR #2 (`388414f`). PR #1 and PR #2 are both merged; GitHub Pages is configured at `https://sassnarep3-star.github.io/FL4/`. The Pages deployment run for `388414f` completed successfully (run `43549635924`, workflow `Publish site to GitHub Pages`); `gh api repos/sassnarep3-star/FL4/pages/builds/latest` reported `built`; the published URL fetch returned the site. No open PRs existed. Do not replace that integrated, feature-rich site with a smaller duplicate static app.
- 2026-11-14 — `origin/main` advanced from `388414f` to `ce7b73e` while this branch was in progress. PRs #3–#6 from session `94107c0d` added the independently verified Signals & origination section, 16 strategy hypotheses, 15 gates, an 11-pair correlation protocol, 26 questions, 16 review flags, a cross-capture injury parser, and build checks. Its Pages publish and verification runs passed. This session now avoids duplicating that section and limits follow-up to root-dashboard affordances that remain distinct.
- 2026-11-14 — T12 implemented on the root dashboard: added six blank offense/defense 2nd/3rd/4th-string field templates; settlement-aware fair-price and joint-combo formulas; a point-in-time/player-opportunity/skill-versus-luck blueprint; browser-local suggestion selectors; official weekly report links on injury rows; an official-source row/link validator; and a root-only citation/terms update. In the completed Signals section, only the personal-location sentence in Q-LEGAL-01 was removed; strategy and injury data are unchanged.
- T12 verification: `python3 tools/build_site.py` + `tools/validate.py` passed (11 root HTML pages; 423 source/evidence rows in 19 tables); `python3 tools/build_signals.py --fail-on-warn` + `tools/check_signals.py` passed (10 checks); JS syntax and local-storage harness passed; injury parser fixture passed; 72 root/Signals HTTP requests returned 200. No odds, model estimates, player depth assignments, correlation values, ROI, picks, or rewards were created. F-19 records the official odds-widget / partnership partner-list mismatch without treating either as an odds feed.
- Official methodology sources verified for the strategy specification:
  - NFL Football Operations, Next Gen Stats: https://operations.nfl.com/game-operations-logistics/technology/performance-tracking-data-next-gen-stats — official description of tracking-derived fields; this does not establish that raw tracking data is public or licensed here.
  - NFL player statistics: https://www.nfl.com/stats/player-stats/ — official navigation/source, not treated as a saved statistical dataset.
  - NFL Game Books support: https://support.nfl.com/hc/en-us/articles/35869678028180-Game-Books — official description of Game Book PDF access in game centers.
  - NFL injury report index: https://www.nfl.com/injuries/ — official discovery route; direct `/league/2026` returned 404, while the index/week selector and exact Week 10 route resolved. The 2025 Week 8 report body/title mismatch remains flagged; no such records were added.
  - NFL Week 10 2026 injury report (S31): https://www.nfl.com/injuries/league/2026/reg10 — direct weekly source attached to each root snapshot row alongside the NFL player page.
  - NFL.com Terms and Conditions (S29): https://www.nfl.com/legal/terms/ — reviewed terms prohibit systematic retrieval absent express prior written consent; no scraping or automatic NFL refresh is configured.
  - NFL odds-widget FAQ (S27) and 2026 sportsbook partnership notice (S28) list different partner sets; this is explicitly flagged as F-19 and neither page is treated as a market feed or licence.
  - NFL roster page: https://www.nfl.com/teams/new-england-patriots/roster — official roster view but no explicit depth ordering, so a roster is not treated as a depth chart.
  - NFL 2026 Rulebook: https://operations.nfl.com/rules-officiating/2026-nfl-rulebook — official rules reference; no rule-based numeric model values inferred.
  - NIST correlation glossary: https://www.itl.nist.gov/div898/handbook/glossary.htm — correlation definition; a coefficient is not a joint parlay probability or a causal effect.
  - NIST bootstrap guidance: https://www.itl.nist.gov/div898/handbook/eda/section3/bootplot.htm — uncertainty estimation via resampling, subject to assumptions.
  - scikit-learn chronological split: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html — chronological evaluation prevents training on future observations and testing on past observations.
  - scikit-learn Brier score: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html — proper scoring loss reference; it is not a return or profitability proof.
- Sources are method/discovery references only. No new odds, injuries, depth tiers, results, rankings, forecasts, correlation estimates, legal conclusions, or reward values were inferred or added.
- 2026-11-16 — Session `arena/f54713e3-fl4` completed a line-by-line repo review (read `data/`, `pages/`, `tools/`, `COORDINATION.md`, `README.md`, `REQUIREMENTS.md`) and closed out T13. Verified: `tools/build_site.py` → 10 pages / 423 sourced rows PASS; `tools/validate.py` → PASS (local links/fragments, HTTPS, source IDs); `tools/build_signals.py --fail-on-warn` → 14 pages / 10 checks PASS; `tools/check_signals.py` → PASS (14 pages, 0 broken links). GitHub Pages: status `built` for commit 62afd1b (== origin/main == this branch), HTTPS enforced, live at https://sassnarep3-star.github.io/FL4/ and https://sassnarep3-star.github.io/FL4/signals/; homepage fetched over HTTPS and renders (dashboard, nav, 39 flags, Signals tile). All requirements are delivered as design/framework with honest named blockers (F-01 no price feed, F-02 no official depth source, etc.); nothing was inferred, filled, or fabricated. The Flagged-for-Review page lists 39 items with source links for manual review; none block publication.
- 2026-11-16 — PR #9 (arena/f54713e3-fl4 → main) merged via merge commit e88008d at 2026-11-16T01:36:12Z; PR closed as MERGED. PR link: https://github.com/sassnarep3-star/FL4/pull/9. GitHub Pages build for e88008d status built; live site https://sassnarep3-star.github.io/FL4/ and /signals/ confirmed rendering. T13 integration complete and recorded.

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
