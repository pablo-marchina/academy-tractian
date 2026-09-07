# Academy × TRACTIAN — Production Handoff and Operations Runbook

**Status:** ACTIVE operational how-to  
**Last verified:** 2026-09-07 BRT  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Current merged backend/runtime source:** `3545d75c00ca30419e0f47e8b1950aa50cbbf462`  
**Current frontend:** `1bc124a8d4dbd029178ff8129b25452129445de7`

This runbook covers current Release 0 V13 operation, governed-action rollout and safe promotion. Local commands are development/reproduction only.

## 1. Production topology

```text
Browser
→ Railway production-web (Caddy / task-driven React)
   ├── /auth/* → Neon Auth
   └── /api/* + SSE → Railway production-api
                         ├→ Neon PostgreSQL/RLS
                         ├→ Cloudflare provisional provider
                         ├→ typed supplied TRACTIAN reads
                         └→ governed action custody/confirmation/executor
                                → server-owned TRACTIAN actor
                                → supplied TRACTIAN action endpoint
```

Consequential actions are enabled only through the governed path. Complete five-action vendor acceptance is still an open gate because the live smoke surfaced an upstream identity/permission mismatch.

## 2. Hard operational envelope

Production must preserve:

- actual project cash cost = USD0;
- no automatic paid spillover;
- no localhost/developer-machine serving dependency;
- managed user session + server-owned tenant authority;
- PostgreSQL/RLS durable state;
- exact backend release identity;
- explicit provider/model route;
- canonical typed TRACTIAN transport;
- grounded structured resource IDs;
- safe evidence/response-mode semantics;
- no hidden reasoning/secrets in browser projections;
- action proposals are not execution;
- exact confirmation only for an already custodied action;
- canonical permissions/resource authority remain server-owned;
- persistent idempotency + lease/fencing before a write;
- vendor actor identity is server-owned and selected only after local authorization;
- no blind retry after an ambiguous write;
- explicit upstream acceptance required for `ACCEPTED`.

## 3. Health and diagnosis order

```text
DNS/TLS/public frontend
→ managed auth/session
→ production API /health + release identity
→ Neon connectivity/RLS
→ provider configuration/quota
→ DecisionSource/controller
→ typed tool/policy
→ TRACTIAN read transport
→ evidence/terminal/response_mode
→ evaluator/persistence
→ action grants/custody/idempotency/lease when actions are involved
→ upstream actor mapping
→ TRACTIAN action transport
→ SSE/cursor catch-up
→ React projection
```

Do not mask upstream problems with hidden retries, hidden fallback identities or more privileged grants.

## 4. Managed-session incident diagnosis

If UI shows `managed_session_unavailable`:

1. check `/health`; if health is 200, do not classify as general API outage;
2. distinguish protected API `401` from `503`;
3. `401 managed_session_invalid` means session must be re-established;
4. `503 managed_session_unavailable` means managed identity validation is temporarily unavailable and is retryable;
5. do not weaken auth or introduce stale-on-error to recover availability;
6. verify GET/HEAD fan-out is using bounded 2-second server cache/singleflight;
7. verify POST/non-read still validates fresh;
8. verify frontend leaves authenticated state on invalid session and exposes retry on unavailable state.

The #207 fix deliberately preserves fail-closed behavior while reducing identity-provider fan-out.

## 5. Current frontend smoke

After frontend-only promotion verify:

1. public page loads/sign-in works;
2. **Home** is the default primary destination;
3. one natural-language question can be submitted;
4. run opens customer result/progress;
5. supporting evidence is reachable contextually;
6. **Analyses** lists/selects persisted runs;
7. **Technical** exposes Current analysis / Quality / Data / System / Actions / Studies;
8. focus/visibility return does not cause a ghost-auth state;
9. backend `/health` and release identity did not unexpectedly change;
10. action UI never reports success unless the backend action state is explicitly `ACCEPTED`;
11. confirmation UI submits only the exact confirmation for an existing action and does not expose raw custody/grants/vendor-actor configuration.

Frontend SHA may advance independently from backend SHA. Record both.

## 6. Backend exact-SHA promotion

A green PR/source merge does **not** automatically promote backend production.

Procedure:

```text
select exact tested backend SHA
→ required CI green
→ set release identity variable without triggering an old snapshot
→ trigger a fresh exact-commit Railway deployment
→ verify build used exact RAILWAY_GIT_COMMIT_SHA
→ wheel install + pip check
→ normal TRACTIAN connectivity predeploy smoke
→ application startup
→ /health 200
→ targeted live acceptance on the promoted behavior
→ record deployment/run evidence
```

### Railway snapshot rule

A Railway **Redeploy** can reuse a previously captured deployment snapshot. It is not proof that a newly edited service configuration, `preDeployCommand` or current source head was materialized.

When configuration provenance matters:

```text
change an explicit operational/release marker
→ create a fresh deployment snapshot
→ inspect deployment source SHA + configuration behavior
→ only then treat the run as current-config evidence
```

This distinction mattered during the governed-action validation: a generic redeploy continued to show the old read connectivity probe even though the service configuration had been edited. A fresh snapshot then executed the intended write smoke and surfaced the real HTTP 403.

## 7. Current backend/action deployment ledger

### Governed action enablement — PR #211

```text
SHA         1a1e7139bfa0361416120b3f21937c4048b5bb1f
deployment  9732a2cb-c321-4fcf-83f8-c6f87eeab06a
status      SUCCESS
```

This proved the production composition could boot with governed writes enabled and server-owned grants.

### Auditable action smoke — PR #213

```text
SHA         3545d75c00ca30419e0f47e8b1950aa50cbbf462
CI gate     34164123263 — SUCCESS
deployment  2cbc4215-f59a-4947-8691-0d4776458445 — SUCCESS
```

This source contains `academy_tractian.governed_write_transport_smoke`.

### Fresh live five-action validation

```text
deployment  5ba36471-776c-4e15-919b-56e2da216b74
status      FAILED SAFE
failure     update_asset_config -> HTTP 403 / accepted=false
containment previous healthy deployment remained serving
```

Never rewrite this failure as success. It remains the current live action-readiness evidence until prospectively superseded by a later 5/5 pass.

## 8. Live read agent smoke after backend promotion

At minimum choose prompts that verify:

- identity/fleet discovery without asking for internal IDs;
- one condition-evidence path;
- data-quality path if changed;
- response-mode semantics;
- missing-resource fail closed;
- safe action proposal/confirmation boundary when relevant.

Inspect Neon/Railway rather than only the displayed prose:

```text
run_id
execution state
tool sequence + arguments/status
model calls
tool proposals/calls
policy blocks/errors
terminal decision
response_mode
remote TRACTIAN HTTP path
blocking evaluation checks
```

### Repetition rule

Do not count `get_rms`/`get_spectrum` repetitions by name only. Compare arguments and resource. Asset-level then `point_id`-specific read is valid drill-down; exact same target/args without new evidence is the redundancy candidate.

## 9. Governed five-action production validation

Canonical validator:

```bash
python -m academy_tractian.governed_write_transport_smoke
```

It must run only with explicit operator approval and server-owned environment configuration.

Before writes it requires the hosted capability endpoint to report:

```text
actions = 5
executable_actions = 5
action_execution.enabled = true
action_execution.mode = GOVERNED_CONFIRMATION
governed_action_path_enabled = true
```

It then calls exactly:

```text
reprocess_analysis
request_specialist_analysis
update_asset_config
request_retraining
escalate_case
```

through the canonical binder and `ProductionTractianTransport`.

Each action passes only when:

```text
HTTP ∈ {200, 201, 202}
AND accepted == true
```

Safe smoke output must not contain credentials, grant material, resource IDs, vendor actor IDs or response bodies.

One failure aborts the validation deployment. The previous healthy release must remain serving.

## 10. Upstream action actor diagnosis

If low-impact writes work but high-impact/escalation writes return 403, do **not** automatically widen the local grant.

Inspect the vendor authorization contract first.

Current supplied-runtime evidence shows:

```text
x-user-id -> vendor actor
endpoint -> required permission
```

and the tested company scope has distinct vendor actors for `action_low` versus `action_high + escalate`.

Correct target:

```text
local authenticated requester
→ local grant/resource/confirmation/idempotency/lease authorization
→ (company_id, required_permission)
→ exactly one server-owned TRACTIAN actor
→ final vendor-bound identity only
```

The browser/model/confirmation payload must never select the actor. Missing/ambiguous actor mapping is a hard block.

The corrective actor-routing implementation is still in progress and is not yet merged/proven at this record's timestamp.

## 11. Production smoke checklist

- [ ] expected frontend deployment identity;
- [ ] expected backend artifact/release SHA;
- [ ] fresh Railway snapshot when source/configuration changed;
- [ ] health truthful;
- [ ] managed auth works;
- [ ] invalid session 401 / temporary auth outage 503 behavior intact;
- [ ] tenant scope/RLS intact;
- [ ] provider route/model explicit and no hidden fallback;
- [ ] authorized fleet grounding works;
- [ ] relevant TRACTIAN read succeeds;
- [ ] no user request for discoverable internal IDs;
- [ ] response_mode matches evidence/message;
- [ ] safe provider/tool failure behavior;
- [ ] terminal/evidence persist;
- [ ] evaluator appears post-runtime;
- [ ] authenticated SSE + reconnect/catch-up;
- [ ] no forbidden/private fields in browser output;
- [ ] action kill-switch/grants state matches intended rollout;
- [ ] no action success claimed without explicit upstream `accepted=true`;
- [ ] vendor actor mapping server-owned and complete for intended action permission;
- [ ] five-action smoke 5/5 before claiming complete action readiness;
- [ ] USD0/no-paid-spillover boundary intact.

## 12. Local / CI reproduction

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]" -e "research/e2[dev]"
cd frontend
npm ci --ignore-scripts --no-audit --no-fund
```

Representative validation:

```bash
python -m pytest -q tests
cd frontend
npm run typecheck
npm test
npm run build
```

Canonical full-product gates include `final-ci-required`, clean clone, full-product Playwright, production runtime and targeted Postgres/observability/EDD/IaC/action-lease regressions.

Provider-free CI is not a substitute for hosted provider/IAM/TRACTIAN acceptance.

## 13. Failure semantics

- invalid tool args → deterministic B1 block;
- policy/authorization denial → no consequential transport;
- missing authorized asset label → bounded unavailable, no cross-tenant guessing;
- insufficient/conflicting evidence → calibrated response/terminal, never fabricate;
- provider failure → safe failure mode;
- TRACTIAN read failure → normalized unavailable/error evidence;
- managed-auth transient failure → 503 retryable, no stale auth;
- action vendor permission/actor mismatch → `NOT_ACCEPTED`/validation failure, never privilege widening by inference;
- action ownership/transport ambiguity → `UNCERTAIN`, no blind retry;
- duplicate idempotency claim → block duplicate action;
- runtime/action lease loss → generation fencing;
- quota exhaustion → fail/degrade safely, never paid fallback;
- SSE gap → durable cursor/catch-up.

## 14. Rollback

```text
stop further promotion
→ preserve failing evidence/logs
→ if action risk exists, set ACADEMY_ACTIONS_ENABLED=false
→ identify last known-good eligible artifact
→ verify DB compatibility
→ deploy known-good exact source/artifact with fresh snapshot
→ production smoke
→ verify tenant/action/cost boundaries
→ document incident + regression
```

Do not change frozen evidence to erase a failed candidate. Never replay an `UNCERTAIN` action automatically.

## 15. Backup / restore

Final RTO/RPO claims are still pending. A real drill must create known state, export/backup, restore to isolated safe environment, verify counts/integrity/tenant isolation/action-state consistency and measure recovery/data-loss windows before any RTO/RPO claim.

## 16. Security/privacy

Never log/project provider/API/database/auth secrets, raw sensitive upstream payloads without a sanitized contract, benchmark gold/evaluator-private material, private action custody/idempotency keys, authorization grants, vendor actor mappings or hidden chain-of-thought.

See [`SECURITY-MODEL.md`](SECURITY-MODEL.md), [`GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md`](GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md) and root [`SECURITY.md`](../SECURITY.md).

## 17. Incident priority

```text
P0 auth/tenant escape, secret leak, unauthorized/duplicate action, vendor-actor privilege escalation, paid spillover, release-identity bypass
P0 product cannot safely complete/stop a real run or contains an ambiguous write incorrectly
P1 wrong grounding/conclusion/tool/evidence/response-mode behavior
P1 expected governed action rejected by vendor mapping/configuration
P1 persistence/SSE/history/session-resilience breakage
P1 severe first-user friction
P2 non-blocking visual/polish issue
```

## 18. Final presentation path

Use the normal hosted product, not a demo stack:

1. architecture overlay;
2. signed-in Home/task boundary;
3. one representative persisted/live investigation;
4. result + response mode + supporting evidence;
5. Analyses/history for a safe alternate outcome;
6. Technical → Current analysis for trace/tools;
7. Technical → Quality for evaluator;
8. Technical → Actions for custody/confirmation/idempotency/lease architecture **and the current explicit 5/5 live-validation limitation**;
9. deployment/auth/realtime overlay;
10. limitations/non-claims.

Do not present the known HTTP 403 as a successful action and do not describe the current action path as deny-all/read-only.

See [`progress/2026-09-07-production-governed-actions-ux-and-validation.md`](progress/2026-09-07-production-governed-actions-ux-and-validation.md) for the dated evidence.