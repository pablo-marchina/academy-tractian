# Codebase Map

**Status:** ACTIVE implementation navigation  
**Last verified:** 2026-09-07 BRT  
**Current merged backend source:** `3545d75c00ca30419e0f47e8b1950aa50cbbf462`

Use this before adding a file: **which existing domain owns the change?**

## End-to-end ownership

```text
frontend task-driven UI
→ authenticated REST/SSE
→ managed-session product API
→ PostgreSQL runtime ownership/RLS
→ V13 DecisionSource / AgentController
→ HarnessRunner / ToolSpec / TRACTIAN transport
→ read evidence OR governed action custody/confirmation
→ evaluator
→ PostgreSQL safe projection/action state
→ result / Analyses / Technical UI
```

## Backend domains — `src/academy_tractian/`

### Runtime / orchestration

`runtime.py`, `realtime_runtime.py`, `decision_source.py`, `runtime_handoff_supervisor.py`, run-access/execution-store modules own decision-loop lifecycle, durable ownership and execution state.

### Release 0 provider / production composition

Current read-serving chain is explicit:

- `release_provider.py` — base Release 0 provider contract/schema;
- `release_provider_v10.py` — structured nested ID extraction, condition-evidence/stopping constraints;
- `release_provider_v11.py` — customer-visible response-mode semantics;
- `release_provider_v12.py` — explicit human asset labels, comparison grounding, data-quality requirements, post-fleet `get_asset` suppression;
- `release_provider_v13.py` — initial `get_current_user` grounding and completed single-asset data-quality suppression;
- `remote_server.py` — production composition, provider/TRACTIAN/action gates;
- `production_config.py` — fail-closed production environment contract.

Do not infer final provider selection from Release 0 composition. Frozen provider decision remains separate.

### TRACTIAN capability / transport

Canonical ToolSpecs live under the accepted `research/e2` registry. Production network ownership is centered on:

- `tractian_transport.py` — real canonical HTTPS boundary, server-managed headers, path/query/body validation, redirect denial, response normalization;
- `release0_capabilities.py` — browser-safe capability truth;
- `governed_write_transport_smoke.py` — manual-only production validator for the five canonical writes.

All real tool execution stays behind `HarnessRunner`; do not create a second network bypass.

### Consequential actions / safety

Current production action owners include:

- `production_actions_v2.py` and PostgreSQL action-runtime equivalents — proposal custody, exact confirmation preparation, execution state;
- `action_safety.py` — canonical permission/resource/confirmation/idempotency policy;
- `trusted_action_authorization.py` — server-owned tenant-aware grant source;
- PostgreSQL custody/idempotency/action-execution/lease/recovery modules — durable one-shot ownership and restart/horizontal safety;
- action-capable product API composition — authenticated confirmation boundary;
- `governed_write_transport_smoke.py` — hosted 5-action acceptance gate.

Promoted local invariants:

```text
proposal != execution
browser/model != permission authority
confirmation != argument replacement
persistent idempotency before I/O
lease/generation fencing
ACCEPTED only on explicit upstream acceptance
UNCERTAIN never blindly retried
```

### Upstream action actor routing — current integration gap

The supplied TRACTIAN runtime uses `x-user-id` as vendor actor context and applies `action_low`, `action_high` or `escalate` permissions. Live validation showed distinct vendor users for low-impact versus high-impact/escalation actions in the tested company scope.

The current base execution binding couples the local requester user ID to `x-user-id`. That coupling is insufficient for all five vendor action families.

Corrective design:

```text
local product user
→ remains auth / tenant / resource / confirmation / audit principal

(company_id, required_permission)
→ server-owned vendor actor
→ injected only at final action transport boundary
```

Implementation is in progress on `fix/server-owned-upstream-action-actors`. It is **not** part of the current production source until merged and must not be documented as completed behavior.

New code for this area belongs in a narrow trusted action-identity/transport owner, not in browser code, model prompts or grant-widening shortcuts.

### Product APIs

`product_api.py`, `postgres_product_api.py`, authenticated/Neon-auth composition, observability APIs and action product APIs own HTTP/runtime integration. `/api/runs` is authenticated and derives trusted context server-side; browser payloads never become canonical tenant/action authority.

### Identity / tenant scope

Key current owners:

- `neon_auth_identity.py` — managed-session validation, ≤2 s GET/HEAD cache, SHA-256 cookie key, singleflight, fresh non-read validation, 401/503 distinction;
- `neon_authenticated_postgres_product_api.py` — managed-session product composition and browser-safe session context;
- PostgreSQL scoped product stores/RLS — independent tenant boundary.

Browser code must never become canonical tenant/permission/vendor-actor authority.

### PostgreSQL persistence

Operational state, observability, runtime handoff, action custody/idempotency/execution/lease state, semantic review and operational-value stores use PostgreSQL in production. Do not silently move production truth to local files/DuckDB.

### Observability / realtime

`observability*`, `realtime_observability.py`, `realtime_wakeup.py`, `production_telemetry.py` and operational read-model modules own safe traces and delivery. Durable cursor/state is authoritative; wake-up is not authorization/correctness truth.

Action grants, raw custody, idempotency keys and vendor actor mappings are not browser-safe observability data.

### Evaluation / EDD

Deterministic evaluation, EDD, semantic calibration, failure/stability/communication campaigns and operational-value research live here. New adaptive/model/framework behavior enters as a challenger/evaluation surface before replacing a promoted path.

## Frontend — `frontend/src/`

### Top-level composition

- `App.tsx` — task-driven application state with home/result/evidence/history/technical views;
- primary navigation components — Home / Analyses / Technical;
- `ProductExperience.tsx` — customer-facing run result/progress/outcome semantics;
- `RunExplorer.tsx`, `TraceGraph.tsx`, `OperationsWorkspace.tsx` — history/runtime/technical inspection;
- `ArchitectureExplorer.tsx`, `Release0CapabilitySurface.tsx`, `ActionControl.tsx` — system/capability/action-depth surfaces.

### Action UI boundary

`ActionControl.tsx` exposes human-readable action state and exact confirmation without becoming action authority. It may show impact/permission/confirmation/execution summaries but must not expose raw grants, private custody, idempotency material or vendor actor configuration.

Current user-facing states include waiting/confirmed/running/accepted/blocked/not accepted/outcome-needs-verification equivalents mapped from the canonical backend action states.

### Authentication

- `auth/AuthBoundary.tsx` — checking/anonymous/authenticated/unavailable states, focus/visibility reconciliation and retry UI;
- managed-auth event plumbing — protected-API auth signals;
- browser API client — invalid session vs temporary session-service unavailability.

### Current task-driven information architecture

**Home** owns question entry and first-use simplicity.  
**Result/evidence** owns the selected run's conclusion/support.  
**Analyses** owns persisted history.  
**Technical** groups specialist analysis / quality / data / system / actions / studies.

The latest UX target is stricter: one primary question/action per screen, less simultaneous card/panel/status density, evidence contextual to Result and Technical outside the normal path. This is an active structural simplification target, not a completed human-usability claim.

Frontend state visualizes server-owned truth; it does not decide tenant authority, agent policy or vendor action identity.

## Tests

- `tests/` — backend/product/regression/integration, including V10–V13, managed-session, all-governed-actions, action safety/config/recovery/lease coverage;
- frontend Vitest — pure UI/auth/result/action-state semantics;
- `frontend/e2e/` + Playwright — task-driven browser acceptance;
- `research/e2/tests/` — accepted controller/tool/evaluator harness.

PR #213 required-gate run `34164123263` passed:

- production wheel/runtime;
- PostgreSQL action execution lease/fencing/restart semantics;
- horizontal Postgres runtime/handoff;
- Railway IaC contracts;
- remote production image/source-drift checks;
- clean-clone full product reproduction;
- Chromium full-product Playwright;
- final required gate.

The live write smoke is separate hosted evidence: it correctly surfaced `update_asset_config` HTTP 403 rather than allowing CI to stand in for vendor acceptance.

## Workflows / deployment

See [`../.github/workflows/README.md`](../.github/workflows/README.md). Distinguish normal regression, exact-SHA production promotion, fresh Railway configuration snapshots and historical one-shot research workflows.

Important: Railway generic `redeploy` can reuse a captured snapshot. A changed pre-deploy/configuration contract needs a fresh snapshot before it becomes evidence.

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
7. For action identity, does the change preserve local requester authorization while keeping vendor actor selection server-owned and fail-closed?

Prefer extending a clear owner over creating another parallel path.

See [`progress/2026-09-07-production-governed-actions-ux-and-validation.md`](progress/2026-09-07-production-governed-actions-ux-and-validation.md) for current implementation/evidence boundaries.