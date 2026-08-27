# E6 — Runtime Discriminating Spike / ADR Result

**Date:** 2026-08-16  
**Status:** EXECUTED / ADR-CANDIDATE-RECORDED  
**Selected current runtime candidate:** LangGraph  
**LOCKED_TEST:** not accessed  
**Model/MCP/RAG/UI freeze:** no

E6 compared LangGraph, Pydantic AI/Graph and OpenAI Agents SDK under the same project constants:

- Canonical ToolSpec v1;
- B3 guarded-boundary candidate from E4;
- evidence-sufficiency/stopping policy from E5;
- DEV + VALIDATION only;
- no LOCKED_TEST access;
- no model/provider, MCP topology, RAG/vector DB, multi-agent, observability or UI freeze.

## Evidence basis

The spike uses a preregistered scorecard from `research/experiments/e6-runtime-spike-manifest.json` and CI validation through `scripts/research/e6_runtime_spike_runner.py`.

External documentation anchors used for the scorecard:

- LangGraph official docs: durable execution, persistence/checkpoints, human-in-the-loop, interrupts and fault-tolerant execution.
- Pydantic AI/Graph official docs: graph support, durable execution integrations, OpenTelemetry/Logfire observability and eval alignment.
- OpenAI Agents SDK official docs: tracing, guardrails, sessions, human-in-the-loop and MCP integration.

This is runtime ADR-direction evidence, not an end-to-end agent-quality benchmark.

## Scorecard

| Runtime | Weighted score | Trace completeness | Guard integration | Replay determinism | Pause/resume/HITL | Lower complexity | Portability | Lower overhead |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LangGraph | 4.404 | 4.2 | 4.4 | 5.0 | 5.0 | 3.2 | 4.2 | 3.6 |
| Pydantic AI/Graph | 4.328 | 4.6 | 4.7 | 4.1 | 4.0 | 4.2 | 4.5 | 4.1 |
| OpenAI Agents SDK | 4.188 | 4.7 | 4.2 | 3.9 | 4.5 | 4.3 | 3.4 | 4.2 |

## Decision

| Candidate | Decision | Reason |
|---|---|---|
| LangGraph | Promote as current runtime candidate | Strongest replay/checkpointing, pause/resume and HITL fit for the B3 + evidence-sufficiency bundle. |
| Pydantic AI/Graph | Retain as fallback/comparator | Strong schema, typed validation, graph and observability fit; slightly weaker on single-runtime replay/HITL fit. |
| OpenAI Agents SDK | Retain as provider-native comparator | Strong tracing/guardrails/HITL/MCP ergonomics; lower portability while model/provider remains unfrozen. |

## Why LangGraph advances

The strongest discriminators for this project are not generic popularity or newest SDK features. They are:

1. deterministic replay/checkpointing;
2. pause/resume and human approval compatibility;
3. ability to keep B3 action gating outside the model;
4. clean trace emission into the existing TraceSchema;
5. ability to express evidence acquisition as explicit graph state;
6. low risk of accidentally freezing the model/provider.

LangGraph ranks first because those criteria are most aligned with its runtime model.

## What is not decided

E6 does **not** decide:

- final model/provider;
- MCP topology;
- RAG/vector DB;
- multi-agent decomposition;
- persistent-memory design;
- observability backend;
- UI/demo flow.

## Next step

The next stage should be a LangGraph integration spike using the already selected policy bundle:

```text
E6 follow-up / LangGraph integration spike
├── implement minimal graph around the existing ToolSpec
├── keep B3 boundary as external deterministic guard
├── keep evidence-sufficiency policy explicit
├── emit TraceSchema-compatible events
├── test checkpoint/replay/pause-resume behavior
├── compare overhead against the current harness
├── keep Pydantic AI/Graph and OpenAI Agents SDK as comparators
└── keep LOCKED_TEST blocked
```

This produces an implementation-grade runtime ADR only after the integration spike confirms the proxy scorecard.
