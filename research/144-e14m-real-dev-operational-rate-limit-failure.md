# E14m — real DEV operational failure from Groq long-window rate limit

**Status:** incomplete / not scoreable  
**Date:** 2026-08-18  
**Scope:** DEV only

## Result

The first real E14m capture did not satisfy the required 6/6 completeness gate:

```text
status:                                   E14M_DEV_ONLY_PUBLIC_DECISION_ADJUDICATION_CAPTURE_NEEDS_REVIEW
parsed_model_outputs_available:           5
scoreable_calls:                          5
retry_count:                              2
adjudication_triggered_calls:             5
additional_adjudication_calls:            5
parseable_adjudication_responses:         5
preserved_initial_drafts:                 0
```

No E9 quality score is authorized for this incomplete capture.

## Sanitized operational diagnosis

A capture-only diagnostic found exactly one failed fixed call. That call failed before a usable initial draft existed and exhausted all three E14 attempts:

```text
missing_final_outputs:                    1
error:                                    E14_MODEL_CALL_FAILED
attempt_count:                            3
retry_count:                              2
sanitized_attempt_failures:               model_call_failed x3
sanitized_provider_failure_category:      rate_limit_long_window x3
initial_model_call_failed_calls:          1
initial_output_parse_failed_calls:        0
```

The E14m adjudication layer cannot explain the missing output. For each of the five calls that produced an initial draft, the adjudicator triggered and produced a parseable second response:

```text
initial_drafts_observed:                  5
adjudication_triggered_calls:             5
additional_adjudication_calls:            5
parseable_adjudication_responses:         5
adjudication_failure_can_explain_missing: false
```

## Interpretation

This is an **operational quota failure**, not a valid quality measurement and not evidence against the E14m semantic intervention.

The Groq transport emits `rate_limit_long_window` when a documented rate-limit wait exceeds the configured 180-second benchmark bound. The candidate's 25-second pacing remains frozen; changing pacing would be a different intervention and is not justified by a long-window exhaustion signal.

Official Groq documentation states that limits may apply across RPM/RPD/TPM/TPD and at project/organization level, and that the exact current limits for the account should be read from the Groq Console. The base Free Plan for `openai/gpt-oss-120b` currently lists 8K TPM and 200K TPD, but project or organization limits can be lower.

## Operational replacement protocol

`research/experiments/e14m-operational-replacement-r1-amendment.json` was preregistered after this non-scoreable failure and before any replacement call.

Exactly one replacement capture is allowed after the long-window quota is available again. The replacement must keep the E14m candidate unchanged. The incomplete 5/6 capture is discarded from quality selection and must never be scored.

If the replacement is 6/6, unchanged E9 v3 must run exactly once regardless of how favorable or unfavorable public diagnostics appear. If the replacement is incomplete, stop E14m with no third real capture.

VALIDATION and LOCKED_TEST remain blocked.
