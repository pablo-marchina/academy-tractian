# Wave 3 Evidence Synthesis — Pre-Onboarding Readiness

Status: **COMPLETE FOR PRE-API RESEARCH SCOPE**

Date: 2026-08-10

## Scope

Wave 3 intentionally addressed only questions that can be resolved before TRACTIAN supplies the API contract:

- deeper comparison of runtime finalists;
- current MCP protocol/Python SDK semantics;
- framework-neutral scenario contract;
- framework-neutral trace contract;
- pre-registered discriminating experiments;
- OpenAPI ingestion/audit methodology.

It does **not** invent domain entities, endpoint behavior, permission semantics or high-impact actions that the TAPI says will come from the supplied API.

## Finding 1 — all three runtime finalists remain credible

Current official capabilities are sufficient to keep LangGraph, Pydantic AI and OpenAI Agents SDK in the runtime spike.

- LangGraph is particularly strong in explicit graph state/checkpoint/interruption semantics.
- Pydantic AI is particularly strong in typed/provider-agnostic tooling and deterministic testing, with deferred tools and external durable-execution integrations.
- OpenAI Agents SDK has stronger current HITL/serializable-run/provider/trace hooks than an early superficial comparison would suggest.

**Project consequence:** documentation alone does not justify selecting a runtime. The spike is now hard-gated and pre-registered.

## Finding 2 — side-effect boundary is more important than framework brand

All finalists can propose/execute tools, but our architecture must force a common external sequence:

```text
proposal
  ↓
schema validation
  ↓
authorization / policy
  ↓
evidence/precondition check
  ↓
approval if required
  ↓
execution
  ↓
postcondition verification
```

A framework that makes this sequence hard to intercept/test loses even if its generic agent API is convenient.

## Finding 3 — restart semantics must be tested around the mutation boundary

Pause/resume abstractions differ.

The critical experiment is not “does HITL exist?” but:

- what happens if the process pauses/restarts before execution?
- what happens if execution succeeds but the runtime crashes before persisting the result?
- can a resumed run accidentally repeat a non-idempotent operation?

This becomes SPK-09/SPK-10 and is a required runtime gate.

## Finding 4 — MCP is now an adapter hypothesis, not the default semantic core

The 2026-07-28 protocol is stateless at its modern core and Python SDK v2 is the current stable line. Older session/SSE assumptions are obsolete for new code.

For this project, the strongest pre-API topology is provisional:

```text
OpenAPI → canonical typed ToolSpec → native adapter and/or MCP v2 adapter
```

This preserves fair runtime comparison and keeps project-specific mutation/risk/permission semantics out of protocol-dependent descriptions.

MCP-first remains possible if partner requirements or the native-vs-MCP spike justify it.

## Finding 5 — ScenarioSchema must separate goal state from trajectory

A reference action sequence is not automatically the only correct solution. Current tau2/tau3 evaluation methodology supports deriving/checking target environment state independently of one reference action path unless action-level policy is itself part of the reward.

Therefore ScenarioSchema v0 separates:

- policy oracle;
- evidence oracle;
- state oracle;
- communication oracle;
- optional trajectory oracle;
- fault profile.

Controlled-pair metadata and split grouping are first-class to support act-vs-abstain, permission and evidence perturbations without leakage.

## Finding 6 — TraceSchema must be project-owned over OpenTelemetry

OpenTelemetry's GenAI/agent conventions are useful and increasingly cover agent/tool/workflow operations, but key agent conventions are still marked Development and GenAI conventions have moved to a dedicated repository.

Therefore:

```text
project trace-v0 semantics
       ↓ maps to
OpenTelemetry / current GenAI conventions
       ↓ exports to
Phoenix / Langfuse / other UI
```

The UI/backend is replaceable; experiment artifacts are not.

## Finding 7 — no hidden chain-of-thought belongs in the evaluator contract

The trace needs observable decisions, proposals, policy checks, calls, outputs, state/evidence references and evaluator results. Correctness should not depend on capturing private internal reasoning.

This also makes runtime comparison more portable because providers differ in how or whether reasoning summaries are exposed.

## Finding 8 — OpenAPI audit must precede code generation

Current OpenAPI specifications are richer than what any one Python generator can be assumed to support perfectly. Official generator projects themselves document version/feature limitations.

Therefore API intake is split into:

1. immutable contract archive/hash;
2. version-aware validation/audit;
3. endpoint/schema/security inventory;
4. semantic mutation/risk/permission review;
5. generator compatibility report;
6. only then client/tool generation.

Generated code never becomes the source of truth.

## Finding 9 — risk classification cannot be inferred from HTTP method alone

`GET/POST/...` are useful metadata, not safety policy. High-impact/mutation/idempotency classification requires API semantics and partner clarification.

The ingestion pipeline therefore emits `unknown` where evidence is absent rather than guessing.

## Machine-readable research contracts added

- `research/schemas/scenario-v0.schema.json`
- `research/schemas/trace-v0.schema.json`

These are intentionally permissive around domain-specific predicate payloads until the API arrives, but strict about the top-level experimental structure.

## Pre-onboarding Research Gate status

### Closed enough to proceed immediately after API delivery

- runtime finalist capability review;
- MCP current-protocol/SDK review;
- scenario schema v0;
- trace schema v0;
- runtime/MCP/client/backend spike protocol;
- OpenAPI ingestion/audit plan;
- state/memory conceptual boundary;
- quantitative/statistical pilot methodology;
- security/threat model baseline.

### Cannot be honestly closed before TRACTIAN input

- formal two-track handling;
- actual OpenAPI/Swagger version/content;
- entity/relationship model;
- auth + business permissions/tenancy;
- mutation/high-impact classification;
- reset/snapshot/replay/idempotency capabilities;
- stochastic-result encoding and freshness/version fields;
- actual knowledge corpus and RAG need;
- rate limits/quotas.

## Onboarding-day execution plan

As soon as the contract is received:

1. archive + SHA-256 the original;
2. run OpenAPI audit/inventory;
3. list every unresolved semantic question;
4. resolve P0 permission/mutation/reset/stochasticity questions with TRACTIAN;
5. freeze `API-MAP-v0`;
6. instantiate `ScenarioSchema v1` from real entities;
7. implement canonical typed client/ToolSpec;
8. build deterministic evaluator/reset/fault harness;
9. implement baseline zero with `TraceSchema v1`/OTel adapter;
10. run runtime/client/MCP discriminating spikes;
11. run statistical pilot and model screening;
12. write ADRs and freeze `FROZEN-v1` only after results.

## Wave 3 architecture changes

No framework was selected. Instead, Wave 3 reduced the number of implicit assumptions and strengthened the constraints any final architecture must satisfy.

The most important new constraint is:

> **The experiment contracts (ScenarioSchema, ToolSpec/policy boundary, TraceSchema and evaluators) must be more stable than the agent runtime.**

That allows us to change frameworks/models without changing what “correct”, “safe” or “reproducible” means.

## Primary sources reviewed in this wave

See `research/sources.md`. Key official sources include current LangGraph, Pydantic AI, OpenAI Agents SDK, MCP 2026-07-28/Python SDK v2, OpenTelemetry GenAI conventions, OpenAPI specifications/generators and tau2/tau3 evaluation materials.
