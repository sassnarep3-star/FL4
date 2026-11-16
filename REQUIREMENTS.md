# REQUIREMENTS REGISTER — FL4 NFL signal-origination system

Source of truth: the project brief. Every requirement is traced to where it is satisfied, and any requirement that cannot be satisfied in this environment is marked **blocked** with the specific blocker named — not quietly dropped.

- **met** — done in this build, verifiable on the live site
- **partial** — the mechanism exists; a named input or decision is missing
- **blocked** — cannot be truthfully completed until a specific question is answered; the site publishes the block
- Verification protocol for every row: see `site/methodology.html` and `data/sources.json`

| ID | Requirement (as stated or implied by the brief) | Status | Where satisfied | Acceptance criteria | Blocker / note |
|----|---|---|---|---|---|
| R-01 | Collect, organize, analyse, using a full list of requirements | met | this file; `data/` (11 datasets); whole site | Every requirement has an ID, status and location | — |
| R-02 | Suggestions to improve the site for better decision-making | met | `data/suggestions.json` → Suggestions page | Each suggestion states problem, proposal, impact, effort, risk, dependencies | — |
| R-03 | Dedicated section to review suggestions and choose a path before implementing | met | Suggestions page: status control, `review_workflow`, `recommended_path_sequence` | Reviewer can approve/reject by editing one field; silence never auto-approves | Reviewer must name the approver — Q-GOV-02 |
| R-04 | Clear list of questions/information/answers needed before any decision | met | `data/questions.json` → Questions page (24 questions, 6 groups) | Each question: known, unknown, resolution path, options, default-if-unanswered, blocking flag | — |
| R-05 | Suggestions must be made to discover missing information | met | `data/inventory.json` → Information Inventory page | Every strategy lists `blocked_on`; every missing input has a next action | — |
| R-06 | Originate our own NFL lines | blocked | `S-13`; Line Origination page | An originated price published with its inputs, sigma and a comparison to market | No price feed: F-01 / Q-MKT-01. Origination is also a venue/counterparty problem, documented as such |
| R-07 | Research and develop strategies for useful signals | met (design) / blocked (validation) | `data/strategies.json` → Strategies page (16 candidates) | Each strategy: hypothesis, signal, inputs, entry, no-bet rules, stake, falsification, how it loses | Every `edge_claim` is null by policy until gates run |
| R-08 | Leaderboard competition with rewards for top strategies | met (design), empty (data) | `data/leaderboard.json` → Leaderboard page | Scoring formula, tiers, promotion, anti-gaming, rewards all defined; board renders zero rows | Zero real entries is correct: no bet ledger exists (IN-16) |
| R-09 | Single-bet strategies | met | S-01…S-07, S-11…S-14, bet_type `single` | Same as R-07 | — |
| R-10 | Parlay strategies | met (design) | S-09, S-10 | Parlay pricing refuses any pair with unmeasured correlation | Correlation register empty: F-11 |
| R-11 | Player-prop bet combos | partial | S-08, S-10; SG-17 descope decision | Prop strategies exist with explicit input requirements | No snap/usage data and no prop line history: F-07, IN-08, IN-10 |
| R-12 | Each strategy must pass validation gates | met (definition) | `data/gates.json` → Validation page (15 gates) | Gates state what failure mode they remove; pass rules are mechanical; blanks fail closed | 5 thresholds are reviewer-set: F-05 |
| R-13 | Determine correlation values | partial | `data/correlations.json` → Correlation page | Protocol defined (phi + excess joint prob + bootstrap CI, n ≥ 300); values published blank until measured | Needs a settlement ledger: F-11 |
| R-14 | Remove luck; selectively skill-based strategies | met | G-1 sample, G-2 walk-forward, G-3 CLV, G-11 multiple-testing, G-14 anti-gaming, leaderboard "no PnL on small samples" | A strategy cannot be promoted on outcome luck alone | — |
| R-15 | Track injuries | met | `data/signals/injuries_week10_2026.json` (81 Out/Doubtful rows, 14 games, all T1; corrected 2026-11-16) | Every row transcribed from the official report with the page link | Single-week snapshot; needs the weekly job (SG-02) |
| R-16 | Know defensive deficiencies when 2nd/3rd/4th-string backups replace starters | blocked | `site/depth.html`, S-16 | Names the unavailable defenders; states the replacement-quality gap where measured | The official report contains no depth/replacement field: F-02. No replacement is named anywhere on this site |
| R-17 | Same for offenses (starters vs backups) | blocked | `site/depth.html`, S-02, S-03, S-08 | Same | Same |
| R-18 | Executive summary of important details | met | `site/index.html` + `site/summary.html` | States findings, what is verified, what is blocked, next 6 decisions | — |
| R-19 | No manual input from the reviewer | met within scope | all capture, parsing, verification, build, publish steps automated in this session | Reviewer is asked to *decide*, never to *produce* | Decisions cannot be automated on the reviewer's behalf; they are published as questions instead of answered with guesses |
| R-20 | Work autonomously start to finish | met | this session: capture → data → site → CI → PR → merge → Pages | — | — |
| R-21 | Verify line by line against official trusted sources | met | every table row carries a source column; tiers in `data/sources.json` | 100% of published rows have a link; T1 only for asserted values | — |
| R-22 | Provide links for manual review | met | per-row links + Sources page register | — | — |
| R-23 | Flag irregularities | met | `data/flagged.json` (16 flags) + Flagged page | Each flag: type, detail, affected pages, action, links | — |
| R-24 | No hallucinations | met | no numeric value published without a source; all model/edge numbers null | Absence of any invented price, edge, win rate, depth chart or probability in the repo | — |
| R-25 | Review the repo line by line | met | `COORDINATION.md` irregularity I-1 | Repo inspected: 1 commit, 1 file (`README.md`, `# FL4`), no code, no data, no CI | Nothing existed to review; recorded honestly rather than pretending otherwise |
| R-26 | GitHub Pages site: clean landing + subpages by category | met | 15 pages built from data by `tools/build_site.py`; deployed by `.github/workflows/deploy-pages.yml` | Build succeeds; no broken internal links; Pages returns 200 | — |
| R-27 | UI clean, friendly, simple dashboard | met | `site/assets/app.css`, `app.js` | One nav, filterable/sortable tables, status badges, no external dependencies | — |
| R-28 | All entries and findings in readable tables with analysis | met | every page pairs tables with a findings/prose block | — | — |
| R-29 | Every table row has a source link to an official site | met | builder raises an error for a verified table row with no source | — | Rows about *decisions* link to the question record instead, labelled as such |
| R-30 | Values not confirmable from an official source left blank + flagged | met | render shows a blank marker; each gap has a flag entry | — | — |
| R-31 | Never infer or fill values | met | standings split columns omitted rather than guessed (F-04); edge claims null; replacements unnamed | — | — |
| R-32 | COORDINATION.md shared task board with claims/status | met | `COORDINATION.md` | Claim pushed before work; done rows record sources and verification | — |
| R-33 | Parallel-session coordination, non-overlapping scopes, rebase before push | met | branch `arena/94107c0d-fl4`; small frequent commits; `git pull --rebase` before each push | — | No other session existed at start (`git ls-remote` showed `main` only) |
| R-34 | Record sources, verification, irregularities when finishing a task | met | `COORDINATION.md` completion section | — | — |
| R-35 | Final integration session merges, re-verifies, checks links, publishes | met | re-verification + link check run before PR; see `COORDINATION.md` | — | — |
| R-36 | PR to main with summary, sources, flagged items; merge without waiting | met | PR body generated from the datasets; merged after a green build | — | — |
| R-37 | Confirm Pages deploys; fix until live; never merge a broken site | met | deploy verified after merge | — | — |
| R-38 | Flagged items published on a labelled "Flagged for Review" page with source links | met | `site/flagged.html`, linked from every page footer and the nav | — | — |

## What this register deliberately does not claim

1. It does not claim any strategy works. No edge number exists in this repo, because no price data exists in this environment. Any file that appears to assert one should be treated as a defect and flagged.
2. It does not claim historical depth. One week of availability data was captured because that is what the official page serves; the fix is an append-only snapshot job (SG-02), not a reconstruction.
3. It does not claim to know who replaces an injured starter. The source has no such field (F-02).
4. It does not give legal or financial advice; it records the compliance questions that must be answered first.
