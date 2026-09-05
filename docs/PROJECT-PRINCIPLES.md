# Academy × TRACTIAN — Non-Negotiable Project Principles

**Status:** mandatory repository-wide governance  
**Checkpoint:** 2026-09-05 corrected production rebaseline  
**Applies to:** research, architecture, models, prompts, evaluators, tools, runtimes, data, security, observability, deployment, UI and every material technical decision.  
**Formal source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Execution plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)

These principles override convenience, novelty, implementation momentum and prior provisional choices. A component is not final because it works, is popular, is already implemented or passed one minimum gate.

## North Star

> **Deliver the strongest defensible TRACTIAN × Inteli product: a remote, multi-user, production-oriented Agent + Evaluation platform whose behavior, architecture, safety, quality and operational value are measurable and observable, while keeping project cash cost at USD 0.**

The project optimizes the requested outcome, not research volume, framework count or architectural sophistication.

Every material workstream must map to at least one of:

1. a formal TAPI/delivered-package requirement;
2. an academic evaluation criterion;
3. a material production/security/reliability risk;
4. a measurable user/operational-value requirement; or
5. an experiment required to choose among credible alternatives for the above.

If it maps to none, defer it.

## P0 — Production-first, remote-first, zero-cost, never demo-first

The final serving path is a real remotely deployed product, not a local demo, and must operate within the project's **USD 0 actual cash-cost hard constraint**.

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

### Zero-cost hard constraint

**USD 0 actual cash cost is a non-negotiable project eligibility gate.** It applies prospectively to the complete project path, including models/APIs, hosting, databases, IAM, telemetry, CI/CD add-ons and other hosted/runtime dependencies selected for the final solution.

```text
actual project cash cost > USD 0              INELIGIBLE
silent paid spillover / automatic billing     FORBIDDEN
required paid upgrade to keep normal path     INELIGIBLE
USD 0 candidate                               ELIGIBLE FOR TECHNICAL EVALUATION
USD 0 + all technical hard gates              ELIGIBLE FOR PROMOTION
no USD 0 candidate passes all gates           NO_SELECTION / explicit blocker
```

Rules:

1. Zero cost is **necessary, not sufficient** for selection.
2. A free candidate still must pass quality, safety, reliability, production-fit and evaluation hard gates.
3. A technically superior paid candidate may be researched as an external benchmark/reference, but it is **not selectable** for this project while the USD 0 rule applies.
4. Free tiers/credits must be evaluated for durability, quotas, sleep/scale-to-zero behavior, account/billing requirements and risk of unexpected charge.
5. The selected production design must have a fail-closed spending boundary: no automatic paid spillover.
6. If production-grade quality cannot be achieved inside USD 0, the correct result is an explicit limitation/blocker or `NO_SELECTION`; the project constraint is not silently relaxed.
7. Historical USD-zero experiments remain immutable evidence for their original scopes.

### Production evidence

A production claim requires evidence from the deployed path itself. Repository tests may qualify algorithms and contracts, but do not automatically prove:

- deployed availability/HA;
- capacity/SLO;
- autoscaling;
- backup/restore;
- RTO/RPO;
- remote IAM;
- live provider reliability.

Those claims require remote tests and observable production evidence, still under the USD 0 constraint.

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
P0 — hard constraints + requested capability + production/security blockers
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
→ hard constraints (including USD 0)
→ systematic primary-source research
→ eligibility filter
→ simple/null baseline + credible eligible alternatives
→ preregistered metrics and hard gates
→ controlled quantitative comparison
→ robustness/failure analysis
→ production-fit analysis
→ Pareto decision among eligible candidates
→ ADR + reversal trigger
→ regression protection
```

Rules:

1. Define the decision question and success/failure criteria before selecting a solution.
2. Search broadly enough to include materially different alternatives and `NO_CHANGE`.
3. Prefer primary sources and reproducible project evidence.
4. Apply hard constraints before promotion; ineligible paid candidates cannot win a project selection.
5. Compare eligible candidates under the same workload and constraints where possible.
6. Use repeated runs, paired comparisons, distributions and uncertainty estimates when relevant.
7. Use ablations when attribution matters.
8. Test failure/adversarial conditions and operational variability.
9. Evaluate correctness, safety, reliability, latency, throughput, resource use, scalability, portability, maintainability and observability.
10. Use Pareto/frontier reasoning rather than hiding trade-offs in arbitrary weighted scores.
11. Record rejected/ineligible options and reversal triggers.
12. A changed user-specified hard constraint may reopen a choice only when the user explicitly changes that constraint; historical evidence itself stays immutable.

### Decision states

- `INELIGIBLE` — violates a hard project constraint, including USD 0.
- `UNASSESSED` — not adequately evaluated.
- `RESEARCHED` — alternatives/evidence mapped.
- `QUALIFIED` — passes minimum gates; not necessarily best.
- `PREFERRED` — best-supported eligible candidate currently after comparison.
- `FROZEN` — best-supported eligible solution for the stated scope after robustness/production validation.
- `SUPERSEDED` — prospectively replaced by stronger eligible evidence.
- `NO_SELECTION` / `NO_CHANGE` — valid result when no eligible candidate deserves promotion.

Passing the zero-cost gate or one technical gate proves eligibility/qualification only, not optimality.

## P2 — Quantitative before qualitative

Where a property can be validly measured, measure it.

Prefer:

- rates and distributions;
- p50/p95/p99;
- paired deltas;
- confidence intervals/effect sizes;
- error/failure rates;
- resource use and explicit USD cash cost (= 0 for selected project paths);
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
- provider/model routing among USD-zero eligible providers;
- retry/backoff within safe semantics and free-tier quotas;
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
- hard execution/resource caps;
- zero-cost/no-paid-spillover boundary.

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
10. Production telemetry should feed later controlled re-evaluation, never bypass hard safety or zero-cost constraints.

## Documentation and provenance gate

Before material implementation, the issue/plan must state:

- requirement/risk mapping;
- current baseline;
- credible alternatives;
- hard constraints, explicitly including USD 0;
- candidate eligibility status;
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
- [ ] USD 0 eligibility was verified for any selected external/hosted dependency;
- [ ] no selected path can silently spill into paid usage;
- [ ] metrics/hard gates were defined before final selection;
- [ ] controlled quantitative evaluation exists where applicable;
- [ ] uncertainty/repeated-run behavior was measured where stochasticity matters;
- [ ] robustness/failure behavior was tested;
- [ ] production fitness was measured on the relevant path rather than inferred from a demo;
- [ ] production mode has no forbidden local serving dependency;
- [ ] actual project cash cost remains USD 0;
- [ ] adaptive behavior was compared with a simpler static baseline where relevant;
- [ ] evaluator/judge validity is established for gating metrics;
- [ ] trade-offs/Pareto position among eligible candidates are understood;
- [ ] decision/reversal triggers are documented;
- [ ] regression protection exists;
- [ ] claims remain bounded by evidence;
- [ ] applicable TAPI/acceptance rows remain covered.

If an applicable item is missing, the correct state is still research/experimental/incomplete — not production-ready. If no USD-zero candidate clears all required gates, the correct outcome is `NO_SELECTION` or an explicit blocker, never a paid fallback.
