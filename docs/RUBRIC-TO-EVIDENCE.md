# Academy × TRACTIAN — Rubric-to-Evidence Crosswalk

**Status:** ACTIVE reviewer navigation  
**Checkpoint:** 2026-09-05 production rebaseline  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Runbook:** [`FINAL-HANDOFF-RUNBOOK.md`](FINAL-HANDOFF-RUNBOOK.md)

This file is reviewer navigation, not a new source of authorization. Exact current state lives in `CURRENT-PROJECT-STATUS.md`; exact Definition of Done lives in `DELIVERY-ACCEPTANCE.md`; historical ADRs/results remain authoritative for their original scopes.

## 1. Fast review path

1. Read [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md) for what is implemented, blocked and explicitly not claimed.
2. Read [`ARCHITECTURE.md`](ARCHITECTURE.md) for the promoted current architecture.
3. Read [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md) for requirement/output mapping.
4. Run repository-level reproduction from [`FINAL-HANDOFF-RUNBOOK.md`](FINAL-HANDOFF-RUNBOOK.md).
5. Inspect frozen machine evidence under `research/results/` and relevant ADRs for exact historical experiment identities.
6. Distinguish repository-level evidence from remote-production evidence; the latter is still a P0 workstream where marked.

## 2. Academic excellence dimensions

| Dimension | Strongest current evidence | What it establishes | Current boundary |
|---|---|---|---|
| API integration quality | typed 18-tool registry, HTTP transport, conformance/integration tests | stable typed TRACTIAN tool boundary, validation and execution contracts | do not claim every real route/provider condition has been exercised in production |
| Technical coherence | `ARCHITECTURE.md`, ADR-004+, PostgreSQL/action/realtime implementations, required CI | controller/tool/evaluator separation, deterministic safety, PostgreSQL durable state, safe realtime | remote hosting/IAM/HA/capacity are not yet proved |
| Experiment clarity | `research/experiments/`, frozen manifests/results, ADRs | preregistered hypotheses, controlled variables, hard gates and negative outcomes | historical consumed experiments cannot be replayed merely to seek a better result |
| Result analysis quality | frozen provider-free campaigns, D01/D02 results, wake-up/load/recovery evidence, EDD machinery | quantitative failure/stability/provider/realtime analysis with explicit non-claims | human semantic/value evidence still requires real participants |
| Limitations / risks | `CURRENT-PROJECT-STATUS.md`, `DELIVERY-ACCEPTANCE.md`, runbook | production/provider/IAM/capacity/HA/human-data boundaries are explicit | no remote-production-readiness claim yet |
| Reproducibility | `final-ci-required`, clean-clone workflow, Playwright, lockfile, runbook | clean repository-level product reproduction and browser acceptance | provider-free CI is not remote provider/IAM evidence |
| Documentation | root README + canonical docs hub + architecture/status/plan/acceptance/runbook | one current source per question plus preserved history | frozen historical docs/results are context/evidence, not current truth |
| Demonstration quality | React control room + Playwright + safe trace/evidence/lineage + historical integrated scenarios | real product UI/runtime/persistence/evaluation path can be inspected | final production presentation should use the future remote deployed path, not local/provider-free serving |

## 3. TAPI / core product evidence

| Requirement / capability | Primary current evidence | Scope note |
|---|---|---|
| Agent + Evaluation integrated solution | `src/academy_tractian/runtime.py`, evaluation modules, product API, TAPI crosswalk | implemented in one repository/product path |
| 18-operation TRACTIAN integration | typed registry + transport/conformance tests | normalized typed contract |
| Contextualize / investigate | controller/runtime scenarios and traces | grounded tool/evidence path |
| Clarify / abstain | deterministic scenario/failure/communication evidence | explicit safe outcomes |
| Escalate / human handoff | escalation/communication campaign and product traces | structured handoff behavior |
| Consequential action | action custody/confirmation/idempotency/lease/fencing tests | governed supplied/test profile; no blanket customer mutation authorization |
| Tool selection / arguments | evaluator + schema/policy tests | deterministic validity where exact truth exists |
| Execution trajectory | `RunTrace`, timeline/trace graph, evaluator | inspectable structured process, no chain-of-thought claim |
| Evidence use | evidence projection/lineage + degraded evidence cases | complete/partial/conflict/unavailable behavior |
| Failure continuity | EV-007 + product fault/recovery tests | safe containment and conservative recovery |
| Stability | EV-008 + repeated-run machinery | repeated behavior evidence for frozen scope |
| Customer-safe communication | EV-011 + terminal outcome contracts | frozen provider-free communication evidence |
| Realtime observability | PostgreSQL observability store + LISTEN/NOTIFY wake-up + SSE + frontend | durable rows/cursors are truth; wake-up is not auth/correctness boundary |
| Cross-replica read-only handoff | PostgreSQL runtime handoff + generation fencing tests | repository-level distributed correctness for tested algorithm |
| Action ownership safety | non-transferable action lease + uncertainty/fencing tests | lost ownership → `UNCERTAIN`, no replacement replay |

## 4. Current architecture evidence

Promoted repository architecture:

```text
browser
→ trusted identity context
→ FastAPI
→ PostgreSQL RLS / durable operational state
→ runtime handoff / leases / generation fencing
→ RealtimeProductionRuntime
→ provider-neutral DecisionSource
→ AgentController
→ HarnessRunner
→ 18 typed TRACTIAN tools
→ deterministic safety boundaries
→ normalized evidence
→ terminal/action proposal
→ RunTrace / ProductionEvaluator
→ sanitized PostgreSQL observability/evaluation
→ durable cursor + LISTEN/NOTIFY wake-up
→ REST/SSE
→ React control room
```

Important current decisions:

- PostgreSQL is the promoted serving/observability/evaluation truth.
- DuckDB is dev/benchmark compatibility only.
- custom controller remains the promoted baseline.
- LangGraph/multi-agent/RAG/memory/MCP are `NO_CHANGE`/unpromoted absent a measured gap.
- historical Cloudflare/provider modules are preserved as experiment evidence, not current provider selection.

## 5. Provider/model evidence

Historical D01/D02 provider experiments are **complete**, not pending.

Current scientific decision:

**`NO_SELECTION`**

Neither candidate crossed the frozen promotion gates. Historical attempt/result/custody artifacts must remain immutable for their scope.

Current production gap:

- no production hosted model/provider is selected;
- the remote-production plan requires a new hosted-provider tournament under a new preregistered protocol;
- local model serving is not a production candidate under the current no-local-serving requirement.

Do not confuse “historical provider experiment completed” with “production provider selected.”

## 6. Evaluation evidence and human-data boundary

### Implemented

- deterministic structural/safety/trajectory evaluation;
- baseline/candidate EDD machinery;
- failure/stability/communication campaigns;
- semantic-review collector/rubric/protocol/source generation;
- operational-value collection + paired analysis machinery;
- evaluator-only adaptive-stopping replay diagnostic.

### Not yet claimable

- human semantic calibration;
- judge-vs-human reliability metrics;
- real manual-vs-assisted engineer-time savings;
- business-value/auto-resolution claims.

Those require real human observations and must remain `NOT READY` until collected.

## 7. Production-quality evidence: implemented vs missing

The project intentionally sets stronger production gates than the minimum assignment.

| Area | Current evidence | Disposition |
|---|---|---|
| PostgreSQL durable product state | real integration/concurrency/recovery tests | implemented in repository |
| Tenant RLS | non-owner/non-bypass role + cross-tenant SQL/API tests | implemented/tested |
| Realtime SSE/catch-up | PostgreSQL rows/cursor + wake-up + browser tests | implemented/tested |
| Cross-replica read-only ownership | lease/generation-fencing tests | implemented/tested algorithmically |
| Consequential action ownership | custody/idempotency/non-transferable lease/fencing | implemented/tested algorithmically |
| Frontend lock/build/E2E | committed lockfile + `npm ci` + Vitest/Playwright | implemented/gated |
| Stable product CI | `final-ci-required / required-gate` | implemented; repository branch protection still pending |
| Remote production deployment | none yet | P0 blocker |
| Standards-based end-user IAM | signed runtime bearer only | P0 blocker; OAuth/OIDC/SSO not yet implemented |
| Branch protection | GitHub reports `main.protected=false` | P0 external/repository-control blocker |
| Remote capacity/SLO | current CI load is descriptive | P0 evidence missing |
| Backup/restore/RTO/RPO/HA | repository recovery tests only | P0 evidence missing for deployed claims |
| Human semantic calibration | collection framework only | P1 human evidence missing |
| Operational value | analysis framework only | P1 human evidence missing |
| Production provider/model | historical `NO_SELECTION` | P1 new hosted tournament required |

## 8. Realtime / frontend evidence

Current product surfaces include or are structured around:

- Mission Control;
- Live Run Cockpit;
- Run Explorer;
- Timeline/Waterfall;
- Trace Graph;
- Architecture Explorer;
- Evidence Explorer;
- Output Lineage;
- Action Control;
- Tools & Policy analytics;
- Eval Lab;
- Provider Lab;
- Dynamic Data Explorer;
- Production Health.

The frontend consumes safe server-owned projections. It must not receive private action custody, evaluator gold, secrets, raw sensitive provider material or hidden chain-of-thought.

Final production acceptance adds remote build/deploy identity, IAM, capacity/recovery and operational-value evidence to these views where available.

## 9. Security/integrity evidence

Reviewer should verify:

- runtime identity/tenant/permissions are server-owned;
- PostgreSQL RLS is an independent tenant boundary;
- private benchmark/gold truth never enters runtime/model context;
- raw sensitive provider/action material is not exposed to browser/SSE;
- consequential actions require explicit governed confirmation;
- idempotency is persistent;
- action execution leases are non-transferable;
- ambiguous ownership loss becomes `UNCERTAIN`;
- stale responses cannot publish false terminal success;
- no blind replay occurs;
- provider/evaluator failures do not fabricate an operational conclusion.

The signed runtime bearer is not an enterprise IAM/SSO claim.

## 10. Reproduction evidence

Repository-level current gate:

```text
final-ci-required
  ├── clean-clone-full-product-reproduction
  ├── full-product-playwright
  ├── horizontal-runtime-handoff
  └── action-execution-lease
       ↓
  required-gate
```

Local/CI reproduction is documented in `FINAL-HANDOFF-RUNBOOK.md` and remains distinct from the future remote production operations path.

Historical research workflows remain available for provenance/manual reproduction but are not ordinary product-PR gates after repository cleanup.

## 11. Historical benchmark/C4 boundary

The exact evaluator-side score-row artifact with SHA-256

`b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`

remains externally unavailable for claims that require that exact historical material. Reconstruction/rescoring/substitution is forbidden. This does not invalidate already frozen evidence for other scoped analyses.

## 12. Reviewer rule

Treat every claim only within the scope of the exact evidence:

- provider-free acceptance ≠ live production provider quality;
- repository cross-replica tests ≠ deployed HA/RTO/RPO;
- signed runtime identity ≠ OIDC/SSO;
- safe supplied/test action ≠ blanket customer mutation authorization;
- semantic collection machinery ≠ human calibration;
- operational-value analysis code ≠ measured business value;
- historical D01/D02 completion ≠ production provider selection;
- green CI ≠ protected branch until GitHub enforcement is active.

Negative outcomes such as `NO_SELECTION`, `NO_CHANGE`, `REJECT` and `NOT READY` are valid evidence-backed results and must not be replaced by invented winners.
