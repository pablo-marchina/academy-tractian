# Post-E0/E1 Execution Backlog — E7 Native Tools vs MCP Pass

Status: **E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 NATIVE TOOLS VS MCP PASS; E7 ADR / TOPOLOGY DECISION PREP NEXT**

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
- E7 native tools vs MCP-compatible surface comparison complete with `E7_PASS`.

## Current candidate policy/runtime/surface bundle

- B3 guarded boundary.
- Evidence-sufficiency/stopping policy.
- LangGraph as current runtime candidate.
- `HttpxTransport` live API path configured and executed against the supplied TRACTIAN API.
- Native ToolSpec calls as internal default candidate.
- MCP-compatible `tools/list` + `tools/call` adapter as external interoperability candidate.
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

## E7 native tools vs MCP-compatible surface

Completed work:

- [x] preregister E7 native tools vs MCP-compatible comparison;
- [x] expose the same ToolSpec through native tool calls;
- [x] expose the same ToolSpec through MCP-compatible `tools/list` and `tools/call` envelopes;
- [x] normalize both surfaces back into `HarnessRunner`;
- [x] preserve B3 + evidence-sufficiency;
- [x] preserve adaptive evidence planning;
- [x] preserve `HttpxTransport` live API path;
- [x] run DEV + VALIDATION only;
- [x] compare trace completeness, guard fidelity, latency, portability and complexity;
- [x] keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- [x] keep LOCKED_TEST blocked;
- [x] avoid freezing model/MCP/RAG/multi-agent/UI.

E7 result:

| Metric | Native tools | MCP-compatible |
|---|---:|---:|
| Tool coverage | 18 | 18 |
| Representative scenarios | 4 | 4 |
| Splits | DEV + VALIDATION | DEV + VALIDATION |
| Request count | 18 | 18 |
| Successful request count | 18 | 18 |
| Trace complete | true | true |
| RunTrace-compatible output | true | true |
| B3 policy events | 2 | 2 |
| B3 allows actions | true | true |
| Evidence-sufficiency events | 4 | 4 |
| Action execution proxy | 2/2 | 2/2 |
| Avg latency ms | 1.9855 | 1.8158 |
| Complexity proxy | 1.0 | 2.0 |
| Portability proxy | 3.0 | 4.5 |

Comparison result:

| Check | Result |
|---|---:|
| Status | `E7_PASS` |
| Native tool coverage | 18/18 |
| MCP-compatible tool coverage | 18/18 |
| Schema equivalence | true |
| Invocation equivalence | true |
| Guard fidelity equivalent | true |
| Trace completeness equivalent | true |
| MCP/native latency ratio | 0.915 |
| Native lower complexity | true |
| MCP higher portability | true |
| LOCKED_TEST accessed | false |
| CI run | `31952679604` |
| Artifact | `e7-native-tools-vs-mcp-summary` |

Artifacts:

- `research/57-e7-native-tools-vs-mcp-preregistration.md`
- `research/58-e7-native-tools-vs-mcp-results.md`
- `research/experiments/e7-native-tools-vs-mcp-manifest.json`
- `research/results/e7-native-tools-vs-mcp-summary-2026-08-16.json`
- `scripts/research/e7_native_vs_mcp_runner.py`

## Next active task

Prepare the E7 ADR/topology decision without freezing the final architecture yet.

Required work:

- [ ] keep native tools as internal default candidate;
- [ ] keep MCP-compatible as external interoperability candidate;
- [ ] decide whether MCP is required for final delivery or only an optional adapter;
- [ ] preserve B3 + evidence-sufficiency + adaptive evidence planning;
- [ ] preserve `HttpxTransport` live API path;
- [ ] keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- [ ] keep LOCKED_TEST blocked;
- [ ] do not freeze final architecture yet.

## Methodological constraint

No item in E2, E3, E4, E5, E6 or E7 is a demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts, splits and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment and cannot use LOCKED_TEST before final evaluation.
