# PostgreSQL restart / failure / recovery campaign — 2026-09-04

## Decision

Close the production restart/recovery P0 with an integrated, provider-free campaign over the promoted authenticated PostgreSQL topology.

The campaign does **not** add replay or retry behavior. It verifies that the existing durable-state recovery boundaries are conservative after an abrupt process-loss equivalent:

- runtime execution left `accepted` or `running` → `interrupted`;
- consequential action execution left nonterminal → `uncertain`;
- action custody left `EXECUTING` → `UNCERTAIN`;
- matching idempotency claim left `CLAIMED` → `UNCERTAIN`;
- `PENDING_CONFIRMATION` remains pending;
- terminal `completed` / `failed` executions remain terminal;
- a second restart performs no new recovery transitions.

No restart is interpreted as permission to replay an agent run or retry a consequential action.

## Why this is separate from EV-007 / EV-008

EV-007 validates provider-free failure semantics and safety behavior at the agent/runtime contract. EV-008 validates repeated deterministic stability across fixed units.

Neither campaign proves the persistent product lifecycle across PostgreSQL restart boundaries. This campaign specifically exercises the operational stores wired into `create_authenticated_postgres_action_capable_product_app`.

## Campaign topology

The trusted harness creates the complete PostgreSQL schema, then seeds mixed durable state before product startup:

1. one runtime execution in `accepted`;
2. one runtime execution in `running`;
3. one runtime execution already `completed`;
4. one runtime execution already `failed`;
5. one consequential action execution in `running`;
6. the same action in custody state `EXECUTING`;
7. the action idempotency ledger in `CLAIMED`;
8. a separate action in `PENDING_CONFIRMATION`.

The seed connection is then closed without reconciliation. This represents the persisted state that can remain after process loss at those persistence boundaries.

The promoted authenticated PostgreSQL factory is created with `initialize_schema=False`. Startup performs:

- action custody / idempotency reconciliation;
- run-execution reconciliation;
- normal product initialization.

A fresh authenticated run is then submitted to prove the product remains usable after recovery, while a second tenant is denied visibility of that run.

The application is shut down and constructed a second time against the same PostgreSQL schema. The second startup must report zero new recoveries.

## Safety invariants

The evidence contract fails closed unless all preregistered expectations are satisfied:

- exactly two orphaned runtime executions become `interrupted`;
- exactly one orphaned action execution becomes `uncertain`;
- exactly one custody `EXECUTING` row becomes `UNCERTAIN`;
- exactly one matching ledger `CLAIMED` row becomes `UNCERTAIN`;
- pending confirmation is preserved;
- completed runtime state is preserved;
- failed runtime state is preserved;
- a fresh run completes after recovery;
- cross-tenant read is blocked;
- no action transport call occurs during either restart;
- no provider call is used by the campaign;
- second restart produces zero new runtime/action/ledger recoveries.

The report is hash-bound and rejects tampering.

## Evidence boundary

The persisted/reportable artifact contains only aggregate counts and booleans. It does not contain:

- run IDs;
- action IDs;
- organization, user or identity values;
- bearer tokens or signing secrets;
- raw action arguments or idempotency keys;
- prompts, raw traces, provider material or chain-of-thought.

The evidence schema explicitly states:

- `interpretation = safety_contract_only`;
- `production_availability_claim_ready = false`;
- `automatic_retry_count = 0`;
- `replay_count = 0`.

## Claim boundary

A green campaign proves the repository's deterministic restart-safety contract against PostgreSQL in CI. It does **not** prove deployment uptime, recovery time objective, recovery point objective, availability percentage, multi-region failover, infrastructure restart orchestration or external PostgreSQL HA behavior.

Those are deployment/infrastructure measurements and must not be inferred from this provider-free repository test.
