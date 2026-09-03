# Full-product Playwright acceptance

This gate implements the browser/product acceptance owned by issues #114 and #131. It intentionally runs against the provider-free **production path**, not a fixture-only frontend or a mocked API.

## Executed topology

`Chromium -> React/Vite -> REST/SSE -> FastAPI -> PostgreSQL operational state -> ActionProposalRealtimeProductionRuntime -> AgentController -> HarnessRunner -> typed ToolSpec + deterministic policy -> bounded provider-free dependency substitute -> RunTrace -> evaluator -> DuckDB safe read model -> React`

The provider-free substitute replaces only external model/API availability. Runtime, typed tool binding, B1/B2/B3 policy behavior, action custody/idempotency, PostgreSQL ownership/RLS, SSE persistence/replay, evaluation and frontend rendering remain the production implementation.

## Browser hard gates

- real run submission returns a safe `run_*` id;
- genuine persisted SSE events render in sequence without logical duplicates;
- disconnect/reconnect uses `Last-Event-ID`, exposes `RECONNECTING` and `CAUGHT_UP`, and reaches terminal state without reload;
- evaluation is absent while the slow runtime is still active and appears only after completion;
- Trace Graph, Architecture Explorer, Evidence Explorer, Output Lineage, Mission Control and Dynamic Data Explorer render from backend state;
- selected-run analytics and drill-down use the same global run scope;
- clarify, abstain, escalate, tool-error and blocked-action outcomes are visible;
- pending consequential action requires explicit operator confirmation;
- a confirmed action follows a separate realtime execution run;
- duplicate confirmation is rejected;
- another user in the same organization cannot read/stream/confirm the run/action;
- the same user in another organization cannot read/stream/confirm the run/action;
- browser/API/SSE projections contain none of the forbidden private keys asserted by the test;
- unsupported chart types are absent from the UI allow-list and rejected by the backend contract;
- long input and desktop/mobile acceptance viewports do not create horizontal page overflow.

## CI environment

The GitHub Actions gate uses PostgreSQL 18, a separate non-owner/non-superuser/non-BYPASSRLS scoped role, Python 3.11, Node 24, the committed npm lockfile, Chromium from the pinned Playwright version, one Playwright worker in CI and the same Vite proxy used by the product frontend.

Artifacts retain the Playwright HTML report, traces/screenshots/videos on failure, and backend/frontend logs. A merge claim is valid only after the final PR SHA is green.
