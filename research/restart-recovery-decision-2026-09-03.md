# Restart + failure recovery decision — 2026-09-03

## Decision

Add one focused recovery campaign for the promoted signed-bearer + PostgreSQL product topology.

This campaign does **not** replace or duplicate EV007/EV008:

- EV007 remains the source of truth for provider-free decision, tool-boundary, transport, authorization, idempotency and adversarial-evaluator failure families.
- EV008 remains the repeated stability campaign.
- this slice measures only durable crash-residue semantics during application startup/restart.

## Frozen protocol

`research/restart-recovery-protocol-v1.json` freezes ten invariants before the integrated result is inspected:

1. accepted runtime execution -> `interrupted`;
2. running runtime execution -> `interrupted`;
3. accepted action execution -> `uncertain`;
4. running action execution -> `uncertain`;
5. executing action custody -> `UNCERTAIN`;
6. claimed action ledger entry -> `UNCERTAIN`;
7. pending confirmation remains `PENDING_CONFIRMATION`;
8. accepted custody + accepted claim remain `ACCEPTED`;
9. authenticated owner visibility and cross-tenant 404 isolation survive recovery;
10. a second startup produces no additional recovery transitions.

The report is hash-bound to the frozen protocol and refuses to build if any preregistered case is missing or fails.

## Why `interrupted` vs `uncertain`

Read-only/runtime work may be safely described as interrupted after process loss because no consequential mutation is being inferred.

Consequential action execution is different. Once execution could have crossed the external mutation boundary, process loss cannot prove whether the remote system accepted the mutation. Therefore action execution, custody and idempotency claims fail safe to `UNCERTAIN`.

Recovery must never convert uncertainty into permission to retry. An operator or later reconciliation mechanism needs external evidence before any new action can be proposed.

## Integrated campaign topology

The CI campaign uses:

- the promoted `create_authenticated_postgres_action_capable_product_app` entrypoint;
- signed bearer identity with explicit tenant/user scope;
- PostgreSQL 18;
- a scoped role that is non-superuser, non-`BYPASSRLS` and non-owner;
- production `PostgresRunExecutionStore`, `PostgresPendingActionCustody`, and `PostgresActionIdempotencyLedger`;
- existing startup `reconcile_orphaned()` and `reconcile_orphaned_actions()` paths;
- an intentionally exploding transport if any startup replay occurs.

Crash residue is seeded through the same durable store APIs before the serving app is instantiated. No browser endpoint is given authority to manufacture recovery state.

## Evidence and privacy

The published artifact contains only aggregate counts and semantic case labels/states. It contains no:

- run IDs;
- action IDs;
- organization IDs;
- user or identity IDs;
- bearer tokens;
- private action arguments or idempotency keys;
- prompts or raw traces.

The integrated test separately asserts those private fragments are absent from the serialized report.

## Claim boundary

A passing campaign supports this repository-level statement:

> The promoted authenticated PostgreSQL topology reconciles the preregistered durable crash-residue states fail-safe and idempotently, without replaying consequential transport and without weakening tenant isolation.

It does **not** prove:

- a process supervisor will restart the deployment;
- a cloud/database outage meets any RTO/RPO;
- PostgreSQL itself survives host/region loss;
- network partitions are detected within a particular time;
- external TRACTIAN APIs expose enough information to resolve an `UNCERTAIN` mutation automatically.

Those are deployment/distributed-systems properties outside this repository-level startup contract.

## Promotion boundary

No retry policy, execution state transition, worker count, storage backend or action behavior is changed by this slice. The existing fail-safe semantics are being exercised end-to-end on the promoted topology.

Any future automatic recovery/retry challenger must be evaluated separately and may not promote while duplicate-action or unauthorized-action hard gates are non-zero.