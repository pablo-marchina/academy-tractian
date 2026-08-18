# E14j real DEV operational failure

Date: 2026-08-18

## Result

E14j did not produce a valid DEV quality measurement.

Sanitized operational result:

```text
status:                         E14J_DEV_ONLY_STRICT_JSON_SCHEMA_OUTPUT_CAPTURE_NEEDS_REVIEW
model:                          openai/gpt-oss-120b
reasoning_effort:               high
response_format:                json_schema
strict:                         true
max_completion_tokens:          1600
total_calls:                    6
parsed_model_outputs_available: 0
scoreable_calls:                0
validation_ran:                 false
completeness_pass:              false
retry_count:                    12
repair_count:                   0
```

The evaluator-side scorer was invoked after the incomplete capture, but it found `parsed_model_outputs_available=0` and `scoreable_calls=0`. Its null quality fields are not benchmark measurements and must not be compared with valid E14–E14g quality results.

Downstream semantic-repair, guard, evidence and selective-reprocess counters are not interpretable as semantic evidence when no parsed model output exists.

## Important telemetry correction

The current transport's historical failure classifier treats any HTTP 400/422 response containing a provider `failed_generation` field as `json_generation_validation_failure`. This classification is broader than a proof of JSON-schema non-adherence. Therefore earlier sanitized failure-category counts from E14h–E14j must not be used to infer a unique provider failure mechanism.

This does not change any already-fixed model output or score. It only corrects the interpretation of sanitized operational telemetry.

## Public-safe operational inference

The strongest public-safe pattern is now:

- E14g: GPT-OSS 120B, `reasoning_effort=medium`, completion budget 1600 -> 6/6 complete.
- E14h/E14i/E14j: GPT-OSS 120B, `reasoning_effort=high`, completion budget 1600 -> 0/6 complete in each real DEV capture.
- E14i and E14j synthetic compatibility preflights succeeded at `reasoning_effort=high` and budget 1600, while the materially larger real DEV task did not complete.
- E14j strict Structured Outputs passed its exact-schema synthetic preflight, so another response-format intervention is not the next justified experiment.

This pattern supports testing completion budget as the next single intervention. It does not establish a causal effect from a single generated comparison and uses no private scorer rows or oracle labels.

## Scope

- DEV only.
- VALIDATION not run.
- LOCKED_TEST not accessed.
- No raw outputs, private scorer rows, output hashes, private paths, expected paths, evaluator labels or reference trajectories are recorded here.
- PR remains draft and final architecture remains unfrozen.
