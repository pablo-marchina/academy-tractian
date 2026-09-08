# Academy × TRACTIAN — Production Handoff and Operations Runbook

**Status:** ACTIVE operational how-to  
**Last verified:** 2026-09-08 BRT  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Current backend/runtime:** `5611687556b3d50c31f20fa85ede794f2500f05c`  
**Backend deployment:** `542bf459-353d-432c-b2ff-b862cedf1574` — `SUCCESS`  
**Current frontend:** `4364364266c6a88d4affd85cb3a734c774cd42c8`  
**Frontend deployment:** `8375d735-539c-46af-b299-9ee4aca8e505` — `SUCCESS`

This runbook covers the current hosted product, exact-SHA promotion, provider/action diagnostics and rollback. Local commands are development/reproduction only. Current OpenRouter V14 is deployed but **not functionally accepted**: the real authenticated B204 matrix currently fails at the first provider decision before any TRACTIAN read.

## 1. Production topology

```text
Browser
→ Railway production-web (Caddy / React)
   ├── /auth/* → Neon Auth
   └── /api/* + SSE → Railway production-api
                         ├→ Neon PostgreSQL/RLS
                         ├→ OpenRouter V14 fixed-free DecisionSource
                         ├→ AgentController → HarnessRunner
                         └→ supplied TRACTIAN API
                              ├→ 13 typed reads
                              └→ 5 governed actions via server-owned action actors
```

## 2. Hard operational envelope

Preserve at all times:

- actual project cash cost = USD0;
- no automatic paid/model/provider fallback;
- no localhost/developer-machine production dependency;
- managed session + server-owned tenant/permission authority;
- PostgreSQL/RLS durable truth;
- exact release identity;
- explicit provider/model/route provenance;
- canonical `AgentController` + `HarnessRunner` authority boundary;
- typed TRACTIAN transport only;
- safe evidence/terminal/response-mode semantics;
- no secrets/private gold/grants/custody/hidden reasoning in browser projections;
- governed action confirmation/authorization/idempotency/lease invariants when actions are enabled.

## 3. Current provider identity

```text
provider_id  openrouter
model_id     nvidia/nemotron-3-super-120b-a12b:free
route_id     openrouter.chat_completions.v1.fixed_free
fallbacks    disabled
cost_policy  usd0-hard-gate
```

V14 accepts a provider decision only when there is exactly one assistant choice, exact model identity when returned, `finish_reason=stop`, no provider-side tool/function call and valid nonempty structured decision content.

## 4. Health / diagnosis order

```text
DNS/TLS/public frontend
→ managed auth/session
→ production API /health + exact release identity
→ PostgreSQL/RLS
→ provider configuration / model pin / quota
→ provider response contract
→ DecisionSource/controller
→ HarnessRunner/tool-policy
→ TRACTIAN read/action transport
→ evidence/terminal/response_mode
→ evaluator/verification/persistence
→ SSE/cursor catch-up
→ React projection
```

Never hide an upstream/provider problem with paid fallback, silent model substitution or unbounded retry.

## 5. Current OpenRouter V14 incident signature

The authenticated B204 functional campaign created:

```text
F01  run_437a59ba893a96e3f902
F02  run_86c832ce46189200b613
F03  run_f081d5d45b0cf4caf4b3
```

All three:

```text
managed auth          PASS
POST /api/runs        202
runtime worker        PASS
OpenRouter decision   FAIL
TRACTIAN calls        0
terminal reason       DECISION_SOURCE_FAILURE
```

A sanitized response-shape probe observed:

```text
HTTP 200
exact pinned model served
assistant content present
finish_reason = length
```

A bounded completion/reasoning comparison subsequently hit HTTP 429 for all variants and is therefore `INCONCLUSIVE`.

### Operator rule

Do not change the runtime until the provider quota/key-tier state is safely measured and the exact `length` failure can be reproduced under eligible conditions. Then compare only bounded fixes and promote a measured winner.

## 6. Managed-session incident diagnosis

If UI shows managed-session failure:

1. check `/health`;
2. distinguish protected API 401 from 503;
3. 401 means invalid/expired session and must re-authenticate;
4. 503 means temporary identity validation unavailability and is retryable;
5. never add stale-on-error authorization;
6. verify GET/HEAD bounded ≤2 s validated-context cache/singleflight;
7. verify POST/non-read still fresh-validates;
8. verify frontend reconciles state after invalid/unavailable signal and focus/visibility return.

## 7. Frontend smoke

After frontend promotion verify:

1. public origin loads;
2. sign-in works;
3. Home is default task entry;
4. natural-language question can be submitted;
5. live progress/result state is truthful;
6. supporting evidence is contextual;
7. Analyses lists persisted runs;
8. Technical exposes trace/quality/data/system/actions/verification/studies;
9. frontend provider/action/release state matches backend-safe APIs;
10. no browser surface exposes secret/private authority material.

Record frontend and backend SHAs independently.

## 8. Exact-SHA backend promotion

A green source branch/PR is not production promotion.

```text
choose exact candidate SHA
→ required CI green on that SHA
→ hosted functional/security gates green for applicable scope
→ trigger fresh Railway deploy from exact commit
→ verify RAILWAY_GIT_COMMIT_SHA/artifact identity
→ predeploy smokes
→ application startup /health 200
→ verify release endpoint exact SHA
→ rerun targeted authenticated acceptance
→ record deployment/run evidence
```

Current backend:

```text
SHA         5611687556b3d50c31f20fa85ede794f2500f05c
deployment  542bf459-353d-432c-b2ff-b862cedf1574
status      SUCCESS
```

It is a deployed candidate, not yet an accepted V14 functional release.

## 9. Authenticated V14 functional acceptance procedure

Use the real managed session; do not bypass auth.

Required immediate matrix:

```text
B204 F01 explicit condition
B204 F02 causal investigation
B204 F03 data quality
```

For each run inspect:

- exact release SHA;
- model/provider/route provenance;
- model-call success/failure code;
- tool sequence and normalized argument fingerprints;
- real TRACTIAN HTTP calls/status;
- policy blocks/errors;
- terminal decision/message;
- response mode;
- persisted evidence/lineage;
- structural/functional/evidence verification.

Acceptance is 3/3 only when all cases reach real TRACTIAN tools and a valid grounded terminal/evaluation. `DECISION_SOURCE_FAILURE` or zero-tool completion is not a pass.

## 10. Repetition / stopping rule

Do not classify repetition by tool name alone.

```text
get_rms(asset)
→ get_rms(asset, point_id=...)
```

may be valid drill-down. Exact successful duplicate operation + normalized arguments/resource must not execute twice in the same run after the evidence is already available.

## 11. Governed action operation

Current production architecture supports five canonical governed actions. Controlled pre-deploy smoke passed 5/5 HTTP 200.

Before any real user-driven consequential action, verify:

- exact release identity;
- current provider functional readiness;
- action capability mode;
- server-owned authorization grant health;
- complete upstream action actor coverage;
- PostgreSQL custody/idempotency/action-lease health;
- tenant/resource binding;
- current SECURITY-V1 go/no-go state.

Do not infer end-user action readiness from the 5/5 transport smoke.

Detailed procedure: [`GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md`](GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md).

## 12. Production smoke checklist

- [ ] expected frontend SHA/deployment;
- [ ] expected backend artifact/runtime SHA;
- [ ] supplied API identity recorded;
- [ ] `/health` truthful;
- [ ] managed auth works;
- [ ] 401 vs 503 semantics intact;
- [ ] tenant scope/RLS intact;
- [ ] exact provider/model/route shown safely;
- [ ] no hidden fallback / paid spillover;
- [ ] provider decision contract succeeds for intended scenario;
- [ ] real TRACTIAN read or governed action path succeeds as applicable;
- [ ] exact duplicate-success suppression intact;
- [ ] terminal/response mode matches evidence;
- [ ] evaluator/verification persists post-runtime;
- [ ] authenticated SSE/reconnect/catch-up;
- [ ] no forbidden/private fields in browser/log evidence;
- [ ] action mode/grants/actors match intended rollout;
- [ ] no unexpected `UNCERTAIN` action;
- [ ] branch/release governance state recorded.

## 13. Failure semantics

- invalid tool args → deterministic schema block;
- policy/authorization denial → no consequential transport;
- missing asset → bounded unavailable, no cross-tenant guessing;
- incomplete provider completion (`finish_reason != stop`) → provider decision failure, no tool authority;
- provider HTTP 429/quota → explicit availability failure, never paid fallback;
- TRACTIAN failure → normalized unavailable/error evidence;
- managed-auth transient failure → 503, no stale auth;
- runtime lease loss → generation fencing;
- action ownership/transport ambiguity → `UNCERTAIN`, no blind replay;
- SSE gap → durable cursor/catch-up.

## 14. Rollback

```text
stop promotion / disable risky capability if needed
→ preserve failing evidence
→ identify last known-good eligible exact artifact
→ verify DB/schema compatibility
→ deploy exact known-good source
→ health/auth/tenant/provider/tool/action smoke
→ document incident + regression
```

For action emergency stop set `ACADEMY_ACTIONS_ENABLED=false` and redeploy/restart exact configuration. Never auto-retry an `UNCERTAIN` action.

Do not rewrite historical evidence to erase a failed candidate.

## 15. Backup / restore

Final RTO/RPO remains unproven. Required real drill:

```text
seed known state
→ create real backup/export/restore point
→ controlled mutation/loss scenario
→ restore into isolated safe target
→ verify schema + row counts + selected hashes + tenant isolation
→ application smoke
→ measure elapsed recovery and data-loss window
```

Only then publish RTO/RPO.

## 16. Security / branch governance

Current branch metadata still reports `main.protected=false`; the stable required CI gate exists but enforcement is external/pending. Do not describe direct mutation as technically blocked until GitHub reports protection active.

Never log provider/API/database/auth secrets, raw private upstream/provider material, benchmark gold, action grant/actor JSON, private custody/idempotency or hidden reasoning.

## 17. Incident priority

```text
P0 tenant escape / unauthorized action / secret leak / paid spillover / false release identity
P0 real authenticated run cannot safely complete under promoted provider
P1 wrong grounding/tool/evidence/terminal/response mode
P1 persistence/SSE/session/action-state breakage
P1 severe first-user friction
P2 non-blocking visual polish
```

The current V14 0/3 authenticated functional gate is therefore a P0 release blocker.

## 18. Final presentation / handoff path

Use the normal hosted product and current state, not a demo stack:

1. current architecture/provider/action overlay;
2. signed-in Home;
3. one verified successful persisted investigation after the V14 gate is green;
4. result + response mode + evidence;
5. Analyses/history;
6. Technical trace/tool/evidence;
7. Quality/Verification distinction;
8. Actions governed-confirmation state and exact claim boundary;
9. deployment/release provenance;
10. remaining limitations/non-claims.

Do not record a failed/incomplete V14 path as if it were final functional success. Historical V13 runs may be shown only when explicitly labeled historical.