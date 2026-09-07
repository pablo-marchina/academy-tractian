# Governed Actions Production Runbook

## Scope

This runbook covers the production rollout and rollback of the five canonical consequential TRACTIAN actions:

- `reprocess_analysis` — requires `action_low`;
- `request_specialist_analysis` — requires `action_low`;
- `update_asset_config` — requires `action_high`;
- `request_retraining` — requires `action_high`;
- `escalate_case` — requires `escalate`.

The model/browser may propose an action, but they never own canonical permissions, organization/company authority, TRACTIAN credentials, confirmation fingerprints, idempotency material, or the action kill switch.

## Default state

Production remains fail-closed unless all action prerequisites are explicitly configured. The safe default is:

```text
ACADEMY_ACTIONS_ENABLED=false
```

With actions disabled, reads may still be live and action proposals may still be observable, but no confirmation can reach the external action transport.

## Required production configuration

Governed action execution may be enabled only when all of the following are true:

1. `ACADEMY_PROVIDER_CALLS_ENABLED=true` with the validated release provider configuration.
2. `ACADEMY_TRACTIAN_TRANSPORT_ENABLED=true` with the remote HTTPS TRACTIAN endpoint and server-managed headers.
3. `ACADEMY_ACTIONS_ENABLED=true`.
4. `ACADEMY_ACTION_AUTHORIZATION_GRANTS_JSON` contains a valid non-empty server-owned grant document.
5. The deployed artifact SHA, configured release SHA, and Railway runtime SHA agree.
6. Durable PostgreSQL action custody, idempotency, run ownership, execution state, wakeup/handoff, and action execution lease stores are healthy.

Example grant shape using non-production placeholder identifiers:

```json
[
  {
    "schema_version": "trusted-action-authorization-grant-v1",
    "user_id": "operator-user-id",
    "organization_id": "organization-id",
    "user_company_id": "company-id",
    "permissions": ["action_low", "action_high", "escalate"],
    "resource_company_bindings": [
      {"resource_id": "analysis-id", "company_id": "company-id"},
      {"resource_id": "asset-id", "company_id": "company-id"},
      {"resource_id": "model-id", "company_id": "company-id"},
      {"resource_id": "case-id", "company_id": "company-id"}
    ],
    "policy_revision": "governed-execute-v1",
    "active": true,
    "source_owned": true
  }
]
```

Grant material is secret operational configuration. Do not place real user, tenant, company, resource, credential, or authorization data in source control, browser payloads, logs, or screenshots.

## Authorization invariants

Every confirmed action must pass all of these independent gates:

- authenticated run/action ownership for the exact `organization_id` and `user_id`;
- tenant-aware server-owned grant resolution for the same authenticated organization/user;
- canonical ToolSpec permission (`action_low`, `action_high`, or `escalate`);
- exact resource-to-company binding matching `user_company_id`;
- exact server-custodied action fingerprint and arguments;
- explicit requester confirmation of that existing action record;
- durable idempotency claim before external I/O;
- active action execution lease/generation ownership;
- global host-owned action kill switch enabled.

The confirmation request accepts only `{"confirm": true}`. Attempts to submit arguments, permissions, idempotency keys, resource authority, or other execution material through the confirmation payload must fail validation.

## State semantics

- `PENDING_CONFIRMATION`: proposal exists; no external side effect has been attempted.
- `EXECUTING`: the platform has claimed the exact action and may attempt the external request once.
- `ACCEPTED`: the external API explicitly accepted the action.
- `NOT_ACCEPTED`: the external API explicitly did not accept it.
- `BLOCKED`: deterministic policy denied execution.
- `UNCERTAIN`: the platform cannot prove whether an external side effect occurred. Never auto-retry this state.

`UNCERTAIN` is a terminal containment state for ambiguous writes, process loss, lease loss, or transport uncertainty. Operator investigation is required before any new action is proposed.

## Promotion sequence

1. Merge/deploy the code with `ACADEMY_ACTIONS_ENABLED=false`.
2. Verify the exact release SHA and `/api/production/health` before enabling writes.
3. Verify `/api/release0/capabilities` reports reads correctly and action execution remains `PROPOSAL_ONLY` while the switch is off.
4. Configure the server-owned grants outside source control. Validate that only intended users/resources receive the minimum required permissions.
5. Confirm the hosted security campaign required by the release policy is not in a failing or inconclusive state. Source-only evidence must never be represented as hosted production proof.
6. Enable `ACADEMY_ACTIONS_ENABLED=true` only after provider, TRACTIAN transport, persistence, lease, identity, and authorization prerequisites are healthy.
7. Verify `/api/release0/capabilities` reports exactly five `EXECUTABLE_WITH_CONFIRMATION` actions and `action_execution.mode=GOVERNED_CONFIRMATION`.
8. Exercise the first real write only on an explicitly approved low-impact resource and with an operator who can independently verify the expected TRACTIAN-side effect.
9. Confirm the action transitions to `ACCEPTED` only after the external API explicitly accepts it and that the execution run/evaluation is persisted.
10. Do not automatically expand grants after the first successful write. Promotion of additional users/resources is an authorization change, not an inference from model quality.

## Go / no-go checks

Go only when all applicable release CI is green and the deployed host reports:

- correct exact release identity;
- provider calls healthy under the configured zero-cost policy;
- TRACTIAN transport configured and server-managed;
- persistent stores ready;
- action execution lease backend ready;
- action kill switch state matches the intended rollout;
- no unexpected `UNCERTAIN` action executions;
- no cross-tenant authorization or observability failures;
- no secret-bearing grant material in browser-safe metadata or observability.

No-go if any prerequisite is missing, any security/evaluation hard gate fails, release identity drifts, the transport is unverified for the intended tenant, or an unexplained `UNCERTAIN` action exists.

## Emergency rollback

There is intentionally no public HTTP endpoint that mutates the action kill switch.

For remote production, disable new confirmations by setting:

```text
ACADEMY_ACTIONS_ENABLED=false
```

and promoting/restarting the host with that configuration. Verify `/api/production/health` reports the action kill switch engaged and `/api/release0/capabilities` no longer advertises executable actions.

Rollback rules:

- never replay an `UNCERTAIN` action automatically;
- never reuse an old idempotency claim for a new proposal;
- do not weaken grants to work around a policy block;
- do not expose a public/admin browser endpoint for canonical action permissions or kill-switch mutation;
- preserve custody, ledger, execution, observability, and lease records for incident review.

## Incident triage

For an unexpected action outcome, capture only safe identifiers and states: action id, execution run id, tool name, impact, safe policy reason code, release SHA, and timestamps. Do not copy raw credentials, private grant JSON, raw TRACTIAN payloads, or private model reasoning into tickets or browser-visible evidence.

If the external outcome cannot be independently established, leave the action as `UNCERTAIN`, keep automatic retry disabled, and require a new operator-reviewed proposal after the external system state has been reconciled.
