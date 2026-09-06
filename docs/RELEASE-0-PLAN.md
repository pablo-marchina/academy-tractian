# Academy × TRACTIAN — Release 0 Immediate User Plan

**Status:** ACTIVE / immediate execution authority  
**Release objective:** put the real remote read-only product in users' hands as soon as the safety-critical release gates pass.  
**Supersedes for Release 0 blocking order:** the final-delivery gate order in `DELIVERY-PLAN.md`. Final-delivery work remains valid but moves behind first-user release unless explicitly listed here as a blocker.

## 1. Release 0 objective

Release a real remotely hosted product where an authenticated user can submit an industrial question, a real hosted DecisionSource can investigate through the real TRACTIAN read API, evidence is persisted and streamed live, and the user receives a safe terminal result.

Release 0 is deliberately **read-only for consequential external effects**. Action proposals may be observed for evaluation, but external consequential action execution remains disabled until the later governed-action gate.

## 2. Non-negotiable release blockers

Release 0 MUST NOT ship unless all are true:

- actual project cash cost remains USD 0;
- automatic paid spillover is impossible;
- production serving has no localhost/developer-machine/local-model/local-file dependency;
- browser identity is authenticated through the managed production boundary;
- browser-supplied tenant/role/permission authority is ignored/rejected;
- tested cross-tenant disclosure is zero for the Release 0 campaign;
- production uses a real hosted provider, not the provider-free/mock DecisionSource;
- production uses real TRACTIAN reads, not the provider-free/mock transport;
- provider/model route is explicit, observable and fail-closed;
- real evidence, terminal output, persistence and SSE/reconnect work on the public path;
- consequential action execution is disabled.

## 3. Critical path

```text
R0-00 rebaseline current branch/deploy state
→ R0-01 minimum hosted IAM acceptance
→ R0-02 real TRACTIAN bounded-read acceptance
→ R0-03 provisional USD0 provider qualification
→ R0-04 production DecisionSource composition
→ R0-05 genuine read-only agent vertical slice
→ R0-06 minimum mode/evidence/user UX acceptance
→ R0-07 external two-user smoke
→ RELEASE TO USERS
```

R0-01, R0-02 and provider qualification preparation may proceed in parallel.

## 4. R0-00 — Rebaseline

Record current source/deployed SHA, G2 state, IAM state, TRACTIAN state, provider state, action state and exact external blockers. Keep `ACTIVE-PROJECT-STATUS.md`, PR #196, this file and chronological progress evidence synchronized.

## 5. R0-01 — Minimum IAM acceptance

Required positive path:

- sign-up/sign-in/session/sign-out;
- authenticated REST;
- authenticated SSE;
- two independent users;
- intended same-organization behavior where configured.

Required release negatives:

- user A cannot access user B runs/evidence/evaluations/SSE;
- browser cannot assert organization, role or permissions;
- missing/invalid/expired/impersonated session fails closed;
- RLS remains an independent scoped-data boundary.

Hard gates:

```text
cross_tenant_disclosure = 0
browser_tenant_authority_acceptance = 0
browser_privilege_authority_acceptance = 0
invalid_session_acceptance = 0
unauthorized_sse_access = 0
```

## 6. R0-02 — Real TRACTIAN bounded reads

Use the existing `ProductionTractianTransport` and authoritative server-managed endpoint/header configuration. First prove a representative vertical slice; expand coverage after users are unblocked.

Release hard gates:

```text
real_remote_request_observed = true
canonical_method_path_binding = pass
typed_arguments = pass
server_owned_auth_context = pass
redirect_follow = 0
credential_leakage = 0
blind_retry = 0
sanitized_failure = pass
```

Capture latency/error evidence and normalized `complete|partial|inconclusive|conflict|unavailable` behavior where observed.

## 7. R0-03 — Provisional provider qualification

The full Provider Tournament v3 remains required for final promotion, but no longer blocks first users. Release 0 may use a **provisionally qualified** USD0 provider/model if it passes a small representative governed campaign and the configuration labels the state honestly.

Use existing USD0-eligible Cloudflare candidates first because the client, request contract, quota model and tournament population already exist in-repo. Do not silently use a paid provider.

Minimum qualification should cover representative investigate/final, clarify, unavailable/conflict and action-safety cases with repeated attempts as quota permits.

Hard gates:

```text
cash_cost_usd = 0
paid_spillover = 0
private_gold_leakage = 0
unsafe_external_action = 0
policy_bypass = 0
route_model_substitution = 0
```

Measure structured-contract success, operational correctness, tool/argument quality, provider failures, latency and quota use. Decision state is `PROVISIONAL_RELEASE_PROVIDER`, not final tournament winner.

## 8. R0-04 — Production DecisionSource

Replace `NoSelectedProviderDecisionSource` only when a provisionally qualified release provider is configured.

Required boundary:

- explicit server-managed credential;
- explicit provider/model/route;
- strict existing `ProviderDecisionPayload` validation;
- bounded timeout/input/output;
- one-shot/no automatic retry;
- no hidden fallback;
- no paid fallback;
- sanitized provider failures;
- provider/model provenance in telemetry;
- controller remains owner of tools and safety.

Boot MUST fail closed when provider calls are enabled but provider configuration is incomplete or unsupported.

## 9. R0-05 — Genuine read-only vertical slice

From the public product origin:

```text
authenticated user
→ submit real question
→ hosted provider decision
→ typed read tool
→ real TRACTIAN response
→ normalized evidence
→ hosted provider next decision
→ FINAL | CLARIFY | ABSTAIN | ESCALATE
→ post-runtime evaluation
→ durable PostgreSQL
→ live SSE/frontend
```

No provider-free/test transport/decision source may participate.

## 10. R0-06 — Minimum user-facing acceptance

Before first users, verify at least one safe path for FINAL, CLARIFY, ABSTAIN and ESCALATE and one real investigation/tool path. The UI must make the current state understandable without exposing hidden chain-of-thought.

Minimum user surface:

- authentication;
- new investigation;
- live status;
- terminal answer/clarification/escalation;
- evidence summary/lineage;
- run history/reload;
- clear failure states.

Engineering/eval surface should expose provider/model, tool calls, evidence, evaluation, latency, release SHA and production dependency health.

## 11. R0-07 — External release smoke

From a fresh external browser/network:

1. authenticate;
2. submit a real question;
3. observe genuine live SSE;
4. observe hosted provider use;
5. observe real TRACTIAN read evidence;
6. receive terminal result;
7. observe post-runtime evaluation;
8. reload and recover persisted run;
9. second user cannot access first user's state;
10. confirm no local/mock dependency participates;
11. confirm action execution remains disabled;
12. confirm cash cost remains USD 0.

When these pass, Release 0 is released to users immediately.

## 12. Post-release priority

After first users are active, prioritize in this order:

1. user-blocking reliability/auth/provider/TRACTIAN defects;
2. correctness/tool/evidence/clarification/escalation defects observed in real runs;
3. UX friction and speed;
4. full provider tournament and final provider promotion;
5. full SECURITY-V1, capacity/SLO and recovery/restore evidence;
6. governed actions;
7. human semantic calibration and operational-value study;
8. adaptive challengers only after measured gaps.

## 13. Scope control

Before Release 0, do not add LangGraph, multi-agent, RAG/vector DB, MCP, Redis/Kafka, microservices, Kubernetes, persistent memory or other optional topology unless a blocker cannot be solved by the current promoted architecture.

## 14. Documentation rule

Every material Release 0 change must update, as applicable:

1. implementation/tests;
2. hosted/source evidence;
3. `ACTIVE-PROJECT-STATUS.md` or the latest progress checkpoint;
4. this plan when sequencing/state changes;
5. PR #196 summary;
6. decision registry when a material promoted/provisional decision changes.

Historical/frozen evidence is never rewritten.
