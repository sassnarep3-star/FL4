# Pre-registration — NFL line-origination strategies (registration 2026-11-16)

**Registration = the git commit that adds this file.** Its hash is recorded in `COORDINATION.md` (task T14) and can be checked with `git log -- prereg/`. The file hashes in `prereg/registration.json` are checked on every build by `tools/build_signals.py` (check: *Pre-registration: frozen files match the registered hashes*). If any frozen file changes, the build fails until a new, dated registration is committed.

## What is frozen

| File | Content | SHA-256 |
|---|---|---|
| `data/signals/strategies.json` | 16 strategy definitions, each with hypothesis, signal, inputs, entry, no-bet rules, stake rule, falsification, how-it-loses, and a two-sided what-would-change-our-mind field | see `prereg/registration.json` |
| `data/signals/gates.json` | 15 validation gates, with thresholds. A null threshold is a deliberate blank that the reviewer must set and that makes the gate refuse to run | see `prereg/registration.json` |
| `data/signals/leaderboard.json` | Divisions (singles, game parlays, same-game parlays, prop combos), ranking metric, control baseline, demotion gate, removal-of-luck panel, backtest-exclusion rule | see `prereg/registration.json` |
| `data/signals/correlations.json` | Correlation protocol: 11 pairs, measurement method, n threshold. All measured values null | see `prereg/registration.json` |

## Rules fixed by this registration

1. **Sample window.** Prospective only. The window opens at the first NFL game kickoff after this registration commit and closes at the last regular-season kickoff published on nfl.com. Kickoff times come from the official game page. No game before the window is evaluated.
2. **Hypothesis before first bet.** A strategy's hypothesis must be timestamped before its first bet in that family (the rule is in `leaderboard.json`, `promotion_rules`).
3. **Frozen rule text.** Changing a strategy, gate, threshold, division rule or control after this commit requires a new dated registration. Editing a frozen file in place is a G-14 violation.
4. **Trials.** The multiplicity adjustment uses the number of registered hypotheses in the family. This registration contains 16 strategies.
5. **Ranking.** Stage 1 is benchmark-relative Brier skill against the control baseline, with a game-cluster lower bound above zero. Stage 2 is prospective CLV and ROI, held in escrow. Raw win rate, short-run ROI and season-long realised ROI are never ranking inputs.
6. **Signal versus staking.** Signal metrics are computed at flat stake. Staking results are reported separately and cannot qualify or rescue a strategy that fails stage 1.
7. **Controls.** Every run includes random picks, favourites-only and the line-shopping baseline (S-12). The number of random draws is reviewer-set.
8. **Joint probabilities.** Combos are rankable only with a directly validated joint probability and the operator's void and push rules. Marginal probabilities are never multiplied.
9. **Backtests.** Backtest numbers never appear on the leaderboard. A leaderboard entry without `basis = prospective` fails the build.
10. **Demotion.** A live strategy whose stage-1 lower bound falls to zero or below, or whose executed CLV is negative with a CI excluding zero, returns to paper. Null thresholds fail closed.
11. **Holdout split.** Train, validation and final-holdout seasons are not defined in this repository. No historical seasons are archived here, so the split is blocked (see the decision-readiness table).

## What this registration does not do

- It does not evaluate any strategy. No bet, price, CLV, ROI or correlation is computed or published here.
- It does not set the reviewer-owned thresholds (gates G-1 to G-15 where null, demotion D-1 and D-2, control draw count).
- It does not establish that any strategy has an edge. Its only claim is that the rules are written down before the window opens.
