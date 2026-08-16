# Academy × TRACTIAN — Industrial Agent Engineering & Evaluation

Repository central do TAPI individual **Engenharia e Avaliação de Agentes Industriais** (Inteli × TRACTIAN).

## Status

**E4 NEXT — Guarded Boundary Experiment B0–B3**

The project now has the updated TAPI, kickoff evidence and the actual TRACTIAN package. Three prerequisite gates are frozen and one harness gate is complete:

- `NORMALIZED-CONTRACT-v1`;
- ScenarioSchema/gold semantics v1;
- E2 framework-neutral harness;
- `BENCHMARK-SPLIT-v1`.

The production architecture is still **not frozen**. Runtime, model, MCP, RAG, multi-agent, routing, memory and observability remain experimental decisions.

Plan: [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md)  
Research hub: [`research/README.md`](research/README.md)  
Active backlog: [`research/37-post-freeze-execution-backlog.md`](research/37-post-freeze-execution-backlog.md)

## Project goal

The updated TAPI requires both components:

1. **Industrial Agent Engineering** — contextualize, investigate, execute and escalate against the supplied industrial API.
2. **Agent Evaluation & Reliability** — quantitatively measure tool choice, arguments, trajectory, evidence, conclusion/response, safety, robustness, stability and action behavior.

The evaluation framework is part of the engineering loop, not a disconnected second product.

## Evidence-first rule

> **Best means best supported by evidence for this problem — not newest, most popular or most complex.**

Decision flow:

`requirement → research → alternatives → hypothesis → TRACTIAN experiment → evidence → ADR → decision`

## Frozen TRACTIAN facts

- 17 agent-input cases and 16 narrative evaluation scenarios;
- 10 primary asset/story groups, so random ticket splitting is unsafe;
- evaluator-only gold separated from agent-visible input;
- 18 operations across 17 path templates;
- reference trajectories are not mandatory scripts;
- actions are accepted events and do not persist mutation state in the supplied environment;
- `x-user-id` and evaluation `seed` are runner-bound;
- response modes are reproducible through deterministic seeds/overrides;
- raw OpenAPI contains a duplicate `/assets/{assetId}` mapping;
- raw action validation is permissive and backend company/resource isolation is coarse;
- knowledge API exposes the supplied corpus directly.

Frozen artifacts:

- `research/34-e0-contract-freeze-v1.md`
- `research/frozen/e0-contract-freeze.manifest.json`
- `research/frozen/API-BEHAVIOR-MAP-v1.json`
- `research/35-e1-gold-freeze-v1.md`
- `research/frozen/e1-gold-freeze.manifest.json`
- `research/40-e3-benchmark-split-freeze-v1.md`
- `research/frozen/benchmark-split-v1.json`

## E2 — framework-neutral foundation

`research/e2/` contains executable:

- ScenarioSchema v1 models;
- 18-operation Canonical ToolSpec registry;
- runner-owned identity/seed binding;
- B0 HTTP transport + live/replay `HarnessRunner`;
- B1/B2/B3 deterministic boundaries;
- TraceSchema v1;
- deterministic replay;
- configuration/artifact hashing;
- integrated evaluator suite.

E2 does **not** choose LangGraph, Pydantic AI/Graph, OpenAI Agents SDK, MCP, RAG, multi-agent or a model provider.

## E3 — frozen benchmark split

- **DEV:** `asset_G501`, `asset_C710`, `asset_S420`, `asset_M208`, `asset_M101`.
- **VALIDATION:** `asset_B204`, `asset_M102`.
- **LOCKED_TEST:** `asset_V301`, `asset_M605`, `asset_M205`.

Locked-test groups are unavailable for architecture/model/prompt/runtime selection.

## Central experiment

H1 tests whether a **guarded contract-aware tool boundary** improves argument correctness and safety without materially reducing task success.

- **B0:** minimal wrapper;
- **B1:** + strict typed validation;
- **B2:** + deterministic permission/company/resource guard;
- **B3:** + evidence-aware action/escalation;
- **B4:** confirmation as a separate safety extension unless canonical policy changes.

## Critical path

`E0 freeze → E1 freeze → E2 complete → E3 split frozen → B0–B3 → evidence/stopping → runtime/MCP → pilot/model benchmark → conditional techniques → ADRs → FROZEN-v1`

Target `FROZEN-v1`: **2026-08-27** (internal project target).  
Final delivery/presentation: **2026-09-08**.

## Development rule

No component remains merely because it looks sophisticated. RAG, reranking, multi-agent, routing, persistent memory, prompt optimization and similar techniques require a measurable hypothesis or explicit requirement and must be removable when evidence does not support them.

No demo-first development: test doubles and scripted paths validate infrastructure only; agent-quality claims require controlled experiments against the TRACTIAN environment.
