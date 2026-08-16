# E6 Follow-up — Adaptive Real ToolSpec LangGraph Results

**Date:** 2026-08-16  
**Status:** EXECUTED / CI-PASSED / ADAPTIVE-TOOLSPEC-RUNNER-RECORDED  
**Runtime candidate:** LangGraph  
**Execution boundary:** HarnessRunner  
**LOCKED_TEST:** not accessed  
**Model/MCP/RAG/UI freeze:** no

This report records the adaptive implementation spike requested after the minimal LangGraph integration. The goal was to reduce fixed deterministic acquisition paths while preserving deterministic safety and benchmark-integrity controls.

## Constants preserved

- Existing ToolSpec registry remained the tool contract source.
- Existing `HarnessRunner` remained the execution boundary.
- B3 remained an external deterministic guard.
- Evidence-sufficiency/stopping remained explicit graph/policy state.
- DEV + VALIDATION remained the only allowed splits.
- `LOCKED_TEST` was not accessed.
- Pydantic AI/Graph and OpenAI Agents SDK remain comparators.
- Model/provider, MCP topology, RAG/vector DB, multi-agent decomposition, observability backend and UI remain unfrozen.

## Adaptive graph behavior

The runner now chooses evidence tools from unresolved evidence requirements instead of following one fixed tool path.

```text
START
  ↓
wire_tool_registry
  ↓
adaptive_evidence_planner
  ↓
evidence_sufficiency_gate
  ↓
b3_boundary_marker
  ↓
execute_with_harness
  ↓
finalize_graph
  ↓
END
```

Adaptivity is scoped to evidence acquisition order and tool selection. Safety remains deterministic.

## CI evidence

- CI run: `31949049937`
- Uploaded artifact: `e6-real-toolspec-langgraph-summary`
- Artifact id: `9264115250`
- Summary file: `research/results/e6-real-toolspec-langgraph-summary-2026-08-16.json`

The workflow installed LangGraph, ran the E2/E4/E5/E6 checks, executed the adaptive ToolSpec LangGraph runner, and uploaded the summary artifact.

## Results

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
| B3 policy events | 2 |
| Deterministic replay equal | true |
| Checkpoint pause/resume roundtrip | true |
| Direct HarnessRunner avg ms | 1.3582 |
| LangGraph avg ms | 20.3439 |
| Overhead ratio | 14.979 |

Tools used through the registry:

```text
get_asset
list_analyses
get_analysis
get_data_quality
get_baseline
get_spectrum
search_knowledge
reprocess_analysis
request_specialist_analysis
```

## Interpretation

1. The integration is now more adaptive than the previous micro-spike because tool choice is derived from missing evidence requirements, not from one hardcoded path.
2. The existing ToolSpec registry and HarnessRunner are now in the runtime loop.
3. RunTrace-compatible output was emitted from representative DEV and VALIDATION scenarios.
4. B3 and evidence-sufficiency stayed deterministic and outside model control.
5. Deterministic replay and checkpoint pause/resume passed.
6. End-to-end overhead is now more realistic than the previous near-zero direct baseline, but still needs to be measured with real model calls and live API latency before architecture freeze.

## Decision

| Candidate | Decision |
|---|---|
| LangGraph | Advance to real DEV/VALIDATION integration implementation. |
| Pydantic AI/Graph | Retain as fallback/comparator. |
| OpenAI Agents SDK | Retain as provider-native comparator. |

This is still not final architecture freeze. It upgrades the LangGraph path from scorecard + toy micro-spike to an adaptive ToolSpec/HarnessRunner integration candidate.

## Next step

```text
E6 real integration continuation
├── replace deterministic stub transport with live supplied API transport
├── connect model proposal generation without leaking evaluator-only gold
├── keep adaptive evidence planning
├── keep B3 and evidence-sufficiency deterministic
├── run representative DEV + VALIDATION scenarios end-to-end
├── measure task success, trace completeness and live latency
├── keep Pydantic AI/Graph and OpenAI Agents SDK as comparators
└── keep LOCKED_TEST blocked
```
