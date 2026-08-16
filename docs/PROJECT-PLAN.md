# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 GROQ FREE MODEL PASS; E9 PRIVATE TASK-QUALITY SCORED; E10 DEV-ONLY PARTIAL IMPROVEMENT RECORDED; E10b STRONG DEV-ONLY IMPROVEMENT WITH ESCALATION GAP; E10c NO ESCALATION IMPROVEMENT; E10d DEV-ONLY PASS; FULL DEV+VALIDATION REMEASUREMENT READY  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 17:15 BRT  
**Target final delivery:** 2026-09-08

This is the active execution plan. It separates frozen evidence/contracts from experimental architecture decisions, preserves the USD 0 provider constraint, and treats private task-quality score as the acceptance signal instead of proxy/schema success.

## Current gate

E10d ran locally and passed the DEV-only private scorer target. It preserved decision, evidence and action correctness, fixed escalation correctness, kept premature actions and unsupported final claims at 0.0, and kept LOCKED_TEST blocked.

The full DEV+VALIDATION remeasurement runner is now ready. It has not yet produced a real full score. The next accepted evidence must come from a local full E10d capture scored by `scripts/research/e9_evaluator_side_scorer_v3.py` after outputs are fixed.

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
- E10d full DEV+VALIDATION remeasurement manifest, runner, documentation and dry-run CI are ready.

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

| Metric | E9 full DEV+VALIDATION | E9 DEV-only baseline | E10 DEV-only | E10b DEV-only | E10c DEV-only | E10d DEV-only |
|---|---:|---:|---:|---:|---:|---:|
| Real task quality | 0.631 | 0.4762 | 0.619 | 0.8571 | 0.8571 | 1.0 |
| Decision correctness | 0.6667 | 0.3333 | 0.3333 | 1.0 | 1.0 | 1.0 |
| Evidence correctness | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Action correctness | 0.25 | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 |
| Escalation correctness | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 |

Interpretation: E8 proxy/schema success was over-optimistic. E10 fixed evidence grounding. E10b fixed decision/action calibration on DEV. E10c did not improve escalation. E10d fixed the remaining DEV-only escalation consistency gap.

## E10d DEV-only escalation consistency guard

E10d is not prompt-only. It preserves E10c generation, then applies a deterministic visible-output guard before private scoring.

The guard is allowed because it uses only the model's own visible parsed output and visible policy consistency. It does not use expected paths, private oracle rows, evaluator labels, reference trajectories, validation feedback or LOCKED_TEST.

## Immediate next gate — full DEV+VALIDATION E10d remeasurement

Now that E10d passed DEV-only, the next step is to run a fixed full DEV+VALIDATION capture for the E10d candidate and score it with E9 v3.

### Full remeasurement artifacts ready

- `research/experiments/e10d-full-dev-validation-remeasurement-manifest.json`
- `scripts/research/e10d_full_dev_validation_capture.py`
- `research/82-e10d-full-dev-validation-remeasurement.md`
- `.github/workflows/research-e10d-full.yml`

The full dry-run CI validates the capture shape without external model calls. The real full Groq capture must still be run locally before claiming any full DEV+VALIDATION quality gain.

### Full remeasurement rules

- Do not tune on VALIDATION.
- Keep LOCKED_TEST blocked.
- Do not commit raw private oracles, raw fixed parsed outputs, score rows, output hashes or private expected paths.
- Commit only sanitized aggregate results and a written interpretation.
- Compare against the original E9 full DEV+VALIDATION baseline.
- Do not freeze final model/provider/architecture unless full remeasurement supports it and later integration gates also pass.

### Full remeasurement acceptance target

The full DEV+VALIDATION E10d candidate should improve over the E9 full baseline without safety regressions:

- real task quality greater than 0.631;
- evidence correctness greater than 0.0;
- action correctness not worse than 0.25;
- escalation correctness not worse than 0.5;
- premature action rate remains 0.0;
- unsupported final-claim rate remains 0.0;
- LOCKED_TEST remains inaccessible.

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
- [x] Build E10d DEV-only escalation consistency guard.
- [x] Add E10d dry-run CI guard.
- [x] Run E10d real DEV-only capture locally.
- [x] Score E10d with E9 v3 private scorer.
- [x] Compare E10d against E10b/E10c and the acceptance target.
- [x] Record E10d as DEV-only acceptance target met.
- [x] Build full DEV+VALIDATION E10d remeasurement runner.
- [x] Add full E10d dry-run CI guard.
- [ ] Run full DEV+VALIDATION E10d capture locally.
- [ ] Score full DEV+VALIDATION E10d with E9 v3 private scorer.
- [ ] Compare full E10d against E9 full baseline.
- [ ] Decide whether to promote E10d candidate into integration gates.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.
