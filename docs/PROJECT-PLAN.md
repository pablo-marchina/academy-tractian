# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 GROQ FREE MODEL PASS; E9 PRIVATE TASK-QUALITY SCORED; E10 DEV-ONLY PARTIAL IMPROVEMENT; E10b STRONG DEV-ONLY IMPROVEMENT WITH ESCALATION GAP; E10c NO ESCALATION IMPROVEMENT; E10d DEV-ONLY PASS; E10d FULL DEV+VALIDATION IMPROVED WITH SAFETY REGRESSION; E10e DEV-ONLY SAFETY PASS  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 17:52 BRT  
**Target final delivery:** 2026-09-08

This is the active execution plan. It separates frozen evidence/contracts from experimental architecture decisions, preserves the USD 0 provider constraint, and treats private task-quality score and safety gates as the acceptance signal instead of proxy/schema success.

## Current gate

E10d passed DEV-only and was remeasured on full DEV+VALIDATION. The full result improves over the E9 full baseline on real task quality, decision correctness, evidence correctness, action correctness and proxy disagreement. However, it fails the full promotion gate because premature action rate increased from 0.0 to 0.25.

E10e has now passed DEV-only private scoring. It preserved task quality and restored/kept premature action at 0.0 on DEV. This allows another full DEV+VALIDATION remeasurement of the E10e candidate, without tuning on VALIDATION and with LOCKED_TEST still blocked. Final architecture remains unfrozen.

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

| Metric | E9 full DEV+VALIDATION | E9 DEV-only baseline | E10 DEV-only | E10b DEV-only | E10c DEV-only | E10d DEV-only | E10d full DEV+VALIDATION | E10e DEV-only |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Real task quality | 0.631 | 0.4762 | 0.619 | 0.8571 | 0.8571 | 1.0 | 0.8214 | 1.0 |
| Decision correctness | 0.6667 | 0.3333 | 0.3333 | 1.0 | 1.0 | 1.0 | 0.75 | 1.0 |
| Evidence correctness | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.75 | 1.0 |
| Action correctness | 0.25 | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 | 0.75 | 1.0 |
| Escalation correctness | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.5 | 1.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.25 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.5 | 0.0 |

Interpretation: E10e preserved the DEV-only perfect score while adding the safety guard. Since the E10d full remeasurement exposed a holdout safety regression, the next required evidence is a full DEV+VALIDATION E10e remeasurement.

## E10e DEV-only premature-action safety guard

E10e keeps the E10d visible-output escalation guard and adds a second deterministic visible-output safety guard.

### E10e artifacts

- `research/experiments/e10e-dev-only-premature-action-safety-guard-manifest.json`
- `scripts/research/e10e_dev_only_premature_action_guard.py`
- `research/84-e10e-dev-only-premature-action-safety-guard.md`
- `.github/workflows/research-e10e.yml`
- `research/results/e10e-dev-only-private-score-summary-2026-08-16.json`
- `research/85-e10e-dev-only-private-score-results.md`

### E10e DEV-only result

- Scoreable calls: 6.
- Real task quality: 1.0.
- Decision correctness: 1.0.
- Evidence correctness: 1.0.
- Action correctness: 1.0.
- Escalation correctness: 1.0.
- Premature action rate: 0.0.
- Unsupported final-claim rate: 0.0.
- Proxy-vs-real disagreement rate: 0.0.
- Guard outputs checked: 6.
- Guard outputs changed: 0.

The DEV-only outputs were already safety-consistent under the visible-output premature-action guard. This does not prove that the full DEV+VALIDATION safety regression is fixed; it only allows the next full remeasurement.

### E10e acceptance decision

E10e meets the DEV-only safety acceptance target. The next step is full DEV+VALIDATION E10e remeasurement.

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
- [ ] Build full DEV+VALIDATION E10e remeasurement runner.
- [ ] Run full DEV+VALIDATION E10e capture locally.
- [ ] Score full DEV+VALIDATION E10e with E9 v3 private scorer.
- [ ] Compare full E10e against E9 full baseline and E10d full result.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.
