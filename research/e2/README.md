# E2 — Canonical ToolSpec + Evaluation Harness

E2 is **COMPLETE** and intentionally framework-neutral. It freezes executable contracts and evaluation infrastructure without selecting an agent runtime, model, MCP topology, RAG stack, multi-agent design or observability vendor.

## Components

- `models.py` — executable ScenarioSchema v1, Canonical ToolSpec, TraceSchema v1 and execution bindings.
- `tool_registry.py` — 18 canonical operations derived from frozen contract/behavior evidence, including explicit per-tool seed support.
- `binding.py` — runner-owned identity/seed injection.
- `transport.py` — B0 contract-valid request construction and HTTP transport boundary.
- `validation.py` — strict deterministic argument validation foundation for B1.
- `policy.py` — deterministic permission/resource-scope guard foundation for B2.
- `action_gate.py` — evidence-aware deterministic action gate for B3.
- `runner.py` — integrated framework-neutral live/replay execution harness with proposal/call/result/observation tracing.
- `trace.py` / `trace_normalize.py` — deterministic trace invariants and volatile-field normalization.
- `replay.py` — request/observation replay without invented observations.
- `evaluators.py` / `evaluator_extensions.py` — structured deterministic evaluator implementations.
- `evaluation_suite.py` — integrated evaluator runner without arbitrary weighted score.
- `conformance.py` — registry-vs-OpenAPI conformance logic.
- `provenance.py` / `hash.py` — configuration/artifact hashing.
- `tests/` — deterministic pass/fail, guard, runner, replay, evaluator and conformance fixtures.

## Invariants

1. `x-user-id` and `seed` are runner-bound.
2. Reference trajectories are not exact-match scripts.
3. Hard policy/identity/trace checks are deterministic.
4. Action success uses the supplied API's accepted-event semantics; no implicit final-state mutation oracle.
5. Replay never invents observations.
6. Model/runtime tool proposals are traced separately from executed calls.
7. There is no arbitrary global score in E2.
8. Test doubles and scripted paths validate infrastructure only; they are not evidence of agent quality.

## Validation

- GitHub Actions on Python 3.13.15: **24 tests passed**.
- Independent registry check against the supplied OpenAPI: **18/18** operations/methods/routes/canonical parameter tuples matched.
- **12** read operations are explicitly seed-capable; seed remains runner-controlled.
- CEN-01 supplied-API transport path: 5/5 HTTP 200 and final escalation `accepted=true`.

See `research/39-e2-integrated-completion-report.md` for the evidence trail, including the initial CI failure that exposed and led to correction of an action-scope metadata defect.

## Runtime neutrality

No LangGraph, Pydantic AI/Graph, OpenAI Agents SDK, MCP, RAG, vector DB or LLM provider is selected here. Those remain later experimental decisions.
