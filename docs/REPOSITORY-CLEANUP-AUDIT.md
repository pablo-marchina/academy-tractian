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

The PR initially triggered DEV-only and historical research jobs including E14j/E14k/E14l/E14m/E14o, benchmark-split audit, BIG-B protocol self-check, E9 scorer audit, E14m-R1 tooling, E9-v4 structural checks and the old E2→E8 free-anywhere pilot suite.

This pass removes the automatic `pull_request` trigger from those historical/DEV-only research workflows. Workflow bodies remain available through `workflow_dispatch`; the dedicated `research/systematic-foundation` push trigger is retained where it already existed.

This changes workflow **activation policy**, not the historical experiment implementation. Previous exact workflow versions remain in Git history and existing Actions runs retain their source provenance.

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

E-series, BIG-B, Cloudflare D-series and other provider experiment workflows are evidence/reproduction surfaces. They should normally be manual or research-branch scoped, not automatic product-PR gates.

## Preliminary source reachability classification

The most visually noisy source families were inspected before any physical cleanup.

### `ACTIVE_CORE`

- `provider_clients.py` — exported by `academy_tractian.__init__` together with the provider-neutral decision boundary; not dead code.
- core runtime/API/PostgreSQL/action/observability/evaluation modules represented in `docs/CODEBASE-MAP.md`.

### `ACTIVE_SPECIALIZED`

- `provider_free_product.py` and related provider-free helpers — exercise the real product/controller/storage/SSE/evaluation path in provider-free acceptance and CI. They are test/acceptance infrastructure, not production-provider selection.

### `HISTORICAL_PINNED` / `RESEARCH_ONLY`

- `cloudflare_*` modules — tied to explicit ADR-018 through ADR-027 records plus Cloudflare experiment workflows. They are historical/provider-experiment implementation evidence and are not safe bulk-deletion candidates.
- historical provider comparison/live-execution surfaces covered by ADR-008 through ADR-012 likewise require provenance-aware treatment before relocation/deletion.

No module from these named families has been classified `DEAD_SAFE_TO_REMOVE` on the evidence collected so far. Therefore this cleanup intentionally does not perform a cosmetic package move.

## Physical cleanup intentionally deferred

The following areas may still contain safe consolidation opportunities, but each requires exact-path reachability proof:

1. versioned implementation modules (`*_v1`, `*_v2`, etc.);
2. duplicate/near-duplicate scripts under `scripts/research/`;
3. experiment-specific workflows whose historical source is preserved elsewhere and no active/frozen record references the current path;
4. flat historical tests whose exact paths may be referenced by workflows/evidence;
5. specialized provider-free CI whose coverage may be redundant with `final-ci-required`.

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

A future non-functional refactor may move the current flat package toward:

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

That refactor is **not part of this cleanup pass**. It should start only after exact import/path provenance is mapped and the full required CI proves compatibility. Historical pinned modules may remain outside that ideal layout if moving them would weaken evidence provenance.

## Exit criteria before feature development

Repository cleanup is ready to hand off to development when:

- canonical navigation has one source of truth per question;
- normal product PRs do not execute historical one-shot research campaigns;
- required CI remains green;
- frozen evidence/reproduction paths remain intact;
- noisy source families are classified instead of guessed/deleted;
- the next feature can be placed in an obvious product domain without creating another miscellaneous top-level module.
