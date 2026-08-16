# E2 — Initial Execution Report

**Date:** 2026-08-16  
**Status:** ACTIVE

## Scope

E2 starts only after the two prerequisite freezes:

- `NORMALIZED-CONTRACT-v1` — `research/34-e0-contract-freeze-v1.md`
- ScenarioSchema/gold semantics v1 — `research/35-e1-gold-freeze-v1.md`

No runtime, model, MCP, RAG or multi-agent architecture is selected here.

## Implemented

- executable ScenarioSchema v1 models with strict extra-field rejection;
- 18-operation Canonical ToolSpec registry / 17 unique path templates / 5 actions;
- action metadata for `action_low`, `action_high`, `escalate`, justification length and accepted-event semantics;
- runner-owned `x-user-id` and seed injection;
- TraceSchema v1 with contiguous sequence and terminal-event invariants;
- deterministic request/observation replay with collision detection;
- canonical JSON/SHA-256 configuration and run-manifest hashing;
- deterministic evaluator interface plus trajectory, decision, policy, action, evidence and safety baselines.

## Local verification

The E2 harness was executed in an isolated Python 3.13 environment with Pydantic 2.13.4:

`8 passed`

The tests cover strict model contracts, runner-owned identity/seed, trace invariants, replay collision detection, order-stable run manifests and 18/5 registry invariants.

The supplied TRACTIAN API's own 39-test suite could not be independently rerun in this environment because the local environment lacks the package's `pyarrow` runtime dependency. The partner package itself records those 39 assertions as green after its scenario corrections; that statement remains source evidence rather than an independent local test result.

## Explicit non-decisions

E2 does **not** select:

- LangGraph;
- Pydantic AI/Graph as an agent runtime;
- OpenAI Agents SDK;
- MCP;
- model/provider;
- RAG/vector DB/reranking;
- multi-agent decomposition;
- persistent memory;
- adaptive routing.

Those remain E4/E5/E6/E7/E8/E9 experimental questions.
