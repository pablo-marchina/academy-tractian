# Academy × TRACTIAN — Project Action Plan

**Status:** E10f DEV-only safety pass with action collapse; E10g balanced safety-action guard next  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 18:42 BRT  
**Target final delivery:** 2026-09-08

## Current gate

E10f was run on DEV only after E10e failed to fix the full DEV+VALIDATION premature-action regression. The E10f scorer run is valid and keeps safety clean on DEV: `premature_action_rate = 0.0`, `unsupported_final_claim_rate = 0.0`, and `LOCKED_TEST accessed = false`.

Decision: do not promote E10f to a new full DEV+VALIDATION remeasurement. E10f is too conservative: it restores/keeps safety, but collapses `action_correctness` to 0.0, drops `decision_correctness` to 0.3333, and lowers DEV real task quality to 0.7619, below the preregistered DEV acceptance floor of 0.8571.

The next gate should be E10g, a balanced safety-action guard. E10g must not use VALIDATION for tuning, must not use private oracle values in the model or guard, and must keep LOCKED_TEST blocked.

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

## Relevant artifacts

- `research/results/e10f-dev-only-private-score-summary-2026-08-16.json`
- `research/89-e10f-dev-only-private-score-results.md`
- `research/experiments/e10f-dev-only-stricter-visible-safety-guard-manifest.json`
- `scripts/research/e10f_dev_only_stricter_visible_safety_guard.py`
- `research/88-e10f-dev-only-stricter-visible-safety-guard.md`
- `.github/workflows/research-e10f.yml`

## Immediate next gate — E10g balanced safety-action guard

E10g should target the failure mode exposed by E10f: broad safety blocking removes action correctness. It should be preregistered as a general policy-level visible-output guard and tested on DEV before any new full remeasurement.

### E10g acceptance target before another full remeasurement

- Premature action rate remains 0.0 on DEV.
- Unsupported final-claim rate remains 0.0.
- Evidence correctness remains 1.0 on DEV.
- Action correctness improves above 0.0 and ideally returns to 1.0 on DEV.
- Escalation correctness remains 1.0 on DEV.
- Real task quality returns to at least 0.8571 on DEV.
- LOCKED_TEST remains blocked.
- No raw private or fixed-output material is committed.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- No final architecture freeze yet.

## Current action checklist

- [x] Record full E10e as not promotable because premature action remains 0.25.
- [x] Build E10f stricter safety guard without VALIDATION tuning.
- [x] Add E10f dry-run CI guard.
- [x] Run E10f DEV-only capture locally.
- [x] Score E10f with E9 v3 private scorer.
- [x] Record E10f as safety-clean but not accepted because action collapses.
- [ ] Build E10g balanced safety-action guard without VALIDATION tuning.
- [ ] Run E10g DEV-only capture locally.
- [ ] Score E10g with E9 v3 private scorer.
- [ ] Only after DEV-only safety/action acceptance, consider another full DEV+VALIDATION remeasurement.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.
