# Full-product Playwright acceptance

**Status:** ACTIVE / canonical browser acceptance contract  
**Checkpoint:** 2026-09-05 BRT

This gate implements browser/product acceptance against the provider-free **production path**, not a fixture-only frontend or mocked product API.

## Executed topology

```text
Chromium
→ React/Vite
→ REST/SSE
→ FastAPI
→ signed runtime context + PostgreSQL tenant RLS
→ PostgreSQL ownership / runtime handoff / action custody
→ ActionProposalRealtimeProductionRuntime
→ AgentController
→ HarnessRunner
→ typed ToolSpec + deterministic B1/B2/B3 policy
→ bounded provider-free dependency substitute
→ RunTrace
→ post-runtime evaluator
→ safe PostgreSQL observability/evaluation rows
→ LISTEN/NOTIFY wakeup + durable cursor fallback
→ React
```

The provider-free substitute replaces only external model/API availability. Runtime, typed tool binding, B1/B2/B3 behavior, PostgreSQL ownership/RLS, read-only handoff, action custody/idempotency/lease fencing, SSE persistence/replay, evaluation and frontend rendering remain production implementations.

DuckDB is not part of this production browser topology.

## Browser hard gates

- real run submission returns a safe `run_*` id;
- genuine persisted SSE events render in sequence without logical duplicates;
- disconnect/reconnect uses `Last-Event-ID`, exposes reconnect/caught-up state and reaches terminal state without reload;
- evaluation is absent while the slow runtime is active and appears only after completion;
- Trace Graph, Architecture Explorer, Evidence Explorer, Output Lineage, Mission Control and Dynamic Data Explorer render from backend state;
- selected-run analytics/drill-down use the same global run scope;
- clarify, abstain, escalate, tool-error and blocked-action outcomes are visible;
- pending consequential action requires explicit operator confirmation;
- confirmed action follows a separate realtime execution run;
- duplicate confirmation is rejected;
- browser confirmation cannot inject raw action args, requester identity, permissions, scope or idempotency key;
- another user in the same organization cannot read/stream/confirm the run/action;
- the same user in another organization cannot read/stream/confirm the run/action;
- browser/API/SSE projections contain none of the forbidden private keys asserted by the test;
- unsupported chart/query combinations are rejected by the safe backend/UI contract;
- long input and desktop/mobile acceptance viewports do not create horizontal page overflow.

Distributed ownership/fencing is additionally required by the reusable horizontal-runtime and action-execution-lease jobs in `final-ci-required`; Chromium is not used to infer distributed exactly-once side effects.

## CI environment

The gate uses:

- PostgreSQL 18;
- a separate non-owner/non-superuser/non-`BYPASSRLS` scoped role;
- Python 3.11;
- Node 24;
- committed npm lockfile + deterministic `npm ci`;
- Chromium from the pinned Playwright dependency;
- one Playwright worker in CI;
- the product Vite proxy and provider-free production backend.

Artifacts retain the Playwright HTML report, traces/screenshots/videos on failure, and backend/frontend logs.

A merge claim is valid only after the exact final PR head is green. Final branch acceptance additionally requires `required-gate`, which aggregates clean clone, Chromium, horizontal runtime handoff and action execution lease.