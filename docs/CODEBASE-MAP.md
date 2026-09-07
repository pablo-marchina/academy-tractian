# Codebase Map

**Status:** ACTIVE implementation navigation  
**Last verified:** 2026-09-07 BRT

Use this before adding a file: **which existing domain owns the change?**

## End-to-end ownership

```text
frontend task-driven UI
→ authenticated REST/SSE
→ managed-session product API
→ PostgreSQL runtime ownership/RLS
→ V13 DecisionSource / AgentController
→ HarnessRunner / ToolSpec / TRACTIAN transport
→ evidence + terminal + response_mode
→ evaluator
→ PostgreSQL safe projection
→ result / Analyses / Technical UI
```

## Backend domains — `src/academy_tractian/`

### Runtime / orchestration

`runtime.py`, `realtime_runtime.py`, `decision_source.py`, `runtime_handoff_supervisor.py`, run-access/execution-store modules own decision-loop lifecycle, durable ownership and execution state.

### Release 0 provider / production composition

Current serving chain is explicit:

- `release_provider.py` — base Release 0 provider contract/schema;
- `release_provider_v10.py` — structured nested ID extraction, condition-evidence/stopping constraints;
- `release_provider_v11.py` — customer-visible response-mode semantics;
- `release_provider_v12.py` — explicit human asset labels, comparison grounding, data-quality requirements, post-fleet `get_asset` suppression;
- `release_provider_v13.py` — force initial `get_current_user` for explicit-asset investigations and suppress completed single-asset data-quality reads;
- `remote_server.py` — serves the V13 factory;
- `production_config.py` — production environment contract.

Do not infer final provider selection from Release 0 composition. Frozen provider decision remains separate.

### TRACTIAN capability / transport

Canonical ToolSpecs live under the accepted `research/e2` registry and production transport/normalization modules. `ProductionTractianTransport` owns the real network contract.

All real tool execution stays behind `HarnessRunner`; do not create a second network bypass.

### Product APIs

`product_api.py`, `postgres_product_api.py`, authenticated/Neon-auth product composition, observability APIs and action product APIs own HTTP/runtime integration. `/api/runs` is authenticated and derives trusted context server-side; payload contains only the user request.

### Identity / tenant scope

Key current owners:

- `neon_auth_identity.py` — managed-session validation, ≤2 s GET/HEAD cache, SHA-256 cookie key, singleflight, fresh non-read validation, 401/503 distinction;
- `neon_authenticated_postgres_product_api.py` — managed-session product composition and browser-safe session context;
- PostgreSQL scoped product stores/RLS — independent tenant boundary.

Browser code must never become canonical tenant/permission authority.

### Consequential actions / safety

Controlled-action, action-safety, production-action, custody/idempotency/lease/recovery/evaluation modules contain the stronger future action architecture. Release 0 external execution remains disabled.

### PostgreSQL persistence

Operational state, observability, runtime handoff, action state, semantic review and operational-value stores use PostgreSQL in production. Do not silently move production truth to local files/DuckDB.

### Observability / realtime

`observability*`, `realtime_observability.py`, `realtime_wakeup.py`, `production_telemetry.py` and operational read-model modules own safe traces and delivery. Durable cursor/state is authoritative; wake-up is not authorization/correctness truth.

### Evaluation / EDD

Deterministic evaluation, EDD, semantic calibration, failure/stability/communication campaigns and operational-value research live here. New adaptive/model/framework behavior enters as a challenger/evaluation surface before replacing a promoted path.

## Frontend — `frontend/src/`

### Top-level composition

- `App.tsx` — task-driven application state with `home`, `result`, `evidence`, `history`, `technical` views;
- `components/PrimaryNavigation.tsx` — primary Home / Analyses / Technical navigation;
- `components/ProductExperience.tsx` — customer-facing run result/progress/outcome semantics;
- `components/RunExplorer.tsx`, `TraceGraph.tsx`, `OperationsWorkspace.tsx` — history/runtime/technical inspection;
- `components/ArchitectureExplorer.tsx`, `Release0CapabilitySurface.tsx`, `ActionControl.tsx` — system/capability/action-depth surfaces.

### Authentication

- `auth/AuthBoundary.tsx` — checking/anonymous/authenticated/unavailable states, focus/visibility reconciliation and retry UI;
- `auth/managedAuthEvents.ts` — protected-API auth signals;
- browser API client — classifies invalid session separately from temporary managed-session unavailability.

### Current task-driven information architecture

**Home** owns question entry and first-use simplicity.  
**Result/evidence** owns the selected run's conclusion/support.  
**Analyses** owns persisted history.  
**Technical** groups Current analysis / Quality / Data / System / Actions / Studies.

The earlier `DepthTabs`/four-layer components/styles may remain for compatibility/history, but they are not the current primary navigation contract.

Frontend state visualizes server-owned truth; it does not decide tenant authority or agent policy.

## Tests

- `tests/` — backend/product/regression/integration, including Release 0 V10–V13 and managed-session regression coverage;
- frontend Vitest — pure UI/auth/result semantics;
- `frontend/e2e/` + Playwright — task-driven browser acceptance;
- `research/e2/tests/` — accepted controller/tool/evaluator harness.

PR #210 passed the complete required backend regression surface before merge. PR #209 passed the required frontend/browser surface before the current frontend deployment.

## Workflows

See [`../.github/workflows/README.md`](../.github/workflows/README.md). Distinguish normal regression, intentional exact-SHA production promotion and historical one-shot research workflows.

## Research / scripts

- `research/` preserves experiment protocol/evidence; it is not miscellaneous code.
- `scripts/` should be thin CLI/validation/operations wrappers; reusable logic belongs in the package.

## New-code checklist

1. Which domain owns the responsibility?
2. Does an existing module already expose the needed contract?
3. Is it production logic or experiment/CLI-only logic?
4. Does a measured gap justify a new abstraction?
5. Does behavior need an evaluator/baseline before promotion?
6. Could the path become frozen evidence or external contract?

Prefer extending a clear owner over creating another parallel path.