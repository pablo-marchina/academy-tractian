# TAPI Requirement Matrix

Source: **[UPDATED] TAPI — Engenharia e Avaliação de Agentes Industriais**, Inteli × TRACTIAN, received 2026-08-13.

Status legend: `CONFIRMED` = explicitly supported by TAPI; `PARTNER_GUIDANCE` = clearly stated in kickoff and should be validated against delivered artifacts/API; `DEPENDENCY` = requires TRACTIAN/API clarification; `PROJECT_CHOICE` = our optional extension.

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

## Kickoff-derived partner guidance — 2026-08-13

These items are strong partner statements from a noisy automatic transcript. They are treated as engineering/evaluation requirements unless the delivered API/dataset clarifies otherwise. Full evidence notes: `25-kickoff-evidence-2026-08-13.md`.

| ID | Partner guidance | Type | Planned verification/evidence |
|---|---|---|---|
| KO-001 | Optimize for automating the existing customer-support investigation/resolution workflow, with safe human fallback when needed | PARTNER_GUIDANCE | End-to-end ticket scenarios + fallback cases |
| KO-002 | Partner cases include customer-question-derived inputs, engineer investigation trajectory/reference accesses, and expected final output/conclusion | PARTNER_GUIDANCE | Dataset ingestion + provenance fields |
| KO-003 | Evaluate intermediate process/tool use as well as final answer | PARTNER_GUIDANCE | Tool/argument/trajectory/evidence evaluators |
| KO-004 | Final-answer correctness should prioritize the operational conclusion/decision rather than exact wording | PARTNER_GUIDANCE | Conclusion/fact oracle; no exact-string primary metric |
| KO-005 | Customer-facing answers should not expose unnecessary internal system/implementation details | PARTNER_GUIDANCE | Communication policy evaluator / forbidden-disclosure checks |
| KO-006 | Insufficient or meaningfully ambiguous evidence is a valid reason to escalate to human analysis | PARTNER_GUIDANCE | Escalation target scenarios + confusion matrix |
| KO-007 | Escalation handoff should contain collected evidence, attempted analysis, unresolved contradiction/question and reason for escalation | PARTNER_GUIDANCE | Escalation-package completeness evaluator |
| KO-008 | State-changing platform actions should require explicit requester confirmation/approval | PARTNER_GUIDANCE | Deterministic confirmation gate + negative tests; exact action classes from API |
| KO-009 | Keep one stable agent-facing integration contract across underlying sources where practical; avoid unnecessary integration heterogeneity | PARTNER_GUIDANCE | Canonical ToolSpec + native/MCP adapter experiment |
| KO-010 | Adding the agent to an existing process must fail safely rather than break the original workflow | PARTNER_GUIDANCE | Fault injection + fallback/escalation assertions |
| KO-011 | Prevent development/evaluation leakage; do not use the same cases as both optimization and final validation | PARTNER_GUIDANCE | Grouped dev/validation/locked-test split |
| KO-012 | Student must be able to explain architectural choices, alternatives and trade-offs | PARTNER_GUIDANCE | ADRs + ablations + presentation evidence |

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
| EV-005 | Response quality | Deterministic conclusion/fact checks where possible; semantic evaluator only where needed |
| EV-006 | Safety | Permission/policy/confirmation/forbidden-action checks |
| EV-007 | Performance under failures | Robust task success + safe fallback by fault profile |
| EV-008 | Stability across executions | Repeated-run reliability / pass-style metrics / variance |
| EV-009 | High-impact action behavior | Mutation/action correctness + approval/pre-execution gate + final state |
| EV-010 | Escalation quality | Correct escalation decision + handoff evidence/unresolved-point completeness |
| EV-011 | Customer-safe communication | Correct conclusion with unnecessary internal-detail leakage controlled |

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

## API/dataset-dependent requirements still unknown

The TAPI explicitly states that the final endpoint/parameter list will be provided in the API contract, and the kickoff transcript is not precise enough to resolve these. Therefore we must not invent:

- exact endpoint catalog;
- exact resource schemas;
- permission representation;
- exact high-impact/mutation/confirmation classification;
- reset/snapshot semantics;
- stable identifiers;
- rate limits;
- timestamps/freshness semantics;
- conflict/partial-result metadata;
- authentication details;
- exact case count and official split packaging;
- hidden-evaluation policy;
- exact model/provider constraints for students.

These are tracked in `05-tractian-open-questions.md`.
