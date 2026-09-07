# Active Security Model

**Status:** ACTIVE threat/trust-boundary model  
**Last reviewed:** 2026-09-07 BRT  
**Release scope:** hosted Release 0 V13 + governed action path enabled; five-action live acceptance incomplete

This is not a claim that the full final SECURITY-V1 campaign is complete.

## 1. What are we protecting?

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
→ governed action custody/confirmation/authorization/idempotency/lease
→ server-owned vendor actor boundary
→ typed TRACTIAN action attempt
→ authenticated REST/SSE
```

### Assets to protect

- user/session identity;
- tenant-scoped runs/evidence/evaluation;
- provider/TRACTIAN/database credentials;
- private action custody/idempotency/authorization material;
- server-owned upstream TRACTIAN actor mappings;
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
7. product requester identity ↔ server-owned action authorization;
8. local action authorization ↔ vendor actor selection;
9. API ↔ TRACTIAN network boundary;
10. runtime ↔ post-runtime evaluator;
11. private/raw state ↔ browser-safe observability;
12. free-tier operation ↔ paid boundary.

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
| confirmation payload tries to replace custodied action arguments | action integrity failure |
| duplicate/replayed consequential action | external side effect |
| ambiguous external write auto-retried | duplicate/unknown side effect |
| browser/model selects a privileged upstream TRACTIAN actor | confused-deputy / privilege escalation |
| local grant permission does not match vendor actor permission | false readiness / upstream denial |
| missing actor mapping silently falls back to a more privileged actor | privilege escalation |
| redirect/credential leak at TRACTIAN boundary | secret disclosure |
| provider/model/route silently substituted | provenance/cost/quality failure |
| automatic paid fallback | USD0 violation |
| raw upstream/evaluator/private material reaches browser | privacy/scientific leakage |
| SSE reorder/gap treated as truth | incorrect visible state |
| stale runtime/action owner finalizes after lease loss | incorrect/duplicate state |
| release SHA decoupled from artifact | false deployment provenance |
| Railway redeploy reuses stale snapshot and is treated as fresh configuration proof | false operational evidence |

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
- `HarnessRunner` is exclusive canonical tool boundary;
- schema/policy/evidence gates deterministic;
- bounded turns/timeouts/payloads;
- no hidden provider fallback;
- human-readable asset labels resolve only against structured IDs observed from authenticated company/fleet responses;
- comparison evidence is required per selected asset;
- missing label closes the authorized tool path rather than expanding scope;
- response-mode semantics have no permission effect.

## 5. Governed action security boundary

Consequential action execution is now enabled in the production composition, but every action remains independently gated.

Required local chain:

```text
authenticated requester
→ tenant-aware server-owned grant
→ canonical permission
→ exact resource/company binding
→ exact private custody/fingerprint
→ explicit confirmation of existing action
→ persistent idempotency claim
→ active execution lease/generation
→ host-owned kill switch
→ vendor actor resolution
→ one typed upstream attempt
→ explicit accepted=true required for ACCEPTED
```

The browser/model cannot provide canonical permissions, grants, resource ownership, idempotency keys, action arguments at confirmation time, kill-switch state or vendor actor identity.

### Vendor actor separation

The local authenticated requester and upstream TRACTIAN actor are different security principals.

The supplied runtime authenticates action context with `x-user-id` and checks endpoint permissions. Live inspection showed separate upstream actors in the tested company scope for `action_low` versus `action_high + escalate`.

Target invariant:

```text
(company_id, required_permission)
→ exactly one server-owned TRACTIAN actor
```

The actor is selected only after local authorization. Missing or ambiguous mappings must fail closed. Never fallback to a more privileged actor.

The corrective routing implementation is still in progress; therefore complete five-action live authorization is not currently a security/readiness claim.

### Ambiguous writes

`UNCERTAIN` is a containment state. A write with unknown external outcome is not automatically retried. A new attempt requires external reconciliation and a new operator-reviewed proposal.

## 6. TRACTIAN network

- canonical 18-operation registry;
- server-owned credentials/headers;
- HTTPS/base URL restrictions;
- bounded timeout/request/response sizes;
- redirects disabled;
- canonical caller-bound `x-user-id` validation at the base transport;
- governed action adapter may replace only the vendor actor at the final trusted boundary once a server-owned mapping is authorized;
- no blind write retry;
- upstream response must explicitly confirm acceptance before local `ACCEPTED`.

## 7. Production write-smoke containment

PR #213 added a manual-only production validation module that contains no credentials/resource IDs/grants in source. It requires five executable governed capabilities and then exercises all five canonical actions through the production transport.

The fresh live validation failed on `update_asset_config` with HTTP 403 / `accepted=false` and aborted the deployment before promotion. The prior healthy deployment remained serving.

This is evidence that:

- the live write gate can detect a vendor authorization mismatch;
- failing validation does not need to weaken the local security policy;
- production can remain available on the prior healthy release;
- capability advertisement is not sufficient evidence of vendor acceptance.

It is **not** evidence that all five actions work yet.

## 8. Evidence / observability

- durable safe event projection;
- raw sensitive/private/gold/chain-of-thought fields excluded;
- action custody/grants/upstream actor mappings excluded from browser projections;
- evaluator post-runtime;
- SSE wake-up not authorization/correctness truth;
- durable cursor catch-up.

Repeated tool names must not be flagged as loops without considering arguments/resource. Legitimate asset→point drill-down is allowed; exact same-resource/args repetition without useful evidence remains a reliability concern.

## 9. Cost

- USD0 hard eligibility rule;
- no automatic paid fallback;
- quota exhaustion fails/degrades rather than spends;
- provider/model/route identity explicit.

## 10. Release provenance

- baked/configured/runtime backend identity cross-check;
- exact-SHA promotion evidence;
- frontend/backend/supplied-API identities tracked independently;
- generic Railway redeploy is not proof of fresh source/configuration because it may reuse a captured snapshot;
- original acceptance SHA remains historical when runtime later hardens.

## 11. Evidence already passed for current scope

- original hosted managed-auth/two-user tenant acceptance;
- #207 managed-session regression suite + post-deploy tested burst without recurrence in tested scope;
- V13 explicit asset grounding/data-quality/missing-resource live retests;
- V13 blocking structural evaluations pass for the recorded read runs;
- real provider + typed TRACTIAN reads;
- exact backend release-identity controls;
- PR #213 required CI/clean-clone/Playwright/action-lease/horizontal-runtime contracts green;
- governed actions can boot enabled under server-owned grants;
- five-action validation can fail closed before replacing healthy production;
- live `update_asset_config` vendor authorization mismatch was surfaced as HTTP 403 instead of being misreported as success.

## 12. Still required before broader claims

- finish and review server-owned upstream actor routing;
- adversarial tests proving browser/model cannot select/upgrade vendor actors;
- fail-closed tests for missing/ambiguous company+permission mappings;
- five-action live smoke with 5/5 explicit acceptance;
- normal product confirmation-path hosted evidence after routing correction;
- full SECURITY-V1 hosted campaign;
- larger session/concurrency/resource-exhaustion campaign;
- provider/TRACTIAN/DB failure campaign at final topology;
- restore/recovery evidence;
- final provider tournament;
- broader semantic/anti-hallucination/false-precision live testing.

## 13. Change trigger

Revisit this model after any auth/tenant/storage change, vendor-actor routing change, consequential-action policy/grant change, new external dependency/provider, new browser data class, major topology change, security incident/finding or adaptive policy that influences tool/resource behavior.

Security findings follow root [`SECURITY.md`](../SECURITY.md). Dated production evidence is in [`progress/2026-09-07-production-governed-actions-ux-and-validation.md`](progress/2026-09-07-production-governed-actions-ux-and-validation.md).