# Academy × TRACTIAN — Project Action Plan

**Status:** E11 full DEV+VALIDATION safety regression persists; integration blocked  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 21:49 BRT  
**Target final delivery:** 2026-09-08

## Current gate

E11 passed DEV-only private scoring after the E10h blocker analysis introduced independent action authorization. The full DEV+VALIDATION E11 remeasurement was then run and scored with E9 v3 after outputs were fixed.

Decision: do not promote E11 to integration gates. E11 full matches E10d/E10e/E10g full: it improves over the E9 full baseline in average task quality, evidence and action, but the full premature-action safety regression persists at `premature_action_rate = 0.25`. The required full safety gate is `premature_action_rate = 0.0`.

The full scorer run is valid: 12 fixed calls, 12 parsed model outputs, 5 private oracles loaded, 12 matching oracle calls and 12 scoreable calls. VALIDATION was measurement-only, not tuning. LOCKED_TEST remains blocked and final architecture remains unfrozen.

## Full score history

| Metric | E9 full | E10d full | E10e full | E10g full | E11 full |
|---|---:|---:|---:|---:|---:|
| Scoreable calls | 12 | 12 | 12 | 12 | 12 |
| Real task quality | 0.631 | 0.8214 | 0.8214 | 0.8214 | 0.8214 |
| Decision correctness | 0.6667 | 0.75 | 0.75 | 0.75 | 0.75 |
| Evidence correctness | 0.0 | 0.75 | 0.75 | 0.75 | 0.75 |
| Action correctness | 0.25 | 0.75 | 0.75 | 0.75 | 0.75 |
| Escalation correctness | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| Premature action rate | 0.0 | 0.25 | 0.25 | 0.25 | 0.25 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Proxy-vs-real disagreement rate | 1.0 | 0.5 | 0.5 | 0.5 | 0.5 |

## Split summary

| Split | Calls | Real quality | Decision | Evidence | Action | Escalation | Premature action | Unsupported claim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DEV | 6 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| VALIDATION | 6 | 0.6429 | 0.5 | 0.5 | 0.5 | 0.0 | 0.5 | 0.0 |

## Relevant completed artifacts

- `research/results/e10g-full-dev-validation-private-score-summary-2026-08-16.json`
- `research/93-e10g-full-dev-validation-private-score-results.md`
- `research/experiments/e10h-non-validation-tuned-safety-blocker-analysis-manifest.json`
- `research/results/e10h-non-validation-tuned-safety-blocker-analysis-summary-2026-08-16.json`
- `research/94-e10h-non-validation-tuned-safety-blocker-analysis.md`
- `research/experiments/e11-dev-only-independent-action-authorization-manifest.json`
- `scripts/research/e11_dev_only_independent_action_authorization.py`
- `research/95-e11-dev-only-independent-action-authorization.md`
- `.github/workflows/research-e11.yml`
- `research/results/e11-dev-only-private-score-summary-2026-08-16.json`
- `research/96-e11-dev-only-private-score-results.md`
- `research/experiments/e11-full-dev-validation-remeasurement-manifest.json`
- `scripts/research/e11_full_dev_validation_capture.py`
- `research/97-e11-full-dev-validation-remeasurement.md`
- `.github/workflows/research-e11-full.yml`
- `research/results/e11-full-dev-validation-private-score-summary-2026-08-16.json`
- `research/98-e11-full-dev-validation-private-score-results.md`

## Gate decision

E11 is not promotable to integration.

Full E11 passes the average-quality floor but fails the safety gate. Because E10d, E10e, E10g and E11 full runs all preserve the same `premature_action_rate = 0.25`, the next step should not be a VALIDATION-tuned patch. It should be a non-validation-tuned authorization instrumentation audit or design diagnosis using only DEV/public invariants and sanitized aggregate evidence.

## Current action checklist

- [x] Record full E10g as not promotable because premature action remains 0.25.
- [x] Keep VALIDATION protected from tuning.
- [x] Keep LOCKED_TEST blocked.
- [x] Record E10h non-validation-tuned blocker analysis.
- [x] Identify the general safety-design failure mode without tuning on VALIDATION.
- [x] Record that the next candidate should be independent action authorization.
- [x] Prepare E11 independent action-authorization policy from DEV/public invariants only.
- [x] Add E11 dry-run CI guard.
- [x] Run E11 DEV-only capture locally.
- [x] Score E11 DEV-only with E9 v3 private scorer.
- [x] Record E11 as DEV-only safety/action acceptance target met.
- [x] Prepare full DEV+VALIDATION E11 remeasurement runner.
- [x] Add full E11 dry-run CI guard.
- [x] Run full DEV+VALIDATION E11 remeasurement locally.
- [x] Score full E11 with E9 v3 private scorer.
- [x] Record full E11 as not promotable because premature action remains 0.25.
- [ ] Decide next non-validation-tuned authorization instrumentation audit or design diagnosis.
- [ ] Keep final architecture unfrozen.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- No final architecture freeze yet.
