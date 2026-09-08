# Governed Actions Production Runbook

**Status:** ACTIVE  
**Last synchronized:** 2026-09-08 BRT  
**Current claim:** governed action architecture is live/configurable and the controlled production transport smoke passed **5/5**; full hosted end-user/adversarial action acceptance remains pending.

## Scope

This runbook covers rollout, verification, incident handling and rollback of the five canonical consequential TRACTIAN actions:

- `reprocess_analysis` — requires `action_low`;
- `request_specialist_analysis` — requires `action_low`;
- `update_asset_config` — requires `action_high`;
- `request_retraining` — requires `action_high`;
- `escalate_case` — requires `escalate`.

The model/browser may propose an action, but never own canonical permissions, organization/company authority, TRACTIAN credentials, upstream action actor identity, confirmation fingerprints, idempotency material or the action kill switch.

## Current production evidence

A production pre-deploy smoke on the governed action path reported:

```text
mode                         GOVERNED_CONFIRMATION
actions                      5
executable_actions           5
governed_action_path_enabled true
status                       PASS
```

Controlled transport results:

```text
reprocess_analysis            accepted / HTTP 200
request_specialist_analysis  accepted / HTTP 200
update_asset_config          accepted / HTTP 200
request_retraining           accepted / HTTP 200
escalate_case                accepted / HTTP 200
```

The smoke recorded no credentials, resource IDs, local/upstream user IDs or response bodies.

**Claim boundary:** this proves the configured governed transport for the smoke's server-owned bindings. It does not replace the pending full end-user/adversarial SECURITY-V1 campaign and does not prove distributed exactly-once external side effects.

## Runtime composition

Provider calls, TRACTIAN transport and actions are independent validated opt-ins. When actions are enabled, production must have both:

1. a server-owned action authorization grant source; and
2. server-owned upstream TRACTIAN action actor bindings with complete coverage for every active grant.

Incomplete actor coverage is a boot blocker. Upstream action actors configured while actions are disabled are also rejected.

Ordinary authenticated users without action grants may still use read paths through a zero-action principal; that fallback grants no consequential permission. Confirmation remains strict and tenant-aware.

## Safe default / kill-switch posture

The fail-closed configuration is still:

```text
ACADEMY_ACTIONS_ENABLED=false
```

Use it for emergency rollback or any deployment where action prerequisites/security evidence are not valid. Current production may intentionally enable governed actions only when all required server-owned grant/actor/persistence/identity prerequisites are present; do not infer the live switch state from a historical document or source default. Check the current capability/health surface on the exact deployed SHA.

## Required production configuration

Governed action execution may be enabled only when all are true:

1. validated provider calls are enabled under the current zero-cost/no-fallback provider policy;
2. real TRACTIAN transport is enabled with server-managed endpoint/headers;
3. `ACADEMY_ACTIONS_ENABLED=true`;
4. `ACADEMY_ACTION_AUTHORIZATION_GRANTS_JSON` contains valid server-owned grants;
5. `ACADEMY_TRACTIAN_ACTION_ACTORS_JSON` contains complete server-owned upstream actor bindings for all active grants;
6. artifact/configured/Railway runtime SHAs agree;
7. PostgreSQL custody, idempotency, run ownership, execution state and action lease stores are healthy;
8. current SECURITY-V1 policy does not contain a failing hard gate that forbids action execution.

Real grant/actor material is secret operational configuration. Never commit it or expose it in browser payloads, logs, screenshots, tickets or public evidence.

## Authorization invariants

Every confirmed action must pass independently:

- authenticated action/run ownership for exact organization/user;
- tenant-aware server-owned grant resolution;
- canonical ToolSpec permission;
- exact resource→company binding matching the authorized company;
- exact server-custodied action arguments/fingerprint;
- explicit requester confirmation of the existing opaque action record;
- active global kill switch state;
- durable idempotency claim before external I/O;
- non-transferable action execution lease/generation ownership;
- server-owned upstream TRACTIAN actor binding for the authorized company/action.

The confirmation request may only confirm/reject the existing action. Browser/model data must never override arguments, permissions, resource authority, actor identity or idempotency.

## State semantics

- `PENDING_CONFIRMATION` — proposal exists; no external action attempt yet;
- `EXECUTING` — exact action claimed; one bounded attempt may be in progress;
- `ACCEPTED` — external API explicitly accepted;
- `NOT_ACCEPTED` — external API explicitly did not accept;
- `BLOCKED` — deterministic policy denied;
- `UNCERTAIN` — external effect cannot be proven either way.

`UNCERTAIN` is terminal containment. Never auto-retry it. Reconcile external system state before a newly reviewed proposal is allowed.

## Pre-enable go/no-go

### Go only when

- exact deployed release identity is verified;
- provider calls are healthy enough for the intended user/action flow under USD0/no paid fallback;
- TRACTIAN transport is configured and server-managed;
- action grants and upstream actors are complete/minimal;
- PostgreSQL custody/idempotency/lease backends are healthy;
- no unexpected `UNCERTAIN` action exists;
- no tenant/observability/security hard gate is failing;
- no secret-bearing authorization/actor material is exposed;
- the currently required security campaign permits the rollout.

### No-go when

- provider functional acceptance for the required flow is failing;
- exact release identity drifts;
- an active grant lacks actor coverage;
- cross-tenant/resource authorization cannot be proven;
- external transport outcome is ambiguous without containment;
- an unexplained `UNCERTAIN` exists;
- cost/provider fallback could cross the USD0 boundary;
- any security/evaluation hard gate fails.

The current OpenRouter V14 B204 read campaign is failing before TRACTIAN tool execution. Do not use a successful action transport smoke to imply the agent-driven end-to-end action flow is functionally green under that provider.

## First-action rollout sequence

1. Deploy exact candidate with actions fail-closed unless the rollout is explicitly authorized.
2. Verify `/health`, production health/capabilities and exact release SHA.
3. Verify provider/model/route/cost identity and functional readiness for the intended action scenario.
4. Verify real TRACTIAN transport.
5. Configure minimal server-owned grants and complete upstream actor bindings outside source control.
6. Run current hosted security/adversarial prerequisites.
7. Enable actions only after all previous checks are green.
8. Verify capability surface reports exactly five actions and governed-confirmation mode when intended.
9. Exercise the first real consequential action only on an explicitly approved low-impact resource with independent external-side-effect verification.
10. Confirm persisted custody→confirmation→execution→outcome→evaluation trace.
11. Do not expand grants/users/resources automatically after success.

## Required final adversarial campaign

Before claiming final action readiness, test at least:

- cross-user confirmation;
- cross-tenant/company/resource binding;
- forged browser/model permissions;
- forged upstream actor identity;
- altered confirmation arguments/fingerprint;
- duplicate confirmation;
- stale/lost action execution lease;
- late response after lease loss;
- ambiguous transport outcome → `UNCERTAIN`;
- kill-switch denial;
- prompt/tool-output injection attempting policy escape;
- safe observability with no grant/actor/credential/custody leakage.

Hard failure: any platform-caused unauthorized or duplicate external side effect.

## Emergency rollback

There is intentionally no public browser endpoint that mutates canonical action permissions or the kill switch.

Disable new governed executions by setting:

```text
ACADEMY_ACTIONS_ENABLED=false
```

and deploying/restarting with that configuration. Verify the exact deployed SHA and that capabilities/health no longer advertise executable actions.

Rollback rules:

- never auto-replay `UNCERTAIN`;
- never reuse an old idempotency claim for a new proposal;
- never weaken grants to work around policy denial;
- never expose a public/admin client-side permission or kill-switch authority;
- preserve custody/ledger/execution/evaluation/lease records for incident review.

## Incident triage

Capture only safe identifiers/state needed for diagnosis: opaque action ID, execution run ID, tool name, safe impact class/reason code, release SHA and timestamps. Do not copy raw credentials, grant/actor JSON, raw TRACTIAN payloads or private model reasoning.

If external outcome cannot be independently established, leave the action `UNCERTAIN`, disable automatic retry and require external-state reconciliation plus a new operator-reviewed proposal.

## Release claim discipline

Use the following distinctions precisely:

```text
action architecture implemented       ≠ end-user action accepted
governed transport smoke 5/5          ≠ full SECURITY-V1
action accepted by TRACTIAN           ≠ distributed exactly-once guarantee
source/CI green                        ≠ exact production SHA accepted
```

See [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md), [`SECURITY-MODEL.md`](SECURITY-MODEL.md) and the current dated progress note for the latest state.