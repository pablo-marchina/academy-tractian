# Main Branch Protection Contract

**Status:** repository CI ready; GitHub enforcement **not yet applied**  
**Observed on 2026-09-05:** `main.protected = false`; repository rulesets = `[]`.

## Why one required check

Most project workflows are intentionally path-filtered. Requiring a path-filtered check directly can leave an unrelated PR waiting because GitHub never creates that check.

The repository therefore exposes one always-triggered final check:

```text
final-ci-required
└── required-gate
    ├── clean-clone current-product reproduction
    ├── full-product Chromium acceptance
    ├── horizontal read-only runtime handoff
    └── non-transferable action execution lease
```

`required-gate` uses `if: always()` and fails unless all four reusable workflows return `success`. It runs on every pull request, every push to `main`, and manual dispatch.

Specialized workflows remain independently runnable and provide detailed evidence; branch protection needs only the stable aggregate check.

Latest accepted functional P0 evidence at this checkpoint:

```text
main functional baseline  d3bed06b132212c85b126f56708863d45f64e03e
final-ci-required         run #386 / 33971230788
required-gate             success
```

Documentation-only rehearsal commits may produce a later `main` SHA without changing the functional topology; they must still pass the same aggregate gate before merge.

## Required GitHub ruleset / branch-protection settings

Target: default branch `main`.

Recommended enforcement:

1. restrict deletions — enabled;
2. block force pushes — enabled;
3. require pull request before merging — enabled;
4. required approvals — `0` while this remains a single-maintainer/student repository; increase only when an independent reviewer actually exists;
5. require conversation resolution — enabled;
6. require status checks to pass — enabled;
7. required status check — stable `required-gate` from `.github/workflows/final-ci-required.yml`;
8. require branch up to date / strict status checks — enabled unless merge queue is intentionally configured;
9. require linear history — enabled; project PRs use squash merge;
10. allow force pushes — disabled;
11. allow branch deletion — disabled.

Do not require provider-live workflows, research diagnostics or other path-filtered checks individually. They are not unconditional contexts.

## Final CI semantics

### Clean clone

Proves from a clean checkout:

- PostgreSQL-backed full Python suite;
- identity/RLS, load and restart P0 campaigns;
- current distributed runtime/action regressions;
- frozen EV and historical delivery-evidence reproduction;
- final handoff audit;
- final freeze bundle validation;
- locked frontend install/typecheck/tests/build;
- zero tracked repository mutation.

### Chromium full product

Proves:

- real provider-free backend/frontend startup;
- PostgreSQL-backed product path;
- REST/SSE/reconnect/catch-up behavior;
- safe trace/evidence/lineage/evaluation surfaces;
- controlled pending/confirmed action browser flow;
- tenant isolation and forbidden-field absence;
- responsive frontend behavior.

### Horizontal runtime handoff

Proves PostgreSQL-real read-only ownership semantics:

- healthy lease non-interference;
- expired takeover;
- generation fencing;
- recovered terminal/evaluation persistence;
- stale owner containment.

### Action execution lease

Proves PostgreSQL-real consequential-action ownership semantics:

- healthy remote action non-interference;
- non-transferable lease;
- lost ownership → `UNCERTAIN`;
- stale terminal result fencing;
- no replacement/automatic replay after lease loss.

The aggregate job does not reinterpret results or loosen thresholds; it only requires all four contracts to be green.

## Claim boundary

`required-gate` proves repository CI acceptance. It does not by itself prove:

- Cloud Run/Cloud SQL deployment HA;
- production RTO/RPO/uptime/autoscaling/multi-region behavior;
- external exactly-once side effects;
- enterprise identity infrastructure.

## Enforcement verification

After GitHub Settings are changed, verify all of the following before claiming branch protection closed:

```text
GET branch metadata → protected=true
repository ruleset/protection read → required-gate present
open test PR → direct merge blocked while required-gate pending/failing
required-gate success → merge becomes eligible
force push/deletion remain blocked
```

The connected GitHub integration used during this development work exposes branch/ruleset reads but no administration write action. Repository code can make protection ready/auditable, but **must not claim enforcement until GitHub reports it active**.