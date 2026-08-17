# E14c Real DEV Measurement Result

**Date:** 2026-08-17  
**Scope:** DEV only  
**Status:** valid complete measurement; unchanged E14 quality gate failed

## Result

E14c completed all six fixed DEV calls with no retries and no repairs. The private E9 v3 scorer consumed all six fixed parsed outputs and produced six scoreable calls. VALIDATION did not run and LOCKED_TEST was not accessed.

| Metric | E14c real DEV | Required | Gate |
|---|---:|---:|---|
| Parsed outputs | 6 | 6 | PASS |
| Scoreable calls | 6 | 6 | PASS |
| Real task quality | 0.8333 | >= 0.8571 | **FAIL** |
| Decision correctness | 0.6667 | >= 0.7500 | **FAIL** |
| Evidence correctness | 1.0000 | 1.0000 | PASS |
| Action correctness | 0.1667 | >= 0.7500 | **FAIL** |
| Escalation correctness | 1.0000 | 1.0000 | PASS |
| Premature action rate | 0.0000 | 0.0000 | PASS |
| Unsupported final-claim rate | 0.0000 | 0.0000 | PASS |

## Public endpoint result

The deterministic E14c comparison canonicalizer observed four concrete public action endpoints, one already-canonical public action endpoint and one `none`/empty endpoint. Five outputs resolved to the same public comparison endpoint:

```text
POST /cases/{case_id}/escalate
```

This supports the E14c root-cause hypothesis that concrete public paths were previously being rejected by exact template equality. The stored model endpoint values remained unchanged; only the guard comparison view was canonicalized.

## Boundary effects

Sanitized aggregate boundary changes:

```text
E10d escalation consistency:       0 outputs changed
E10e premature action guard:       2 outputs changed
E10g balanced action guard:        3 outputs changed
E11 independent authorization:     0 outputs changed
E14 selective reprocess targets:   0
```

The action collapse therefore remains post-model but has moved downstream: E10g is now the dominant boundary changing outputs after E14c canonicalization.

For a canonical case-escalation endpoint, E10g treats the action as a human handoff rather than an autonomous maintenance mutation. After its general rubric checks, the handoff-specific condition requires at least two visible evidence markers. The exact aggregate reason codes for the three E10g changes must be read from the already-fixed E14c capture before any next candidate is preregistered.

## Interpretation

E14c is a meaningful improvement relative to the recovered E14 baseline on the same GPT-OSS settings: it restores evaluator evidence correctness to 1.0 and keeps escalation correctness, premature-action safety and unsupported-claim safety at their required values while real task quality rises close to the gate. This does **not** authorize VALIDATION because decision and action correctness remain below threshold.

No E14d candidate is preregistered from aggregate score deltas alone. The next step is a zero-provider-call sanitized boundary-reason diagnostic over the already-fixed E14c capture to determine whether E10g's three downgrades are legitimate visible-safety blocks or a mismatch between its public evidence-marker heuristic and the supported human-handoff semantics.

## Methodological boundary

- no VALIDATION tuning;
- no LOCKED_TEST access;
- no private oracle or expected path in model or policy;
- no raw fixed outputs, scorer rows, output hashes, private paths or evaluator labels committed;
- no prompt/model/reasoning/completion-budget change is authorized yet;
- final architecture remains unfrozen.

Sanitized machine-readable record: `results/e14c-real-dev-sanitized-summary.json`.
