# Academy × TRACTIAN — Project Action Plan

**Status:** E11 full safety regression persists; E12 hard-gate root-cause audit ready  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 21:58 BRT  
**Target final delivery:** 2026-09-08

## Current gate

E11 passed DEV-only private scoring after the E10h blocker analysis introduced independent action authorization. The full DEV+VALIDATION E11 remeasurement was then run and scored with E9 v3 after outputs were fixed.

Decision: do not promote E11 to integration gates. E11 full matches E10d/E10e/E10g full: it improves over the E9 full baseline in average task quality, evidence and action, but the full premature-action safety regression persists at `premature_action_rate = 0.25`. The required full safety gate is `premature_action_rate = 0.0`.

The full scorer run is valid: 12 fixed calls, 12 parsed model outputs, 5 private oracles loaded, 12 matching oracle calls and 12 scoreable calls. VALIDATION was measurement-only, not tuning. LOCKED_TEST remains blocked and final architecture remains unfrozen.

Project rule: no integration, no demo and no downstream phase while the current gate or any dependency used by it remains incomplete.

## Full score history

| Metric | E9 full | E10d full | E10e full | E10g full | E11 full |
|---|---:|---:|---:|---:|---:|
| Scoreable calls | 12 | 12 | 12 | 12 | 12 |
| Real task quality | 0.631 | 0.8214 | 0.8214 | 0.8214 | 0.8214 |
| Decision correctness | 0.6667 | 0.75 | 0.75 | 0.75 | 0.75 |
| Evidence correctness | 0.0 | 0.75 | 0.75 | 0.75 | 0.75 |
| Action correctness | 0.25 | 0.75 | 0.75 | 0.75 | 0.75 |
| Escalation correctness | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| Premature action rate | 0.0 | 0.25 | 0.25 | 0.25 | 0.25 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Proxy-vs-real disagreement rate | 1.0 | 0.5 | 0.5 | 0.5 | 0.5 |

## Split summary

| Split | Calls | Real quality | Decision | Evidence | Action | Escalation | Premature action | Unsupported claim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DEV | 6 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| VALIDATION | 6 | 0.6429 | 0.5 | 0.5 | 0.5 | 0.0 | 0.5 | 0.0 |

## Relevant completed artifacts

- `research/results/e11-full-dev-validation-private-score-summary-2026-08-16.json`
- `research/98-e11-full-dev-validation-private-score-results.md`

## E12 hard-gate root-cause audit ready

E12 is not a demo, not integration, not a new product and not a new guard. It audits E11 full capture instrumentation before any next design step.

Artifacts ready:

- `research/experiments/e12-hard-gate-root-cause-audit-manifest.json`
- `scripts/research/e12_hard_gate_root_cause_audit.py`
- `research/99-e12-hard-gate-root-cause-audit.md`
- `.github/workflows/research-e12.yml`

E12 audits whether the independent action-authorization policy actually ran on full DEV+VALIDATION, how many outputs it checked, how many it changed, whether it covered both DEV and VALIDATION, and whether the failure class is policy non-application, partial coverage, over-permissive authorization or wrong action-class/endpoint classification.

E12 may use local non-committed E11 full fixed-capture metadata plus sanitized aggregate score summaries. It must not use private expected paths, raw scorer rows, output hashes, evaluator labels, reference trajectories, validation feedback, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet` or LOCKED_TEST.

## Gate decision

E11 is not promotable to integration.

No next candidate is allowed until E12 identifies the root-cause class. No full rerun is allowed until a later change is preregistered from that root-cause class without VALIDATION tuning.

## Current action checklist

- [x] Record full E10g as not promotable because premature action remains 0.25.
- [x] Keep VALIDATION protected from tuning.
- [x] Keep LOCKED_TEST blocked.
- [x] Record E10h non-validation-tuned blocker analysis.
- [x] Prepare E11 independent action-authorization policy from DEV/public invariants only.
- [x] Run and score E11 DEV-only.
- [x] Prepare, run and score E11 full DEV+VALIDATION.
- [x] Record full E11 as not promotable because premature action remains 0.25.
- [x] Preregister E12 hard-gate root-cause audit.
- [x] Add E12 audit script.
- [x] Add E12 dry-run CI guard.
- [ ] Run E12 audit locally against non-committed E11 full capture.
- [ ] Record sanitized E12 audit result.
- [ ] Keep final architecture unfrozen.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- No final architecture freeze yet.
- No demo or integration while the current safety gate remains incomplete.
