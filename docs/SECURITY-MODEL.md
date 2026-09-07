# Active Security Model

**Status:** ACTIVE threat/trust-boundary model  
**Last reviewed:** 2026-09-06 BRT  
**Release scope:** promoted read-only Release 0

This document follows the practical four-question threat-model loop: **What are we working on? What can go wrong? What are we doing about it? Did we do a good enough job?**

It is not a claim that the full final SECURITY-V1 campaign is complete.

## 1. What are we working on?

A remote multi-user industrial agent/evaluation product:

```text
browser
→ Railway public frontend
→ managed Neon Auth + Railway FastAPI
→ server-owned tenant context
→ Neon PostgreSQL/RLS
→ Cloudflare provisional provider
→ typed TRACTIAN reads
→ evidence/terminal/evaluator
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
- safe customer outputs;
- availability/quota within free-tier limits.

### Trust boundaries

1. browser ↔ public origin;
2. public web proxy ↔ managed auth/API;
3. API ↔ Neon Auth;
4. API ↔ PostgreSQL/RLS;
5. runtime ↔ model provider;
6. model output ↔ deterministic controller/tool/policy;
7. API ↔ TRACTIAN external system;
8. runtime state ↔ post-runtime evaluator;
9. private/raw state ↔ browser-safe observability;
10. free-tier operation ↔ paid cost boundary.

## 2. What can go wrong?

| Threat | Primary impact |
|---|---|
| forged/missing/impersonated session | unauthorized access |
| browser asserts organization/role/permission | privilege/tenant escalation |
| RLS misconfiguration/BYPASSRLS role | cross-tenant disclosure |
| model attempts unknown/malformed/unauthorized tool | safety boundary bypass |
| prompt/tool output injection tries to control policy | unsafe action/claim |
| redirect/credential leak at TRACTIAN boundary | secret disclosure |
| provider/model/route silently substituted | provenance/cost/quality failure |
| automatic paid fallback/quota overage | violates USD0 hard constraint |
| raw upstream/evaluator/private material reaches browser | privacy/scientific leakage |
| SSE reorder/gap treated as truth | incorrect visible state |
| stale runtime/action owner finalizes after lease loss | incorrect/duplicate state |
| consequential action duplicated/replayed | external side effect |
| release SHA decoupled from artifact | false deployment provenance |
| resource exhaustion | availability/quota loss |

## 3. What are we doing about it?

### Identity / tenant

- managed session validated server-side;
- tenant/permissions are server-owned;
- browser authority headers ignored/rejected as authority;
- PostgreSQL scoped role + RLS independent boundary;
- hosted two-user REST/SSE negative acceptance.

### Model/tool authority

- provider returns typed decisions/proposals, not raw execution authority;
- `HarnessRunner` is exclusive real tool boundary;
- schema/policy/evidence gates are deterministic;
- bounded turns/timeouts/payloads;
- no hidden provider fallback.

### TRACTIAN network

- canonical 18-operation registry;
- server-owned credentials/headers;
- HTTPS/base URL restrictions;
- bounded timeout/request/response sizes;
- redirects disabled;
- no blind write retry.

### Evidence / observability

- durable safe event projection;
- raw sensitive/private/gold/chain-of-thought fields excluded;
- evaluator runs post-runtime;
- SSE wake-up not authorization/correctness truth;
- durable cursor supports catch-up.

### Consequential actions

Release 0 external action execution is disabled. The codebase additionally has private custody, explicit confirmation, idempotency and non-transferable lease/fencing design for future promotion.

### Cost

- USD0 is a hard eligibility rule;
- no automatic paid fallback;
- quota exhaustion should fail/degrade rather than spend;
- provider selection and route identity are explicit.

### Release provenance

- baked/configured/runtime backend identity cross-check;
- hosted promotion requires exact expected SHA.

## 4. Did we do a good enough job?

### Evidence already passed for Release 0 scope

- hosted managed auth path;
- two-user/tenant REST/SSE negatives;
- forged browser authority negatives;
- real provider + real typed TRACTIAN read;
- safe terminal modes;
- exact backend release identity;
- provider-free adversarial/regression suite;
- full Playwright/required CI on current UX baseline;
- external action calls = 0 in Release 0 acceptance.

### Still required before broader final claims

- full SECURITY-V1 hosted campaign;
- resource-exhaustion/load boundary;
- provider/TRACTIAN/DB failure campaign at final topology;
- restore/recovery evidence;
- governed real action adversarial campaign before enabling actions;
- final provider tournament;
- any additional privacy/security checks introduced by new features.

## 5. Change trigger

Revisit this model after:

- new external dependency/provider;
- auth/tenant/storage change;
- consequential action enablement;
- new data class exposed to browser;
- major deployment/topology change;
- security incident/finding;
- new adaptive policy that influences tool/resource behavior.

Security findings should follow root [`SECURITY.md`](../SECURITY.md).