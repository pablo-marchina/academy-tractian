# Academy × TRACTIAN — Current Project Status

**Status:** ACTIVE / sole canonical human-readable state  
**Checkpoint:** 2026-09-02  
**Final delivery:** 2026-09-08  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)

## 1. Executive status

```text
TAPI scope                                  Track A + Track B combined
external API/hosted-service project cost    USD 0 hard constraint
production agent runtime                    IMPLEMENTED
production deterministic evaluator          IMPLEMENTED
TRACTIAN typed tool registry                 18 operations
provider-free integrated demo               IMPLEMENTED / REPRODUCIBLE
controlled supplied/test action path         IMPLEMENTED / bounded
standalone wheel reproduction                PROVED

D01 Cloudflare live comparison               COMPLETE
D01 attempts                                 32 / 32 completed
D01 actual cash cost                         USD 0.00
D01 observed Neurons                         2813.628464
D01 selection                                NO_SELECTION
D01 raw provider material persisted          NO
D01 CLIENT_FAILURE at 512-token ceiling      24 / 24

D02 completion cap                           1024
D02 worst-case packet                        9352.805376 Neurons
D02 provider-free implementation             MERGED / VALIDATED
D02 live result                              NOT YET EXECUTED

agent topology                               SINGLE AGENT / PRESERVE
LangGraph / multi-agent / RAG / memory       NOT AUTHORIZED BY EVIDENCE

realtime observability backend               P0 PLANNED
frontend control room                        P0 PLANNED
architecture/output lineage UI               P0 PLANNED
dynamic data explorer                        P0 PLANNED
```

## 2. D01 result and interpretation

D01 executed the frozen 8 public probes × 2 repeats × 2 candidates packet.

Candidates:

- `@cf/zai-org/glm-4.7-flash`
- `@cf/nvidia/nemotron-3-120b-a12b`

Both failed the frozen quality/stability hard gates, therefore the valid result is `NO_SELECTION`.

Post-run sanitized telemetry showed:

```text
GLM CLIENT_FAILURE              16 / 16 at 512 output tokens
Nemotron CLIENT_FAILURE          8 / 8 at 512 output tokens
all CLIENT_FAILURE              24 / 24 at exact 512 ceiling
Nemotron accepted outputs        7, 297..495 output tokens
Nemotron RESPONSE_PAYLOAD_INVALID 1, 476 output tokens
```

This is strong evidence that the D01 completion budget censored many outputs. It is not evidence that multi-agent/RAG/LangGraph would improve the system.

## 3. D02 boundary

D02 changes only the measured diagnostic variables:

```text
max_completion_tokens   512 -> 1024
failure diagnostics     generic code + sanitized subtype
```

Prompt, providers, units, repeats, schemas, evaluator, tool contract, zero retry/fallback policy and USD0 constraint remain fixed.

Full D02 worst case:

```text
GLM       1300.377600 Neurons
Nemotron  8052.427776 Neurons
total     9352.805376 Neurons
```

The D01 allocation already consumed 2813.628464 Neurons in the 2026-09-02 UTC day, so the full D02 packet requires a fresh eligible reset/zero-use window. Governed execution is tracked by issue #117. No live D02 call has been made by the provider-free implementation work.

## 4. Delivered agent/evaluation architecture

Implemented production path:

```text
request
→ ProductionRuntime
→ DecisionSource
→ AgentController
→ HarnessRunner
→ typed ToolSpec registry
→ B1 argument validation
→ B2 resource/action policy
→ B3 evidence/authorization when applicable
→ TRACTIAN transport
→ observations
→ FINAL / CLARIFY / ABSTAIN / ESCALATE
→ RunTrace
→ ProductionEvaluator
```

The evaluator does not supply gold/private truth to runtime. Identity and seed remain runtime-owned, not model-controlled.

## 5. Active product work: realtime observability control room

There was no existing frontend. The delivery frontend is now explicitly designed as a production-style **realtime agent observability control room**, not a static dashboard.

P0 workstreams:

- #121 — safe telemetry projection + local analytics/read API;
- #124 — genuine runtime event sink + SSE + reconnect/catch-up;
- #122 — React control room;
- #125 — architecture explorer + per-run output lineage;
- #123 — schema-driven dynamic data explorer;
- #119 — safe observability/realtime/frontend explanation acceptance matrix;
- #114 — integrated frontend/realtime/security/freeze acceptance.

Target path:

```text
RunTrace/event emission
→ safe projection
→ durable local telemetry
→ FastAPI REST + SSE
→ React control room
```

Raw `RunTrace` must never cross directly to the browser.

## 6. Frontend/observability target stack

Target delivery baseline, to be frozen in actual dependency files when scaffolded:

- FastAPI;
- DuckDB;
- Server-Sent Events;
- React + TypeScript + Vite;
- TanStack Query;
- Apache ECharts;
- React Flow;
- Vitest + Testing Library + Playwright.

Redis Streams is optional only if horizontal multi-instance realtime is actually configured/tested. Grafana/Phoenix/Langfuse/OpenTelemetry may be optional exports but are not primary delivery UI dependencies.

## 7. TAPI coverage status

The project explicitly combines:

- **Track A:** functional industrial agent/integration;
- **Track B:** evaluation framework/application.

The active TAPI technical/output crosswalk is [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md).

Required final outputs include:

1. functional industrial agent;
2. typed TRACTIAN integration;
3. agent evaluation framework;
4. governed experiment reports;
5. realtime observability control room;
6. architecture explorer;
7. per-run output lineage;
8. dynamic data explorer;
9. realtime telemetry/reconnect behavior;
10. technical documentation/reproduction package.

## 8. Current blockers and risks

```text
D02 live result                       waiting on eligible fresh authorization
realtime observability implementation P0 open
frontend implementation               P0 open
frontend integrated test/freeze        P0 open
C4 exact evaluator-side artifact       external exact-byte blocker
production provider                    may legitimately remain NO_SELECTION
```

The missing C4 artifact must not be reconstructed or substituted.

## 9. Current non-claims

Do not claim:

- a production provider is selected unless D02/frozen evidence supports it;
- horizontal multi-instance realtime before a shared durable stream adapter is tested;
- real-customer action authorization from the supplied/test controlled action demonstration;
- LangGraph/multi-agent/RAG/memory benefit without a measured material gap;
- evaluator semantic correctness beyond the evidence its contracts actually establish;
- unconditional production readiness.

## 10. State update rule

When evidence changes this state, update this document once. Do not copy a new status snapshot into README, project-plan compatibility files or historical audits. Machine/frozen evidence remains authoritative for its exact scope.