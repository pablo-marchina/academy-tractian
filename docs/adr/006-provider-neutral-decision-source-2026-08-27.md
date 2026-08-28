# ADR-006 — P0 provider-neutral production DecisionSource adapter contract

Status: `ACCEPTED`
Date: 2026-08-27
Decision state: `FROZEN_FOR_P0_PROVIDER_ADAPTER_CONTRACT`
Issue: #26
Initial implementation validation: PR #27 head `8e30968c34eb5972111a6189766bb76b33ac0667`, `production-runtime` run `#8` / Actions run `33134915702`, `completed / success`
Root production tests: `66/66 PASS`
ADR-004 controller regression: `12/12 PASS`
Triggered workflows on validated implementation head: `11/11 success`
Scientific state changed: `NO`
Provider/model calls for this decision: `0`
Production provider/model selected: `NO`
Evaluator/private/gold access: `0`
Production action enablement changed: `NO`

## Context

ADR-004 froze a provider-free `AgentController` for the P0 controller/runtime scope and made `DecisionSource.decide(ControllerContext) -> ControllerDecision` the only model-facing decision seam. `HarnessRunner.execute_tool()` remains the exclusive real tool-execution boundary. ADR-005 subsequently froze the production consequential-action safety policy while keeping all production actions disabled.

The production runtime already accepts any object satisfying `DecisionSource`; therefore the next missing runtime component is not a new agent loop. It is a narrow adapter that can eventually connect a real model/provider to the existing controller without allowing provider-specific code to own orchestration, dispatch tools, inject runtime identity/authorization state, fork canonical ToolSpec validation, or access evaluator-private state.

Issue #26 asks: **what provider-facing adapter contract should be frozen before any real production provider/model comparison is authorized?**

This decision is deliberately provider-free. It establishes the contract and deterministic failure behavior only. It does not select a provider/model and authorizes zero live provider calls.

## Requirements affected

- P0 — complete the production Agent runtime path required by `REQ-017` while preserving the accepted deterministic evaluator and execution boundary.
- P0/P1 — strict structured decisions, deterministic tool-contract projection, fail-closed provider failure, portability and trace integrity.
- Architecture — preserve ADR-004 application-owned loop/tool-dispatch ownership.
- Safety — preserve ADR-005 runtime-owned action authorization and keep identity, seed, permissions, scope, confirmation and idempotency outside model control.
- Governance — keep historical C4 provider qualification distinct from production provider/model selection.

## Hard constraints

1. `AgentController` remains the owner of the bounded decision/tool loop.
2. `HarnessRunner.execute_tool()` remains the exclusive real tool-execution boundary.
3. The production runtime and controller require no provider-specific changes to use the adapter.
4. Provider-visible state derives only from `ControllerContext` plus a deterministic public projection of canonical ToolSpecs.
5. Runtime identity, `x-user-id`, runner seed, config hash, action permissions/scope/confirmation/idempotency and evaluator-private/gold state are not provider-visible.
6. Exactly one provider-client invocation produces at most one provider decision for each `DecisionSource.decide()` call; retries/fallbacks are not hidden in this adapter.
7. Provider output must be strict JSON and validate into the existing typed `ControllerDecision` / `ToolProposal` contract before the controller can act.
8. Unknown tools, non-object JSON, malformed JSON, duplicate JSON object keys, extra fields and invalid decision shapes fail closed.
9. Model-controlled `user_id`, `x-user-id` and `seed` remain rejected by the existing `ToolProposal` binding guard.
10. Known-tool canonical argument semantics remain B1-owned; the adapter must not create a second ToolSpec validator.
11. B2/ADR-005 remains the owner of consequential action authorization; accepting this ADR cannot enable an action.
12. The adapter contract imports no provider or orchestration SDK.
13. Real provider/model calls remain unauthorized until a separate preregistered comparison and model-call provenance protocol are accepted.

## Decision criteria

| Criterion | Required interpretation |
|---|---|
| Ownership preservation | Provider code cannot own the agent loop or direct tool transport. |
| Provider isolation | Core controller/runtime contract contains no provider SDK dependency. |
| Context minimization | Provider request contains only public controller context and public tool metadata. |
| Structured-output integrity | Every provider response is strict and typed before reaching controller behavior. |
| Fail-closed behavior | Provider/parser/shape failures become the existing `DECISION_SOURCE_FAILURE` safe abstention with zero tool transport. |
| Tool fidelity | Known tool names use the canonical registry; unknown names fail before execution. |
| B1 fidelity | Canonical argument validation stays in the existing HarnessRunner B1 boundary. |
| B2 fidelity | Production action authorization stays in ADR-005 and remains disabled. |
| Determinism | Equivalent context + registry produce the same ordered tool projection and request SHA-256. |
| Portability | Replacing a future provider changes only the client implementation, not the controller contract. |
| Traceability | Future live-provider work can add explicit model-call provenance without changing decision semantics. |
| Reversibility | A later ownership decision can supersede the adapter without rewriting historical evidence. |

## Alternatives considered

### A — Continue with scripted/raw DecisionSource only

Use deterministic hand-written `DecisionSource` implementations and add no provider-facing contract.

**Advantages**

- Simplest null baseline.
- Zero provider coupling.
- Excellent deterministic testability.

**Risks / costs**

- No stable provider request schema.
- No public ToolSpec projection contract.
- No common strict parser or provider failure boundary.
- Future provider integrations could diverge independently.

**Decision:** retained as the provider-free/null baseline, but `REJECTED_AS_COMPLETE_PRODUCTION_ADAPTER`.

### B — Provider-neutral client protocol + strict JSON adapter

Introduce a small replaceable `ProviderDecisionClient.complete(request) -> str` boundary. `ProviderDecisionSource` builds an immutable deterministic provider request, calls the client once, parses exactly one strict JSON object and converts it into the existing ADR-004 decision models.

Provider-visible request fields are limited to:

- user request text;
- bounded turn index;
- bounded tool-call count;
- normalized prior controller observations;
- deterministic public tool definitions;
- request/adapter schema versions;
- canonical request SHA-256.

The public ToolSpec projection exposes operation identity, HTTP method/path, read/action kind, public parameters and public justification requirements. It excludes required permissions, identity binding, seed controls, action authorization state and evaluator truth.

**Advantages**

- Preserves ADR-004 ownership exactly.
- Keeps provider-specific transport/auth/model details out of controller/runtime code.
- Gives all future provider clients one deterministic contract.
- Strict parsing and typed conversion fail closed before controller behavior.
- Does not duplicate B1 or B2.
- No provider SDK required.

**Risks / costs**

- A future real provider client still needs an explicit prompt/schema transport implementation.
- Real model-call retries, telemetry, cost/latency and fallback semantics are intentionally unresolved.
- JSON normalization may require provider-specific adaptation outside this core contract.

**Decision:** `SELECTED`.

### C — Provider SDK directly implements DecisionSource

A provider-specific adapter could implement ADR-004 `DecisionSource` directly and encode its own request/tool/structured-output behavior.

**Advantages**

- Potentially less adapter code for a single provider.
- Can exploit provider-specific structured output features directly.

**Risks / costs**

- Couples request semantics, retry/error behavior and tool representation to one provider SDK.
- Expands the surface that must be re-proven when switching providers.
- Increases risk that SDK convenience features silently own loop/tool behavior.

**Decision:** `REJECTED_AS_DEFAULT_CONTRACT`; a provider SDK may later exist behind `ProviderDecisionClient`, not in the frozen controller adapter.

### D — Framework/provider-managed loop and tool dispatch

Move the agent loop/tool calling to a framework/provider runtime.

**Advantages**

- May provide built-in retries, memory, tool calling and durable state.

**Risks / costs**

- Conflicts with ADR-004 application-owned orchestration and the exclusive `HarnessRunner` execution boundary.
- Can bypass B1/B2 or force duplicated execution semantics.
- Material ownership reversal would require new comparative evidence, not an incremental adapter.

**Decision:** `REJECTED_FOR_CURRENT_P0_SCOPE`.

## Systematic evidence and comparison protocol

The provider-free comparison is recorded in `research/provider-decision-source-matrix-2026-08-27.md`. It compares the null/scripted baseline, provider-neutral strict adapter, direct provider-SDK coupling and framework-managed loop/dispatch against the frozen ownership/safety constraints.

Primary repository sources are the executable ADR-004 controller contract, canonical ToolSpec registry, production runtime, ADR-005 action-safety policy and the new provider-neutral tests. Earlier ADR-004 framework research remains relevant only as evidence that richer orchestration paths exist; this ADR does not re-rank frameworks or providers.

A future live provider/model comparison is separately preregistered in the matrix and must include at minimum:

1. provider-free scripted/null baseline;
2. one strong quality-frontier provider/model candidate;
3. one feasible lower-cost/local/open candidate;
4. additional candidates only for a distinct credible Pareto trade-off.

Before a live call, exact model/route identifiers, allowed development inputs, structured-decision adherence, tool/argument validity, task-quality metrics, failure behavior, latency, reliability, resource/cost, portability, trace-integrity and retry/fallback policy must be frozen prospectively.

Historical C4 serving-route qualification is not a production-provider selection and may not bypass this comparison.

## Validation experiment

The selected adapter was implemented before ADR acceptance and validated entirely provider-free.

Initial implementation head:

`8e30968c34eb5972111a6189766bb76b33ac0667`

Primary validation:

```text
workflow                  production-runtime
run                       33134915702 / #8
root production tests     66 / 66 PASS
ADR-004 controller tests  12 / 12 PASS
job conclusion            success
triggered workflows       11 / 11 success
provider/model calls      0
production action change  0
```

The controlled tests prove:

- all five decision kinds (`TOOL`, `FINAL`, `CLARIFY`, `ESCALATE`, `ABSTAIN`) map into existing controller types;
- exactly one client call per `decide()` turn;
- deterministic 18-tool ordering and canonical provider-request hash;
- runtime-private identity, seed, config, action-authorization and evaluator-private fields are absent from the provider request structure;
- malformed/non-object/extra/unknown/invalid provider decisions fail through `DECISION_SOURCE_FAILURE` and execute zero tools;
- provider-client exceptions fail closed without leaking exception secrets into the final trace;
- model-controlled identity/seed fields fail before tool execution;
- a known tool with invalid canonical arguments reaches B1, is contained as `ARGUMENT_INVALID`, and becomes a normalized next-turn blocked observation rather than being revalidated in the adapter;
- a valid read proposal reaches transport only through the existing runner boundary, where runner-owned identity/seed are injected;
- provider/orchestration/private-evaluator SDK/module isolation is enforced by regression tests;
- ADR-004 controller behavior remains green.

The initial validation emitted one non-failing Pydantic warning because the public parameter model used a field named `schema`. Before final-head validation, the field was renamed to the unambiguous `parameter_schema`; strict JSON parsing was also hardened to reject duplicate object keys, with regression coverage. These changes do not alter the ownership decision and are included in the final ADR head to force exact-head production revalidation.

## Failure evidence

The validation intentionally exercises negative paths rather than inferring safety from successful examples:

- invalid JSON;
- non-object JSON;
- duplicate JSON keys;
- extra provider fields;
- unknown tool name;
- invalid terminal/tool shape;
- provider/client exception with secret text;
- attempted model control of `user_id`, `x-user-id` and `seed`;
- known-tool missing canonical required argument, proving B1 remains authoritative.

Every provider/adapter failure above is required to stop before real tool transport. The known-tool argument defect is deliberately *not* treated as a provider-adapter failure; it remains an auditable B1 policy block.

## Decision

Freeze the **provider-neutral strict `ProviderDecisionSource` adapter contract for the P0 production provider-integration scope**.

The accepted boundary is:

```text
ControllerContext
  + deterministic public canonical ToolSpec projection
  -> ProviderDecisionRequest + canonical SHA-256
  -> ProviderDecisionClient.complete(request)   [one call, provider-specific implementation later]
  -> strict JSON object / duplicate-key rejection
  -> ProviderDecisionPayload
  -> existing ControllerDecision / ToolProposal
  -> AgentController
  -> HarnessRunner.execute_tool()
  -> B1 canonical argument validation
  -> B2 ADR-005 action-safety policy
  -> transport only when existing guards allow
```

Provider-specific SDKs, credentials, model identifiers, retry/fallback behavior and live-call telemetry belong behind or around the future client implementation and require separate governed work. They do not belong in the frozen controller adapter.

## Explicit non-authorization

ADR-006 does **not**:

- select, rank or prefer a production model/provider;
- authorize any real model/provider/API call;
- claim historical C4 provider routes are selected for production;
- define or authorize prompt-quality/semantic evaluation;
- authorize survivor/PREFERRED inference, FRESH_BLIND or LEGACY_LOCKED_TEST access;
- expose evaluator-private/gold/oracle state to the model;
- enable any production consequential action;
- change ADR-005 permission/scope/confirmation/idempotency requirements;
- modify any frozen C4 artifact or score;
- define provider retries, fallbacks or automatic model switching;
- claim a real provider call is yet fully represented in production model-call telemetry;
- freeze the global architecture or claim production readiness.

The scientific gate remains independently `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`.

## Consequences and trade-offs

- **Positive:** future providers share one stable controller-facing contract.
- **Positive:** provider SDK churn cannot silently redefine orchestration or tool execution ownership.
- **Positive:** context minimization keeps identity/action/evaluator state outside model-visible input.
- **Positive:** strict output parsing and existing controller safe-abstention provide deterministic failure containment.
- **Positive:** B1 and B2 remain single sources of truth instead of being duplicated in provider code.
- **Positive:** provider request hashing makes equivalent input packages reproducibly identifiable.
- **Negative:** the adapter deliberately forgoes provider-specific agent-loop conveniences.
- **Negative:** a real client, model-call trace/provenance contract and provider comparison still need implementation/evidence.
- **Negative:** provider-side structured-output capabilities may require translation to/from the frozen neutral schema.
- **Operational:** retry/fallback logic cannot be added implicitly inside a client; it must be separately specified and traceable.

## Reversal / amendment triggers

Reopen or supersede ADR-006 if:

1. a future provider cannot reliably represent the neutral request/decision contract without material loss;
2. measured provider integration shows the one-call-per-decision boundary is inadequate and a retry/fallback policy is justified;
3. ADR-004 is deliberately superseded and loop/tool-dispatch ownership moves to another runtime;
4. the canonical ToolSpec contract changes materially enough that the public projection no longer represents provider needs;
5. production evidence requires additional provider-visible context that cannot safely fit `ControllerContext`;
6. model-call telemetry/provenance requirements require a materially different client boundary;
7. a durable orchestration requirement triggers the ADR-004 LangGraph upgrade path or another evidence-backed architecture;
8. security evidence shows the strict JSON/typed boundary is insufficient.

Provider/model selection by itself should not supersede this ADR if the selected provider can live behind `ProviderDecisionClient` while preserving the frozen contract.

## Regression obligations

Any implementation derived from ADR-006 must continue to prove:

- `ProductionRuntime` can consume the adapter without provider-specific controller/runtime changes;
- provider-visible request structure excludes runtime identity/seed/config/action-authorization and private evaluator state;
- all 18 canonical tools project deterministically;
- equivalent canonical provider requests have stable hashes;
- exactly one client invocation occurs per decision turn unless a future ADR explicitly changes retry semantics;
- malformed JSON, duplicate keys, non-object JSON, extra fields, invalid shapes and unknown tools fail closed;
- model-controlled identity/seed arguments fail before execution;
- known-tool canonical argument defects remain B1-owned and traceable as `ARGUMENT_INVALID`;
- action authorization remains B2/ADR-005-owned;
- valid real tool execution remains exclusively through `HarnessRunner.execute_tool()`;
- provider/client exception details do not leak into the final response/trace;
- provider/orchestration SDK imports remain outside the neutral adapter contract;
- no real provider comparison occurs before model-call trace/provenance and comparison criteria are prospectively frozen;
- provider calls remain zero until separately authorized;
- the scientific gate and frozen experiment artifacts cannot change as a side effect of this adapter.

## Sources

Repository evidence:

- issue #26
- PR #27
- ADR-004
- ADR-005
- `research/e2/controller.py`
- `research/e2/tool_registry.py`
- `src/academy_tractian/runtime.py`
- `src/academy_tractian/action_safety.py`
- `src/academy_tractian/decision_source.py`
- `tests/test_decision_source.py`
- `research/provider-decision-source-matrix-2026-08-27.md`
- `production-runtime` Actions run #8 / `33134915702`

No external provider capability is accepted by this ADR. The material decision is the repository-local integration boundary; live provider facts must be refreshed from official primary sources in the separately governed provider/model comparison immediately before any such comparison is authorized.
