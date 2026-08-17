# E14b real DEV measurement — valid capture, quality gate failed

**Date:** 2026-08-17  
**Scope:** DEV only  
**Gate:** E14 hard phase gate  
**Outcome:** **E14b candidate rejected**

## Measurement validity

The E14b real DEV capture completed with all six fixed calls parsed and scoreable. No VALIDATION data was used and LOCKED_TEST was not accessed.

| Capture metric | Result |
|---|---:|
| Fixed DEV calls | 6 |
| Parsed outputs | 6 |
| Scoreable calls | 6 |
| Completeness pass | true |
| Retry count | 2 |
| Syntax repair count | 0 |
| VALIDATION ran | false |
| LOCKED_TEST accessed | false |

The E14 selective-reprocess boundary was not exercised by these model outputs:

| Selective-reprocess metric | Result |
|---|---:|
| Target reprocess outputs checked | 0 |
| Authorized target reprocess outputs | 0 |
| Blocked target reprocess outputs | 0 |

## Private E9 v3 aggregate result

Only aggregate metrics are recorded here. Raw fixed outputs, score rows, output hashes, private paths, oracle values, and evaluator-only labels are intentionally not committed.

| Metric | E14b real DEV | Required | Gate |
|---|---:|---:|---|
| Real task quality | 0.6429 | >= 0.8571 | **FAIL** |
| Decision correctness | 0.5000 | >= 0.7500 | **FAIL** |
| Evidence correctness | 0.3333 | 1.0000 | **FAIL** |
| Action correctness | 0.0000 | >= 0.7500 | **FAIL** |
| Escalation correctness | 0.6667 | 1.0000 | **FAIL** |
| Premature action rate | 0.0000 | 0.0000 | PASS |
| Unsupported final-claim rate | 0.0000 | 0.0000 | PASS |

## Comparison with the valid E14 real DEV measurement

E14 and E14b used the same recovered provider/model/settings and the same DEV gate, so this within-recovery comparison is meaningful for rejecting the E14b prompt-policy candidate.

| Metric | E14 | E14b | Delta |
|---|---:|---:|---:|
| Real task quality | 0.7381 | 0.6429 | -0.0952 |
| Decision correctness | 0.5000 | 0.5000 | 0.0000 |
| Evidence correctness | 0.5000 | 0.3333 | -0.1667 |
| Action correctness | 0.1667 | 0.0000 | -0.1667 |
| Escalation correctness | 1.0000 | 0.6667 | -0.3333 |
| Premature action rate | 0.0000 | 0.0000 | 0.0000 |
| Unsupported final-claim rate | 0.0000 | 0.0000 | 0.0000 |

E14b therefore degraded every positive-quality metric except decision correctness, which remained unchanged. The two explicit safety rates remained at zero.

## Interpretation

The broad E14b evidence/endpoint/reconciliation prompt is rejected. Another prompt expansion is not justified yet.

Before preregistering E14c, the existing E14b capture must be inspected using only sanitized aggregate instrumentation to distinguish two materially different failure modes:

1. the GPT-OSS model itself selected weak/no actions or insufficient evidence; or
2. deterministic post-model guards/authorization boundaries downgraded otherwise actionable model outputs.

This distinction can be measured without another provider call and without consulting the private oracle.

Diagnostic:

```text
scripts/research/e14_semantic_boundary_diagnostic.py
```

The diagnostic reports only aggregate distributions, public endpoint/resource coverage, and boundary-change counts. It does not print private outputs, group rows, hashes, prompts, private paths, oracle data, or evaluator labels.

## Gate decision

```text
E14b: REJECT
E14 hard gate: FAIL
VALIDATION: BLOCKED
LOCKED_TEST: NOT ACCESSED
E14c: NOT YET PREREGISTERED
final architecture freeze: false
```

The next candidate may be designed only after the semantic/boundary diagnostic identifies whether the remaining failure is model-side or post-model-policy-side.
