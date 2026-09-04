# Hard-freeze readiness gate — 2026-09-04

## Decision

Add a fail-closed **readiness** gate for the hard feature/visual/architecture freeze scheduled for the end of 2026-09-05.

This gate does not activate the hard freeze and does not broaden product-readiness claims. Its only purpose is to prevent the repository from declaring the scheduled freeze ready while any known external or repository-side prerequisite is unproven.

## Post-merge candidate evidence

The final freeze bundle candidate was merged to `main` as:

`3c0eb98054d9d67c52ba821b0e7329b4544f30e7`

The always-on `final-ci-required` push run on that exact SHA was:

`33835290807`

It completed successfully with:

```text
clean-clone / reproduce-current-product      success
full-product-browser / chromium-full-product success
required-gate                                success
```

This supersedes the earlier integration-only baseline `b86b15ef32762e5bc3cd474421c177eaa3f56787` for post-merge freeze-candidate verification. It does **not** make the hard freeze effective before its scheduled time.

## Readiness requirements

The live readiness check may return `READY_FOR_ACTIVATION` only when all of the following are simultaneously true:

1. current UTC time is at or after `2026-09-06T03:00:00Z` (end of 2026-09-05 in America/Sao_Paulo);
2. the checked-out candidate SHA equals the GitHub-observed `main` SHA;
3. `main.protected=true`;
4. branch metadata exposes `required-gate` as a required status context;
5. the latest completed `final-ci-required` run for that exact SHA concluded `success`;
6. that run contains a successful `required-gate` job;
7. the current final freeze evidence bundle validates with zero failures.

Any missing observation blocks readiness. There is no fallback from missing protection metadata to an operator assertion.

## Evidence boundary

The emitted report is aggregate-only and hash-bound. It records:

- candidate/main SHA;
- observation time;
- branch-protection boolean;
- whether `required-gate` is observed as required;
- final-CI run id and success booleans;
- final bundle manifest SHA-256 and validation-failure count;
- blocker codes;
- report SHA-256.

It does not persist GitHub tokens, authorization headers, users, tenants, runtime identities, prompts, traces, action arguments or raw API response bodies.

Raw GitHub branch/run/job responses are used transiently by the CLI and are not uploaded as artifacts.

## State semantics

`READY_FOR_ACTIVATION` means only that the scheduled freeze prerequisites are evidenced at the observation point.

The report always carries:

```text
hard_freeze_effective = false
production_readiness_claim_ready = false
interpretation = freeze_readiness_only
```

A later explicit repository state transition is still required to call the product hard-frozen.

## Current expected live result

On 2026-09-04, a live dispatch is expected to be blocked because:

- the not-before window has not opened; and
- GitHub last reported `main.protected=false` with no rulesets.

That is the correct result. The workflow must not be weakened to obtain a green artifact before those facts change.

## Non-goals

This slice does not:

- change runtime/controller/tool behavior;
- change frontend behavior;
- select a provider;
- collect or synthesize human semantic/value data;
- promote adaptive stopping;
- introduce LangGraph or another orchestration framework;
- claim RTO/RPO/HA/capacity;
- apply GitHub branch protection itself.

The last item remains an external GitHub Settings action because the connected development integration exposes read but not branch-protection/ruleset write capabilities.
