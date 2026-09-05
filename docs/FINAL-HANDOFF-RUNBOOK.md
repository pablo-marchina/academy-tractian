# Academy × TRACTIAN — Handoff and Operations Runbook

**Status:** ACTIVE operational runbook  
**Checkpoint:** 2026-09-05 corrected production rebaseline  
**Authority:** subordinate to [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md), [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md), [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md), accepted ADRs and frozen experiment evidence.

This runbook separates three paths:

1. **local/CI reproduction** — deterministic evidence and developer verification;
2. **remote USD0 staging/production operation** — the required final serving path;
3. **historical experiment reproduction** — frozen evidence only.

Local reproducibility is important, but local execution must never be presented as the final production topology. Likewise, a paid hosted path must never be presented as project-compliant while the USD0 hard constraint applies.

## 1. Hard operational envelope

The selectable production path must satisfy all of the following simultaneously:

```text
actual project cash cost = USD 0
no automatic paid spillover
remote serving; no developer-machine dependency
standards-based user identity
multi-user tenant isolation
safe consequential actions
remote durable PostgreSQL-compatible state
observable/reproducible release
```

If no available topology satisfies this envelope plus the technical gates, the correct state is an explicit blocker/`NO_SELECTION`, not a paid fallback.

## 2. Promoted logical product architecture

```text
remote browser
→ standards-based USD0 user identity (target production IAM)
→ FastAPI product API
→ trusted server-owned runtime context
→ PostgreSQL tenant RLS + mutable/durable product state
→ runtime handoff / leases / generation fencing
→ RealtimeProductionRuntime
→ USD0 hosted provider DecisionSource
→ AgentController
→ HarnessRunner
→ 18 typed TRACTIAN tools
→ deterministic B1/B2/B3 boundaries
→ normalized evidence
→ terminal/action proposal
→ RunTrace + ProductionEvaluator
→ sanitized PostgreSQL observability/evaluation
→ durable cursor + LISTEN/NOTIFY wake-up
→ REST/SSE
→ React operator control room
```

The currently implemented signed bearer runtime identity and provider-free decision source remain useful repository/test boundaries. They are not, by themselves, the final production IAM/provider claim.

Consequential actions remain governed by private PostgreSQL custody, explicit confirmation, current authorization, host kill switch, persistent idempotency and non-transferable execution leases. Ambiguous ownership loss becomes `UNCERTAIN` and is never blindly replayed.

## 3. Local/CI reproduction prerequisites

Canonical CI toolchain currently uses Python 3.11+, Node compatible with `frontend/package.json`, PostgreSQL in the current Actions contracts, dependencies from `pyproject.toml` and committed `frontend/package-lock.json`.

Backend/dev installation:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]" -e "research/e2[dev]"
```

Frontend deterministic install:

```bash
cd frontend
npm ci --ignore-scripts --no-audit --no-fund
cd ..
```

Provider-free reproduction requires no live model/provider secret.

## 4. Canonical clean-clone reproduction

The authoritative current-product repository reproduction workflow is:

`.github/workflows/clean-clone-full-product-reproduction.yml`

The older `.github/workflows/final-delivery-provider-free-reproduction.yml` is historical evidence and intentionally distinct.

Current clean-clone coverage includes:

```text
clean tracked checkout
→ install backend/E2 dependencies
→ PostgreSQL-backed Python product suite
→ identity/RLS/load/recovery checks
→ distributed/action correctness regressions through required workflows
→ accepted controller/safety evidence
→ frozen historical evidence validation
→ npm ci
→ frontend typecheck + unit tests + production build
→ no tracked repository mutation
```

Do not modify frozen expected identities or historical evidence merely to make a later gate pass.

## 5. Manual local reproduction

This is developer/reviewer reproduction only, not production serving.

A local PostgreSQL DSN such as:

```text
POSTGRES_OPERATIONAL_TEST_DSN=postgresql://postgres:postgres@127.0.0.1:5432/academy_tractian
```

is allowed for local tests. The production environment must reject loopback/local serving dependencies.

Representative local commands:

```bash
python -m pytest -q tests
python -m pytest -q research/e2/tests/test_controller.py
python scripts/validate_ev007_failure_campaign.py
python scripts/validate_ev008_stability_campaign.py
python scripts/validate_ev011_communication_campaign.py
python scripts/validate_delivery_reproduction.py
python scripts/validate_final_handoff_audit.py
cd frontend
npm ci --ignore-scripts --no-audit --no-fund
npm run typecheck
npm test
npm run build
```

## 6. Full browser acceptance in CI/staging

Current Chromium acceptance is `.github/workflows/full-product-playwright.yml`.

It exercises the real product controller/tool/persistence/evaluation/SSE/frontend path with a deterministic provider-free decision source. This proves product integration/browser semantics, not remote provider/IAM production quality.

After remote deployment exists, staging-compatible browser acceptance must cover the selected USD0 IAM/deployment topology without unsafe customer actions/data.

## 7. Remote production prerequisites

Before a deployment may be called production, record the systematic infrastructure decision/ADR and provide:

- remote frontend/API URL(s);
- selected USD0 remote PostgreSQL-compatible store;
- selected USD0 IAM configuration;
- selected USD0 hosted model/provider configuration;
- selected USD0 telemetry/monitoring path where external tooling is used;
- secret/environment contract;
- deployment topology/region;
- migration strategy;
- health/readiness/version endpoints;
- build/commit/artifact identity;
- rollback target/procedure;
- strongest USD0 backup/export/PITR mechanism available;
- quota/free-tier limits and fail-closed behavior;
- evidence that actual cash cost remains USD0 and automatic paid spillover is impossible/disabled.

Paid candidates may appear in research comparisons as references but cannot populate these selected-production fields.

## 8. Production startup/configuration guards

Production must fail closed or be considered ineligible when configured with:

- localhost/loopback backend/DB/model endpoints;
- local model server;
- SQLite/DuckDB/filesystem production state;
- provider-free/mock decision source;
- development identity bypass;
- a component requiring non-zero project cash spend;
- automatic paid-overage/spillover behavior.

Quota exhaustion must degrade/fail safely rather than authorize spending.

## 9. Remote deployment procedure — contract

Exact commands depend on the USD0 infrastructure selected by systematic comparison. Once selected, replace the provider-specific placeholders with executable steps.

```text
merge protected main
→ immutable build artifact
→ deploy/migrate USD0 staging
→ staging health + smoke
→ staging authenticated browser E2E
→ verify quota/cost guard
→ production promotion
→ production health + smoke
→ synthetic safe run
→ monitor errors/latency/event delivery/quota
→ keep known-good rollback target where the selected free platform permits it
```

A deployment is not complete because a build succeeded. Remote health, persistence, authenticated access, live run behavior and zero-cost enforcement must be verified.

## 10. Production smoke checklist

After every production promotion verify:

- expected commit/build/deploy revision;
- health/readiness truthfulness;
- DB connectivity/RLS scope;
- authentication succeeds for authorized test user;
- unauthorized/expired identity fails closed;
- safe run submission;
- genuine SSE events;
- terminal state/evaluation persistence;
- reconnect/catch-up;
- evidence/lineage visibility;
- no forbidden fields;
- provider errors fail safely;
- no action executes without governed confirmation;
- free-tier/quota state is healthy;
- actual project cash cost remains USD0;
- no automatic paid spillover is enabled.

## 11. Failure/recovery behavior

- **Invalid arguments:** B1 blocks before transport.
- **Authorization/policy denial:** stop before consequential transport and preserve safe denial/audit evidence.
- **Missing/conflicting evidence:** clarify, abstain or escalate; never fabricate certainty.
- **Provider failure:** never manufacture a conclusion/action from malformed/unavailable output.
- **Read-only runtime ownership loss:** generation fencing prevents stale finalization; eligible expired read-only work may transfer according to the handoff contract.
- **Consequential action ownership loss:** converge to `UNCERTAIN`; never start a replacement external transport automatically.
- **Process/deployment restart:** recovery remains conservative/idempotent and never authorizes blind action replay.
- **Quota exhaustion/free-tier suspension:** fail/degrade safely, expose status and preserve durable state; never cross to paid operation automatically.
- **Database/provider outage:** preserve safe user-visible state/handoff according to the selected topology and record recovery evidence.

## 12. Backup and restore

For the selected USD0 database topology:

1. identify the strongest free backup/PITR/export capability;
2. create known test state;
3. run a controlled restore/reconstruction drill in isolation;
4. verify tenant/action/run/evaluation integrity;
5. record recovery time and possible data-loss window;
6. update RTO/RPO claims only from measured evidence.

If a stronger backup/HA feature is paid-only, document that limitation; do not enable it.

## 13. Security/privacy rules

Never expose provider secrets, auth headers, signing secrets, benchmark/gold truth, raw sensitive provider/tool material, private action arguments/idempotency keys or hidden chain-of-thought.

Tenant/permission authority remains server-owned. Production end-user auth is not described as OIDC/SSO until the standards-based flow is actually deployed/tested.

Also treat cost-boundary bypass as a security/operations failure: credentials/config must not allow normal workflows to silently incur paid charges.

## 14. Operational diagnosis order

```text
DNS/TLS/deployment health
→ USD0 quota/cost guard
→ user authentication/session
→ tenant ownership/RLS
→ runtime preparation/ownership
→ hosted decision provider
→ controller decision
→ tool proposal
→ B1 validation
→ B2/B3 policy
→ TRACTIAN transport
→ normalized evidence
→ terminal outcome
→ trace validation/evaluator
→ PostgreSQL safe projection
→ wake-up/SSE
→ browser reducer/render
```

Do not mask one layer with uncontrolled retries/fallbacks from another.

## 15. Rollback procedure — contract

```text
identify bad deployment
→ stop further promotion
→ preserve evidence/logs
→ verify DB migration compatibility
→ route/deploy previous known-good eligible artifact
→ production smoke
→ verify durable runs/actions remain safe
→ verify USD0/cost guard
→ document incident + regression
```

Never use a paid rollback service/plan as an implicit fallback if that would violate the project constraint.

## 16. Provider experiment state

Historical D01/D02 Cloudflare packets remain frozen evidence.

D02 completed 32/32 attempts at USD0 and preserved safe failure/trace behavior, but the tested GLM and Nemotron candidates failed frozen M1/M4/M7 promotion gates. Therefore current provider state is `NO_SELECTION`.

Cloudflare is not rejected for being expensive; it passed the cost gate. It is not selected because the tested candidates did not pass the technical gates. A materially new USD0 Cloudflare candidate may be evaluated only through a new preregistered experiment; consumed D01/D02 packets are not replayed.

There is no paid provider fallback.

## 17. Final presentation sequence

The final presentation should operate the normal remote USD0 product:

```text
1. show Production Health / build identity / USD0 boundary health
2. authenticate as a normal authorized user
3. submit a representative industrial request
4. watch live run + architecture/trace growth
5. inspect tool/policy/evidence path
6. inspect terminal conclusion
7. inspect evaluator after runtime completion
8. inspect output lineage / dynamic analytics
9. show clarify/abstain/escalate safe behavior
10. show governed pending action + confirmation in authorized safe profile
11. show provider/model state
12. show remote production/load/recovery evidence and exact limitations
```

Do not use a separate demo-only or paid serving stack.

## 18. Final completion checklist

Before final production freeze:

- repository cleanup/rebaseline merged;
- `final-ci-required` green on exact final SHA;
- historical evidence intact;
- actual project cash cost remains USD0;
- no selected component can silently spill into paid usage;
- remote product works independently of developer machines;
- local-dependency guard passes;
- USD0 standards-based IAM + multi-user/tenant tests pass;
- branch protection + CI/CD enforced;
- staging/production smoke + rollback tested;
- production observability live;
- remote load/soak evidence exists before capacity/SLO claims;
- backup/restore/recovery evidence exists before RTO/RPO/HA claims;
- semantic calibration remains `NOT READY` unless real labels exist;
- operational-value claims remain `NOT READY` unless real human measurements exist;
- provider/model remains truthful (`NO_SELECTION` unless a new USD0 hosted challenger wins);
- no secrets/private evaluator material in repo/artifacts/frontend;
- documentation matches deployed/code state;
- no last-minute framework expansion without measured need.

If a gate is not closed, report the exact limitation instead of broadening the claim or relaxing a user-specified hard constraint.
