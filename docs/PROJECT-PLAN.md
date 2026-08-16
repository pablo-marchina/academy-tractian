# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 GROQ FREE MODEL PASS; E9 PRIVATE TASK-QUALITY SCORED; E10 DEV-ONLY PARTIAL IMPROVEMENT; E10b STRONG DEV-ONLY IMPROVEMENT WITH ESCALATION GAP; E10c NO ESCALATION IMPROVEMENT; E10d DEV-ONLY PASS; E10d FULL DEV+VALIDATION IMPROVED WITH SAFETY REGRESSION; E10e DEV-ONLY SAFETY PASS; E10e FULL DEV+VALIDATION SAFETY REGRESSION PERSISTS  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 18:15 BRT  
**Target final delivery:** 2026-09-08

This is the active execution plan. It separates frozen evidence/contracts from experimental architecture decisions, preserves the USD 0 provider constraint, and treats private task-quality score and safety gates as the acceptance signal instead of proxy/schema success.

## Current gate

E10e passed DEV-only private scoring, then was remeasured on full DEV+VALIDATION. The full result matches the E10d full result: it improves over the E9 full baseline on average quality, evidence and action, but premature action rate remains 0.25.

Decision: do not promote E10e into integration gates. The safety gate is stricter than the aggregate quality score. A candidate cannot advance while full premature action rate is above 0.0.

The next gate is E10f, a stricter general visible-output safety guard. E10f must not use VALIDATION for tuning, must not use private oracle values in the model or guard, and must keep LOCKED_TEST blocked.

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
- E10d DEV-only visible-output escalation consistency guard passed private DEV-only scoring.
- E10d full DEV+VALIDATION remeasurement completed and recorded as improved but not promotable because of a safety regression.
- E10e DEV-only premature-action safety guard completed and passed private DEV-only scoring.
- E10e full DEV+VALIDATION remeasurement completed and recorded as unchanged versus E10d full, with the safety regression still present.

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

| Metric | E9 full DEV+VALIDATION | E9 DEV-only baseline | E10 DEV-only | E10b DEV-only | E10c DEV-only | E10d DEV-only | E10d full DEV+VALIDATION | E10e DEV-only | E10e full DEV+VALIDATION |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Real task quality | 0.631 | 0.4762 | 0.619 | 0.8571 | 0.8571 | 1.0 | 0.8214 | 1.0 | 0.8214 |
| Decision correctness | 0.6667 | 0.3333 | 0.3333 | 1.0 | 1.0 | 1.0 | 0.75 | 1.0 | 0.75 |
| Evidence correctness | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.75 | 1.0 | 0.75 |
| Action correctness | 0.25 | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 | 0.75 | 1.0 | 0.75 |
| Escalation correctness | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.5 | 1.0 | 0.5 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.25 | 0.0 | 0.25 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.5 | 0.0 | 0.5 |

Interpretation: E10e did not regress relative to E10d full, but also did not fix the full safety issue. The E10e full guard checked 12 outputs and changed 0 outputs, so the unsafe full cases were not caught by the current visible-output safety conditions.

## E10e artifacts

- `research/experiments/e10e-dev-only-premature-action-safety-guard-manifest.json`
- `scripts/research/e10e_dev_only_premature_action_guard.py`
- `research/84-e10e-dev-only-premature-action-safety-guard.md`
- `.github/workflows/research-e10e.yml`
- `research/results/e10e-dev-only-private-score-summary-2026-08-16.json`
- `research/85-e10e-dev-only-private-score-results.md`
- `research/experiments/e10e-full-dev-validation-remeasurement-manifest.json`
- `scripts/research/e10e_full_dev_validation_capture.py`
- `research/86-e10e-full-dev-validation-remeasurement.md`
- `.github/workflows/research-e10e-full.yml`
- `research/results/e10e-full-dev-validation-private-score-summary-2026-08-16.json`
- `research/87-e10e-full-dev-validation-private-score-results.md`

## Immediate next gate — E10f stricter safety guard

E10f should target full safety generalization without using VALIDATION for tuning. It should be preregistered as a general policy-level visible-output guard, then tested on DEV before any new full remeasurement.

### E10f design direction

- Preserve evidence/action/escalation gains when action is visibly and strongly supported.
- Block state-changing action when the visible evidence plan is marginal or the proposed action is not explicitly supported by enough concrete evidence resources.
- Distinguish human escalation from autonomous action.
- Prefer investigate/escalate over action when visible safety support is weak.
- Do not use expected paths, private oracle rows, evaluator labels, validation feedback or LOCKED_TEST.

### E10f acceptance target before another full remeasurement

- Restore premature action rate to 0.0 on DEV.
- Keep unsupported final-claim rate at 0.0.
- Preserve evidence correctness above the E9 DEV baseline.
- Preserve action correctness above the E9 DEV baseline where safe.
- Preserve or improve escalation correctness.
- Keep LOCKED_TEST blocked.
- Do not commit raw private or fixed-output material.

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
- [x] E10d DEV-only escalation guard run and scored.
- [x] Full DEV+VALIDATION E10d capture run and scored.
- [x] Record E10d full result as improved but blocked by safety regression.
- [x] Build E10e safety/premature-action guard without VALIDATION tuning.
- [x] Add E10e dry-run CI guard.
- [x] Run E10e DEV-only capture locally.
- [x] Score E10e with E9 v3 private scorer.
- [x] Record E10e as DEV-only safety acceptance target met.
- [x] Build full DEV+VALIDATION E10e remeasurement runner.
- [x] Run full DEV+VALIDATION E10e capture locally.
- [x] Score full DEV+VALIDATION E10e with E9 v3 private scorer.
- [x] Record full E10e as not promotable because premature action remains 0.25.
- [ ] Build E10f stricter safety guard without VALIDATION tuning.
- [ ] Run E10f DEV-only capture locally.
- [ ] Score E10f with E9 v3 private scorer.
- [ ] Only after DEV-only safety acceptance, consider another full DEV+VALIDATION remeasurement.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.
