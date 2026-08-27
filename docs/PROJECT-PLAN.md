# Academy × TRACTIAN — Governed Project Plan to Production Delivery

**Status:** ACTIVE / canonical macro plan  
**Planning checkpoint:** 2026-08-26 22:51 BRT  
**Final delivery target:** 2026-09-08  
**Current status:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

## 1. Planning objective

Finish the project with the strongest defensible evidence and the strongest production-path implementation achievable by 2026-09-08, without weakening scientific validity, production fitness, security boundaries or evaluator independence.

This plan applies the four repository-wide rules directly:

- **P1 — systematic comparison:** no material architecture/product decision is final before credible alternatives are compared under explicit requirements;
- **P2 — production-first:** production constraints are evaluated during selection, not added after a benchmark winner is chosen;
- **P3 — quantitative/adaptive by default:** measurable decisions use metrics/uncertainty and adaptive policies must beat simpler static baselines;
- **P4 — eval-driven engineering:** requirements, evaluators, baselines and regression coverage drive implementation from research through deployment.

A gate PASS means evidence for that gate. It does not automatically mean `PREFERRED`, `FROZEN`, final or production-ready.

## 2. Macro phases

| Phase | Objective | State |
|---|---|---|
| 1. Governance and benchmark foundation | Freeze evidence roles, benchmark integrity, access rules and evaluation semantics | COMPLETE |
| 2. Candidate exploration and failure learning | Preserve and learn from E-series and P12-C1/C2/C3 evidence | COMPLETE / historical evidence retained |
| 3. C4 confirmatory packet generation | Qualify serving route, collect 36/36 common parents, expand locally to 144/144 and freeze | COMPLETE |
| 4. C4 deterministic/statistical/semantic evaluation | Score the immutable packet, run only subsequently authorized statistics and qualify exact survivors | **CURRENT** |
| 5. Production-fit selection and independent validation | Systematically compare production choices, freeze candidate/evaluator generation, obtain authorized independent evidence | PENDING / research may run in parallel |
| 6. Final architecture freeze and production implementation | Freeze evidence-backed architecture and implement the production path | PENDING |
| 7. Integration, regression, controlled deployment and final delivery | Prove the production path end to end and deliver reproducibly | PENDING |

## 3. Current critical path — Phase 4

The current immutable input is `FROZEN_COMPLETE_C4_PACKET`. Exactly 36/36 fresh common parents and 144/144 A00/A10/A01/A11 outputs exist. No further provider generation is authorized for this C4 packet.

### 3.1 Deterministic scoring — current gate

Before execution:

1. identify and verify the exact frozen deterministic scoring implementation and its source pins;
2. identify the exact authorized evaluator-side private oracle/input source without reconstructing it from public fixtures;
3. verify the complete C4 packet, hashes, parent/arm cardinality and source provenance;
4. isolate deterministic scoring from any bootstrap/LOGO/slice/semantic code path;
5. define fail-closed checks for missing rows, duplicate rows, schema mismatch, source mismatch or unauthorized access.

Execution must produce exactly one deterministic result for every authorized fixed output and preserve the immutable output hashes.

After execution:

- validate completeness and deterministic reproducibility;
- record scorer/oracle/input provenance and access counters;
- freeze the deterministic scoring result;
- authorize no later analysis unless the new freeze explicitly permits it.

### 3.2 Statistical gates — only after authorization

After deterministic-scoring freeze, follow the already frozen P12 statistical contract and gate order. This includes the preregistered factorial/paired contrasts, 20,000-resample group/cluster bootstrap, applicable LOGO analyses, slices, safety/failure-family analysis and missingness/denominator reporting only when each transition is authorized.

No new threshold, slice or decision rule may be promoted to confirmatory status after outcomes are observed.

### 3.3 Deterministic survivor decision

- no survivor: stop semantic progression and reassess project scope honestly;
- survivor(s): freeze the exact survivor set and open a separately preregistered semantic child gate only for those exact outputs/arms.

### 3.4 Semantic child gate

Before semantic labels/judgments are exposed, freeze:

- survivor arms;
- claim-packet construction;
- judge/model/configuration;
- evaluator validation evidence;
- metrics and thresholds;
- missingness/failure treatment;
- one-shot/repetition semantics.

Semantic PASS is qualification evidence; it does not by itself make a candidate project-level `PREFERRED`, `FROZEN` or production-ready.

## 4. Parallel architecture and production-fit evidence program — start now, freeze later

Production-first does **not** mean waiting until the end to think about production. Research for material architecture decisions should proceed in parallel now, but no final architecture freeze is allowed before candidate evidence and independent-validation requirements are satisfied.

Every material decision must use this template:

```text
decision question
→ requirements + hard constraints
→ primary-source systematic research
→ credible materially different alternatives
→ simple/null baseline
→ preregistered metrics + comparison design
→ controlled quantitative evaluation
→ uncertainty + repeated-run behavior where relevant
→ robustness / adversarial / failure-mode tests
→ production-fit evaluation
→ Pareto/trade-off analysis
→ ADR + rejected options + reversal triggers
→ PREFERRED
→ confirmation / regression
→ FROZEN
```

### 4.1 Material decision register

The following decisions must be evaluated before final architecture freeze; existing implementations are evidence/candidates, not automatic final standards.

| Decision | Minimum comparison scope | Production metrics that must be included |
|---|---|---|
| Provider/model serving strategy | current viable route vs credible alternatives and simpler serving options | correctness, availability, latency, throughput, cost/quota, portability, failure recovery |
| Orchestration/runtime | simple explicit loop/state machine vs LangGraph and other credible patterns | correctness, determinism, observability, recovery, complexity, latency, maintainability |
| Agent topology | single-agent baseline vs justified decomposition/multi-agent alternatives | task quality, coordination errors, latency, token/cost overhead, debuggability |
| Evidence/retrieval | direct tool/evidence routing baseline vs RAG/vector/reranking only if justified | recall/precision, evidence correctness, latency, storage/ops cost, failure modes |
| Tool protocol/topology | native tool contract baseline vs adapters/protocol alternatives such as MCP where materially useful | schema fidelity, portability, failure isolation, maintainability |
| Memory/state | request-local/stateful baseline vs persistent memory if required | task benefit, contamination risk, privacy, storage cost, reproducibility |
| Adaptive policies | static baseline vs adaptive routing/stopping/retrieval/model selection | quality, uncertainty calibration, resource use, stability, safety-boundary compliance |
| Safety/authorization/retry/idempotency | deterministic safe baseline vs bounded operational policies | unsafe action rate, duplicate-action risk, recovery success, auditability |
| Evaluator/judge stack | deterministic evaluator wherever possible vs validated semantic judge alternatives | agreement/calibration, variance, cost, leakage risk, failure behavior |
| Observability | minimum structured tracing baseline vs richer backends | coverage, debug time, overhead, retention/privacy, operational complexity |
| Deployment topology | simplest viable deployment vs credible scaling patterns | availability, latency, cost, secrets/security, rollback, scalability |
| UI/integration architecture | direct production-path client baseline vs richer UI patterns | task completion, error transparency, authorization UX, maintainability |

A material choice is not final while a credible materially different alternative remains unevaluated within the defined scope.

## 5. Phase 5 — production-fit selection and independent validation

### 5.1 Production-fit candidate decision

Combine candidate quality evidence with the architecture decision program. A benchmark improvement that is fragile, unsafe, unaffordable, unobservable or non-maintainable cannot become the final production choice.

Before independent outcome access:

- freeze the candidate behavior/configuration used for measurement;
- freeze evaluator generation/configuration as required by P12;
- document production-fit evidence and unresolved assumptions;
- document reversal triggers;
- keep hidden independent outcomes inaccessible.

### 5.2 FRESH_BLIND / independent evidence

Independent measurement requires a separate authorization and must preserve custody/isolation rules. Candidate-specific tuning after independent outcomes are seen invalidates a claim that the modified version was independently blind-tested.

If independent evidence fails and a material change is made, create a new candidate/version and a new evidence cycle rather than rebranding the same blind measurement.

### 5.3 Decision-state rule

Use repository states literally:

- `QUALIFIED` — minimum gate passed;
- `PREFERRED` — best-supported current option after broad comparison;
- `FROZEN` — confirmed best-supported choice after robustness and production-fit validation;
- `SUPERSEDED` — replaced by stronger evidence.

## 6. Phase 6 — final architecture freeze and production implementation

Architecture freeze is permitted only when all applicable material decisions satisfy the repository completion gate and the independent-evidence plan/measurement supports the intended claim.

The production implementation must preserve the validated behavior while adding production engineering explicitly rather than silently changing semantics.

Required production concerns include:

- typed API/tool contracts and validation;
- authorization boundaries and auditability;
- bounded retry/idempotency semantics where applicable;
- state/persistence behavior;
- timeout and provider/tool failure handling;
- dependency/configuration pinning;
- secrets/environment handling;
- structured tracing, logs and metrics;
- latency/throughput/resource budgets;
- cost/quota controls;
- security/privacy boundaries;
- reproducible build/deployment;
- rollback/reversal path.

Experimental one-shot constraints such as C4 zero-retry semantics do not automatically become production policy. Production policies require their own requirements, comparison and regression evidence.

## 7. Phase 7 — integration, regression, controlled deployment and final delivery

Protect the final project window primarily for integration and evidence closure rather than repeated speculative research.

Required production-path verification:

1. unit and deterministic regression;
2. evaluator regression and behavior preservation;
3. real integration-contract tests;
4. end-to-end production-path tests;
5. provider/tool failure and recovery tests;
6. authorization/idempotency/security tests;
7. latency/load/resource measurements appropriate to expected use;
8. observability evidence;
9. reproducible environment/secrets setup;
10. rollback/reversal test;
11. staging/shadow/canary path where meaningful and feasible;
12. final release artifact/configuration/version evidence.

Final handoff must include source code, frozen decision records, architecture documentation, evaluation methodology/results, limitations/non-claims, deployment/runbook documentation, monitoring/rollback instructions and a production-path demonstration rather than a mock-only path.

## 8. Repository-wide definition of done

No workstream is `done` merely because it works. All applicable `PROJECT-PRINCIPLES.md` completion checks must hold, including research of alternatives, controlled quantitative comparison, uncertainty, robustness, production fit, evaluator validity, Pareto understanding, ADR/reversal triggers and regression protection.

Project completion requires both:

```text
scientific evidence strong enough for the claims
        +
production-path engineering strong enough for real operation
```

If external constraints prevent the strongest target by 2026-09-08, the correct outcome is an evidence-honest delivery with explicit limitations and unresolved risks, never a stronger claim than the frozen evidence supports.

## 9. Stop / pivot rules

- preserve failed and consumed experiments; never silently erase or rerun them;
- do not score incomplete packets;
- do not cross evaluator/private/independent boundaries before authorization;
- do not promote `QUALIFIED` to `PREFERRED/FROZEN` without systematic comparison;
- do not freeze an architecture because it is already implemented or popular;
- do not add RAG, multi-agent, memory, vector DB, reranking or other complexity without measurable advantage over a simpler baseline;
- do not accept adaptive complexity without measurable benefit over a static baseline and deterministic safety boundaries;
- do not infer production fitness from a demo or benchmark alone;
- after any material implementation change, rerun applicable regression/evaluation before release.
