# E13 DEV-only Private Score Results

**Status:** E13_DEV_ONLY_PRIVATE_SCORE_ACTION_COLLAPSE_AND_PARSE_MISSING  
**Date:** 2026-08-16  
**Scope:** DEV only  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Summary

E13 implemented only the preregistered reprocess-specific authorization boundary after E12 identified the root-cause class `policy_executed_but_over_permissive_or_wrong_authorization_class`.

The E9 v3 private scorer passed, but E13 failed DEV-only acceptance. The scorer consumed 6 fixed calls, found 5 parsed model outputs, loaded 3 private oracles, matched all 6 calls to a private oracle, and had 5 scoreable calls.

E13 preserved the safety floor on scoreable DEV calls: `premature_action_rate = 0.0` and `unsupported_final_claim_rate = 0.0`. However, it caused action collapse and quality regression: `action_correctness = 0.0`, `decision_correctness = 0.4`, and `real_task_quality = 0.7714`. One DEV call was not scoreable because a parsed model output was missing.

E13 is not promotable to a full DEV+VALIDATION remeasurement.

The committed record is sanitized. It does not include raw fixed parsed outputs, score rows, output hashes, private expected paths, oracle values, local private paths, API keys, validation feedback, reference trajectories, evaluator-only labels or LOCKED_TEST material.

## DEV score comparison

| Metric | E11 DEV-only | E13 DEV-only |
|---|---:|---:|
| Scoreable calls | 6 | 5 |
| Parsed outputs | 6 | 5 |
| Real task quality | 1.0 | 0.7714 |
| Decision correctness | 1.0 | 0.4 |
| Evidence correctness | 1.0 | 1.0 |
| Action correctness | 1.0 | 0.0 |
| Escalation correctness | 1.0 | 1.0 |
| Premature action rate | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 |
| Proxy-vs-real disagreement rate | 0.0 | 1.0 |

## Acceptance target check

| Target | Required | E13 DEV-only | Result |
|---|---:|---:|---|
| Parsed outputs | 6 | 5 | fail |
| Scoreable calls | 6 | 5 | fail |
| Premature action rate | 0.0 | 0.0 | pass |
| Unsupported final-claim rate | 0.0 | 0.0 | pass |
| Real task quality | >= 0.8571 | 0.7714 | fail |
| Decision correctness | >= 0.75 | 0.4 | fail |
| Action correctness | >= 0.75 | 0.0 | fail |
| Evidence correctness | 1.0 | 1.0 | pass |
| Escalation correctness | 1.0 | 1.0 | pass |
| LOCKED_TEST blocked | true | true | pass |

## Gate decision

Do not prepare full DEV+VALIDATION E13.

Do not integrate.  
Do not demo.  
Do not freeze final architecture.

E13 achieved the intended safety direction on scoreable DEV calls, but it overcorrected: the reprocess-specific boundary removed correct action behavior on DEV and reduced average task quality below the preregistered threshold.

## Boundary

- VALIDATION was not used for tuning.
- Private expected paths were read only by the local scorer after outputs were fixed.
- The model did not receive private oracle values.
- The policy did not receive private oracle values.
- LOCKED_TEST remained blocked.
- Raw expected values were not printed or committed.
- Raw fixed outputs, score rows and output hashes were not committed.
- Final architecture remains unfrozen.

## Next gate

Do not design another candidate blindly.

The next step should be a non-validation-tuned E13 blocker audit focused only on why DEV action collapsed and why one parsed output was missing. That audit may use sanitized E13 aggregate evidence plus non-private capture instrumentation, but must not use private expected paths, raw scorer rows, output hashes, validation feedback or LOCKED_TEST.
