# Academy × TRACTIAN — Project Action Plan

**Status:** E10h non-validation-tuned safety blocker analysis recorded; E11 independent action authorization next  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 19:31 BRT  
**Target final delivery:** 2026-09-08

## Current gate

E10g passed DEV-only safety/action scoring, then was remeasured on full DEV+VALIDATION. The full capture and private E9 v3 scoring are valid: 12 fixed calls, 12 parsed model outputs, 5 private oracles loaded, 12 matching oracle calls, and 12 scoreable calls.

Decision: do not promote E10g to integration gates. E10g full matches E10d/E10e full: it improves over the E9 full baseline in average task quality, evidence and action, but the full premature-action safety regression persists at `premature_action_rate = 0.25`. The required full safety gate is `premature_action_rate = 0.0`.

E10h records a non-validation-tuned blocker analysis. The analysis concludes that the failed assumption is reliance on post-hoc visible-output self-consistency: when the model produces an internally coherent but overconfident action recommendation, the visible guard may trust the model's own action-safety assertions.

The next design step should not be another VALIDATION-tuned guard. It should be E11: an independent action-authorization policy derived from DEV/public invariants only.

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

- `research/results/e10g-full-dev-validation-private-score-summary-2026-08-16.json`
- `research/93-e10g-full-dev-validation-private-score-results.md`
- `research/experiments/e10h-non-validation-tuned-safety-blocker-analysis-manifest.json`
- `research/results/e10h-non-validation-tuned-safety-blocker-analysis-summary-2026-08-16.json`
- `research/94-e10h-non-validation-tuned-safety-blocker-analysis.md`

## E10h blocker analysis conclusion

E10h is not a new guard and not a tuning step. It uses only sanitized aggregate results and general public/project safety invariants.

The observed failure is class-level: visible-output guards are checking the model's own stated action safety, endpoint, evidence and escalation fields. If those fields are internally coherent but overconfident, the guard has no independent authorization layer strong enough to reject the action.

Next design direction: independent action authorization. A future candidate should decide whether action is allowed before trusting `safe_to_act` or other model self-attestation.

## Current action checklist

- [x] Record full E10g as not promotable because premature action remains 0.25.
- [x] Keep VALIDATION protected from tuning.
- [x] Keep LOCKED_TEST blocked.
- [x] Record E10h non-validation-tuned blocker analysis.
- [x] Identify the general safety-design failure mode without tuning on VALIDATION.
- [x] Record that the next candidate should be independent action authorization.
- [ ] Prepare E11 independent action-authorization policy from DEV/public invariants only.
- [ ] Run E11 DEV-only before any new full DEV+VALIDATION measurement.
- [ ] Keep final architecture unfrozen.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- No final architecture freeze yet.
