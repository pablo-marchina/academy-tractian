# 2026-09-07 — Production UX, governed actions and live validation

**Record type:** append-only progress/evidence note  
**Date:** 2026-09-07 BRT  
**Canonical release branch at record time:** `release/production-final`  
**Current merged backend/runtime source:** `d43644d22df8e3ee5bb5a1532bbea3512c3a7ac0`

This note records the material progress completed during the 2026-09-07 production hardening conversation. It intentionally separates implementation, CI evidence, hosted deployment evidence, failed live evidence, corrective work and the final prospective five-action acceptance evidence.

## 1. Frontend and authentication progress

The public product remains hosted on Railway and uses the task-driven frontend architecture documented in `ACTIVE-PROJECT-STATUS.md` and `ARCHITECTURE.md`.

Material frontend/auth milestones during this hardening sequence include:

- progressive-disclosure UX work that moved the product away from exposing engineering depth as the default journey;
- task-driven navigation centered on Home, result/evidence drill-down, Analyses and Technical surfaces;
- managed-session resilience hardening in PR #207, including bounded reuse for already validated read sessions, fresh validation for mutations, explicit invalid-vs-unavailable auth states, and browser reconciliation on focus/visibility return;
- explicit asset-label grounding and evidence/stopping fixes through PRs #208 and #210;
- browser acceptance and clean-clone reproduction remained green after the later governed-action work.

A user review also identified continuing UX debt: the frontend can still feel visually dense and over-structured. The current design rule is therefore stronger than simple progressive disclosure:

> each screen should answer one primary user question, with specialist/technical depth outside the normal journey.

This UX simplification direction is a design/development target, not a claim of completed human usability validation. Automated browser tests and accessibility-oriented implementation checks are not substitutes for representative-user testing.

## 2. Governed consequential actions promoted in code — PR #211

PR #211 promoted governed execution support for all five canonical TRACTIAN action operations.

Merge commit:

```text
1a1e7139bfa0361416120b3f21937c4048b5bb1f
```

Canonical action contract:

| Tool | Upstream operation | Required permission |
|---|---|---|
| `reprocess_analysis` | POST `/analyses/{analysis_id}/reprocess` | `action_low` |
| `request_specialist_analysis` | POST `/analyses/{analysis_id}/request-specialist` | `action_low` |
| `update_asset_config` | PATCH `/assets/{asset_id}` | `action_high` |
| `request_retraining` | POST `/models/{model_id}/request-retraining` | `action_high` |
| `escalate_case` | POST `/cases/{case_id}/escalate` | `escalate` |

The production action architecture preserves these invariants:

- canonical permissions are server-owned;
- tenant/company/resource authority is server-owned;
- browser/model output cannot grant permission or resource authority;
- proposals are privately custodied before execution;
- confirmation is for the exact existing action, not a new browser-supplied payload;
- action fingerprint and idempotency material are server-owned;
- external I/O is attempted only after the deterministic safety boundary passes;
- action execution is protected by durable lease/generation ownership;
- ambiguous write outcomes become `UNCERTAIN` and are not retried automatically;
- `ACCEPTED` is only used when the external API explicitly confirms acceptance.

The action state vocabulary remains:

```text
PENDING_CONFIRMATION
CONFIRMED
EXECUTING
ACCEPTED
BLOCKED
NOT_ACCEPTED
UNCERTAIN
```

## 3. Production configuration and initial deployment

The `production-api` Railway service was configured for the governed write path with live provider execution, live TRACTIAN transport, `ACADEMY_ACTIONS_ENABLED=true`, a minimum-scope server-owned authorization grant document and no canonical permission/resource authority supplied by the browser/model.

Real secret/grant/user/resource values are intentionally excluded from this record.

Deployment for PR #211:

```text
Railway deployment: 9732a2cb-c321-4fcf-83f8-c6f87eeab06a
source SHA:        1a1e7139bfa0361416120b3f21937c4048b5bb1f
status:            SUCCESS
```

This proved that the governed-action composition could boot and serve under the production configuration. It did **not** by itself prove that all five upstream writes were accepted.

## 4. Auditable five-action production smoke — PR #213

PR #213 added the manual-only production smoke module:

```text
src/academy_tractian/governed_write_transport_smoke.py
```

PR #213 merge commit:

```text
3545d75c00ca30419e0f47e8b1950aa50cbbf462
```

The smoke contains no production credentials, tenant IDs, resource IDs or authorization grants in source. Runtime targets and credentials are supplied only through server-owned environment variables.

Before attempting writes it requires the hosted capability endpoint to report exactly five canonical actions, exactly five executable actions, `action_execution.enabled=true`, `action_execution.mode=GOVERNED_CONFIRMATION` and the governed action path enabled.

It then binds and sends all five canonical action requests through the same canonical binder and production TRACTIAN transport used by the application. An action passes only when:

```text
HTTP status ∈ {200, 201, 202}
AND response.accepted == true
```

Safe output contains only action name, HTTP status, acceptance boolean and aggregate capability state. Credentials, resource IDs and upstream response bodies are not printed.

## 5. CI evidence for PR #213

Required-gate workflow run:

```text
34164123263
```

Green jobs included standalone production wheel, PostgreSQL action execution lease/stale-result fencing, production runtime regression, Railway IaC, remote production image/source-drift checks, horizontal PostgreSQL runtime/handoff/recovery, clean-clone full product reproduction, Chromium full-product Playwright and the final `required-gate`.

This was strong source/artifact regression evidence. It was not equivalent to upstream live write acceptance.

## 6. Hosted deployment of the smoke-capable release

PR #213 deployment:

```text
Railway deployment: 2cbc4215-f59a-4947-8691-0d4776458445
source SHA:        3545d75c00ca30419e0f47e8b1950aa50cbbf462
status:            SUCCESS
```

A later Railway `redeploy` reused an older captured snapshot. Because a redeploy is not proof that newly edited service configuration was materialized, that run was **not** accepted as evidence that the intended five-action pre-deploy smoke had executed.

To force a fresh configuration snapshot, an operational validation marker was changed and a new deployment was created.

## 7. Decisive first live write result: fail-closed HTTP 403

Fresh validation deployment:

```text
5ba36471-776c-4e15-919b-56e2da216b74
status: FAILED in pre-deploy by design
```

The failure was:

```text
RuntimeError: governed write transport smoke failed for update_asset_config: http_403:accepted_false
```

This was simultaneously a successful safety outcome and a failed capability proof:

- the real validation gate ran;
- it refused to promote a deployment when one canonical write was not accepted;
- the prior healthy production deployment remained serving;
- the local grant was not widened to hide the vendor denial.

At that point the correct claim was: governed actions were implemented/configured, but 5/5 upstream acceptance had **not** yet been proven.

## 8. Root cause: local product identity and TRACTIAN actor identity are different principals

An investigation reconstructed the immutable supplied TRACTIAN runtime and inspected its authorization contract.

The supplied API resolves the acting user from `x-user-id` and applies endpoint-specific permission checks. For the production company scope under test, the supplied runtime has distinct upstream actors:

- one actor with `read + action_low`;
- a different actor with `read + action_high + escalate`.

Therefore one product-authenticated user identifier cannot simply be forwarded as the TRACTIAN actor for all five action families.

The discovered trust requirement was:

```text
local authenticated product user
  → tenant authorization, resource scope, confirmation, custody, idempotency and audit

server-owned TRACTIAN action actor
  → vendor-side execution identity only
  → selected after local authorization
  → selected by company + canonical required permission
```

Required invariant:

```text
(company_id, required_permission) -> exactly one server-owned upstream actor
```

The browser, model and confirmation payload must never choose or submit that actor. Missing/ambiguous actor bindings must fail closed.

## 9. Corrective implementation — PR #214

PR #214 implemented the identity separation without weakening local authorization.

PR head:

```text
1b63898eda14c04fa5c245c75a9d719ea138816f
```

Merge commit:

```text
d43644d22df8e3ee5bb5a1532bbea3512c3a7ac0
```

Main implementation properties:

- `ConfiguredServerOwnedUpstreamActionActorSource` parses immutable server-owned company+permission actor bindings;
- `ServerOwnedUpstreamActionActorTransport` rewrites only canonical ACTION calls at the final vendor boundary;
- READ calls preserve the original local requester identity and are never mapped to privileged action actors;
- the local action principal is re-resolved before actor selection;
- a canonical action must have exactly one expected action permission;
- the local principal must hold that permission before actor mapping;
- missing actor binding fails before upstream I/O;
- actor documents may bind only `action_low`, `action_high` or `escalate` and must be source-owned;
- incomplete actor coverage for any active production action grant blocks production boot;
- browser/model/pending action/confirmation payload cannot select the actor;
- the production smoke now uses the exact same actor-routing boundary as normal action execution.

The new server-owned environment contract is:

```text
ACADEMY_TRACTIAN_ACTION_ACTORS_JSON
```

Real actor values remain secret operational configuration and are intentionally not recorded here.

## 10. PR #214 validation

PR #214 required head workflows all completed successfully, including:

```text
final-ci-required                       SUCCESS
clean-clone-full-product-reproduction  SUCCESS
production-runtime                     SUCCESS
frontend-provider-free                 SUCCESS
observability-api-provider-free        SUCCESS
eval-driven-development-provider-free  SUCCESS
final-handoff-acceptance-audit         SUCCESS
final-delivery-provider-free-reproduction SUCCESS
repository-branch-hygiene              SUCCESS
```

The final required-gate workflow for the head was green before merge.

This proves the corrective source/regression contract, including parameterized coverage for all five canonical actions, read identity preservation, missing local permission, missing upstream binding and rejection of forged/non-server-owned actor grants.

## 11. Production promotion of PR #214

The production branch advanced to:

```text
d43644d22df8e3ee5bb5a1532bbea3512c3a7ac0
```

Current successful Railway deployment:

```text
b1259276-0c1b-425b-bf81-ab9a748a5089
status: SUCCESS
source: d43644d22df8e3ee5bb5a1532bbea3512c3a7ac0
```

The service passed its healthcheck and continued serving after the pre-deploy write validation.

## 12. Final live five-action smoke — PASS 5/5

The decisive hosted pre-deploy output used:

```text
governed-write-production-smoke-v2
```

Capability state:

```text
actions:                       5
executable_actions:            5
governed_action_path_enabled:  true
mode:                          GOVERNED_CONFIRMATION
HTTP capability status:        200
```

Action results:

| Tool | HTTP | `accepted` |
|---|---:|---|
| `reprocess_analysis` | 200 | `true` |
| `request_specialist_analysis` | 200 | `true` |
| `update_asset_config` | 200 | `true` |
| `request_retraining` | 200 | `true` |
| `escalate_case` | 200 | `true` |

Safe-output assertions from the same smoke:

```text
credentials_recorded:    false
local_user_ids_recorded: false
upstream_user_ids_recorded: false
resource_ids_recorded:   false
response_bodies_recorded:false
status:                  PASS
```

This prospectively supersedes the earlier 403 for the **current source/configuration** while preserving that failure as historical evidence that motivated the fix.

Current action claim is therefore:

> all five canonical governed TRACTIAN action endpoints were exercised in the production pre-deploy smoke for source `d43644d...` and each returned HTTP 200 with `accepted=true` through the same server-owned actor-routing boundary used by production action execution.

This is a strong live acceptance claim for the tested release/configuration, not a mathematical guarantee that an external service can never fail in the future.

## 13. Truth table after PR #214

| Claim | State on 2026-09-07 |
|---|---|
| remote hosted product | PROVEN |
| managed auth + tenant isolation | IMPLEMENTED / tested in current scope |
| provider + TRACTIAN read path | PROVEN for exercised reads |
| five canonical action operations exist | PROVEN |
| custody/confirmation/idempotency/lease architecture | PROVEN by tests/CI |
| governed actions enabled in production composition | PROVEN |
| server-owned company+permission vendor actor routing implemented | PROVEN in merged source |
| incomplete actor coverage blocks boot | PROVEN by implementation/tests |
| current #214 source deployed successfully | PROVEN |
| all five canonical writes accepted in hosted pre-deploy smoke | **PROVEN 5/5 for current tested release/config** |
| previous `update_asset_config` 403 occurred | PROVEN historical evidence |
| failed validation can preserve healthy production | PROVEN |
| browser/model can select vendor actor | FALSE by current contract/tests |
| actions can be guaranteed to succeed forever | impossible claim; external dependencies can fail |

## 14. Reliability guarantee boundary

The correct production guarantee is not “every external action succeeds forever.” The controllable contract is:

- deterministic local authorization and tenant/resource scope;
- exact operator confirmation;
- server-owned company+permission actor routing;
- boot failure on incomplete active actor coverage;
- one-shot/idempotent write custody;
- active lease/generation ownership;
- explicit upstream acceptance required for `ACCEPTED`;
- fail closed on missing permission, actor mapping, release drift or unhealthy dependency;
- no invented success;
- no blind retry after an ambiguous write;
- deployment validation can prevent a failing candidate from replacing healthy production.

The 5/5 smoke establishes current endpoint/configuration acceptance. It does not eliminate future network, authorization, dependency, quota or vendor failures.

## 15. Remaining action evidence beyond 5/5 transport acceptance

The transport-level five-action gate is now closed for the current release. Broader final-production evidence can still include:

1. normal user-facing proposal → confirmation → persisted action-state execution for representative actions;
2. repeated duplicate-confirmation/idempotency rejection under hosted conditions;
3. explicit `UNCERTAIN` recovery/drill evidence without blind retry;
4. tenant/cross-user confirmation negatives under the final topology;
5. full SECURITY-V1 action-actor confused-deputy/adversarial campaign;
6. provider/TRACTIAN/DB failure campaigns and restore/recovery evidence.

These are broader hardening gates, not reasons to deny the now-observed 5/5 transport acceptance.

## 16. Documentation rule after this sequence

Active documentation should now say:

- the original Release 0 acceptance was historically read-only;
- governed execution was promoted later through #211;
- #213 added the auditable five-write gate;
- the first real smoke exposed a 403 and safely aborted promotion;
- #214 separated local requester identity from server-owned vendor actor identity;
- the current `d43644d...` production deployment passed the five-action smoke 5/5;
- no document should turn that tested acceptance into a promise of perpetual external availability/reliability;
- frozen historical records should continue to preserve the earlier read-only and 403 states exactly as they occurred.