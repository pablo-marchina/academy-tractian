# Academy × TRACTIAN — Handoff and Operations Runbook

**Status:** ACTIVE operational runbook  
**Checkpoint:** 2026-09-05 production rebaseline  
**Authority:** subordinate to [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md), [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md), accepted ADRs and frozen experiment evidence.

This runbook deliberately separates three paths:

1. **local/CI reproduction** — deterministic evidence and developer verification;
2. **remote staging/production operation** — the required final serving path;
3. **historical experiment reproduction** — frozen evidence only.

Local reproducibility is important, but local execution must never be presented as the final production topology.

## 1. Promoted product architecture

```text
remote browser
→ standards-based user identity (target production IAM)
→ FastAPI product API
→ trusted server-owned runtime context
→ PostgreSQL tenant RLS + mutable/durable product state
→ runtime handoff / leases / generation fencing
→ RealtimeProductionRuntime
→ hosted provider DecisionSource
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

## 2. Local/CI reproduction prerequisites

Canonical CI toolchain currently uses:

- Python 3.11+
- Node compatible with `frontend/package.json`
- PostgreSQL 18 in current GitHub Actions contracts
- dependencies from `pyproject.toml` and committed `frontend/package-lock.json`

Python development/reproduction install from repository root:

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

## 3. Canonical clean-clone reproduction

The authoritative current-product repository reproduction workflow is:

`.github/workflows/clean-clone-full-product-reproduction.yml`

The older `.github/workflows/final-delivery-provider-free-reproduction.yml` is historical evidence and is intentionally distinct.

Current clean-clone coverage includes:

```text
clean tracked checkout
→ install backend/E2 dependencies
→ PostgreSQL-backed Python product suite
→ promoted identity/RLS/load/recovery checks
→ cross-replica/action correctness regressions through required workflows
→ accepted controller/safety evidence
→ frozen EV-007 / EV-008 / EV-011 reproduction
→ final evidence/handoff validation
→ npm ci
→ frontend typecheck + unit tests + production build
→ no tracked repository mutation
```

Do not modify frozen expected identities or historical evidence merely to make a later reproduction gate pass.

## 4. Manual local reproduction

This section is **developer/reviewer reproduction only**, not production serving.

Start an isolated local PostgreSQL instance and expose the test DSN to the test process, for example:

```text
POSTGRES_OPERATIONAL_TEST_DSN=postgresql://postgres:postgres@127.0.0.1:5432/academy_tractian
```

Then from repository root:

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

PowerShell example:

```powershell
$env:POSTGRES_OPERATIONAL_TEST_DSN = "postgresql://postgres:postgres@127.0.0.1:5432/academy_tractian"
```

A localhost DSN is valid here because this section is explicitly local reproduction. The production environment must reject local serving dependencies.

## 5. Full browser acceptance in CI/staging

Current repository Chromium acceptance is:

`.github/workflows/full-product-playwright.yml`

It exercises the real product controller/tool/persistence/evaluation/SSE/frontend path with a deterministic provider-free decision source.

This proves product integration and browser semantics, including reconnect/catch-up and safe projection. It does **not** prove that a remote production provider/model or production IAM works.

After remote deployment exists, add/retain a staging-compatible browser suite that covers the selected IAM and deployment topology without using customer data or unsafe consequential actions.

## 6. Remote production prerequisites

Before the runbook may call a deployment “production”, record the selected infrastructure decision/ADR and provide:

- production frontend URL;
- production API URL;
- managed PostgreSQL endpoint/service identity without publishing secrets;
- selected IAM/identity provider configuration;
- selected hosted model/provider configuration;
- secret manager/environment contract;
- deployment region/topology;
- migration strategy;
- health/readiness/version endpoints;
- build/commit/artifact identity;
- rollback target/procedure;
- backup/PITR configuration where selected.

Production startup/config validation must fail closed on forbidden local/test configuration such as:

- localhost/loopback backend/DB/model endpoint;
- local model server;
- SQLite/DuckDB/filesystem production state;
- provider-free/mock decision source;
- test identity bypass.

## 7. Remote deployment procedure — contract

The exact commands depend on the infrastructure selected by systematic comparison. Once selected, this section must contain executable provider-specific steps rather than placeholders.

The deployment contract is:

```text
merge protected main
→ immutable build artifact
→ deploy/migrate staging
→ staging health + smoke
→ staging authenticated browser E2E
→ production promotion
→ production health + smoke
→ synthetic safe run
→ monitor errors/latency/event delivery
→ keep previous release available for rollback
```

A deployment is not complete because the build succeeded. Remote health, persistence, authenticated access and live run behavior must be verified.

## 8. Production smoke checklist

After every production promotion, verify at minimum:

- expected commit/build/deploy revision is visible;
- `/health` and `/ready` are truthful;
- database connectivity/RLS scope is healthy;
- authentication succeeds for an authorized test user;
- unauthorized/expired identity fails closed;
- one safe run can be submitted;
- genuine runtime events arrive over SSE;
- terminal state/evaluation is persisted;
- reconnect/catch-up works;
- safe evidence/lineage is visible;
- no forbidden fields appear in browser/API/SSE;
- provider errors, if induced/observed, fail safely;
- no consequential action executes without explicit governed confirmation.

## 9. Failure/recovery behavior

### Invalid arguments

B1 blocks before transport. Never convert denial into invented success.

### Authorization/policy denial

Stop before consequential transport and preserve the safe denial/audit record.

### Missing/conflicting evidence

Clarify, abstain or escalate. Never fabricate certainty.

### Provider/decision-source failure

Do not manufacture a conclusion/action from malformed or unavailable output. Raw sensitive provider material remains private.

### Read-only runtime ownership loss

Generation fencing prevents stale owner finalization. An expired read-only lease may be recovered by another replica only according to the promoted handoff contract.

### Consequential action ownership loss

Action execution leases are non-transferable. Lost/stale ownership converges to `UNCERTAIN`; no replacement external transport attempt is started automatically.

### Process/deployment restart

Recovery must remain conservative and idempotent. Restart/deploy never authorizes blind action replay.

### Database/provider outage

Production response must preserve user-visible safe status/handoff and durable-state guarantees demonstrated by the selected deployed topology. Record the incident/recovery metrics instead of hiding outages with uncontrolled retries.

## 10. Backup and restore

Once the managed database is selected:

1. verify automated backup/PITR configuration;
2. create known test state;
3. execute a controlled restore/PITR drill in an isolated environment;
4. verify tenant/action/run/evaluation integrity;
5. record measured recovery time and possible data-loss window;
6. update production RTO/RPO claims only from measured evidence.

Provider SLA is not a substitute for this drill.

## 11. Security/privacy rules

Never expose through browser/API/SSE/artifacts/logs:

- provider secrets/tokens;
- account/auth headers;
- signing/identity secrets;
- benchmark/evaluator seed or gold truth;
- raw sensitive provider prompt/response content;
- forbidden raw tool/observation bodies;
- private action arguments/idempotency keys;
- hidden chain-of-thought.

Tenant and permission authority must remain server-owned. Production end-user auth must not be described as enterprise/OIDC until the standards-based flow is actually deployed and tested.

## 12. Operational diagnosis order

Diagnose the earliest failing boundary:

```text
DNS/TLS/deployment health
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

Do not mask one layer with retries/fallbacks from another.

Correlate with request/run/build/trace identifiers where the production observability design supports them.

## 13. Rollback procedure — contract

A production rollback must be tested before final freeze.

Required behavior:

```text
identify bad deployment
→ stop further promotion
→ preserve evidence/logs
→ verify DB migration compatibility
→ route/deploy previous known-good artifact
→ production smoke
→ verify durable runs/actions remain semantically safe
→ document incident + regression
```

Never roll back schema/application combinations blindly when a migration is not backward compatible. Migration/rollback design is part of the infrastructure decision.

## 14. Historical provider-free campaigns

Historical frozen identities remain evidence for their original scopes:

```text
EV-007  7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
EV-008  1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8
EV-011  cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e
DEMO    43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445
```

They are reproducibility evidence, not proof of remote provider/IAM/capacity/HA readiness.

Historical D01/D02 currently conclude `NO_SELECTION`; do not replay consumed protocols simply to search for a more attractive outcome.

## 15. Final presentation sequence

The final presentation should operate the same normal remote product used by authorized users:

```text
1. open Production Health / build identity
2. authenticate as a normal authorized user
3. submit a representative industrial request
4. watch LIVE run + architecture/trace growth
5. inspect tool/policy/evidence path
6. inspect terminal operational conclusion
7. inspect evaluator after runtime completion
8. inspect output lineage / dynamic analytics
9. show clarify/abstain/escalate safe behavior
10. show governed pending action + explicit confirmation in an authorized safe profile
11. show provider/model evaluation state
12. show remote production/load/recovery evidence and explicit non-claims
```

Do not use a separate demo-only serving stack.

## 16. Final completion checklist

Before final production freeze:

- repository cleanup/rebaseline merged;
- current-product `final-ci-required` green on exact final SHA;
- historical evidence remains intact;
- remote deployment URL works independently of developer machines;
- production-local-dependency guard passes;
- standards-based IAM + multi-user/tenant tests pass;
- branch protection + CI/CD are enforced;
- staging/production smoke and rollback are tested;
- production observability is live;
- remote load/soak evidence exists before capacity/SLO claims;
- backup/restore/recovery evidence exists before RTO/RPO/HA claims;
- semantic calibration remains `NOT READY` unless real labels exist;
- operational-value claims remain `NOT READY` unless real human measurements exist;
- provider/model state remains truthful (`NO_SELECTION` unless a new hosted challenger wins);
- no secrets/private evaluator material is present in repo/artifacts/frontend;
- documentation commands and URLs match the deployed/code state;
- no last-minute framework expansion without measured need.

If a gate is not closed, report the exact limitation instead of broadening the claim.
