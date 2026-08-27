# Academy × TRACTIAN — Architecture Roadmap

**Status:** ACTIVE / canonical macro architecture roadmap  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate execution:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This document describes the **general project architecture and the path from controlled research to a production-path system**. It is deliberately slower-changing than `NEXT-STEPS.md` and does not encode the current experiment gate.

A research implementation, provider, runtime or pattern is a candidate until the applicable comparison, robustness, production-fit and independent-evidence requirements justify a stronger state.

## 1. Architectural model

The project is organized as five externally understandable blocks:

```text
1. Experiment Definition
        ↓
2. Generation & Transformation
        ↓
3. Immutable Evidence Store
        ↓
4. Private Evaluation & Statistics
        ↓
5. Decision, Independent Validation & Production Delivery
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

## 2. Detailed layers

### 2.1 Experiment definition layer

Owns:

- problem/decision question;
- benchmark/evidence roles;
- cases and partition policy;
- candidate/intervention definitions;
- seeds and repetition policy;
- metrics, thresholds and failure policy;
- access/authorization boundaries;
- preregistration and source pins.

Output: immutable experiment contracts/manifests.

### 2.2 Input / case layer

Owns:

- allowed visible/public case material;
- exact case selection;
- ticket/group/scenario bindings;
- seed binding;
- request materialization inputs.

Private evaluator truth and independent hidden outcomes do not belong in this layer.

### 2.3 Common-parent generation layer

Owns controlled external model/provider generation when the frozen experiment requires it.

Responsibilities include:

- exact model/provider/request contract;
- one-shot/retry/pacing rules;
- response-schema enforcement;
- request/result provenance;
- operational failure classification;
- fail-closed packet completeness rules.

Provider/model choice here is an experimental serving route unless a separate production decision freezes it.

### 2.4 Local factorial / candidate transformation layer

Owns provider-free candidate interventions over the same frozen common parent.

The layer exists to isolate intervention effects from provider regeneration. Candidate transforms must preserve their preregistered semantics, source pins and parent identity.

### 2.5 Immutable evidence-store layer

Owns the handoff between scientific stages.

Evidence should carry, where applicable:

- artifact identity;
- content hashes;
- Git source blobs/commits;
- workflow run/job/artifact provenance;
- exact cardinality and schema;
- access counters;
- execution/failure state;
- explicit next-gate authorization.

Historical failures and consumed attempts remain evidence.

### 2.6 Private deterministic evaluator layer

Consumes already frozen candidate outputs plus authorized evaluator-side private truth.

Hard boundary:

```text
candidate/generation side  ─X─> private oracle
private evaluator          ──> frozen candidate outputs only
```

The deterministic evaluator must not regenerate candidates, call the provider or leak private expected-path content into sanitized results.

### 2.7 Statistical analysis layer

Consumes immutable deterministic scores and only runs analyses explicitly authorized by the preceding freeze.

Potential frozen analyses include:

- paired/factorial contrasts;
- uncertainty intervals;
- group/cluster bootstrap;
- LOGO sensitivity;
- modality/failure slices;
- denominator/missingness reporting.

Statistics cannot change candidate outputs or deterministic labels.

### 2.8 Decision / gate layer

Combines evidence, failure policy, uncertainty and production constraints to assign literal repository states such as:

- `QUALIFIED`;
- `PREFERRED`;
- `FROZEN`;
- `SUPERSEDED`.

A gate PASS is evidence for that gate, not automatic production selection.

### 2.9 Independent validation layer

Measures generalization only after the relevant candidate/evaluator generation is frozen and custody/access rules are satisfied.

Independent outcomes must not be used to silently retune the same candidate while preserving the original blind claim.

### 2.10 Production-system layer

The production implementation is a separate engineering surface derived from validated behavior and evidence-backed architecture decisions.

It must add production concerns explicitly, including:

- typed API/tool contracts;
- authorization and auditability;
- bounded retry/idempotency behavior;
- state/persistence semantics;
- provider/tool failure handling;
- configuration/dependency pinning;
- secrets management;
- observability;
- latency/throughput/resource budgets;
- security/privacy boundaries;
- reproducible build/deployment;
- rollback/reversal mechanisms.

Research-only one-shot constraints do not automatically become production policy.

## 3. Cross-cutting architecture

Three concerns span every layer.

### 3.1 Gates

- authorization boundaries;
- fail-closed behavior;
- no leakage between candidate/evaluator/blind roles;
- literal state transitions;
- no crossing into later stages without a new freeze.

### 3.2 Artifacts

- JSON/JSONL and other immutable evidence;
- generated outputs;
- scoring/statistical results;
- manifests and authorizations;
- freeze records;
- release artifacts.

### 3.3 Provenance

- Git commits/blobs;
- source/runtime pins;
- workflow runs/jobs;
- artifact IDs/digests;
- deterministic content hashes.

## 4. Production architecture decision register

The following choices must be compared before final architecture freeze. Existing implementations are candidates/evidence, not automatic standards.

| Decision | Minimum comparison | Production evidence required |
|---|---|---|
| Provider/model strategy | current viable route vs credible alternatives/simple serving baseline | correctness, availability, latency, throughput, cost/quota, portability, recovery |
| Orchestration/runtime | explicit loop/state machine baseline vs LangGraph/credible alternatives | correctness, determinism, observability, recovery, complexity, latency, maintainability |
| Agent topology | single-agent baseline vs justified decomposition | quality, coordination errors, latency, cost/token overhead, debuggability |
| Evidence/retrieval | direct evidence/tool routing baseline vs RAG/vector/reranking when justified | recall/precision, evidence correctness, latency, storage/ops cost, failure modes |
| Tool protocol/topology | native tool contract baseline vs adapters/protocols such as MCP when useful | schema fidelity, portability, isolation, maintainability |
| Memory/state | request-local baseline vs persistent memory when required | task benefit, contamination/privacy risk, storage cost, reproducibility |
| Adaptive policies | static baseline vs adaptive routing/stopping/retrieval/model choice | quality, calibration, resource use, stability, safety compliance |
| Safety/retry/idempotency | deterministic safe baseline vs bounded operational policies | unsafe action rate, duplicate-action risk, recovery, auditability |
| Evaluator/judge stack | deterministic evaluator where possible vs validated semantic judges | agreement/calibration, variance, cost, leakage, failure behavior |
| Observability | minimum structured tracing vs richer backends | coverage, debug time, overhead, privacy/retention, complexity |
| Deployment topology | simplest viable deployment vs credible scaling patterns | availability, latency, cost, secrets/security, rollback, scalability |
| UI/integration | direct production-path client baseline vs richer interface patterns | completion, error transparency, authorization UX, maintainability |

For every material choice:

```text
decision question
→ requirements/hard constraints
→ primary-source research
→ alternatives + simple/null baseline
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

## 5. Productionization sequence

The intended transition after candidate/architecture evidence is sufficient is:

### Stage A — validated behavior extraction

Define the behavior that production must preserve without copying experiment-only plumbing blindly.

### Stage B — production contracts

Freeze public/internal interfaces, tool schemas, state boundaries, authorization semantics, error classes and operational budgets.

### Stage C — production runtime implementation

Create a distinct production code boundary rather than promoting `scripts/research/` into application code.

A likely repository shape, only after architecture selection justifies it, is:

```text
src/                 production implementation
  ...
tests/               unit/contract/integration/regression tests
config/              non-secret configuration contracts
docs/                architecture/runbooks/ADRs
research/            preserved scientific evidence
scripts/research/    historical/active research runners
```

The exact package/framework/deployment structure remains a decision output, not a preregistered conclusion.

### Stage D — production verification

Required evidence includes, as applicable:

- unit tests;
- deterministic behavior regression;
- evaluator regression;
- tool/API contract tests;
- integration tests;
- end-to-end production-path tests;
- failure/recovery tests;
- authorization/idempotency/security tests;
- latency/load/resource measurements;
- observability validation;
- reproducible environment/build;
- rollback/reversal validation.

### Stage E — controlled delivery

Deliver the versioned production path with frozen decisions, evidence, limitations, deployment/runbook instructions, monitoring and rollback behavior.

## 6. Architecture freeze criteria

Final architecture may be frozen only when applicable material choices have:

1. explicit requirements and hard constraints;
2. credible alternatives and a simple baseline;
3. quantitative controlled evidence;
4. uncertainty/repeated-run evidence where relevant;
5. robustness/failure-mode evidence;
6. production-fit evidence;
7. understood trade-offs/Pareto position;
8. ADR and reversal triggers;
9. regression obligations;
10. compatibility with the intended independent-evidence claim.

Popularity, prior implementation effort or a benchmark-only win is insufficient.

## 7. Relationship to experimental cycles

P12-C1/C2/C3/C4 and similar cycles are **experimental instances inside this architecture**, not the architecture itself.

They provide evidence for candidate behavior and decision gates. The production architecture is selected later from the accumulated scientific and production-fit evidence.
