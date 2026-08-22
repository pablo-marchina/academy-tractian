# E14h Real DEV Operational Result

**Status:** OPERATIONAL FAIL — no valid task-quality measurement  
**Scope:** DEV only  
**VALIDATION:** not run  
**LOCKED_TEST:** not accessed

## Capture outcome

E14h used `openai/gpt-oss-120b`, `reasoning_effort=high`, temperature `0`, JSON Object Mode, and the unchanged 1600 completion-token cap.

The capture did not satisfy the mandatory completeness precondition:

- total calls: 6
- parsed outputs: 0
- schema-valid calls: 0
- each call exhausted the configured 3 harness attempts
- 18/18 provider attempts failed before a usable response was returned
- sanitized provider failure category: `json_generation_validation_failure` on all 18 attempts
- no provider token-usage counters were returned

The unchanged E9 scorer subsequently consumed six fixed calls but found zero parsed model outputs, so `scoreable_calls=0` and all task-quality metrics were null. That scorer result is not a quality measurement.

## Budget diagnostic

The fixed-capture diagnostic reported:

- `completion_budget_exhaustion_supported=false`
- zero calls with observed completion-token usage
- provider failures present on every call
- interpretation: `provider_failure_present_budget_exhaustion_not_isolated`

Therefore the evidence does **not** support increasing the token budget as the next intervention.

## Provider-configuration finding

Current Groq reasoning documentation states that when JSON mode is used with reasoning models, `reasoning_format` must be set to `parsed` or `hidden`. The current E14 transport sends `reasoning_effort` and `response_format={"type":"json_object"}` but does not set `reasoning_format`.

This creates a provider-configuration hypothesis that is more specific than token exhaustion and matches the observed `json_generation_validation_failure` pattern. The next candidate must correct only this configuration incompatibility before any further quality interpretation.

## Methodological consequence

E14h is not rerun and is not scored again. No VALIDATION is authorized. E10d/E10e/E10g/E11/E14 policies and thresholds remain frozen.
