# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 GROQ FREE MODEL PASS; E9 PRIVATE TASK-QUALITY SCORED; E10 DEV-ONLY PARTIAL IMPROVEMENT; E10b STRONG DEV-ONLY IMPROVEMENT WITH ESCALATION GAP; E10c NO ESCALATION IMPROVEMENT; E10d DEV-ONLY PASS; E10d FULL DEV+VALIDATION IMPROVED WITH SAFETY REGRESSION; E10e SAFETY GUARD READY  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 17:40 BRT  
**Target final delivery:** 2026-09-08

This is the active execution plan. It separates frozen evidence/contracts from experimental architecture decisions, preserves the USD 0 provider constraint, and treats private task-quality score and safety gates as the acceptance signal instead of proxy/schema success.

## Current gate

E10d passed DEV-only and was remeasured on full DEV+VALIDATION. The full result improves over the E9 full baseline on real task quality, decision correctness, evidence correctness, action correctness and proxy disagreement. However, it fails the full promotion gate because premature action rate increased from 0.0 to 0.25.

Decision: do not promote E10d into integration gates. E10e is now ready as a DEV-only safety/premature-action guard. VALIDATION remains protected from tuning and LOCKED_TEST remains blocked.

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
- E10e DEV-only premature-action safety guard manifest, runner, documentation and dry-run CI are ready.

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

| Metric | E9 full DEV+VALIDATION | E9 DEV-only baseline | E10 DEV-only | E10b DEV-only | E10c DEV-only | E10d DEV-only | E10d full DEV+VALIDATION |
|---|---:|---:|---:|---:|---:|---:|---:|
| Real task quality | 0.631 | 0.4762 | 0.619 | 0.8571 | 0.8571 | 1.0 | 0.8214 |
| Decision correctness | 0.6667 | 0.3333 | 0.3333 | 1.0 | 1.0 | 1.0 | 0.75 |
| Evidence correctness | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.75 |
| Action correctness | 0.25 | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 | 0.75 |
| Escalation correctness | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.5 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.25 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.5 |

Interpretation: E10d generalizes partially. The full result is much stronger than the E9 full baseline in average quality, but the safety regression blocks promotion.

## E10e DEV-only premature-action safety guard

E10e keeps the E10d visible-output escalation guard and adds a second deterministic visible-output safety guard.

### E10e artifacts ready

- `research/experiments/e10e-dev-only-premature-action-safety-guard-manifest.json`
- `scripts/research/e10e_dev_only_premature_action_guard.py`
- `research/84-e10e-dev-only-premature-action-safety-guard.md`
- `.github/workflows/research-e10e.yml`

The dry-run CI validates the DEV-only capture shape without external model calls. The real Groq capture must still be run locally before claiming any E10e quality or safety improvement.

### E10e design direction

- Preserve the E10d improvements in evidence, action and escalation when a safe action is actually supported.
- Add a visible-output safety veto when the model's own output says evidence is incomplete, conditional, uncertain, permission-blocked, missing or not safe to act.
- Set `should_take_action_now=false` when the visible output is internally conditional or contradicts immediate state-changing action.
- Preserve `requires_human_escalation=true` when human review is still needed.
- Do not use expected paths, private oracle rows, evaluator labels, validation feedback or LOCKED_TEST.

### E10e acceptance target before another full remeasurement

- Restore premature action rate to 0.0.
- Keep unsupported final-claim rate at 0.0.
- Preserve evidence correctness above the E9 DEV baseline.
- Preserve action correctness above the E9 DEV baseline.
- Preserve escalation correctness at least comparable to the E9 full baseline.
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
- [ ] Run E10e DEV-only capture locally.
- [ ] Score E10e with E9 v3 private scorer.
- [ ] Only after DEV-only safety acceptance, consider another full DEV+VALIDATION remeasurement.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.
