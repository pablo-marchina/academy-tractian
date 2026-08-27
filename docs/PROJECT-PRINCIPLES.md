# Academy × TRACTIAN — Non-Negotiable Project Principles

**Status:** mandatory repository-wide governance  
**Applies to:** research, architecture, models, prompts, evaluators, judges, tools, runtimes, retrieval, memory, orchestration, data, security, observability, deployment, UI/integration and any other material project decision.  
**Formal project source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)

These principles override convenience, novelty, implementation momentum and prior provisional choices. A component or decision is not final merely because it works, passes a minimum gate, is already implemented, is popular, or was previously selected.

## Project North Star — maximize the actual requested delivery

The fixed objective of this repository is:

> **Deliver the strongest defensible individual TRACTIAN × Inteli project against the actual assignment, delivered package, partner-quality guidance and academic criteria, while following P1–P4 rigorously.**

The project must optimize for the requested outcome, not for research volume, benchmark novelty, framework sophistication or the number of technologies used.

Every material workstream must map to at least one of:

1. a formal TAPI/delivered-package requirement;
2. an academic evaluation criterion;
3. a material security/reliability/production risk that could block the requested delivery; or
4. an experiment required to select among credible alternatives for one of the above.

If it maps to none, defer it.

### Canonical source hierarchy

When upstream sources differ, use:

1. **[UPDATED] TAPI** — formal scope, deliverables and academic criteria;
2. **delivered TRACTIAN project package** — Student Guide, agent input, evaluation material, contract/docs and synthetic environment as actually delivered;
3. **executable supplied API behavior/tests** — operational truth for the simplified API when prose and implementation differ;
4. **kickoff partner guidance** — product-quality guidance where compatible with the written sources;
5. **project-generated research/assumptions** — hypotheses/extensions that must never overwrite upstream requirements.

Record discrepancies instead of silently reconciling them. The current audited bundle and hashes are frozen in `research/tractian-source-baseline-2026-08-27.md`.

### Acceptance-first priority

Use this delivery priority throughout development:

```text
P0 — requested capabilities + trustworthy evaluation
        ↓
P1 — production/security/reliability needed to operate P0 well
        ↓
P2 — optional complexity only when measured benefit justifies it
```

P0 coverage and rubric quality must not be sacrificed to add RAG, vector DB, reranking, multi-agent decomposition, persistent memory, MCP, adaptive routing, a richer UI or any other optional component merely because it is interesting or fashionable.

### Academic excellence target

The final project should maximize evidence quality across the official evaluation dimensions:

- API integration quality;
- technical coherence;
- hypothesis/experiment clarity;
- quality of result analysis;
- limitations and risk treatment;
- reproducibility;
- documentation;
- demonstration quality.

These dimensions are cross-cutting acceptance objectives, not end-of-project polish.

## P1 — Systematic research and comparative decision-making

Every material project decision must be preceded by a systematic decision process.

Required sequence:

`decision question → requirements/constraints → systematic research → credible alternative set → preregistered comparison → quantitative experiments → robustness/sensitivity analysis → production-fit analysis → decision record → confirmation/freeze`

Mandatory rules:

1. Define the decision question, scope, hard constraints and success/failure criteria before selecting a solution.
2. Search broadly enough to identify all credible materially different alternatives, including the null/simple option and alternative architectural patterns.
3. Prefer primary sources: project/API contracts, specifications, source code, official documentation, peer-reviewed or otherwise primary research, and reproducible project experiments.
4. Compare viable alternatives under the same task distribution and controlled conditions whenever possible.
5. Use quantitative measurements, uncertainty estimates, repeated runs and paired comparisons where applicable.
6. Include ablations so improvements can be attributed to the component being evaluated.
7. Test robustness, adversarial/failure conditions, sensitivity to configuration and operational variability.
8. Evaluate production-relevant trade-offs, including correctness, safety, reliability, latency, throughput, cost/resource use, scalability, portability, maintainability, observability and operational complexity.
9. Use Pareto/frontier reasoning when objectives conflict; do not hide trade-offs in an arbitrary weighted score unless the utility function itself is justified and preregistered.
10. Record evidence, alternatives, results, uncertainty, rejected options, reversal triggers and unresolved questions in an ADR or equivalent decision record.
11. When an upstream project source is updated or newly delivered, reconcile the requirement/acceptance maps before allowing downstream architecture momentum to continue unchanged.

### Decision-state semantics

Every material choice should be understood as one of these states:

- `UNASSESSED` — no adequate systematic evaluation yet.
- `RESEARCHED` — alternatives and evidence mapped, but no sufficient experiment/decision yet.
- `QUALIFIED` — candidate meets minimum gates; this does **not** mean it is the best choice.
- `PREFERRED` — candidate is currently best-supported after a broad comparative evaluation, but confirmation or production validation may still be pending.
- `FROZEN` — best-supported choice after systematic comparison, robustness confirmation and production-fit validation; change requires new evidence or a failed assumption.
- `SUPERSEDED` — replaced by a better-supported choice.

**Passing a gate proves qualification, not optimality.** A choice may be called final only when no credible material alternative remains unevaluated within the explicitly defined search scope and project constraints.

### Meaning of “best possible”

The project does not claim mathematical global optimality. “Best possible” means the **best-supported known option after an explicit, sufficiently broad and reproducible search of the credible decision space**, with quantitative comparison and robustness/production confirmation, while preserving full required-scope coverage. If a material alternative remains untested or a P0 delivery requirement remains uncovered, the decision/project is not final.

## P2 — Production-first, never demo-first

The target is a real production-path final system, not a presentation demo, scripted prototype or benchmark-only artifact.

Therefore:

- demos, mocks, fixtures, scripted paths and test doubles may validate infrastructure, but cannot establish production quality or agent capability;
- architecture must be evaluated for real deployment constraints, failure recovery, security, authorization, privacy, observability, reproducibility, maintainability, scaling, latency, throughput and resource/cost behavior;
- integrations must exercise real supplied contracts and realistic failure modes before production readiness is claimed;
- state-changing behavior requires explicit authorization, idempotency/retry semantics where applicable, auditability and safe failure behavior;
- production configuration, dependency/version control, secrets handling, environment setup, monitoring and rollback/reversal paths are part of the product, not post-demo cleanup;
- a component that improves a benchmark but is operationally fragile, unsafe, unaffordable, unobservable or non-maintainable cannot be considered the final choice;
- introducing the agent must not make the underlying support workflow less available: provider/model/agent failure must have a safe fallback or human-handoff path;
- customer-facing behavior must distinguish operationally useful conclusions from unnecessary disclosure of internal implementation details;
- consequential action confirmation is a production-policy decision to evaluate explicitly; do not force it into benchmark semantics when the delivered scenario contract already treats a request as authorized execution;
- use a stable agent-facing tool contract and isolate backend/protocol heterogeneity behind adapters when that improves maintainability and reliability;
- for model/provider selection, do not prematurely cap capability merely for cost convenience: compare a strong quality frontier against feasible lower-cost/local options, prove value, then optimize the production Pareto frontier for latency/cost/reliability.

No project milestone may be marked complete solely because the UI/demo works or because a happy-path scenario succeeds.

## P3 — Quantitative and adaptive by default

The project should maximize justified quantitative behavior and runtime adaptivity while preserving deterministic safety boundaries.

### Quantitative-by-default

Where a decision can be measured, it should be measured. Prefer explicit metrics, calibrated thresholds, confidence/uncertainty estimates, distributions and empirical decision rules over unsupported qualitative judgment.

Examples include:

- evidence sufficiency and stopping;
- model/runtime selection;
- retrieval depth and routing;
- tool selection and action authorization;
- reliability and stability;
- latency/throughput/resource budgets;
- confidence, abstention and escalation;
- production health and drift;
- customer-safe communication and escalation-handoff quality when reliable annotation/judging is available.

Thresholds must be justified empirically or by hard requirements, not chosen only for convenience.

### Adaptive-by-default

Static rules/configurations must not be assumed optimal when context-sensitive adaptation can be evaluated. Where justified, the system should adapt behavior to observed task state, evidence sufficiency, uncertainty, risk, API/tool availability, failure state, resource budget and other measurable runtime signals.

Adaptation itself must be evaluated. It must not bypass deterministic security/safety/authorization constraints, must be observable and reproducible enough for debugging, and must demonstrate measurable benefit over simpler static baselines before adoption.

## P4 — Eval-driven engineering across the entire project

The project as a whole is eval-driven. Evaluation is not a final QA phase; it defines and controls the engineering loop.

Required loop:

`requirement → evaluator/measurement design → baseline → candidate hypothesis → preregistration → implementation → controlled evaluation → diagnosis → comparison → decision → regression coverage`

Mandatory implications:

1. Define how success and failure will be measured before materially changing a candidate whenever feasible.
2. Establish a baseline before claiming improvement.
3. Keep DEV/VALIDATION/LOCKED_TEST boundaries explicit and prevent tuning leakage.
4. Separate deterministic evaluation from LLM-judge evaluation whenever deterministic ground truth is available.
5. Validate evaluators and judges themselves before allowing them to gate candidates.
6. Benchmark candidate models, judges, prompts, runtimes, retrieval strategies, guards and architectures rather than accepting the first one that passes.
7. Preserve failed experiments and consumed attempts as evidence; do not silently rerun or erase inconvenient results.
8. Require regression evaluation after material changes.
9. Treat operational failures separately from scientific/task-quality failures.
10. Production telemetry and post-deployment evaluation must eventually feed controlled adaptation/re-evaluation without bypassing frozen safety constraints.
11. Evaluate both the final conclusion and the observable execution process: tool choice, arguments, evidence use, stopping, action/escalation decisions, robustness and safety.
12. Exact wording must not become the primary correctness signal when the requested operational conclusion can be evaluated more directly.

## Repository-wide completion gate

A material component, decision or workstream is **not complete** unless all applicable conditions are satisfied:

- [ ] the work maps to an explicit delivery requirement, academic criterion, material risk or required comparison;
- [ ] decision question and requirements are explicit;
- [ ] systematic research is documented;
- [ ] credible materially different alternatives were identified;
- [ ] comparison criteria and hard constraints were defined before final selection;
- [ ] appropriate baselines and ablations exist;
- [ ] quantitative controlled evaluation was executed;
- [ ] uncertainty/repeated-run behavior was measured where stochasticity matters;
- [ ] robustness, adversarial and failure-mode behavior was evaluated where applicable;
- [ ] production fitness was evaluated, not inferred from a demo;
- [ ] adaptive behavior was considered and compared against static/simple baselines where relevant;
- [ ] evaluator/judge validity is established for any metric used as a gate;
- [ ] no material credible alternative remains unevaluated within the defined search scope;
- [ ] trade-offs and Pareto position are understood;
- [ ] decision and reversal triggers are documented;
- [ ] regression protection exists for the accepted behavior;
- [ ] the evidence supports `PREFERRED`/`FROZEN`, not merely `QUALIFIED`;
- [ ] applicable P0 rows in `DELIVERY-ACCEPTANCE.md` remain covered or have an explicit evidence-honest limitation.

If any applicable item is missing, the correct state is still research/experimental, not done.

## Consequence for existing provisional choices

Existing choices remain valid as historical experimental evidence, but their status must be interpreted using this policy. A previously “qualified” component is not automatically the final project standard. Before final architecture freeze, major choices — including model, semantic judge, orchestration/runtime, retrieval strategy, tool topology, memory, adaptive policies and evaluation stack — must be checked against this repository-wide systematic-comparison rule and against the actual requested delivery.
