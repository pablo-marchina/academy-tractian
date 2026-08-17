# E14d Real DEV Measurement Result

**Date:** 2026-08-17  
**Scope:** DEV only  
**Status:** valid complete measurement; unchanged E14 quality gate failed

## Capture validity

E14d completed all six DEV calls with six parsed/scoreable outputs, completeness pass, zero repair operations, VALIDATION false, and LOCKED_TEST untouched. Two provider retries occurred; the capture nevertheless completed under the preregistered transport/retry policy.

## Unchanged gate

| Metric | E14d real DEV | Required | Gate |
|---|---:|---:|---|
| Parsed outputs | 6 | 6 | PASS |
| Scoreable calls | 6 | 6 | PASS |
| Real task quality | 0.8095 | >= 0.8571 | **FAIL** |
| Decision correctness | 0.8333 | >= 0.7500 | PASS |
| Evidence correctness | 0.6667 | 1.0000 | **FAIL** |
| Action correctness | 0.3333 | >= 0.7500 | **FAIL** |
| Escalation correctness | 0.8333 | 1.0000 | **FAIL** |
| Premature action rate | 0.0000 | 0.0000 | PASS |
| Unsupported final-claim rate | 0.0000 | 0.0000 | PASS |
| LOCKED_TEST accessed | false | false | PASS |

VALIDATION therefore remains blocked.

## Public evidence canonicalization result

All six calls contained at least one concrete public GET route equivalent that the historical literal-template counter would not fully recognize. Historical versus normalized distinct-family histograms were:

```text
historical template-only count:
  0 -> 3 calls
  1 -> 1 call
  2 -> 1 call
  7 -> 1 call

canonical public-family count:
  2 -> 2 calls
  5 -> 1 call
  8 -> 2 calls
  9 -> 1 call
```

The E14d intervention therefore exercised its intended representation-equivalence path on every real DEV call without changing the accepted family set or evidence thresholds.

## Boundary effects

```text
E10d escalation consistency:       2 outputs changed
E10e premature action guard:       2 outputs changed
E10g balanced action guard:        0 outputs changed
E11 independent authorization:     0 outputs changed
E14 selective reprocess targets:   0
```

The specific E14d root-cause hypothesis about E10g was supported: after equivalent concrete public GET routes were counted as their frozen public families, E10g no longer downgraded any output for insufficient handoff evidence.

However, E14d still fails the overall gate. The next blocker must not be inferred from score deltas alone. The already-fixed E14d capture must be inspected with the sanitized semantic-boundary diagnostic to identify the two E10d and two E10e reason classes before any E14e candidate is defined.

## Causal interpretation boundary

E14c and E14d were separate real model generations. E14d also experienced two provider retries. Therefore the aggregate score differences between E14c and E14d are not treated as pure causal effects of evidence-resource canonicalization. The causal claim supported by this run is narrower: the E14d comparison view recognized concrete public evidence families, and E10g made zero downstream changes under that corrected view.

## Methodological boundary

- no VALIDATION tuning;
- no LOCKED_TEST access;
- no private oracle or expected path in model or policy;
- no raw fixed outputs, scorer rows, output hashes, private paths or evaluator labels committed;
- no threshold reduction;
- no prompt/model/reasoning/completion-budget change;
- E14e is not preregistered;
- final architecture remains unfrozen.

Sanitized machine-readable record: `results/e14d-real-dev-sanitized-summary.json`.
