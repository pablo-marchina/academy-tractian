# E10e DEV-only Private Score Results

**Status:** E10E_DEV_ONLY_PRIVATE_SCORE_PASS_ACCEPTANCE_TARGET_MET  
**Date:** 2026-08-16  
**Scope:** DEV only  
**VALIDATION used for tuning:** false  
**VALIDATION ran:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Summary

E10e was run locally and then scored with the E9 v3 evaluator-side private scorer after outputs were fixed.

The committed record is sanitized. It does not include raw fixed parsed outputs, output hashes, score rows, private expected paths, oracle values, API keys, validation feedback, reference trajectories, evaluator-only labels or locked-test material.

## Why this gate was needed

E10d passed DEV-only and improved the full DEV+VALIDATION aggregate, but it failed the full promotion gate because premature action rate regressed from `0.0` to `0.25`.

E10e therefore added a visible-output premature-action safety guard and tested it on DEV only before any new full DEV+VALIDATION remeasurement.

## E10e DEV-only result

| Metric | E10e DEV-only |
|---|---:|
| Fixed calls consumed | 6 |
| Parsed model outputs available | 6 |
| Private oracles loaded | 3 |
| Calls with matching private oracle | 6 |
| Scoreable calls | 6 |
| Real task quality | 1.0 |
| Decision correctness | 1.0 |
| Evidence correctness | 1.0 |
| Action correctness | 1.0 |
| Escalation correctness | 1.0 |
| Premature action rate | 0.0 |
| Unsupported final-claim rate | 0.0 |
| Proxy success rate | 1.0 |
| Proxy-vs-real disagreement rate | 0.0 |

## Capture guard summary

| Metric | Value |
|---|---:|
| Guard outputs checked | 6 |
| Guard outputs changed | 0 |

The DEV-only outputs were already safety-consistent under the visible-output premature-action guard. This is a positive DEV-only result, but it does not prove that the full DEV+VALIDATION safety regression is fixed. A new full remeasurement is still required.

## Gate decision

E10e meets the DEV-only safety acceptance target:

- premature action rate remained `0.0`;
- unsupported final-claim rate remained `0.0`;
- real task quality remained `1.0`;
- decision, evidence, action and escalation correctness remained `1.0`;
- LOCKED_TEST remained blocked.

This allows a new full DEV+VALIDATION remeasurement of the E10e candidate. It does not freeze the final model, provider, architecture, MCP topology, RAG/vector DB, multi-agent decomposition, memory, observability or UI/demo flow.

## Boundary

- Private expected paths were read only by the local scorer after outputs were fixed.
- The model did not receive private oracle values.
- The guard did not use private oracle values.
- VALIDATION was not used for tuning.
- LOCKED_TEST remained blocked.
- Raw expected values were not printed or committed.
- Raw fixed outputs, score rows and output hashes were not committed.
- Final architecture remains unfrozen.

## Next gate

Run a full DEV+VALIDATION fixed capture using the E10e candidate, then score it with E9 v3 using private DEV+VALIDATION expected paths after outputs are fixed.

Acceptance for promotion remains strict:

- improve over the E9 full baseline;
- restore full premature action rate to `0.0`;
- keep unsupported final-claim rate at `0.0`;
- keep LOCKED_TEST blocked;
- do not tune on VALIDATION;
- do not commit private or fixed-output material.
