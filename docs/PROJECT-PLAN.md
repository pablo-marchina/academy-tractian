# Academy × TRACTIAN — Project Action Plan

**Status:** E10g DEV-only safety-action pass; full DEV+VALIDATION E10g remeasurement next  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 19:10 BRT  
**Target final delivery:** 2026-09-08

## Current gate

E10g was run on DEV only after E10f kept safety clean but overblocked action. The E10g scorer run is valid and restores the DEV safety/action balance: `real_task_quality = 1.0`, `decision_correctness = 1.0`, `evidence_correctness = 1.0`, `action_correctness = 1.0`, `escalation_correctness = 1.0`, `premature_action_rate = 0.0`, and `unsupported_final_claim_rate = 0.0`.

Decision: E10g passes the DEV-only acceptance target. The next gate should be a full DEV+VALIDATION E10g remeasurement, with VALIDATION used only for measurement, not tuning. LOCKED_TEST remains blocked and final architecture remains unfrozen.

Important caveat: E10g changed 0 DEV outputs, which is acceptable because DEV already scored perfectly. It does not prove the prior full DEV+VALIDATION premature-action issue is solved. The next full run must explicitly test that.

## Score history

| Metric | E9 full | E10d full | E10e full | E10e DEV | E10f DEV | E10g DEV |
|---|---:|---:|---:|---:|---:|---:|
| Real task quality | 0.631 | 0.8214 | 0.8214 | 1.0 | 0.7619 | 1.0 |
| Decision correctness | 0.6667 | 0.75 | 0.75 | 1.0 | 0.3333 | 1.0 |
| Evidence correctness | 0.0 | 0.75 | 0.75 | 1.0 | 1.0 | 1.0 |
| Action correctness | 0.25 | 0.75 | 0.75 | 1.0 | 0.0 | 1.0 |
| Escalation correctness | 0.5 | 0.5 | 0.5 | 1.0 | 1.0 | 1.0 |
| Premature action rate | 0.0 | 0.25 | 0.25 | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 | 0.5 | 0.5 | 0.0 | 1.0 | 0.0 |

## Relevant completed artifacts

- `research/results/e10f-dev-only-private-score-summary-2026-08-16.json`
- `research/89-e10f-dev-only-private-score-results.md`
- `research/results/e10g-dev-only-private-score-summary-2026-08-16.json`
- `research/91-e10g-dev-only-private-score-results.md`
- `research/experiments/e10g-dev-only-balanced-safety-action-guard-manifest.json`
- `scripts/research/e10g_dev_only_balanced_safety_action_guard.py`
- `research/90-e10g-dev-only-balanced-safety-action-guard.md`
- `.github/workflows/research-e10g.yml`

## Next gate — full DEV+VALIDATION E10g remeasurement

The next run should measure E10g on DEV + VALIDATION only after outputs are fixed and before any integration promotion.

Rules:

- Do not tune on VALIDATION.
- Do not use private expected paths in the model or guard.
- Keep LOCKED_TEST blocked.
- Score with E9 v3 only after fixed outputs exist.
- Do not commit raw fixed outputs, score rows, output hashes or private oracle material.
- Compare against E9 full baseline, E10d full and E10e full.

Full acceptance target:

- Real task quality above 0.631.
- Premature action rate restored to 0.0.
- Unsupported final-claim rate remains 0.0.
- Evidence correctness remains above 0.0.
- Action correctness remains at least 0.25 and should not collapse.
- Escalation correctness remains at least 0.5.
- LOCKED_TEST remains inaccessible.

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
- [ ] Prepare full DEV+VALIDATION E10g remeasurement runner.
- [ ] Run full DEV+VALIDATION E10g remeasurement locally.
- [ ] Score full E10g with E9 v3 private scorer.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- No final architecture freeze yet.
