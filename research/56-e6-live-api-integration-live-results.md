# E6 Continuation — Live API Integration Results

**Date:** 2026-08-16  
**Status:** LIVE PASS  
**Runtime candidate:** LangGraph  
**Execution boundary:** HarnessRunner  
**Transport surface:** `HttpxTransport`  
**API endpoint:** `http://localhost:8000`  
**LOCKED_TEST:** blocked  
**Model/MCP/RAG/UI freeze:** no

This report records the live execution that followed the E6 live API integration contract gate. The previous contract result proved the implementation path but did not exercise a live endpoint. This run executed the configured LangGraph + HarnessRunner + `HttpxTransport` path against the supplied TRACTIAN API running locally.

## What was executed

```text
LangGraph
  ↓
safe agent-input proposal generation
  ↓
adaptive evidence planning
  ↓
evidence-sufficiency policy node
  ↓
HarnessRunner
  ↓
HttpxTransport against supplied TRACTIAN API
  ↓
B3 deterministic action gate
  ↓
RunTrace-compatible trace
```

## Integrity constraints preserved

- Only DEV + VALIDATION representative cases were used.
- `LOCKED_TEST` was not accessed.
- `x-user-id` and seed remained runner-bound.
- Model/proposal generation used the safe `agent-input` proposal generator.
- Evaluator-only gold sources remained blocked.
- B3 remained an external deterministic guard.
- Evidence-sufficiency remained explicit and deterministic.
- Pydantic AI/Graph and OpenAI Agents SDK remain comparators.
- Model/provider, MCP topology, RAG/vector DB, multi-agent design and UI remain unfrozen.

## Live results

| Metric | Result |
|---|---:|
| Status | `LIVE_PASS` |
| Live API transport configured | true |
| Transport class | `HttpxTransport` |
| Live API executed | true |
| API base URL | `http://localhost:8000` |
| ToolSpec registry size | 18 |
| HarnessRunner used | true |
| B3 external guard preserved | true |
| Evidence-sufficiency explicit | true |
| Adaptive evidence planning | true |
| Model/proposal generation connected | true |
| Proposal gold leakage blocked | true |
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

Tools used through the live ToolSpec/HarnessRunner path:

```text
escalate_case
get_analysis
get_asset
get_baseline
get_data_quality
get_rms
get_spectrum
list_analyses
reprocess_analysis
search_knowledge
```

## Interpretation

The E6 live API execution gate passed. This is stronger evidence than the previous contract-only gate because the runner exercised the supplied API surface through `HttpxTransport` and produced RunTrace-compatible output over DEV + VALIDATION representative cases.

This still is not a final architecture freeze. It validates the LangGraph + adaptive evidence planning + B3 + HarnessRunner + live API path as the current implementation candidate. The next discriminating step is to compare native tools vs MCP on the same ToolSpec while preserving the same evidence/safety bundle and keeping `LOCKED_TEST` blocked.

## Decision

| Candidate | Decision |
|---|---|
| LangGraph + ToolSpec + HarnessRunner + `HttpxTransport` | Promote as current live integration candidate. |
| Pydantic AI/Graph | Retain as typed/schema-native fallback and comparator. |
| OpenAI Agents SDK | Retain as provider-native comparator. |

## Next step

```text
E7 native tools vs MCP discriminating setup
├── expose the same ToolSpec through native tool calls and MCP-compatible surface
├── keep B3 + evidence-sufficiency constant
├── keep adaptive evidence planning constant
├── run DEV + VALIDATION only
├── compare trace completeness, guard fidelity, latency, portability and complexity
├── preserve live API transport path
├── keep Pydantic AI/Graph and OpenAI Agents SDK as comparators
└── keep LOCKED_TEST blocked
```
