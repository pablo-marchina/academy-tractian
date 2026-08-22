# E14c structural dry-run result

**Date:** 2026-08-17  
**Scope:** DEV-only structural/instrumentation validation  
**Quality evidence:** none; no real provider call

## Result

GitHub Actions run `32033397539` passed on commit `8f1705eaf332eb3f1eedcb51e15b0f5794c6f97f`.

```text
status:                              E14C_DEV_ONLY_PUBLIC_ENDPOINT_CANONICALIZATION_CAPTURE_PASS
total_calls:                         6
parsed_model_outputs_available:      6
scoreable_calls:                     6
validation_ran:                      false
dry_run:                             true
completeness_pass:                   true
retry_count:                         0
repair_count:                        0
concrete_public_action_endpoints:    0  (dry fixture uses canonical templates)
target_reprocess_outputs_checked:    6
authorized_target_reprocess_outputs: 3
blocked_target_reprocess_outputs:    3
```

The E14c self-check additionally validates concrete public action paths directly rather than relying on the canonical-template dry fixture. It verifies all five frozen public action endpoint shapes, rejects wrong methods/extra text, and proves the specific safety invariant that motivated E14c:

- concrete `POST /cases/<id>/escalate` + `safe_to_act=true` is not rejected merely as an unsupported endpoint;
- the same concrete public endpoint + `safe_to_act=false` remains blocked as `visible_rubric_not_safe_to_act`.

## CI implementation notes

Two earlier E14c CI attempts failed before candidate logic executed:

1. importing the E2 ToolSpec runtime pulled an unavailable `pydantic` dependency into minimal CI;
2. a `dataclass` loaded through the existing lightweight `importlib` helper hit a Python 3.13 module-registration edge case.

Both were harness-only issues. The final canonicalizer is stdlib-only and parses the literal five `action(...)` declarations from the frozen `research/e2/tool_registry.py` source without importing the E2 runtime.

## Interpretation

This run proves only structural behavior and policy-shape invariants. It does not establish model quality. A real six-call DEV-only E14c capture and private E9 v3 scoring are still required before any VALIDATION measurement is allowed.
