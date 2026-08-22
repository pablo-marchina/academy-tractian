# E14v-A structural CI checkpoint — 2026-08-19

## Operational diagnosis

The first real E14v public synthetic qualification is classified as operationally invalid for planner-quality qualification. Sanitized aggregate diagnostics showed 14/14 provider errors, all `HTTPError`, after 3 transport attempts each, with 0 valid route-contract rows. No case IDs, selected reads, expected reads, raw outputs, private scorer rows, VALIDATION feedback, or LOCKED_TEST content were inspected.

## Amendment

E14v-A is an explicit operational transport-contract amendment. The E14v planner hypothesis is unchanged: same public synthetic fixture, model, prompt, public route catalog, reasoning effort, temperature, completion budget, retry policy, pacing, route cap, and qualification thresholds.

The corrected provider envelope uses only GPT-OSS-compatible response controls documented by Groq:

- `include_reasoning=false`;
- strict `json_schema` Structured Output for the single `reads` array;
- no `reasoning_format` parameter.

The original E14v synthetic output and attempt lock remain historical and must not be deleted or overwritten.

## Structural CI

```text
workflow   research-e14v-a-synthetic-transport-amendment
run_id     32309058317
job_id     96248075512
conclusion success
```

All structural steps passed:

- compile E14v-A;
- amendment self-check;
- zero-provider amended synthetic dry-run;
- amendment-boundary verification;
- forbidden private-selector access scan.

## Authorization boundary

This checkpoint authorizes exactly one real-provider **corrected public synthetic qualification** attempt under E14v-A, using a distinct output path and a new attempt lock.

It does **not** authorize real DEV, VALIDATION, or LOCKED_TEST.

If the corrected synthetic attempt passes the unchanged gate, real DEV may be activated only through a subsequent explicit checkpoint. If it fails, the corrected attempt lock remains in place and real DEV stays blocked.
