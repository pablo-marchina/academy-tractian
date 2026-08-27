# E6 Follow-up — LangGraph Integration Spike Results

**Date:** 2026-08-16  
**Status:** EXECUTED / CI-PASSED / CURRENT-RUNTIME-CANDIDATE-CONFIRMED  
**Runtime candidate:** LangGraph  
**LOCKED_TEST:** not accessed  
**Model/MCP/RAG/UI freeze:** no

This report records the implementation-grade follow-up to the E6 runtime discriminating spike. The goal was to test whether a minimal LangGraph graph can carry the current policy bundle without weakening the project constraints.

## Constants preserved

- Canonical ToolSpec discipline was held constant.
- B3 remained an external deterministic guard.
- Evidence-sufficiency/stopping remained explicit graph state.
- Events were emitted in TraceSchema-compatible shape.
- DEV + VALIDATION remained the only allowed splits.
- `LOCKED_TEST` was not accessed.
- Pydantic AI/Graph and OpenAI Agents SDK remain comparators.
- Model/provider, MCP topology, RAG/vector DB, multi-agent design, observability backend and UI remain unfrozen.

## Minimal graph tested

```text
START
  ↓
acquire_evidence
  ↓
evidence_sufficiency_gate
  ↓
b3_guard
  ↓
execute_tool
  ↓
finalize
  ↓
END
```

The graph was implemented in `scripts/research/e6_langgraph_integration_spike.py` using LangGraph `StateGraph` with a memory checkpointer and a static interrupt before `execute_tool` for pause/resume validation.

## CI evidence

- CI run: `31948300145`
- Uploaded artifact: `e6-langgraph-integration-summary`
- Artifact id: `9263920951`
- Summary file: `research/results/e6-langgraph-integration-summary-2026-08-16.json`

The workflow installed LangGraph, compiled the graph, invoked it, tested deterministic replay, tested checkpoint pause/resume, and uploaded the summary.

## Results

| Metric | Result |
|---|---:|
| LangGraph imported | true |
| Graph compiled | true |
| Graph invoked | true |
| Trace-compatible event output | true |
| Trace event count | 6 |
| B3 external guard preserved | true |
| Evidence-sufficiency policy explicit | true |
| Deterministic replay equal | true |
| Checkpoint pause/resume roundtrip | true |
| Direct harness avg ms | 0.0076 |
| LangGraph avg ms | 9.2244 |
| Micro-benchmark overhead ratio | 1213.737 |

## Interpretation

1. LangGraph integration is viable for the current policy bundle: the graph compiled, invoked and emitted TraceSchema-compatible events.
2. B3 remained outside model control as a deterministic guard node.
3. Evidence-sufficiency/stopping remained explicit rather than prompt-only behavior.
4. Replay was deterministic in the minimal graph.
5. Static interrupt + checkpointer pause/resume worked before `execute_tool`.
6. The overhead ratio is not yet a production conclusion because the direct baseline is near-zero Python function dispatch. Absolute LangGraph latency stayed in single-digit milliseconds in this micro-spike, but overhead must be remeasured in an end-to-end run before architecture freeze.

## Decision

| Candidate | Decision |
|---|---|
| LangGraph | Confirm as current runtime candidate for implementation spike. |
| Pydantic AI/Graph | Retain as fallback/comparator. |
| OpenAI Agents SDK | Retain as provider-native comparator. |

This confirms the E6 scorecard direction but still does **not** freeze final architecture. The next step should move from micro-integration to an implementation spike over the real ToolSpec/HarnessRunner boundary.

## Next step

```text
E6 implementation spike / real ToolSpec graph
├── wire LangGraph nodes to the existing ToolSpec registry
├── call the existing HarnessRunner instead of spike-local toy execution
├── preserve B3 and evidence-sufficiency as deterministic graph/policy nodes
├── emit full RunTrace-compatible events
├── test checkpoint/replay/pause-resume over representative DEV/VALIDATION scenarios
├── remeasure overhead end-to-end
├── keep Pydantic AI/Graph and OpenAI Agents SDK as comparators
└── keep LOCKED_TEST blocked
```
