# Academy × TRACTIAN — Industrial Agent Engineering & Evaluation

Repository central do TAPI individual **Engenharia e Avaliação de Agentes Industriais** (Inteli × TRACTIAN).

## Status

**E0 + E1 FROZEN; E2 COMPLETE; E3 UNLOCKED**

The project has the updated TAPI, kickoff evidence and the actual TRACTIAN package. Contract/gold semantics and the framework-neutral execution/evaluation harness are now validated.

The production architecture is still **not frozen**. Runtime, model, MCP, RAG, multi-agent, routing, memory and observability remain experimental decisions.

Plan: [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md)  
Research hub: [`research/README.md`](research/README.md)  
Active execution backlog: [`research/37-post-freeze-execution-backlog.md`](research/37-post-freeze-execution-backlog.md)

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

## E2 — completed framework-neutral harness

`research/e2/` contains executable:

- ScenarioSchema v1 models;
- 18-operation Canonical ToolSpec registry;
- explicit per-tool seed capability and runner-owned identity/seed binding;
- B0 HTTP transport + integrated live/replay `HarnessRunner`;
- B1 strict argument validation;
- B2 deterministic permission/resource guard;
- B3 evidence-aware action gate;
- TraceSchema v1 and volatile normalization;
- deterministic replay;
- configuration/artifact hashing;
- integrated structured evaluator suite;
- registry-vs-contract conformance tooling.

Validation: **24 tests passed** on Python 3.13.15 in GitHub Actions. See `research/39-e2-integrated-completion-report.md`.

E2 chose **no** LangGraph, Pydantic AI/Graph, OpenAI Agents SDK, MCP, RAG, multi-agent design or model provider.

## Central experiment

H1 tests whether a **guarded contract-aware tool boundary** improves argument correctness and safety without materially reducing task success.

- **B0:** minimal wrapper;
- **B1:** + strict typed validation;
- **B2:** + deterministic permission/company/resource guard;
- **B3:** + evidence-aware action/escalation;
- **B4:** confirmation as a separate safety extension unless canonical policy changes.

## Critical path

`E0 freeze → E1 freeze → E2 complete → E3 split → B0–B3 → evidence/stopping → runtime/MCP → pilot/model benchmark → conditional techniques → ADRs → FROZEN-v1`

Target `FROZEN-v1`: **2026-08-27** (internal project target).  
Final delivery/presentation: **2026-09-08**.

## Development rule

No component remains merely because it looks sophisticated. RAG, reranking, multi-agent, routing, persistent memory, prompt optimization and similar techniques require a measurable hypothesis or explicit requirement and must be removable when evidence does not support them.

**No demo-first development:** fixtures, scripted paths and test doubles validate infrastructure only; they are never evidence that the final agent works.
