# E14v-B public synthetic qualification — FAIL (2026-08-20)

E14v-B consumed its single authorized public synthetic provider attempt after manual remediation of Groq model permissions.

## Sanitized aggregate result

```text
status                         E14V_PUBLIC_SYNTHETIC_ROUTE_PLANNER_QUALIFICATION_FAIL
synthetic_cases                14
valid_output_rate              0.0
route_recall                   0.0
action_dependency_recall       0.0
exact_set_match_rate           0.0
mean_extra_reads               0.0
unknown_route_count            0
duplicate_route_count          0
read_cap_violations            0
```

The E14v-B wrapper reports that the scientific candidate remained unchanged from E14v-A: same model, prompt, fixture, thresholds, provider, response contract, temperature, and reasoning effort. Real DEV was not authorized by this run.

## Interpretation boundary

This aggregate result is insufficient to classify the planner itself as a route-selection failure because `valid_output_rate=0.0` and all downstream route-contract counters remain zero. A sanitized transport diagnostic is required before any further amendment or scientific interpretation.

No case IDs, selected reads, expected reads, private scorer rows, VALIDATION feedback, or LOCKED_TEST data may be inspected for this classification.

## Gate state

- E14v-B attempt lock: consumed; preserve it.
- Real DEV: blocked.
- VALIDATION: blocked.
- LOCKED_TEST: untouched/final-only.
- Next authorized action: aggregate-only local transport diagnostic over the already-fixed E14v-B artifact. No provider call.
