# Academy × TRACTIAN — Unified Delivery Plan

**Status:** ACTIVE / canonical final-delivery execution plan  
**Checkpoint:** 2026-09-05 BRT  
**Accepted P0 baseline:** `d3bed06b132212c85b126f56708863d45f64e03e`  
**Post-merge acceptance:** `final-ci-required` run #386 / `required-gate = success`  
**Hard feature/visual/architecture freeze:** end of 2026-09-05  
**Final delivery:** 2026-09-08  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)

This document owns the execution sequence from the final P0 closure through delivery. Earlier sprint sequencing remains recoverable in Git history and historical ADR/research artifacts; it is no longer the active plan.

## 1. Final objective

Deliver one defensible **TRACTIAN Industrial Agent Operations Platform** containing:

1. an industrial agent over the supplied TRACTIAN API;
2. deterministic safety/tool/action boundaries;
3. an integrated agent-evaluation framework;
4. governed technical experiments and explicit negative decisions;
5. genuine realtime safe observability;
6. a React operator control room exposing trace/evidence/evaluation/health;
7. reproducible PostgreSQL-backed serving/recovery paths;
8. evidence-honest documentation, limitations and presentation.

P0 hard constraints:

```text
external API/hosted-service project cost     USD 0
paid spillover                               FORBIDDEN
gold/evaluator-private leakage               0
credential/private-field leakage             0
unauthorized consequential actions           0
automatic consequential-action replay        0
final delivery                               2026-09-08
```

## 2. Frozen engineering rules

Material behavior/architecture changes follow EDD:

```text
requirement
→ evaluator/metric
→ frozen baseline
→ preregistered hypothesis/candidate
→ controlled implementation
→ repeated/sliced comparison
→ uncertainty/failure analysis
→ Pareto decision
→ regression protection
```

Always deterministic:

- authentication/tenant/permissions;
- ToolSpec/schema validation;
- resource/action authorization;
- consequential-action confirmation;
- persistent idempotency/no-replay;
- action ownership fencing;
- privacy/field deny-list;
- gold/evaluator-private boundary;
- hard execution/resource caps.

No technology enters P0 because it is fashionable. RAG, vector DB, Redis, Kafka, Temporal, multi-agent, MCP migration, LangGraph or provider routing require a measured gap and a challenger win.

## 3. Accepted P0 state

Merged and post-merge green:

```text
AgentController + HarnessRunner runtime                  accepted
18 typed TRACTIAN operations                             accepted
deterministic evaluator/failure/stability campaigns      accepted
PostgreSQL tenant RLS                                    accepted
PostgreSQL shared serving persistence                    accepted
PostgreSQL safe observability/evaluation                 accepted
PostgreSQL LISTEN/NOTIFY wakeup + durable fallback       accepted
read-only cross-replica lease takeover/fencing           accepted
action custody/idempotency/non-transferable lease        accepted
React operator control room                              accepted
full Chromium product acceptance                         accepted
clean-clone reproduction                                 accepted
final freeze bundle validator                            accepted
required-gate                                            success
```

Provider/model state remains `NO_SELECTION`. Semantic human calibration and engineer-time value remain `NOT_READY_HUMAN_DATA`. Adaptive stopping remains not promoted.

## 4. Distributed-runtime decision frozen for P0

### Read-only runtime work

- durable PostgreSQL work item;
- expiring lease;
- generation/fencing token;
- expired work may transfer to another replica;
- stale generation cannot renew/finalize/publish.

### Consequential actions

- private custody + explicit confirmation;
- persistent idempotency claim before transport;
- non-transferable action execution lease;
- stale/lost ownership → `UNCERTAIN`;
- no replacement transport attempt after lease loss;
- stale result cannot overwrite uncertainty.

This supports repository-level cross-replica correctness claims for the tested algorithms, not deployed HA/RTO/RPO/exactly-once external side effects.

## 5. Provider/model state

D01/D02 are complete consumed governed experiments:

- cash cost: USD0;
- D02 improved multiple metrics over D01;
- both candidates still failed frozen M1/M4/M7 promotion gates;
- selection: `NO_SELECTION`.

D01/D02 must not be replayed.

Any future provider/model work is **P1**, starts only after the delivery freeze path is secured, and requires:

```text
new experiment ID
→ current primary-source provider/model/cost verification
→ new candidate eligibility decision
→ new preregistered population/request/budget/metrics
→ provider-free validator/tests
→ explicit live authorization before attempt 1
```

No P1 provider campaign may mutate the frozen P0 delivery candidate.

## 6. Human-dependent evidence

### Semantic calibration

Infrastructure exists, but production semantic gating remains `NOT_READY_HUMAN_DATA` until:

- real blinded human labels exist;
- two-reviewer/adjudication protocol is executed;
- judge-vs-human agreement/error is measured by relevant slices;
- an explicit promotion decision is recorded.

### Operational/business value

Collection and paired analysis exist, but no Engineer Minutes Saved/business-value claim is allowed until real operator timing/outcome observations exist.

Absent real data, `NOT READY` is the correct final state.

## 7. Hard-freeze path — 2026-09-05

Before the end-of-day freeze:

1. finish canonical documentation drift cleanup;
2. repin/validate the final evidence bundle if canonical artifacts change;
3. run clean clone + Chromium + horizontal runtime + action lease + `required-gate` on the exact final head;
4. merge only if all hard gates are green;
5. verify the post-merge `required-gate` on exact `main`;
6. record the final baseline SHA;
7. freeze feature set, visual/information hierarchy and runtime→telemetry→frontend contracts.

After that point, no feature/framework/provider expansion enters the delivery branch.

## 8. Rehearsal — 2026-09-06/07

Run the final provider-independent product path on the intended presentation environment.

Required rehearsal sequence:

```text
request
→ live run
→ architecture/trace growth
→ typed tool proposal
→ deterministic policy
→ TRACTIAN transport metadata
→ safe evidence
→ terminal/clarify/abstain/escalation
→ governed action proposal/confirmation where relevant
→ completed RunTrace
→ post-runtime evaluation
→ output lineage
→ Production Health
→ dynamic analytics
→ D01/D02 + architecture-decision evidence
```

Rehearse multiple outcome/failure classes; do not depend on live provider availability.

Inspect:

- `/health` and `/ready` truthfulness;
- tenant isolation;
- SSE disconnect/reconnect/catch-up;
- action confirmation + separate execution run;
- forbidden-field absence;
- long/empty/error states;
- responsive presentation viewport;
- final docs/commands against committed code;
- exact evidence links/SHAs.

## 9. Branch protection

Desired stable required status: `required-gate`.

Last observed GitHub state on 2026-09-05:

```text
main.protected = false
rulesets = []
```

The connected repository integration in this workstream has no branch-protection write action. Applying enforcement therefore remains an external GitHub-admin task. Until a subsequent read proves protection active, delivery documentation must say `PENDING_EXTERNAL_ENFORCEMENT`.

## 10. C4 historical blocker

The exact evaluator-side C4 artifact with required SHA-256 remains externally unavailable. Reconstruction, substitution and rescoring are forbidden.

The final delivery must preserve this blocker explicitly; current product CI does not resolve it.

## 11. Final delivery — 2026-09-08

Delivery package/presentation must show:

- integrated Agent + Evaluation scope;
- actual PostgreSQL serving architecture;
- cross-replica read-only takeover vs non-transferable action fencing;
- deterministic safety/tool/action boundaries;
- genuine safe realtime path;
- browser acceptance and reproducibility;
- D01/D02 `NO_SELECTION` evidence;
- adaptive/runtime/storage decisions, including negative `NO_CHANGE`/not-promoted outcomes;
- human-data limitations;
- branch-protection/C4 external blockers;
- exact final SHA and green required-gate evidence.

## 12. Delivery-blocker rule after freeze

A post-freeze change is allowed only if all are true:

1. it blocks reproducibility, correctness, safety, evidence truthfulness or presentation of an already-frozen requirement;
2. the change is the smallest viable fix;
3. no new feature/architecture/provider scope is introduced;
4. targeted regression is added/run;
5. full required-gate is green on the new exact SHA;
6. affected evidence pins are updated without weakening validators.

## 13. Explicitly deferred P1

Deferred beyond the frozen delivery candidate:

- new provider/model benchmark;
- adaptive provider routing;
- LangGraph/framework challenger;
- broader OpenTelemetry export standardization;
- additional cloud/IaC deployment proof;
- managed enterprise identity;
- any retrieval/memory/multi-agent layer without a measured product gap.

P1 cannot be used to justify destabilizing a complete, evidence-backed P0 immediately before delivery.