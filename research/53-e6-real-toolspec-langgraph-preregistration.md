# E6 Follow-up — Adaptive Real ToolSpec LangGraph Spike Preregistration

**Date:** 2026-08-16  
**Status:** PREREGISTERED  
**Scope:** DEV + VALIDATION only  
**LOCKED_TEST:** forbidden  
**Runtime candidate:** LangGraph  
**Model/MCP/RAG/UI freeze:** no

This preregisters the next implementation-grade runtime spike after the minimal LangGraph integration test. The goal is to make the runtime path more adaptive without weakening deterministic safety boundaries.

## Hypothesis

A LangGraph graph can orchestrate adaptive evidence acquisition around the existing ToolSpec registry and HarnessRunner while preserving the B3 guard and evidence-sufficiency policy as deterministic graph/policy nodes outside model control.

## Constant project decisions

- Canonical ToolSpec registry remains the source of tool names, methods, path templates and action/read classification.
- `HarnessRunner` remains the execution boundary for tool proposals and trace generation.
- B3 remains a deterministic guard, not a prompt-only instruction.
- Evidence-sufficiency remains explicit graph state and a policy node.
- DEV and VALIDATION are the only allowed splits.
- LOCKED_TEST is forbidden.
- Pydantic AI/Graph and OpenAI Agents SDK remain comparators.
- No final model/provider, MCP topology, RAG/vector DB, multi-agent design, observability backend or UI is frozen.

## What changes versus the previous micro-spike

The previous LangGraph spike used spike-local toy execution. This follow-up must:

1. read from the existing ToolSpec registry;
2. call `HarnessRunner` for execution;
3. emit full RunTrace-compatible artifacts;
4. choose evidence tools adaptively from remaining evidence gaps rather than executing a single fixed tool path;
5. test checkpoint/replay/pause-resume on representative DEV and VALIDATION scenarios;
6. measure end-to-end graph overhead against an equivalent direct HarnessRunner pipeline.

## Adaptivity constraint

Adaptivity is allowed only in the acquisition/planning layer. Safety and benchmark-integrity controls remain deterministic:

- identity and seed remain runner-bound;
- B1/B2/B3 checks remain deterministic;
- LOCKED_TEST access remains impossible;
- final evidence sufficiency is measured against explicit required evidence groups;
- no scenario gold or evaluator-only expected text enters the graph state.

## Metrics

Primary integration metrics:

- ToolSpec registry wired;
- HarnessRunner used;
- B3 external deterministic guard preserved;
- evidence-sufficiency policy explicit;
- RunTrace-compatible event output;
- deterministic replay equality;
- checkpoint pause/resume roundtrip;
- DEV + VALIDATION only;
- LOCKED_TEST not accessed.

Adaptive behavior metrics:

- representative scenarios executed;
- distinct adaptive evidence paths;
- required evidence coverage;
- action/execution correctness proxy;
- unnecessary calls proxy;
- graph overhead versus direct HarnessRunner pipeline.

## Exit criteria

- CI executes the adaptive LangGraph ToolSpec runner.
- The runner proves it used the ToolSpec registry and HarnessRunner.
- B3 and evidence-sufficiency remain outside model control.
- RunTrace-compatible traces are emitted for representative DEV/VALIDATION scenarios.
- LOCKED_TEST is not accessed.
- The result is recorded as integration evidence only, not final architecture freeze.
