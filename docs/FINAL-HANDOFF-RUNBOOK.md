# Academy × TRACTIAN — Final Handoff Runbook

**Status:** ACTIVE operational runbook  
**Authority:** subordinate to [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md), accepted ADRs and frozen experiment evidence.  
**Final delivery:** 2026-09-08

## 1. Promoted provider-free product path

```text
signed bearer identity
→ FastAPI product API
→ PostgreSQL mutable operational state + tenant RLS
→ RealtimeProductionRuntime
→ DecisionSource
→ AgentController
→ HarnessRunner
→ 18 typed TRACTIAN tools
→ B1/B2/B3 boundaries
→ normalized evidence
→ terminal/action proposal
→ RunTrace + evaluator
→ safe DuckDB read model
→ REST/SSE
→ React operator control room
```

The provider-free profile performs no live provider call and no real-customer mutation.

Consequential actions are separately governed by persistent custody, explicit confirmation, current authorization, a host kill switch and a persistent one-shot idempotency claim. Ambiguous post-claim outcomes become `UNCERTAIN` and are never blindly retried.

## 2. Prerequisites

Canonical CI versions:

- Python 3.11
- Node 24
- PostgreSQL 18
- npm dependencies from committed `frontend/package-lock.json`

Python install from repository root:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]" -e "research/e2[dev]"
```

Frontend locked install:

```bash
cd frontend
npm ci --ignore-scripts --no-audit --no-fund
cd ..
```

No provider secret is required for provider-free reproduction.

## 3. Canonical clean-clone reproduction

The authoritative automated path is:

`.github/workflows/final-delivery-provider-free-reproduction.yml`

It starts from a clean `actions/checkout`, starts PostgreSQL 18 and runs:

```text
1. verify tracked checkout is clean
2. install Python + E2 dependencies
3. run complete `tests` suite with POSTGRES_OPERATIONAL_TEST_DSN set
4. explicitly rerun promoted identity/RLS + load + restart P0 Postgres tests
5. regress ADR-004 controller boundary
6. reproduce frozen EV-007
7. reproduce frozen EV-008
8. reproduce frozen EV-011
9. validate final-delivery demo/evidence index
10. validate final-handoff audit
11. npm ci from package-lock
12. frontend typecheck
13. frontend unit tests
14. frontend production build
15. verify no tracked repository mutation
```

This is the P0 clean-checkout reproduction contract. Do not change frozen expected identities merely to make this gate pass; diagnose the implementation/evidence mismatch.

## 4. Manual provider-free reproduction

Start a local PostgreSQL 18 instance and expose an admin DSN only to the test process, for example:

```text
POSTGRES_OPERATIONAL_TEST_DSN=postgresql://postgres:postgres@127.0.0.1:5432/academy_tractian
```

Then run from repository root:

```bash
python -m pytest -q tests
python -m pytest -q \
  tests/test_postgres_authenticated_product_api.py \
  tests/test_postgres_load_concurrency_benchmark.py \
  tests/test_postgres_restart_recovery_campaign.py
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

On PowerShell, set the DSN with:

```powershell
$env:POSTGRES_OPERATIONAL_TEST_DSN = "postgresql://postgres:postgres@127.0.0.1:5432/academy_tractian"
```

## 5. Full browser acceptance

Chromium full-product acceptance remains a separate mandatory gate:

`.github/workflows/full-product-playwright.yml`

It starts PostgreSQL, the provider-free backend and Vite frontend, then exercises the real browser path. It also proves deterministic `npm ci`, typecheck, unit tests and build before Playwright.

Browser acceptance covers realtime run growth, safe drill-down, semantic-review/operational-value participant surfaces and responsive behavior without exposing raw private evaluator/runtime material.

## 6. Frozen provider-free campaigns

Historical expected identities remain immutable for their original scopes:

```text
EV-007  7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
EV-008  1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8
EV-011  cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e
DEMO    43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445
```

EV-007 covers failure safety, EV-008 repeated stability and EV-011 communication behavior. The final demo validates representative integrated outcomes and one controlled synthetic action path.

## 7. Current production-safety evidence

Additional P0 evidence is intentionally separate from frozen historical identities:

- authenticated identity + PostgreSQL RLS integration;
- blinded semantic-review and operational-value collection contracts;
- evaluator-only adaptive stopping diagnostic;
- load/concurrency aggregate campaign;
- PostgreSQL restart/recovery aggregate campaign.

Load evidence is descriptive only and does not establish production capacity/SLOs. Restart evidence verifies conservative persisted-state semantics only and does not establish RTO/RPO/HA/uptime.

## 8. Failure/recovery behavior

### Invalid arguments

B1 blocks before transport. Never convert the denied operation into invented success.

### Authorization/policy denial

Stop before consequential transport and preserve the denial in safe telemetry.

### Missing/conflicting evidence

Clarify, abstain or escalate. Do not fabricate certainty.

### Provider/decision-source failure

Do not manufacture a conclusion or action from malformed/unavailable output. Raw provider material remains private.

### Consequential action uncertainty

Once a durable idempotency claim is consumed, never delete/reuse it to manufacture retry eligibility. Ambiguity becomes `UNCERTAIN` pending external reconciliation.

### Process restart

Startup reconciliation is conservative:

```text
orphan runtime accepted/running    → interrupted
orphan action execution            → uncertain
custody EXECUTING                  → UNCERTAIN
ledger CLAIMED                     → UNCERTAIN
PENDING_CONFIRMATION               → preserved
completed / failed                 → preserved
```

A second startup is expected to perform zero additional recovery transitions. Restart never authorizes automatic replay.

## 9. Security/privacy

Never expose through browser/API/SSE/artifacts:

- provider secrets/tokens;
- account/auth headers;
- raw identity binding or signing secrets;
- benchmark/evaluator seed;
- raw provider prompt/response material;
- forbidden raw tool/observation bodies;
- private action arguments/idempotency keys;
- evaluator gold/oracles/private labels;
- hidden chain-of-thought.

The project-owned signed bearer is not an enterprise SSO/OIDC claim.

## 10. Operational diagnosis order

Diagnose the earliest failing boundary:

```text
request/auth context
→ tenant ownership/RLS
→ runtime preparation
→ decision source
→ controller decision
→ tool proposal
→ B1 validation
→ B2/B3 policy
→ transport
→ normalized observation/evidence
→ terminal outcome
→ trace validation
→ evaluator
→ safe projection
→ persistence
→ SSE
→ browser reducer/render
```

Do not mask one layer with retries/fallbacks from another.

## 11. Final presentation sequence

Recommended provider-independent demo:

```text
1. Mission Control / production state
2. submit representative industrial request
3. observe LIVE run + architecture/trace growth
4. inspect tool/policy/evidence path
5. inspect terminal operational conclusion
6. inspect evaluator after runtime completion
7. inspect output lineage / dynamic explorer
8. show clarification/abstain/escalation example
9. show governed pending action + explicit confirmation using synthetic profile
10. show provider evidence state: D01/D02 = NO_SELECTION
11. explain load and restart evidence with their explicit non-claim boundaries
```

Never make live provider availability a single point of presentation failure.

## 12. Final completion checklist

Before delivery:

- clean-clone reproduction green on exact final SHA;
- full-product Playwright green on exact final SHA;
- branch protection/final CI configured and verified;
- final benchmark/evidence bundle frozen;
- documentation commands match committed code;
- no secrets/private evaluator material in repo/artifacts/frontend;
- human-dependent claims remain marked `NOT READY` unless real data exists;
- provider state remains truthful (`NO_SELECTION` unless a frozen challenger actually wins);
- no last-minute framework/feature expansion without measured need;
- exact demo rehearsed on the presentation environment.

If a gate is not closed, report the exact boundary and limitation instead of broadening the claim.