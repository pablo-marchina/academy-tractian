# Main Branch Protection Contract

**Status:** repository CI ready; GitHub enforcement **not yet applied**  
**Observed on 2026-09-04:** `main.protected = false`; repository rulesets = `[]`.

## Why one required check

Most project workflows are intentionally path-filtered. Requiring a path-filtered check directly can leave an unrelated PR permanently waiting because GitHub never creates that check.

The repository therefore exposes one always-triggered final check:

```text
final-ci-required
└── required-gate
    ├── clean-clone current-product reproduction
    └── full-product Chromium acceptance
```

`required-gate` uses `if: always()` and fails unless both reusable workflows return `success`. It runs on every pull request, every push to `main`, and manual dispatch.

The specialized workflows remain independently runnable and continue to provide detailed evidence; branch protection needs only the stable aggregate check.

## Required GitHub ruleset / branch-protection settings

Target: repository default branch `main`.

Recommended enforcement:

1. **Restrict deletions:** enabled.
2. **Block force pushes:** enabled.
3. **Require a pull request before merging:** enabled.
4. **Required approvals:** `0` while this is a single-maintainer/student repository; requiring self-approval would make legitimate work impossible. Increase this only when an independent reviewer is actually available.
5. **Require conversation resolution before merging:** enabled.
6. **Require status checks to pass:** enabled.
7. **Required status check:** the stable `required-gate` check produced by `.github/workflows/final-ci-required.yml` (confirm the exact GitHub UI context after its first successful run before saving the ruleset).
8. **Require branch to be up to date before merging / strict status checks:** enabled unless merge-queue behavior is intentionally configured instead.
9. **Require linear history:** enabled; project PRs are squash-merged.
10. **Allow force pushes:** disabled.
11. **Allow branch deletion:** disabled.

Do not require provider-live workflows, research diagnostics, or other path-filtered checks individually. They may not run for every PR and are not suitable as unconditional required contexts.

## Final CI semantics

The clean-clone reusable workflow proves from a clean checkout:

- PostgreSQL-backed full Python suite;
- identity/RLS, load and restart P0 campaigns;
- frozen EV and delivery-evidence reproduction;
- final handoff audit;
- locked frontend install/typecheck/tests/build;
- zero tracked repository mutation.

The browser reusable workflow proves:

- real provider-free backend/frontend startup;
- PostgreSQL-backed product acceptance;
- Chromium full-product E2E;
- browser-safe semantic-review and operational-value participant flows;
- responsive frontend behavior and safe observability surfaces.

The aggregate required job does not reinterpret results or select thresholds; it only requires both contracts to be green.

## Enforcement verification

After GitHub Settings are changed, verify all of the following before claiming this P0 fully closed:

```text
GET branch metadata → protected=true
repository ruleset/protection read → required status check present
open test PR → direct merge blocked while required-gate is pending/failing
required-gate success → merge becomes eligible
force push/deletion remain blocked
```

The connected GitHub integration used during this development session exposes ruleset/branch-protection reads but no ruleset/protection write action. Therefore repository code can make protection ready and auditable, but **must not claim enforcement until GitHub Settings actually reports it**.
