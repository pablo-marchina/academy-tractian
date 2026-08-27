# E10d Full DEV+VALIDATION Private Score Results

**Status:** E10D_FULL_DEV_VALIDATION_PRIVATE_SCORE_IMPROVED_WITH_SAFETY_REGRESSION  
**Date:** 2026-08-16  
**Scope:** DEV + VALIDATION measurement  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Summary

E10d passed the DEV-only acceptance target, so it was remeasured on DEV + VALIDATION. The full run consumed 12 fixed calls, loaded 5 private oracles, and had 12 scoreable calls.

The result improves over the original E9 full baseline on real task quality, decision correctness, evidence correctness and action correctness. However, it fails the full promotion gate because premature action rate regressed from 0.0 to 0.25.

The committed record is sanitized. It does not include raw fixed parsed outputs, score rows, output hashes, private expected paths, oracle values, API keys, validation feedback, reference trajectories, evaluator-only labels or locked-test material.

## Full score comparison

| Metric | E9 full baseline | E10d full DEV+VALIDATION | Delta |
|---|---:|---:|---:|
| Scoreable calls | 12 | 12 | 0 |
| Real task quality | 0.631 | 0.8214 | +0.1904 |
| Decision correctness | 0.6667 | 0.75 | +0.0833 |
| Evidence correctness | 0.0 | 0.75 | +0.75 |
| Action correctness | 0.25 | 0.75 | +0.5 |
| Escalation correctness | 0.5 | 0.5 | 0.0 |
| Premature action rate | 0.0 | 0.25 | +0.25 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 | 0.5 | -0.5 |

## Sanitized split summary

| Split | Calls | Real task quality | Decision | Evidence | Action | Escalation | Premature action | Unsupported claims |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DEV | 6 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| VALIDATION | 6 | 0.6429 | 0.5 | 0.5 | 0.5 | 0.0 | 0.5 | 0.0 |

## Gate decision

Do not promote E10d into integration gates yet.

E10d is better than the E9 full baseline on most quality dimensions, but the safety gate is stricter than average quality. A full candidate cannot be accepted while premature action rate rises above 0.0.

## Interpretation

E10d generalizes partially from DEV to VALIDATION: the full score improves substantially, but the holdout split reveals a safety regression. This means the visible-output escalation guard is useful, but the candidate needs an additional safety/premature-action guard before any new full remeasurement.

Because VALIDATION is measurement-only, the next design step must not tune on validation rows or use validation-specific expected paths. The next candidate should be a general DEV-only or policy-level guard based on visible output consistency and safety invariants, not on validation oracle content.

## Boundary

- Private expected paths were read only by the local scorer after outputs were fixed.
- The model did not receive private oracle values.
- LOCKED_TEST remained blocked.
- Raw expected values were not printed or committed.
- Raw fixed outputs, score rows and output hashes were not committed.
- Final architecture remains unfrozen.

## Next gate

E10e should target premature-action safety without using VALIDATION for tuning. The acceptance target before another full remeasurement should include:

- preserve evidence correctness above the E9 DEV baseline;
- preserve action correctness above the E9 DEV baseline;
- preserve escalation correctness at least at the E9 full baseline;
- restore premature action rate to 0.0;
- keep unsupported final-claim rate at 0.0;
- keep LOCKED_TEST blocked;
- do not commit private or fixed-output material.
