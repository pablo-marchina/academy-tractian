# Academy × TRACTIAN — Architecture Roadmap

**Status:** ACTIVE / canonical macro architecture roadmap  
**Architecture checkpoint:** 2026-09-01  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate execution:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This document describes the production-path architecture and which architecture decisions are already supported, still conditional or explicitly blocked. It does not authorize live execution; `CURRENT-PROJECT-STATUS.md` remains authoritative for authorization.

## 1. Architecture objective

The final solution has two coupled planes separated by an evaluator-private boundary:

```text
                    AGENT RUNTIME PLANE

User / request
      ↓
Request Context Boundary
  - identity
  - authorization
  - request state
      ↓
Agent Controller / selected topology
  - evidence sufficiency
  - stopping
  - clarification / abstention
  - action / escalation decision
      ↓
Stable typed Tool Contract
      ↓
TRACTIAN API Adapter
      ↓
Supplied industrial API
      ↓
Normalized observations
      ↓
Agent Controller
      ↓
Customer-safe outcome
      ↓
Normalized RunTrace
      │
      │ sanitized runtime evidence only
      ▼
              EVALUATION & RELIABILITY PLANE

Scenario/requirement contract
+ evaluator-only references
      ↓
Deterministic evaluators where possible
      ↓
Validated semantic/human judgment only where necessary
      ↓
quality / tool / argument / evidence / action /
escalation / safety / robustness / stability metrics
      ↓
reports + trace inspection + architecture evidence
```

Hard boundary:

```text
runtime ─X─> private oracle / evaluator-only gold / hidden outcomes
```

Observable structured state is required; hidden chain-of-thought is not.

## 2. Architectural invariants already strongly supported

These are not waiting for broad reimplementation.

### 2.1 HarnessRunner remains the execution boundary

`HarnessRunner.execute_tool()` remains the sole real tool-execution boundary for the current production path. Provider/model output proposes decisions; it does not execute provider-native tools.

### 2.2 Stable typed native tool contract

Historical Native Tools × MCP evidence is sufficient for the current scope:

```text
native typed ToolSpec       preferred current integration surface
MCP adapter                 conditional portability option
new Native-vs-MCP experiment not justified now
```

Backend/protocol heterogeneity belongs behind adapters rather than in the model context.

### 2.3 Deterministic safety and action semantics

Authorization, action validation, idempotency and no-replay behavior are hard boundaries. New architecture may preserve or strengthen them but may not weaken them for convenience.

### 2.4 Structured trace / evaluator separation

Normalized `RunTrace` and deterministic operational evaluation are sufficient architecture foundations for the current scope. Richer observability backends are optional unless a measured diagnostic/delivery gap appears.

### 2.5 Human fallback is first-class

When evidence/provider/tool availability is insufficient, valid outcomes include:

```text
clarify
abstain
escalate with evidence handoff
```

rather than invented certainty or unsafe action.

## 3. Current provider serving architecture

The old OpenAI/Gemini path is historical evidence only and must not be executed as the current production provider packet.

The currently frozen experimental serving path is:

```text
ProviderDecisionSource
      ↓
CloudflareWorkersAIChatCompletionsDecisionClient
      ↓
direct Workers AI OpenAI-compatible endpoint
      ↓
ONE OF
  @cf/zai-org/glm-4.7-flash
  @cf/nvidia/nemotron-3-120b-a12b
      ↓
strict ProviderDecisionPayload
      ↓
Cloudflare-specific exact provenance adapter
      ↓
AgentController / HarnessRunner
```

Frozen layers:

```text
ADR-018  provider comparison preregistration
ADR-019  direct provider client
ADR-020  comparison executor/custody/resource accounting
ADR-021  live authorization protocol
```

Scientific packet:

```text
8 public probes × 2 repeats × 2 models
max attempts       32
input ceiling      8000 accounted tokens/attempt
output ceiling     512 tokens/attempt
packet maximum     7937.522688 neurons
selection          Pareto / NO_SELECTION allowed
```

Current state:

```text
live attempts consumed        0 / 32
production provider selected  NO
```

## 4. Current provider blocker is authorization evidence, not architecture code

The target account proves `Workers Free / Active`, but its current Workers AI dashboard does not expose the explicit Neuron balance assumed by ADR-021.

Therefore:

```text
Cloudflare client architecture         READY / FROZEN PROVIDER-FREE
Cloudflare executor/custody            READY / FROZEN PROVIDER-FREE
live authorization protocol            FROZEN
original Neuron evidence source        NOT OPERABLE ON TARGET UI
issue #80                              CURRENT REVALIDATION
```

Do not solve this by:

- fabricating `used=0`;
- scraping undocumented private dashboard APIs as canonical evidence;
- sacrificial inference;
- arbitrary credential probes;
- silently weakening the 9000-Neuron gate.

If a defensible prospective amendment is frozen, live comparison may proceed. Otherwise the architecture must carry an explicit externally-blocked provider-selection non-claim into final delivery.

## 5. Production architecture decision register — reconciled

| Decision | Current state | Architecture consequence |
|---|---|---|
| Provider/model | `PARTIALLY_ASSESSED`; Cloudflare packet frozen, live comparative evidence pending/blockable | current critical decision |
| Tool topology | `EVIDENCE_SUFFICIENT` | native typed ToolSpec remains standard; MCP conditional |
| Evidence-sufficiency stopping | `EVIDENCE_SUFFICIENT` | preserve current policy |
| Safety/authorization/idempotency | strong hard boundary | preserve/strengthen only |
| RunTrace/operational evaluator | `EVIDENCE_SUFFICIENT` current scope | preserve |
| Retrieval/RAG/vector/reranking | no material gap demonstrated | do not add |
| Persistent memory | no material task need demonstrated | do not add |
| Agent topology | strong single-agent qualified baseline; comparative optimality unresolved | conditional post-provider audit |
| Runtime/orchestration | historical evidence strong but asymmetric | conditional after topology/materiality audit |
| Adaptive model routing | unassessed, not currently material | defer |
| Rich observability backend | optional | defer unless diagnostic requirement appears |
| Hosted deployment | final delivery need not assume paid hosted deployment | choose simplest reproducible zero-cost path |
| Rich UI | optional | only add if it improves acceptance/demo materially |

## 6. Agent topology — conditional decision, not automatic next experiment

Current architecture:

```text
single AgentController
+ explicit decision state
+ evidence-sufficiency stopping
+ stable typed tools
+ HarnessRunner execution boundary
```

This remains the **strong qualified baseline**.

The previous roadmap required single-agent vs planner→executor vs critic/reviewer before final freeze by default. That rule is now refined by evidence-first governance:

```text
provider D01 resolved/bounded
→ audit whether topology can still materially change P0/P1/final architecture
→ if NO: preserve simple baseline and document bounded comparative non-claim
→ if YES: preregister minimum controlled topology experiment
```

If a topology experiment is justified, hold constant where feasible:

- provider/model basis;
- public task population;
- ToolSpecs/HarnessRunner;
- safety/authorization boundaries;
- evaluator definitions;
- repetition geometry.

Adopt multi-agent only if measured benefit survives coordination failure, latency/quota overhead, trace complexity and debugging burden.

## 7. Runtime/orchestration — one gate later

Explicit controller/state-machine behavior and historical LangGraph/runtime evidence already exist. Do not launch generic framework research.

After topology is closed/bounded, ask:

```text
Would changing runtime/orchestrator still materially improve correctness,
recovery, observability or maintainability for the final architecture?
```

Only if YES, compare the minimum credible runtime alternatives with topology/provider held fixed.

Framework novelty alone is not evidence.

## 8. Retrieval, memory and routing

### Retrieval/RAG

Current direct tool/evidence routing has no demonstrated retrieval-recall bottleneck requiring RAG/vector DB/reranking. Architecture therefore remains:

```text
structured request
→ explicit tools/API evidence
→ normalized observations
```

RAG remains a reversal-triggered option only.

### Persistent memory

Request-local/explicit state remains preferred because persistent memory has no demonstrated task benefit and introduces contamination/privacy/reproducibility risk.

### Adaptive model routing

Do not add routing until multiple qualified provider/model options exist and routing can solve a measured problem. A routing experiment before provider qualification is premature.

## 9. Evaluation architecture

The final evaluator should consume the same normalized production trace while preserving evaluator-only truth.

Required layers:

```text
deterministic contract/safety/tool/action evaluation
+
evidence/conclusion evaluation where authorized
+
robustness/failure variants
+
repeated-run reliability when applicable
+
trace inspection
+
requirement/rubric coverage reporting
```

Semantic/human judgment is used only where deterministic truth is insufficient and the judge itself is validated.

C4 remains a separate scientific gate, not a reason to rewrite the runtime architecture.

## 10. C4 parallel track

Required exact evaluator-side artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

Only exact-byte recovery is currently authorized. Reconstruction/rescoring/substitution remains forbidden absent a prospective scientific amendment.

Final architecture claims must distinguish operational evaluator evidence from the externally blocked C4 claim scope.

## 11. Productionization sequence — current

### Stage A — material decision closure

Current focus:

1. close/bound provider D01;
2. audit whether topology remains material;
3. audit whether runtime remains material;
4. preserve evidence-sufficient decisions.

### Stage B — architecture freeze

Freeze only components that are necessary for the strongest supported final path:

- request/context boundary;
- selected/bounded provider strategy;
- controller/topology;
- stable Tool Contract;
- API adapter;
- action/authorization semantics;
- RunTrace;
- evaluator interface;
- fallback/escalation behavior;
- resource/latency/reliability boundaries;
- zero-cost run path.

### Stage C — integrated verification

Required evidence, as applicable:

- unit/contract/integration tests;
- production-path regression;
- evaluator regression;
- degraded/conflicting/unavailable evidence behavior;
- provider/tool failure continuity;
- authorization/idempotency/security;
- escalation handoff;
- customer-safe response boundary;
- latency/resource/quota evidence;
- trace/observability validation;
- clean reproducibility;
- fallback/rollback path.

### Stage D — final delivery

Deliver versioned architecture + evidence + limitations + runbook/demo. A live Cloudflare comparison is valuable if defensibly authorized, but final delivery must remain truthful and viable even if the external account-evidence gate remains blocked.

## 12. Architecture freeze criteria — deadline-aware

A material architecture choice can freeze when it has:

1. requirement/material-risk rationale;
2. applicable hard constraints;
3. repository evidence audit;
4. credible alternatives or documented non-materiality;
5. quantitative evidence where comparison remains necessary;
6. robustness/failure analysis;
7. production-fit trade-offs;
8. ADR/reversal triggers;
9. regression obligations;
10. compatibility with independent/private-evidence boundaries;
11. no unresolved P0 blocker caused by that choice.

By 2026-09-05, unresolved optional comparative breadth should default to a bounded non-claim rather than launching speculative P2 experiments.

## 13. Deadline architecture strategy

```text
09-01 → 09-02
  resolve/bound Cloudflare authorization evidence (#80)

09-02 → 09-03
  execute frozen provider packet if admissible
  OR freeze external blocker/non-claim

09-03 → 09-05
  close only still-material topology/runtime decisions
  integrated reliability/regression
  architecture freeze

09-05 → 09-07
  evidence package, runbook, demo, acceptance reconciliation

09-08
  delivery
```

## 14. Architecture quality rule

The best final architecture is:

> **the simplest architecture on the best-supported zero-cost quality/production Pareto frontier that fully covers the requested delivery.**

More components are not inherently better. An experiment is not inherently better than a bounded evidence-backed decision. Existing code is not automatically final. Evidence decides.
