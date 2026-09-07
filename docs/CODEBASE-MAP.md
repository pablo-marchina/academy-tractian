# Codebase Map

**Status:** ACTIVE implementation navigation  
**Last verified:** 2026-09-06 BRT

Use this before adding a file: **which existing domain owns the change?**

## End-to-end ownership

```text
frontend/
→ authenticated REST/SSE
→ product/auth API
→ Postgres runtime ownership
→ DecisionSource / AgentController
→ HarnessRunner / typed tools / TRACTIAN transport
→ evidence + terminal
→ evaluator
→ Postgres safe projection
→ frontend depth layers
```

## Backend domains — `src/academy_tractian/`

### Runtime / orchestration

Key modules include `runtime.py`, `realtime_runtime.py`, `decision_source.py`, `runtime_identity.py`, `runtime_handoff_supervisor.py`, `run_access.py` and `run_execution_store.py`.

Changes to decision-loop lifecycle, ownership or execution state belong here.

### Release 0 provider / production composition

Key modules include:

- `release_provider.py` — fail-closed provisional Release 0 provider composition;
- `production_config.py` — production environment contract;
- `remote_server.py` — production application composition;
- Cloudflare/provider client modules — provider boundary and historical/provider-free research support.

Do not infer final provider selection from Release 0 composition. `DP-004` remains separate.

### TRACTIAN capability / transport

Key ownership includes canonical runtime registry/ToolSpecs, `ProductionTractianTransport`, response normalization and Release 0 capability manifest (`release0_capabilities.py`).

All real tool execution stays behind `HarnessRunner`; do not create a second network bypass.

### Product APIs

Primary modules include `product_api.py`, `postgres_product_api.py`, authenticated product composition, observability APIs and `action_product_api.py`.

HTTP routes should remain thin over product/runtime/store contracts.

### Identity / tenant scope

Managed session validation and runtime-context composition own browser identity. PostgreSQL-scoped product stores own the independent RLS boundary.

Browser code must never become the canonical tenant/permission source.

### Consequential actions / safety

Primary modules include `controlled_actions.py`, `action_safety.py`, `production_actions_v2.py`, action custody/idempotency/lease/recovery/evaluation modules.

Release 0 external execution remains disabled even though these mechanisms exist and are testable.

### PostgreSQL persistence

Primary modules include operational state, observability store, runtime handoff, action operational state, semantic review and operational value stores.

Production truth is PostgreSQL. New production state must not silently move to local files/DuckDB.

### Observability / realtime

Primary modules include `observability*`, `realtime_observability.py`, `realtime_wakeup.py`, `production_telemetry.py` and the operational read model.

Durable cursor/state is authoritative; wake-up is not authorization/correctness truth.

### Evaluation / EDD

Primary modules include deterministic evaluation, EDD, semantic evaluation/calibration, failure/stability/communication campaigns, adaptive-stopping diagnostics and operational-value analysis/collection.

New adaptive/model/framework behavior should enter as a challenger/evaluation surface before it can replace a promoted path.

## Frontend — `frontend/src/`

### Top-level composition

- `App.tsx` — current four-layer workspace composition.
- `components/DepthTabs.tsx` — Results/Evidence/Investigation/Engineering navigation and keyboard semantics.
- `components/ProductExperience.tsx` — first-run onboarding, quick start, live stages, terminal next steps/evidence summary.

### Four depth layers

**Results** owns user-first outcome/input.  
**Evidence** owns canonical safe explanation trail.  
**Investigation** owns history/runtime/trace/action-control inspection.  
**Engineering** owns deep architecture/capability/evaluator/analytics/research surfaces.

### Supporting structure

- `api/` — browser-safe backend contracts/clients;
- `hooks/` — reusable live/product hooks;
- `state/` — deterministic client projections/metrics;
- CSS files — visual/layout/accessibility styling;
- components such as `RunExplorer`, `TraceGraph`, `ArchitectureExplorer`, `OperationsWorkspace`, `Release0CapabilitySurface`, `ActionControl` and controlled collectors.

Frontend state visualizes server-owned truth; it does not decide tenant authority or agent policy.

## Tests

- `tests/` — backend/product/regression/integration;
- `frontend/src/**` + Vitest — frontend logic tests;
- `frontend/e2e/` + Playwright — browser task/invariant acceptance;
- `research/e2/tests/` — accepted controller/tool/evaluator harness.

The UX baseline `2ca6215...` passed full Playwright and the required gate.

## Workflows

See [`../.github/workflows/README.md`](../.github/workflows/README.md). Distinguish normal regression, manual production promotion and historical one-shot research workflows.

## Research / scripts

- `research/` preserves experiment protocol/evidence; it is not miscellaneous code.
- `scripts/` should be thin CLI/validation/operations wrappers; reusable logic belongs in the package.

See `research/README.md`, `scripts/README.md` and `tests/README.md` before large cleanup/refactor work.

## New-code checklist

Before adding a top-level module:

1. Which domain owns the responsibility?
2. Does an existing module already expose the needed contract?
3. Is it production logic or experiment/CLI-only logic?
4. Does a measured gap justify a new abstraction?
5. Does the behavior need an evaluator/baseline before promotion?
6. Could the path become frozen evidence or external contract?

Prefer extending a clear owner over creating another parallel path.