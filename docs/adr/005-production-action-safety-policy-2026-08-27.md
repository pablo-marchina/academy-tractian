# ADR-005 — P0 production consequential-action safety boundary

Status: `ACCEPTED`
Date: 2026-08-27
Decision state: `FROZEN_FOR_PRODUCTION_ACTION_SAFETY_POLICY`
Issue: #23
Initial implementation validation: PR #24 head `f6d3be0fb26472d18d12ba5df858ac8aa55bc60d`, `production-runtime` run `#5` / Actions run `33133709999`, `completed / success`
Root production tests: `45/45 PASS`
ADR-004 controller regression: `12/12 PASS`
Triggered workflows on validated implementation head: `11/11 success`
Scientific state changed: `NO`
Provider/model calls for this decision: `0`
Evaluator/private/gold access: `0`
Production action transport calls under the real runtime: `0`

## Context

The repository now has a validated provider-free production runtime, an accepted P0 controller boundary (ADR-004), the canonical 18-operation ToolSpec registry, and a trace-only deterministic production evaluator. Five of the canonical ToolSpecs are mutating actions:

- `update_asset_config`;
- `reprocess_analysis`;
- `request_specialist_analysis`;
- `request_retraining`;
- `escalate_case`.

The first production runtime intentionally granted zero action permissions and fixed `actions_enabled = false`, which safely prevented every action from reaching transport. That simple baseline is correct for the current runtime, but by itself it does not define what would have to be true before a future production action could be considered safe.

The existing E2 boundary already provides useful deterministic controls: B1 strict argument validation, required action justification, B2 declared-permission and known cross-company resource checks, runner-owned identity, and normalized trace evidence. The remaining production-specific gaps are material: explicit requester confirmation, fail-closed handling of unknown resource ownership, idempotency/duplicate-action protection, and a global production execution switch that cannot be overridden by model output.

Issue #23 therefore asks a deliberately narrower question than “should production actions be enabled?” The question is: **what deterministic production action-safety protocol should be frozen now while all real production actions remain disabled?**

## Requirements affected

- P0 — safe `execute` path foundations and useful human fallback/escalation.
- P0 — `REQ-017`: integrated Agent + evaluation framework with a credible path to consequential actions.
- P1 — authorization isolation, traceability, failure containment, reproducibility and duplicate-action prevention.
- Partner-quality requirement — requester confirmation for consequential real-product actions must remain separate from benchmark accepted-action semantics.

This ADR does **not** authorize production action execution and does not change the scientific evaluation gate.

## Hard constraints

1. `HarnessRunner.execute_tool()` remains the exclusive real tool-execution boundary.
2. `ProductionRuntimeConfig.actions_enabled` remains `Literal[False]` in the accepted implementation covered by this ADR.
3. No production action may reach transport as a consequence of accepting this ADR.
4. Permission, company/resource scope, requester confirmation, idempotency state, global execution state and user identity are runtime-owned; none may be inferred from model text.
5. Runtime-owned authorization data must not appear in `ControllerContext` or be accepted as model/tool arguments.
6. Confirmation and idempotency must bind to the exact proposed action, not merely a tool name or resource class.
7. Resource-targeted actions fail closed when company ownership is unknown.
8. Every material gate remains independently inspectable; authorization is not an arbitrary weighted score.
9. Duplicate consequential action attempts must be detectable before transport.
10. The policy must remain provider-free and require no private evaluator/gold/semantic state.
11. Actual future action enablement requires a separate governed decision and evidence; capability is not authorization.

## Decision criteria

| Criterion | Required interpretation |
|---|---|
| Fail-closed default | Current production runtime continues to execute zero mutating actions. |
| Permission integrity | Each action requires all declared ToolSpec permissions from runtime-owned authorization state. |
| Scope integrity | Resource ownership must be known and match the requester/company boundary; unknown scope fails closed. |
| Requester control | Consequential action requires explicit runtime-owned confirmation bound to the exact proposed action. |
| Duplicate safety | Exact action must have a runtime-owned idempotency key that has not already been consumed. |
| Argument/justification integrity | Canonical ToolSpec/B1 requirements and minimum justification remain mandatory. |
| Model isolation | Model/tool arguments cannot set confirmation, idempotency, permissions, scope, identity or global execution state. |
| Traceability | Stable reason codes and independently testable checks must identify why an action is blocked. |
| Reproducibility | Policy decisions/fingerprints are deterministic and testable with zero provider calls. |
| Boundary compatibility | No second execution path is introduced; the policy remains a B2-compatible guard above `HarnessRunner`. |
| Reversibility | The policy can later be connected to real authorization/idempotency state without weakening its invariants. |

## Alternatives considered

### A — Keep the simple read-only baseline only

Continue granting zero permissions and rely on `actions_enabled = false`, without defining a richer production action policy.

**Advantages**

- Smallest implementation.
- Safe for the current read-only product slice.
- No additional state contracts.

**Risks / costs**

- Provides no evidence-backed path to future action enablement.
- Cannot distinguish readiness failures such as missing confirmation, unknown scope or duplicate idempotency state.
- Makes later action enablement a larger one-step change instead of a staged safety decision.

**Decision:** `REJECTED_AS_COMPLETE_POLICY`; retained as the current execution baseline, but insufficient as the production action-safety contract.

### B — Use only existing E2 permission + resource scope + justification

Reuse `ResourcePolicy` plus B1 validation as the complete production authorization layer.

**Advantages**

- Already implemented and tested.
- Small integration surface.
- Preserves existing B2 semantics.

**Risks / costs**

- Known-resource checking is not fail-closed when ownership is absent.
- No explicit requester confirmation contract.
- No idempotency or duplicate-action protection.
- Does not separate benchmark action semantics from real-product authorization strongly enough.

**Decision:** `REJECTED_AS_INCOMPLETE_FOR_PRODUCTION_ACTIONS`.

### C — Layered runtime-owned production action-safety policy, while keeping execution disabled

Add an explicit production B2-compatible policy requiring all relevant gates independently:

```text
canonical action proposal
  -> declared permission
  -> global production execution switch
  -> runtime-context isolation
  -> canonical argument contract
  -> known resource/company scope
  -> same-company scope
  -> canonical justification
  -> requester confirmation bound to exact action fingerprint
  -> runtime-owned idempotency key for exact fingerprint
  -> idempotency key not previously consumed
  -> ALLOWED only if every check passes
```

The action fingerprint is a deterministic SHA-256 over canonical action identity and arguments. Confirmation and idempotency therefore authorize one exact proposal rather than a broad action class. Raw idempotency keys are not serialized into the policy decision; only their hash may appear in the diagnostic result.

The policy supports deterministic dry-run evaluation with a hypothetical explicitly enabled context so every gate can be tested. The real `ProductionRuntime` continues to instantiate it with execution disabled, zero permissions, and no confirmations/idempotency/scope bindings.

**Advantages**

- Creates a testable path to future safe action enablement without enabling anything now.
- Preserves E2/HarnessRunner ownership.
- Keeps runtime-owned state outside model control.
- Makes unknown scope and duplicate actions explicit fail-closed states.
- Separates independent safety gates and preserves exact reasons.
- Provider-free and private-evaluator-free.

**Risks / costs**

- Introduces additional authorization state that must eventually be backed by trusted production sources.
- In-memory/dry-run idempotency bindings are not a substitute for a durable distributed idempotency store.
- A future action-enabled runtime still needs real identity/authorization/scope/confirmation provenance plus retry/failure semantics.

**Decision:** `SELECTED` for the P0 production action-safety policy scope.

### D — Move action execution/approval outside `HarnessRunner` or make all actions human-only

Use a separate workflow/framework/manual system for action approval/execution instead of the canonical agent execution boundary.

**Advantages**

- Could reduce immediate implementation pressure on automated action controls.
- Human-only operation can be an appropriate fallback for high-risk cases.

**Risks / costs**

- A second execution path weakens the stable ToolSpec/RunTrace contract and complicates evaluation/replay.
- Does not satisfy the intended integrated execute path if used as the only long-term mechanism.
- Framework-owned dispatch could bypass the exact E2 ownership rule frozen in ADR-004.

**Decision:** `REJECTED_AS_PRIMARY_PATH`; human escalation remains a fallback, not a replacement for the governed execution boundary.

## Validation experiment

The selected policy was implemented before acceptance and validated without enabling real production actions.

Implementation head:

`f6d3be0fb26472d18d12ba5df858ac8aa55bc60d`

Primary validation:

```text
workflow                  production-runtime
run                       33133709999 / #5
root production tests     45 / 45 PASS
ADR-004 controller tests  12 / 12 PASS
job conclusion            success
triggered workflows       11 / 11 success
provider/model calls      0
real action transport     0
```

The deterministic tests cover:

- all five canonical actions reaching `ALLOWED` only inside a fully satisfied hypothetical dry-run context;
- missing permission → `PERMISSION_DENIED`;
- disabled global switch with other gates satisfied → `ACTIONS_DISABLED`;
- unknown scope → `RESOURCE_SCOPE_UNKNOWN`;
- cross-company scope → `RESOURCE_SCOPE_DENIED`;
- insufficient justification → `INVALID_JUSTIFICATION`;
- missing exact requester confirmation → `CONFIRMATION_REQUIRED`;
- missing runtime-owned idempotency binding → `IDEMPOTENCY_KEY_REQUIRED`;
- already-consumed idempotency key → `DUPLICATE_ACTION`;
- attempted model/tool injection of runtime-owned authorization fields → `RUNTIME_CONTEXT_FIELD_PROPOSED` plus canonical argument rejection;
- stable action/decision hashes and no raw idempotency-key serialization;
- complete safety metadata across all five canonical action ToolSpecs;
- DecisionSource isolation from runtime authorization state;
- real `ProductionRuntime` action proposals still causing zero transport calls;
- provider/orchestration/private-evaluator import isolation.

The initial implementation retained `PERMISSION_DENIED` as the real runtime's first B2 reason because the real runtime still grants zero permissions. This preserves the established read-only trace behavior. The independently tested `ACTIONS_DISABLED` gate proves that granting a permission alone would still be insufficient to authorize execution.

## Decision

Freeze the **layered runtime-owned `ProductionActionSafetyPolicy` for the P0 production consequential-action safety scope**.

The frozen policy requires every material authorization condition independently and binds requester confirmation/idempotency to the exact action fingerprint.

The accepted production boundary is:

```text
DecisionSource ToolProposal
  -> HarnessRunner.execute_tool()
  -> B1 canonical argument / justification validation
  -> B2 ProductionActionSafetyPolicy
       - permission
       - global execution switch
       - runtime-context isolation
       - known + same-company scope
       - requester confirmation for exact action fingerprint
       - idempotency key for exact fingerprint
       - non-consumed idempotency key
  -> transport only if every applicable guard passes
```

**For the currently accepted runtime, transport remains unreachable for all mutating actions** because `actions_enabled` is fixed to `False` and the runtime grants no action permissions or action authorization state.

This ADR freezes the **policy protocol**, not action execution authorization.

## Explicit non-authorization

ADR-005 does **not**:

- enable `actions_enabled=True`;
- authorize any of the five canonical mutating tools to execute in production;
- provision real user permissions, resource/company mappings, requester confirmations or idempotency state;
- define a durable/distributed idempotency store;
- define retry semantics for real accepted actions;
- select a model/provider or authorize provider/model calls;
- authorize semantic evaluation, survivor/PREFERRED inference, FRESH_BLIND or LEGACY_LOCKED_TEST;
- modify any frozen C4 artifact or score;
- freeze the global architecture;
- claim production readiness.

The scientific gate remains independently `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`.

## Consequences

- **Positive:** a future action-enabled release has an explicit checklist and deterministic contract instead of an implicit permission-only boundary.
- **Positive:** exact-action fingerprinting prevents broad confirmation/idempotency from silently applying to a different proposal.
- **Positive:** unknown scope and duplicate action attempts fail closed.
- **Positive:** runtime-owned authorization data stays outside model control and outside `DecisionSource` context.
- **Positive:** no new execution path or provider dependency is introduced.
- **Negative:** future real action execution now depends on trusted external state sources for permission, scope, confirmation and idempotency.
- **Negative:** durable duplicate protection and retry semantics remain unresolved production-fit work.
- **Operational:** every future action-enablement change must prove the policy with real trusted state and preserve the current zero-bypass execution path.
- **Evaluation:** action-safety diagnostics may be evaluated deterministically from the runtime trace, but semantic task correctness remains a separate evaluator concern.

## Reversal / amendment triggers

Reopen or supersede ADR-005 if:

1. real identity/authorization infrastructure requires a materially different policy contract;
2. durable/distributed idempotency semantics cannot be represented by the current exact-action fingerprint model;
3. retry/timeout/provider failure evidence shows the current duplicate-protection contract is insufficient;
4. requester confirmation must support scoped/batched actions and evidence shows exact-action confirmation is too restrictive;
5. the canonical supplied API changes action semantics, persistence behavior or resource ownership boundaries;
6. a future architecture decision deliberately moves real tool execution away from `HarnessRunner`;
7. measured product evidence justifies different confirmation requirements by action impact, provided the replacement remains fail-closed and independently testable.

Actual action enablement is not a mere implementation toggle and therefore requires its own governed decision even if this ADR is not otherwise reopened.

## Regression obligations

Any implementation derived from ADR-005 must continue to prove:

- all five canonical action ToolSpecs remain covered by the action-safety protocol;
- model/tool arguments cannot supply runtime-owned permission/scope/confirmation/idempotency/global-switch state;
- unknown resource scope fails closed;
- cross-company scope fails closed;
- invalid canonical arguments/justification fail closed;
- requester confirmation is bound to the exact action fingerprint;
- an idempotency key is bound to that exact fingerprint;
- consumed idempotency state blocks a duplicate before transport;
- all blocking checks remain independently inspectable;
- raw idempotency keys are not emitted into policy diagnostics;
- `HarnessRunner.execute_tool()` remains the exclusive real execution boundary;
- DecisionSource remains isolated from authorization state;
- current production runtime continues to execute zero actions until a separate authorization explicitly changes that boundary;
- provider/private/semantic/scientific state cannot silently enter this policy.

## Sources

Repository evidence:

- issue #23
- PR #24
- `src/academy_tractian/action_safety.py`
- `src/academy_tractian/runtime.py`
- `tests/test_action_safety.py`
- `tests/test_runtime.py`
- `research/e2/policy.py`
- `research/e2/validation.py`
- `research/e2/tool_registry.py`
- ADR-004
- `production-runtime` Actions run #5 / `33133709999`

No external framework or provider capability is needed for this decision; the material choice is a repository-local production authorization boundary over the already frozen ToolSpec/HarnessRunner contracts.
