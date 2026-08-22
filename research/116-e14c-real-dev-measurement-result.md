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

The subsequent fixed-capture semantic diagnostic isolated the reason codes:

```text
E10e:
  no_supported_action_endpoint_visible   1
  visible_rubric_needs_more_evidence     1
  none                                    4

E10g:
  balanced_guard_handoff_without_minimum_visible_evidence   3
  none                                                     3
```

E10g therefore did not block these three outputs because of an unsupported endpoint, `safe_to_act=false`, a state-change decision conflict, or an autonomous-maintenance rule. All three were blocked by the handoff-specific minimum-public-evidence-marker heuristic.

A narrower sanitized fixed-capture diagnostic then measured the E10g-blocked handoffs only:

```text
blocked handoffs:                  3
recognized public markers = 0:    2
recognized public markers = 1:    1
plan length min / max / avg:       2 / 7 / 4.667
```

This result does **not** justify lowering the E10g handoff threshold from 2 to 1: two blocked handoffs have zero markers under the historical counter. However, the historical counter itself performs literal substring matching against public template forms such as `GET /assets/{asset_id}`. It does not canonicalize concrete public read paths such as `GET /assets/<concrete-id>` to the same public resource family. That is the same representation class already proven to affect action endpoints in E14c.

Therefore E14d is still not preregistered. A final zero-provider-call shape diagnostic now distinguishes, within those three blocked handoffs, between:

- already-recognized template-form evidence families;
- concrete public GET paths equivalent to one of the **same ten existing E10e evidence families** but historically not counted;
- genuinely unrecognized/generic evidence with no equivalent accepted public family.

The diagnostic keeps the existing threshold at 2 and adds no new evidence families. It is diagnostic-only and does not use private evaluator information.

Sanitized helpers:

- `../scripts/research/e14c_e10g_handoff_evidence_diagnostic.py`
- `../scripts/research/e14c_e10g_handoff_evidence_shape_diagnostic.py`

## Interpretation

E14c is a meaningful improvement relative to the recovered E14 baseline on the same GPT-OSS settings: it restores evaluator evidence correctness to 1.0 and keeps escalation correctness, premature-action safety and unsupported-claim safety at their required values while real task quality rises close to the gate. This does **not** authorize VALIDATION because decision and action correctness remain below threshold.

No E14d candidate is preregistered from aggregate score deltas or private-evaluator implications alone. The next step remains local public-contract analysis of the already-fixed E14c capture.

## Methodological boundary

- no VALIDATION tuning;
- no LOCKED_TEST access;
- no private oracle or expected path in model or policy;
- no raw fixed outputs, scorer rows, output hashes, private paths or evaluator labels committed;
- no prompt/model/reasoning/completion-budget change is authorized yet;
- final architecture remains unfrozen.

Sanitized machine-readable record: `results/e14c-real-dev-sanitized-summary.json`.
