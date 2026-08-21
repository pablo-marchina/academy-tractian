# Research Protocol and Architecture Freeze Gate

## Governing policy

This protocol is subordinate to and operationalizes the repository-wide [`../docs/PROJECT-PRINCIPLES.md`](../docs/PROJECT-PRINCIPLES.md). Its four non-negotiable rules apply to **every material project decision**:

1. systematic research and comparative evaluation before final selection;
2. production-first, never demo-first;
3. quantitative and adaptive by default;
4. eval-driven engineering across the entire project.

A candidate that merely passes a minimum acceptance gate is `QUALIFIED`, not necessarily `PREFERRED` or `FROZEN`.

## Objective

Eliminate all material **researchable** uncertainty before freezing the production architecture. Unknowns that depend exclusively on the TRACTIAN contract, environment or partner policy must be isolated as explicit external dependencies rather than silently assumed.

The final architecture must represent the best-supported known design after a sufficiently broad search of credible alternatives, controlled quantitative comparison, robustness/sensitivity testing and production-fit validation. If a material credible alternative remains unevaluated, the relevant decision cannot be considered final.

## Research method

For every architectural, methodological, model, evaluator, judge, prompt, runtime, retrieval, memory, routing, tool, security, observability or deployment decision:

1. **Define the decision** and the project requirement(s) it affects.
2. **Define hard constraints and evaluation outcomes before selection**, including safety and production constraints.
3. **Systematically enumerate credible alternatives**, including the null/simple baseline and materially different architectural patterns.
4. **Collect primary evidence**: project/API contract, specifications, papers, official docs/source and prior reproducible experiments.
5. **Separate facts from hypotheses and unknowns**.
6. **Define baselines, ablations and a fair comparison protocol**.
7. **Identify measurable trade-offs**: correctness, reliability, safety, groundedness, latency, throughput, resource/cost use, scalability, implementation/operational complexity, portability, maintainability and observability.
8. **Preregister the discriminating experiment** before observing outcome-dependent labels whenever feasible.
9. **Run repeated/paired quantitative evaluation** where stochasticity or matched scenarios matter, preserving configuration/seeds and uncertainty estimates.
10. **Test robustness and failure modes**, including adversarial or degraded conditions where relevant.
11. **Evaluate adaptivity explicitly**: compare context-sensitive/adaptive behavior against simpler static baselines where adaptation is plausible.
12. **Evaluate production fitness explicitly**; do not infer it from a demo or happy-path benchmark.
13. **Analyze the Pareto frontier/trade-offs** rather than hiding conflicting objectives in unjustified weighted scores.
14. **Record the result in an ADR**, including rejected candidates and reversal triggers.
15. **Classify the decision state** as `UNASSESSED`, `RESEARCHED`, `QUALIFIED`, `PREFERRED`, `FROZEN` or `SUPERSEDED`.
16. **Revisit the decision** when new evidence appears, the TRACTIAN API violates an assumption, production telemetry reveals a failure mode, or a credible new alternative could materially dominate the current choice.

## Eval-driven rule

Evaluation is a prerequisite and continuous control loop, not a final QA phase.

Default engineering sequence:

`requirement → evaluator/metric validity → baseline → research/alternatives → hypothesis → preregistration → implementation → controlled measurement → diagnosis → comparison → decision → regression evaluation`

Consequences:

- no improvement claim without a baseline;
- no final model/judge/runtime/retrieval/architecture choice from a single candidate trial;
- evaluator and judge validity must be established before their labels can gate candidates;
- deterministic ground truth is preferred over LLM judging when available;
- operational failures are separated from scientific/task-quality failures;
- failed experiments and consumed attempts remain part of the evidence record;
- candidate tuning from VALIDATION or LOCKED_TEST feedback is forbidden;
- material accepted changes require regression measurement.

## Quantitative and adaptive rule

Where a project decision can be measured, it should be measured. Metrics, calibrated thresholds, distributions, repeated-run stability and uncertainty estimates are preferred to unsupported qualitative judgments.

Static behavior is not presumed optimal. If runtime context can justify adaptation — evidence sufficiency, uncertainty, risk, tool/API availability, failure state, resource budget, latency budget or similar measurable signals — adaptive strategies should be included in the candidate set and compared quantitatively against simpler static baselines.

Adaptivity must remain bounded by deterministic authorization/safety constraints and must be observable, auditable and testable.

## Production-first rule

The project target is a production-grade final system.

A demo, mock, fixture, scripted trace or local happy path may prove infrastructure behavior but cannot prove production readiness or agent quality. Final acceptance must account for applicable production concerns including:

- reliability and failure recovery;
- security, authorization and privacy;
- side-effect safety and auditability;
- idempotency/retry semantics where applicable;
- observability and diagnosability;
- reproducible configuration/dependency management;
- latency, throughput and resource/cost constraints;
- scalability and concurrency behavior;
- maintainability and portability;
- deployment/rollback and operational ownership;
- realistic integration and degraded-mode testing.

## Evidence grading

| Grade | Evidence |
|---|---|
| A | Project/API contract, reproducible project experiment, formal specification, primary benchmark/paper directly matching the problem |
| B | Official framework/library documentation or source code; adjacent primary research |
| C | Secondary technical source or indirect benchmark |
| D | Anecdote, popularity, unsupported intuition |

Architecture freeze decisions should normally have at least one A/B source and, for consequential alternatives, a repository experiment. Evidence quality does not remove the requirement to compare credible alternatives when the decision is empirically testable.

## Research anti-patterns

The following do **not** count as sufficient justification:

- “framework X is industry standard” without problem-specific evidence;
- selecting the first candidate that passes a minimum gate and calling it optimal;
- comparing only one serious candidate when credible alternatives exist;
- choosing multi-agent because it is more advanced;
- adding RAG because the project involves knowledge;
- adding MCP merely because the TAPI mentions it;
- using an LLM judge when deterministic ground truth exists;
- selecting a semantic judge because it passes a small reliability gate without broad judge comparison before final freeze;
- selecting a model from a generic leaderboard without testing the TRACTIAN task distribution;
- optimizing a prompt before freezing the evaluation objective;
- collapsing safety, accuracy, latency and cost into arbitrary weighted scores without justified constraints/utility;
- testing only one stochastic run per scenario when repeatability matters;
- evaluating only final text for actions that mutate state;
- claiming production readiness from a demo or happy path;
- introducing adaptive complexity without showing measurable benefit over a simpler static baseline.

## Architecture Decision Record (ADR) requirements

Every major ADR must contain:

- Context/problem;
- Project requirements affected;
- Search scope and credible alternatives considered;
- Evidence reviewed;
- Decision criteria and hard constraints;
- Baselines and ablations;
- Experiment and preregistration (if applicable);
- Quantitative results with uncertainty/repeated-run treatment where relevant;
- Robustness/failure/adversarial results where relevant;
- Production-fit analysis;
- Adaptivity comparison where relevant;
- Pareto/trade-off analysis;
- Decision state (`UNASSESSED` / `RESEARCHED` / `QUALIFIED` / `PREFERRED` / `FROZEN` / `SUPERSEDED`);
- Decision;
- Consequences/trade-offs;
- Failure/reversal trigger;
- Remaining unevaluated alternatives, if any.

An ADR cannot mark a choice `FROZEN` while a material credible alternative remains unevaluated within the defined search scope.

## Freeze Gate

Architecture can be labeled `FROZEN-v1` only when all items below are satisfied.

### Systematic decision completeness

- [ ] All material architecture/model/judge/runtime/retrieval/tool/memory/orchestration/evaluation choices have explicit decision records.
- [ ] Credible materially different alternatives were systematically identified for each major choice.
- [ ] Fair quantitative comparisons were completed for all major empirically testable choices.
- [ ] Appropriate baselines and ablations were completed.
- [ ] Repeated-run uncertainty/stability was measured where stochasticity matters.
- [ ] Robustness, adversarial and failure-mode evaluation was completed where applicable.
- [ ] Production-fit constraints were evaluated for the preferred candidates.
- [ ] Adaptive alternatives were considered and tested where runtime context can materially improve decisions.
- [ ] No major choice is frozen merely because it passed a minimum qualification gate.
- [ ] No credible material alternative remains unevaluated within each documented search scope.

### Requirements and domain

- [ ] 100% of TAPI requirements mapped to a deliverable and verification method.
- [ ] Domain entities/actions mapped from the actual Swagger/OpenAPI contract.
- [ ] Permission model understood.
- [ ] High-impact/mutating actions identified.
- [ ] API partial/inconclusive/conflict/unavailable semantics understood.
- [ ] State reset/snapshot/replay capabilities understood.
- [ ] Rate limits and experiment constraints understood.

### Agent engineering

- [ ] Baseline agent design defined.
- [ ] Candidate orchestrators compared.
- [ ] Tool schema/dispatch strategies compared and decided.
- [ ] Planning/stopping policies compared and decided.
- [ ] State/memory boundaries compared and decided.
- [ ] Ask/investigate/act/abstain/escalate policy specified and evaluated.
- [ ] Deterministic authorization/policy boundaries specified.
- [ ] High-impact action verification policy specified and evaluated.
- [ ] MCP alternatives/ADR completed.
- [ ] Multi-agent vs simpler alternatives ADR completed.
- [ ] Retrieval/RAG vs non-RAG alternatives ADR completed.

### Evaluation

- [ ] Canonical scenario schema defined.
- [ ] Gold-dataset creation/QA methodology defined.
- [ ] Development/validation/locked-test split policy defined.
- [ ] Final-state evaluator defined where state ground truth exists.
- [ ] Tool/argument/trajectory/evidence evaluators defined and validated.
- [ ] Safety/policy evaluator defined and validated.
- [ ] Reliability repeated-run protocol defined.
- [ ] Fault-injection profiles defined.
- [ ] Adversarial/red-team protocol defined.
- [ ] Human/LLM-judge role and judge-validation policy defined.
- [ ] Credible judge architectures/models compared before final judge freeze.
- [ ] Failure taxonomy defined.

### Quantitative method

- [ ] Primary outcomes and hard safety constraints defined.
- [ ] Secondary efficiency/production outcomes defined.
- [ ] Confidence/uncertainty method defined.
- [ ] Paired-comparison method defined.
- [ ] Multiple-run aggregation defined.
- [ ] Missing/error run treatment defined.
- [ ] Seed/config/version recording defined.
- [ ] Baselines and ablations defined.
- [ ] Model-selection protocol includes broad candidate discovery/comparison.
- [ ] Adaptive-vs-static comparison policy defined where relevant.
- [ ] Optimization is isolated from measurement-only/final data.

### Production readiness

- [ ] Security and authorization boundaries verified end-to-end.
- [ ] Failure recovery and degraded modes evaluated.
- [ ] Side effects are auditable and safely controlled.
- [ ] Retry/idempotency behavior evaluated where applicable.
- [ ] Latency/throughput/resource/cost envelopes measured.
- [ ] Scalability/concurrency behavior evaluated where applicable.
- [ ] Monitoring/observability and production diagnostics defined.
- [ ] Configuration, secrets, dependencies and environment setup are production-reproducible.
- [ ] Deployment and rollback/reversal strategy defined.
- [ ] Integration tests exercise realistic production contracts, not only mocks.
- [ ] No production-readiness claim depends solely on demo behavior.

### Observability and reproducibility

- [ ] Trace schema frozen.
- [ ] Tool calls and side effects traceable end-to-end.
- [ ] Model/config/prompt/tool/API versions recorded.
- [ ] OpenTelemetry/export strategy decided through comparison/production requirements.
- [ ] Experiment artifacts are serializable and versioned.
- [ ] Replays can distinguish API randomness from agent/model randomness where feasible.
- [ ] Environment setup is reproducible.

### Remaining uncertainty

- [ ] Zero material **researchable** questions remain open for final production architecture.
- [ ] Zero credible material alternatives remain unevaluated inside the documented decision scopes.
- [ ] Any remaining questions are explicitly marked `TRACTIAN_DEPENDENCY` with owner/date.

## Change control after freeze

After `FROZEN-v1`, a high-impact architectural change requires:

1. new evidence, failed assumption, production signal or credible potentially dominating alternative;
2. systematic research update and candidate comparison;
3. ADR amendment/new ADR;
4. regression experiment against the same appropriate evaluation splits;
5. no regression on hard safety constraints;
6. production-fit revalidation where affected.

This turns architecture evolution into an auditable, eval-driven experimental process instead of ad-hoc iteration.
