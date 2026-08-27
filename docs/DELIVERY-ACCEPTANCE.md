# Academy × TRACTIAN — Delivery Acceptance Matrix

**Status:** ACTIVE / canonical final-delivery coverage map  
**Requirements source:** [`../research/01-requirements-matrix.md`](../research/01-requirements-matrix.md)  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Next steps:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

## 1. Purpose

This document answers: **what must be demonstrably true for the final project to satisfy the requested scope at the strongest evidence-backed level?**

It prevents two failure modes:

1. optimizing the research protocol while leaving a requested product capability unproven; and
2. adding fashionable architecture complexity that does not improve a required capability, risk, or measured production objective.

The authoritative requirement semantics remain in `research/01-requirements-matrix.md`. This file is the active delivery crosswalk from those requirements to final evidence.

## 2. Delivery priority rule

Use three priority tiers:

- **P0 — MUST:** directly required by the TAPI/package or necessary to support the final claim. P0 coverage takes priority over optional architecture enhancements.
- **P1 — MATERIAL PRODUCTION:** necessary to make the P0 system safe, reliable, reproducible, observable and realistically operable.
- **P2 — CONDITIONAL ENHANCEMENT:** RAG, vector DB, reranking, persistent memory, multi-agent decomposition, richer protocol adapters, adaptive routing/model selection or similar complexity. Implement only when a simpler baseline is insufficient or controlled evidence shows material benefit.

A workstream that maps to no acceptance requirement, no recognized material risk and no experiment needed to select among credible alternatives should be deferred.

## 3. P0 — project-level mandatory acceptance

| Requirement | Final acceptance condition | Required evidence |
|---|---|---|
| REQ-001 — Individual project | final repository/delivery is attributable and self-contained as the individual project | repository authorship + final handoff |
| REQ-003 — Technical experiment | at least one technically coherent, reproducible experiment supports a material decision/claim | frozen protocol/manifest, baseline or comparison, quantitative results, uncertainty/analysis, reproducibility artifacts |
| REQ-004 — Document results | results, methodology, decisions, limitations and evidence are understandable from the delivered repository | final README + experiment reports + ADRs + final evaluation/limitations documentation |
| REQ-017 — Agent + evaluation framework | final delivery contains both an operational agent path and an integrated evaluation framework | integrated runtime/evaluator demonstration + source/eval suite |

These are not optional packaging details. A strong agent without a trustworthy evaluator, or strong experiments without a usable integrated agent path, does not satisfy the complete requested scope.

## 4. P0 — agent construction acceptance

| Requirement coverage | Final capability | Required evidence before acceptance | Current state |
|---|---|---|---|
| REQ-002, REQ-009 | Integrate with the supplied industrial API and consult assets/analyses/technical data | real contract/conformance test, typed tool contract, successful production-path trace | Research foundations exist; final production integration pending |
| REQ-005 | Contextualize a customer request | representative end-to-end contextualization scenario with correct grounded response | Evaluation/case foundations exist; final integrated proof pending |
| REQ-006, AG-003, AG-005 | Investigate using appropriate tools and stopping/planning behavior | tool-selection/evidence metrics + end-to-end scenario traces | Candidate/evaluator research ongoing |
| REQ-007, REQ-011, REQ-014, REQ-015, EV-009 | Execute justified platform actions safely | correct tool/target/arguments/justification, accepted execution event, no duplicate/unnecessary action | Safety/evaluator foundations exist; final integrated proof pending |
| REQ-008, REQ-010 | Request additional information / ask pertinent questions when evidence is insufficient | ambiguity/missing-information scenarios, justified clarification behavior | Must be explicit in final regression suite |
| REQ-012, EV-010 | Escalate correctly to human analysis | correct escalation decision and useful evidence/reason handoff where gold permits | Evaluator foundations exist; final integrated proof pending |
| REQ-013, AG-006 | Handle complete, partial, inconclusive, conflicting and unavailable results | deterministic robustness profiles covering all response modes + safe fallback metrics | Required before final acceptance |
| AG-004 | Construct valid and semantically correct arguments | schema validation + semantic argument evaluator + negative tests | Research evaluator foundations exist |
| AG-007 | Ground responses in evidence | evidence correctness/recall and unsupported-claim checks | Current confirmatory evaluation directly contributes |
| AG-009 | Decide orient/investigate/act/escalate/clarify/abstain appropriately | deterministic decision metrics and scenario coverage | Current confirmatory evaluation directly contributes |
| REQ-016, AG-010 | Keep calls/results inspectable | normalized structured trace containing decisions, tools, arguments, results and final outcome | Trace foundations exist; final production-path inspection pending |

## 5. P0 — evaluation framework acceptance

The final delivery is incomplete if it contains only an agent. The updated TAPI explicitly requires both **agent construction** and an **agent evaluation framework**.

| Requirement coverage | Evaluation capability | Required final evidence | Current state |
|---|---|---|---|
| REQ-017 | Integrated agent + evaluator | same production-path run can be captured and evaluated without leaking private truth into runtime | Architecture/evaluator foundations exist; final integration pending |
| EV-001 | Function/tool choice | required/allowed/forbidden tool correctness metrics | Implemented in research stack; preserve into final eval suite |
| EV-002 | Argument accuracy | schema + semantic argument correctness | Implemented foundations; final regression coverage required |
| EV-003 | Execution trajectory | policy/order/evidence/efficiency evaluation without brittle exact-sequence primary scoring | Research foundations exist |
| EV-004 | Evidence use | required evidence, provenance, uncertainty/conflict handling | Current deterministic/semantic evaluation path contributes |
| EV-005 | Response quality | structured conclusion/fact quality; no exact-string primary score | Semantic stage required only under its authorized/frozen gate |
| EV-006 | Safety | identity/seed isolation, permissions/policy/resource boundaries, forbidden action checks | Security/evaluator foundations exist; production regression required |
| EV-007 | Failure performance | robust success/safe fallback under deterministic perturbations | Must be part of pre-release verification |
| EV-008 | Stability | repeated-run reliability under controlled environment/seed policy | Statistical/reliability evidence required |
| EV-009 | High-impact actions | decision/tool/target/arguments/justification/accepted/no-duplicate checks | Must be demonstrated end to end |
| EV-010 | Escalation | correct escalation + handoff completeness when gold supports it | Must be demonstrated end to end |
| EV-011 | Customer-safe communication | correctness separated from disclosure/style policy | Include only where annotation/rule is reliable |

The evaluator deliverable should expose, where useful for the final scope: scenario execution, metrics/evaluator library, trace inspection, controlled/adversarial variants, robustness/reliability analysis, capture/replay and reproducible experiment configuration.

## 6. P0 — benchmark/security integrity acceptance

| Constraint | Final acceptance condition |
|---|---|
| REQ-018, REQ-019 | evaluation-only gold/reference material never enters agent runtime context; canonical cases remain evaluation provenance, not prompt material |
| PC-001 | requester/user identity remains outside model control |
| PC-002 | evaluation seed remains outside model control |
| PC-003 | raw partner artifact provenance is preserved; normalization is derived/versioned rather than silently rewriting source truth |
| PC-004 | API permission enforcement and project/system policy enforcement remain separate and testable |
| PC-005 | accepted action-event semantics are used instead of false final-state equality assumptions |

Any violation of these boundaries blocks the corresponding scientific or production-readiness claim.

## 7. P1 — production-path acceptance

Production-first means the selected behavior must be operable beyond a benchmark script. Before production readiness is claimed, the applicable final system must demonstrate:

| Area | Required evidence |
|---|---|
| Contracts | typed/validated API and tool interfaces; explicit error classes |
| Authorization | deterministic authorization boundaries, audit trail and negative tests |
| Action reliability | idempotency/duplicate-action protection and retry policy justified by requirements/evidence |
| Failure handling | provider/tool/API timeout/error paths with safe fallback/recovery behavior |
| State/context | explicit request/state lifecycle; persistent memory only if justified by measured benefit |
| Configuration | versioned non-secret config and pinned dependencies/build inputs |
| Secrets/privacy | no credentials/private oracle/blind outcomes in runtime artifacts or logs |
| Observability | structured traces/logs/metrics sufficient to inspect decisions and failures |
| Performance | measured latency, reliability, resource/cost behavior appropriate to the final environment |
| Reproducibility | clean setup/build/run path from documented inputs |
| Rollback | known reversal/rollback path for the selected release |

## 8. Final demonstration acceptance

The final demonstration must exercise the **real integrated path**, not a scripted mock-only path.

Minimum demonstration portfolio:

1. **Contextualize:** a request is handled with relevant grounded context.
2. **Investigate:** the agent chooses and uses real read tools, handles evidence, and reaches an appropriate decision.
3. **Execute:** a justified state-changing request produces the correct accepted action behavior under authorization controls.
4. **Clarify / insufficient evidence:** the agent requests additional information or abstains safely when appropriate.
5. **Escalate:** the agent escalates a case with useful evidence/reason when required.
6. **Failure/robustness:** at least one incomplete/conflicting/unavailable-tool/data condition is handled safely.
7. **Per-run evaluation:** the resulting trace is evaluated by the integrated evaluation framework without exposing evaluation-only truth to the agent.
8. **Reliability view:** show aggregate/repeated-run or robustness evidence rather than relying on a single happy path.

## 9. Final documentation/package acceptance

Final handoff should include:

- problem and scope;
- final architecture and ADRs;
- setup/configuration and dependency versions;
- model/provider/runtime choices and why they were selected;
- evaluation methodology and benchmark integrity boundaries;
- technical experiment(s), baselines/ablations and quantitative results with uncertainty;
- robustness/failure analysis;
- limitations, non-claims and known risks;
- source code and evaluation suite;
- deployment/runbook/monitoring/rollback instructions appropriate to the implemented production path;
- reproducibility/provenance package;
- real production-path demonstration instructions.

This section is the final closure evidence for REQ-003 and REQ-004, not a substitute for the underlying experiment/result artifacts.

## 10. Architecture complexity gate

No optional architecture component is a delivery requirement by itself.

```text
RAG / vector DB / reranker / multi-agent / persistent memory / MCP / adaptive routing / richer UI
        ↓
Which P0/P1 requirement or measured bottleneck does it improve?
        ↓
What is the simple baseline?
        ↓
Does controlled quantitative evidence show material benefit after production costs/risks?
        ├── NO  → do not add / remove
        └── YES → ADR → regression → eligible for PREFERRED/FROZEN
```

This is how the project maximizes quality: **complete mandatory behavior and evidence first; add complexity only when it earns its place quantitatively.**

## 11. Final acceptance rule

The project may be called complete only when:

```text
REQ-001/003/004/017 project-level obligations are closed
+
requested P0 agent capabilities are demonstrably covered
+
evaluation framework is integrated and trustworthy
+
benchmark/security integrity boundaries hold
+
applicable P1 production risks are closed or explicitly bounded
+
final material choices satisfy PROJECT-PRINCIPLES
+
final claims do not exceed independent/frozen evidence
```

Any uncovered P0 row is a delivery blocker unless the final scope is explicitly reduced with an evidence-honest limitation.
