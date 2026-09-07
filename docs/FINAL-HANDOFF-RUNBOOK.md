# Academy × TRACTIAN — Production Handoff and Operations Runbook

**Status:** ACTIVE operational how-to  
**Last verified:** 2026-09-06 BRT  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Promoted backend/runtime:** `082d6f115c070fdc898df749b4b3018efd9ceeab`

This runbook covers current Release 0 operation and safe future promotion. Local commands are for development/reproduction only.

## 1. Production topology

```text
Browser
→ Railway production-web (Caddy / React)
   ├── /auth/* → Neon Auth
   └── /api/* + SSE → Railway production-api
                         ↓
                 Neon PostgreSQL
                 Cloudflare Workers AI
                 supplied TRACTIAN API
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
- safe failure/abstain/escalate behavior;
- no hidden reasoning/secrets in browser projections;
- external consequential action execution disabled until separately promoted.

## 3. Health and first diagnosis

Start with the public origin and server health/readiness/release metadata. Diagnose in dependency order:

```text
DNS/TLS/public frontend
→ managed auth/session
→ production API health/readiness/release identity
→ Neon connectivity/RLS
→ provider configuration/quota
→ DecisionSource/controller
→ typed tool/policy
→ TRACTIAN transport
→ evidence/terminal
→ evaluator/persistence
→ SSE/cursor catch-up
→ React projection
```

Do not mask an upstream problem with hidden retries/fallbacks.

## 4. Safe production smoke after a frontend-only UX deployment

Verify:

1. public page loads and sign-in boundary is present;
2. Results is default layer;
3. Quick Start/custom request input works;
4. Evidence/Investigation/Engineering tabs are keyboard/click accessible;
5. backend `/health`/release identity did not unexpectedly change;
6. one bounded read-only investigation reaches a safe terminal state if quota permits;
7. history and SSE/reconnect behavior remain correct;
8. no external action execution is enabled.

A frontend SHA can advance without changing the immutable backend Release 0 SHA. Record them separately.

## 5. Backend promotion procedure

Backend promotion is intentional, not implied by a green PR or frontend deploy.

```text
select exact tested backend SHA
→ ensure required CI green
→ set/verify exact release identity contract
→ deploy the exact source/artifact
→ predeploy TRACTIAN connectivity gate must pass
→ run hosted G2 exact-SHA smoke
→ manually dispatch hosted-production-release0-agent with expected_sha=<exact SHA>
→ verify FINAL + CLARIFY + ABSTAIN + ESCALATE + tenant boundaries
→ record immutable evidence
```

`.github/workflows/hosted-production-release0-agent.yml` is `workflow_dispatch` only and requires `expected_sha`.

Do not trigger a live provider acceptance simply because an unrelated frontend/docs PR changed.

## 6. Production smoke checklist

- [ ] expected frontend deployment identity;
- [ ] expected backend artifact/release SHA;
- [ ] health/readiness truthful;
- [ ] managed auth works;
- [ ] invalid/unauthorized session fails closed;
- [ ] tenant scope/RLS behavior intact;
- [ ] provider route/model explicit and no hidden fallback;
- [ ] bounded TRACTIAN read succeeds when expected;
- [ ] safe tool/provider failure behavior;
- [ ] terminal mode and evidence persist;
- [ ] evaluator appears only post-runtime;
- [ ] authenticated SSE + reconnect/catch-up;
- [ ] no forbidden/private fields in browser output;
- [ ] external consequential actions remain disabled unless a later action gate is explicitly promoted;
- [ ] USD0/no-paid-spillover boundary intact.

## 7. Local / CI reproduction

Developer setup:

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

Canonical full-product contracts are implemented through GitHub Actions, especially:

- `final-ci-required.yml`;
- `clean-clone-full-product-reproduction.yml`;
- `full-product-playwright.yml`;
- `production-runtime.yml`;
- targeted Postgres/observability/EDD/IaC regressions.

Provider-free CI proves product integration without consuming live provider quota; it is not a substitute for hosted production acceptance.

## 8. Failure semantics

- invalid tool args → deterministic B1 block before transport;
- policy/authorization denial → no consequential transport;
- missing/conflicting evidence → clarify/abstain/escalate, never fabricate;
- provider failure → safe failure mode, no invented conclusion/action;
- TRACTIAN failure → normalized unavailable/error evidence, no false success;
- read-only runtime lease loss → generation fencing prevents stale finalization;
- action ownership ambiguity (future action path) → `UNCERTAIN`, never blind replacement attempt;
- quota exhaustion → fail/degrade safely, never auto-upgrade to paid;
- SSE gap → recover through durable cursor/catch-up.

## 9. Rollback

For a bad deployment:

```text
stop further promotion
→ preserve failing evidence/logs
→ identify last known-good eligible artifact
→ verify DB compatibility
→ restore/redeploy known-good frontend/backend as applicable
→ production smoke
→ verify tenant/action/cost boundaries
→ document incident + regression
```

Do not change frozen evidence to erase the failed candidate.

## 10. Backup / restore

Final RTO/RPO claims are still pending. Before claiming them:

1. identify the strongest USD0 export/backup mechanism actually available;
2. create known tenant/run/evaluation test state;
3. take export/backup;
4. restore into isolated safe environment;
5. verify counts, hashes/identity where applicable, tenant isolation and run/evaluation integrity;
6. measure recovery time/data-loss window;
7. publish only the measured RTO/RPO boundary.

## 11. Security/privacy

Never log/project:

- provider/API/database/auth secrets;
- raw sensitive upstream payloads without a justified sanitized contract;
- benchmark gold/evaluator-private material;
- private action custody/idempotency keys;
- hidden chain-of-thought.

See [`SECURITY-MODEL.md`](SECURITY-MODEL.md) and root [`SECURITY.md`](../SECURITY.md).

## 12. Incident priority

```text
P0: auth/tenant escape, secret leak, unauthorized action, paid-spillover, release-identity bypass
P0: product cannot safely complete/stop a real read-only run
P1: wrong conclusion/tool/evidence/mode behavior
P1: persistence/SSE/history breakage
P1: severe first-user friction
P2: non-blocking visual/polish issue
```

## 13. Final presentation path

Use the normal hosted product, not a special demo stack:

1. show public health/release/guardrails;
2. sign in normally;
3. submit a representative investigation from Results;
4. show live progress and terminal next step;
5. open Evidence for support;
6. open Investigation for runtime/Trace Graph/history;
7. open Engineering for evaluator/architecture/capabilities;
8. demonstrate safe CLARIFY/ABSTAIN/ESCALATE behavior as quota/evidence permits;
9. show proposal-only action boundary without executing a consequential external change;
10. show final evidence/non-claims accurately.