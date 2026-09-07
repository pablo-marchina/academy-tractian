# Governed Actions Production Runbook

**Status:** ACTIVE operational contract  
**Last verified:** 2026-09-07 BRT  
**Current merged production source:** `3545d75c00ca30419e0f47e8b1950aa50cbbf462`  
**Current live-validation state:** governed path enabled; five-action upstream acceptance incomplete

## Scope

This runbook covers rollout, validation, incident response and rollback for the five canonical consequential TRACTIAN actions:

- `reprocess_analysis` — requires `action_low`;
- `request_specialist_analysis` — requires `action_low`;
- `update_asset_config` — requires `action_high`;
- `request_retraining` — requires `action_high`;
- `escalate_case` — requires `escalate`.

The model/browser may propose an action, but they never own canonical permissions, organization/company authority, TRACTIAN credentials, upstream actor identity, confirmation fingerprints, idempotency material or the action kill switch.

## Current production truth

The governed action architecture is implemented, CI-qualified and enabled in the production composition. The hosted capability contract advertises exactly five executable governed actions under `GOVERNED_CONFIRMATION`.

That is **not equivalent to proving all five upstream writes**.

The auditable production smoke introduced by PR #213 was executed through a fresh Railway configuration snapshot. The pre-deploy validation failed safely on:

```text
update_asset_config: HTTP 403, accepted=false
```

Validation deployment:

```text
5ba36471-776c-4e15-919b-56e2da216b74
```

The previous healthy deployment remained serving. Therefore the current claim boundary is:

> governed execution is enabled and its local safety architecture is proven by tests/CI, but complete five-action upstream acceptance remains open until server-owned upstream actor routing is corrected and the smoke passes 5/5.

Do not weaken the local grant, resource scope, confirmation, idempotency or lease boundary to make the upstream 403 disappear.

## Safe default and emergency switch

The configuration default remains fail-closed:

```text
ACADEMY_ACTIONS_ENABLED=false
```

Production may intentionally set it to `true` only when all prerequisites below are satisfied. The variable is a host-owned kill switch; there is intentionally no browser/admin endpoint that mutates it.

With the switch off, no confirmation reaches the external action transport.

## Required production configuration

Governed action execution may be enabled only when all of the following are true:

1. `ACADEMY_PROVIDER_CALLS_ENABLED=true` with the validated release provider configuration.
2. `ACADEMY_TRACTIAN_TRANSPORT_ENABLED=true` with the remote HTTPS TRACTIAN endpoint and server-managed headers.
3. `ACADEMY_ACTIONS_ENABLED=true`.
4. `ACADEMY_ACTION_AUTHORIZATION_GRANTS_JSON` contains a valid non-empty server-owned grant document.
5. The deployed artifact SHA, configured release SHA and Railway runtime SHA agree.
6. Durable PostgreSQL action custody, idempotency, run ownership, execution state, wakeup/handoff and action execution lease stores are healthy.
7. The upstream action-actor binding required by the supplied TRACTIAN runtime is server-owned, complete for every intended `(company_id, required_permission)` pair and cannot be influenced by the browser/model.
8. The live write smoke for the release/tenant under promotion passes the exact action set intended for production.

Example grant shape using non-production placeholders:

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

Grant material, upstream actor mappings and credentials are secret operational configuration. Do not place real user, tenant, company, resource, credential, authorization or actor values in source control, browser payloads, screenshots or browser-safe logs.

## Authorization invariants

Every confirmed action must pass all of these independent gates:

- authenticated run/action ownership for the exact organization and requester;
- tenant-aware server-owned grant resolution for the same authenticated organization/user;
- canonical ToolSpec permission (`action_low`, `action_high`, or `escalate`);
- exact resource-to-company binding matching `user_company_id`;
- exact server-custodied action fingerprint and arguments;
- explicit requester confirmation of that existing action record;
- durable idempotency claim before external I/O;
- active action execution lease/generation ownership;
- global host-owned action kill switch enabled;
- server-owned upstream TRACTIAN actor selection for the already-authorized company/permission;
- explicit upstream acceptance before the state becomes `ACCEPTED`.

The confirmation request accepts only:

```json
{"confirm": true}
```

Attempts to submit arguments, permissions, idempotency keys, resource authority, upstream actor identity or other execution material through the confirmation payload must fail validation.

## Local requester identity vs upstream TRACTIAN actor

These are distinct trust concepts.

```text
local authenticated product user
→ owns tenant authorization
→ resource/company scope
→ action custody
→ exact confirmation
→ idempotency
→ audit trail

server-owned TRACTIAN actor
→ vendor-specific execution identity only
→ selected after local authorization
→ selected by company + canonical required permission
→ injected only at final action network boundary
```

The supplied runtime uses `x-user-id` as its actor context and applies endpoint-specific permission checks. Live investigation showed that the company scope under test contains separate upstream actors for low-impact and high-impact/escalation permissions. Therefore forwarding one local requester ID as the vendor actor for every action family is not a valid universal mapping.

Required mapping invariant:

```text
(company_id, required_permission) -> exactly one server-owned upstream actor
```

Fail closed when the mapping is missing, malformed or ambiguous. Never choose an upstream actor based on model output, browser data or convenience fallback.

The corrective actor-routing implementation is in progress and is not yet production-proven at this record's timestamp.

## State semantics

- `PENDING_CONFIRMATION`: proposal exists; no external side effect has been attempted.
- `CONFIRMED`: exact existing action was explicitly confirmed.
- `EXECUTING`: the platform has claimed the exact action and may attempt the external request once.
- `ACCEPTED`: the external API explicitly accepted the action.
- `NOT_ACCEPTED`: the external API explicitly did not accept it.
- `BLOCKED`: deterministic policy denied execution.
- `UNCERTAIN`: the platform cannot prove whether an external side effect occurred. Never auto-retry this state.

`UNCERTAIN` is a terminal containment state for ambiguous writes, process loss, lease loss or transport uncertainty. Operator investigation is required before any new action is proposed.

## Auditable five-action production smoke

Canonical module:

```text
python -m academy_tractian.governed_write_transport_smoke
```

The module contains no production credentials, resource IDs or grants in source. Targets and credentials are supplied through server-owned runtime environment variables.

Before any write it requires the hosted capability endpoint to report:

- `actions == 5`;
- `executable_actions == 5`;
- `action_execution.enabled == true`;
- `action_execution.mode == GOVERNED_CONFIRMATION`;
- governed action path enabled.

It then exercises the five canonical action ToolSpecs through the canonical request binder and `ProductionTractianTransport`.

Each action passes only when:

```text
status in {200, 201, 202}
AND body.accepted == true
```

The smoke must not print credentials, resource IDs, grant contents or upstream response bodies.

A single failed action fails the validation deployment. Do not reinterpret a 401/403/404/5xx or `accepted=false` as success.

## Promotion sequence

1. Select the exact tested source SHA.
2. Require the applicable CI matrix to be green, including action safety/idempotency/lease/recovery regressions.
3. Deploy the exact source with the normal read/connectivity preflight and verify release identity.
4. Configure server-owned grants and upstream actor mappings outside source control using minimum required scope.
5. Verify `/api/release0/capabilities` reports exactly five `EXECUTABLE_WITH_CONFIRMATION` actions and `action_execution.mode=GOVERNED_CONFIRMATION`.
6. Force a **fresh Railway configuration snapshot** for the action smoke. A generic Railway `redeploy` may reuse a previously captured snapshot and therefore is not proof that a newly edited `preDeployCommand` or variable set was materialized.
7. Execute `academy_tractian.governed_write_transport_smoke` as the pre-deploy validation.
8. Require all five intended actions to return accepted HTTP status + `accepted=true`.
9. Verify a failed smoke leaves the previous healthy deployment serving.
10. After 5/5 pass, exercise the normal product confirmation path and independently verify action-state persistence/evaluation.
11. Do not automatically expand grants or upstream actor mappings after one successful tenant/resource test.

## Current evidence ledger

### PR #211

```text
merge SHA   1a1e7139bfa0361416120b3f21937c4048b5bb1f
Railway     9732a2cb-c321-4fcf-83f8-c6f87eeab06a
status      SUCCESS
```

This proved production composition with governed actions enabled; it did not prove 5/5 vendor acceptance.

### PR #213

```text
merge SHA   3545d75c00ca30419e0f47e8b1950aa50cbbf462
CI gate     34164123263 — required-gate SUCCESS
Railway     2cbc4215-f59a-4947-8691-0d4776458445 — SUCCESS
```

CI included production wheel/image, action lease/fencing, horizontal runtime, Railway IaC, clean-clone full-product reproduction and Chromium Playwright acceptance.

### Fresh live action validation

```text
Railway     5ba36471-776c-4e15-919b-56e2da216b74
result      FAILED SAFE
cause       update_asset_config -> HTTP 403 / accepted=false
containment previous healthy production remained serving
```

This failure is current evidence and must remain visible until superseded by a later prospective 5/5 pass.

## Go / no-go checks

Go only when all applicable release CI is green and the deployed host reports:

- correct exact release identity;
- provider calls healthy under the configured zero-cost policy;
- TRACTIAN transport configured and server-managed;
- persistent stores ready;
- action execution lease backend ready;
- action kill switch state matches the intended rollout;
- server-owned upstream actor mapping is complete for the intended company/permissions;
- five-action smoke passes for the intended action set;
- no unexpected `UNCERTAIN` action executions;
- no cross-tenant authorization or observability failures;
- no secret-bearing grant/actor material in browser-safe metadata or observability.

No-go if any prerequisite is missing, any hard security/evaluation gate fails, release identity drifts, an actor mapping is missing/ambiguous, the vendor rejects any required action or an unexplained `UNCERTAIN` action exists.

## Emergency rollback

For remote production, disable new confirmations by setting:

```text
ACADEMY_ACTIONS_ENABLED=false
```

and promoting/restarting the host with that configuration. Verify capabilities no longer advertise executable actions.

Rollback rules:

- never replay an `UNCERTAIN` action automatically;
- never reuse an old idempotency claim for a new proposal;
- do not weaken grants or substitute a more privileged actor to work around a policy/upstream block;
- do not expose a public/admin browser endpoint for canonical permissions, actor selection or kill-switch mutation;
- preserve custody, ledger, execution, observability, lease and failed-smoke records for incident review.

## Incident triage

For an unexpected action outcome, capture only safe identifiers and states: action id, execution run id, tool name, impact, safe policy/upstream status code, release SHA and timestamps. Do not copy raw credentials, private grant JSON, actor mapping JSON, raw TRACTIAN payloads or private model reasoning into tickets or browser-visible evidence.

If the external outcome cannot be independently established, leave the action as `UNCERTAIN`, keep automatic retry disabled and require a new operator-reviewed proposal after the external system state has been reconciled.

See [`progress/2026-09-07-production-governed-actions-ux-and-validation.md`](progress/2026-09-07-production-governed-actions-ux-and-validation.md) for the dated evidence record.