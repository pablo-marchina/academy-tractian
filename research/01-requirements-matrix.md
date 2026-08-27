# TAPI Requirement Matrix

**Canonical source audit:** [`tractian-source-baseline-2026-08-27.md`](tractian-source-baseline-2026-08-27.md)

Source hierarchy:

1. **[UPDATED] TAPI — Engenharia e Avaliação de Agentes Industriais**, Inteli × TRACTIAN;
2. delivered written partner package (`STUDENT-GUIDE.md`, agent/eval material, contract/docs/data);
3. executable supplied API behavior/tests;
4. confidence-labeled kickoff guidance where not contradicted by written artifacts;
5. project-generated hypotheses/extensions.

Status legend: `CONFIRMED` = explicitly supported by TAPI/written package; `PARTNER_GUIDANCE` = kickoff guidance compatible with the package but not necessarily encoded as a universal benchmark rule; `PROJECT_CONSTRAINT` = required to preserve benchmark/security integrity; `PROJECT_CHOICE` = experimentable extension.

## Mandatory integrated scope

The updated TAPI requires one individual project containing both:

1. **Construção de agente**; and
2. **Framework de avaliação de agentes**.

The delivered package further requires a hard separation between **agent-visible case/API material** and **evaluation-only gold/reference material**. The architecture must preserve this boundary throughout research, production implementation and demonstration.

## Delivered-package baseline facts

The reviewed package contains:

- 17 agent-visible case rows in `agent-input/cases.json`;
- 17 evaluation rows in `eval/expected-paths.json`;
- 16 narrative scenarios in `docs/test-scenarios.md` / `eval/test-scenarios.md`;
- 17 concrete operations in the delivered agent-facing OpenAPI;
- deterministic seed control plus degraded query behavior;
- authenticated/permission-checked impact actions with justification validation;
- accepted action semantics (`accepted=true`) without a required asynchronous status cycle.

Known source-quality discrepancies are recorded rather than silently corrected in `tractian-source-baseline-2026-08-27.md`. In particular, the package README's endpoint count and the Student Guide's reference to missing eval helper files must not be treated as executable facts when the delivered contract/files differ.

## Core project requirements

| ID | Requirement | Source | Type | Verification evidence planned |
|---|---|---|---|---|
| REQ-001 | Individual project | TAPI | CONFIRMED | Repository authorship / final delivery |
| REQ-002 | Integrate with the TRACTIAN-provided industrial API | TAPI + package | CONFIRMED | Live integration test + trace against delivered contract |
| REQ-003 | Include a technical experiment | TAPI | CONFIRMED | Reproducible experiment report + frozen artifacts |
| REQ-004 | Document results | TAPI | CONFIRMED | Final README + experiment/decision evidence |
| REQ-005 | Handle contextualization requests | TAPI + cases | CONFIRMED | Context scenario suite |
| REQ-006 | Handle investigation requests using tools | TAPI + cases | CONFIRMED | Scenario + tool/evidence evaluation |
| REQ-007 | Handle execution requests affecting the customer solution | TAPI + cases | CONFIRMED | Action scenarios + accepted-execution oracle |
| REQ-008 | Be able to request additional information | TAPI | CONFIRMED | Ambiguity/missing-info cases |
| REQ-009 | Consult assets, analyses and technical data | TAPI + API | CONFIRMED | Tool/API tests |
| REQ-010 | Ask pertinent investigative questions | TAPI | CONFIRMED | Multi-turn scenarios where justified |
| REQ-011 | Execute justified platform actions | TAPI + API | CONFIRMED | Action-policy + argument evaluator |
| REQ-012 | Escalate cases to human analysis | TAPI + API/cases | CONFIRMED | Escalation scenarios + handoff quality where reliably evaluable |
| REQ-013 | Handle complete, partial, inconclusive, conflicting and unavailable query results | TAPI + API | CONFIRMED | Seeded/fixed robustness profiles |
| REQ-014 | High-impact actions require valid parameters and adequate justification | TAPI | CONFIRMED | Strict validation + action experiment |
| REQ-015 | Accepted action call represents execution; no later status cycle is required | TAPI + API | CONFIRMED | `accepted=true` action oracle |
| REQ-016 | Calls and results must be inspectable | TAPI | CONFIRMED | End-to-end normalized trace |
| REQ-017 | Deliver both agent construction and evaluation framework | Updated TAPI + Student Guide | CONFIRMED | Integrated runtime + evaluation subsystem |
| REQ-018 | Gold/evaluation-only reference material must not enter agent runtime context | Student Guide/package boundary | CONFIRMED | Import/module/context isolation tests |
| REQ-019 | Preserve canonical/reference cases as evaluation provenance rather than prompt material | Student Guide/package | CONFIRMED | Scenario manifest + gold access boundary |
| REQ-020 | Final README must cover problem/scope, architecture, setup, models/configurations, experimental methodology, results, limitations and evolution | TAPI + Student Guide | CONFIRMED | Final documentation acceptance review |
| REQ-021 | Final work must be executable end to end by another person | Student Guide | CONFIRMED | Clean setup/run/reproduction exercise |

## Benchmark/security integrity constraints derived from the actual API

These are not claims about TRACTIAN production systems. They are project constraints required to make the supplied simplified environment valid and secure for experimentation.

| ID | Constraint | Why it is required | Verification |
|---|---|---|---|
| PC-001 | Bind case `user_id` outside model control | Raw API uses `x-user-id`; model-controlled identity would enable impersonation | Tool schema excludes auth identity; negative test |
| PC-002 | Bind evaluation `seed` outside model control | Model-controlled seed could select favorable response modes and invalidate robustness evaluation | Tool schema excludes seed; runner injects it |
| PC-003 | Preserve raw partner package/contract immutably; normalize only into derived artifacts with hashes/change log | Delivered source contains documentation/contract inconsistencies that must not be silently rewritten | Artifact manifest + normalization tests |
| PC-004 | Treat API permission enforcement and project/system policy enforcement separately | Simplified backend checks permission level but is not a complete real-world authorization system | Cross-company/policy adversarial tests |
| PC-005 | Do not use final-state equality as the primary oracle for supplied actions that do not persist state | Action handlers model accepted execution events | Action-call/accepted-event evaluator |
| PC-006 | Group coupled ticket/scenario evidence when splitting/evaluating | 17 case/gold rows map to 16 narrative scenarios; some investigation/action evidence is coupled | Group-aware split and leakage audit |

## Kickoff-derived partner guidance reconciled with delivered artifacts

| ID | Guidance | Status after package | Treatment |
|---|---|---|---|
| KO-001 | Automate support investigation/resolution with safe human fallback | Supported | End-to-end scenario objective |
| KO-002 | Partner supplies question/case + reference investigation + expected conclusion | Partially supported | Agent cases + expected paths + narrative resolutions; normalize conclusion truth carefully |
| KO-003 | Evaluate intermediate process/tool use and final answer | Strongly supported | Separate trace/process/conclusion evaluators |
| KO-004 | Operational conclusion matters more than exact wording | Strongly supported | Structured conclusion/fact oracle; no exact-string primary score |
| KO-005 | Avoid unnecessary internal implementation disclosure to customers | Explicit partner quality guidance; not machine-encoded per case | Customer-safe communication evaluator/human or validated semantic assessment |
| KO-006 | Insufficient or materially ambiguous evidence should prefer human review over unjustified certainty | Strongly supported and compatible with scenarios | Escalation/abstention policy + uncertainty benchmark |
| KO-007 | Escalation should hand off collected evidence, unresolved contradiction/uncertainty and reason | Strong partner guidance; partially encoded | Handoff completeness evaluator where reliable |
| KO-008 | Consequential state-changing operations should use requester confirmation in real interactive product flows | Not encoded as universal benchmark turn; TAPI says accepted action call is execution | Treat as production-policy experiment; do not alter official benchmark semantics silently |
| KO-009 | Stable agent-facing integration contract is desirable across heterogeneous backends | Strongly compatible with package/API | Canonical ToolSpec + adapter/protocol comparison; no requirement to simulate every backend type |
| KO-010 | Agent/LLM failure must not break the pre-existing support workflow | Strong production guidance | Safe fallback/handoff failure experiment; production acceptance blocker if applicable |
| KO-011 | Prevent development/final-evaluation leakage | Strongly supported | Group-aware DEV/VALIDATION/LOCKED_TEST boundaries |
| KO-012 | Student must explain choices/trade-offs and understand AI-assisted implementation | Strongly supported | ADRs + ablations + presentation defense evidence |
| KO-013 | Prove product value/quality with a strong modern model frontier before prematurely optimizing cost/latency | Strong partner guidance; TAPI tech list is suggestive, not mandatory | Model comparison must include a quality frontier and feasible lower-cost/local baselines; production choice uses Pareto evidence |
| KO-014 | Roll out risky/new agent behavior conservatively and with awareness of customer context | Supported production guidance | Controlled rollout/runbook consideration; not required for benchmark scoring |

## Agent-construction coverage

| ID | Capability | Planned evidence |
|---|---|---|
| AG-001 | Interpret HTTP contracts | Duplicate/inconsistency-aware OpenAPI normalization + conformance tests |
| AG-002 | Define tools and schemas | Canonical typed ToolSpec / strict validation |
| AG-003 | Select functions | Tool selection metrics |
| AG-004 | Construct arguments | Schema + semantic argument correctness |
| AG-005 | Planning/stopping policy | Baseline vs evidence-aware policy experiment |
| AG-006 | Handle incomplete returns and failures | Deterministic seeded robustness benchmark |
| AG-007 | Ground responses in evidence | Evidence coverage/unsupported-claim evaluator |
| AG-008 | Memory/context where needed | Multi-turn/state experiment only if actual cases require it |
| AG-009 | Decide orient/investigate/act/escalate/clarify/abstain | Decision metrics |
| AG-010 | Execution traceability | Project-owned TraceSchema + production-compatible tracing adapter |
| AG-011 | Preserve customer-safe communication boundary | Conclusion correctness + unnecessary-internal-disclosure checks where reliable |
| AG-012 | Produce useful escalation handoff | Evidence/uncertainty/reason completeness evaluation where gold supports it |
| AG-013 | Fail safely when model/provider/tool path is unavailable | Fault injection + human/fallback continuity test |

## Evaluation-framework coverage

| ID | Evaluation object | Canonical signal after artifact inspection |
|---|---|---|
| EV-001 | Function choice | Required/allowed/forbidden tool correctness; reference-path diagnostics |
| EV-002 | Argument accuracy | Strict schema validity + semantic argument correctness |
| EV-003 | Execution trajectory | Policy/order constraints + evidence coverage + efficiency; **not raw exact-sequence match** |
| EV-004 | Evidence use | Required evidence, provenance, response mode, conflict/uncertainty handling |
| EV-005 | Response quality | Human-reviewed/validated structured conclusion/fact oracle derived from narrative resolution; no exact-string primary score |
| EV-006 | Safety | Bound identity/seed, permission/policy/resource constraints, forbidden actions |
| EV-007 | Performance under failures | Robust task success + safe fallback by deterministic response-mode/tool/provider perturbation |
| EV-008 | Stability across executions | Repeated-run reliability with controlled environment seed/observations |
| EV-009 | High-impact action behavior | Correct decision/tool/target/arguments/justification + `accepted=true` + no duplicate/unnecessary action |
| EV-010 | Escalation quality | Correct escalation + useful handoff completeness where reliable |
| EV-011 | Customer-safe communication | Correct conclusion separated from tone/internal-disclosure policy |
| EV-012 | Evaluation-system integrity | Gold isolation, scorer provenance, evaluator calibration/agreement and no tuning leakage |

## Evaluation deliverable forms

The integrated framework should provide, where useful:

- automated test suite;
- metrics/evaluator library;
- scenario runner;
- trace inspection application;
- adversarial/controlled variants;
- robustness and consistency evaluation;
- execution capture/replay;
- reproducible experiment manifests;
- requirement/rubric coverage reporting.

The supplied ZIP does **not** contain every evaluation utility described narratively in the Student Guide. Missing framework pieces are therefore part of the student's implementation responsibility rather than something to assume exists upstream.

## Documentation requirements

Final README must cover:

- problem and declared scope;
- integrated agent/evaluator architecture;
- installation and execution;
- models/providers/configurations and versions;
- experimental hypothesis/methodology;
- quantitative results and uncertainty;
- limitations/risks/non-claims;
- reproducibility;
- possibilities for evolution.

Another person must be able to run the final solution end to end from the delivered documentation.

## Rubric-to-evidence map — excellence target

| Rubric criterion | Minimum evidence | Excellence bar for this project |
|---|---|---|
| API integration quality | Functional API connection | Typed contract, conformance tests, real traces, permissions/errors/failure handling, stable agent-facing interface |
| Technical coherence | Working architecture | Requirement-driven architecture, clear boundaries, evidence-backed ADRs, no unjustified complexity |
| Hypothesis/experiment clarity | Stated hypothesis | Preregistered comparison, simple baseline, controlled variables, explicit success/failure criteria |
| Result analysis quality | Aggregate scores | Uncertainty/CIs, paired/group-aware analysis, robustness/slices, failure diagnosis and trade-off interpretation |
| Limitations/risks | Limitations list | Threat model, leakage boundaries, failure taxonomy, validity limits, production reversal triggers |
| Reproducibility | Run instructions | Source/config/artifact hashes, deterministic seeds where applicable, capture/replay, clean-environment reproduction |
| Documentation | README | Navigable source-of-truth docs, architecture/ADRs, results, runbook and evidence traceability |
| Demonstration | Happy-path demo | Real integrated agent + per-run evaluator + contextualize/investigate/execute/clarify/escalate/failure coverage + reliability view |

## Remaining partner/instructor dependencies

The delivered package resolves most former API/dataset unknowns. Remaining non-inferable questions include:

- whether additional/hidden evaluation cases will be used;
- model/provider restrictions or credits beyond the written feasibility guidance;
- whether raw partner package/gold material may be published in the public repository;
- exact final-demo environment/constraints;
- whether requester confirmation should be promoted from partner production guidance to a canonical policy for any official hidden scenario.

All architecture choices beyond the integrity constraints above remain subject to project-specific experiment and ADR. Technology suggestions in the TAPI/package define a feasible candidate space, not predetermined winners.