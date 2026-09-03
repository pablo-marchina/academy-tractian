# Academy × TRACTIAN — Current Project Status

**Status:** ACTIVE / sole canonical human-readable state  
**Checkpoint:** 2026-09-02 22:54 BRT / 2026-09-03 01:54 UTC  
**Final delivery:** 2026-09-08  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)

## 1. Executive status

```text
UPDATED TAPI scope                          Agent + Evaluation in one solution
external API/hosted-service project cost   USD 0 hard constraint
production agent runtime                   IMPLEMENTED
production deterministic evaluator         IMPLEMENTED
EDD baseline/candidate gate                IMPLEMENTED
TRACTIAN typed tool registry               18 operations
standalone wheel reproduction              PROVED

safe observability projection              IMPLEMENTED
DuckDB telemetry/read model                IMPLEMENTED
FastAPI product/read API                   IMPLEMENTED
POST /api/runs request→evaluation path     IMPLEMENTED
runtime-time SSE + reconnect/catch-up      IMPLEMENTED
Live Run Cockpit                           IMPLEMENTED
Run Explorer / Trace Graph                 IMPLEMENTED
Architecture Explorer                      IMPLEMENTED
Evidence Explorer / Output Lineage         IMPLEMENTED
Mission Control / Production Health        IMPLEMENTED
Tools & Policy / Eval Lab                  IMPLEMENTED
Provider D01/D02 Lab                       IMPLEMENTED
Dynamic Data Explorer + cross-filter       IMPLEMENTED
quant runtime/API/resource/SSE telemetry   IMPLEMENTED

production consequential actions          IMPLEMENTED / merged #143
action custody + explicit confirmation     IMPLEMENTED
action idempotency + no blind replay       IMPLEMENTED
action realtime trace/evaluator            IMPLEMENTED

D01 Cloudflare live comparison             COMPLETE
D01 attempts                               32 / 32
D01 cash cost                              USD 0.00
D01 observed Neurons                       2813.628464
D01 selection                              NO_SELECTION
D01 512-token censoring diagnostic         24 / 24 CLIENT_FAILURE at cap

D02 controlled 1024-token comparison       COMPLETE
D02 attempts                               32 / 32
D02 cash cost                              USD 0.00
D02 observed Neurons                       3344.130856
D02 packet Neuron delta vs D01             +18.85%
D02 selection                              NO_SELECTION
D02 production selection claim             FALSE
D02 raw provider material persisted        NO

semantic response-quality calibration      NEXT P0/P1 GATE / #128
adaptive evidence/stopping policy          P1 EXPERIMENT / #129
runtime/HITL final architecture            REVALIDATION REQUIRED / #92
operational storage topology               REVALIDATION REQUIRED / #131
Playwright full-product E2E                 NOT YET CLOSED / #114
frontend lockfile deterministic install    NOT YET CLOSED
production deployment/restart path         NOT YET CLOSED / #131
final integrated freeze                    NOT YET DONE / #114
```

## 2. Updated-TAPI interpretation

The latest TAPI is the formal source for scope. The project is one integrated solution containing:

- a functional industrial agent that interprets requests, obtains evidence from the provided TRACTIAN API and chooses safe operational outcomes/actions; and
- a framework/process/application for evaluating agent quality and reliability.

The delivery also includes API integration, technical experiments and documented results. Agent + Evaluation are therefore one P0 product, not independent optional tracks.

## 3. Delivered production path

```text
user request
→ POST /api/runs
→ trusted RuntimeContextProvider
→ RealtimeProductionRuntime.prepare()
→ genuine persisted run_started
→ provider-neutral DecisionSource
→ AgentController
→ HarnessRunner
→ typed 18-operation ToolSpec registry
→ deterministic B1/B2/B3
→ TRACTIAN transport
→ normalized observation/evidence
→ FINAL / CLARIFY / ABSTAIN / ESCALATE / action proposal
→ RunTrace
→ ProductionEvaluator
→ safe projection
→ DuckDB
→ FastAPI REST/SSE
→ React operator control room
```

Consequential actions use a separate two-phase production path:

```text
agent proposes exact action
→ deterministic permission/scope/schema/justification validation
→ private persistent action custody
→ PENDING_CONFIRMATION
→ authenticated operator confirms opaque action_id
→ current authorization + host kill switch revalidated
→ persistent atomic idempotency claim
→ exact custodied action executes through the existing safety/tool boundary
→ accepted=true semantics
→ separate realtime action RunTrace
→ ProductionActionEvaluator
→ same safe REST/SSE/frontend path
```

The browser cannot inject action arguments, identity, permissions, resource scope or idempotency material. Ambiguous post-claim failures become `UNCERTAIN` and are never automatically retried.

## 4. Safe realtime product surface

Delivered operator surfaces:

- Live Run Cockpit;
- historical Run Explorer;
- canonical-event Timeline;
- Trace Graph;
- versioned Architecture Explorer with active path;
- Evidence Explorer;
- Output Lineage;
- Action Control;
- Mission Control / Production Health;
- Tools analytics;
- Policy analytics;
- post-runtime Eval Lab;
- Provider D01/D02 Lab;
- Dynamic Data Explorer with allow-listed queries;
- global run cross-filter + drill-down.

Measured production telemetry includes runtime request/execution latency, API/query latency, CPU/load/RSS, executor pressure, runtime heartbeat, observability overhead, event→persistence latency, persistence→SSE latency, SSE reconnect/integrity signals, passive provider/TRACTIAN operability and host-owned kill switches.

All browser-facing state is projected through the safe observability boundary. Raw RunTrace, credentials, identity binding, evaluator seed/private truth, provider raw material and chain-of-thought are not browser-visible.

## 5. D01 → D02 controlled provider result

D01 established a strong completion-budget censoring signal at 512 completion tokens:

```text
all sanitized CLIENT_FAILURE at exact 512 cap  24 / 24
GLM success rate                              0.0000
Nemotron success rate                         0.4375
selection                                     NO_SELECTION
```

D02 changed the completion budget to 1024 under the frozen governed plan:

`e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958`

The one-shot D02 packet completed 32/32 attempts at USD 0.00 with complete resource accounting and no raw provider material recorded.

### GLM controlled delta

```text
M1 structured adherence     0.0000 → 0.4375   +43.75 pp
M4 public task quality      0.0000 → 0.3750   +37.50 pp
M7 success rate             0.0000 → 0.4375   +43.75 pp
M7 signature stability      0.0000 → 0.2500   +25.00 pp
median latency              8959.5 → 15329 ms +71.09%
observed Neurons            450.3848 → 642.9772 +42.76%
hard gates                  FAIL M1/M4/M7 → FAIL M1/M4/M7
```

### Nemotron controlled delta

```text
M1 structured adherence     0.4375 → 0.5625   +12.50 pp
M4 public task quality      0.3750 → 0.5625   +18.75 pp
M7 success rate             0.4375 → 0.5625   +12.50 pp
M7 signature stability      0.3750 → 0.5000   +12.50 pp
median latency              6214.0 → 4218.5 ms -32.11%
observed Neurons            2363.243664 → 2701.153656 +14.30%
hard gates                  FAIL M1/M4/M7 → FAIL M1/M4/M7
```

Packet observed Neurons increased from `2813.628464` to `3344.130856` (+18.85%). Safety/trace aggregates remained intact, but neither candidate crossed the frozen quality/stability gates. Therefore the evidence-backed decision is still:

**`NO_SELECTION` / no production provider claim.**

The accepted D02 aggregate does not expose the full 32-row failure-subtype matrix, so no precise residual censoring rate at 1024 is claimed or reconstructed.

Canonical D02 evidence:

- `research/cloudflare-d02-live-result-2026-09-03.json`
- `research/cloudflare-d01-d02-controlled-comparison-2026-09-03.md`

D02 is complete and must not be replayed.

## 6. Evaluation state and next gate

Strong delivered layers:

- deterministic structural/safety/trajectory evaluation;
- tool selection and argument validation;
- evidence/provenance checks;
- failure and repeated-run stability campaigns;
- provider public-rubric experiments;
- group-aware baseline/candidate EDD comparison;
- hard safety/integrity merge gates;
- separate read-only and consequential-action evaluators.

The next material TAPI gap is semantic response quality where deterministic traces alone cannot prove usefulness, groundedness or communication quality.

Issue #128 must close this with:

```text
Layer 1  deterministic checks first
Layer 2  semantic evaluator only where needed
Layer 3  human-labelled calibration / disagreement analysis
```

No LLM judge may become a promotion gate until its agreement/error profile against human labels is measured and accepted.

## 7. Adaptive policy gate

Issue #129 remains a prospective experiment, not a preselected architecture change.

Candidate adaptive behavior may cover:

- evidence sufficiency / marginal evidence gain;
- adaptive investigation budget;
- stopping;
- clarify / abstain / escalate thresholds.

The following remain deterministic regardless of experiment outcome:

- schema validation;
- identity;
- authorization/permissions;
- resource scope;
- explicit confirmation;
- idempotency;
- privacy projection;
- hard resource/safety caps.

Promote adaptivity only on measured Pareto improvement under the #128 evaluator without critical safety/integrity regression.

## 8. Runtime/HITL revalidation

ADR-004 remains authoritative for the original controller scope. The action-custody workflow creates a new materiality question for durable HITL/restart recovery.

Issue #92 must compare, with provider/tools/safety/scenarios/evaluator held constant:

```text
current custom controller + persistent action custody
vs
LangGraph-compatible persistent checkpoint/HITL candidate
```

No migration is implied. `NO_CHANGE` is the correct result if the current controller remains on the best measured production Pareto frontier.

## 9. Operational persistence and deployment

DuckDB remains the accepted analytical store for sanitized telemetry.

Issue #131 must explicitly freeze the final operational claim:

```text
single-process/single-node production
or
multi-process durable production
```

If stronger multi-process/restart guarantees are required, compare current operational DuckDB custody/idempotency against local PostgreSQL under controlled concurrency/recovery tests. Do not migrate based on convention alone.

Still required:

- one documented production startup path;
- deterministic environment/config validation;
- environment-only secret injection;
- graceful shutdown/restart;
- tested persistence/recovery semantics;
- schema lifecycle where applicable;
- clean checkout → running full product.

## 10. Browser/E2E and final reproduction

Current frontend CI proves strict TypeScript, Vitest and a production Vite build.

Before freeze, #114/#131 must additionally prove with Playwright against a real provider-free executing product path:

```text
request
→ run_started
→ live SSE growth
→ disconnect/reconnect/Last-Event-ID catch-up
→ terminal
→ evaluation
→ trace/architecture/evidence/lineage
→ dynamic drill-down
→ pending consequential action
→ explicit confirmation
→ action execution follow-run
→ action evaluation
```

Also required before final freeze:

- committed frontend lockfile;
- deterministic `npm ci` (or equivalent lockfile install);
- clean-clone reproduction;
- baseline-derived production thresholds defined prospectively, never post-hoc;
- documentation/rehearsal freeze.

## 11. Current critical path

```text
1. integrate D02 result + regression gate        CURRENT
2. close #117 after merged evidence              CURRENT
3. semantic response-quality calibration         #128
4. adaptive stopping/evidence experiment         #129, if evaluator ready
5. runtime/HITL revalidation                     #92
6. operational storage/deployment hardening      #131
7. Playwright + lockfile + full E2E              #114/#131
8. baseline-derived thresholds                   after baseline freeze
9. clean reproduction + final acceptance/freeze  #114
```

## 12. Current non-claims

Do not claim:

- a production provider has been selected; D02 explicitly ended `NO_SELECTION`;
- the exact residual D02 failure/censoring distribution without attempt-level sanitized evidence;
- adaptive policy improves the product before #129 passes EDD;
- LangGraph is needed or superior before #92;
- PostgreSQL is needed before #131 comparison;
- multi-process/horizontal production before shared durable state is tested;
- semantic correctness beyond validated evaluator evidence;
- unconditional production readiness before clean startup/restart/browser E2E acceptance.

## 13. State update rule

When accepted evidence changes current project state, update this document once. Historical ADRs and experiment evidence remain immutable and authoritative for their original scopes. Never rewrite frozen history merely to make the current architecture appear simpler.
