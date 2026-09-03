# Academy × TRACTIAN — Current Project Status

**Status:** ACTIVE / sole canonical human-readable state  
**Checkpoint:** 2026-09-02 20:20 BRT  
**Final delivery:** 2026-09-08  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)

## 1. Executive status

```text
UPDATED TAPI scope                          Agent + Evaluation in one solution
external API/hosted-service project cost   USD 0 hard constraint
production agent runtime                   IMPLEMENTED
production deterministic evaluator         IMPLEMENTED
EDD baseline/candidate gate                 IMPLEMENTED
TRACTIAN typed tool registry                18 operations
standalone wheel reproduction               PROVED

safe observability projection               IMPLEMENTED
DuckDB telemetry/read model                 IMPLEMENTED
FastAPI product/read API                     IMPLEMENTED
POST /api/runs request→evaluation path       IMPLEMENTED
runtime-time SSE + reconnect/catch-up        IMPLEMENTED
Live Run Cockpit                             IMPLEMENTED
Run Explorer / Trace Graph                   IMPLEMENTED
Architecture Explorer                        IMPLEMENTED
Evidence Explorer / Output Lineage           IMPLEMENTED
Mission Control / Production Health          IMPLEMENTED
Tools & Policy / Eval Lab                    IMPLEMENTED
Provider D01/D02 Lab                         IMPLEMENTED
Dynamic Data Explorer + cross-filter         IMPLEMENTED
quant runtime/API/resource/SSE telemetry     IMPLEMENTED

production consequential actions             PR #143 OPEN / 16-workflow gate green
action frontend control/follow-run           PR #143 OPEN / implemented

D01 Cloudflare live comparison               COMPLETE
D01 attempts                                 32 / 32 completed
D01 actual cash cost                         USD 0.00
D01 observed Neurons                         2813.628464
D01 selection                                NO_SELECTION
D01 raw provider material persisted          NO
D01 CLIENT_FAILURE at 512-token ceiling      24 / 24

D02 completion cap                           1024
D02 worst-case packet                        9352.805376 Neurons
D02 provider-free/live executor              MERGED / VALIDATED
D02 live result                              NOT YET EXECUTED

semantic response-quality calibration        P0/P1 GAP / #128
adaptive evidence/stopping policy             P1 EXPERIMENT / #129
runtime/HITL final architecture               REVALIDATION REQUIRED / #92
operational storage topology                  REVALIDATION REQUIRED / #131
Playwright full-product E2E                   NOT YET CLOSED
frontend lockfile deterministic install       NOT YET CLOSED
production deployment/restart path            NOT YET CLOSED / #131
final integrated freeze                       NOT YET DONE / #114
```

## 2. Updated-TAPI interpretation

The latest TAPI is the formal source for scope. It describes the objective as a solution containing both:

- a functional industrial agent capable of interpreting requests, consulting the provided API and conducting appropriate actions; and
- a framework/process/application for evaluating agent quality and reliability.

Every delivery also requires API integration, a technical experiment and documented results.

The project therefore treats Agent + Evaluation as one integrated P0 product rather than two independent optional tracks.

## 3. Delivered production path on main

Current merged main path:

```text
user request
→ POST /api/runs
→ trusted RuntimeContextProvider
→ RealtimeProductionRuntime.prepare()
→ genuine persisted run_started
→ background production execution
→ DecisionSource
→ AgentController
→ HarnessRunner
→ typed 18-operation ToolSpec registry
→ deterministic B1/B2/B3
→ TRACTIAN transport
→ normalized observation/evidence
→ FINAL / CLARIFY / ABSTAIN / ESCALATE
→ RunTrace
→ ProductionEvaluator
→ safe evaluation projection
→ DuckDB read model
→ FastAPI REST/SSE
→ React operator control room
```

The browser receives only safe projected telemetry. Raw RunTrace, credentials, identity binding, evaluation seed, forbidden raw provider/tool/observation material and evaluator-private truth remain outside the browser boundary.

## 4. Realtime / frontend state

The previous documentation statement that the frontend/observability were merely planned is obsolete.

Delivered in main:

- genuine event-time safe projection rather than post-run fake replay;
- persistent safe telemetry;
- Last-Event-ID catch-up/reconnect;
- idempotent browser reducer;
- Live Run Cockpit;
- historical Run Explorer;
- actual-event Trace Graph;
- versioned Architecture Manifest + active-path view;
- Evidence Explorer;
- Output Lineage / source labels;
- Mission Control / Production Health;
- Tools/Policy analytics;
- post-runtime Eval Lab;
- D01/D02 provider lab;
- Dynamic Data Explorer with allow-listed query contract;
- global run scope + drill-down/cross-filter;
- runtime/API/resource/SSE quantitative telemetry.

Measured Health v3 includes runtime request/execution latency, API/query latency, CPU/load/RSS, observability overhead, SSE client/reconnect/integrity signals, executor pressure, provider/adapter passive operability and host-owned kill switches. Thresholds remain explicitly not preregistered until baseline-derived targets are frozen.

## 5. Consequential action state

PR #143 implements a prospective two-phase production action path without weakening the frozen read-only runtime:

```text
agent proposes action
→ deterministic permission/scope/schema/justification validation
→ private persistent action custody
→ PENDING_CONFIRMATION
→ authenticated operator confirms opaque action_id
→ current authorization + host action kill switch revalidated
→ persistent atomic idempotency claim
→ exact custodied action executes through HarnessRunner/B2
→ accepted=true semantics
→ separate realtime action RunTrace
→ ProductionActionEvaluator
```

Hard properties implemented in the PR:

- browser cannot inject action args, permissions, identity, resource scope or idempotency key during confirmation;
- raw action payload/idempotency stay in private custody, not the public observability store;
- ambiguous post-claim failure becomes `UNCERTAIN` and is not automatically retried;
- requester isolation returns 404 instead of existence disclosure;
- action execution has a separate realtime run that uses the same SSE/frontend trace path;
- the existing read-only ProductionEvaluator remains unchanged.

Current status: PR #143 is still open, but its current head passed the complete 16-workflow repository gate.

## 6. D01 result and D02 boundary

D01 frozen result:

```text
GLM CLIENT_FAILURE                16 / 16 at 512 output tokens
Nemotron CLIENT_FAILURE            8 / 8 at 512 output tokens
all CLIENT_FAILURE                24 / 24 at exact 512 ceiling
Nemotron accepted outputs          7, 297..495 output tokens
Nemotron RESPONSE_PAYLOAD_INVALID  1, 476 output tokens
```

Both candidates failed frozen quality/stability gates. `NO_SELECTION` remains the valid result.

D02 changes only:

```text
max_completion_tokens   512 → 1024
failure diagnostics     generic code + sanitized subtype
```

Full worst-case packet:

```text
GLM       1300.377600 Neurons
Nemotron  8052.427776 Neurons
total     9352.805376 Neurons
```

Earliest reset boundary is 2026-09-03T00:00:00Z / 2026-09-02 21:00 BRT. Reset is not authorization: fresh same-day zero-use/free/no-paid/exclusive/direct-route evidence and a valid receipt remain mandatory before the one governed execution.

## 7. Evaluation state

Strong current layers:

- deterministic structural/safety/trajectory evaluation;
- scenario runner and failure/stability campaigns;
- tool selection/argument/trace/provenance checks;
- provider experiment public rubric;
- group-aware candidate-vs-baseline EDD machinery;
- paired/bootstrap-style comparison support where applicable;
- hard safety/integrity merge gates.

Remaining material gap: close the explicit TAPI `response quality` dimension where deterministic traces alone are insufficient.

Target under #128:

```text
Layer 1 deterministic evaluator
Layer 2 calibrated semantic evaluator where needed
Layer 3 human-labelled calibration / disagreement analysis
```

No LLM judge may gate production candidates until its agreement/error profile against human labels is measured and acceptable.

## 8. Adaptive policy state

Current fixed/bounded controller remains the baseline.

Issue #129 is the authorized adaptive candidate area:

- adaptive investigation budget;
- evidence-sufficiency/marginal-gain stopping;
- calibrated risk × uncertainty × contradiction escalation.

Deterministic safety, auth, schema, identity, confirmation, idempotency and privacy boundaries cannot become adaptive.

Adaptive behavior is promoted only if it materially improves the quality/reliability/efficiency Pareto frontier under #128 without critical regressions.

## 9. Runtime/HITL materiality state

ADR-004 froze the custom AgentController only for the original P0 controller scope, when durable cross-process HITL/checkpoint recovery was not required.

The new two-phase pending-action/confirmation workflow creates a legitimate new P1 materiality question.

Issue #92 must now prospectively compare at minimum:

```text
current custom controller + action custody
vs
LangGraph-compatible persistent checkpoint/HITL adapter
```

with provider, ToolSpecs, HarnessRunner, safety semantics, scenarios and evaluator held constant.

No migration is implied. `NO_CHANGE` is correct if the current design remains on the best-supported production Pareto frontier.

## 10. Operational storage/deployment state

DuckDB remains strong and implemented for sanitized analytical telemetry.

The action/HITL mutable-state role is not yet globally frozen for a broader production claim. Issue #131 must compare current single-process DuckDB custody/idempotency against a local PostgreSQL operational-state candidate if multi-process/restart/concurrency claims are desired.

The project must explicitly choose its final production claim:

```text
single-process/single-node production
or
multi-process durable production
```

and prove only the claim actually tested.

Still required under #131:

- one documented production startup path (`docker compose` or equivalent);
- deterministic environment/config validation;
- secret injection from environment only;
- graceful shutdown/restart;
- tested persistence/recovery semantics;
- schema lifecycle where applicable;
- clean checkout → running full product.

## 11. Browser/E2E reproduction gap

Current frontend CI proves:

- strict TypeScript typecheck;
- Vitest tests;
- Vite production build.

Before final freeze it must additionally prove browser behavior with Playwright against a real provider-free executing product path, including SSE reconnect, architecture/trace/lineage, dynamic drill-down and action confirmation/follow-run.

The final frontend dependency graph must be frozen with a committed lockfile and deterministic lockfile install (`npm ci` or equivalent) rather than resolving transitive dependencies afresh.

## 12. Current critical blockers / next gates

```text
1. merge PR #143                              immediate
2. D02 fresh post-reset execution             after 21:00 BRT + valid gate
3. integrate D02 result                       after execution
4. semantic response-quality calibration      #128
5. adaptive stopping/evidence experiment       #129, if evaluator baseline ready
6. runtime/HITL revalidation                  #92
7. operational storage/deployment hardening   #131
8. Playwright + lockfile + full E2E            #114/#131
9. baseline-derived production thresholds      after measured baseline freeze
10. clean reproduction + documentation freeze  before 2026-09-06 exit
```

External scientific blocker remains:

- missing exact C4 evaluator-side artifact; do not reconstruct or substitute it.

## 13. Current non-claims

Do not claim:

- a production provider is selected unless D02/frozen evidence supports it;
- adaptive policy improves the system before #129 passes the EDD gate;
- LangGraph is needed or better before #92 comparison;
- multi-process/horizontal production realtime before a shared durable adapter is tested;
- DuckDB is sufficient for multi-process operational mutation without evidence;
- PostgreSQL is required before comparison;
- semantic correctness beyond validated evaluator evidence;
- real-customer authorization beyond the controlled production-action policy implemented/tested;
- unconditional production readiness before clean start/restart/E2E acceptance.

## 14. State update rule

When evidence changes this state, update this document once. Do not duplicate mutable state across historical ADRs/audits. Frozen experiment evidence remains immutable and authoritative for its original scope.
