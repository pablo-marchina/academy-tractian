# Active Security Model

**Status:** ACTIVE threat/trust-boundary model  
**Last reviewed:** 2026-09-07 BRT  
**Release scope:** hosted read-only Release 0 V13

This is not a claim that the full final SECURITY-V1 campaign is complete.

## 1. What are we working on?

```text
browser
→ Railway production-web
→ Neon managed auth + Railway FastAPI
→ server-owned tenant context
→ Neon PostgreSQL/RLS
→ Cloudflare provisional provider
→ V13 grounded DecisionSource/controller
→ typed TRACTIAN reads
→ evidence/terminal/response_mode/evaluator
→ authenticated REST/SSE
```

### Assets to protect

- user/session identity;
- tenant-scoped runs/evidence/evaluation;
- provider/TRACTIAN/database credentials;
- private action custody/idempotency/authorization material;
- evaluator/gold/blind research truth;
- release/provenance identity;
- USD0/no-paid-spillover boundary;
- safe grounded customer outputs;
- availability/quota within free-tier limits.

### Trust boundaries

1. browser ↔ public origin;
2. web proxy ↔ managed auth/API;
3. API ↔ Neon Auth;
4. API ↔ PostgreSQL/RLS;
5. runtime ↔ model provider;
6. model output ↔ deterministic controller/tool/policy;
7. API ↔ TRACTIAN;
8. runtime ↔ post-runtime evaluator;
9. private/raw state ↔ browser-safe observability;
10. free-tier operation ↔ paid boundary.

## 2. What can go wrong?

| Threat | Primary impact |
|---|---|
| forged/missing/impersonated session | unauthorized access |
| auth validation fan-out overloads managed identity | availability/session instability |
| stale auth served during outage | unauthorized continued access |
| browser asserts organization/role/permission | privilege/tenant escalation |
| RLS misconfiguration/BYPASSRLS role | cross-tenant disclosure |
| model invents or asks user for internal resource ID | grounding/UX failure; potential unsafe resource reference |
| missing explicit asset label triggers cross-scope speculation | tenant/grounding failure |
| model compares assets with evidence for only one | unsupported operational conclusion |
| baseline/data quality treated as fault proof | false diagnosis |
| model attempts unknown/malformed/unauthorized tool | safety bypass |
| prompt/tool output injection controls policy | unsafe action/claim |
| redirect/credential leak at TRACTIAN boundary | secret disclosure |
| provider/model/route silently substituted | provenance/cost/quality failure |
| automatic paid fallback | USD0 violation |
| raw upstream/evaluator/private material reaches browser | privacy/scientific leakage |
| SSE reorder/gap treated as truth | incorrect visible state |
| stale runtime/action owner finalizes after lease loss | incorrect/duplicate state |
| consequential action duplicated/replayed | external side effect |
| release SHA decoupled from artifact | false deployment provenance |

## 3. Identity / tenant mitigations

- managed session validated server-side;
- tenant/permissions server-owned;
- browser authority headers ignored/rejected;
- PostgreSQL scoped role + RLS independent boundary;
- hosted tenant negative acceptance;
- impersonated managed sessions rejected.

### Read-burst session resilience

Current #207 contract:

```text
GET/HEAD
→ cookie digest
→ ≤2 s validated-context cache
→ bounded LRU (256)
→ striped singleflight
→ Neon Auth when cache miss

POST/non-read
→ always fresh Neon Auth validation
```

Security invariants:

- raw cookie never stored in read cache;
- cache digest is SHA-256;
- expired entry is deleted and never stale-on-error;
- managed auth redirect not followed with cookie;
- invalid 401/403 → API 401;
- unexpected/unavailable identity response → API 503 + Retry-After;
- frontend invalid signal exits authenticated state;
- frontend unavailable signal exposes retryable protected state;
- focus/visibility return reconciles the session.

## 4. Model/tool/grounding authority

- provider returns typed decisions/proposals, not execution authority;
- `HarnessRunner` is exclusive real tool boundary;
- schema/policy/evidence gates deterministic;
- bounded turns/timeouts/payloads;
- no hidden provider fallback;
- human-readable asset labels resolve only against structured IDs observed from authenticated company/fleet responses;
- comparison evidence is required per selected asset;
- missing label closes the authorized tool path rather than expanding scope;
- response-mode semantics have no permission effect.

## 5. TRACTIAN network

- canonical 18-operation registry;
- server-owned credentials/headers;
- HTTPS/base URL restrictions;
- bounded timeout/request/response sizes;
- redirects disabled;
- no blind write retry;
- Release 0 external action execution disabled.

## 6. Evidence / observability

- durable safe event projection;
- raw sensitive/private/gold/chain-of-thought fields excluded;
- evaluator post-runtime;
- SSE wake-up not authorization/correctness truth;
- durable cursor catch-up.

Repeated tool names must not be flagged as loops without considering arguments/resource. Legitimate asset→point drill-down is allowed; exact same-resource/args repetition without useful evidence remains a reliability concern.

## 7. Cost

- USD0 hard eligibility rule;
- no automatic paid fallback;
- quota exhaustion fails/degrades rather than spends;
- provider/model/route identity explicit.

## 8. Release provenance

- baked/configured/runtime backend identity cross-check;
- exact-SHA promotion evidence;
- frontend/backend/supplied-API identities tracked independently;
- original acceptance SHA remains historical when runtime later hardens.

## 9. Evidence already passed for current scope

- original hosted managed-auth/two-user tenant acceptance;
- #207 managed-session regression suite + post-deploy tested burst without recurrence in tested scope;
- V13 explicit asset grounding/data-quality/missing-resource live retests;
- V13 blocking structural evaluations all pass for the three final runs;
- real provider + typed TRACTIAN reads;
- exact backend release identity;
- required CI/Playwright on the relevant backend/frontend heads;
- external action calls remain zero in Release 0 live testing.

## 10. Still required before broader claims

- full SECURITY-V1 hosted campaign;
- larger session/concurrency/resource-exhaustion campaign;
- provider/TRACTIAN/DB failure campaign at final topology;
- restore/recovery evidence;
- real action adversarial campaign before enabling actions;
- final provider tournament;
- broader semantic/anti-hallucination/false-precision live testing.

## 11. Change trigger

Revisit this model after new external dependency/provider, auth/tenant/storage change, consequential action enablement, new browser data class, major topology change, security incident/finding or adaptive policy that influences tool/resource behavior.

Security findings follow root [`SECURITY.md`](../SECURITY.md).