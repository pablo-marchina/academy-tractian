# E14i real DEV operational failure

E14i did not produce a valid task-quality measurement.

## Frozen configuration

- provider: Groq
- model: `openai/gpt-oss-120b`
- reasoning effort: `high`
- recorded `E14_REASONING_FORMAT=hidden` environment value
- max completion tokens: `1600`
- temperature: `0`
- response format: JSON Object Mode
- DEV only; VALIDATION not run; LOCKED_TEST not accessed

No causal effect is attributed to `reasoning_format` for GPT-OSS. Current provider documentation states that GPT-OSS reasoning exposure is controlled separately, and the observed E14i preflight PASS does not establish a reasoning-format effect.

## Real capture result

```text
status:                   E14I_DEV_ONLY_GPT_OSS_120B_HIGH_REASONING_HIDDEN_FORMAT_CAPTURE_NEEDS_REVIEW
total_calls:              6
parsed_outputs:           0
scoreable_calls:          0
completeness_pass:        false
retry_count:              12
```

The E9 scorer was invoked after the failed capture but found `parsed_model_outputs_available=0` and `scoreable_calls=0`. Its null quality metrics are **not** task-quality results and must not be compared with valid E14/E14b–E14g measurements.

## Sanitized provider diagnosis

Across the six calls, there were 18 provider-failure attempts:

```text
json_generation_validation_failure: 16
unknown_provider_failure:             2
```

Call-level sequence analysis showed:

```text
calls_with_any_json_generation_validation_failure:   6
calls_without_json_generation_validation_failure:    0
calls_with_only_json_generation_validation_failures: 5
calls_with_mixed_json_and_unknown_failures:           1
unknown_failure_isolated_from_json_validation:       false
dominant_json_validation_failure_pattern:            true
```

The two unknown failures occurred only inside one call that also experienced JSON-generation validation failure. They do not form an independent call-level failure mechanism in this capture.

## Decision

- E14i is an **operational FAIL**, not a quality FAIL.
- Do not rerun E14i.
- Do not infer scores from the null E9 output.
- Do not increase the completion budget on this evidence.
- The next candidate may test provider-side strict structured output enforcement while holding model, reasoning effort, token budget, prompts, policies, scorer and DEV gate fixed.

No raw fixed outputs, prompts, hashes, private paths, oracle rows, evaluator labels, VALIDATION feedback or LOCKED_TEST material are recorded here.
