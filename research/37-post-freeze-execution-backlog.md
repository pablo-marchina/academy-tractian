# Post-E0/E1 Execution Backlog — E6 Live API Pass

Status: **E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 NATIVE TOOLS VS MCP NEXT**

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
- E6 live API integration path and CI contract gate complete.
- E6 local live API execution complete with `LIVE_PASS`.

## Current candidate policy/runtime bundle

- B3 guarded boundary.
- Evidence-sufficiency/stopping policy.
- LangGraph as current runtime candidate.
- `HttpxTransport` live API path configured and executed against the supplied TRACTIAN API.
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

## E6 live API integration contract gate

Completed work:

- [x] replace deterministic stub transport path with a live `HttpxTransport` path;
- [x] configure `HarnessRunner` to execute tool proposals against the live supplied API surface;
- [x] connect model/proposal generation boundary without evaluator-only gold;
- [x] preserve adaptive evidence planning;
- [x] preserve B3 and evidence-sufficiency as deterministic policy nodes;
- [x] enforce DEV + VALIDATION only;
- [x] keep LOCKED_TEST blocked;
- [x] retain Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- [x] add CI contract gate;
- [x] avoid claiming live task-success evidence before a real API endpoint run.

Contract result:

| Metric | Result |
|---|---:|
| Status | `CONTRACT_PASS_LIVE_ENDPOINT_REQUIRED` |
| Live API transport configured | true |
| Transport class | `HttpxTransport` |
| Live API executed | false |
| Live API missing reason | no `--api-base-url` in CI/contract mode |
| ToolSpec registry size | 18 |
| HarnessRunner path configured | true |
| B3 preserved | true |
| Evidence-sufficiency explicit | true |
| Adaptive evidence planning | true |
| Model/proposal generation connected | true |
| Gold leakage blocked | true |
| LOCKED_TEST accessed | false |
| CI run | `31949759607` |
| Artifact | `e6-live-api-integration-summary` |

## E6 live API execution

Completed work:

- [x] start supplied TRACTIAN API locally;
- [x] run `e6_live_api_langgraph_runner.py` with `--transport-mode live`, `--api-base-url` and `--agent-input-cases`;
- [x] keep adaptive evidence planning from missing evidence requirements;
- [x] preserve B3 and evidence-sufficiency as deterministic graph/policy nodes;
- [x] run representative DEV + VALIDATION cases end-to-end;
- [x] measure trace compatibility and live latency;
- [x] record request/action success proxy;
- [x] update result status from `CONTRACT_PASS` to `LIVE_PASS`;
- [x] keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- [x] keep LOCKED_TEST blocked;
- [x] avoid freezing model/MCP/RAG/multi-agent/UI.

Live result:

| Metric | Result |
|---|---:|
| Status | `LIVE_PASS` |
| Live API transport configured | true |
| Transport class | `HttpxTransport` |
| Live API executed | true |
| Seed binding | runner-bound |
| ToolSpec registry size | 18 |
| HarnessRunner used | true |
| B3 external guard preserved | true |
| Evidence-sufficiency explicit | true |
| Adaptive evidence planning | true |
| Model/proposal generation connected | true |
| Proposal source class | `safe_agent_input_proposal_generator` |
| Gold leakage blocked | true |
| Checkpoint pause/resume roundtrip | true |
| Representative cases | 8 |
| Splits | DEV + VALIDATION |
| Live request count | 37 |
| Successful live request count | 37 |
| Live success rate | 1.000 |
| Action execution proxy | 4/4 |
| Action accepted proxy | 4/4 |
| RunTrace-compatible output | true |
| LOCKED_TEST accessed | false |
| Live latency avg ms | 2422.9925 |
| Live latency p95 ms | 2108.5737 |

Artifacts:

- `research/51-e6-langgraph-integration-spike-preregistration.md`
- `research/52-e6-langgraph-integration-spike-results.md`
- `research/53-e6-real-toolspec-langgraph-preregistration.md`
- `research/54-e6-real-toolspec-langgraph-results.md`
- `research/55-e6-live-api-integration-contract-results.md`
- `research/56-e6-live-api-integration-live-results.md`
- `research/experiments/e6-langgraph-integration-spike-manifest.json`
- `research/experiments/e6-real-toolspec-langgraph-manifest.json`
- `research/experiments/e6-live-api-integration-manifest.json`
- `research/results/e6-langgraph-integration-summary-2026-08-16.json`
- `research/results/e6-real-toolspec-langgraph-summary-2026-08-16.json`
- `research/results/e6-live-api-integration-contract-summary-2026-08-16.json`
- `research/results/e6-live-api-integration-live-summary-2026-08-16.json`
- `scripts/research/e6_langgraph_integration_spike.py`
- `scripts/research/e6_langgraph_toolspec_runner.py`
- `scripts/research/e6_langgraph_toolspec_runner_v3.py`
- `scripts/research/e6_live_api_langgraph_runner.py`

## Next active task

Run E7: native tools vs MCP discriminating setup on the same ToolSpec and live API path.

Required work:

- [ ] expose the same ToolSpec through native tool calls;
- [ ] expose the same ToolSpec through an MCP-compatible surface;
- [ ] keep B3 + evidence-sufficiency constant;
- [ ] keep adaptive evidence planning constant;
- [ ] preserve `HttpxTransport` live API path;
- [ ] run DEV + VALIDATION only;
- [ ] compare trace completeness, guard fidelity, latency, portability and complexity;
- [ ] keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- [ ] keep LOCKED_TEST blocked;
- [ ] do not freeze model/MCP/UI yet.

## Methodological constraint

No item in E2, E3, E4, E5 or E6 is a demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts, splits and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment and cannot use LOCKED_TEST before final evaluation.
