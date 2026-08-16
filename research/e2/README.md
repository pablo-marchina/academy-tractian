# E2 — Canonical ToolSpec + Evaluation Harness

E2 is intentionally **framework-neutral**. It freezes contracts and evaluation semantics without selecting an agent runtime, model, MCP topology, RAG stack, multi-agent design or observability vendor.

## Components

- `models.py` — executable ScenarioSchema v1, Canonical ToolSpec, TraceSchema v1 and execution bindings.
- `tool_registry.py` — 18 canonical operations derived from frozen contract/behavior evidence.
- `binding.py` — runner-owned identity/seed injection.
- `transport.py` — minimal B0 HTTP transport and contract-valid request construction.
- `validation.py` — strict deterministic argument validation foundation for B1.
- `policy.py` — deterministic permission/resource-scope guard foundation for B2.
- `action_gate.py` — evidence-aware deterministic pre-execution gate for B3.
- `trace.py` — deterministic trace invariants.
- `trace_normalize.py` — normalization of volatile identifiers/timestamps for replay comparison.
- `replay.py` — request/observation replay.
- `evaluators.py` — structured deterministic evaluator interface and baseline evaluators.
- `evaluator_extensions.py` — structured argument, conclusion/fact and escalation/handoff evaluators.
- `provenance.py` / `hash.py` — configuration/artifact hashing.

## Invariants

1. `x-user-id` and `seed` are runner-bound.
2. Reference trajectories are not exact-match scripts.
3. Hard policy/identity/trace checks are deterministic.
4. Action success uses the supplied API's accepted-event semantics; no implicit final-state mutation oracle.
5. Replay never invents observations.
6. There is no arbitrary global score in E2.
7. B0 is a transport baseline, not a product/demo architecture.
8. Demo or test-double behavior is never treated as evidence of agent quality.

## Runtime neutrality

No LangGraph, Pydantic AI/Graph, OpenAI Agents SDK, MCP, RAG, vector DB or LLM provider is selected here. Those remain later experimental decisions.

## Unlock condition for E3

E3 starts only after the integrated B0 runner executes a representative reference scenario, trace capture/replay is stable, deterministic guard/evaluator fixtures pass, and no new contract/gold inconsistency is found.
