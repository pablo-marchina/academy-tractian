# Academy × TRACTIAN — Architecture Roadmap

**Status:** ACTIVE / canonical macro architecture roadmap  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate execution:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This document describes the **general project architecture and the path from controlled research to the integrated agent + evaluation production path requested by the project**. It is deliberately slower-changing than `NEXT-STEPS.md` and does not encode the current experiment gate.

A research implementation, provider, runtime or pattern is a candidate until the applicable comparison, robustness, production-fit and independent-evidence requirements justify a stronger state.

## 1. Architecture target — two coupled planes, one protected boundary

The final requested solution contains both:

1. **Agent Runtime Plane** — contextualize, investigate, clarify/abstain, execute and escalate against the supplied industrial API; and
2. **Evaluation & Reliability Plane** — capture and evaluate tool use, arguments, trajectory, evidence, decision/response, actions, escalation, safety, robustness and stability.

They must integrate through structured traces/artifacts while preserving the evaluation-only truth boundary.

```text
                         AGENT RUNTIME PLANE

User / case / request
        ↓
Request + identity/context boundary
        ↓
Agent decision/orchestration
        ↓
Evidence / tool-selection / stopping logic
        ↓
Typed industrial API tools
        ↓
┌──────────────────────────────────────────────────────┐
│ possible outcome                                     │
│ contextualize | investigate | clarify/abstain        │
│ execute authorized action | escalate with handoff    │
└──────────────────────────────────────────────────────┘
        ↓
Structured response + normalized execution trace
        │
        │ sanitized runtime evidence only
        ▼
                    EVALUATION & RELIABILITY PLANE

Scenario/requirement contract + evaluator-only references
        ↓
Deterministic evaluators where ground truth is deterministic
        ↓
Validated semantic evaluation only where necessary
        ↓
Tool / argument / evidence / decision / action / escalation /
safety / robustness / stability metrics
        ↓
Experiment/reliability report + trace inspection
```

Hard boundary:

```text
agent runtime ─X─> private oracle / evaluation-only gold / hidden outcomes
```

The evaluation framework may inspect frozen/captured runtime traces; it must not leak its supervision into the agent context.

## 2. Research/control architecture

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

### 2.1 Experiment definition layer

Owns problem/decision question, cases/evidence roles, candidate definitions, seeds/repetitions, metrics/thresholds, failure policy, access boundaries, preregistration and source pins.

Output: immutable experiment contracts/manifests.

### 2.2 Input / case layer

Owns allowed visible case material, exact selection, ticket/group/scenario binding, seed binding and request materialization. Private evaluator truth and independent hidden outcomes do not belong here.

### 2.3 Common-parent generation layer

Owns controlled model/provider generation when required by a frozen experiment: exact request/model/transport contract, pacing/retry semantics, response schema, provenance and operational failure classification.

Provider/model choice here is an experimental serving route unless a separate production decision freezes it.

### 2.4 Local candidate transformation layer

Owns provider-free interventions over frozen common parents, preserving preregistered candidate semantics and common-parent identity so intervention effects are not confounded by regeneration.

### 2.5 Immutable evidence-store layer

Carries artifact identity, hashes, commits/blobs, run/job/artifact provenance, cardinality/schema, access counters, failure state and explicit next-gate authorization. Historical failures and consumed attempts remain evidence.

### 2.6 Private deterministic evaluator layer

Consumes frozen outputs plus authorized evaluator-side private truth. It must not regenerate candidates, call a provider or serialize private expected-path content into sanitized evidence.

### 2.7 Statistical analysis layer

Consumes immutable deterministic scores and only runs analyses authorized by the preceding freeze: paired/factorial contrasts, uncertainty, bootstrap, LOGO, slices and missingness/denominator reporting when applicable.

### 2.8 Decision / gate layer

Combines quality, uncertainty, failures and production constraints to assign literal states such as `QUALIFIED`, `PREFERRED`, `FROZEN` or `SUPERSEDED`. Gate PASS is not automatic final selection.

### 2.9 Independent validation layer

Measures generalization only after candidate/evaluator generation is appropriately frozen. Independent outcomes cannot become a silent retuning loop for the same claimed blind candidate.

## 3. Required production behavior contracts

Regardless of framework choice, the final production path must preserve the capabilities mapped in `DELIVERY-ACCEPTANCE.md`.

### 3.1 Request/context contract

- requester identity/auth context outside model control;
- input/schema validation;
- explicit case/request context;
- clarification path when required information is missing;
- no evaluator/private/blind material in context.

### 3.2 Evidence/tool contract

- canonical typed tool/API schemas;
- correct function and argument selection;
- evidence provenance;
- bounded stopping/evidence sufficiency behavior;
- handling of complete, partial, inconclusive, conflicting and unavailable results.

### 3.3 Decision/outcome contract

The runtime must be able to produce a justified one of the required outcomes:

```text
contextualize
investigate further
request clarification / abstain safely
execute an authorized justified action
escalate to human analysis with useful handoff
```

No architecture is acceptable if it makes a required outcome materially harder to express, evaluate or audit.

### 3.4 Action/safety contract

- high-impact action parameters and justification validated;
- system authorization boundary separate from model choice;
- accepted action event interpreted according to supplied API semantics;
- duplicate/unnecessary action risk controlled;
- retry/idempotency policy explicit and production-tested;
- failure is safe and inspectable.

### 3.5 Trace/evaluation contract

Every meaningful run should be capturable in a normalized trace sufficient to inspect:

- input/context identifiers that are safe to expose;
- decisions/state transitions;
- tool choice and arguments;
- tool result classifications;
- evidence/provenance references;
- action/escalation/clarification outcome;
- final response;
- operational errors/timing metadata where appropriate.

The evaluation framework consumes this interface rather than coupling itself to hidden internal implementation details.

## 4. Production engineering cross-cutting concerns

The production implementation is a separate engineering surface derived from validated behavior and evidence-backed architecture decisions. It must explicitly address:

- typed API/tool contracts;
- authorization and auditability;
- bounded retry/idempotency behavior;
- state/context/persistence semantics;
- provider/tool failure handling;
- configuration/dependency pinning;
- secrets management;
- observability and trace inspection;
- latency/throughput/resource/cost budgets;
- security/privacy boundaries;
- reproducible build/deployment;
- rollback/reversal mechanisms.

Research one-shot constraints do not automatically become production policy.

## 5. Production architecture decision register

The following choices must be compared before final architecture freeze. Existing implementations are candidates/evidence, not automatic standards.

| Decision | Simple baseline / minimum comparison | Production evidence required |
|---|---|---|
| Provider/model strategy | simplest viable serving route vs credible alternatives | correctness, availability, latency, throughput, cost/quota, portability, recovery |
| Orchestration/runtime | explicit loop/state machine vs LangGraph/credible alternatives | correctness, determinism, observability, recovery, complexity, latency, maintainability |
| Agent topology | single-agent baseline vs justified decomposition | quality, coordination errors, latency, cost/token overhead, debuggability |
| Evidence/retrieval | direct API/evidence routing vs RAG/vector/reranking only if requirement/bottleneck exists | recall/precision, evidence correctness, latency, storage/ops cost, failure modes |
| Tool protocol/topology | native typed tool contract vs adapters/protocols such as MCP if portability benefit exists | schema fidelity, portability, isolation, maintainability |
| Memory/state | request-local/explicit conversation state vs persistence only if required | multi-turn/task benefit, contamination/privacy risk, storage cost, reproducibility |
| Adaptive policies | static baseline vs adaptive routing/stopping/retrieval/model choice | quality, calibration, resource use, stability, safety compliance |
| Safety/retry/idempotency | deterministic safe baseline vs bounded operational policies | unsafe action rate, duplicate-action risk, recovery, auditability |
| Evaluator/judge stack | deterministic evaluator wherever possible vs validated semantic judges | agreement/calibration, variance, cost, leakage, failure behavior |
| Observability | normalized trace + structured logs baseline vs richer backend | requirement coverage, debug time, overhead, privacy/retention, complexity |
| Deployment topology | simplest viable deployment vs credible scaling patterns | availability, latency, cost, secrets/security, rollback, scalability |
| UI/trace inspection | minimum usable production-path client/trace view vs richer interface | task completion, evaluator visibility, error transparency, authorization UX, maintainability |

For every material choice:

```text
acceptance requirement / material risk
→ decision question + hard constraints
→ primary-source research
→ credible alternatives + simple/null baseline
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

If a proposed component cannot identify the acceptance requirement/risk it improves, it should not be a final architecture component.

## 6. Complexity and delivery priority

Use the priority classes from `DELIVERY-ACCEPTANCE.md`:

- **P0:** required agent + evaluator capabilities and integrity boundaries;
- **P1:** production engineering required to safely/reliably operate P0;
- **P2:** optional architectural sophistication.

P2 candidates include RAG/vector DB/reranking, persistent memory, multi-agent decomposition, richer protocol adapters and adaptive routing/model selection unless a concrete P0/P1 requirement promotes them to a necessary decision.

A P2 component must beat its simpler baseline on relevant quality/production metrics after accounting for complexity, failure surface, cost and maintainability.

## 7. Productionization sequence

### Stage A — validated behavior extraction

Freeze the behavior the production implementation must preserve: decision classes, evidence policy, action/escalation/clarification semantics, tool contracts, safety boundaries and evaluator-visible trace semantics.

### Stage B — production contracts

Freeze public/internal interfaces, tool schemas, trace schema, state/context boundaries, authorization semantics, error classes and operational budgets.

### Stage C — production runtime + evaluator implementation

Create a distinct production code boundary rather than promoting `scripts/research/` into application code. The agent runtime and evaluation framework should share explicit contracts, not private evaluator truth.

A likely repository shape, only after architecture selection justifies it, is:

```text
src/                 production agent/runtime + shared public contracts
  ...
eval/ or equivalent production-compatible evaluation subsystem
  ...
tests/               unit/contract/integration/regression tests
config/              non-secret configuration contracts
docs/                architecture/runbooks/ADRs
research/            preserved scientific evidence
scripts/research/    historical/active research runners
```

Exact package/framework/deployment structure remains a decision output.

### Stage D — production verification

Verify all applicable P0/P1 acceptance rows through unit/regression, tool/API contracts, integration, end-to-end scenarios, failure/recovery, authorization/idempotency/security, latency/resource measurements, trace/observability validation, reproducible build and rollback.

### Stage E — controlled delivery

Deliver a versioned production path with frozen decisions, acceptance evidence, evaluation results, limitations, deployment/runbook instructions, monitoring and rollback behavior.

The demonstration must include real agent behavior plus per-run evaluation and reliability/robustness evidence.

## 8. Architecture freeze criteria

Final architecture may be frozen only when applicable material choices have:

1. a mapped P0/P1 acceptance requirement or material risk;
2. explicit requirements and hard constraints;
3. credible alternatives and a simple baseline;
4. quantitative controlled evidence;
5. uncertainty/repeated-run evidence where relevant;
6. robustness/failure-mode evidence;
7. production-fit evidence;
8. understood trade-offs/Pareto position;
9. ADR and reversal triggers;
10. regression obligations;
11. compatibility with the intended independent-evidence claim;
12. no unresolved P0 architecture gap hidden behind optional complexity.

Popularity, prior implementation effort or a benchmark-only win is insufficient.

## 9. Relationship to experimental cycles

P12-C1/C2/C3/C4 and similar cycles are **experimental instances inside this architecture**, not the architecture itself.

They provide evidence for candidate behavior and decision gates. The final product must additionally prove the requested integrated agent/evaluator capabilities and production fitness defined in `DELIVERY-ACCEPTANCE.md`.
