# Academy × TRACTIAN — Rubric-to-Evidence Crosswalk

**Status:** ACTIVE / canonical reviewer navigation  
**Checkpoint:** 2026-09-05 BRT  
**Functional P0 baseline:** `d3bed06b132212c85b126f56708863d45f64e03e`  
**Post-merge gate:** `final-ci-required` run #386 / `required-gate = success`

This file is navigation, not a new authorization source. Exact state lives in [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md), acceptance semantics in [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md), and historical ADR/research artifacts remain authoritative for their original scopes.

## 1. Fast reviewer path

1. [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md) — exact current state, blockers and non-claims.
2. [`ARCHITECTURE.md`](ARCHITECTURE.md) — final P0 serving/runtime/action topology.
3. [`FINAL-HANDOFF-RUNBOOK.md`](FINAL-HANDOFF-RUNBOOK.md) — reproduction and presentation rehearsal.
4. [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md) — canonical Definition of Done.
5. [`../research/results/final-freeze-evidence-bundle-2026-09-04.json`](../research/results/final-freeze-evidence-bundle-2026-09-04.json) — machine-verified current/frozen artifact identities.
6. [`../research/results/final-handoff-acceptance-audit-2026-08-28.json`](../research/results/final-handoff-acceptance-audit-2026-08-28.json) — historical acceptance audit and exact C4 blocker.

## 2. Academic excellence dimensions

| Dimension | Strongest current evidence | Establishes | Boundary |
|---|---|---|---|
| API integration | TRACTIAN API conformance artifacts; typed registry; runtime/controller tests | 18 normalized typed operations behind one `HarnessRunner` boundary | do not claim live exercise of every route unless separately evidenced |
| Technical coherence | `ARCHITECTURE.md`; P0 closure; ADRs; PostgreSQL distributed gates | one integrated Agent + Evaluation product with deterministic safety and evidence-backed topology | repository-level correctness is not deployed HA |
| Experiment clarity | `research/experiments/`; benchmark integrity docs; D01/D02 decision | preregistration, fixed metrics, consumed-attempt accounting, explicit `NO_SELECTION` | D01/D02 cannot be replayed |
| Result analysis | EV-007/008/011; D01/D02 comparison; load/restart/realtime/distributed campaigns | failure, stability, communication, provider, resource and recovery analyses with explicit bounds | C4 exact continuation remains externally blocked |
| Limitations/risks | current status; acceptance; runbook; branch-protection contract | provider/human/HA/exactly-once/branch-protection limitations are explicit | no unconditional production-readiness claim |
| Reproducibility | clean-clone workflow; runbook; final freeze validator | clean checkout reproduces backend/eval/frontend/evidence with PostgreSQL and zero tracked mutation | provider-free product path; not cloud deployment proof |
| Documentation | README; architecture; plan; acceptance; runbook; this crosswalk | active docs agree with accepted final P0 topology | historical docs remain historical and may describe prior states |
| Demonstration | Chromium acceptance; provider-free demo; EV campaigns | real backend/frontend/realtime/action/evaluator paths without relying on live provider availability | synthetic/provider-free demo; zero real-customer mutation |

## 3. P0 capability coverage

| Requirement/capability | Primary evidence | Current disposition |
|---|---|---|
| Agent + Evaluation integrated solution | production runtime/evaluator + browser product | PASS_EVIDENCED |
| TRACTIAN API/tool integration | 18 typed ToolSpecs + HarnessRunner + contract tests | PASS_EVIDENCED |
| contextualize/investigate/finalize | runtime/controller + demo/EV evidence | PASS_EVIDENCED |
| clarify/abstain/escalate | runtime/controller + EV-011/browser states | PASS_EVIDENCED |
| deterministic safety | B1/B2/B3 + action/negative tests | PASS_EVIDENCED |
| consequential action proposal/confirmation | custody/idempotency/action RunTrace + browser E2E | PASS_EVIDENCED |
| tenant isolation | signed bearer + PostgreSQL RLS integration | PASS_EVIDENCED |
| read-only cross-replica handoff | horizontal-runtime-handoff reusable gate | PASS_EVIDENCED |
| action stale-owner fencing/no replay | action-execution-lease reusable gate | PASS_EVIDENCED |
| genuine safe realtime | PostgreSQL safe rows + LISTEN/NOTIFY + SSE/reconnect | PASS_BOUNDED |
| frontend control room | React/Vite + Chromium full-product acceptance | PASS_EVIDENCED |
| clean reproduction | clean-clone workflow | PASS_EVIDENCED |
| stable final CI | `final-ci-required` → `required-gate` | PASS_EVIDENCED |

## 4. Agent/evaluator evidence

| Capability | Evidence | Scope note |
|---|---|---|
| Industrial tool contract | API conformance + typed registry | 18 normalized operations under one stable agent-facing contract |
| Investigation | provider-free integrated traces/controller tests | grounded read-tool path |
| Clarification/abstention | EV/demo/controller tests | insufficient-context/no-safe-path behavior |
| Escalation | EV-011/demo/browser surfaces | structured human handoff |
| Consequential action | custody/idempotency/lease tests + browser controlled profile | explicit governed action; no blind retry |
| Failure continuity | EV-007 + runtime fault tests | fail-safe provider/tool/runtime behavior |
| Stability | EV-008 | repeated-run structural stability evidence |
| Communication | EV-011 | deterministic communication predicates; bounded by evaluator design |
| Per-run evaluation | ProductionEvaluator + safe evaluation rows | post-runtime evaluation, runtime cannot access private gold |
| Evaluation integrity | benchmark-integrity gates | leakage/exposure roles are explicit and protected |

## 5. Production/reliability evidence

| Area | Evidence | Disposition boundary |
|---|---|---|
| Serving storage | PostgreSQL production composition + operational store decision | production mutable + safe observability/evaluation persistence |
| DuckDB | `pyproject.toml` optional extras | dev/benchmark compatibility only, not serving dependency |
| Identity | signed bearer verification + RLS tests | project-owned auth envelope; not enterprise OIDC/SSO |
| Runtime handoff | PostgreSQL work-item/lease tests | tested cross-replica read-only takeover/fencing |
| Action ownership | non-transferable action lease tests | lost ownership → `UNCERTAIN`; replacement replay forbidden |
| Restart recovery | restart campaign + split recovery ownership | conservative repository recovery; not RTO/RPO/HA |
| Realtime | PostgreSQL rows + LISTEN/NOTIFY benchmark + browser reconnect | durable rows authoritative; hosted CI latency is not production SLO |
| Load/concurrency | provider-free PostgreSQL benchmark | descriptive only; not production capacity/worker sizing |
| Privacy | deny-list tests + safe projections | no credentials/raw action/private evaluator/CoT in browser contract |

## 6. Provider/model evidence

D01/D02 are complete consumed USD0 experiments.

Accepted D02 aggregate result:

| Candidate | M1 structured | M4 quality | success | stability | median latency | p95 latency | Promotion |
|---|---:|---:|---:|---:|---:|---:|---|
| GLM 4.7 Flash | 0.4375 | 0.3750 | 0.4375 | 0.2500 | 15329 ms | 38270 ms | FAIL M1/M4/M7 |
| Nemotron 3 120B A12B | 0.5625 | 0.5625 | 0.5625 | 0.5000 | 4218.5 ms | 9168 ms | FAIL M1/M4/M7 |

Both preserved safe-failure and trace-integrity aggregates at 1.0 in the accepted comparison, but neither crossed the frozen quality/stability hard gates.

Final state: **`NO_SELECTION`**.

D01/D02 must not be replayed. Any P1 provider/model work requires a new experiment ID and fresh preregistration.

## 7. Human semantic/value evidence

| Layer | Infrastructure | Missing evidence | State |
|---|---|---|---|
| Semantic response quality | blinded review/adjudication collection + source generation | real human labels + judge-vs-human agreement/error | NOT_READY_HUMAN_DATA |
| Engineer-time/business value | blinded MANUAL×ASSISTED collection + paired analysis | real operator timing/outcome observations | NOT_READY_HUMAN_DATA |

No final presentation may fabricate these observations.

## 8. Runtime/framework/adaptive decisions

| Decision | State | Evidence rule |
|---|---|---|
| Custom AgentController | `NO_CHANGE` / final P0 baseline | distributed P0 requirements solved without framework migration |
| LangGraph/framework swap | not promoted | no material Pareto challenger win |
| Adaptive runtime stopping | `NOT_PROMOTED` | evaluator-only diagnostic; no oracle-free runtime win |
| RAG/vector DB | not justified | no measured retrieval gap |
| Multi-agent | not justified | no measured topology gap |
| Persistent memory | not justified | no cross-request requirement demonstrated |
| Redis/Kafka/Temporal/MCP migration | not justified | PostgreSQL topology meets current tested P0 needs |

Negative/no-change decisions are valid EDD outcomes.

## 9. Browser/demo coverage

The provider-independent final demo + Chromium acceptance together cover:

- Mission Control / Production Health;
- live run submission;
- genuine SSE growth;
- trace/architecture/evidence/lineage;
- tool/policy transitions;
- clarify/abstain/escalate/error states;
- pending action + explicit confirmation;
- separate action execution run;
- post-runtime evaluation;
- dynamic analytics;
- forbidden-field absence;
- reconnect/catch-up;
- responsive states.

Use this path for presentation rehearsal; live provider availability must not be a single point of failure.

## 10. Exact final CI navigation

Functional P0 baseline:

`d3bed06b132212c85b126f56708863d45f64e03e`

Post-merge run #386 / `33971230788`:

```text
clean clone                       success
Chromium                          success
horizontal runtime handoff        success
action execution lease            success
required-gate                     success
```

A later docs-only merge does not change that functional topology but must independently pass the same gate before becoming the frozen delivery head.

## 11. External/bounded items

### Branch protection

Last observed on 2026-09-05:

```text
main.protected = false
rulesets = []
```

State: `PENDING_EXTERNAL_ENFORCEMENT`.

### Historical C4 artifact

The exact evaluator-side artifact required for C4 continuation remains unavailable. Reconstruction/substitution/rescoring is forbidden.

State: `EXTERNALLY_BLOCKED`.

## 12. Reviewer-safe final claims

Supported:

- integrated Agent + Evaluation product;
- PostgreSQL serving/realtime state;
- tested read-only cross-replica takeover/fencing;
- tested non-transferable action ownership/no replacement replay;
- deterministic safety/privacy boundaries;
- real provider-free Chromium product acceptance;
- clean reproducibility;
- D01/D02 controlled `NO_SELECTION`;
- explicit human/HA/external blockers.

Not supported:

- production provider/model selected;
- completed human semantic calibration;
- measured engineer-time savings;
- production capacity/SLO from CI;
- deployed HA/RTO/RPO/autoscaling/multi-region uptime;
- external exactly-once side effects;
- enterprise OIDC/SSO;
- LangGraph/RAG/multi-agent superiority;
- branch-protection enforcement while GitHub reports it disabled;
- reconstructed C4 evidence.