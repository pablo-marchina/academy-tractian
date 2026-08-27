# Academy × TRACTIAN — Architecture Roadmap

**Status:** ACTIVE / canonical macro architecture roadmap  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate execution:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)

This document describes the **general project architecture and the path from controlled research to the integrated industrial agent + evaluation framework requested by TRACTIAN/Inteli**. It is deliberately slower-changing than `NEXT-STEPS.md` and does not encode the current experiment gate.

A research implementation, provider, runtime or pattern is a candidate until the applicable comparison, robustness, production-fit and independent-evidence requirements justify a stronger state.

## 1. Architecture target — two coupled planes, one protected boundary

The final requested solution contains both:

1. **Agent Runtime Plane** — contextualize, investigate, clarify/abstain, execute and escalate against the supplied industrial API; and
2. **Evaluation & Reliability Plane** — capture and evaluate tool use, arguments, trajectory, evidence, decisions/conclusions, actions, escalation, safety, robustness and stability.

They integrate through structured traces/artifacts while preserving the evaluation-only truth boundary.

```text
                         AGENT RUNTIME PLANE

User / case / request
        ↓
Identity + authorization + request-context boundary
        ↓
Agent decision/orchestration
        ↓
Evidence / tool-selection / stopping logic
        ↓
Stable typed Tool Contract
        ↓
Adapter(s) to supplied TRACTIAN industrial API
        ↓
┌──────────────────────────────────────────────────────┐
│ possible outcome                                     │
│ contextualize | investigate | clarify/abstain        │
│ execute authorized action | escalate with handoff    │
└──────────────────────────────────────────────────────┘
        ↓
Customer-safe response + normalized execution trace
        │
        │ sanitized runtime evidence only
        ▼
                    EVALUATION & RELIABILITY PLANE

Scenario/requirement contract + evaluator-only references
        ↓
Deterministic evaluators where truth is deterministic
        ↓
Validated semantic/human evaluation only where necessary
        ↓
Tool / argument / evidence / decision / action / escalation /
communication / safety / robustness / stability metrics
        ↓
Experiment/reliability report + trace inspection
```

Hard boundary:

```text
agent runtime ─X─> private oracle / evaluation-only gold / hidden outcomes
```

The evaluation framework may inspect frozen/captured runtime traces; it must not leak supervision into the agent context.

## 2. Product-quality constraints from the actual TRACTIAN brief

The final architecture must preserve these requirements/guidance unless later evidence explicitly supersedes a project-choice layer:

### 2.1 Conclusion over wording

Operational correctness is primarily about the decision/conclusion and evidence, not matching the engineer's prose exactly. The runtime may vary communication style while the evaluator separates:

- conclusion/factual correctness;
- evidence support;
- action/escalation correctness;
- customer-safe communication.

Exact-string matching is not the primary quality signal.

### 2.2 Process must be diagnosable

The system must expose enough trace structure to answer:

- which tool was selected and why;
- which arguments were constructed;
- what evidence returned;
- how degraded/conflicting evidence changed behavior;
- why the system stopped, clarified, acted or escalated;
- where a failed run first diverged from an acceptable path.

Hidden chain-of-thought is not required; observable decision/tool/evidence state is.

### 2.3 Human fallback is a first-class outcome

When evidence is insufficient, materially ambiguous or the agent/provider/tool path fails, the system must be able to preserve the support workflow through clarification, abstention or human handoff rather than inventing certainty or blocking the workflow.

An escalation handoff should carry, where available:

- evidence already collected;
- relevant observations;
- unresolved contradiction/uncertainty;
- why the remote/automated path cannot safely conclude;
- the next question a human needs to resolve.

### 2.4 Customer-safe response boundary

The system should give the customer the useful operational conclusion without unnecessarily exposing internal implementation details, backend failures or internal service structure unless that information is genuinely necessary for the requested resolution.

### 2.5 Stable integration surface

The agent should reason against a stable typed tool contract. HTTP/MCP/RPC/file/backend heterogeneity, if ever introduced, belongs behind adapters rather than becoming arbitrary protocol complexity in the model context.

This does **not** require implementing multiple backend protocols for the assignment. Generalization beyond the supplied API is optional unless it earns its place quantitatively.

### 2.6 Consequential actions

The delivered benchmark treats an accepted action call as execution. Real interactive product policy may additionally require requester confirmation for consequential mutations. Keep those concepts separate:

```text
benchmark action semantics
        !=
future interactive confirmation UX policy
```

If confirmation is adopted for the final production-path interface, freeze/test the policy without corrupting official benchmark semantics.

### 2.7 Quality-first model validation, then optimization

Model/provider research must not prematurely optimize cost by excluding a materially stronger quality frontier. Compare:

- a strong quality-frontier candidate/configuration;
- a feasible lower-cost/local/open baseline where relevant;
- any additional credible Pareto candidate.

Then select based on measured correctness, robustness, latency, reliability, cost/resource use, portability and operational constraints.

Experimental no-card/free provider history remains evidence about a specific research path; it is not automatically the final product-provider requirement.

## 3. Research/control architecture

The scientific path that selects and validates behavior remains:

```text
1. Experiment Definition
        ↓
2. Generation & Transformation
        ↓
3. Immutable Evidence Store
        ↓
4. Private Evaluation & Statistics
        ↓
5. Decision + Independent Validation
        ↓
6. Evidence-backed production specification
```

The fundamental transition is always:

```text
frozen input
→ authorized execution
→ validation
→ artifact
→ hash/provenance
→ freeze
→ next gate
```

Generation must not know private evaluator truth. Evaluation must not alter generated outputs. Statistical analysis must not alter deterministic scores. Independent validation must not become a tuning loop for the same candidate.

### 3.1 Experiment definition layer

Owns problem/decision question, cases/evidence roles, candidate definitions, seeds/repetitions, metrics/thresholds, failure policy, access boundaries, preregistration and source pins.

### 3.2 Input / case layer

Owns allowed visible case material, exact selection, ticket/scenario grouping, identity binding, seed binding and request materialization. Private evaluator truth and independent hidden outcomes do not belong here.

The delivered package has 17 case/gold rows but 16 narrative scenarios; grouped evidence must remain grouped where needed to prevent leakage.

### 3.3 Common-parent generation layer

Owns controlled model/provider generation when required by a frozen experiment: exact request/model/transport contract, pacing/retry semantics, response schema, provenance and operational failure classification.

Provider/model choice here is an experimental serving route unless a separate production decision freezes it.

### 3.4 Local candidate transformation layer

Owns provider-free interventions over frozen common parents, preserving preregistered candidate semantics and common-parent identity so intervention effects are not confounded by regeneration.

### 3.5 Immutable evidence-store layer

Carries artifact identity, hashes, commits/blobs, run/job/artifact provenance, cardinality/schema, access counters, failure state and explicit next-gate authorization. Historical failures and consumed attempts remain evidence.

### 3.6 Private deterministic evaluator layer

Consumes frozen outputs plus authorized evaluator-side private truth. It must not regenerate candidates, call a provider or serialize private expected-path content into sanitized evidence.

### 3.7 Statistical analysis layer

Consumes immutable deterministic scores and only runs analyses authorized by the preceding freeze: paired/factorial contrasts, uncertainty, bootstrap, LOGO, slices and missingness/denominator reporting when applicable.

### 3.8 Decision / gate layer

Combines evidence, failure policy, uncertainty, delivery requirements and production constraints to assign literal states: `QUALIFIED`, `PREFERRED`, `FROZEN`, `SUPERSEDED`.

Gate PASS is evidence, not automatic final selection.

### 3.9 Independent validation layer

Measures generalization after candidate/evaluator generation is frozen and custody/access rules are satisfied. Independent outcomes cannot become a silent tuning loop for the same blind claim.

## 4. Final production-path logical architecture

The architecture that reaches final delivery should be decomposed by responsibility rather than by framework brand:

```text
Client / demo / integration
        ↓
Request Context Boundary
  - user/case identity
  - authorization
  - conversation/request state
        ↓
Agent Controller
  - decision state
  - evidence sufficiency
  - stopping / clarification / escalation
        ↓
Stable Tool Contract
        ↓
TRACTIAN API Adapter
        ↓
Supplied Industrial API
        ↓
Normalized Tool Observations
        ↘
          Trace / Observability Stream
        ↙
Agent Controller
        ↓
Outcome
  - answer/orient
  - clarify/abstain
  - action
  - escalation handoff
        ↓
Customer-safe response

Captured Trace ───────────────► Evaluation Runner
                               ├─ deterministic evaluators
Evaluation-only references ───►├─ validated semantic evaluator if needed
                               ├─ robustness/reliability analysis
                               └─ report / trace inspection
```

A single-agent explicit controller is the default simple baseline. Multi-agent decomposition is only eligible if controlled evidence shows material benefit after coordination/latency/cost/debugging overhead.

## 5. Production architecture decision register

Existing code is candidate evidence, not an automatic standard.

| Decision | Minimum comparison | Required evidence before freeze |
|---|---|---|
| Provider/model strategy | strong quality frontier vs feasible lower-cost/local baseline + credible alternatives | task quality, robustness, stability, availability, latency, cost/resource, portability, failure behavior |
| Orchestration/runtime | explicit loop/state-machine baseline vs LangGraph/other credible runtime | correctness, determinism, observability, recovery, complexity, latency, maintainability |
| Agent topology | single-agent baseline vs justified specialized/multi-agent decomposition | quality, coordination errors, latency, token/cost overhead, debugability, failure isolation |
| Evidence/retrieval | direct API/tool/evidence routing baseline vs RAG/vector/reranking only if needed | evidence correctness/recall, latency, complexity, storage/ops burden, failure modes |
| Tool protocol/topology | canonical native typed Tool Contract vs MCP/adapter options where useful | schema fidelity, portability, isolation, maintainability, model simplicity |
| Memory/state | request-local/explicit state baseline vs persistent memory if actual scenarios need it | measurable task benefit, contamination/privacy risk, reproducibility, storage/ops cost |
| Adaptive policies | static explicit baseline vs adaptive stopping/routing/model/retrieval | quality/calibration, resource use, stability, safety compliance, observability |
| Safety/authorization | deterministic policy baseline vs additional guards/confirmation layers | unsafe-action rate, permission correctness, duplicate-action risk, auditability |
| Failure continuity | simple human fallback baseline vs richer retry/fallback policies | workflow continuity, recovery time, duplicate/unsafe risk, operator clarity |
| Evaluator/judge stack | deterministic evaluator wherever possible vs validated semantic/human judgment where needed | agreement/calibration, variance, leakage risk, cost, failure behavior |
| Observability | normalized structured trace baseline vs richer OTel/inspection backend | coverage, diagnostic value, overhead, privacy/retention, demo value |
| Deployment topology | simplest viable reproducible deployment vs scaling alternatives | availability, latency, cost/resource, secrets/security, rollback, setup reliability |
| UI/integration | minimal real production-path interface vs richer interface | task completion, authorization/confirmation UX, trace/eval inspection, maintainability |

For every material choice:

```text
decision question
→ official requirement / material risk
→ hard constraints
→ primary-source research
→ credible alternatives + simple baseline
→ preregistered comparison
→ quantitative evaluation
→ uncertainty/repeated behavior
→ robustness/failure analysis
→ production-fit evidence
→ Pareto/trade-off analysis
→ ADR + reversal triggers
→ PREFERRED
→ confirmation/regression
→ FROZEN
```

## 6. Productionization sequence

### Stage A — validated behavior extraction

Define exactly what behavior production must preserve from the accepted candidate without copying experiment-only plumbing blindly.

### Stage B — production contracts

Freeze, as applicable:

- input/request schema;
- user/authorization binding;
- stable Tool Contract;
- API adapter contract;
- trace schema;
- outcome schema;
- action/escalation semantics;
- failure classes;
- latency/reliability/resource budgets;
- evaluator interface.

### Stage C — production runtime implementation

Create a distinct production code boundary rather than promoting `scripts/research/` into application code.

A likely repository shape, only after architecture selection justifies it:

```text
src/                 production implementation
tests/               unit/contract/integration/regression tests
config/              non-secret configuration contracts
docs/                architecture/runbooks/ADRs
research/            preserved scientific evidence
scripts/research/    historical/active research runners
```

The exact package/framework/deployment structure remains a decision output.

### Stage D — integrated evaluation implementation

The final evaluator must be able to consume the same normalized production trace while keeping evaluator-only truth isolated.

Preserve or implement:

- deterministic tool/argument/action/decision checks;
- evidence and conclusion evaluation;
- robustness/failure variants;
- repeated-run reliability;
- trace inspection/capture-replay;
- evaluator/judge calibration evidence;
- requirement/rubric coverage reporting.

### Stage E — production verification

Required evidence includes, as applicable:

- unit tests;
- deterministic behavior regression;
- evaluator regression;
- tool/API contract tests;
- integration tests;
- end-to-end production-path tests;
- data/tool/provider failure and fallback tests;
- authorization/idempotency/security tests;
- escalation-handoff tests;
- customer-safe communication checks;
- latency/load/resource measurements;
- observability validation;
- reproducible environment/build;
- rollback/fallback validation.

### Stage F — controlled final delivery

Deliver the versioned production path with frozen decisions, evidence, limitations, setup/runbook instructions, fallback/monitoring/rollback behavior and a demonstration that exercises the real integrated agent/evaluator path.

## 7. Architecture freeze criteria

Final architecture may be frozen only when applicable material choices have:

1. an explicit TAPI/package requirement or material risk rationale;
2. explicit hard constraints;
3. credible alternatives and a simple baseline;
4. quantitative controlled evidence;
5. uncertainty/repeated-run evidence where relevant;
6. robustness/failure-mode evidence;
7. production-fit evidence;
8. understood trade-offs/Pareto position;
9. ADR and reversal triggers;
10. regression obligations;
11. compatibility with independent-evidence claims;
12. no uncovered P0 acceptance row caused by the choice.

Popularity, prior implementation effort, framework novelty or a benchmark-only win is insufficient.

## 8. Relationship to experimental cycles

P12-C1/C2/C3/C4 and similar cycles are **experimental instances inside this architecture**, not the architecture itself.

They provide evidence for candidate behavior and decision gates. The final production architecture is selected from accumulated scientific, partner-quality and production-fit evidence.

## 9. Architecture quality rule

The best final architecture is the **simplest architecture on the best-supported quality/production Pareto frontier that fully covers the requested delivery**.

More components are not inherently better. Fewer components are not inherently better. Evidence decides.