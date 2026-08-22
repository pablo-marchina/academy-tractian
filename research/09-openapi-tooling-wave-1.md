# OpenAPI, Tool Contract and Integration Research — Wave 1

Status: **PROVISIONAL — final design depends on TRACTIAN Swagger/OpenAPI**

## 1. Contract-first principle

The TAPI states that the final endpoint and parameter list will be provided through the API contract. Therefore the real OpenAPI document must be treated as the authoritative integration input; public TRACTIAN material must not be used to invent resources or semantics.

The integration layer should preserve a clear separation:

`OpenAPI/API contract → HTTP client → canonical domain/tool boundary → runtime adapter(s)`

This separation lets us compare agent runtimes without changing the meaning of a tool and lets the evaluation framework validate the same canonical arguments regardless of orchestration framework.

## 2. Do not expose raw OpenAPI operations blindly

OpenAPI describes paths, operations, parameters, schemas and responses, but it does not automatically encode all agent-specific safety semantics such as:

- whether an operation is high-impact in our domain;
- which evidence must exist before the operation is allowed;
- whether a mutation needs human approval;
- scenario-specific permissions;
- whether two operations are semantically interchangeable for evaluation.

Therefore the candidate architecture uses a **project-owned ToolSpec metadata layer** over the transport/API contract.

Candidate metadata fields (only after real contract inspection):

```yaml
name: ...
operation_id: ...
mode: READ | MUTATE
risk_class: ...
required_permissions: [...]
input_schema: ...
output_schema: ...
idempotency: ...
preconditions: [...]
postconditions: [...]
trace_tags: [...]
```

Do not invent values before onboarding.

## 3. `operationId` is useful but not sufficient

OpenAPI operation objects support an `operationId`, intended as a unique identifier for an operation and commonly used by tooling/code generators. If the TRACTIAN contract provides stable unique operation IDs, they are good candidates for canonical mapping keys.

If operation IDs are absent, unstable or semantically poor for an LLM, we should preserve the raw contract identity internally while defining explicit agent-facing tool names/descriptions in project code. The mapping must be deterministic and versioned.

Source: OpenAPI Specification — https://spec.openapis.org/oas/latest.html

## 4. Generated client vs manual typed client is an empirical/code-quality decision

### Option A — generated OpenAPI client

Potential advantages:

- broad endpoint/schema coverage;
- contract-driven regeneration;
- less handwritten transport boilerplate.

Potential risks:

- generated abstractions can be cumbersome for a small API;
- nullable/union/error-response behavior may need manual adaptation;
- generator output should not become the agent-facing tool interface;
- generated code churn can complicate review.

### Option B — small manual HTTPX client with Pydantic models

Potential advantages:

- explicit semantics and tests;
- small, transparent code surface;
- easy fault injection and instrumentation.

Potential risks:

- manual drift from contract;
- more handwritten endpoint coverage;
- duplication if API is large.

### Option C — generated transport + project-owned adapter

Likely strongest candidate if the API is nontrivial: generation handles low-level contract coverage, while a small canonical adapter owns agent semantics, policies and evaluation metadata.

Decision after Swagger inspection. Compare maintenance burden, schema fidelity, testability and code volume rather than framework fashion.

Sources:
- OpenAPI Generator Python — https://openapi-generator.tech/docs/generators/python/
- OpenAPI Specification — https://spec.openapis.org/oas/latest.html

## 5. JSON Schema / Pydantic validation as an invariant candidate

Pydantic can generate JSON Schema from typed models and validate runtime values before API execution. This is useful because the same schema can support:

- agent tool declaration;
- pre-execution validation;
- deterministic argument evaluator;
- test fixture validation;
- API response normalization.

However, schema-valid arguments can still be semantically wrong (e.g. valid but wrong asset ID). Therefore argument evaluation must separate **schema validity** from **semantic correctness/authorization**.

Source: https://docs.pydantic.dev/latest/concepts/json_schema/

## 6. Canonical `ToolSpec` should be runtime-neutral

Candidate interface:

```python
ToolSpec(
    canonical_name=...,
    input_model=...,
    output_model=...,
    mode=READ_OR_MUTATE,
    risk_metadata=...,
    permission_metadata=...,
    invoke=...,
)
```

Then adapters can expose the same spec as:

- LangGraph/LangChain-compatible tool;
- Pydantic AI tool;
- OpenAI Agents SDK function tool;
- MCP tool;
- direct deterministic evaluator/test fixture.

This is a key design hypothesis for the runtime comparison spike because it isolates orchestration differences from tool-definition differences.

## 7. Tool descriptions are part of the model-facing experiment

Even when the transport contract is fixed, natural-language descriptions can affect tool selection. We should version:

- canonical tool name;
- description;
- parameter descriptions;
- examples if used;
- any runtime transformation of schemas.

These belong in the experiment configuration hash. Prompt/tool-description optimization must occur only on development/validation data.

## 8. Tool catalog exposure strategy depends on actual endpoint count

If the API has a small, clearly distinct tool set, exposing all tools may be simplest and best.

If the API is large or contains semantically overlapping operations, compare:

1. all tools exposed;
2. deterministic subset by task/resource class;
3. semantic/dynamic tool search;
4. hierarchical namespace/routing.

Primary outcomes:

- task success;
- tool recall / wrong-tool rate;
- argument correctness;
- latency/context use;
- missed necessary tool;
- hallucinated/irrelevant tool behavior.

Do not build tool search before endpoint scale demonstrates a need.

## 9. Fault injection belongs below the canonical tool interface

Candidate architecture:

`agent runtime → ToolSpec adapter → FaultController → typed API client → TRACTIAN API`

Benefits:

- every runtime receives the same controlled response/fault;
- replay can happen without rewriting the agent;
- real API stochasticity and synthetic injected fault can be tagged separately;
- tools preserve the same model-facing contract.

The controller should distinguish:

- TAPI-defined semantic outcomes: complete, partial, inconclusive, conflict, unavailable;
- transport failures, only if realistic/compatible: timeout, HTTP error, malformed response;
- live untouched mode.

## 10. Mutations need explicit pre- and post-execution semantics

For every mutating operation, after Swagger/onboarding we need to document:

- required permissions;
- required arguments;
- required justification/evidence;
- whether idempotency exists;
- state fields expected to change;
- state fields that must not change;
- whether the mutation is reversible/resettable;
- how success is verified after a single accepted call.

This metadata powers both deterministic policy gates and final-state evaluation.

## 11. MCP mapping research question

The current MCP specification defines tools with named inputs/outputs but does not replace application-specific authorization/safety. Therefore MCP should be treated as an adapter/interoperability layer unless the spike shows a compelling reason to make it the canonical boundary.

Compare:

- native ToolSpec only;
- ToolSpec + MCP adapter;
- MCP-first.

Measure:

- schema fidelity;
- mapping duplication;
- pre-side-effect policy interception;
- trace propagation;
- latency;
- implementation complexity;
- runtime portability.

Source: https://modelcontextprotocol.io/specification/2026-07-28

## 12. Contract drift and reproducibility

The final benchmark must record the exact API-contract version/hash. If the partner changes Swagger during the project:

1. store new version/hash;
2. diff endpoints/schemas;
3. regenerate/adapt client if necessary;
4. rerun contract tests;
5. do not compare experiment results across materially different contracts without labeling the change.

## 13. Required tests after Swagger arrives

### Contract tests

- every selected operation maps to one canonical operation identity;
- input model accepts valid examples and rejects known-invalid inputs;
- output/error normalization covers documented responses;
- generated/manual client sends parameters in correct path/query/body/header positions;
- model-facing tool schema matches canonical validation schema.

### Safety tests

- mutating tool cannot execute after failed schema validation;
- unauthorized action is blocked before network side effect where policy requires it;
- risk metadata is present for every mutation;
- tool output cannot modify authorization metadata.

### Evaluation tests

- argument evaluator distinguishes schema-valid/wrong-value from malformed;
- recorded tool call can be replayed/parsed;
- state-changing operation exposes enough information for postcondition verification, or is explicitly marked non-verifiable.

## 14. Decision state

No final decision yet on:

- client generation;
- runtime tool adapter;
- MCP-first vs adapter;
- tool subset/search strategy;
- parallel read calls;
- mutation idempotency handling.

These become decidable immediately after the actual OpenAPI contract and onboarding answers are available.
