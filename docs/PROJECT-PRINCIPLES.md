# Academy × TRACTIAN — Non-Negotiable Project Principles

**Status:** mandatory repository-wide governance  
**Checkpoint:** 2026-09-05 production rebaseline  
**Applies to:** research, architecture, models, prompts, evaluators, tools, runtimes, data, security, observability, deployment, UI and every material technical decision.  
**Formal source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Execution plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)

These principles override convenience, novelty, implementation momentum and prior provisional choices. A component is not final because it works, is popular, is already implemented or passed one minimum gate.

## North Star

> **Deliver the strongest defensible TRACTIAN × Inteli product: a remote, multi-user, production-oriented Agent + Evaluation platform whose behavior, architecture, safety, quality and operational value are measurable and observable.**

The project optimizes the requested outcome, not research volume, framework count or architectural sophistication.

Every material workstream must map to at least one of:

1. a formal TAPI/delivered-package requirement;
2. an academic evaluation criterion;
3. a material production/security/reliability risk;
4. a measurable user/operational-value requirement; or
5. an experiment required to choose among credible alternatives for the above.

If it maps to none, defer it.

## P0 — Production-first, remote-first, never demo-first

The final serving path is a real remotely deployed product, not a local demo.

### Production eligibility

Production mode must not depend on:

- `localhost` / `127.0.0.1` services;
- a developer laptop or manually running process;
- local/open-weight model serving;
- SQLite/DuckDB/filesystem state as production source of truth;
- test doubles, scripted scenario sources or mock provider responses;
- browser-provided tenant/identity/permission authority.

Local execution remains valid for development, deterministic tests, reproduction and controlled benchmarks. It is not evidence that the deployed product is production-ready.

Production configuration should fail closed when a forbidden local dependency is detected.

### Cost policy

Cost is a **measured optimization objective and operating constraint**, not a universal architecture veto.

```text
unbounded spend / silent paid spillover       FORBIDDEN
unapproved paid execution/deployment          FORBIDDEN
cost measurement and budgets                  REQUIRED
free option that meets all hard gates         PREFERRED when Pareto-competitive
paid option needed for stronger production    ELIGIBLE only after explicit owner authorization
```

No assistant, workflow or deployment automation may create paid usage merely because a paid candidate is technically superior. A budget/spend-bearing production step requires explicit authorization and must expose expected/actual cost.

Historical USD-zero provider experiments remain valid evidence for their original scope; this prospective policy does not rewrite their frozen protocols.

### Production evidence

A production claim requires evidence from the deployed path itself. Repository tests may qualify algorithms and contracts, but do not automatically prove:

- deployed availability/HA;
- capacity/SLO;
- autoscaling;
- backup/restore;
- RTO/RPO;
- remote IAM;
- live provider reliability.

Those claims require remote tests and observable production evidence.

## Source hierarchy

When upstream sources differ:

1. current/updated TAPI;
2. delivered TRACTIAN package and contract;
3. executable supplied API behavior/tests;
4. kickoff/partner guidance compatible with formal sources;
5. project research and assumptions.

Record discrepancies instead of silently reconciling them.

## Priority rule

```text
P0 — requested capability + production/security blockers
        ↓
P1 — measurable quality, evaluation and operational value
        ↓
P2 — optional complexity only after a measured gap
```

P0/P1 work must not be displaced by RAG, vector DB, multi-agent decomposition, persistent memory, MCP, framework migration, Kafka/Redis or other optional components merely because they are modern.

## P1 — Systematic research before material choices

Every material choice follows:

```text
decision question
→ requirement/risk mapping
→ constraints
→ systematic primary-source research
→ simple/null baseline + credible alternatives
→ preregistered metrics and hard gates
→ controlled quantitative comparison
→ robustness/failure analysis
→ production-fit analysis
→ Pareto decision
→ ADR + reversal trigger
→ regression protection
```

Rules:

1. Define the decision question and success/failure criteria before selecting a solution.
2. Search broadly enough to include materially different alternatives and `NO_CHANGE`.
3. Prefer primary sources and reproducible project evidence.
4. Compare candidates under the same workload and constraints where possible.
5. Use repeated runs, paired comparisons, distributions and uncertainty estimates when relevant.
6. Use ablations when attribution matters.
7. Test failure/adversarial conditions and operational variability.
8. Evaluate correctness, safety, reliability, latency, throughput, cost, scalability, portability, maintainability and observability.
9. Use Pareto/frontier reasoning rather than hiding trade-offs in arbitrary weighted scores.
10. Record rejected options and reversal triggers.
11. A changed hard assumption reopens a previously frozen choice prospectively; historical evidence itself stays immutable.

### Decision states

- `UNASSESSED` — not adequately evaluated.
- `RESEARCHED` — alternatives/evidence mapped.
- `QUALIFIED` — passes minimum gates; not necessarily best.
- `PREFERRED` — best-supported currently after comparison.
- `FROZEN` — best-supported for the stated scope after robustness/production validation.
- `SUPERSEDED` — prospectively replaced by stronger evidence.
- `NO_SELECTION` / `NO_CHANGE` — valid result when no candidate deserves promotion.

Passing one gate proves qualification, not optimality.

## P2 — Quantitative before qualitative

Where a property can be validly measured, measure it.

Prefer:

- rates and distributions;
- p50/p95/p99;
- paired deltas;
- confidence intervals/effect sizes;
- error/failure rates;
- resource/cost usage;
- repeated-run stability;
- calibration/agreement metrics;
- operational-value deltas.

Thresholds must be justified by a hard requirement or empirical evidence.

Qualitative judgment is reserved for dimensions that cannot be reduced reliably to deterministic metrics. Semantic/LLM judges must be calibrated before they can gate candidates.

## P3 — Adaptive where valuable, deterministic where safety-critical

Adaptive behavior is encouraged when context-sensitive decisions can outperform a simpler static baseline.

Potentially adaptive:

- investigation depth;
- evidence gathering/tool ordering;
- stopping;
- clarification/abstention/escalation thresholds;
- provider/model routing;
- retry/backoff within safe semantics;
- contextual time/resource budget;
- visualization prioritization.

Always deterministic/hard-gated:

- authentication and tenant binding;
- RLS/authorization;
- permission/resource scope;
- schema validation;
- consequential-action confirmation;
- custody/idempotency/leases/fencing;
- privacy/field deny-lists;
- evaluator partition/gold isolation;
- hard execution/resource caps.

Adaptivity must be observable, reproducible enough to debug and promoted only after measured benefit.

## P4 — Eval-driven engineering

Evaluation controls the engineering loop:

```text
requirement
→ evaluator/measurement design
→ baseline
→ candidate hypothesis
→ preregistration
→ implementation
→ controlled evaluation
→ diagnosis
→ comparison
→ promote/reject/no-change
→ regression coverage
```

Mandatory implications:

1. Define measurable success before material implementation whenever feasible.
2. Establish a baseline before claiming improvement.
3. Keep DEV / VALIDATION / LOCKED_TEST boundaries explicit.
4. Prefer deterministic ground truth over LLM judges when exact checks exist.
5. Validate judges/evaluators before allowing them to gate candidates.
6. Preserve failed experiments and consumed attempts.
7. Separate operational failure from scientific/task-quality failure.
8. Evaluate conclusion **and** observable execution process: tool choice, arguments, evidence, stopping, escalation/action behavior and safety.
9. Exact wording is not the primary correctness signal when operational conclusion can be evaluated directly.
10. Production telemetry should feed later controlled re-evaluation, never bypass hard safety constraints.

## Documentation and provenance gate

Before material implementation, the issue/plan must state:

- requirement/risk mapping;
- current baseline;
- credible alternatives;
- hard constraints;
- metrics and hard gates;
- robustness/failure plan;
- production-fit evidence required;
- stopping/decision semantics;
- regression/reversal triggers.

Frozen/source-pinned evidence is never silently rewritten or cosmetically moved. Repository cleanup follows `docs/REPOSITORY-CLEANUP-AUDIT.md` and the lifecycle rules in `docs/README.md`.

## Completion gate

A material workstream is not done unless all applicable conditions hold:

- [ ] maps to an explicit requirement/risk/value objective;
- [ ] baseline and decision question are explicit;
- [ ] credible alternatives were researched;
- [ ] metrics/hard gates were defined before final selection;
- [ ] controlled quantitative evaluation exists where applicable;
- [ ] uncertainty/repeated-run behavior was measured where stochasticity matters;
- [ ] robustness/failure behavior was tested;
- [ ] production fitness was measured on the relevant path rather than inferred from a demo;
- [ ] production mode has no forbidden local serving dependency;
- [ ] cost is bounded, measured and explicitly authorized if non-zero;
- [ ] adaptive behavior was compared with a simpler static baseline where relevant;
- [ ] evaluator/judge validity is established for gating metrics;
- [ ] trade-offs/Pareto position are understood;
- [ ] decision/reversal triggers are documented;
- [ ] regression protection exists;
- [ ] claims remain bounded by evidence;
- [ ] applicable TAPI/acceptance rows remain covered.

If an applicable item is missing, the correct state is still research/experimental/incomplete — not production-ready.
