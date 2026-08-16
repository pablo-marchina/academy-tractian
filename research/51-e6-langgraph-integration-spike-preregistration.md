# E6 Follow-up — LangGraph Integration Spike Preregistration

**Date:** 2026-08-16  
**Status:** PREREGISTERED  
**Current runtime candidate:** LangGraph  
**Current policy bundle:** B3 guarded boundary + evidence-sufficiency/stopping policy  
**LOCKED_TEST:** forbidden

This preregisters the implementation-grade follow-up to the E6 runtime discriminating spike. The previous E6 scorecard promoted LangGraph as the current runtime candidate. This follow-up checks whether that scorecard survives a minimal executable integration around the existing project contracts.

## Objective

Implement a minimal LangGraph graph around the existing ToolSpec/Trace discipline while keeping the selected policy bundle outside the model:

- B3 remains an external deterministic guard, not prompt-only behavior;
- evidence-sufficiency/stopping remains explicit graph state;
- trace output remains compatible with the project TraceSchema event discipline;
- checkpoint/replay/pause-resume behavior is tested before any architecture freeze;
- overhead is compared against a direct harness-style execution baseline.

## Non-objectives

This spike does not choose:

- final model/provider;
- MCP topology;
- RAG/vector database;
- multi-agent decomposition;
- persistent memory design;
- observability backend;
- UI/demo flow.

It also does not use LOCKED_TEST and does not claim final agent-quality success.

## Constants held fixed

- Canonical ToolSpec v1.
- B3 guarded-boundary candidate from E4.
- Evidence-sufficiency/stopping policy from E5.
- DEV + VALIDATION only.
- Existing TraceSchema-compatible event vocabulary.
- Existing rule that identity/seed are runner-bound.

## Runtime shape to test

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

The graph is intentionally minimal. Its purpose is runtime integration evidence, not modeling or demo behavior.

## Metrics

- `langgraph_imported`;
- graph compilation success;
- graph invocation success;
- TraceSchema-compatible event count;
- B3 guard externalization preserved;
- evidence-sufficiency policy explicit;
- deterministic replay equality;
- checkpoint/pause-resume round trip;
- direct-harness baseline milliseconds;
- LangGraph milliseconds;
- overhead ratio;
- locked-test access flag.

## Promotion rule

LangGraph remains the current runtime candidate only if:

1. the graph compiles and runs;
2. replay is deterministic;
3. pause/resume works or is explicitly diagnosed;
4. B3 and evidence-sufficiency remain outside model control;
5. emitted events stay TraceSchema-compatible;
6. overhead remains acceptable for the small supplied benchmark;
7. LOCKED_TEST remains blocked.

If these fail, Pydantic AI/Graph and OpenAI Agents SDK remain active comparators rather than discarded alternatives.
