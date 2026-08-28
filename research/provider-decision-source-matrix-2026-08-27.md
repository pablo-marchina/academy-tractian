# Production DecisionSource adapter — provider-free comparison protocol — 2026-08-27

Status: `VALIDATED / FROZEN_BY_ADR_006 / PROVIDER_FREE_ONLY`
Issue: #26
Initial validation head: `8e30968c34eb5972111a6189766bb76b33ac0667`
Initial validation: `production-runtime` run `#8` / Actions run `33134915702` — `66/66` root production tests + `12/12` ADR-004 controller regressions PASS; `11/11` triggered workflows success
Scientific state changed: `NO`
Provider/model calls authorized by this work: `0`
Production provider/model selected: `NO`

## Decision question

What is the smallest production adapter boundary that can connect a future model/provider to the accepted ADR-004 `DecisionSource` contract while preserving application-owned orchestration, canonical ToolSpec/B1 validation, `HarnessRunner` execution ownership, runtime-private state isolation and provider portability?

This document compares **adapter architectures only**. It does not compare or rank live providers/models and does not authorize a provider call.

## Hard constraints

- `AgentController` remains the owner of the bounded decision/tool loop.
- `HarnessRunner.execute_tool()` remains the exclusive real tool-execution boundary.
- Provider-visible state is derived only from `ControllerContext` plus a public projection of the canonical ToolSpec registry.
- User identity, runner seed, config hash, production action permissions/scope/confirmation/idempotency and evaluator-private/gold state are not provider-visible.
- Exactly one provider-client invocation may produce one provider decision per `DecisionSource.decide()` call.
- Provider output must become an existing typed `ControllerDecision` before the controller can act on it.
- Unknown tools, malformed/non-object JSON, duplicate object keys, extra fields and invalid decision shapes fail closed.
- Model-controlled `user_id`, `x-user-id` or `seed` remains rejected by the existing `ToolProposal` binding guard.
- Canonical known-tool argument semantics remain owned by B1; the adapter must not fork ToolSpec validation.
- No automatic provider retry/fallback is part of this contract.
- No provider SDK is required by the adapter contract.

## Alternatives

| Alternative | Loop/tool ownership | Portability | Structured-output safety | Boundary duplication | Current fit |
|---|---|---:|---:|---:|---|
| A. Existing scripted/raw `DecisionSource` only | application | very high | caller-dependent | none | useful null baseline, not a provider integration contract |
| B. Provider-neutral client protocol + strict JSON adapter | application | high | high; strict Pydantic shape before `ControllerDecision` | low | **selected and frozen by ADR-006** |
| C. Provider SDK directly implements `DecisionSource` | application nominally | low-medium | provider-specific | medium | rejected as default; couples core contract to provider semantics |
| D. Framework/provider-managed agent loop and tool dispatch | framework/provider | medium | framework-dependent | high / ownership conflict | rejected under ADR-004 because it can bypass application-owned execution |

### A — scripted/raw DecisionSource

This is the simplest null baseline and remains valuable for deterministic tests. It proves ADR-004 can operate without any provider dependency, but it does not define a stable provider request contract, public tool projection, parsing policy or future provider portability boundary.

### B — provider-neutral strict adapter

`ProviderDecisionSource` builds a deterministic request from `ControllerContext` and a public canonical ToolSpec projection. A replaceable `ProviderDecisionClient` receives that immutable request and returns exactly one JSON string. The adapter strictly parses that JSON into one of `TOOL`, `FINAL`, `CLARIFY`, `ESCALATE`, `ABSTAIN`, then maps it to the existing ADR-004 models.

Selected properties:

- provider-specific transport/auth/model parameters remain outside the controller contract;
- provider-visible tools are sorted deterministically and do not expose authorization/runtime binding state;
- request content has a deterministic SHA-256;
- strict extra-field and duplicate-key rejection prevents ambiguous/provider-drift payloads from silently entering controller state;
- unknown tool names are rejected before `HarnessRunner`;
- known-tool arguments are deliberately *not* semantically revalidated here, so B1 remains authoritative;
- provider/client exceptions naturally hit the existing controller `DECISION_SOURCE_FAILURE` fail-closed path;
- no retry or fallback semantics are hidden in the adapter.

### C — direct provider SDK DecisionSource

A provider-specific class could implement `DecisionSource` directly. This is technically feasible but rejected as the default contract because request structure, structured-output behavior, tool representation, retries and provider error semantics would leak into the production orchestration boundary. Replacing providers would then require re-proving more than the transport/client layer.

### D — provider/framework-managed loop

Framework-managed agent loops can provide convenient tool calling, retries and state, but the current project explicitly owns the loop and execution boundary through ADR-004. Moving tool dispatch into a provider/framework would require a deliberate ownership reversal and new evidence; it is not an incremental provider adapter.

## Selected contract

The provider-neutral boundary frozen by ADR-006 is:

```text
ControllerContext
   + public canonical ToolSpec projection
   -> deterministic ProviderDecisionRequest
   -> replaceable ProviderDecisionClient.complete(request)
   -> one strict JSON object
   -> ProviderDecisionPayload
   -> existing ControllerDecision / ToolProposal
   -> AgentController
   -> HarnessRunner / B1 / B2 / transport
```

Provider-visible request fields are limited to:

- user request text;
- bounded turn index;
- bounded tool-call count;
- prior normalized controller observations;
- deterministic public tool definitions;
- adapter/request schema versions;
- canonical request SHA-256.

The public tool projection includes operation identity, method/path, read/action kind, public parameters and public justification requirements. It intentionally excludes required permissions, identity binding, seed controls, production authorization state and evaluator truth.

## Failure ownership

| Failure | Owner | Expected behavior |
|---|---|---|
| client/network/provider exception | DecisionSource/controller | controller safe-abstains with `DECISION_SOURCE_FAILURE`; no tool executes |
| invalid/non-object/duplicate-key JSON | adapter | reject → `DECISION_SOURCE_FAILURE` |
| extra provider fields / invalid terminal shape | adapter | reject → `DECISION_SOURCE_FAILURE` |
| unknown tool name | adapter | reject → `DECISION_SOURCE_FAILURE` |
| model-supplied identity/seed control | existing `ToolProposal` guard | reject → `DECISION_SOURCE_FAILURE` |
| known tool with missing/invalid canonical args | B1 `HarnessRunner` | contained `ARGUMENT_INVALID`, visible as next-turn blocked observation |
| consequential action authorization | B2 ADR-005 policy | fail closed; actions remain disabled |
| tool transport failure | existing controller/tool boundary | `TOOL_BOUNDARY_FAILURE` safe abstention |

## Provider-free validation evidence

Initial implementation validation on PR #27 head `8e30968c34eb5972111a6189766bb76b33ac0667`:

```text
production-runtime run     33134915702 / #8
root production tests      66 / 66 PASS
ADR-004 controller tests   12 / 12 PASS
triggered workflows        11 / 11 success
provider/model calls       0
production action changes  0
```

The tests prove:

- all five decision kinds parse into the existing controller models;
- one client invocation per decision turn;
- deterministic 18-tool projection and request hash;
- no runtime-private/evaluator-private state in the request;
- strict rejection of malformed/extra/unknown decisions;
- identity/seed injection rejection;
- B1 ownership of canonical argument failures;
- valid read-tool execution still receives runner-owned identity/seed only at the execution boundary;
- provider/client exception text does not leak into final trace/output;
- provider/orchestration SDK import isolation;
- current production action-safety and ADR-004 regressions remain green.

The implementation validation surfaced one non-failing Pydantic warning caused by naming the public parameter field `schema`. The final ADR head renames it to `parameter_schema` and adds explicit duplicate-JSON-key rejection/coverage before exact-head revalidation. This is hardening of the accepted neutral contract, not provider/model evidence.

## Later provider/model comparison protocol — not authorized or executed here

A separate task must update provider/model facts from current official sources immediately before comparison and preregister the candidates and evidence. The minimum comparison set is:

1. provider-free scripted/null baseline for contract and lower-bound behavior;
2. one strong quality-frontier provider/model candidate;
3. one feasible lower-cost/local/open candidate;
4. additional candidates only for a distinct credible Pareto trade-off.

Before any live request, freeze:

- exact candidate/model identifiers and serving route;
- allowed development inputs and custody boundaries;
- structured-decision adherence metric;
- valid known-tool selection rate;
- canonical argument validity / B1 containment rate;
- task-quality metrics on authorized development evidence;
- terminal/failure behavior and malformed-output rate;
- latency distribution;
- request reliability/error rate;
- resource/cost accounting;
- portability/operational constraints;
- trace-integrity requirements, including explicit model-call provenance for any real provider path;
- retry/fallback policy (default: none unless prospectively justified).

Historical C4 provider qualification is evidence about those historical experiment routes only. It is not a production-provider prior that may bypass this comparison.

## Non-claims

This protocol does not claim that:

- any provider/model is preferred, qualified or authorized for production;
- provider calls are permitted now;
- prompt/task quality has been measured for this adapter;
- semantic evaluation is authorized;
- actions are enabled;
- a real provider call is yet fully represented in production `RunTrace` model-call telemetry;
- the global architecture is frozen or the product is production-ready.

The explicit model-call trace/provenance behavior for a real provider client must be frozen before the first live production-provider comparison; the provider-free adapter itself has no live call to record.
