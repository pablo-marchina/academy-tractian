# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 GROQ FREE MODEL PASS; E9 PRIVATE TASK-QUALITY SCORED; E10 DEV-ONLY PARTIAL IMPROVEMENT RECORDED; E10b STRONG DEV-ONLY IMPROVEMENT WITH ESCALATION GAP; E10c DEV-ONLY ESCALATION LOOP READY  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 16:28 BRT  
**Target final delivery:** 2026-09-08

This is the active execution plan after the real TRACTIAN package was audited and after the first real free-provider and private scorer cycles. The plan separates frozen evidence/contracts from experimental architecture decisions, explicitly forbids demo-first development, preserves the USD 0 provider constraint, and treats private task-quality score as the acceptance signal instead of proxy/schema success.

## Current gate

E10c is ready for local DEV-only execution. It has not yet produced a real quality score. The next accepted evidence must come from a local Groq capture scored by `scripts/research/e9_evaluator_side_scorer_v3.py` against private DEV expected paths after outputs are fixed.

## Frozen / complete

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` and gold/evaluator boundary frozen.
- `BENCHMARK-SPLIT-v1` frozen before runtime/model/prompt/architecture selection.
- E2 framework-neutral ToolSpec/Trace/Replay/Evaluator harness complete.
- E4 B0-B3 guarded-boundary DEV+VALIDATION comparison complete.
- E5 evidence acquisition/stopping comparison executed.
- E6 LangGraph + ToolSpec + HarnessRunner + HttpxTransport live path passed.
- E7 topology ADR recorded: native ToolSpec calls internally, MCP-compatible adapter externally.
- E8 Groq `llama-3.1-8b-instant` passed DEV + VALIDATION as a real zero-cost remote model candidate under proxy/schema gates.
- E9 private evaluator-side task-quality scorer implemented and run against fixed Groq outputs plus private DEV/VALIDATION expected paths.
- E10 DEV-only evidence-first loop improved evidence but not action/escalation.
- E10b DEV-only action/escalation loop improved decision/evidence/action but not escalation.
- E10c DEV-only escalation calibration manifest, capture wrapper, documentation and dry-run CI are ready.

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

| Metric | E9 full DEV+VALIDATION | E9 DEV-only baseline | E10 DEV-only | E10b DEV-only |
|---|---:|---:|---:|---:|
| Real task quality | 0.631 | 0.4762 | 0.619 | 0.8571 |
| Decision correctness | 0.6667 | 0.3333 | 0.3333 | 1.0 |
| Evidence correctness | 0.0 | 0.0 | 1.0 | 1.0 |
| Action correctness | 0.25 | 0.0 | 0.0 | 1.0 |
| Escalation correctness | 0.5 | 0.0 | 0.0 | 0.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 |

Interpretation: E8 proxy/schema success was over-optimistic. E10 fixed evidence grounding. E10b fixed decision/action calibration on DEV, but escalation correctness remains the blocker before full DEV+VALIDATION.

## E10c DEV-only escalation calibration

E10c is a narrower DEV-only loop. It preserves E10b's evidence/action rules and focuses on the remaining escalation gap.

### E10c artifacts ready

- `research/experiments/e10c-dev-only-escalation-calibration-manifest.json`
- `scripts/research/e10c_dev_only_escalation_capture.py`
- `research/78-e10c-dev-only-escalation-calibration.md`
- `.github/workflows/research-e10c.yml`

The E10c CI dry-run validates the DEV-only capture shape without external model calls. The real Groq capture must still be run locally before claiming any quality gain.

### E10c design direction

- Preserve `evidence_correctness = 1.0` if possible.
- Preserve `action_correctness > 0.0`.
- Improve `escalation_correctness > 0.0`.
- Treat human escalation as not mutually exclusive with action.
- Set `requires_human_escalation=true` for specialist/case-escalate endpoints and for visible safety, severity, permission, specialist-review, high-impact or human-approval reasons.
- Do not escalate for generic uncertainty alone.
- Keep premature actions and unsupported final claims at 0.0.

### E10c acceptance target before full remeasurement

Do not promote E10c to full DEV+VALIDATION unless a DEV-only private scorer run shows all of the following:

- evidence correctness remains materially above the E9 DEV baseline;
- action correctness remains above 0.0;
- escalation correctness improves above 0.0;
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
- [x] Build E10c DEV-only escalation calibration runner.
- [x] Add E10c dry-run CI guard.
- [ ] Run E10c real DEV-only Groq capture locally.
- [ ] Score E10c with E9 v3 private scorer.
- [ ] Compare E10c against E10b and the acceptance target.
- [ ] Promote to full DEV+VALIDATION only if E10c meets acceptance target.
- [ ] Keep LOCKED_TEST blocked.
- [ ] Keep final architecture unfrozen.
