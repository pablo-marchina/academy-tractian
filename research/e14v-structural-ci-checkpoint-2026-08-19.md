# E14v structural CI checkpoint — 2026-08-19

E14v remains preregistered with real DEV blocked pending the public synthetic route-planner qualification.

## Structural CI

```text
workflow   research-e14v-isolated-public-evidence-route-planner
run_id     32307291772
conclusion success
```

All structural steps passed:

- compile E14v planner and self-check;
- offline self-check;
- zero-provider synthetic dry-run;
- preregistered-boundary verification;
- forbidden private-selector access scan.

The earlier failed workflow attempts were infrastructure/checker issues only: first repository import path, then missing `pydantic`, then an over-broad substring scan that mistook the audit field `split_coverage_tags_used=false` for selector access. None changed the preregistered planner, synthetic fixture, route catalog, thresholds, model, or experimental hypothesis, and no provider call was made by those failures.

## Authorization boundary

This checkpoint authorizes exactly one real-provider **public synthetic qualification** attempt under the frozen E14v preregistration. It does **not** authorize real DEV, VALIDATION, or LOCKED_TEST.

Real DEV may be activated only if the frozen synthetic qualification gate passes. If the synthetic attempt fails, its attempt lock must remain in place and real DEV stays blocked.
