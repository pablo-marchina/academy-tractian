# Academy × TRACTIAN — Project Action Plan

**Status:** E10g DEV-only balanced safety-action guard ready  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 18:59 BRT  
**Target final delivery:** 2026-09-08

## Current gate

E10f was run on DEV only after E10e failed to fix the full DEV+VALIDATION premature-action regression. E10f kept safety clean on DEV, but overblocked action: `action_correctness = 0.0`, `decision_correctness = 0.3333`, and `real_task_quality = 0.7619`.

Decision: do not promote E10f to a new full DEV+VALIDATION remeasurement.

E10g is now ready as a DEV-only balanced safety-action guard. It avoids inheriting E10f's overblocking thresholds, preserves action when the visible endpoint/evidence/rubric supports action, still blocks unsafe state-changing action, does not use VALIDATION for tuning, does not use private oracle values in the model or guard, and keeps LOCKED_TEST blocked.

## Score history

| Metric | E9 full | E10d full | E10e full | E10e DEV | E10f DEV |
|---|---:|---:|---:|---:|---:|
| Real task quality | 0.631 | 0.8214 | 0.8214 | 1.0 | 0.7619 |
| Decision correctness | 0.6667 | 0.75 | 0.75 | 1.0 | 0.3333 |
| Evidence correctness | 0.0 | 0.75 | 0.75 | 1.0 | 1.0 |
| Action correctness | 0.25 | 0.75 | 0.75 | 1.0 | 0.0 |
| Escalation correctness | 0.5 | 0.5 | 0.5 | 1.0 | 1.0 |
| Premature action rate | 0.0 | 0.25 | 0.25 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 | 0.5 | 0.5 | 0.0 | 1.0 |

## Relevant completed artifacts

- `research/results/e10f-dev-only-private-score-summary-2026-08-16.json`
- `research/89-e10f-dev-only-private-score-results.md`
- `research/experiments/e10f-dev-only-stricter-visible-safety-guard-manifest.json`
- `scripts/research/e10f_dev_only_stricter_visible_safety_guard.py`
- `research/88-e10f-dev-only-stricter-visible-safety-guard.md`
- `.github/workflows/research-e10f.yml`

## E10g artifacts ready

- `research/experiments/e10g-dev-only-balanced-safety-action-guard-manifest.json`
- `scripts/research/e10g_dev_only_balanced_safety_action_guard.py`
- `research/90-e10g-dev-only-balanced-safety-action-guard.md`
- `.github/workflows/research-e10g.yml`

## E10g design

E10g reuses the E10e safety guard and adds a balanced deterministic visible-output safety-action guard.

The guard blocks immediate action only when the model's visible output shows general safety failures such as `needs_more_evidence=true`, `safe_to_act=false`, missing/unsupported action endpoint, too few concrete evidence resources for autonomous state-changing action, uncertainty without strong visible safety support, or autonomous state-changing action without human escalation.

Unlike E10f, E10g accepts a visible `action_endpoint` in the rubric as endpoint support and does not require the endpoint to be repeated in the free-text proposed step. Human handoff endpoints remain treated as review paths rather than autonomous maintenance changes.

## E10g acceptance target before another full remeasurement

- Premature action rate remains 0.0 on DEV.
- Unsupported final-claim rate remains 0.0.
- Evidence correctness remains 1.0 on DEV.
- Action correctness improves above 0.0 and ideally returns to 1.0 on DEV.
- Escalation correctness remains 1.0 on DEV.
- Decision correctness recovers above 0.3333 and ideally returns to 1.0 on DEV.
- Real task quality returns to at least 0.8571 on DEV.
- LOCKED_TEST remains blocked.
- No raw private or fixed-output material is committed.

## Current action checklist

- [x] Record full E10e as not promotable because premature action remains 0.25.
- [x] Build E10f stricter safety guard without VALIDATION tuning.
- [x] Run and score E10f DEV-only.
- [x] Record E10f as safe but overblocking action.
- [x] Build E10g balanced safety-action guard without VALIDATION tuning.
- [x] Add E10g dry-run CI guard.
- [ ] Run E10g DEV-only capture locally.
- [ ] Score E10g with E9 v3 private scorer.
- [ ] Only after DEV-only safety/action acceptance, consider another full DEV+VALIDATION remeasurement.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- No final architecture freeze yet.
