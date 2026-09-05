# LIVE-PRODUCTION-READY promotion contract — 2026-09-05

Status: **IN PROGRESS / NOT PROMOTED**

This supersedes `LIVE-DEMO-READY-PLAN-2026-09-05.md` as the acceptance contract for PR #191. The live presentation is an operating context, not a separate product mode. No component may be promoted solely because it is sufficient for a presentation.

## Definition

`LIVE-PRODUCTION-READY` means the exact hosted artifact intended for the live presentation is also suitable for an initial production deployment under the documented capacity and external-service assumptions. The only demo-specific dependency may be the replaceable TRACTIAN sandbox upstream; security, persistence, identity, execution, observability, deployment and recovery boundaries must remain production boundaries.

## Immutable safety boundaries

- OIDC/JWKS asymmetric verification; no fixed/demo identity fallback.
- Durable shared PostgreSQL is the source of truth; no local persistent fallback in hosted serving.
- Migration/DDL credentials are absent from the serving process.
- Service/scoped PostgreSQL roles are least-privilege and RLS-scoped where applicable.
- Tenant identity is bound independently between OIDC organization and TRACTIAN user/company at new-run creation.
- Every model-facing TRACTIAN resource request passes a server-owned tenant authorization guard before the upstream response can become evidence.
- Cross-tenant resource access is denied before response exposure to the model.
- Consequential actions require server-owned permission, resource ownership, exact confirmation and idempotency; a config flag alone cannot enable them.
- Interrupted consequential actions are never blindly replayed.
- Browser-visible observability contains sanitized decisions/evidence/policies, never hidden chain-of-thought, raw secrets or private action payloads.
- `eval/`, gold labels and evaluator-only challenge material never enter hosted runtime images or authorization decisions.

## Current proven production substrate

Already accepted on the branch baseline before this contract:

- PostgreSQL durable observability/run/execution state.
- production wheel boots without DuckDB installed.
- PostgreSQL LISTEN/NOTIFY wakeups with durable-row truth and fallback recovery.
- horizontal read-only runtime handoff/recovery.
- OIDC/JWKS hosted identity boundary.
- separate migration owner, service role and scoped role; serving uses no DDL credential.
- reproducible sandbox manifest derived from the exact user-supplied archive SHA-256 `37546f7a9af93e7364d35313c53a67621769d454a3803624aad4daffa4d0d134`, with hosted runtime limited to `api/` + `data/` and evaluator/gold material excluded.

## Current P0 slice: tenant/resource authorization

The supplied challenge upstream proves action permissions through `/users/me`, but its resource GETs and action endpoints do not consistently enforce company ownership. Therefore hosted production must be stricter than the sandbox itself.

Promoted design:

1. verified OIDC subject identifies the user;
2. `/users/me` supplies server-owned TRACTIAN company and supported permissions;
3. OIDC organization must match TRACTIAN company when a new run is created;
4. asset ownership is proven from the normal asset endpoint;
5. analysis ownership is proven through analysis -> asset -> company;
6. a last-mile guarded transport blocks cross-tenant reads/actions before model exposure;
7. model retraining and case escalation remain fail-closed until the public upstream contract can prove their company ownership.

No private sandbox store, seed source, evaluator data, ID naming convention, browser claim or model text may be used as an authorization source.

## Remaining blockers before promotion

### P0 — exact-target action authorization

Promote a target-aware resolver used at both proposal and confirmation so enabling actions does not require enumerating the tenant's full resource graph on every run. Prove TOCTOU revalidation, same-company binding, confirmation binding and idempotency. Keep `request_retraining` and `escalate_case` blocked while ownership is not publicly introspectable.

### P0 — hosted external topology

Provision and validate remote PostgreSQL, managed OIDC, backend hosting, frontend hosting and remote TRACTIAN sandbox/real endpoint using the same production artifact. No localhost dependency is allowed in the deployed request path.

### P0 — live provider selection

Run the frozen provider comparison on actual eligible USD0 candidates. Select only from quantitative evidence across semantic correctness, tool/argument correctness, safety, latency, failure rate and operational cost. Provider-free execution remains a contingency/test path, not the claimed production model.

### P0 — remote end-to-end acceptance

From a clean browser on a different network prove:

`browser -> OIDC -> hosted frontend -> hosted FastAPI -> shared PostgreSQL -> selected provider -> tenant-guarded TRACTIAN HTTP -> evidence -> terminal response -> evaluator -> SSE/replay`

Include refresh/reconnect and `Last-Event-ID` recovery.

### P0 — security/failure campaign

Prove fail-closed behavior for invalid/expired JWTs, tenant mismatch, cross-tenant resource IDs, malicious tool arguments, confirmation replay, idempotency replay, provider outage, TRACTIAN outage, PostgreSQL transient failure, replica loss during read-only execution, and interrupted consequential actions.

### P1 — production UI/control room

Expose the existing safe operational evidence needed for a real operator: request lifecycle, tool/evidence timeline, policy decisions, run evaluation, provider provenance, production health, distributed execution/recovery and sanitized failure reasons. Do not expose hidden reasoning.

## Promotion gates

PR #191 stays draft and `LIVE-PRODUCTION-READY` stays **NOT PROMOTED** until all of the following are true on one exact commit SHA:

- `hosted-production-boundary` green;
- `production-runtime` green, including a standalone no-DuckDB wheel boot;
- PostgreSQL operational/restart/handoff/realtime gates green;
- load/concurrency benchmark green;
- clean-clone reproduction green;
- provider/evaluation/observability/frontend gates green;
- full-product Playwright green;
- final delivery/handoff/final-ci gates green;
- remote hosted E2E evidence exists for the exact promoted artifact;
- no P0 security or cross-tenant failure remains open;
- provider/model selection is backed by current measured evidence;
- exact deployment SHA/config provenance is recorded.

A green local or CI-only product is not sufficient to claim `LIVE-PRODUCTION-READY`. A visually successful live demo is not sufficient either.
