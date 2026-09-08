# Active Security Model

**Status:** ACTIVE threat/trust-boundary model  
**Last reviewed:** 2026-09-08 BRT  
**Release scope:** hosted read-only Release 0; provider-selection research remains non-production  
**Provider state:** [`PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](PROVIDER-QUALIFICATION-STATUS-2026-09-08.md)

This is not a claim that the full final SECURITY-V1 campaign is complete.

## 1. What are we protecting?

```text
browser
→ Railway production-web
→ managed auth + production-api
→ server-owned tenant context
→ Neon PostgreSQL/RLS
→ provisional production provider
→ grounded DecisionSource/controller
→ typed TRACTIAN reads
→ evidence/terminal/response_mode/evaluator
→ authenticated REST/SSE
```

Provider research is a separate trust/experiment path:

```text
frozen benchmark inputs
→ disposable QA runner
→ external provider API
→ sanitized structural result
→ evaluation/hard gates
→ no automatic production promotion
```

### Assets to protect

- user/session identity;
- tenant-scoped runs/evidence/evaluation;
- provider/TRACTIAN/database credentials;
- private action custody/idempotency/authorization material;
- evaluator/gold/blind research truth;
- frozen benchmark population/rubric integrity;
- release/provider provenance identity;
- no-hidden-paid-fallback/cost boundary;
- safe grounded customer outputs;
- availability/quota within allowed account limits.

### Trust boundaries

1. browser ↔ public origin;
2. web proxy ↔ managed auth/API;
3. API ↔ Neon Auth;
4. API ↔ PostgreSQL/RLS;
5. production runtime ↔ production provider;
6. provider output ↔ deterministic controller/tool/policy;
7. API ↔ TRACTIAN;
8. runtime ↔ post-runtime evaluator;
9. private/raw state ↔ browser-safe observability;
10. free/allowed operation ↔ paid boundary;
11. frozen research inputs ↔ candidate provider;
12. provider-research result ↔ production-promotion authority.

## 2. What can go wrong?

| Threat | Primary impact |
|---|---|
| forged/missing session | unauthorized access |
| auth fan-out overload | availability instability |
| stale auth served during outage | unauthorized continued access |
| browser asserts tenant/role | privilege escalation |
| RLS misconfiguration | cross-tenant disclosure |
| model invents/asks for unauthorized resource ID | grounding/scope failure |
| missing label triggers cross-scope speculation | tenant/grounding failure |
| evidence for one asset used for another | unsupported operational conclusion |
| baseline/data quality treated as fault proof | false diagnosis |
| unknown/malformed/unauthorized tool | safety bypass |
| prompt/tool-output injection controls policy | unsafe action/claim |
| redirect/credential leak | secret disclosure |
| provider/model/route silently substituted | provenance/cost/quality failure |
| automatic paid fallback | cost-boundary violation |
| raw provider/evaluator/private material reaches browser/log | privacy/scientific leakage |
| benchmark/gold truth leaks into candidate context | invalid evaluation |
| failed benchmark attempts selectively retried/removed | scientific-integrity failure |
| best-effort JSON passes syntax but violates controller relation | unsafe/invalid decision state |
| provider strict schema is treated as authorization | policy/safety bypass |
| account quota/rate rejection misclassified as model quality | invalid selection evidence |
| overlapping QA deployments stitched into one campaign | invalid experimental claim |
| SSE reorder/gap treated as truth | incorrect visible state |
| stale owner finalizes after lease loss | incorrect/duplicate state |
| consequential action replay | external side effect |
| release SHA decoupled from artifact | false provenance |

## 3. Identity / tenant mitigations

- managed session validated server-side;
- tenant/permissions server-owned;
- browser authority headers ignored/rejected;
- PostgreSQL scoped role + RLS independent boundary;
- tenant negative acceptance;
- impersonated sessions rejected.

### Read-burst session resilience

```text
GET/HEAD
→ cookie digest
→ bounded validated-context cache
→ singleflight
→ managed auth on cache miss

POST/non-read
→ fresh managed-auth validation
```

Raw cookie is not stored in read cache; expired entries are never stale-on-error. Invalid auth and temporary identity-service unavailability remain distinct fail-closed states.

## 4. Model/tool/grounding authority

- provider returns decisions/proposals, never execution authority;
- `HarnessRunner` is exclusive real tool boundary;
- schema, argument, policy and evidence gates are deterministic;
- bounded turns/timeouts/payloads;
- no hidden provider fallback;
- asset labels resolve only against authorized structured observations;
- comparison evidence is resource-specific;
- missing labels close scope rather than expand it;
- response mode has no permission effect.

A provider's `strict:true` constrained decoding, if later introduced, is only an additional syntax/structure barrier. It does not replace `ProviderDecisionPayload`, argument validation, tenant policy or action safety.

## 5. TRACTIAN network / actions

- canonical 18-operation registry;
- server-owned credentials/headers;
- HTTPS/base URL restrictions;
- bounded timeout/request/response sizes;
- redirects disabled;
- no blind write retry;
- Release 0 consequential external execution disabled.

The exact supplied `ActionRequest` schema must be recovered from the canonical contract before strict action-output variants are trusted; do not guess it.

## 6. Evidence / observability / research integrity

- durable safe production event projection;
- raw sensitive/private/gold/hidden-reasoning fields excluded;
- evaluator post-runtime;
- durable cursor is truth for realtime;
- frozen provider populations/rubrics remain immutable after exposure;
- preflights are distinct from scored attempts;
- failures remain denominator under the frozen protocol;
- no automatic JSON repair/fallback/selective rerun to manufacture a pass;
- partial campaigns affected by overlapping deployments are discarded rather than combined.

Repeated tool names are judged with arguments/resource/evidence contribution; legitimate asset→point drill-down remains allowed.

## 7. Provider qualification state

Groq `openai/gpt-oss-120b` completed the frozen 85-attempt single-provider qualification and returned **`NO_SELECTION`**:

```text
rubric pass        81.18%
reliability        82.35%
contract failures  9
repeat stability   64.71%
```

This negative result is security/reliability evidence. It does not authorize lowering contract gates or moving Groq into production.

Cloudflare GPT-OSS quota failures were non-scored preflight evidence and the candidate was subsequently removed from the requested path; no paired winner is claimed.

Current causal work investigates completion budget, reasoning effort and best-effort vs strict structured output. A clean 21/21 matrix and strict eligibility still remain pending.

## 8. Cost / capacity boundary

- no hidden automatic paid provider fallback;
- quota exhaustion/admission rejection must remain explicit;
- provider/model/route identity explicit;
- capacity errors are separated from model-quality evidence;
- provider research never publishes API credentials.

A concurrent OpenRouter capacity probe observed a free-model daily limit below the 85-call final population; that route cannot be treated as an equivalent final qualification path without changing the account capacity/protocol explicitly.

## 9. Release provenance

Track independently:

- production backend/frontend/supplied-API identity;
- production provider/model route;
- research branch/manifests/population SHA;
- frozen runner/bootstrap identities;
- historical acceptance identities.

A docs/research commit is not a backend/provider promotion.

## 10. Evidence already passed for current scope

- hosted managed-auth/tenant isolation in Release 0 scope;
- managed-session resilience regression + live retesting for tested scope;
- explicit asset/data-quality/missing-resource live retests;
- structural blocking evaluations for referenced hosted runs;
- real typed TRACTIAN reads;
- external action calls remain disabled/zero in promoted Release 0 scope;
- provider framework successfully rejected the tested Groq configuration under unchanged gates.

## 11. Still required before broader claims

- clean isolated provider causal 21/21;
- exact `ActionRequest` recovery;
- strict-schema eligibility if justified;
- unchanged-rubric challenger comparison and winner-only 85/85;
- Academy live E2E before provider promotion;
- full SECURITY-V1 hosted campaign;
- larger session/concurrency/resource-exhaustion campaign;
- provider/TRACTIAN/DB failure campaign at final topology;
- restore/recovery evidence;
- real action adversarial campaign before enabling actions;
- broader semantic/anti-hallucination/false-precision live testing.

## 12. Change trigger

Revisit this model after a production provider change, new external dependency, auth/tenant/storage change, consequential action enablement, new browser data class, major topology change, security incident/finding or adaptive policy that changes tool/resource authority.

Security findings follow root [`SECURITY.md`](../SECURITY.md).
