# E14v public synthetic qualification — first real attempt result — 2026-08-19

## Scope

Public-synthetic-only checkpoint for the preregistered E14v isolated evidence-route planner. Real DEV remains blocked. VALIDATION was not run and LOCKED_TEST was not used.

## Observed aggregate

```text
status                         E14V_PUBLIC_SYNTHETIC_ROUTE_PLANNER_QUALIFICATION_FAIL
dry_run                        false
provider                       groq_zero_cost
model                          openai/gpt-oss-120b
reasoning_effort               medium
temperature                    0.0
synthetic_cases                14
valid_output_rate              0.0
route_recall                   0.0
action_dependency_recall       0.0
exact_set_match_rate           0.0
mean_extra_reads               0.0
unknown_route_count            0
duplicate_route_count          0
read_cap_violations            0
private_oracle_used            false
private_scorer_rows_used       false
validation_feedback_used       false
locked_test_used               false
```

The synthetic attempt lock is consumed and must not be deleted or bypassed. Real DEV is not authorized.

## Operational diagnosis pending

The all-zero validity/recall pattern with zero unknown/duplicate/cap violations is compatible with a transport/parse failure before route-set evaluation. Repository inspection found that the E14v Chat Completions payload sends `reasoning_effort=medium` with `response_format={"type":"json_object"}` but omits `reasoning_format`. Current Groq documentation for reasoning models states that JSON mode must use `reasoning_format=parsed` or `hidden`; GPT-OSS supports `reasoning_effort` low/medium/high.

This is a public transport-contract finding, not a private benchmark-row inference. Before any amendment or second public-synthetic attempt can be authorized, inspect only sanitized provider error-category counts from the already-consumed local synthetic artifact. Do not inspect or use DEV private rows.

If the sanitized diagnostic confirms transport/configuration failure (for example all provider rows ending in HTTPError), the first synthetic attempt should be classified as operationally invalid for model qualification and a narrowly scoped preregistered transport amendment may authorize one corrected synthetic qualification attempt. If it instead shows valid provider responses with route-contract failures, E14v should be rejected or scientifically amended rather than silently rerun.
