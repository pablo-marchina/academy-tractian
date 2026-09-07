# Academy × TRACTIAN — Production Handoff and Operations Runbook

**Status:** ACTIVE operational how-to  
**Last verified:** 2026-09-07 BRT  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Current backend/runtime:** `08866da60245f58f217981b7ae668b10be45cc67`  
**Current frontend:** `1bc124a8d4dbd029178ff8129b25452129445de7`

This runbook covers current Release 0 V13 operation and safe future promotion. Local commands are development/reproduction only.

## 1. Production topology

```text
Browser
→ Railway production-web (Caddy / task-driven React)
   ├── /auth/* → Neon Auth
   └── /api/* + SSE → Railway production-api
                         ├→ Neon PostgreSQL/RLS
                         ├→ Cloudflare provisional provider
                         └→ supplied TRACTIAN API
```

Release 0 is read-only with respect to consequential external TRACTIAN actions.

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
- external consequential action execution disabled until separately promoted.

## 3. Health and diagnosis order

```text
DNS/TLS/public frontend
→ managed auth/session
→ production API /health + release identity
→ Neon connectivity/RLS
→ provider configuration/quota
→ DecisionSource/controller
→ typed tool/policy
→ TRACTIAN transport
→ evidence/terminal/response_mode
→ evaluator/persistence
→ SSE/cursor catch-up
→ React projection
```

Do not mask upstream problems with hidden retries/fallbacks.

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
10. no external action execution is enabled.

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
→ TRACTIAN predeploy connectivity smoke
→ application startup
→ /health 200
→ targeted live acceptance on the promoted behavior
→ record deployment/run evidence
```

Do not use a generic redeploy when exact source provenance matters. A redeploy may reuse an old deployment snapshot.

Current successful V13 deployment:

```text
SHA         08866da60245f58f217981b7ae668b10be45cc67
deployment  062c3cc4-4ac9-48ac-be06-2b4c490cea2a
status      SUCCESS
```

Original manual Release 0 acceptance workflow/run remains historical evidence and does not need to be falsified into a V13 acceptance run.

## 7. Live agent smoke after backend promotion

At minimum choose prompts that verify:

- identity/fleet discovery without asking for internal IDs;
- one condition-evidence path;
- data-quality path if changed;
- response-mode semantics;
- missing-resource fail closed;
- read-only action challenge.

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

## 8. Production smoke checklist

- [ ] expected frontend deployment identity;
- [ ] expected backend artifact/release SHA;
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
- [ ] no external consequential action execution;
- [ ] USD0/no-paid-spillover boundary intact.

## 9. Local / CI reproduction

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

Canonical full-product gates include `final-ci-required`, clean clone, full-product Playwright, production runtime and targeted Postgres/observability/EDD/IaC regressions.

Provider-free CI is not a substitute for hosted provider/IAM/TRACTIAN acceptance.

## 10. Failure semantics

- invalid tool args → deterministic B1 block;
- policy/authorization denial → no consequential transport;
- missing authorized asset label → bounded unavailable, no cross-tenant guessing;
- insufficient/conflicting evidence → calibrated response/terminal, never fabricate;
- provider failure → safe failure mode;
- TRACTIAN failure → normalized unavailable/error evidence;
- managed-auth transient failure → 503 retryable, no stale auth;
- read-only runtime lease loss → generation fencing;
- future action ownership ambiguity → `UNCERTAIN`, no blind replacement attempt;
- quota exhaustion → fail/degrade safely, never paid fallback;
- SSE gap → durable cursor/catch-up.

## 11. Rollback

```text
stop further promotion
→ preserve failing evidence/logs
→ identify last known-good eligible artifact
→ verify DB compatibility
→ deploy known-good exact source/artifact
→ production smoke
→ verify tenant/action/cost boundaries
→ document incident + regression
```

Do not change frozen evidence to erase a failed candidate.

## 12. Backup / restore

Final RTO/RPO claims are still pending. A real drill must create known state, export/backup, restore to isolated safe environment, verify counts/integrity/tenant isolation and measure recovery/data-loss windows before any RTO/RPO claim.

## 13. Security/privacy

Never log/project provider/API/database/auth secrets, raw sensitive upstream payloads without a sanitized contract, benchmark gold/evaluator-private material, private action custody/idempotency keys or hidden chain-of-thought.

See [`SECURITY-MODEL.md`](SECURITY-MODEL.md) and root [`SECURITY.md`](../SECURITY.md).

## 14. Incident priority

```text
P0 auth/tenant escape, secret leak, unauthorized action, paid spillover, release-identity bypass
P0 product cannot safely complete/stop a real read-only run
P1 wrong grounding/conclusion/tool/evidence/response-mode behavior
P1 persistence/SSE/history/session-resilience breakage
P1 severe first-user friction
P2 non-blocking visual/polish issue
```

## 15. Final presentation path

Use the normal hosted product, not a demo stack:

1. architecture overlay;
2. signed-in Home/task boundary;
3. one representative persisted/live investigation;
4. result + response mode + supporting evidence;
5. Analyses/history for a safe alternate outcome;
6. Technical → Current analysis for trace/tools;
7. Technical → Quality for evaluator;
8. Technical → Actions for deny-all external execution boundary;
9. deployment/auth/realtime overlay;
10. limitations/non-claims.