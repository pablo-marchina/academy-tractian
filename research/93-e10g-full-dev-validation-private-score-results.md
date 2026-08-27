# E10g Full DEV+VALIDATION Private Score Results

**Status:** E10G_FULL_DEV_VALIDATION_SAFETY_REGRESSION_PERSISTS  
**Date:** 2026-08-16  
**Scope:** DEV + VALIDATION  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Summary

E10g passed DEV-only safety/action scoring, then was remeasured on full DEV+VALIDATION as a measurement gate only.

The full capture passed with 12 calls, 12 parsed model outputs, `validation_ran=true`, `dry_run=false`, 12 guard outputs checked, and 0 guard outputs changed.

The E9 v3 private scorer passed after outputs were fixed: 12 fixed calls were consumed, 5 private oracles were loaded, all 12 calls had a matching private oracle, and all 12 were scoreable.

E10g full improves over the E9 full baseline on average task quality, evidence and action, but it is not promotable because `premature_action_rate = 0.25`. The full safety gate requires `premature_action_rate = 0.0`.

## Full score comparison

| Metric | E9 full baseline | E10d full | E10e full | E10g full |
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

## Gate decision

Do not promote E10g to integration gates.

E10g restores DEV-only performance but does not fix the full DEV+VALIDATION premature-action failure. The full result matches E10d and E10e full: stronger than E9 baseline in average task quality, but blocked by safety.

## Sanitization

This committed record is sanitized. It does not include:

- raw fixed parsed outputs;
- score rows;
- output hashes;
- private expected paths;
- private oracle values;
- API keys;
- validation feedback;
- reference trajectories;
- evaluator-only labels;
- locked-test material.

## Boundary

- Private expected paths were read only by the local scorer after outputs were fixed.
- The model did not receive private oracle values.
- The guard did not use private oracle values.
- VALIDATION was used only for measurement, not tuning.
- LOCKED_TEST remained blocked.
- Raw expected values were not printed or committed.
- Final architecture remains unfrozen.

## Next gate

Do not create another validation-tuned guard from these holdout rows.

The next step should be a non-validation-tuned integration-readiness blocker analysis or a general safety design revision based on DEV/public invariants only, because repeated full measurements have shown the same holdout premature-action issue in E10d, E10e and E10g.
