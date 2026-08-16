# E7 — Native Tools vs MCP Discriminating Setup Results

**Date:** 2026-08-16  
**Status:** E7_PASS / CI-PASSED / CONTRACT-SURFACE-COMPARISON  
**Prior gate:** E6 `LIVE_PASS`  
**Tool contract source:** `research.e2.tool_registry.TOOLS`  
**Boundary:** `HarnessRunner` + B3  
**Evidence/stopping:** evidence-sufficiency policy  
**Transport path preserved:** `HttpxTransport`  
**LOCKED_TEST:** not accessed  
**Model/MCP/RAG/UI freeze:** no

## Scope

E7 compared two exposure surfaces over the same ToolSpec and execution boundary:

1. **Native tools:** internal `{tool_name, arguments}` envelope.
2. **MCP-compatible:** JSON-RPC-style `tools/list` and `tools/call` envelopes mapped back into the same `HarnessRunner`.

The MCP-compatible test is intentionally an adapter/surface test, not a final MCP server topology freeze.

## Constants preserved

- Same canonical ToolSpec registry.
- Same `HarnessRunner` execution boundary.
- Same B3 deterministic guard.
- Same evidence-sufficiency policy.
- Same adaptive evidence planning from missing evidence requirements.
- Same DEV + VALIDATION split scope.
- Same `HttpxTransport` live API path preserved from E6.
- `LOCKED_TEST` blocked.
- Pydantic AI/Graph and OpenAI Agents SDK retained as comparators.

## CI evidence

- CI run: `31952679604`
- Artifact: `e7-native-tools-vs-mcp-summary`
- Artifact id: `9265091777`
- Artifact digest: `sha256:92d1b23e8fc7957ab5c1dc8448a6babc070ab33ae4a989967fdf0c5c7f4b645c`
- Job status: success

## Surface equivalence

| Metric | Result |
|---|---:|
| Native tool coverage | 18 |
| MCP-compatible tool coverage | 18 |
| Registry size | 18 |
| Same tool names | true |
| Schema equivalence | true |
| MCP tools/list shape valid | true |

## Execution comparison

| Metric | Native tools | MCP-compatible |
|---|---:|---:|
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

Tools exercised by both surfaces:

```text
get_analysis
get_asset
get_baseline
get_data_quality
get_spectrum
list_analyses
reprocess_analysis
request_specialist_analysis
search_knowledge
```

## Comparison summary

| Check | Result |
|---|---:|
| Schema equivalence | true |
| Invocation equivalence | true |
| Guard fidelity equivalent | true |
| Trace completeness equivalent | true |
| MCP/native latency ratio | 0.915 |
| Native lower complexity | true |
| MCP higher portability | true |
| LOCKED_TEST accessed | false |

## Decision

| Surface | Decision |
|---|---|
| Native tools | Keep as internal default candidate because it preserves fidelity with lower envelope complexity. |
| MCP-compatible | Keep as external interoperability candidate because it preserves fidelity with higher portability. |
| MCP topology | Not frozen. |
| Final architecture | Not frozen. |

## Interpretation

E7 validates that the same ToolSpec can be exposed through native and MCP-compatible surfaces without losing schema coverage, guard fidelity, trace completeness or split hygiene. Native remains the simpler internal path; MCP-compatible remains the stronger external interoperability path. The project should now move to an MCP/native ADR and, after that, to the statistical pilot/model benchmark.

## Next step

```text
E7 ADR / topology decision prep
├── keep native tools as internal default candidate
├── keep MCP-compatible as external interoperability candidate
├── decide whether MCP is required for final delivery or only an optional adapter
├── preserve B3 + evidence-sufficiency + adaptive evidence planning
├── preserve HttpxTransport live API path
├── keep Pydantic AI/Graph and OpenAI Agents SDK as comparators
├── keep LOCKED_TEST blocked
└── do not freeze final architecture yet
```
