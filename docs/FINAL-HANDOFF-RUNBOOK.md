# Academy × TRACTIAN — Final Handoff Runbook

**Status:** ACTIVE / canonical final-P0 operational runbook  
**Checkpoint:** 2026-09-05 BRT  
**Accepted baseline:** `d3bed06b132212c85b126f56708863d45f64e03e`  
**Post-merge acceptance:** `final-ci-required` run #386 / `required-gate = success`  
**Final delivery:** 2026-09-08

This runbook is subordinate to [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md), the P0 closure addendum and frozen experiment evidence.

## 1. Promoted provider-free product path

```text
signed bearer identity
→ FastAPI product API
→ PostgreSQL tenant RLS + shared serving state
→ runtime handoff queue / lease generation
→ RealtimeProductionRuntime
→ provider-neutral DecisionSource
→ AgentController
→ HarnessRunner
→ 18 typed TRACTIAN tools
→ B1/B2/B3 deterministic boundaries
→ normalized evidence
→ terminal / escalation / action proposal
→ RunTrace + post-runtime evaluator
→ safe PostgreSQL observability/evaluation rows
→ REST/SSE
→ LISTEN/NOTIFY wakeup + durable cursor fallback
→ React operator control room
```

Provider-free reproduction performs no live provider call and no real-customer mutation.

## 2. Consequential actions

```text
proposal
→ deterministic validation
→ PostgreSQL private custody
→ PENDING_CONFIRMATION
→ authenticated operator confirms opaque action_id
→ current authorization + kill switch revalidated
→ persistent atomic idempotency claim
→ non-transferable PostgreSQL action execution lease
→ exact custodied transport attempt
→ lease-fenced custody/ledger/observability/terminal state
→ action RunTrace + ProductionActionEvaluator
```

If action ownership is lost, the attempt converges to `UNCERTAIN`; another replica does **not** acquire the action lease and does not start a replacement transport attempt.

Do not describe this as external exactly-once. The external TRACTIAN API would need to participate in a common idempotency/fencing protocol for that stronger guarantee.

## 3. Prerequisites

Canonical CI toolchain:

- Python 3.11
- Node 24
- PostgreSQL 18
- frontend dependencies from committed `frontend/package-lock.json`

Python test/rehearsal install:

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

Production root dependencies do not require DuckDB. The `dev` extra installs DuckDB only for historical/test compatibility.

## 4. Canonical automated reproduction

Current-product reproduction:

`.github/workflows/clean-clone-full-product-reproduction.yml`

Historical immutable reproduction:

`.github/workflows/final-delivery-provider-free-reproduction.yml`

The current clean-clone workflow executes:

```text
1. clean checkout verification
2. Python/E2 install
3. full `tests` suite with PostgreSQL enabled
4. promoted PostgreSQL identity/RLS/load/restart regressions
5. distributed runtime-handoff/action-lease regressions through current suite
6. ADR-004 controller regression
7. EV-007 failure campaign
8. EV-008 stability campaign
9. EV-011 communication campaign
10. historical final-delivery validation
11. final handoff audit
12. final freeze bundle validation
13. frontend `npm ci`
14. frontend typecheck/tests/production build
15. tracked repository mutation check = 0
```

Do not alter frozen identities, historical workflow blobs or validator rules merely to make a gate pass. Diagnose the implementation/evidence mismatch.

## 5. Manual provider-free rehearsal

Start PostgreSQL 18 and set:

```text
POSTGRES_OPERATIONAL_TEST_DSN=postgresql://postgres:postgres@127.0.0.1:5432/academy_tractian
```

PowerShell:

```powershell
$env:POSTGRES_OPERATIONAL_TEST_DSN = "postgresql://postgres:postgres@127.0.0.1:5432/academy_tractian"
```

From repository root:

```bash
python -m pytest -q tests
python -m pytest -q \
  tests/test_postgres_authenticated_product_api.py \
  tests/test_postgres_load_concurrency_benchmark.py \
  tests/test_postgres_restart_recovery_campaign.py \
  tests/test_postgres_multi_instance_product.py \
  tests/test_postgres_action_execution_lease.py
python -m pytest -q research/e2/tests/test_controller.py
python scripts/validate_ev007_failure_campaign.py
python scripts/validate_ev008_stability_campaign.py
python scripts/validate_ev011_communication_campaign.py
python scripts/validate_delivery_reproduction.py
python scripts/validate_final_handoff_audit.py
python scripts/validate_final_freeze_bundle.py
cd frontend
npm ci --ignore-scripts --no-audit --no-fund
npm run typecheck
npm test
npm run build
```

The exact set may be broader inside CI; the clean-clone workflow remains authoritative.

## 6. Browser acceptance

Mandatory reusable gate:

`.github/workflows/full-product-playwright.yml`

It starts PostgreSQL, the provider-free production backend and the Vite frontend, then runs Chromium against the real product path.

Acceptance covers, among other surfaces:

- live request/runtime progression;
- genuine SSE event ordering;
- reconnect/cursor catch-up;
- trace/architecture/evidence/lineage drill-down;
- post-runtime evaluator timing;
- tenant isolation;
- pending/confirmed action flow in controlled profile;
- forbidden-field absence;
- responsive/empty/error/long-content states.

## 7. Stable aggregate CI gate

`.github/workflows/final-ci-required.yml` exposes `required-gate`.

It requires all four reusable jobs:

```text
clean-clone reproduction
Chromium full-product acceptance
horizontal read-only runtime handoff
action execution non-transferable lease
```

Latest accepted post-merge evidence at this checkpoint:

```text
main SHA       d3bed06b132212c85b126f56708863d45f64e03e
run            final-ci-required #386 / 33971230788
required-gate  success
```

GitHub branch-protection enforcement is separate. Last observed repository state remains `main.protected=false`, `rulesets=[]`.

## 8. Read-only runtime recovery

Read-only runtime work may move between replicas after lease expiry.

Expected semantics:

```text
healthy owner A               → B cannot claim/interfere
expired owner A               → B may claim a new generation
stale owner/generation A      → cannot renew/finalize/publish
recovered owner B             → may continue to evaluator/terminal state
terminal run                  → private handoff payload removed
```

This is different from consequential actions and must remain different.

## 9. Action ownership/recovery

Action recovery authority belongs to the action lease subsystem, not the read-only runtime handoff reconciler.

Expected semantics:

```text
PENDING_CONFIRMATION                  → preserved
accepted setup + no lease, within grace → temporarily preserved
running + no lease                    → ownership lost / UNCERTAIN
healthy remote action lease           → not an orphan
expired/stale action lease            → UNCERTAIN
claimed ledger on lost ownership      → UNCERTAIN
late stale terminal result            → cannot overwrite UNCERTAIN
automatic replay                      → forbidden
```

A second restart/reconciliation should not manufacture new transport eligibility.

## 10. Failure diagnosis order

Diagnose the earliest failing boundary:

```text
request/auth context
→ tenant ownership/RLS
→ runtime work-item ownership
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
→ safe PostgreSQL projection
→ durable event sequence
→ LISTEN/NOTIFY wakeup/fallback
→ SSE
→ browser reducer/render
```

For actions, additionally inspect:

```text
custody
→ confirmation authorization
→ idempotency claim
→ action execution lease owner/generation
→ transport
→ fenced terminal persistence
```

Do not mask one layer with retries/fallbacks from another.

## 11. Security/privacy rehearsal

Never expose through browser/API/SSE/artifacts:

- provider secrets/tokens;
- account/auth headers;
- raw identity binding/signing secrets;
- benchmark/evaluator seed;
- raw provider prompt/response;
- forbidden raw tool/observation bodies;
- private action args/idempotency keys;
- evaluator gold/oracles/private labels;
- hidden chain-of-thought.

The project-owned signed bearer is not enterprise OAuth/OIDC/SSO.

## 12. Frozen provider/evaluation state

D01/D02 are consumed governed experiments and remain `NO_SELECTION`. Do not replay them to seek a preferred winner.

Human semantic calibration and engineer-time/business-value layers remain `NOT_READY_HUMAN_DATA` until real blinded labels/adjudication or real timing observations exist. Do not fabricate them for the presentation.

Adaptive stopping remains evaluator-only and not promoted.

## 13. Presentation rehearsal sequence

Recommended provider-independent flow:

```text
1. Mission Control / Production Health
2. submit representative industrial request
3. observe LIVE run and architecture/trace growth
4. inspect typed tool + policy + evidence path
5. inspect terminal operational conclusion
6. inspect post-runtime evaluation
7. inspect output lineage / Dynamic Data Explorer
8. show clarify / abstain / escalation path
9. show governed pending action + explicit confirmation in synthetic profile
10. explain read-only takeover vs non-transferable action lease
11. show D01/D02 = NO_SELECTION
12. explain load/restart/cross-replica evidence and non-claims
```

Never make live provider availability a single point of presentation failure.

## 14. Final completion checklist

Before delivery:

- final `main` SHA recorded;
- clean-clone green on that SHA;
- Chromium green on that SHA;
- horizontal runtime gate green;
- action lease gate green;
- `required-gate` green;
- final freeze bundle validates;
- canonical README/architecture/plan/acceptance/runbook match committed code;
- historical frozen reproduction/evidence remains unmodified;
- no secrets/private evaluator material in repo/artifacts/frontend;
- human-dependent claims stay `NOT READY` unless real data exists;
- provider stays `NO_SELECTION` unless a new frozen challenger actually wins;
- no last-minute framework/feature expansion after hard freeze;
- demo rehearsed on presentation environment;
- branch protection either verified active or explicitly reported pending external enforcement;
- missing exact C4 artifact explicitly remains externally blocked.

If a gate is not closed, report the exact boundary instead of broadening the claim.