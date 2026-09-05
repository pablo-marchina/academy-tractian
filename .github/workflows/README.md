# GitHub Actions — Active CI and Historical Research Workflows

`.github/workflows/` contains both the **current product CI surface** and a large set of historical/experimental execution wrappers retained for provenance.

Workflow presence is not authorization. Current project state comes from [`docs/CURRENT-PROJECT-STATUS.md`](../../docs/CURRENT-PROJECT-STATUS.md), and active execution priorities come from [`docs/DELIVERY-PLAN.md`](../../docs/DELIVERY-PLAN.md).

## Current required product CI

The stable top-level gate is:

- `final-ci-required.yml`

It composes the current required contracts:

- `clean-clone-full-product-reproduction.yml`;
- `full-product-playwright.yml`;
- `horizontal-runtime-handoff.yml`;
- `action-execution-lease.yml`.

`required-gate` is the stable status context intended for branch protection.

These workflows represent the active product regression surface. Changes to their meaning are material and should be reviewed like production code.

## Specialized active validation

Additional workflows may remain useful for targeted validation, benchmarking or diagnosis, for example PostgreSQL operational/recovery, load/concurrency and hard-freeze checks. Their presence does not make their outputs stronger than the current canonical status/acceptance documents.

## Historical / experimental workflows

Many provider-specific, one-shot and experiment-specific YAML files are intentionally retained because they are referenced by frozen evidence, Actions provenance, ADRs or reproduction paths.

Examples include historical provider-free/provider-live campaigns and experiment-specific EV/D-series wrappers.

Do not infer that these workflows are safe or authorized to rerun simply because they still exist.

## Lifecycle rules

- retain consumed/failed workflows when needed for provenance or reproducibility;
- do not rerun a one-shot/consumed workflow merely because its YAML remains present;
- prefer a new versioned workflow/authorization when a prospectively allowed material execution changes;
- pin source/runtime contracts where the frozen protocol requires it;
- separate provider-free checks from live-provider execution;
- never expose provider/evaluator/blind secrets or hidden outcomes through cleanup or logging changes;
- a workflow that executes multiple scientific gates must not be used when the current authorization permits only an earlier subset.

## Cleanup rule

Do not bulk-delete or rename historical workflow YAML for visual cleanliness.

Before physical cleanup, prove the workflow is not:

- referenced by a frozen manifest/result;
- referenced by an Actions provenance record or ADR;
- required by a reproduction path;
- referenced from an active workflow.

When a historical workflow is unsafe to leave triggerable, disable it prospectively while preserving the exact historical source/run provenance.

## Rule for new workflows

Avoid adding one workflow per small code path.

Prefer:

1. reusable workflow contracts;
2. a small stable set of top-level gates;
3. matrix jobs for equivalent variants;
4. scripts/modules for shared logic rather than duplicated YAML.

Every new workflow should have an explicit lifecycle: `required`, `specialized`, `experimental`, or `historical-one-shot`.
