# E14e Real DEV Measurement Result

**Date:** 2026-08-17  
**Scope:** DEV only  
**Status:** valid complete measurement; unchanged E14 quality gate failed

## Capture validity

E14e completed all six DEV calls with six parsed/scoreable outputs, completeness pass, zero retries, zero repairs, VALIDATION false, and LOCKED_TEST untouched.

## Unchanged gate

| Metric | E14e real DEV | Required | Gate |
|---|---:|---:|---|
| Parsed outputs | 6 | 6 | PASS |
| Scoreable calls | 6 | 6 | PASS |
| Real task quality | 0.7619 | >= 0.8571 | **FAIL** |
| Decision correctness | 0.6667 | >= 0.7500 | **FAIL** |
| Evidence correctness | 0.5000 | 1.0000 | **FAIL** |
| Action correctness | 0.3333 | >= 0.7500 | **FAIL** |
| Escalation correctness | 0.8333 | 1.0000 | **FAIL** |
| Premature action rate | 0.0000 | 0.0000 | PASS |
| Unsupported final-claim rate | 0.0000 | 0.0000 | PASS |
| LOCKED_TEST accessed | false | false | PASS |

VALIDATION therefore remains blocked.

## E14e intervention behavior

E10d changed two outputs under the refined semantics:

```text
explicit_current_handoff_phrase:                         1
state_changing_action_requires_visible_human_loop_guard: 1
none:                                                    4
```

This is consistent with the preregistered intervention. The former historical bare/generic-marker fallback did not appear as an E14e reason. E10g remained at zero changes under the E14d public evidence-family canonicalization.

Other boundary counts:

```text
E10e premature action guard:       2 outputs changed
E10g balanced action guard:        0 outputs changed
E11 independent authorization:     0 outputs changed
E14 selective reprocess targets:   0
```

## Public evidence canonicalization

Historical versus normalized public evidence-family histograms were:

```text
historical template-only count:
  0 -> 1 call
  1 -> 2 calls
  2 -> 1 call
  6 -> 1 call
  9 -> 1 call

canonical public-family count:
  2 -> 1 call
  6 -> 2 calls
  7 -> 1 call
  9 -> 2 calls
```

Four of six calls contained at least one concrete public GET equivalent not fully represented by the historical literal-template counter.

## Interpretation boundary

E14d and E14e are separate model generations. Therefore aggregate score differences between them are not treated as paired causal effects of the E10d fallback refinement. The supported structural claim is narrower: E14e replaced the broad fallback with explicit-current-handoff semantics and the real run exercised only the intended strong E10d reasons.

The remaining two E10e changes must now be diagnosed from the already-fixed E14e capture before any further candidate is defined. If those reasons are explicit visible safety contradictions or otherwise structurally justified, further boundary relaxation is not supported and the remaining failure should be treated as upstream model semantic behavior rather than a policy-representation bug.

## Methodological boundary

- no VALIDATION tuning;
- no LOCKED_TEST access;
- no private oracle or expected path in model or policy;
- no raw fixed outputs, scorer rows, output hashes, private paths or evaluator labels committed;
- no threshold reduction;
- no prompt/model/reasoning/completion-budget change;
- no E14f candidate is preregistered;
- final architecture remains unfrozen.

Sanitized machine-readable record: `results/e14e-real-dev-sanitized-summary.json`.
