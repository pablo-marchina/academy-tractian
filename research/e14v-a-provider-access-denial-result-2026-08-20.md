# E14v-A provider-access denial result — 2026-08-20

## Status

E14v-A corrected public synthetic qualification did **not** reach planner-quality measurement because all provider calls were rejected with HTTP 403.

Sanitized aggregate diagnostic:

```text
synthetic_rows                        14
rows_with_provider_error              14
rows_with_no_provider_error            0
provider_error_category_counts        HTTPError: 14
http_status_counts                    403: 14
transport_attempt_count_distribution  3: 14
valid_route_contract_rows              0
```

No case IDs, selected reads, expected reads, raw outputs, prompts, private oracle rows, scorer rows, VALIDATION feedback, or LOCKED_TEST data were inspected.

## Interpretation

This is a provider-permission/access denial, not evidence that the route planner selected bad routes. Groq documents HTTP 403 as a permissions restriction, and model-level organization/project restrictions specifically return 403.

The `openai/gpt-oss-120b` model remains a supported production model, so this result does not indicate model removal.

## Experimental consequence

- The original E14v synthetic attempt lock remains consumed and intact.
- The E14v-A corrected synthetic attempt lock remains consumed and intact.
- Real E14v DEV remains blocked.
- VALIDATION remains blocked.
- LOCKED_TEST remains untouched.
- No prompt, schema, route-selection algorithm, model, temperature, reasoning effort, synthetic fixture, expected sets, or qualification thresholds are changed by this result.

The next admissible step is external provider-access remediation followed by a separately preregistered provider-permission-only reattempt. No silent rerun is allowed.
