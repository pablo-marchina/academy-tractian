# E2 — Initial Execution Report

**Date:** 2026-08-16  
**Status:** ACTIVE

E2 starts only after the two prerequisite freezes: `NORMALIZED-CONTRACT-v1` and ScenarioSchema/gold semantics v1.

## Implemented

- executable ScenarioSchema v1 models with strict extra-field rejection;
- 18-operation Canonical ToolSpec registry / 17 unique path templates / 5 actions;
- action metadata for `action_low`, `action_high`, `escalate`, justification length and accepted-event semantics;
- runner-owned `x-user-id` and seed injection;
- TraceSchema v1 with contiguous sequence and terminal-event invariants;
- deterministic request/observation replay with collision detection;
- canonical JSON/SHA-256 configuration and run-manifest hashing;
- deterministic evaluator interface and baseline trajectory/decision/policy/action/evidence/safety evaluators;
- strict action argument validation foundation;
- deterministic permission/resource-scope guard foundation.

## Local verification

The E2 harness was executed in an isolated Python 3.13 environment with Pydantic 2.13.4: **10 tests passed**.

The supplied TRACTIAN API's own 39-test suite could not be independently rerun in the current environment because `pyarrow` is unavailable. The partner package's documented green result remains source evidence rather than an independent local test result.

## Explicit non-decisions

E2 does **not** select LangGraph, Pydantic AI/Graph, OpenAI Agents SDK, MCP, a model/provider, RAG, vector DB, multi-agent decomposition, routing, persistent memory or an observability backend.

Those remain later experimental decisions.
