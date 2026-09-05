# Repository Cleanup Audit — 2026-09-05

## Scope

This audit records the non-functional cleanup performed before the next product-development phase.

The cleanup follows one safety rule: **repository cleanliness must not destroy scientific provenance**. Frozen results, source-pinned experiment paths, accepted ADRs and historical workflow code are preserved unless reachability/reproduction safety is proven.

## Pass 1 — navigation and ownership

Completed on branch `chore/repository-cleanup`:

- replaced the root README with a concise canonical entrypoint;
- corrected promoted storage wording: PostgreSQL is the serving/operational/observability truth; DuckDB is dev/benchmark compatibility only;
- created `docs/CODEBASE-MAP.md`;
- created `tests/README.md` and `scripts/README.md`;
- updated `research/README.md` with evidence lifecycle and placement rules;
- updated `docs/README.md` with canonical document ownership and anti-drift rules;
- updated `.github/workflows/README.md` to distinguish required product CI from historical experiment workflows;
- expanded `.gitignore` for build/cache/report/local-secret artifacts.

The first cleanup commit passed `final-ci-required` successfully. No runtime, frozen evidence or accepted experiment path was moved.

## Pass 2 — workflow activation cleanup

Opening a documentation-only cleanup PR exposed a CI-organization defect: historical research workflows were still subscribed to ordinary product pull requests.

The PR triggered DEV-only and historical research jobs including E14j/E14k/E14l/E14m/E14o, benchmark-split audit, BIG-B protocol self-check, E9 scorer audit, E14m-R1 tooling and E9-v4 structural checks.

For those historical workflows, this pass removes only the automatic `pull_request` trigger. The workflow body remains available through `workflow_dispatch`; research-branch push triggers are retained where they already existed.

`research-e2.yml` is deliberately not rewritten in this pass. It is a large legacy suite with explicit path filtering rather than a global PR trigger. It ran because this cleanup intentionally changed paths listed in its legacy filter (`README.md` / `research/README.md`). Its trigger/path contract should be simplified in a dedicated workflow-consolidation change rather than hidden inside a documentation cleanup.

## Current CI classes

### Required product gate

- `.github/workflows/final-ci-required.yml`
  - clean-clone full-product reproduction;
  - full-product Playwright;
  - horizontal runtime handoff;
  - action execution lease;
  - stable `required-gate` result.

### Specialized product checks

Provider-free product/runtime/observability/eval/handoff checks remain available while their coverage is compared against the required gate. They are candidates for later consolidation, not immediate deletion.

### Historical / experiment-specific

E-series, BIG-B and provider experiment workflows are evidence/reproduction surfaces. They should normally be manual or research-branch scoped, not automatic product-PR gates.

## Physical cleanup intentionally deferred

The following areas look structurally noisy but require a reachability audit before removal or relocation:

1. `src/academy_tractian/provider_*`;
2. `src/academy_tractian/cloudflare_*`;
3. versioned implementation modules (`*_v1`, `*_v2`, etc.);
4. duplicate/near-duplicate scripts under `scripts/research/`;
5. experiment-specific workflows that may now be fully superseded;
6. flat historical tests whose exact paths may be referenced by workflows/evidence.

## Required reachability proof before deletion/move

For each candidate artifact, collect:

- imports from promoted runtime/API modules;
- imports from tests;
- references from active workflows;
- references from scripts;
- references from ADRs/current docs;
- exact path/blob references from frozen manifests/results;
- reproduction/handoff references.

Then classify:

```text
ACTIVE_CORE
ACTIVE_SPECIALIZED
COMPATIBILITY
RESEARCH_ONLY
HISTORICAL_PINNED
DEAD_SAFE_TO_REMOVE
```

Only `DEAD_SAFE_TO_REMOVE` may be deleted without a compatibility shim. Moves of `HISTORICAL_PINNED` are prohibited unless the frozen provenance contract explicitly permits it.

## Package-layout target

A future refactor may move the current flat package toward:

```text
academy_tractian/
  api/
  runtime/
  actions/
  storage/
  observability/
  evaluation/
  providers/
```

That refactor is **not part of this cleanup pass**. It should start only after the reachability map exists and the full required CI is green.

## Exit criteria before feature development

Repository cleanup is ready to hand off to development when:

- canonical navigation has one source of truth per question;
- normal product PRs do not execute historical one-shot research campaigns;
- required CI remains green;
- frozen evidence/reproduction paths remain intact;
- dead-code candidates are explicitly classified instead of guessed;
- the next feature can be placed in an obvious product domain without creating another miscellaneous top-level module.
