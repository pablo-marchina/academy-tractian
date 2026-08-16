# E2 — Canonical ToolSpec + Evaluation Harness

E2 is intentionally **framework-neutral**. It freezes contracts and evaluation semantics without selecting an agent runtime, model, MCP topology, RAG stack, multi-agent design or observability vendor.

## Components

- `models.py` — executable ScenarioSchema v1, Canonical ToolSpec, TraceSchema v1 and execution bindings.
- `tool_registry.py` — 18 canonical operations derived from the frozen contract/behavior evidence.
- `binding.py` — runner-owned identity/seed injection; model-controlled identity/seed are rejected.
- `trace.py` — deterministic trace invariants.
- `replay.py` — request/observation replay with collision detection.
- `evaluators.py` — structured evaluator interface and deterministic baseline evaluators.
- `provenance.py` / `hash.py` — configuration/artifact hashing and reproducible run manifests.

## Design invariants

1. `x-user-id` and `seed` are runner-bound.
2. Reference trajectories are not exact-match scripts.
3. Hard policy/identity/trace checks are deterministic.
4. Action success uses the supplied API's accepted-event semantics; no implicit final-state mutation oracle.
5. Replay never invents an observation.
6. Evaluation outputs are structured and separately inspectable; there is no arbitrary global score here.

## Runtime neutrality

The package has no dependency on LangGraph, Pydantic AI, OpenAI Agents SDK, MCP, RAG, vector databases or any LLM provider. Those remain experimental decisions for E6/E7/E8.
