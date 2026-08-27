# E10d DEV-only Private Score Results

**Status:** E10D_DEV_ONLY_PRIVATE_SCORE_PASS_ACCEPTANCE_TARGET_MET  
**Date:** 2026-08-16  
**Scope:** DEV only  
**VALIDATION used for tuning:** false  
**VALIDATION ran:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Summary

E10d was run locally and then scored with the E9 v3 evaluator-side private scorer after outputs were fixed.

The committed record is sanitized. It does not include raw fixed parsed outputs, output hashes, score rows, private expected paths, oracle values, API keys, validation feedback, reference trajectories, evaluator-only labels or locked-test material.

## DEV-only score progression

| Metric | E9 DEV baseline | E10 DEV | E10b DEV | E10c DEV | E10d DEV |
|---|---:|---:|---:|---:|---:|
| Real task quality | 0.4762 | 0.619 | 0.8571 | 0.8571 | 1.0 |
| Decision correctness | 0.3333 | 0.3333 | 1.0 | 1.0 | 1.0 |
| Evidence correctness | 0.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Action correctness | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 |
| Escalation correctness | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Proxy-vs-real disagreement rate | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 |

## E10d aggregate private score

| Metric | Value |
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

## Interpretation

E10d meets the preregistered DEV-only acceptance target. It preserved the E10b/E10c decision, evidence and action gains while fixing the remaining escalation correctness gap on DEV-only private scoring.

This result allows full DEV+VALIDATION remeasurement of the E10d candidate. It does not freeze the final model, final provider, final architecture, MCP topology, RAG/vector DB, multi-agent decomposition, memory, observability or UI/demo flow.

## Boundary

The E10d consistency guard is allowed only because it uses visible model output and visible policy consistency. It does not use private expected paths, oracle labels, reference trajectories, validation feedback or locked-test data to modify outputs.

## Next gate

Run a full DEV+VALIDATION fixed capture using the E10d candidate, then score it with E9 v3 using private DEV+VALIDATION expected paths after outputs are fixed.

Acceptance for promotion remains stricter than DEV-only success:

- keep LOCKED_TEST blocked;
- do not tune on VALIDATION;
- do not commit raw private oracles or fixed parsed outputs;
- compare full DEV+VALIDATION E10d against the original E9 full baseline;
- only then decide whether the candidate is ready for later architecture integration work.
