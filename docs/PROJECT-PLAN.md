# Academy × TRACTIAN — Project Action Plan

**Status:** E11 DEV-only independent action authorization pass; full DEV+VALIDATION E11 remeasurement next  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 19:51 BRT  
**Target final delivery:** 2026-09-08

## Current gate

E10g passed DEV-only safety/action scoring, then was remeasured on full DEV+VALIDATION. The full capture and private E9 v3 scoring were valid: 12 fixed calls, 12 parsed model outputs, 5 private oracles loaded, 12 matching oracle calls, and 12 scoreable calls.

Decision: do not promote E10g to integration gates. E10g full matches E10d/E10e full: it improves over the E9 full baseline in average task quality, evidence and action, but the full premature-action safety regression persists at `premature_action_rate = 0.25`. The required full safety gate is `premature_action_rate = 0.0`.

E10h recorded a non-validation-tuned blocker analysis. The analysis concludes that the failed assumption is reliance on post-hoc visible-output self-consistency: when the model produces an internally coherent but overconfident action recommendation, the visible guard may trust the model's own action-safety assertions.

E11 is the next DEV-only candidate: an independent action-authorization policy. It does not use VALIDATION for tuning, does not use private oracle values in the model/policy, keeps LOCKED_TEST blocked, and does not treat model `safe_to_act` as sufficient authorization.

E11 has now passed DEV-only private scoring: `real_task_quality = 1.0`, `decision_correctness = 1.0`, `evidence_correctness = 1.0`, `action_correctness = 1.0`, `escalation_correctness = 1.0`, `premature_action_rate = 0.0`, and `unsupported_final_claim_rate = 0.0`.

Decision: E11 passes the DEV-only safety/action acceptance gate. The next gate should be a full DEV+VALIDATION E11 remeasurement, with VALIDATION used only for measurement, not tuning. LOCKED_TEST remains blocked and final architecture remains unfrozen.

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

| Metric | E10e DEV | E10f DEV | E10g DEV | E11 DEV |
|---|---:|---:|---:|---:|
| Real task quality | 1.0 | 0.7619 | 1.0 | 1.0 |
| Decision correctness | 1.0 | 0.3333 | 1.0 | 1.0 |
| Evidence correctness | 1.0 | 1.0 | 1.0 | 1.0 |
| Action correctness | 1.0 | 0.0 | 1.0 | 1.0 |
| Escalation correctness | 1.0 | 1.0 | 1.0 | 1.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy-vs-real disagreement rate | 0.0 | 1.0 | 0.0 | 0.0 |

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

## E11 design

E11 adds an independent authorization layer after E10g DEV-only capture. It uses visible parsed output plus public/project tool invariants, but does not use private expected paths, VALIDATION feedback, evaluator labels, reference trajectories or LOCKED_TEST.

The policy authorizes action only after independently checking:

- exact supported endpoint classification;
- human handoff/review path vs autonomous state-changing maintenance;
- required endpoint identifiers;
- endpoint-specific evidence-family sufficiency;
- human review/escalation support for autonomous state-changing actions;
- a policy-level explanation for why immediate action is allowed.

Model `safe_to_act=true` is not sufficient authorization.

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
- [ ] Prepare full DEV+VALIDATION E11 remeasurement runner.
- [ ] Run full DEV+VALIDATION E11 remeasurement locally.
- [ ] Score full E11 with E9 v3 private scorer.
- [ ] Keep final architecture unfrozen.

## E11 acceptance target before any new full remeasurement

- `premature_action_rate = 0.0` on DEV.
- `unsupported_final_claim_rate = 0.0` on DEV.
- `evidence_correctness = 1.0` on DEV.
- `action_correctness >= 0.75` on DEV.
- `decision_correctness >= 0.75` on DEV.
- `escalation_correctness = 1.0` on DEV.
- `real_task_quality >= 0.8571` on DEV.
- LOCKED_TEST remains blocked.
- No raw private or fixed-output material is committed.

E11 met this DEV-only acceptance target.

## Next gate — full DEV+VALIDATION E11 remeasurement

The next full run must be measurement-only on VALIDATION. It must compare against the E9 full baseline and E10d/E10e/E10g full runs, and it must require `premature_action_rate = 0.0` before any integration promotion.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- No final architecture freeze yet.
