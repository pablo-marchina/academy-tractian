# Main Branch Protection Contract

**Status:** repository CI ready; GitHub enforcement **not yet applied**  
**Last observed:** 2026-09-08 BRT  
**Observed state:** `main.protected = false`; required status-check enforcement = `off`.

This remains a P0 release-governance gap. A green CI workflow is not equivalent to GitHub technically preventing a direct/unchecked branch mutation.

## Current repository state

Latest branch metadata reports:

```text
main SHA                       4364364266c6a88d4affd85cb3a734c774cd42c8
main.protected                 false
protection.enabled             false
required-check enforcement     off
required contexts/checks       []
```

The functional-closure work is currently isolated on draft PR #222 and is intentionally not accepted/merged until hosted OpenRouter V14 functional acceptance is green.

## Why one stable required check

Most project workflows are path-filtered, research-specific, provider-specific or manually promoted. Requiring them individually can leave unrelated PRs waiting or couple branch governance to experiments.

Use the stable aggregate contract:

```text
final-ci-required
└── required-gate
    ├── clean-clone/current-product reproduction
    ├── full-product browser acceptance
    └── any reusable hard product gates wired by the current workflow revision
```

The workflow README is authoritative for the exact current dependency graph. `required-gate` is the stable branch-protection context; live provider experiments, exact-SHA production promotion and research workflows remain separate evidence.

## Required GitHub settings

Target: `main`.

Recommended enforcement:

1. restrict deletions;
2. block force pushes;
3. require pull request before merge;
4. required approvals `0` only while this remains a single-maintainer/student repository without an independent available reviewer; increase when real review capacity exists;
5. require conversation resolution;
6. require status checks;
7. require the stable `required-gate` context from `.github/workflows/final-ci-required.yml`;
8. require branch to be up to date before merge unless an intentional merge-queue policy supersedes it;
9. require linear history if squash-merge remains the project convention;
10. disable force pushes;
11. disable deletion.

Do **not** make provider-live workflows, rate-limit probes, research tournament jobs, one-shot hosted diagnostics or exact-SHA promotion workflows unconditional required contexts. They are evidence/operations surfaces, not always-triggered PR checks.

## Release branch

Production is sourced from `release/production-final`. The same principle applies: production source should not be mutable through unchecked force/direct push when the platform/account permits an enforceable rule. Do not state release-branch protection is currently verified unless GitHub metadata for that branch has been read after the rule is configured.

## Exact-SHA release relationship

Branch protection is only one gate. Final release evidence must also prove:

```text
candidate required CI        PASS
candidate functional gate    PASS
candidate security gates     PASS as applicable
production deployment SHA    exact candidate SHA
release identity endpoint    exact candidate SHA
```

PR/head success without exact production promotion is not a production acceptance claim.

Current production backend is `5611687556b3d50c31f20fa85ede794f2500f05c`, while the functional-closure PR is intentionally ahead. This divergence is acceptable during closure but must disappear for the final accepted candidate.

## Enforcement verification

After applying GitHub Settings, verify before declaring the gap closed:

```text
branch metadata → protected=true
protection/ruleset → required-gate present
new PR → merge blocked while required-gate pending/failing
required-gate success → merge eligible
force push → blocked
deletion → blocked
```

If the connected GitHub integration cannot mutate repository administration settings, apply them in GitHub Settings and use connector/REST metadata only to verify. Do not downgrade the requirement because the automation lacks admin permission.

## Evidence language

Allowed now:

> The repository exposes a stable required CI gate and is branch-protection-ready, but GitHub currently reports `main.protected=false`, so enforcement remains open.

Not allowed now:

> Direct/unchecked changes to main are technically blocked.

Update this file and `ACTIVE-PROJECT-STATUS.md` only after GitHub itself reports the protection active.