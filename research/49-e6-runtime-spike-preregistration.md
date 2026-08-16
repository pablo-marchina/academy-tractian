# E6 — Runtime Discriminating Spike Preregistration

**Date:** 2026-08-16  
**Status:** PREREGISTERED  
**Scope:** DEV + VALIDATION metadata and project constraints only  
**LOCKED_TEST:** forbidden  
**Model/MCP/RAG/UI freeze:** no

E6 compares agent runtime candidates after E4 promoted the B3 guarded boundary and E5 promoted the evidence-sufficiency stopping policy. The runtime decision must preserve all prior frozen constraints: ToolSpec v1, runner-owned identity/seed, B3 boundary, evidence-sufficiency policy, private-gold isolation and LOCKED_TEST blocking.

## Question

Which runtime should be carried forward as the current implementation candidate for the selected boundary/stopping policy bundle?

Candidates:

1. LangGraph;
2. Pydantic AI/Graph;
3. OpenAI Agents SDK.

## Constants

E6 holds constant:

- Canonical ToolSpec / 18-operation registry;
- B3 guarded boundary: strict arguments + resource/permission guard + evidence-aware action gate;
- E5 evidence-sufficiency/stopping policy;
- DEV/VALIDATION-only evidence boundary;
- no LOCKED_TEST access;
- no model/provider final selection;
- no MCP topology final selection;
- no RAG/vector DB/multi-agent/UI final selection.

## Discriminating criteria

Runtime candidates are scored on a 0–5 ordinal scale, where higher is better. Scores are proxy ADR evidence, not agent task-quality metrics.

| Criterion | Weight | Meaning |
|---|---:|---|
| Trace completeness | 0.16 | Can the runtime expose LLM/tool/guard/handoff state cleanly into our TraceSchema? |
| Guard integration | 0.18 | Can B1/B2/B3 and evidence sufficiency intercept tool proposals before execution? |
| Replay determinism | 0.20 | Can runs be checkpointed/replayed/resumed without hiding tool-call behavior? |
| Pause/resume/HITL | 0.18 | Can the runtime support human approval or long-lived pauses when needed? |
| Lower complexity | 0.10 | Can the project implement the runtime without excessive ceremony or hidden state? |
| Portability | 0.12 | Can the runtime remain model/provider/tool-interface independent? |
| Lower overhead | 0.06 | Does the runtime avoid avoidable runtime/cognitive overhead? |

## Evidence basis

The scorecard uses current official documentation and already executed project constraints. It does not require importing the frameworks into CI yet, because E6 is a discriminating spike for runtime ADR direction, not final production integration.

External evidence anchors:

- LangGraph: official documentation describes durable execution, persistence/checkpointing, human-in-the-loop, streaming and fault-tolerant execution.
- Pydantic AI/Graph: official documentation describes durable execution integrations, graph support, OpenTelemetry/Logfire observability and code-first eval capabilities.
- OpenAI Agents SDK: official documentation describes guardrails, tracing, sessions, human-in-the-loop and MCP integration.

Project evidence anchors:

- E2 supplies framework-neutral ToolSpec/Trace/Replay contracts.
- E4 promotes B3 as the current guarded-boundary candidate.
- E5 promotes evidence-sufficiency/stopping as the current acquisition policy.

## Decision policy

E6 may select a **current runtime candidate** for the next implementation stage. It must not freeze:

- model/provider;
- MCP topology;
- RAG/vector DB;
- multi-agent decomposition;
- persistent-memory design;
- observability backend;
- UI/demo flow.

A runtime candidate can be revised if the next integration spike contradicts the proxy scorecard.
