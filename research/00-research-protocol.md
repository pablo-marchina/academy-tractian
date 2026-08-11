# Research Protocol and Architecture Freeze Gate

## Objective

Eliminate all material **researchable** uncertainty before freezing the production architecture. Unknowns that depend exclusively on the TRACTIAN contract, environment or partner policy must be isolated as explicit external dependencies rather than silently assumed.

## Research method

For every architectural or methodological decision:

1. **Define the decision** and what project requirement it affects.
2. **Enumerate credible alternatives**, including the option to not add a component.
3. **Collect primary evidence**: specification, paper, official docs/source.
4. **Separate facts from hypotheses**.
5. **Identify measurable trade-offs**: correctness, reliability, safety, latency, resource use, implementation complexity, portability and observability.
6. **Design the smallest discriminating experiment** when evidence alone cannot resolve the choice.
7. **Record the result in an ADR**.
8. Revisit the decision if the TRACTIAN API reveals a violated assumption.

## Evidence grading

| Grade | Evidence |
|---|---|
| A | Project/API contract, reproducible project experiment, formal specification, primary benchmark/paper directly matching the problem |
| B | Official framework/library documentation or source code; adjacent primary research |
| C | Secondary technical source or indirect benchmark |
| D | Anecdote, popularity, unsupported intuition |

Architecture freeze decisions should normally have at least one A/B source and, for consequential alternatives, a repository experiment.

## Research anti-patterns

The following do **not** count as sufficient justification:

- “framework X is industry standard” without problem-specific evidence;
- choosing multi-agent because it is more advanced;
- adding RAG because the project involves knowledge;
- adding MCP merely because the TAPI mentions it;
- using an LLM judge when deterministic ground truth exists;
- selecting a model from a generic leaderboard without testing the TRACTIAN task distribution;
- optimizing a prompt before freezing the evaluation objective;
- collapsing safety, accuracy, latency and cost into arbitrary weighted scores without justified constraints/utility;
- testing only one stochastic run per scenario;
- evaluating only the final text for actions that mutate state.

## Architecture Decision Record (ADR) requirements

Every major ADR must contain:

- Context/problem;
- Project requirements affected;
- Alternatives considered;
- Evidence reviewed;
- Decision criteria;
- Experiment required (if any);
- Decision;
- Consequences/trade-offs;
- Failure/reversal trigger;
- Status: proposed / experimental / accepted / superseded.

## Freeze Gate

Architecture can be labeled `FROZEN-v1` only when all items below are satisfied.

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
- [ ] Tool schema/dispatch strategy decided.
- [ ] Planning/stopping policy decided or experiment specified.
- [ ] State/memory boundaries decided.
- [ ] Ask/investigate/act/abstain/escalate policy specified.
- [ ] Deterministic authorization/policy boundaries specified.
- [ ] High-impact action verification policy specified.
- [ ] MCP ADR completed.
- [ ] Multi-agent ADR completed.
- [ ] Retrieval/RAG ADR completed.

### Evaluation

- [ ] Canonical scenario schema defined.
- [ ] Gold-dataset creation/QA methodology defined.
- [ ] Development/validation/locked-test split policy defined.
- [ ] Final-state evaluator defined where state ground truth exists.
- [ ] Tool/argument/trajectory/evidence evaluators defined.
- [ ] Safety/policy evaluator defined.
- [ ] Reliability repeated-run protocol defined.
- [ ] Fault-injection profiles defined.
- [ ] Adversarial/red-team protocol defined.
- [ ] Human/LLM-judge role and judge-validation policy defined.
- [ ] Failure taxonomy defined.

### Quantitative method

- [ ] Primary outcomes and safety constraints defined.
- [ ] Secondary efficiency outcomes defined.
- [ ] Confidence interval method defined.
- [ ] Paired-comparison method defined.
- [ ] Multiple-run aggregation defined.
- [ ] Missing/error run treatment defined.
- [ ] Seed/config/version recording defined.
- [ ] Baselines and ablations defined.
- [ ] Model-selection protocol defined.
- [ ] Optimization is isolated to development/validation data.

### Observability and reproducibility

- [ ] Trace schema frozen.
- [ ] Tool calls and side effects traceable end-to-end.
- [ ] Model/config/prompt/tool/API versions recorded.
- [ ] OpenTelemetry/export strategy decided.
- [ ] Experiment artifacts are serializable and versioned.
- [ ] Replays can distinguish API randomness from agent/model randomness where feasible.
- [ ] Environment setup is reproducible.

### Remaining uncertainty

- [ ] Zero material **researchable** questions remain open.
- [ ] Any remaining questions are explicitly marked `TRACTIAN_DEPENDENCY` with owner/date.

## Change control after freeze

After `FROZEN-v1`, a high-impact architectural change requires:

1. new evidence or failed assumption;
2. ADR amendment/new ADR;
3. regression experiment against the same evaluation split;
4. no regression on hard safety constraints.

This turns architecture evolution into an auditable experimental process instead of ad-hoc iteration.
