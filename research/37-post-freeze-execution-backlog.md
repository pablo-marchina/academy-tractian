# Post-E0/E1 Execution Backlog — E6 Adaptive ToolSpec LangGraph Executed

Status: **E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 ADAPTIVE TOOLSPEC LANGGRAPH EXECUTED; LIVE API INTEGRATION NEXT**

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
- E6 adaptive real ToolSpec/HarnessRunner LangGraph spike complete.

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

## E6 minimal LangGraph integration completion

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

## E6 adaptive ToolSpec/HarnessRunner completion

Completed work:

- [x] preregister adaptive real ToolSpec LangGraph spike;
- [x] wire LangGraph nodes to the existing ToolSpec registry;
- [x] call the existing HarnessRunner instead of spike-local toy execution;
- [x] preserve B3 and evidence-sufficiency as deterministic graph/policy nodes;
- [x] emit RunTrace-compatible events;
- [x] test checkpoint/replay/pause-resume over representative DEV/VALIDATION scenarios;
- [x] remeasure overhead end-to-end;
- [x] keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- [x] keep LOCKED_TEST blocked;
- [x] avoid freezing model/MCP/RAG/multi-agent/UI.

Adaptive ToolSpec result:

| Metric | Result |
|---|---:|
| Adaptive mode | true |
| ToolSpec registry wired | true |
| ToolSpec registry size | 18 |
| HarnessRunner used | true |
| B3 external guard preserved | true |
| Evidence-sufficiency policy explicit | true |
| RunTrace-compatible output | true |
| Representative scenarios | 4 |
| Splits used | DEV + VALIDATION |
| Adaptive path count | 3 |
| Required evidence coverage | 1.000 |
| Action execution proxy | 2/2 |
| Deterministic replay equal | true |
| Checkpoint pause/resume roundtrip | true |
| Direct HarnessRunner avg ms | 1.3582 |
| LangGraph avg ms | 20.3439 |
| Overhead ratio | 14.979 |

Artifacts:

- `research/51-e6-langgraph-integration-spike-preregistration.md`
- `research/52-e6-langgraph-integration-spike-results.md`
- `research/53-e6-real-toolspec-langgraph-preregistration.md`
- `research/54-e6-real-toolspec-langgraph-results.md`
- `research/experiments/e6-langgraph-integration-spike-manifest.json`
- `research/experiments/e6-real-toolspec-langgraph-manifest.json`
- `research/results/e6-langgraph-integration-summary-2026-08-16.json`
- `research/results/e6-real-toolspec-langgraph-summary-2026-08-16.json`
- `scripts/research/e6_langgraph_integration_spike.py`
- `scripts/research/e6_langgraph_toolspec_runner.py`
- `scripts/research/e6_langgraph_toolspec_runner_v3.py`

## Next active task

Move from deterministic stub transport to live supplied API integration while keeping adaptive evidence planning.

Required work:

- [ ] replace deterministic stub transport with live supplied API transport;
- [ ] connect model proposal generation without leaking evaluator-only gold;
- [ ] keep adaptive evidence planning from missing evidence requirements;
- [ ] preserve B3 and evidence-sufficiency as deterministic graph/policy nodes;
- [ ] run representative DEV + VALIDATION scenarios end-to-end;
- [ ] measure task success, trace completeness and live latency;
- [ ] keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- [ ] keep LOCKED_TEST blocked;
- [ ] do not freeze model/MCP/UI yet.

## Methodological constraint

No item in E2, E3, E4, E5 or E6 is a demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts, splits and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment and cannot use LOCKED_TEST before final evaluation.
