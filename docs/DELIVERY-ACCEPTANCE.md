# Academy × TRACTIAN — Delivery Acceptance Matrix

**Status:** ACTIVE / canonical final-delivery coverage map  
**Requirements source:** [`../research/01-requirements-matrix.md`](../research/01-requirements-matrix.md)  
**Audited source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Next steps:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

## 1. Purpose

This document answers: **what must be demonstrably true for the final project to satisfy the requested TRACTIAN × Inteli scope at the strongest evidence-backed level?**

It prevents three failure modes:

1. optimizing the research protocol while leaving a requested product capability unproven;
2. building a strong agent without a trustworthy integrated evaluation framework; and
3. adding architecture complexity that does not improve a required capability, material risk or measured production objective.

The authoritative requirement semantics remain in `research/01-requirements-matrix.md`. This file is the active final-delivery crosswalk.

## 2. Delivery priority rule

Use three priority tiers:

- **P0 — MUST:** directly required by the TAPI/package or necessary to support the final academic/product claim. P0 coverage takes priority over optional enhancements.
- **P1 — MATERIAL PRODUCTION/QUALITY:** necessary to make the P0 system safe, reliable, understandable, reproducible, observable and realistically operable at the quality bar expressed by the partner.
- **P2 — CONDITIONAL ENHANCEMENT:** RAG, vector DB, reranking, persistent memory, multi-agent decomposition, richer protocol adapters, adaptive routing/model selection, richer UI or similar complexity. Implement only when a simpler baseline is insufficient or controlled evidence shows material benefit.

A workstream that maps to no acceptance requirement, no recognized material risk and no experiment needed to select among credible alternatives should be deferred.

## 3. Official academic excellence dimensions

The final delivery must be optimized explicitly across the eight TAPI evaluation dimensions, not only for aggregate agent score.

| Official criterion | Minimum acceptable evidence | Excellence target for this project |
|---|---|---|
| API integration quality | API calls work | typed/validated contract, conformance tests, permissions/errors/failure handling, real traces, stable agent-facing interface |
| Technical coherence | architecture can be explained | requirement-driven boundaries, evidence-backed ADRs, minimal unjustified complexity, clear runtime/evaluator separation |
| Hypothesis/experiment clarity | hypothesis is stated | preregistered comparison, simple baseline, controlled variables, explicit success/failure criteria |
| Result analysis quality | aggregate results | uncertainty, paired/group-aware analysis, robustness/failure slices, diagnosis and trade-off interpretation |
| Limitations/risks | limitations section | leakage/security boundaries, failure taxonomy, validity limits, production risks and reversal triggers |
| Reproducibility | setup instructions | pinned source/config/artifact identity, deterministic seeds where applicable, replay and clean-environment reproduction |
| Documentation | README exists | navigable source-of-truth docs, architecture/ADRs/results/runbook/evidence traceability |
| Demonstration quality | one happy path | real integrated agent + evaluator, multiple requested behaviors, failure path and reliability view |

A technically impressive component that weakens another official criterion is not automatically an improvement.

## 4. P0 — project-level mandatory acceptance

| Requirement | Final acceptance condition | Required evidence |
|---|---|---|
| REQ-001 — Individual project | final repository/delivery is attributable and self-contained as the individual project | repository authorship + final handoff |
| REQ-003 — Technical experiment | at least one technically coherent, reproducible experiment supports a material decision/claim | frozen protocol/manifest, baseline/comparison, quantitative results, uncertainty/analysis, reproducibility artifacts |
| REQ-004 / REQ-020 — Document results | methodology, architecture, decisions, results, limitations and evolution are understandable from the delivered repository | final README + experiment reports + ADRs + final evaluation/limitations documentation |
| REQ-021 — Reproducible handoff | another person can execute the solution end to end from the documentation | clean setup/build/run exercise + recorded versions/configuration |
| REQ-017 — Agent + evaluation framework | final delivery contains both an operational agent path and an integrated evaluation framework | integrated runtime/evaluator demonstration + source/eval suite |

These are not packaging details. Strong experiments without a usable agent, or a strong agent without a trustworthy evaluator, do not satisfy the complete assignment.

## 5. P0 — agent construction acceptance

| Requirement coverage | Final capability | Required evidence before acceptance | Current interpretation |
|---|---|---|---|
| REQ-002, REQ-009 | Integrate with the supplied industrial API and consult assets/analyses/technical data | real contract/conformance test, typed tool contract, successful production-path trace | delivered OpenAPI/API behavior is the executable target |
| REQ-005 | Contextualize a customer request | representative end-to-end contextualization scenario with correct grounded response | conclusion/facts matter more than exact phrasing |
| REQ-006, AG-003, AG-005 | Investigate using appropriate tools and evidence-aware stopping/planning | tool-selection/evidence metrics + end-to-end scenario traces | process quality must be inspectable, not inferred only from final text |
| REQ-007, REQ-011, REQ-014, REQ-015, EV-009 | Execute justified platform actions safely | correct tool/target/arguments/justification, permission behavior, accepted execution event, no duplicate/unnecessary action | benchmark semantics use accepted action event as execution |
| REQ-008, REQ-010 | Request additional information / ask pertinent questions when evidence is insufficient | ambiguity/missing-information cases + justified clarification/abstention behavior | must be explicit in final regression suite |
| REQ-012, AG-012, EV-010 | Escalate correctly to human analysis | correct escalation decision plus useful handoff with collected evidence, unresolved uncertainty/contradiction and reason where reliably evaluable | partner-quality requirement, compatible with TAPI |
| REQ-013, AG-006 | Handle complete, partial, inconclusive, conflicting and unavailable results | deterministic robustness profiles covering all modes + safe fallback metrics | include pending/stale domain states separately where relevant |
| AG-004 | Construct valid and semantically correct arguments | schema validation + semantic argument evaluator + negative tests | required for both reads and actions |
| AG-007 | Ground responses in evidence | evidence correctness/recall and unsupported-claim checks | no unsupported certainty under degraded evidence |
| AG-009 | Decide orient/investigate/act/escalate/clarify/abstain appropriately | deterministic decision metrics and scenario coverage | decision is a first-class evaluation object |
| REQ-016, AG-010 | Keep calls/results inspectable | normalized structured trace containing decisions, tools, arguments, observations, actions and final outcome | trace must support diagnosis of where a failure occurred |
| AG-011 | Communicate customer-safe conclusions | conclusion remains useful without unnecessary internal implementation disclosure | human/validated semantic check where reliable |
| AG-013 | Fail safely if model/provider/tool path is unavailable | fault-injection evidence showing fallback/human handoff rather than broken support flow | P1 production requirement with direct partner emphasis |

## 6. P0 — evaluation framework acceptance

The final delivery is incomplete if it contains only an agent. The updated TAPI explicitly requires both **agent construction** and an **agent evaluation framework**.

| Requirement coverage | Evaluation capability | Required final evidence |
|---|---|---|
| REQ-017 | Integrated agent + evaluator | the same production-path run can be captured and evaluated without leaking evaluation-only truth into runtime |
| EV-001 | Function/tool choice | required/allowed/forbidden tool correctness metrics |
| EV-002 | Argument accuracy | schema + semantic argument correctness |
| EV-003 | Execution trajectory | policy/order/evidence/efficiency evaluation without brittle exact-sequence primary scoring |
| EV-004 | Evidence use | required evidence, provenance, uncertainty/conflict handling |
| EV-005 | Response quality | structured operational conclusion/fact quality; no exact-string primary score |
| EV-006 | Safety | identity/seed isolation, permissions/policy/resource boundaries, forbidden action checks |
| EV-007 | Failure performance | robust task success/safe fallback under deterministic data/tool/provider perturbations |
| EV-008 | Stability | repeated-run reliability under controlled environment/seed policy |
| EV-009 | High-impact actions | decision/tool/target/arguments/justification/accepted/no-duplicate checks |
| EV-010 | Escalation | correct escalation + handoff completeness where gold/annotation supports it |
| EV-011 | Customer-safe communication | conclusion correctness separated from tone/internal-disclosure policy |
| EV-012 | Evaluation integrity | gold isolation, scorer provenance, judge validity/calibration and no tuning leakage |

The evaluator deliverable should expose, where useful: scenario execution, metrics/evaluator library, trace inspection, controlled/adversarial variants, robustness/reliability analysis, capture/replay and reproducible experiment configuration.

The supplied package does not contain every evaluation utility described narratively; the final evaluation framework is part of the student's actual implementation responsibility.

## 7. P0 — benchmark/security integrity acceptance

| Constraint | Final acceptance condition |
|---|---|
| REQ-018, REQ-019 | evaluation-only gold/reference material never enters agent runtime context; canonical cases remain evaluation provenance, not prompt material |
| PC-001 | requester/user identity remains outside model control |
| PC-002 | evaluation seed remains outside model control |
| PC-003 | raw partner artifact provenance is preserved; normalization is derived/versioned rather than silently rewriting source truth |
| PC-004 | API permission enforcement and project/system policy enforcement remain separate and testable |
| PC-005 | accepted action-event semantics are used instead of false final-state equality assumptions |
| PC-006 | coupled scenario/ticket evidence is grouped to prevent split leakage |

Any violation blocks the corresponding scientific or production-readiness claim.

## 8. P1 — partner-informed production/quality acceptance

Production-first means the selected behavior must be operable beyond a benchmark script, while partner guidance defines additional quality targets compatible with the written assignment.

| Area | Required evidence / policy |
|---|---|
| Contracts | typed/validated API and tool interfaces; one stable agent-facing contract; backend protocol diversity hidden behind adapters when useful |
| Authorization | deterministic authorization boundaries, audit trail and negative tests |
| Consequential actions | idempotency/duplicate-action protection; explicit decision on requester-confirmation policy for interactive production; benchmark semantics must remain unchanged |
| Failure continuity | model/provider/tool failure must lead to safe fallback/handoff rather than breaking the underlying support workflow |
| Escalation handoff | human receives enough evidence, unresolved contradiction/uncertainty and reason to continue efficiently |
| Customer communication | final answer emphasizes the operationally useful conclusion and avoids unnecessary disclosure of internal implementation details |
| State/context | explicit request/state lifecycle; persistent memory only if cases/evidence justify it |
| Configuration | versioned non-secret config and pinned dependencies/build inputs |
| Secrets/privacy | no credentials/private oracle/blind outcomes in runtime artifacts or logs |
| Observability | structured traces/logs/metrics sufficient to inspect decisions, tools, failures and evaluator results |
| Model/provider quality | compare a strong quality frontier with feasible lower-cost/local baselines; do not prematurely cap capability before proving value |
| Performance | measured latency, reliability and resource/cost behavior appropriate to the final interaction mode |
| Reproducibility | clean setup/build/run path from documented inputs |
| Rollback | known fallback/reversal path for the selected release |

## 9. Final demonstration acceptance

The final demonstration must exercise the **real integrated path**, not a scripted mock-only path.

Minimum portfolio:

1. **Contextualize:** handle a request with relevant grounded context.
2. **Investigate:** choose/use real read tools, interpret evidence and reach an appropriate decision.
3. **Execute:** perform a justified state-changing request under authorization controls with correct accepted-action semantics.
4. **Clarify / insufficient evidence:** request additional information or abstain safely when appropriate.
5. **Escalate:** hand off a case with useful evidence/reason when required.
6. **Conflict/uncertainty:** resolve or safely escalate a conflicting/inconclusive condition rather than invent certainty.
7. **Failure/robustness:** handle at least one partial/unavailable tool/data or model/provider failure safely.
8. **Customer-safe response:** show an operationally useful conclusion without unnecessary internal-system disclosure.
9. **Per-run evaluation:** evaluate the resulting trace with the integrated framework without exposing gold to the agent.
10. **Reliability view:** show aggregate/repeated-run or robustness evidence rather than relying on one happy path.

The demo should make it possible to explain **why** the agent took the path it took and **where** an error occurred if the run failed.

## 10. Final documentation/package acceptance

Final handoff should include:

- problem and declared scope;
- final integrated agent/evaluator architecture and ADRs;
- setup/configuration and dependency versions;
- model/provider/runtime choices and evidence for their selection;
- evaluation methodology and benchmark-integrity boundaries;
- technical experiment(s), baselines/ablations and quantitative results with uncertainty;
- robustness/failure analysis;
- limitations, non-claims and known risks;
- source code and evaluation suite;
- deployment/runbook/monitoring/fallback/rollback instructions appropriate to the implemented production path;
- reproducibility/provenance package;
- real integrated demonstration instructions;
- concise rubric-to-evidence index so reviewers can find the strongest evidence quickly.

## 11. Architecture complexity gate

No optional architecture component is a delivery requirement by itself.

```text
RAG / vector DB / reranker / multi-agent / persistent memory / MCP /
adaptive routing / richer UI / extra backend simulations
        ↓
Which P0/P1 requirement, rubric dimension or measured bottleneck does it improve?
        ↓
What is the simple baseline?
        ↓
Does controlled quantitative evidence show material benefit after production costs/risks?
        ├── NO  → do not add / remove
        └── YES → ADR → regression → eligible for PREFERRED/FROZEN
```

For model/provider choice specifically, the baseline set must not be artificially limited to the cheapest option: include a strong quality frontier, then select the best production Pareto point using measured quality, latency, reliability, cost/resource and portability.

## 12. Final acceptance rule

The project may be called complete only when:

```text
requested P0 capabilities are demonstrably covered
+
evaluation framework is integrated and trustworthy
+
applicable P1 production/partner-quality risks are closed or explicitly bounded
+
all material choices satisfy PROJECT-PRINCIPLES
+
official rubric dimensions have findable high-quality evidence
+
final claims do not exceed independent/frozen evidence
```

Any uncovered P0 row is a delivery blocker unless the final scope is explicitly reduced with an evidence-honest limitation.