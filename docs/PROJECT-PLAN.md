# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 GROQ FREE MODEL PASS; E9 PRIVATE TASK-QUALITY SCORED; E10 DEV-ONLY PARTIAL IMPROVEMENT; E10b STRONG DEV-ONLY IMPROVEMENT WITH ESCALATION GAP; E10c NO ESCALATION IMPROVEMENT; E10d DEV-ONLY PASS; E10d FULL DEV+VALIDATION IMPROVED WITH SAFETY REGRESSION; E10e DEV-ONLY SAFETY PASS; E10e FULL DEV+VALIDATION SAFETY REGRESSION PERSISTS; E10f DEV-ONLY SAFETY PASS WITH ACTION COLLAPSE  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 18:42 BRT  
**Target final delivery:** 2026-09-08

This is the active execution plan. It separates frozen evidence/contracts from experimental architecture decisions, preserves the USD 0 provider constraint, and treats private task-quality score and safety gates as the acceptance signal instead of proxy/schema success.

## Current gate

E10f was run on DEV only after E10e failed to fix the full DEV+VALIDATION premature-action regression. The E10f scorer run is valid and keeps safety clean on DEV: `premature_action_rate = 0.0`, `unsupported_final_claim_rate = 0.0`, and `LOCKED_TEST accessed = false`.

Decision: do not promote E10f to a new full DEV+VALIDATION remeasurement. E10f is too conservative: it restores/keeps safety, but collapses `action_correctness` to 0.0, drops `decision_correctness` to 0.3333, and lowers DEV real task quality to 0.7619, below the preregistered DEV acceptance floor of 0.8571.

The next gate should be E10g, a balanced safety-action guard. E10g must not use VALIDATION for tuning, must not use private oracle values in the model or guard, and must keep LOCKED_TEST blocked.

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
- E10f DEV-only stricter visible-output safety guard completed and scored; safety remained clean, but action correctness collapsed.

## Score history

| Metric | E9 full DEV+VALIDATION | E9 DEV-only baseline | E10 DEV-only | E10b DEV-only | E10c DEV-only | E10d DEV-only | E10d full DEV+VALIDATION | E10e DEV-only | E10e full DEV+VALIDATION | E10f DEV-only |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Real task quality | 0.631 | 0.4762 | 0.619 | 0.8571 | 0.8571 | 1.0 | 0.8214 | 1.0 | 0.8214 | 0.7619 |
| Decision correctness | 0.6667 | 0.3333 | 0.3333 | 1.0 | 1.0 | 1.0 | 0.75 | 1.0 | 0.75 | 0.3333 |
| Evidence correctness | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.75 | 1.0 | 0.75 | 1.0 |
| Action correctness | 0.25 | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 | 0.75 | 1.0 | 0.75 | 0.0 |
| Escalation correctness | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.5 | 1.0 | 0.5 | 1.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.25 | 0.0 | 0.25 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.5 | 0.0 | 0.5 | 1.0 |

Interpretation: E10f fixes the visible DEV safety side but overblocks. It is not a good promotion candidate because the private scorer expects the DEV action capability to be preserved.

## E10f artifacts

- `research/experiments/e10f-dev-only-stricter-visible-safety-guard-manifest.json`
- `scripts/research/e10f_dev_only_stricter_visible_safety_guard.py`
- `research/88-e10f-dev-only-stricter-visible-safety-guard.md`
- `.github/workflows/research-e10f.yml`
- `research/results/e10f-dev-only-private-score-summary-2026-08-16.json`
- `research/89-e10f-dev-only-private-score-results.md`

## Immediate next gate — E10g balanced safety-action guard

E10g should target the failure mode exposed by E10f: broad safety blocking removes action correctness. The next guard should be preregistered as a general policy-level visible-output guard and tested on DEV before any new full remeasurement.

### E10g design direction

- Preserve E10e/E10d DEV action gains when the model visibly selects a supported human-handoff or justified action path.
- Avoid E10f-style blanket suppression of state-changing action.
- Block action only when visible safety invariants fail clearly.
- Distinguish autonomous high-impact maintenance action from human handoff/review routing.
- Preserve evidence correctness and escalation correctness.
- Keep premature action at 0.0 and unsupported final claims at 0.0.
- Do not use expected paths, private oracle rows, evaluator labels, validation feedback or LOCKED_TEST.

### E10g acceptance target before another full remeasurement

- Premature action rate remains 0.0 on DEV.
- Unsupported final-claim rate remains 0.0.
- Evidence correctness remains 1.0 on DEV.
- Action correctness improves above 0.0 and ideally returns to 1.0 on DEV.
- Escalation correctness remains 1.0 on DEV.
- Real task quality returns to at least 0.8571 on DEV.
- LOCKED_TEST remains blocked.
- No raw private or fixed-output material is committed.

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
- [x] Build E10f stricter safety guard without VALIDATION tuning.
- [x] Add E10f dry-run CI guard.
- [x] Run E10f DEV-only capture locally.
- [x] Score E10f with E9 v3 private scorer.
- [x] Record E10f as safety-clean but not accepted because action collapses.
- [ ] Build E10g balanced safety-action guard without VALIDATION tuning.
- [ ] Run E10g DEV-only capture locally.
- [ ] Score E10g with E9 v3 private scorer.
- [ ] Only after DEV-only safety/action acceptance, consider another full DEV+VALIDATION remeasurement.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.
