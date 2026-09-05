# Academy × TRACTIAN — Current Project Status

**Status:** `READY_FOR_HARD_FREEZE` candidate / canonical human-readable state  
**Checkpoint:** 2026-09-05 BRT  
**Functional P0 baseline:** `d3bed06b132212c85b126f56708863d45f64e03e`  
**Post-merge gate:** `final-ci-required` run #386 / `required-gate = success`  
**Hard feature/visual/architecture freeze:** end of 2026-09-05  
**Final delivery:** 2026-09-08  
**P0 closure:** [`../research/p0-hard-freeze-closure-2026-09-05.md`](../research/p0-hard-freeze-closure-2026-09-05.md)

The current canonical-document rehearsal branch is documentation/evidence-only. It does not change runtime behavior, so `d3bed06b…` remains the accepted **functional** P0 baseline even if a later docs-only merge produces a newer `main` commit SHA.

## 1. Executive state

```text
updated TAPI scope                         Agent + Evaluation
production agent runtime                  IMPLEMENTED
production deterministic evaluator        IMPLEMENTED
TRACTIAN typed tool registry              18 operations
React operator control room               IMPLEMENTED
full-product Chromium E2E                 PASS / gated
clean-clone reproduction                  PASS / gated
stable final required CI                  PASS / required-gate

production serving persistence            PostgreSQL
production observability/evaluation       PostgreSQL
DuckDB production dependency              FALSE
PostgreSQL tenant RLS                     IMPLEMENTED / tested

read-only cross-replica handoff           IMPLEMENTED / generation-fenced
action execution lease                    IMPLEMENTED / non-transferable
lost consequential ownership              UNCERTAIN / no replacement replay
realtime wakeup                            LISTEN/NOTIFY + durable fallback
realtime durable truth                    PostgreSQL rows + sequence cursor

request authentication                    signed bearer HMAC-SHA256 v1
enterprise OIDC/SSO claim                  FALSE

D01/D02 provider experiments              COMPLETE / USD0
production provider/model                 NO_SELECTION
semantic human calibration                NOT_READY_HUMAN_DATA
engineer-time/business-value claim         NOT_READY_HUMAN_DATA
adaptive runtime stopping                 NOT_PROMOTED
orchestration framework migration          NO_CHANGE

load/concurrency evidence                 descriptive only
cross-replica algorithm correctness       PASS_EVIDENCED
production capacity/SLO claim             FALSE
deployed HA/RTO/RPO/uptime claim          FALSE
external exactly-once action claim        FALSE

branch protection enforcement             PENDING_EXTERNAL_ENFORCEMENT
last observed main.protected              false (2026-09-05)
last observed rulesets                    [] (2026-09-05)
C4 exact historical artifact              EXTERNALLY_BLOCKED
```

## 2. Exact accepted functional evidence

Accepted `main` functional baseline:

`d3bed06b132212c85b126f56708863d45f64e03e`

Post-merge `final-ci-required` run `33971230788` / run #386:

```text
clean-clone / reproduce-current-product                  success
full-product-browser / chromium-full-product              success
horizontal-runtime-handoff / postgres-horizontal-runtime  success
action-execution-lease / postgres-action-lease            success
required-gate                                             success
```

Inside clean clone:

- full Python suite passed with PostgreSQL enabled;
- promoted PostgreSQL P0 campaigns passed;
- ADR-004 regression passed;
- frozen EV-007 / EV-008 / EV-011 reproduced;
- historical final-delivery evidence validated;
- final handoff audit passed;
- final freeze bundle validator passed;
- frontend locked install/typecheck/tests/build passed;
- tracked repository mutation remained zero.

## 3. Promoted production topology

```text
browser
→ signed RuntimeContextProvider
→ FastAPI product API
→ PostgreSQL tenant RLS + shared serving state
→ runtime handoff work item / generation lease
→ RealtimeProductionRuntime
→ provider-neutral DecisionSource
→ AgentController
→ HarnessRunner
→ 18 typed TRACTIAN ToolSpecs
→ B1/B2/B3 deterministic boundaries
→ TRACTIAN transport
→ normalized evidence
→ FINAL / CLARIFY / ABSTAIN / ESCALATE / action proposal
→ RunTrace
→ post-runtime ProductionEvaluator
→ safe PostgreSQL projection
→ REST/SSE
→ LISTEN/NOTIFY wakeup + durable cursor fallback
→ React operator control room
```

Production PostgreSQL holds:

- run ownership/execution;
- tenant-scoped serving state;
- runtime private handoff payloads + leases/generations;
- action custody/idempotency/non-transferable execution leases;
- safe observability runs/events/evidence/evaluations;
- semantic-review and operational-value collection state.

Root production dependencies do not include DuckDB. DuckDB remains only in explicit dev/benchmark extras.

## 4. Read-only runtime ownership

Read-only investigation work may transfer between replicas after lease expiry.

Proven repository-level invariants:

- no double-claim of a healthy lease;
- healthy replica-A ownership is not interrupted by replica B;
- expired runtime lease may be claimed by B with a new generation;
- stale generation cannot renew/finalize/publish;
- recovered runtime may complete evaluation/terminal persistence;
- private handoff payload is removed after terminal completion.

## 5. Consequential-action ownership

Actions use intentionally asymmetric lease semantics:

```text
read-only runtime lease expiry  → takeover may be allowed
action lease expiry/loss        → UNCERTAIN; takeover/replay forbidden
```

Proven repository-level invariants:

- proposal is not execution;
- exact action payload remains private server-side custody;
- confirmation accepts opaque action identity + consent only;
- current authorization/kill switch are revalidated;
- persistent atomic idempotency claim precedes transport;
- healthy action on another replica is not a startup orphan;
- expired/missing stale action ownership converges to `UNCERTAIN`;
- action lease cannot transfer to another replica;
- stale late result cannot overwrite uncertainty;
- forced-expiry campaign issues exactly one external transport call;
- automatic replay remains false.

This is not an external exactly-once guarantee.

## 6. Realtime state

PostgreSQL observability rows and `(run_id, sequence)` cursors remain authoritative. One LISTEN connection per replica provides wakeup fan-out; missed NOTIFY is recovered through bounded durable cursor reads.

RT-WAKEUP-001 remains bounded CI evidence. A same-SHA passing rerun recorded:

```text
polling baseline event p95          52.10 ms
LISTEN/NOTIFY event p95             23.71 ms
candidate - baseline p95           -28.39 ms
idle durable-read ratio             0.375
idle durable-read reduction         62.5%
```

One earlier same-code sample was efficiency-inconclusive while all hard gates remained green. No threshold was relaxed. Do not convert CI latency into a production SLO.

## 7. Evaluation/human evidence

Delivered:

- deterministic structural/safety/trajectory evaluation;
- failure/stability/communication campaigns;
- operational-conclusion/value contracts;
- blinded semantic-review collection infrastructure;
- blinded operational-value collection + paired analysis;
- evaluator-only adaptive stopping diagnostic.

Not ready without real human data:

- semantic labels/adjudication;
- judge-vs-human agreement/error profile;
- real manual-vs-assisted timing observations;
- Engineer Minutes Saved/business-value claims.

`NOT_READY_HUMAN_DATA` is the correct final state until real observations exist.

## 8. Provider/model state

D01/D02 are consumed governed USD0 experiments. D02 improved multiple public metrics after the controlled 512→1024 completion-budget change, but both candidates remained below frozen M1/M4/M7 promotion gates.

Final P0 state:

**`NO_SELECTION`**.

D01/D02 must not be replayed. Any P1 provider/model comparison requires a new experiment ID, current factual revalidation, new preregistration and fresh authorization.

## 9. Runtime/framework state

Final P0 topology:

`custom AgentController + HarnessRunner + PostgreSQL durable handoff/custody/fencing`.

No LangGraph or alternate orchestration challenger demonstrated a material Pareto improvement. Final P0 decision is **`NO_CHANGE`**.

RAG/vector DB, multi-agent, persistent memory, Redis/Kafka/Temporal/MCP migration remain unjustified without a measured gap and challenger win.

## 10. Load/restart claim boundary

CI evidence supports measured queueing/latency/resource behavior, conservative restart semantics and tested cross-replica correctness.

It does not support claims of:

- production capacity/SLO/optimal worker sizing;
- deployed Cloud Run/Cloud SQL HA;
- RTO/RPO/uptime;
- autoscaling behavior;
- multi-region failover.

## 11. External blockers

### Branch protection

Stable CI context: `required-gate`.

Last observed 2026-09-05:

```text
main.protected = false
rulesets = []
```

The connected GitHub integration used here exposes reads but no administrative write for protection/rulesets. Enforcement remains a genuine external GitHub-admin dependency and must not be claimed until a later read proves it active.

### Historical C4 artifact

The exact required evaluator-side C4 artifact remains unavailable. Reconstruction, substitution and rescoring are forbidden. Current product CI does not resolve this historical blocker.

## 12. Delivery path

```text
P0 runtime/action distributed correctness       merged
P0 evidence closure                            merged
post-merge required-gate #386                  PASS
canonical active-doc drift cleanup             current pre-freeze work
hard feature/visual/architecture freeze        end 2026-09-05
final rehearsal/evidence inspection            2026-09-06/07
final delivery                                 2026-09-08
```

After the hard freeze, only delivery-blocking fixes with targeted regression may alter the delivery candidate.

## 13. Current non-claims

Do not claim:

- production provider/model selection;
- completed human semantic calibration;
- engineer minutes saved/business value without real human data;
- promoted adaptive runtime stopping;
- production capacity/SLO from CI load numbers;
- deployed HA/RTO/RPO/autoscaling/multi-region/uptime from repository tests;
- external exactly-once consequential side effects;
- enterprise OAuth/OIDC/SSO;
- need/superiority of LangGraph/RAG/multi-agent/etc. without controlled evidence;
- branch protection before GitHub reports it active;
- reconstruction/substitution of the missing C4 artifact.

## 14. State update rule

This file is the mutable current-state summary. Historical ADRs, frozen experiment evidence and historical reproduction artifacts remain immutable and authoritative for their original checkpoints. Documentation-only rehearsal commits do not change the accepted functional P0 baseline unless they alter runtime behavior.