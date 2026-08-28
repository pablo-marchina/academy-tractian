# ADR-012 — Controlled consequential-action execution profile

**Status:** ACCEPTED  
**Decision state:** `FROZEN_FOR_CONTROLLED_ACTION_EXECUTION_PROFILE`  
**Date:** 2026-08-28  
**Issue:** #45  
**PR:** #46  
**Scientific state changed:** NO  
**Production provider/model selected:** NO  
**ADR-009 live provider calls consumed by this decision:** 0  
**Real customer mutations performed by this decision:** 0

## Decision question

Can the repository prove the requested consequential-action execution path end to end, with the same ADR-004 controller and `HarnessRunner.execute_tool()` boundary, while preserving ADR-005 authorization semantics and adding durable pre-transport duplicate protection — without turning the existing read-only `ProductionRuntime` into an action-enabled global runtime?

## Context

ADR-005 froze the production action-safety policy but deliberately kept the real `ProductionRuntime` action-disabled. That decision proved what must be true before an action can be authorized, but did not yet prove that a fully authorized action can traverse the integrated production path exactly once and be evaluated as accepted.

The delivery requirements include justified execution requests and safe consequential-action handling. A credible product path therefore needs evidence for both halves:

1. unauthorized or duplicate proposals are contained before transport; and
2. an explicitly authorized exact action can reach the supplied API boundary once, with inspectable trace evidence and deterministic evaluation.

The new profile must not weaken the default read-only runtime, infer authorization from model text, introduce a second tool transport path, or allow process restart to replay a possibly consumed mutation.

## Decision

Accept `src/academy_tractian/controlled_actions.py` plus `src/academy_tractian/controlled_action_evaluation.py` as a separate, explicit controlled-action execution profile.

The default `ProductionRuntime` remains unchanged and action-disabled. Controlled execution requires explicit construction of `ControlledActionRuntime` with:

- a trusted runtime-owned `ActionAuthorizationSource`;
- ADR-005-compliant authorization state bound to the exact action fingerprint;
- a durable `DurableActionAttemptClaimStore`;
- an explicitly supplied transport;
- the existing canonical ToolSpec registry and `HarnessRunner.execute_tool()` boundary.

Validated pre-freeze identity:

```text
validated implementation head             c6d0108780c40ffd9522001d6941058c4fc59c3f
controlled_actions.py blob                 9e5f2d49ebc82303423f81ec8916b02c511f2a1e
controlled_action_evaluation.py blob       ae5f1a7777893941882196c8c2f3810676eba0a4
test_controlled_actions.py blob            357cc503d0b329d025abe004a2c780f6ee5ea2fa
test_controlled_action_evaluation.py blob  4b65fd911539092bb1126cc4e6db5dc985dad76b
ADR-005 action_safety.py blob              21840f8711450dcca93f2c0b9880387702118104
HarnessRunner blob                         184544ede9fa81188f795dd6c698b5b4556a59c9
baseline ProductionEvaluator blob          27adfc0e009398bf765ac05afe1ef6e8799adea1
read-only ProductionRuntime blob           a7f8adf02dded71188ce61668b111be258206745
production-runtime run                     33149724402 / #46 / success
production tests                           168 passed
ADR-004 controller regression              12 passed
triggered workflows                        11 / 11 success
ADR-009 provider calls                     0 / 32
real customer mutations                    0
```

Machine-readable freeze:

`research/frozen/controlled-action-execution-profile-freeze-v1.json`

## Preserved ownership boundaries

ADR-012 does not replace or weaken:

- ADR-004 application-owned controller ownership;
- `HarnessRunner.execute_tool()` as the exclusive real tool execution boundary;
- B1 canonical argument validation;
- ADR-005 production action-safety semantics;
- ADR-006 provider-neutral `DecisionSource` contract;
- ADR-007 sanitized model-call provenance;
- ADR-009/010/011 provider-comparison geometry, executor or custody;
- the default read-only `ProductionRuntime` configuration;
- the scientific `REQUIRED_PER_GROUP_AND_SLICE_REPORTING` gate.

No provider/private/semantic evaluator state is required by this profile.

## Controlled execution path

The accepted action-capable path is:

```text
DecisionSource ToolProposal
→ AgentController
→ HarnessRunner.execute_tool()
→ B1 canonical argument validation
→ DurableProductionActionPolicy
   → trusted exact-fingerprint authorization lookup
   → ADR-005 ProductionActionSafetyPolicy
   → durable exclusive-create idempotency claim
→ existing HarnessRunner transport path
→ tool_result / observation
→ ControlledActionEvaluator
```

There is no direct action transport owned by `ControlledActionRuntime` or the authorization source.

## Trusted authorization boundary

`ActionAuthorizationSource` is runtime-owned control-plane state. Its contents are not passed to `ControllerContext` and are not provider-visible tool arguments.

For the accepted provider-free proof, `StaticActionAuthorizationSource` maps an exact deterministic action fingerprint to a `ProductionActionAuthorizationContext`. This proves the boundary but is not itself a production identity/permission service.

The profile inherits ADR-005's independent requirements:

- execution enabled for the controlled context;
- all declared permissions present;
- known same-company resource scope;
- canonical valid arguments and adequate justification;
- requester confirmation bound to the exact action fingerprint;
- one runtime-owned idempotency binding for that exact fingerprint;
- no previously consumed idempotency state;
- no model-controlled authorization fields.

An exact action without a provisioned trusted grant is denied as `AUTHORIZATION_NOT_PROVISIONED`.

## Durable pre-transport claim rule

ADR-005 is evaluated first. A denial consumes no durable claim and performs zero transport calls.

Only after ADR-005 returns `ALLOWED`, the profile resolves the exact runtime-owned idempotency key and performs an exclusive-create claim:

```text
ADR-005 ALLOWED
→ SHA-256(raw idempotency key)
→ exclusive-create <claim-root>/<hash>.json
→ fsync file
→ fsync directory where supported
→ B2 ALLOWED
→ HarnessRunner tool_call / transport
```

The claim artifact stores only:

- runtime/schema version;
- tool name;
- action fingerprint;
- SHA-256 of the idempotency key;
- `state = claimed`;
- `raw_idempotency_key_recorded = false`.

The raw key is not persisted.

If the claim path already exists, the action is denied as `DUPLICATE_ACTION` before transport.

If the process or transport fails after claim creation, the claim remains consumed/uncertain. Automatic replay is forbidden because the external mutation may already have been accepted even when no response was captured.

## Controlled evaluator

The existing `ProductionEvaluator` remains read-only and deliberately continues to reject traces containing executed action calls.

`ControlledActionEvaluator` composes that validated baseline rather than weakening it globally. It retains the baseline lifecycle, ToolSpec, identity/seed isolation, execution-chain, policy-containment, provider-free/model-call-provenance and terminal-consistency checks.

Only two profile-specific assumptions change:

1. the controlled namespace is `prod-action:*`; and
2. an action call is valid only when a matching B2 `ALLOWED` event precedes it and the supplied API result records `accepted=true`.

The controlled evaluator does not copy action response bodies or justification text into its report.

A trace with an action call but no matching B2 allow fails `controlled_action_execution`. A result without `accepted=true` also fails the controlled action check.

## Provider-free evidence

The accepted tests prove all five canonical action ToolSpecs can execute exactly once through the same controller/runner boundary when every trusted authorization condition is satisfied:

- `update_asset_config`;
- `reprocess_analysis`;
- `request_specialist_analysis`;
- `request_retraining`;
- `escalate_case`.

The supplied deterministic transport returns `202` with `accepted=true` for this proof. These are synthetic/test transport semantics, not real customer mutations.

The tests also prove:

- authorization/idempotency state never enters `DecisionSource` context;
- missing confirmation, permission, scope or execution enablement performs zero transport and consumes no claim;
- unknown and cross-company scope fail closed through ADR-005;
- an unprovisioned exact action performs zero transport;
- duplicate action across new runtime instances is blocked before the second transport;
- a transport failure after claim cannot be replayed by a new runtime instance;
- raw idempotency keys are absent from claim artifacts and source repr;
- default `ProductionRuntime` remains action-disabled;
- default `ProductionEvaluator` still rejects an action-executing trace;
- `ControlledActionEvaluator` accepts the same structurally valid controlled trace and rejects missing B2 allow or `accepted!=true`;
- provider/private evaluator SDK stacks are not imported.

## Preserved validation failure

The first evaluator-composition head `02a7a95765075df08cb10ccd5f89482a813f3fa0` failed the production suite:

```text
165 passed / 3 failed
```

The failures were not action-policy/runtime failures:

1. two evaluator tests used the non-canonical terminal value `EXECUTE`, which is not a member of the frozen `Decision` enum; the reprocess fixture was corrected to canonical `ACT_REPROCESS` rather than weakening `terminal_consistency`;
2. one import-isolation test rejected the word `Scenario` appearing only in a docstring; the assertion was corrected to inspect imported symbols/modules rather than arbitrary source text.

No ADR-005 rule, action runtime path, controlled evaluator safety condition or `HarnessRunner` behavior was relaxed. The corrected head passed 168 production tests, 12 ADR-004 regressions and all 11 triggered workflows.

## Capability versus authorization

ADR-012 freezes a controlled action **capability**, not blanket production mutation authorization.

It is now evidence-backed that the requested execution path can:

- contain unauthorized consequential actions;
- execute an exact explicitly authorized action once;
- prevent duplicate replay across runtime instances;
- preserve a valid integrated trace;
- evaluate accepted-action semantics deterministically.

This does not authorize arbitrary real customer mutations. A real deployment must still provision trusted production sources for identity/permissions, company/resource scope, requester confirmation and durable idempotency custody, and must explicitly select the target environment/transport.

Until such an execution task is separately authorized:

```text
default ProductionRuntime actions          DISABLED
controlled profile                         FROZEN / PROVIDER-FREE EVIDENCE
real customer mutations                    0
production provider/model selected         NO
ADR-009 calls consumed                     0 / 32
scientific provider calls                  0
```

## Rejected alternatives

### Change `ProductionRuntime.actions_enabled` to true

Rejected because it would convert a staged proof into global action enablement and weaken the existing fail-closed default.

### Add a direct action executor outside `HarnessRunner`

Rejected because it would create a second execution path and bypass the stable ToolSpec/RunTrace boundary.

### Mark idempotency consumed only after a successful response

Rejected because a process/network failure can occur after the external system has accepted a mutation. Retrying would risk duplicate consequential actions.

### Delete the claim after transport failure

Rejected for the same reason. Failure after claim remains consumed/uncertain.

### Reuse raw idempotency keys as filenames or persisted diagnostics

Rejected because runtime-owned action authorization state should not be unnecessarily exposed.

### Make the baseline `ProductionEvaluator` non-read-only

Rejected because read-only remains the safe default. A separate composed controlled evaluator makes the changed assumption explicit.

## Reversal triggers

A prospective amendment is required before any of the following:

- changing ADR-005 authorization semantics;
- deleting/releasing a claim after uncertain transport failure;
- automatic action retries;
- allowing more than one idempotency binding for one exact action fingerprint;
- introducing model/provider-controlled authorization or confirmation state;
- executing actions outside `HarnessRunner`;
- replacing the durable claim store with weaker non-atomic semantics;
- enabling arbitrary real customer mutations globally;
- accepting action success semantics other than the supplied API's explicit accepted result without a new contract;
- changing the scientific gate or using provider-comparison calls for this work.
