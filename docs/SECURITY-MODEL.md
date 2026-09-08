# Active Security Model

**Status:** ACTIVE threat/trust-boundary model  
**Last reviewed:** 2026-09-08 BRT  
**Release scope:** hosted multi-user production with OpenRouter V14 composition and governed TRACTIAN action architecture

This document is a current threat model, **not** a claim that full hosted SECURITY-V1 is complete. Current OpenRouter V14 functional acceptance is failing before the first TRACTIAN tool call; the governed action transport has a controlled 5/5 production smoke but still requires the final adversarial/end-user campaign.

## 1. Current trust topology

```text
browser
→ Railway production-web
→ Neon managed auth + FastAPI
→ server-owned tenant/runtime context
→ Neon PostgreSQL/RLS
→ OpenRouter fixed-free V14 DecisionSource
→ AgentController
→ HarnessRunner / deterministic tool-policy boundary
→ supplied TRACTIAN reads
   OR governed action custody/confirmation/authorization/actor transport
→ evidence / terminal / action outcome
→ deterministic evaluator + independent verification
→ PostgreSQL safe projection
→ authenticated REST/SSE
```

### Assets to protect

- managed session identity;
- tenant-scoped runs/evidence/evaluation;
- provider/TRACTIAN/database credentials;
- action authorization grants, upstream actors, custody, fingerprints, idempotency and leases;
- evaluator/gold/blind research truth;
- exact release/provider/model/route provenance;
- USD0/no-paid-spillover boundary;
- safe grounded industrial conclusions/actions;
- provider/free-tier quota and product availability;
- durable run/action history and realtime ordering.

### Trust boundaries

1. browser ↔ public origin;
2. proxy ↔ managed auth/API;
3. API ↔ Neon Auth;
4. API ↔ PostgreSQL/RLS;
5. runtime ↔ OpenRouter;
6. model output ↔ deterministic controller/tool/policy;
7. API/HarnessRunner ↔ TRACTIAN read transport;
8. action proposal ↔ private custody/confirmation;
9. confirmed action ↔ server-owned authorization/upstream actor transport;
10. runtime/action trace ↔ post-runtime evaluator/verification;
11. private/raw state ↔ browser-safe observability;
12. free-tier operation ↔ paid boundary;
13. source/CI ↔ exact production deployment identity.

## 2. Current material threats

| Threat | Primary impact |
|---|---|
| forged/missing/impersonated managed session | unauthorized access |
| auth validation fan-out overload | availability/session instability |
| stale auth served during outage | unauthorized continued access |
| browser/model asserts organization/role/permission/resource authority | privilege/tenant escalation |
| RLS misconfiguration/BYPASSRLS role | cross-tenant disclosure |
| model invents/request internal IDs instead of grounded discovery | grounding/scope failure |
| missing asset label causes cross-scope speculation | tenant/grounding failure |
| one-sided comparison supports bilateral claim | false operational conclusion |
| baseline/data-quality evidence treated as fault proof | false diagnosis |
| exact successful tool repeats indefinitely | latency/quota/non-progress failure |
| prompt/tool-output injection controls policy | unsafe claim/action |
| malformed/unauthorized tool proposal bypasses boundary | unsafe execution |
| OpenRouter silently serves different model/route | provenance/cost/quality failure |
| provider fallback crosses into paid route | USD0 violation |
| truncated provider output is parsed as valid decision | unsafe/invalid tool authority |
| unbounded provider retry exhausts quota/availability | availability/cost-policy failure |
| redirect/credential leak at TRACTIAN/provider boundary | secret disclosure |
| action confirmation mutates arguments/authority | unauthorized side effect |
| model/browser mints action grants/upstream actor identity | privilege escalation |
| duplicate confirmation/action retry creates duplicate side effect | external safety failure |
| stale action owner publishes success after lease loss | false action state |
| ambiguous write automatically replays | duplicate external side effect |
| action kill switch bypassed | loss of operational control |
| raw grant/custody/provider/evaluator material reaches browser/logs | privacy/scientific/security leakage |
| SSE gap/reorder becomes source of truth | incorrect visible state |
| source/CI SHA differs from hosted runtime claim | false release provenance |
| unprotected branch allows unchecked mutation | supply-chain/release governance risk |

## 3. Identity / tenant mitigations

- managed session validated server-side;
- tenant/permissions derived server-side;
- browser authority headers/fields do not become canonical context;
- PostgreSQL scoped role + RLS independent of application/model logic;
- tenant negative acceptance and manipulated-session regressions;
- POST/non-read requests always fresh-validate managed session.

### Read-burst session resilience

```text
GET/HEAD
→ SHA-256 cookie digest
→ ≤2 s validated-context cache
→ bounded 256-entry cache + singleflight
→ Neon Auth on miss

POST/non-read
→ no read-cache authority
→ fresh Neon Auth validation
```

Security invariants:

- raw cookie never stored in read cache;
- no stale-on-error after expiration;
- invalid managed session → 401;
- temporary auth dependency failure → 503 + retry semantics;
- frontend exits/reconciles authenticated state on invalid/unavailable signals and focus/visibility return;
- RLS remains authoritative even if the application layer is buggy.

## 4. OpenRouter V14 provider mitigations

Exact production route:

```text
provider_id = openrouter
model_id    = nvidia/nemotron-3-super-120b-a12b:free
route_id    = openrouter.chat_completions.v1.fixed_free
allow_fallbacks = false
require_parameters = true
cost_policy = usd0-hard-gate
```

The adapter:

- sends strict JSON Schema for the current visible tool surface;
- requires exactly one assistant choice;
- requires exact served model when model metadata is present;
- requires `finish_reason=stop`;
- rejects provider-side `tool_calls`/`function_call`;
- rejects empty/non-text decision content;
- performs no automatic output repair, provider-side tool execution, hidden credential lookup or retry;
- preserves V13 grounding/response semantics.

### Current V14 failure is correctly fail-closed

A sanitized probe observed HTTP 200, exact pinned model and assistant content, but `finish_reason=length`. The adapter rejects the response and produces no TRACTIAN call. This is the desired safety behavior for incomplete structured output.

A later bounded comparison hit HTTP 429 on every tested variant. Do **not** respond by enabling fallback, accepting truncation or adding unbounded retries. Provider availability/quota must be measured and treated as an explicit functional dependency.

## 5. Model/tool/grounding authority

- model returns proposals, never execution authority;
- `AgentController` owns bounded control flow;
- `HarnessRunner` is the exclusive canonical real tool boundary;
- schema/argument/resource/policy/evidence checks are deterministic;
- internal IDs must come from authorized structured observations;
- human labels resolve only against authenticated fleet resources;
- missing labels close scope instead of expanding tenant/company;
- comparison evidence is resource-specific;
- response mode changes epistemic presentation, not permissions;
- exact successful duplicate calls are suppressed by operation + normalized argument/resource fingerprint;
- same-tool/different-argument point/resource drill-down remains allowed.

## 6. TRACTIAN read/network boundary

- canonical 18-operation registry;
- server-owned headers/credentials;
- bounded HTTPS transport, timeout and payload contracts;
- redirect/host restrictions;
- no model/provider direct TRACTIAN I/O;
- no blind write retry;
- safe normalized evidence before browser projection.

## 7. Governed consequential actions

Current architecture:

```text
model proposal
→ deterministic validation
→ private PostgreSQL custody
→ PENDING_CONFIRMATION
→ authenticated operator confirms existing opaque action_id
→ fresh tenant/user grant + resource binding + kill-switch validation
→ exact custodied fingerprint
→ persistent idempotency claim
→ non-transferable action execution lease/generation
→ server-owned upstream TRACTIAN actor
→ one bounded transport attempt
→ ACCEPTED | NOT_ACCEPTED | BLOCKED | UNCERTAIN
→ action evaluation + safe observability
```

### Server-owned invariants

The browser/model cannot supply canonical:

- action permission;
- organization/company/resource ownership;
- upstream TRACTIAN action actor identity;
- credentials;
- confirmation fingerprint;
- idempotency material;
- kill-switch state.

Incomplete server-owned action actor coverage is a boot blocker when actions are enabled. Actor bindings configured while actions are disabled are rejected.

### Current evidence and boundary

A production pre-deploy smoke proved the configured governed transport for all five canonical actions with HTTP 200 acceptance and no sensitive material recording.

This **does not** yet prove the full final hosted adversarial action contract. SECURITY-V1 must still exercise cross-user/tenant confirmation, altered arguments/fingerprint, duplicate confirmation, lease loss/stale owner, ambiguous transport, kill switch, prompt/tool injection and private-material leakage.

Never claim distributed exactly-once external side effects without cooperation from the external API. `UNCERTAIN` is the containment state when an external write outcome cannot be proven, and automatic replay remains forbidden.

## 8. Evidence / observability / evaluator isolation

- PostgreSQL durable run/event/evidence/evaluation truth;
- browser gets sanitized safe projection only;
- no raw credentials, provider bodies, grants, private custody, benchmark gold or hidden reasoning;
- evaluator is post-runtime and cannot feed private truth back into the agent;
- live provider mode requires model-call provenance;
- independent verification checks claims/evidence without becoming runtime authority;
- SSE/LISTEN-NOTIFY is delivery/wakeup, not authorization/correctness truth;
- durable cursor catch-up preserves authoritative order.

## 9. Cost / quota safety

- actual project cash-cost target/hard rule: USD0;
- no automatic paid fallback;
- exact provider/model/route provenance recorded safely;
- rate-limit/quota exhaustion causes explicit degraded/failure state rather than spend;
- runtime retry behavior must remain bounded and evidence-driven;
- paid infrastructure may not be silently enabled to strengthen a delivery claim.

## 10. Release / supply-chain governance

- backend artifact/configured/runtime SHA agreement required for production claims;
- frontend/backend/supplied-API identities tracked separately;
- exact candidate CI and exact hosted promotion are separate gates;
- historical acceptance SHAs remain immutable evidence;
- latest observed GitHub metadata still reports `main.protected=false` with required status-check enforcement off.

Branch protection is therefore a current governance gap, even though the repository has a stable required CI gate.

## 11. Evidence already passed for current scope

- hosted managed auth and tenant/RLS boundaries in tested scope;
- task-driven frontend/product serving;
- V13 grounding/session/condition/data-quality hardening historical evidence;
- independent verification V1 implementation/regressions;
- exact-success duplicate-call suppression regressions;
- controlled production governed-write smoke 5/5;
- OpenRouter exact-model HTTP-200 response-shape probe without raw material recording;
- V14 fail-closed behavior on `finish_reason=length`;
- production release identity and health for backend `561168755...`.

## 12. Current SECURITY-V1 / production gaps

Before broad final security/production claims:

- make the authenticated V14 path functionally green without weakening provider/cost/safety gates;
- run full current-topology action adversarial campaign;
- broaden provider/TRACTIAN malformed/failure/injection scenarios;
- concurrent session/resource-exhaustion campaign;
- load/soak and quota/saturation characterization;
- known-state restore drill and measured recovery bounds;
- external availability monitoring if required for the final operational claim;
- branch-protection enforcement;
- final exact-SHA freeze/reproduction.

## 13. Change trigger

Revisit this model after any provider/model/route change, auth/tenant/storage change, action grant/actor model change, browser data-class expansion, major topology change, security incident, release-governance change or adaptive runtime policy that influences tool/resource/action behavior.

Security findings follow root [`SECURITY.md`](../SECURITY.md).