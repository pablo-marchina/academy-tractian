# 028 — Controlled consequential-action execution profile — FROZEN / PROVIDER-FREE — 2026-08-28

Issue #45 / PR #46 closed the missing execution proof between ADR-005's frozen consequential-action safety policy and the final delivery requirement to support justified action requests.

The accepted change does **not** globally enable production mutations. It adds a separate controlled action-capable profile while preserving the existing read-only `ProductionRuntime` unchanged.

## Delivered boundary

Accepted runtime:

`src/academy_tractian/controlled_actions.py`

Frozen source blob:

`9e5f2d49ebc82303423f81ec8916b02c511f2a1e`

Accepted controlled evaluator:

`src/academy_tractian/controlled_action_evaluation.py`

Frozen source blob:

`ae5f1a7777893941882196c8c2f3810676eba0a4`

The profile preserves the same application-owned path:

```text
DecisionSource
→ AgentController
→ HarnessRunner.execute_tool()
→ B1 canonical argument validation
→ ADR-005 ProductionActionSafetyPolicy
→ durable exclusive-create idempotency claim
→ supplied transport
→ normalized RunTrace
→ ControlledActionEvaluator
```

No direct action transport or framework-owned action loop was added.

## Durable action-attempt custody

`DurableActionAttemptClaimStore` hashes the runtime-owned idempotency key and uses exclusive-create semantics before B2 returns `ALLOWED` to the existing runner.

The stored claim contains only:

- schema/runtime version;
- tool name;
- action fingerprint;
- idempotency-key SHA-256;
- `state=claimed`;
- `raw_idempotency_key_recorded=false`.

The file is flushed/fsynced and the containing directory is fsynced where supported.

Therefore:

```text
ADR-005 denial
→ no claim
→ no action transport

ADR-005 ALLOWED
→ durable claim
→ B2 ALLOWED
→ action transport may occur

existing claim
→ DUPLICATE_ACTION
→ no second transport

transport/process failure after claim
→ consumed / uncertain
→ no automatic replay
```

## Canonical action evidence

All five canonical mutating ToolSpecs were exercised exactly once with fully satisfied explicit trusted authorization and deterministic supplied/test transport returning `202` + `accepted=true`:

```text
update_asset_config            PASS
reprocess_analysis             PASS
request_specialist_analysis    PASS
request_retraining             PASS
escalate_case                  PASS
```

The same tests prove zero unsafe transport for missing confirmation, missing permission, unknown scope, cross-company scope, disabled execution and unprovisioned exact action fingerprints.

A new runtime instance using the same consumed idempotency key cannot replay the action.

## Controlled evaluator

The default `ProductionEvaluator` remains deliberately read-only and still rejects traces containing executed actions.

`ControlledActionEvaluator` composes the validated baseline and changes only the explicit controlled-profile assumptions:

- namespace is `prod-action:*`;
- an action call requires a preceding matching B2 `ALLOWED` event;
- supplied API success requires `accepted=true`.

It preserves lifecycle, ToolSpec, identity/seed isolation, execution-chain, policy-containment, provider-free/model-call provenance and terminal consistency checks. It does not copy action response bodies or justification text into the evaluation report.

## Preserved falsification

Evaluator-composition head:

`02a7a95765075df08cb10ccd5f89482a813f3fa0`

Production test result:

```text
165 passed / 3 failed
```

Two failures came from test fixtures using terminal value `EXECUTE`, which is not part of the canonical `Decision` enum. The fixture was corrected to canonical `ACT_REPROCESS`; terminal consistency was not weakened.

The third failure came from an isolation test rejecting the text `Scenario` when it appeared only in a docstring. The test was corrected to inspect imported symbols/modules rather than arbitrary prose.

No action policy, idempotency rule, evaluator safety check or runner behavior was relaxed.

## Validation and freeze

Corrected pre-freeze head:

`c6d0108780c40ffd9522001d6941058c4fc59c3f`

```text
production-runtime        33149724402 / #46 / success
production tests          168 passed
ADR-004 regression        12 passed
triggered workflows       11 / 11 success
```

ADR-012 and the machine freeze were then added, followed by a self-check that recomputes the declared Git blob identities.

Final PR head:

`d60fdd46dee3735bd4a49a85df3eedc7b5e799d7`

Final exact-head validation:

```text
production-runtime        33149898961 / #49 / success
production tests          170 passed
ADR-004 regression        12 passed
triggered workflows       11 / 11 success
freeze self-check         PASS
provider calls            0
real customer mutations   0
```

PR #46 merged with expected-head guard as:

`f45c568c24217b54ead8be01c7ac7e0cca2dea7e`

ADR:

`docs/adr/012-controlled-action-execution-profile-2026-08-28.md`

Machine freeze:

`research/frozen/controlled-action-execution-profile-freeze-v1.json`

## Post-merge boundary

```text
default ProductionRuntime actions          DISABLED
controlled action capability               FROZEN / ADR-012
controlled canonical action coverage       5 / 5
blanket real-customer mutations            NOT AUTHORIZED
real customer mutations performed          0
ADR-009 provider calls consumed             0 / 32
production provider/model selected         NO
scientific gate        REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

The next unblocked provider-free delivery priority is EV-007 failure-performance evidence, followed by EV-008 repeated-run stability and EV-011 customer-safe communication. The actual live provider comparison remains issue #44 and must not consume attempt 0 until its custody/secrets prerequisites are satisfied.
