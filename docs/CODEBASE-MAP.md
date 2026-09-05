# Codebase Map

This document maps the current code surface without changing import paths or frozen evidence.

Its purpose is to answer a simple question before new development: **where should a change live?**

## Promoted runtime flow

```text
FastAPI product API
→ authenticated runtime context
→ PostgreSQL tenant-scoped state
→ RealtimeProductionRuntime
→ DecisionSource
→ AgentController / HarnessRunner
→ typed TRACTIAN tools
→ normalized evidence
→ decision / action proposal
→ ProductionEvaluator
→ PostgreSQL observability projection
→ REST / SSE / React control room
```

## Backend domains

### Runtime and orchestration

Primary modules include:

- `runtime.py`
- `realtime_runtime.py`
- `decision_source.py`
- `runtime_identity.py`
- `runtime_handoff_supervisor.py`
- `run_access.py`
- `run_execution_store.py`

Changes that alter the agent execution lifecycle belong here.

### Product APIs

Primary modules include:

- `product_api.py`
- `postgres_product_api.py`
- `authenticated_postgres_product_api.py`
- `observability_api.py`
- `action_product_api.py`

HTTP contracts should remain thin over product services/storage contracts rather than owning core decision logic.

### Consequential actions and safety

Primary modules include:

- `controlled_actions.py`
- `action_safety.py`
- `production_actions_v2.py`
- `action_execution_lease.py`
- `postgres_action_execution_lease.py`
- `action_recovery.py`
- `action_evaluation.py`
- `controlled_action_evaluation.py`

Hard safety boundaries, confirmation, custody, idempotency and execution ownership remain deterministic.

### PostgreSQL persistence

Primary modules include:

- `postgres_operational.py`
- `postgres_observability_store.py`
- `postgres_runtime_handoff.py`
- `postgres_action_operational.py`
- `postgres_semantic_review.py`
- `postgres_operational_value.py`

The promoted serving path uses PostgreSQL as durable truth. New serving persistence should not introduce local-file state.

### Observability and realtime delivery

Primary modules include:

- `observability.py`
- `observability_contract.py`
- `observability_store.py`
- `realtime_observability.py`
- `realtime_wakeup.py`
- `production_telemetry.py`
- `operational_read_model.py`

Durable rows/cursors are authoritative; wake-up/delivery mechanisms are not authorization boundaries.

### Evaluation and EDD

Primary modules include:

- `evaluation.py`
- `eval_driven.py`
- `semantic_evaluation.py`
- `semantic_human_calibration.py`
- `adaptive_stopping.py`
- `failure_campaign.py`
- `stability_campaign.py`
- `communication_campaign.py`
- `operational_value.py`
- `operational_value_analysis.py`
- `operational_value_collection.py`

New adaptive/model/framework behavior should enter first as a challenger/evaluation surface, not by silently replacing the promoted runtime.

### Provider/research compatibility surface

The package currently contains several `provider_*` and `cloudflare_*` modules created by earlier provider experiments and live/provider-free campaigns.

Do not assume these modules are production-core merely because they live under `src/academy_tractian/`. Before deleting or moving them, run a reachability audit against:

- imports from promoted runtime/API modules;
- tests;
- active workflows;
- research execution bundles;
- frozen evidence/source pins.

This is the primary target for the **second cleanup pass**.

## Frontend

`frontend/src/` is organized around:

- `api/` — backend contracts/client access;
- `components/` — product UI surfaces;
- `hooks/` — reusable product hooks;
- `state/` — client state;
- `App.tsx` — top-level composition;
- domain CSS files — current styling surface.

The frontend should visualize server-owned state; it must not become an authorization or decision source.

## Tests

- `tests/` — backend/product/regression/integration tests;
- `frontend/src/**` + Vitest — frontend unit/component tests;
- `frontend/e2e/` + Playwright — full-browser acceptance.

See [`../tests/README.md`](../tests/README.md) for organization rules.

## Scripts

`scripts/` is a CLI/validation/reporting surface only. Reusable logic belongs in the package. See [`../scripts/README.md`](../scripts/README.md).

## Research/evidence

`research/` preserves experiment history and accepted E2 contracts. It should not be treated as a miscellaneous code directory.

See [`../research/README.md`](../research/README.md) before moving or deleting anything there.

## Target package shape after reachability audit

A future non-functional refactor may split the flat package into domains such as:

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

That split is **not yet authorized by this cleanup**. It should happen only after import/path provenance is mapped and CI proves compatibility, ideally with temporary compatibility shims where frozen or external paths require them.

## Rule for new code

Before creating a new module, ask:

1. Is this product runtime, evaluation, storage, observability, API, action safety or research-only?
2. Does an existing module already own the responsibility?
3. Is the logic reusable/importable, or is it only a CLI wrapper?
4. Does the change need an evaluator/baseline before promotion?
5. Will the new path become part of a frozen evidence contract?

Avoid adding another top-level module when an existing domain already owns the behavior.
