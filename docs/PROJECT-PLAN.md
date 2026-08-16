# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 GROQ FREE MODEL PASS; E9 PRIVATE TASK-QUALITY SCORED; E10 DEV-ONLY PARTIAL IMPROVEMENT RECORDED; E10b STRONG DEV-ONLY IMPROVEMENT WITH ESCALATION GAP; E10c NO ESCALATION IMPROVEMENT; E10d NEXT  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 16:40 BRT  
**Target final delivery:** 2026-09-08

This is the active execution plan. It separates frozen evidence/contracts from experimental architecture decisions, preserves the USD 0 provider constraint, and treats private task-quality score as the acceptance signal instead of proxy/schema success.

## Current gate

E10c ran locally and scored successfully, but it did not improve escalation correctness. The next gate is E10d: a DEV-only visible-output escalation consistency guard. E10d must not use private oracle values; it may only enforce consistency between the model's own visible output fields, such as `decision_class`, `action_escalation_rubric`, `action_endpoint`, `proposed_next_step`, and `risk_notes`.

## Frozen / complete

- E0/E1 contract and gold/evaluator boundary frozen.
- E2 framework-neutral ToolSpec/Trace/Replay/Evaluator harness complete.
- E3 benchmark split frozen before architecture/model/prompt/runtime selection.
- E4 B3 guarded boundary promoted.
- E5 evidence-sufficiency/stopping policy promoted.
- E6 LangGraph + ToolSpec + HarnessRunner + HttpxTransport live path passed.
- E7 topology ADR recorded: native ToolSpec calls internally, MCP-compatible adapter externally.
- E8 Groq `llama-3.1-8b-instant` passed DEV + VALIDATION as a real zero-cost remote model candidate under proxy/schema gates.
- E9 private evaluator-side task-quality scorer implemented and run against fixed Groq outputs plus private DEV/VALIDATION expected paths.
- E10 DEV-only evidence-first loop improved evidence but not action/escalation.
- E10b DEV-only action/escalation loop improved decision/evidence/action but not escalation.
- E10c DEV-only escalation loop preserved E10b gains but did not improve escalation.

## Current candidate bundle

- Boundary: B3 guarded boundary.
- Evidence/stopping: evidence-sufficiency policy.
- Evidence planning: adaptive from missing evidence requirements.
- Runtime: LangGraph current candidate.
- Execution boundary: HarnessRunner.
- Transport: HttpxTransport live API path.
- Internal tool surface: native ToolSpec calls.
- External interoperability surface: MCP-compatible adapter.
- Leading free-provider candidate: Groq `llama-3.1-8b-instant`.
- Paid providers: OpenAI/Anthropic disabled under the USD 0 project constraint.

## Score history

| Metric | E9 full DEV+VALIDATION | E9 DEV-only baseline | E10 DEV-only | E10b DEV-only | E10c DEV-only |
|---|---:|---:|---:|---:|---:|
| Real task quality | 0.631 | 0.4762 | 0.619 | 0.8571 | 0.8571 |
| Decision correctness | 0.6667 | 0.3333 | 0.3333 | 1.0 | 1.0 |
| Evidence correctness | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 |
| Action correctness | 0.25 | 0.0 | 0.0 | 1.0 | 1.0 |
| Escalation correctness | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

Interpretation: E8 proxy/schema success was over-optimistic. E10 fixed evidence grounding. E10b fixed decision/action calibration on DEV. E10c did not improve escalation, so escalation correctness remains the blocker before full DEV+VALIDATION.

## E10d DEV-only escalation consistency guard

E10d should not be another prompt-only escalation instruction. It should preserve E10b/E10c evidence, decision and action gains while enforcing output-level consistency based only on the model's own visible response.

### E10d design direction

- If `decision_class=escalation_candidate`, then `requires_human_escalation=true`.
- If `action_escalation_rubric.needs_human_escalation=true`, then `requires_human_escalation=true`.
- If `action_endpoint`, `proposed_next_step`, or `risk_notes` names `request-specialist`, `case escalation`, `escalate`, `specialist`, `human approval`, `engineering approval`, `permission`, safety, severity or high operational impact, then `requires_human_escalation=true`.
- Preserve the model's existing evidence/action decision unless the output is internally inconsistent.
- Do not use expected paths, private oracle rows, evaluator labels or validation feedback.

### E10d acceptance target before full remeasurement

Do not promote E10d to full DEV+VALIDATION unless a DEV-only private scorer run shows all of the following:

- evidence correctness remains materially above the E9 DEV baseline;
- action correctness remains above 0.0;
- escalation correctness improves above 0.0;
- real task quality does not materially regress from E10b/E10c;
- premature action rate remains 0.0;
- unsupported final-claim rate remains 0.0;
- LOCKED_TEST remains inaccessible;
- no raw private oracles or fixed parsed outputs are committed.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- Optional provider comparators are useful but must not delay scorer-driven DEV improvements.
- No final architecture freeze yet.

## Current action checklist

- [x] E8 real free remote model path established with Groq.
- [x] E9 private scorer implemented and run against fixed Groq outputs.
- [x] E10 DEV-only evidence-first iteration run and scored.
- [x] E10b DEV-only action/escalation iteration run and scored.
- [x] E10c DEV-only escalation iteration run and scored.
- [x] Record E10c as no escalation improvement.
- [ ] Build E10d DEV-only escalation consistency guard.
- [ ] Run E10d real DEV-only Groq capture locally.
- [ ] Score E10d with E9 v3 private scorer.
- [ ] Compare E10d against E10b/E10c and the acceptance target.
- [ ] Promote to full DEV+VALIDATION only if E10d meets acceptance target.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.
