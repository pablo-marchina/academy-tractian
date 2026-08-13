# TAPI Requirement Matrix

Source: **[UPDATED] TAPI — Engenharia e Avaliação de Agentes Industriais**, Inteli × TRACTIAN, received 2026-08-13.

Status legend: `CONFIRMED` = explicitly supported by TAPI; `DEPENDENCY` = requires TRACTIAN/API clarification; `PROJECT_CHOICE` = our optional extension.

## Critical scope update — 2026-08-13

The updated TAPI changed the project objective from selecting **one of two tracks** to developing a solution **containing both**:

1. **Construção de agente**; and
2. **Framework de avaliação de agentes**.

Therefore, dual-track coverage is no longer a project extension or framing choice. It is a **confirmed project requirement**. The project architecture should remain unified: the evaluation framework evaluates and drives development of the industrial agent rather than being a disconnected second deliverable.

## Core project requirements

| ID | Requirement | Source section | Type | Verification evidence planned |
|---|---|---|---|---|
| REQ-001 | Individual project | Header | CONFIRMED | Repository authorship / final delivery |
| REQ-002 | Integrate with the TRACTIAN-provided industrial API | Objective / Deliverables | CONFIRMED | Live integration test + trace |
| REQ-003 | Include a technical experiment | Objective | CONFIRMED | Reproducible experiment report + artifacts |
| REQ-004 | Document results | Objective / Documentation | CONFIRMED | README + research/experiment reports |
| REQ-005 | Handle contextualization requests | Context of use | CONFIRMED | Scenario suite |
| REQ-006 | Handle investigation requests using tools | Context of use | CONFIRMED | Scenario + tool trajectory evaluation |
| REQ-007 | Handle execution requests with impact on customer solution | Context of use | CONFIRMED | Side-effect scenarios + final-state evaluator |
| REQ-008 | Be able to request additional information | Context of use | CONFIRMED | Ambiguity/missing-info cases |
| REQ-009 | Be able to consult assets, analyses and technical data | Context of use | CONFIRMED | Tool/API tests |
| REQ-010 | Be able to ask pertinent investigative questions | Context of use | CONFIRMED | Multi-turn scenarios |
| REQ-011 | Execute justified platform actions | Context of use | CONFIRMED | Action policy + state verification |
| REQ-012 | Escalate cases to human analysis | Context of use | CONFIRMED | Escalation scenarios |
| REQ-013 | Handle complete, partial, inconclusive, conflicting and temporarily unavailable query results | API behavior | CONFIRMED | Fault profiles / scenario perturbations |
| REQ-014 | High-impact actions require valid parameters and adequate justification | API behavior | CONFIRMED | Schema/policy/action gate evaluation |
| REQ-015 | Accepted action call represents execution; no additional status loop required | API behavior | CONFIRMED | Tool adapter semantics |
| REQ-016 | Calls and results must be inspectable | Reference architecture | CONFIRMED | End-to-end trace view |
| REQ-017 | Deliver a solution containing both agent construction and an agent-evaluation framework | Objective | CONFIRMED | Integrated runtime + evaluation subsystem demonstrated end-to-end |

## Agent-construction coverage

The construction component is now mandatory. The TAPI says the solution **may explore** the capabilities below; our research goal is to cover all that materially apply and measure them where possible.

| ID | Capability | Status | Planned evidence |
|---|---|---|---|
| AG-001 | Interpret HTTP contracts | CONFIRMED opportunity | OpenAPI-driven adapter + tests |
| AG-002 | Define tools and schemas | CONFIRMED opportunity | Typed tool registry / schema validation |
| AG-003 | Select functions | CONFIRMED opportunity | Tool selection metrics |
| AG-004 | Construct arguments | CONFIRMED opportunity | Exact/semantic/schema argument metrics |
| AG-005 | Planning and stopping policy | CONFIRMED opportunity | Baseline vs structured policy experiment |
| AG-006 | Handle incomplete returns and failures | CONFIRMED opportunity | Fault-injection benchmark |
| AG-007 | Ground/fundament responses | CONFIRMED opportunity | Evidence trace + unsupported-claim evaluator |
| AG-008 | Memory/context across interactions | CONFIRMED opportunity | Multi-turn benchmark + state policy |
| AG-009 | Decide orient vs act vs escalate | CONFIRMED opportunity | Decision policy metrics |
| AG-010 | Execution traceability | CONFIRMED opportunity | OpenTelemetry/app trace |

## Evaluation-framework coverage

The evaluation framework is now a mandatory component of the project objective. The TAPI explicitly lists the following analysis objects.

| ID | Evaluation object explicitly listed by TAPI | Planned canonical signal |
|---|---|---|
| EV-001 | Function choice | Tool precision/recall/correctness |
| EV-002 | Argument accuracy | Schema validity + exact/semantic argument correctness |
| EV-003 | Execution trajectory | Trajectory constraints/goal path/step efficiency |
| EV-004 | Evidence use | Evidence coverage, provenance, conflict handling, unsupported claims |
| EV-005 | Response quality | Deterministic reference checks where possible; semantic evaluator only where needed |
| EV-006 | Safety | Permission/policy/forbidden-action checks |
| EV-007 | Performance under failures | Robust task success by fault profile |
| EV-008 | Stability across executions | Repeated-run reliability / pass-style metrics / variance |
| EV-009 | High-impact action behavior | Mutation/action correctness + pre-execution gate + final state |

## Evaluation-framework deliverable forms explicitly supported by TAPI

The format remains open. We intend the integrated framework to provide equivalents of all of these where feasible:

- automated test suite;
- metrics library;
- scenario runner;
- trace inspection application;
- adversarial-case generation;
- robustness and consistency evaluation;
- execution capture, anonymization and reproduction/replay.

## Documentation requirements

Final README must cover:

- chosen problem;
- integrated dual-track scope;
- architecture;
- installation and execution;
- models and configurations;
- experimental methodology;
- results;
- limitations;
- evolution opportunities.

## Rubric-to-evidence map

| Rubric criterion | Evidence we must produce |
|---|---|
| API integration quality | Contract-aware typed client/tools, failure handling, live traces |
| Technical coherence | Unified agent+evaluation architecture, ADRs, ablation results |
| Hypothesis and experiment clarity | Pre-registered hypotheses, baselines, splits, protocol |
| Result analysis quality | Quantitative metrics, CIs, failure slices, qualitative trace examples |
| Limitations and risks | Threat model, failure taxonomy, explicit validity limitations |
| Reproducibility | Versioned configs/datasets, reset/replay, deterministic evaluators, environment setup |
| Documentation | README + research + ADRs + experiment reports |
| Demo quality | Live agent run + evaluation trace + state verification + repeated-run/fault comparison dashboard |

## Scope interpretation after the update

`RESOLVED_BY_UPDATED_TAPI`:

- We no longer need to ask whether one track must be designated primary.
- We no longer frame the evaluation framework as an optional subsystem of the construction track.
- The project must integrate both components coherently.

The wording `Nesta trilha` in the evaluation-deliverable section is treated as a section label/legacy wording, because the updated objective explicitly states that the solution must contain both components. If partner guidance contradicts this interpretation, record that guidance as a superseding project requirement.

## API-dependent requirements still unknown

The TAPI explicitly states that the final endpoint/parameter list will be provided in the API contract. Therefore we must not invent:

- exact endpoint catalog;
- exact resource schemas;
- permission representation;
- exact high-impact action classification;
- reset/snapshot semantics;
- stable identifiers;
- rate limits;
- timestamps/freshness semantics;
- conflict/partial-result metadata;
- authentication details.

These are tracked in `05-tractian-open-questions.md`.
