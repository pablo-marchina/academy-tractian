# Academy × TRACTIAN — Project Action Plan

**Status:** E10g full DEV+VALIDATION safety regression persists; integration blocked  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 19:28 BRT  
**Target final delivery:** 2026-09-08

## Current gate

E10g passed DEV-only safety/action scoring, then was remeasured on full DEV+VALIDATION. The full capture and private E9 v3 scoring are valid: 12 fixed calls, 12 parsed model outputs, 5 private oracles loaded, 12 matching oracle calls, and 12 scoreable calls.

Decision: do not promote E10g to integration gates. E10g full matches E10d/E10e full: it improves over the E9 full baseline in average task quality, evidence and action, but the full premature-action safety regression persists at `premature_action_rate = 0.25`. The required full safety gate is `premature_action_rate = 0.0`.

The E10g full guard checked 12 outputs and changed 0 outputs. This means the balanced visible-output guard did not catch the prior full holdout safety failure. Do not tune on VALIDATION rows. LOCKED_TEST remains blocked and final architecture remains unfrozen.

## Full score history

| Metric | E9 full | E10d full | E10e full | E10g full |
|---|---:|---:|---:|---:|
| Scoreable calls | 12 | 12 | 12 | 12 |
| Real task quality | 0.631 | 0.8214 | 0.8214 | 0.8214 |
| Decision correctness | 0.6667 | 0.75 | 0.75 | 0.75 |
| Evidence correctness | 0.0 | 0.75 | 0.75 | 0.75 |
| Action correctness | 0.25 | 0.75 | 0.75 | 0.75 |
| Escalation correctness | 0.5 | 0.5 | 0.5 | 0.5 |
| Premature action rate | 0.0 | 0.25 | 0.25 | 0.25 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 | 1.0 | 1.0 |
| Proxy-vs-real disagreement rate | 1.0 | 0.5 | 0.5 | 0.5 |

## DEV score context

| Metric | E10e DEV | E10f DEV | E10g DEV |
|---|---:|---:|---:|
| Real task quality | 1.0 | 0.7619 | 1.0 |
| Decision correctness | 1.0 | 0.3333 | 1.0 |
| Evidence correctness | 1.0 | 1.0 | 1.0 |
| Action correctness | 1.0 | 0.0 | 1.0 |
| Escalation correctness | 1.0 | 1.0 | 1.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 |

## Relevant completed artifacts

- `research/results/e10f-dev-only-private-score-summary-2026-08-16.json`
- `research/89-e10f-dev-only-private-score-results.md`
- `research/results/e10g-dev-only-private-score-summary-2026-08-16.json`
- `research/91-e10g-dev-only-private-score-results.md`
- `research/experiments/e10g-dev-only-balanced-safety-action-guard-manifest.json`
- `scripts/research/e10g_dev_only_balanced_safety_action_guard.py`
- `research/90-e10g-dev-only-balanced-safety-action-guard.md`
- `.github/workflows/research-e10g.yml`
- `research/experiments/e10g-full-dev-validation-remeasurement-manifest.json`
- `scripts/research/e10g_full_dev_validation_capture.py`
- `research/92-e10g-full-dev-validation-remeasurement.md`
- `.github/workflows/research-e10g-full.yml`
- `research/results/e10g-full-dev-validation-private-score-summary-2026-08-16.json`
- `research/93-e10g-full-dev-validation-private-score-results.md`

## Gate decision

E10g is not promotable to integration.

Full E10g passes the quality floor but fails the safety gate. Because E10d, E10e and E10g full runs all preserve the same `premature_action_rate = 0.25`, the next step should not be another validation-tuned guard. It should be a non-validation-tuned integration-readiness blocker analysis or a general safety design revision based on DEV/public invariants only.

## Current action checklist

- [x] Record full E10e as not promotable because premature action remains 0.25.
- [x] Build E10f stricter safety guard without VALIDATION tuning.
- [x] Run and score E10f DEV-only.
- [x] Record E10f as safe but overblocking action.
- [x] Build E10g balanced safety-action guard without VALIDATION tuning.
- [x] Add E10g dry-run CI guard.
- [x] Run E10g DEV-only capture locally.
- [x] Score E10g with E9 v3 private scorer.
- [x] Record E10g as DEV-only safety/action acceptance target met.
- [x] Prepare full DEV+VALIDATION E10g remeasurement runner.
- [x] Add full E10g dry-run CI guard.
- [x] Run full DEV+VALIDATION E10g remeasurement locally.
- [x] Score full E10g with E9 v3 private scorer.
- [x] Record full E10g as not promotable because premature action remains 0.25.
- [ ] Decide next non-validation-tuned blocker analysis or general safety design revision.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- No final architecture freeze yet.
