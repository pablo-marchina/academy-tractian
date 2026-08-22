# Wave 3 — Discriminating Spikes Protocol

Status: **PRE-REGISTERED BEFORE API DELIVERY**

## Purpose

Prevent architecture selection from becoming a subjective framework demo. Once the TRACTIAN API arrives, credible alternatives must solve the same minimal industrial problem under controlled conditions.

## Experimental order

```text
Swagger/API audit
  ↓
canonical HTTP client + ToolSpec
  ↓
scenario/evaluator/reset harness
  ↓
trace-v0 adapter
  ↓
runtime spike
  ↓
native-vs-MCP spike
  ↓
statistical pilot/model screening
  ↓
architecture ADRs
```

No runtime-specific implementation may redefine the canonical tool semantics.

## Spike A — Agent runtime

Candidates:

- LangGraph
- Pydantic AI (+ Graph only where needed)
- OpenAI Agents SDK

### Controlled variables

- same model/provider path where supported;
- same model parameters;
- same canonical tools and schemas;
- same deterministic policy/authorization functions;
- same API observations/fault fixtures;
- same scenario definitions;
- same stop/tool-call budgets;
- same normalized trace requirements.

### Required scenario kernel

The final IDs/entities will come from Swagger, but the semantic cases are fixed now:

| ID | Case | What it discriminates |
|---|---|---|
| SPK-01 | read-only request, complete result | minimum overhead/correctness |
| SPK-02 | partial result requiring another investigation | conditional loop/evidence handling |
| SPK-03 | conflicting observations | state/evidence handling |
| SPK-04 | authorized mutation with sufficient evidence | proposal → gate → execute |
| SPK-05 | unauthorized/high-impact mutation request | interception before side effect |
| SPK-06 | mutation requiring external approval then resume | durable HITL semantics |
| SPK-07 | tool timeout then bounded recovery | retry/recovery control |
| SPK-08 | invalid model-generated arguments | typed validation/retry |
| SPK-09 | process/runtime interruption before approved mutation | persistence/restart behavior |
| SPK-10 | interruption immediately after mutation response | duplicate-side-effect/idempotency risk |
| SPK-11 | ask-for-missing-info case | multi-turn state |
| SPK-12 | correct abstention/escalation | explicit stopping/control outcome |

### Hard gates

A runtime fails the spike if any of these are impossible or unreliable under the reference implementation:

- intercept mutation before actual HTTP side effect;
- enforce external deterministic authorization/policy;
- resume a paused workflow with correct state;
- avoid duplicate mutation in the designed restart test when idempotency strategy is available;
- deterministic offline test with fake model/tool environment;
- complete normalized trace for observable actions;
- benchmark-run isolation;
- same canonical ToolSpec semantics.

### Quantitative measurements

- task/state success;
- policy violation proposals and executions separately;
- argument/schema correctness;
- duplicate side effects;
- resume correctness;
- trace completeness;
- framework-only latency with fake model/API;
- process memory where useful;
- dependency count;
- production/test/adapter LOC as descriptive complexity indicators;
- provider-path success on shortlisted providers.

Complexity measures are descriptive; no arbitrary weighted score is allowed.

## Spike B — Native tools vs MCP adapter

Compare with one selected/provisional runtime and the same canonical operations:

- B0: native adapter;
- B1: MCP v2 adapter using current 2026-07-28 semantics.

Measure:

- schema equivalence;
- argument/result equality after normalization;
- policy/authorization equivalence;
- W3C trace continuity;
- local transport overhead;
- failure propagation;
- approval/resume behavior;
- implementation/dependency surface.

MCP-first is not automatically tested unless B1 or a partner requirement demonstrates a reason to make protocol semantics canonical.

## Spike C — Generated client vs project-owned typed adapter

After the Swagger audit, compare at least:

- C0: minimal manual/project-owned typed HTTPX client generated from our normalized contract metadata;
- C1: OpenAPI Generator Python client candidate;
- C2: `openapi-python-client` candidate when compatible with the supplied OAS version/features.

Evaluation:

- request fidelity;
- response typing/fidelity;
- auth support;
- complex schema support (`oneOf`/`anyOf`, nullable, additional properties, refs, multipart etc. as present);
- ability to insert fault/replay transport;
- ability to expose stable canonical ToolSpec;
- generated-code maintenance burden.

Generated code is not ground truth. The raw OpenAPI contract and live conformance tests are ground truth.

## Spike D — Observability backend

Feed the same normalized `trace-v0` sample to Phoenix and Langfuse if both remain viable at experiment time.

Compare:

- OTel ingestion fidelity;
- trace tree/readability;
- experiment/eval association;
- local/self-host footprint;
- exportability;
- sensitive-content controls;
- ability to inspect policy/mutation/evidence fields.

Backend choice cannot change canonical run artifacts.

## Decision methodology

### 1. Hard constraints first

Any option violating a hard safety/reproducibility requirement is rejected regardless of speed or developer convenience.

### 2. Pareto comparison second

For surviving options, compare correctness, reliability, traceability, latency/resources and implementation burden without inventing ungrounded weights.

### 3. ADR records the choice

Each major decision records:

- exact versions;
- scenario/spike results;
- failures;
- limitations;
- rejected alternatives;
- reversal trigger.

## Reproducibility requirements

Every spike run records:

- Git SHA;
- runtime/library versions;
- Python version;
- OS/container manifest;
- API contract SHA-256;
- scenario hash;
- tool/policy versions;
- model/provider path;
- fault profile;
- normalized trace artifact.

## Anti-bias rule

Do not modify a common scenario/tool/policy contract to accommodate a framework unless the change is semantically necessary for all candidates. Framework-specific workarounds must live in adapters and be counted in implementation complexity.
