# Post-E0/E1 Execution Backlog — E6 LangGraph Integration Executed

Status: **E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LANGGRAPH INTEGRATION EXECUTED; REAL TOOLSPEC GRAPH NEXT**

This file supersedes the pre-freeze task statuses in `research/06-research-backlog.md` for active execution. The older file is retained as historical planning evidence.

## Completed gates

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` semantics frozen.
- 16 scenarios / 17 tickets / 10 leakage groups frozen as grouping constraints.
- E2 integrated framework-neutral harness complete.
- `BENCHMARK-SPLIT-v1` frozen before runtime/model/prompt/architecture selection.
- E4 B0-B3 guarded-boundary DEV+VALIDATION comparison complete.
- E5 evidence acquisition/stopping comparison complete.
- E6 runtime discriminating spike complete.
- E6 minimal LangGraph integration spike complete.

## Current candidate policy/runtime bundle

- B3 guarded boundary.
- Evidence-sufficiency/stopping policy.
- LangGraph as current runtime candidate.
- B0/free loop/fixed reference retained as baselines or infrastructure anchors.
- Pydantic AI/Graph and OpenAI Agents SDK retained as comparators.

Still not frozen:

- model/provider;
- MCP topology;
- RAG/vector DB;
- multi-agent decomposition;
- persistent memory;
- observability backend;
- UI/demo flow.

## E6 runtime scorecard

| Runtime | Weighted score | Decision |
|---|---:|---|
| LangGraph | 4.404 | Promote as current runtime candidate |
| Pydantic AI/Graph | 4.328 | Retain as typed/schema-native fallback and comparator |
| OpenAI Agents SDK | 4.188 | Retain as provider-native comparator |

## E6 LangGraph integration completion

Completed work:

- [x] preregister minimal LangGraph integration spike;
- [x] implement minimal graph around the current policy bundle;
- [x] keep B3 boundary external and deterministic;
- [x] keep evidence-sufficiency policy explicit;
- [x] emit TraceSchema-compatible events;
- [x] test deterministic replay;
- [x] test checkpoint/static interrupt pause-resume before tool execution;
- [x] compare overhead against a direct harness-style baseline;
- [x] keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- [x] keep LOCKED_TEST blocked;
- [x] avoid freezing model/MCP/RAG/multi-agent/UI.

Integration result:

| Metric | Result |
|---|---:|
| LangGraph imported | true |
| Graph compiled | true |
| Graph invoked | true |
| Trace-compatible events | true |
| B3 external guard preserved | true |
| Evidence-sufficiency policy explicit | true |
| Deterministic replay equal | true |
| Checkpoint pause/resume roundtrip | true |
| Direct harness avg ms | 0.0076 |
| LangGraph avg ms | 9.2244 |
| Micro-benchmark overhead ratio | 1213.737 |

Interpretation: the minimal integration confirms LangGraph as the current runtime candidate, but the overhead result must be remeasured end-to-end because the direct baseline is near-zero Python dispatch.

Artifacts:

- `research/51-e6-langgraph-integration-spike-preregistration.md`
- `research/52-e6-langgraph-integration-spike-results.md`
- `research/experiments/e6-langgraph-integration-spike-manifest.json`
- `research/results/e6-langgraph-integration-summary-2026-08-16.json`
- `scripts/research/e6_langgraph_integration_spike.py`

## Next active task

Move from toy/minimal integration to real ToolSpec/HarnessRunner graph integration.

Required work:

- [ ] wire LangGraph nodes to the existing ToolSpec registry;
- [ ] call the existing HarnessRunner instead of spike-local toy execution;
- [ ] preserve B3 and evidence-sufficiency as deterministic graph/policy nodes;
- [ ] emit full RunTrace-compatible events;
- [ ] test checkpoint/replay/pause-resume over representative DEV/VALIDATION scenarios;
- [ ] remeasure overhead end-to-end;
- [ ] keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- [ ] keep LOCKED_TEST blocked;
- [ ] do not freeze model/MCP/UI yet.

## Methodological constraint

No item in E2, E3, E4, E5 or E6 is a demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts, splits and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment and cannot use LOCKED_TEST before final evaluation.
