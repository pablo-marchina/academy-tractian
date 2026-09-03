# Academy × TRACTIAN — Unified Delivery Plan

**Status:** ACTIVE / canonical execution plan  
**Checkpoint:** 2026-09-02 20:20 BRT  
**Final delivery:** 2026-09-08  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)

This is the canonical execution plan after the updated-TAPI / TRACTIAN-delivery review and the production-observability implementation cycle through PR #142. It replaces stale sequencing in older planning snapshots without rewriting frozen historical evidence.

## 1. Final objective

Deliver the strongest defensible **TRACTIAN Industrial Agent Operations Platform** under the actual updated TAPI, delivered package, partner guidance and repository P1–P4 principles.

The final system is not a demo stack. It is one production-oriented product containing:

1. a functional industrial agent;
2. the full typed TRACTIAN integration;
3. a quantitative/eval-driven agent evaluation framework;
4. governed technical experiments;
5. consequential-action safety and human confirmation;
6. genuine realtime safe observability;
7. an operator frontend exposing live architecture, trace, evidence, outputs, evaluation and health;
8. schema-driven quantitative analytics;
9. a reproducible production start/restart path;
10. evidence-backed technical documentation and limitations.

Hard constraints:

```text
external API / hosted-service project cost   USD 0
paid spillover                               FORBIDDEN
gold/evaluator-private leakage               0
credential/private-field leakage             0
unauthorized consequential actions           0
duplicate consequential actions              0
final delivery                               2026-09-08
```

## 2. Updated-TAPI interpretation

The updated TAPI describes the project objective as a solution containing both:

- construction of an industrial agent; and
- a framework/process/application for evaluating agent quality and reliability.

Therefore the final acceptance treats **Agent + Evaluation** as one combined product requirement, not as a choice between two disconnected tracks.

The final product must visibly cover the three customer-support modes:

```text
CONTEXTUALIZE
INVESTIGATE
EXECUTE
```

and the operational outcomes:

```text
FINAL / ORIENT
CLARIFY
ABSTAIN
ESCALATE
ACTION PROPOSAL / CONFIRMED ACTION
```

## 3. Engineering rules for the remainder of the project

### 3.1 Eval-Driven Development

Every material behavior/architecture change follows:

```text
requirement
→ evaluator / measurement design
→ frozen baseline
→ hypothesis
→ preregistered candidate
→ controlled implementation
→ repeated / sliced evaluation
→ diagnosis
→ Pareto decision
→ regression protection
```

No change is accepted because it merely looks better.

### 3.2 Quantitative before qualitative

Prefer rates, distributions, p50/p95, paired deltas, confidence intervals/effect sizes, pass/failure rates, resource usage and repeated-run stability whenever they are meaningful.

Qualitative judgment is reserved for dimensions that cannot be validly reduced to deterministic metrics, and any semantic judge used as a gate must be calibrated first.

### 3.3 Adaptive intelligence inside deterministic safety

Potentially adaptive:

- investigation depth;
- stopping;
- clarification;
- abstention;
- escalation;
- evidence-gathering strategy;
- provider/model routing only after multiple eligible providers exist.

Always deterministic:

- ToolSpec/schema validation;
- identity and evaluation seed ownership;
- authorization/resource scope;
- permissions;
- consequential-action confirmation;
- idempotency/no-replay;
- privacy/field deny-list;
- hard resource and execution caps.

### 3.4 Every material technology decision must be evidence-backed

Required sequence:

```text
decision question
→ requirement/risk mapping
→ systematic primary-source research
→ credible alternatives + NO_CHANGE/simple baseline
→ preregistered metrics/hard gates
→ controlled comparison
→ uncertainty/failure/production-fit analysis
→ Pareto decision
→ ADR/reversal trigger
```

`works` means at most `QUALIFIED`; final project choices should reach `PREFERRED` or `FROZEN` where feasible.

## 4. State entering this rebaseline

Already merged and green in `main` through PR #142:

- production provider-neutral runtime;
- 18-operation typed TRACTIAN ToolSpec integration;
- deterministic B1/B2/B3 safety envelope;
- provider-free deterministic evaluator and failure/stability campaigns;
- EDD baseline/candidate delta machinery;
- safe RunTrace projection;
- persistent DuckDB observability store;
- FastAPI product/read API;
- genuine runtime-time SSE with persisted catch-up;
- `POST /api/runs` request → runtime → evaluation product path;
- Live Run Cockpit;
- Run Explorer;
- Trace Graph;
- Architecture Explorer;
- Evidence Explorer;
- Output Lineage;
- Mission Control / Production Health;
- Tools & Policy analytics;
- Eval Lab;
- Provider D01/D02 Lab;
- schema-driven Dynamic Data Explorer;
- global run scope, cross-filter and drill-down;
- runtime/API/resource/SSE quantitative operability telemetry;
- provider/action kill-switch observability.

PR #143 is open and has passed the complete 16-workflow gate. It adds the production-capable two-phase consequential-action path and frontend Action Control.

D01 remains frozen:

```text
32 / 32 attempts complete
USD 0
2813.628464 observed Neurons
selection = NO_SELECTION
24 / 24 CLIENT_FAILURE at exact 512 completion ceiling
```

D02 remains prospective and unexecuted.

## 5. Critical path from this checkpoint

```text
A. merge #143 production actions
        ↓
B. D02 fresh post-reset preflight + single governed execution (#117)
        ↓
C. integrate D02 result / bounded provider state
        ↓
D. close semantic response-quality evaluation layer (#128)
        ↓
E. adaptive evidence/stopping/escalation experiment (#129)
        ↓
F. runtime/HITL materiality revalidation (#92)
        ↓
G. operational storage + deployment/restart hardening (#131)
        ↓
H. Playwright + lockfile + full integrated E2E (#114/#131)
        ↓
I. current documentation + clean reproduction
        ↓
HARD FEATURE / VISUAL / ARCHITECTURE FREEZE
```

Adaptive/runtime/storage candidates are promoted only if the controlled evidence supports them. `NO_CHANGE` is a valid and preferred result when the simple baseline remains on the best-supported Pareto frontier.

## 6. Gate A — merge production action path (#143 / #130)

Acceptance before merge:

- all repository workflows green;
- proposal never directly executes a consequential action;
- private custody is separated from public observability;
- browser confirmation accepts consent only, not tool args/permissions/idempotency;
- current authorization and host kill switch are revalidated at execution time;
- persistent atomic idempotency claim precedes transport;
- ambiguous execution becomes `UNCERTAIN` and is never blindly retried;
- confirmed action receives a separate realtime RunTrace + ActionEvaluator;
- Action Control follows the execution run using the same SSE/reducer path.

Do not weaken the frozen read-only `ProductionRuntime` or `ProductionEvaluator` contracts to achieve this.

## 7. Gate B — D02 provider diagnosis (#117)

Earliest possible reset boundary:

```text
2026-09-03T00:00:00Z
=
2026-09-02 21:00 America/Sao_Paulo
```

Reset alone is not authorization.

Before D02:

- fresh zero-use evidence for the new UTC day;
- Workers Free confirmed;
- Workers Paid disabled;
- no worker/app/background consumer on the target account;
- exclusive packet window;
- direct Workers AI route;
- no AI Gateway/prepaid path;
- valid short-lived receipt;
- no previous D02 custody/run collision.

Execute exactly once under the frozen D02 packet. If a provider attempt may have started and custody is `CLAIMED`/`UNCERTAIN`, do not replay.

Analyze:

- M1/M4/M7 and frozen hard gates;
- success/structured-decision/rubric rates;
- sanitized failure subtype;
- completion-cap hits at 1024;
- latency p50/p95;
- observed Neurons/cost;
- D01 vs D02 delta;
- Pareto selection / `NO_SELECTION`.

No architecture expansion follows automatically from a provider failure.

## 8. Gate C — semantic response-quality closure (#128)

The deterministic evaluator remains the primary safety/integrity layer. Add semantic evaluation only for TAPI dimensions not sufficiently captured deterministically:

- operational conclusion quality;
- evidence support / groundedness;
- unsupported-claim rate;
- escalation/handoff usefulness;
- customer-safe communication;
- completeness vs unnecessary verbosity where task-relevant.

Required architecture:

```text
Layer 1 — deterministic structural/safety/trajectory evaluation
Layer 2 — calibrated semantic evaluation where necessary
Layer 3 — human-labelled calibration / disagreement analysis
```

Before any semantic judge gates candidates:

- define rubric and task-level labels;
- create a small blind human-labelled calibration set without leaking evaluator-private data to runtime;
- compare judge vs human labels;
- quantify agreement/error by response-mode slice;
- reject judge metrics that are not sufficiently reliable;
- keep deterministic metrics authoritative wherever exact ground truth exists.

The final Eval Lab must display deterministic and semantic layers separately.

## 9. Gate D — adaptive evidence/stopping/escalation experiment (#129)

Baseline: current bounded controller with fixed hard turn/tool ceilings.

Candidates:

A. fixed execution budget vs adaptive investigation budget;  
B. fixed stopping vs evidence-sufficiency/marginal-gain stopping;  
C. fixed escalation vs calibrated risk × uncertainty × contradiction policy.

Hold constant wherever possible:

- provider/model/config;
- scenario groups;
- ToolSpecs and HarnessRunner;
- deterministic safety policy;
- evaluator definitions;
- hard execution caps.

Report overall + group/response-mode slices:

- task/terminal success;
- tool-selection and argument correctness;
- evidence support/coverage;
- unnecessary tool calls;
- trajectory length;
- clarification/abstention/escalation correctness;
- latency;
- tokens/Neurons where measured;
- repeated-run stability;
- safety hard gates.

Promote only a material Pareto improvement. Otherwise retain the fixed/simple baseline and record the negative result.

## 10. Gate E — runtime / HITL materiality revalidation (#92)

PR #143 introduces durable pending-action custody and an explicit human confirmation/resume workflow. This activates a legitimate runtime decision question that did not exist at the original P0 controller freeze.

Compare prospectively:

```text
A — current custom AgentController + private action custody
B — LangGraph-compatible durable/checkpoint/HITL runtime adapter
```

Only add a third candidate if systematic research identifies a materially distinct credible alternative.

Keep the following fixed:

- provider/model;
- ToolSpecs;
- HarnessRunner execution boundary;
- B1/B2/B3 and action safety;
- scenarios;
- evaluator;
- action payload/authorization semantics.

Measure:

- task/trace equivalence;
- HITL pause/resume correctness;
- process-restart recovery;
- duplicate-action rate;
- failure containment;
- latency/overhead;
- resource use;
- new dependency/runtime surface;
- implementation/maintenance complexity;
- clean reproduction;
- debuggability and trace clarity.

LangGraph enters production only if it provides measurable net benefit while preserving every hard safety/evaluation invariant. Otherwise `NO_CHANGE/custom` is frozen.

## 11. Gate F — operational persistence and deployment (#131)

Keep DuckDB as the current safe analytics store unless evidence says otherwise.

Separately evaluate the operational mutable-state role introduced by actions/HITL:

```text
A — current DuckDB single-process custody/idempotency baseline
B — local PostgreSQL operational state
```

Decision question: what storage topology is required for the production claim we will actually make?

If final claim remains explicitly single-process/single-node, the current baseline may remain sufficient. If the project claims concurrent multi-process recovery, the operational store must prove that capability.

Measure:

- concurrent confirmation/claim correctness;
- duplicate action rate;
- restart/crash recovery;
- transaction/atomicity behavior;
- read/write latency;
- setup and migration complexity;
- disk/memory footprint;
- clean checkout reproducibility;
- USD0 compliance.

Target separation if PostgreSQL materially wins:

```text
PostgreSQL → operational mutable state
DuckDB     → sanitized analytical telemetry
```

Do not migrate without the comparison.

Production start/recovery acceptance in the same gate:

- one documented product startup path (`docker compose` or equivalent);
- environment/config validation;
- secret injection from environment only;
- graceful shutdown;
- restart recovery;
- schema lifecycle/migrations where applicable;
- health/readiness/version/config endpoints;
- bounded concurrency/resource controls;
- provider/action kill switches;
- no demo-only service.

## 12. Gate G — frontend/browser E2E and reproducibility (#114/#131)

The frontend is already implemented; this gate changes it from a green build to browser-proved product acceptance.

Required package/install behavior:

- commit/freeze the frontend transitive dependency lockfile;
- use deterministic lockfile installation in CI (`npm ci` or equivalent);
- no unbounded dependency resolution in final reproduction.

Required Playwright E2E over the actual provider-free product path:

1. submit request via `POST /api/runs`;
2. observe genuine SSE events;
3. verify event ordering/idempotent UI;
4. disconnect and reconnect with persisted catch-up;
5. inspect Timeline/Trace Graph/Architecture path;
6. inspect Evidence Explorer + Output Lineage;
7. use global run scope and Dynamic Data Explorer drill-down;
8. verify Production Health values come from real telemetry;
9. exercise clarification/abstain/escalation/error/blocked-action states;
10. confirm a pending action in the production action profile and follow the separate realtime execution run;
11. verify terminal output only after real completion;
12. verify evaluation appears post-runtime only;
13. assert forbidden fields never appear in browser/API/SSE payloads;
14. test long/empty/error/unsupported-chart states and presentation viewport.

## 13. Gate H — production quantitative acceptance thresholds

PR #142 now provides real runtime/API/resource/SSE measurements. Use provider-free baselines to preregister acceptance targets before the final candidate/rehearsal results are examined.

At minimum report:

- startup/readiness time;
- runtime request and execution p50/p95;
- API/query p50/p95;
- observability publish/persistence overhead;
- runtime-event → persistence p50/p95;
- persistence → SSE delivery p50/p95;
- reconnect recovery rate/time;
- event-gap rate;
- logical duplicate rate;
- concurrent executor pressure;
- process CPU/load/RSS;
- provider failure/latency observations;
- TRACTIAN HTTP success/status distribution.

Do not create post-hoc numeric PASS targets from observed final results.

## 14. Frontend final product contract

The final UI is one native agent control room, not a marketing dashboard.

Required connected surfaces:

1. Mission Control;
2. Live Run Cockpit;
3. Run Explorer;
4. Timeline/Waterfall;
5. Trace Graph;
6. Architecture Explorer;
7. Evidence Explorer;
8. Output Lineage / Explain This Run;
9. Action Control;
10. Tools & Policy analytics;
11. Eval Lab;
12. Provider D01/D02 Lab;
13. Dynamic Data Explorer;
14. Production Health.

Every safe aggregate must drill toward exact safe run/event/evidence records where semantically meaningful.

`total observability` means all operationally relevant **safe** data, not secrets, raw sensitive bodies, evaluator-private truth or hidden chain-of-thought.

## 15. Schedule from this checkpoint

### 2026-09-02 — close current branch + D02 window

Before 21:00 BRT:

1. merge #143 after final green verification;
2. land this plan/status rebaseline;
3. prepare fresh D02 evidence paths without credentials/provider calls.

At/after 21:00 BRT:

4. verify current time/reset;
5. obtain fresh truthful D02 zero-use/free/no-paid/exclusive attestation;
6. issue fresh receipt;
7. execute D02 exactly once if every gate is valid;
8. analyze and integrate the D02 result.

Do not spend the D02 window on unrelated architecture experiments.

### 2026-09-03 — quality/evaluation + highest-value experiments

Priority order:

1. close semantic response-quality/calibration work under #128;
2. integrate Eval Lab result layers;
3. run #129 adaptive-policy experiment if the evaluator baseline is trustworthy;
4. freeze `PROMOTE / REJECT / INCONCLUSIVE` for adaptive candidate;
5. activate #92 runtime/HITL comparison only after the action path is merged and testable;
6. start #131 operational-storage comparison/deployment path.

No multi-agent/RAG/MCP/memory work unless one of these gates finds a measured requirement.

### 2026-09-04 — production hardening + browser E2E

- finish runtime/HITL and storage decisions or freeze `NO_CHANGE`;
- implement only the winning production candidate where necessary;
- lock frontend dependency graph;
- add Playwright full-product suite;
- finish production start/restart/config path;
- execute full safe state matrix in frontend;
- integrate D02/adaptive/runtime/storage decision evidence into UI/docs;
- presentation/accessibility/overflow polish only after functional gates are green.

### 2026-09-05 — dedicated integrated test/fix day

No planned feature expansion.

Run:

- complete TAPI requirement/evidence matrix;
- complete EDD scorecard;
- backend/runtime/action/storage regressions;
- API/SSE/security tests;
- Playwright real-run/reconnect/action flows;
- dynamic query/chart tests;
- architecture/lineage consistency;
- operability/latency/overhead acceptance;
- slow/disconnected client stress;
- restart/recovery tests;
- clean product startup rehearsal;
- documentation consistency audit.

Fix P0/P1 blockers only.

**HARD FEATURE + VISUAL + ARCHITECTURE FREEZE at end of 2026-09-05.**

### 2026-09-06 — clean reproduction and evidence freeze

From a clean checkout:

- install backend from pinned constraints;
- install frontend from lockfile;
- start the entire product using the documented production path;
- run complete Python/runtime/evaluator/action/observability suite;
- run frontend unit + Playwright E2E;
- execute provider-independent realtime request → evaluation path;
- verify restart/recovery;
- verify architecture/output lineage;
- freeze final metric/evidence bundle;
- update README/runbook/results/limitations to exactly match the product.

No open unbounded P0 is allowed after this phase.

### 2026-09-07 — final acceptance / presentation-machine rehearsal

- execute the exact normal product path end to end;
- verify live frontend/Action Control/health/data explorer;
- verify D01/D02 evidence;
- verify provider-independent safe fallback;
- verify all final decision records and limitations;
- no redesign;
- P0 delivery blockers only + targeted regression.

### 2026-09-08 — delivery

- smoke tests only;
- no same-day feature/architecture work;
- deliver frozen code, evidence and documentation;
- operate the real product during presentation;
- state `NO_SELECTION`, rejected adaptive/runtime/storage alternatives and limitations honestly when applicable.

## 16. Scope-cut rule under time pressure

Never cut:

1. updated-TAPI agent behavior;
2. evaluation framework / EDD evidence;
3. API/tool/action safety and evaluator isolation;
4. real request → runtime → tool → output → evaluation path;
5. genuine realtime observability;
6. Live Run / Trace / Architecture / Evidence / Output Lineage;
7. consequential-action safety path;
8. clean reproduction;
9. documentation matching actual state.

Cut/defer first:

1. an adaptive candidate that has not beaten baseline;
2. LangGraph/runtime migration if `NO_CHANGE` remains on the Pareto frontier;
3. PostgreSQL migration if single-process DuckDB satisfies the bounded production claim;
4. adaptive chart recommendation;
5. optional Grafana/OpenTelemetry/Redis/multi-instance claims;
6. additional chart types/exports;
7. multi-agent/RAG/MCP/persistent memory without measured need;
8. cosmetic polish beyond presentation usability.

## 17. Final completion statement

The project is complete only when a third party can, from a clean checkout, start the production-oriented system, submit a real support request, observe the real agent/tools/policies/evidence/architecture/output live, obtain a safe terminal result or governed action/escalation, inspect post-runtime evaluation and quantitative metrics, reproduce the accepted experiments, and understand why every material architecture/stack choice was selected or rejected from evidence rather than preference.
