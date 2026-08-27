# TAPI Requirement Matrix

Source hierarchy:

1. **[UPDATED] TAPI — Engenharia e Avaliação de Agentes Industriais**, Inteli × TRACTIAN, received 2026-08-13;
2. written partner package received 2026-08-15;
3. executable supplied API behavior;
4. confidence-labeled kickoff guidance where not contradicted by written artifacts.

Status legend: `CONFIRMED` = explicitly supported by TAPI/written package; `PARTNER_GUIDANCE` = kickoff guidance not yet promoted to universal canonical policy; `PROJECT_CONSTRAINT` = required to preserve benchmark/security integrity; `PROJECT_CHOICE` = experimentable extension.

## Mandatory integrated scope

The updated TAPI requires a solution containing both:

1. **Construção de agente**; and
2. **Framework de avaliação de agentes**.

The delivered package further provides an explicit separation between **agent-visible case/API material** and **evaluation-only gold/reference material**. The architecture must preserve this boundary.

## Core project requirements

| ID | Requirement | Source | Type | Verification evidence planned |
|---|---|---|---|---|
| REQ-001 | Individual project | TAPI | CONFIRMED | Repository authorship / final delivery |
| REQ-002 | Integrate with the TRACTIAN-provided industrial API | TAPI | CONFIRMED | Live integration test + trace |
| REQ-003 | Include a technical experiment | TAPI | CONFIRMED | Reproducible experiment report + artifacts |
| REQ-004 | Document results | TAPI | CONFIRMED | README + research/experiment reports |
| REQ-005 | Handle contextualization requests | TAPI + cases | CONFIRMED | Context scenario suite |
| REQ-006 | Handle investigation requests using tools | TAPI + cases | CONFIRMED | Scenario + tool/evidence evaluation |
| REQ-007 | Handle execution requests affecting the customer solution | TAPI + cases | CONFIRMED | Action scenarios + accepted-execution oracle |
| REQ-008 | Be able to request additional information | TAPI | CONFIRMED | Ambiguity/missing-info cases |
| REQ-009 | Consult assets, analyses and technical data | TAPI + API | CONFIRMED | Tool/API tests |
| REQ-010 | Ask pertinent investigative questions | TAPI | CONFIRMED | Multi-turn scenarios where justified |
| REQ-011 | Execute justified platform actions | TAPI + API | CONFIRMED | Action-policy + argument evaluator |
| REQ-012 | Escalate cases to human analysis | TAPI + API/cases | CONFIRMED | Escalation scenarios |
| REQ-013 | Handle complete, partial, inconclusive, conflicting and unavailable query results | TAPI + API | CONFIRMED | Seeded/fixed robustness profiles |
| REQ-014 | High-impact actions require valid parameters and adequate justification | TAPI | CONFIRMED | Strict project validation + action experiment |
| REQ-015 | Accepted action call represents execution; no later status cycle is required | TAPI + API | CONFIRMED | `accepted=true` action oracle |
| REQ-016 | Calls and results must be inspectable | TAPI | CONFIRMED | End-to-end normalized trace |
| REQ-017 | Deliver both agent construction and evaluation framework | Updated TAPI | CONFIRMED | Integrated runtime + evaluation subsystem |
| REQ-018 | Gold/evaluation-only reference material must not enter agent runtime context | Student Guide/package boundary | CONFIRMED | Import/module/context isolation tests |
| REQ-019 | Preserve canonical/reference cases as evaluation provenance rather than prompt material | Student Guide/package | CONFIRMED | Scenario manifest + gold access boundary |

## Benchmark/security integrity constraints derived from the actual API

These are not claims about TRACTIAN production systems. They are project constraints required to make the supplied simplified environment valid and secure for experimentation.

| ID | Constraint | Why it is required | Verification |
|---|---|---|---|
| PC-001 | Bind case `user_id` outside model control | Raw API uses `x-user-id`; model-controlled identity would enable impersonation | Tool schema excludes auth identity; negative test |
| PC-002 | Bind evaluation `seed` outside model control | Model-controlled seed could select favorable response modes and invalidate robustness evaluation | Tool schema excludes seed; runner injects it |
| PC-003 | Preserve raw partner package/contract immutably; normalize only into derived artifacts with hashes/change log | Raw OpenAPI contains a duplicate path key and must not be silently rewritten | Artifact manifest + normalization tests |
| PC-004 | Treat API permission enforcement and project/system policy enforcement separately | Simplified backend checks coarse permission but not resource/company ownership | Cross-company adversarial tests |
| PC-005 | Do not use final-state equality as the primary oracle for supplied actions that do not persist state | Action handlers simulate accepted execution events | Action-call/accepted-event evaluator |

## Kickoff-derived partner guidance reconciled with delivered artifacts

| ID | Guidance | Status after package | Treatment |
|---|---|---|---|
| KO-001 | Automate support investigation/resolution with safe human fallback | Supported | End-to-end scenario objective |
| KO-002 | Partner supplies case/question + reference investigation + expected conclusion | Partially supported | Case input + reference paths + narrative expected resolution exist; final conclusion is not structured machine JSON and must be normalized |
| KO-003 | Evaluate intermediate process/tool use and final answer | Supported | Separate trace/process/conclusion evaluators |
| KO-004 | Operational conclusion matters more than exact wording | Supported by scenario P1 framing | Structured conclusion/fact oracle; no exact-string primary score |
| KO-005 | Avoid unnecessary internal implementation disclosure to customers | Not contradicted; not formally encoded per case | Communication evaluator/extension where annotation can be made reliable |
| KO-006 | Insufficient/ambiguous evidence can justify escalation | Supported | Escalation scenarios + seeded uncertainty variants |
| KO-007 | Escalation should hand off useful evidence/analysis/reason | Not fully machine-encoded | Normalize narrative requirements / evaluate when reliable |
| KO-008 | State-changing operations should use requester confirmation | **Not encoded as universal canonical scenario policy** | Demoted to guarded safety experiment unless partner explicitly requires confirmation for a scenario |
| KO-009 | Stable agent-facing integration contract is desirable | Strongly compatible with package/API | Canonical ToolSpec + native/MCP experiment |
| KO-010 | Agent failure must not break existing workflow | Supported engineering guidance | Fault/fallback experiment |
| KO-011 | Prevent development/final-evaluation leakage | Strongly supported | Group-aware dev/validation/locked-test split |
| KO-012 | Student must explain choices/trade-offs | Supported | ADRs + ablations + presentation evidence |

## Agent-construction coverage

| ID | Capability | Planned evidence |
|---|---|---|
| AG-001 | Interpret HTTP contracts | Duplicate-aware OpenAPI normalization + conformance tests |
| AG-002 | Define tools and schemas | Canonical typed ToolSpec / strict validation |
| AG-003 | Select functions | Tool selection metrics |
| AG-004 | Construct arguments | Schema + semantic argument correctness |
| AG-005 | Planning/stopping policy | Baseline vs evidence-aware policy experiment |
| AG-006 | Handle incomplete returns and failures | Deterministic seeded robustness benchmark |
| AG-007 | Ground responses in evidence | Evidence coverage/unsupported-claim evaluator |
| AG-008 | Memory/context where needed | Multi-turn/state experiment only if actual cases require it |
| AG-009 | Decide orient/investigate/act/escalate | Decision metrics |
| AG-010 | Execution traceability | Project-owned TraceSchema + OTel adapter |

## Evaluation-framework coverage

| ID | Evaluation object | Canonical signal after artifact inspection |
|---|---|---|
| EV-001 | Function choice | Required/allowed/forbidden tool correctness; reference-path diagnostics |
| EV-002 | Argument accuracy | Strict schema validity + semantic argument correctness |
| EV-003 | Execution trajectory | Policy/order constraints + evidence coverage + efficiency; **not raw exact-sequence match** |
| EV-004 | Evidence use | Required evidence, provenance, response mode, conflict/uncertainty handling |
| EV-005 | Response quality | Human-reviewed structured conclusion/fact oracle derived from narrative P1/expected resolution |
| EV-006 | Safety | Bound identity/seed, permission/policy/resource constraints, forbidden actions |
| EV-007 | Performance under failures | Robust task success + safe fallback by deterministic response-mode perturbation |
| EV-008 | Stability across executions | Repeated-run reliability with fixed environment seed/observations |
| EV-009 | High-impact action behavior | Correct decision/tool/target/arguments/justification + `accepted=true` + no duplicate/unnecessary action |
| EV-010 | Escalation quality | Correct escalation decision and, where gold supports it, handoff completeness |
| EV-011 | Customer-safe communication | Conclusion correctness separated from disclosure/style policy |

## Evaluation deliverable forms

The integrated framework should provide, where useful:

- automated test suite;
- metrics/evaluator library;
- scenario runner;
- trace inspection application;
- adversarial/controlled variants;
- robustness and consistency evaluation;
- execution capture/replay;
- reproducible experiment manifests.

## Documentation requirements

Final README must cover problem/scope, architecture, setup, models/configurations, experimental methodology, results, limitations and future evolution.

## Rubric-to-evidence map

| Rubric criterion | Evidence |
|---|---|
| API integration quality | Normalized/conformance-tested contract, typed tools, live traces, failure handling |
| Technical coherence | Unified agent+evaluation architecture, ADRs, ablations |
| Hypothesis/experiment clarity | Pre-registered guarded-boundary + evidence/stopping experiments, baselines, splits |
| Result analysis quality | Metrics, CIs, failure slices, trace examples, environment-vs-agent variability decomposition |
| Limitations/risks | Package quality audit, threat model, failure taxonomy, validity limits |
| Reproducibility | Raw artifact hashes, normalized manifests, config hashes, deterministic seed catalog, replay |
| Documentation | README + research + ADRs + experiment reports |
| Demonstration | Live agent + per-run evaluator + seeded robustness/reliability comparisons |

## Remaining partner/instructor dependencies

The delivered package resolves most former API/dataset unknowns. Remaining non-inferable questions include:

- whether additional/hidden evaluation cases will be used;
- model/provider restrictions or credits for students beyond the written feasibility guidance;
- whether raw partner package/gold material may be published in the public repository;
- exact final-demo environment/constraints;
- whether confirmation should be promoted from kickoff safety guidance to a canonical action policy in any official case.

All architecture choices beyond the integrity constraints above remain subject to project-specific experiment and ADR.