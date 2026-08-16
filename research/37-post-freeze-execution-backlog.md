# Post-E0/E1 Execution Backlog — E4 Validation Complete

Status: **E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 NEXT**

This file supersedes the pre-freeze task statuses in `research/06-research-backlog.md` for active execution. The older file is retained as historical planning evidence.

## Completed gates

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` semantics frozen.
- 16 scenarios / 17 tickets / 10 leakage groups frozen as grouping constraints.
- E2 integrated framework-neutral harness complete.
- `BENCHMARK-SPLIT-v1` frozen before runtime/model/prompt/architecture selection.
- E4 B0-B3 guarded-boundary DEV+VALIDATION comparison complete.

## E2 completion

- [x] executable ScenarioSchema v1 models;
- [x] 18-operation Canonical ToolSpec registry;
- [x] runner-owned identity and seed boundary;
- [x] B0 HTTP transport + trace/replay runner;
- [x] strict B1 validation;
- [x] deterministic B2 permission/resource guard;
- [x] deterministic B3 evidence-aware action gate;
- [x] integrated evaluator suite;
- [x] representative pass/fail fixtures;
- [x] CI retained.

Completion report: `research/39-e2-integrated-completion-report.md`.

## E3 completion

- [x] **DEV:** `asset_G501`, `asset_C710`, `asset_S420`, `asset_M208`, `asset_M101` — 5 groups / 8 scenarios;
- [x] **VALIDATION:** `asset_B204`, `asset_M102` — 2 groups / 3 scenarios;
- [x] **LOCKED_TEST:** `asset_V301`, `asset_M605`, `asset_M205` — 3 groups / 5 scenarios.

Artifacts:

- `research/40-e3-benchmark-split-freeze-v1.md`
- `research/frozen/benchmark-split-v1.json`
- `scripts/research/e3_validate_split.py`

## E4 completion

- [x] define the B0-B3 experiment manifest;
- [x] validate that DEV + VALIDATION are allowed and LOCKED_TEST is forbidden;
- [x] implement DEV-only E4 runner;
- [x] require explicit `proposal_source_class` in the DEV runner;
- [x] block LOCKED_TEST by construction in the DEV runner;
- [x] run B0/B1/B2/B3 smoke path on DEV with scripted/reference proposal source;
- [x] mark scripted/reference source as infrastructure-only;
- [x] implement model-proposal adapter;
- [x] require `proposal_source_class=model_agent` and provider/model identity;
- [x] block LOCKED_TEST and non-DEV groups in the model-proposal adapter;
- [x] generate first DEV model proposal plan;
- [x] run `scripts/research/e4_model_proposal_adapter.py` on that proposal plan;
- [x] export B0/B1/B2/B3 boundary metrics for model proposals;
- [x] combine first DEV boundary run with private DEV proxy evaluator;
- [x] generate scoreable DEV proposal plan with natural-language final answer/handoff text;
- [x] include B1 pressure case for malformed/invalid action argument;
- [x] include B3 pressure case for premature action before evidence;
- [x] rerun B0/B1/B2/B3 on scoreable DEV proposal plan;
- [x] combine scoreable run with private DEV evaluator in redacted aggregate form;
- [x] carry B1/B2/B3 forward as candidate boundaries and B0 as baseline;
- [x] generate a VALIDATION-only proposal plan for `asset_B204` and `asset_M102`;
- [x] implement a VALIDATION-only proposal adapter;
- [x] keep `LOCKED_TEST` blocked by construction;
- [x] rerun B0/B1/B2/B3 boundary metrics on VALIDATION in CI;
- [x] combine with private VALIDATION evaluator locally without exposing gold;
- [x] promote/reject B1/B2/B3 components with evidence.

## Scoreable DEV result

| Variant | Scoreable pass | Scoreable fail | Action OK | Safety OK | Uncontained safety failures |
|---|---:|---:|---:|---:|---:|
| B0 | 6/8 | 2/8 | 6/8 | 6/8 | 2 |
| B1 | 7/8 | 1/8 | 7/8 | 7/8 | 1 |
| B2 | 7/8 | 1/8 | 7/8 | 7/8 | 1 |
| B3 | 8/8 | 0/8 | 8/8 | 8/8 | 0 |

## Scoreable VALIDATION result

| Variant | Scoreable pass | Scoreable fail | Action OK | Safety OK | Uncontained safety failures |
|---|---:|---:|---:|---:|---:|
| B0 | 2/3 | 1/3 | 2/3 | 2/3 | 2 |
| B1 | 2/3 | 1/3 | 2/3 | 2/3 | 1 |
| B2 | 2/3 | 1/3 | 2/3 | 2/3 | 1 |
| B3 | 3/3 | 0/3 | 3/3 | 3/3 | 0 |

## E4 component decision

- **B0:** retain as baseline only; reject as deployment boundary due uncontained safety failures.
- **B1:** promote as a required validation sublayer; reject as sufficient standalone boundary.
- **B2:** promote as a required resource/permission sublayer based on DEV scope-safety evidence; VALIDATION did not contain new scope-denial pressure.
- **B3:** promote as the current guarded-boundary candidate for the next experimental stage.

## E5 next active task

Move from boundary safety to evidence acquisition / stopping behavior.

Required work:

- [ ] preregister E5 evidence/stopping experiment;
- [ ] use B3 as current guarded-boundary candidate;
- [ ] keep B0 as baseline where useful;
- [ ] compare fixed/reference-like investigation, free tool loop and evidence-sufficiency/stopping policy;
- [ ] measure premature stopping, unnecessary calls, task success, escalation correctness and efficiency;
- [ ] keep LOCKED_TEST blocked;
- [ ] do not freeze runtime/model/MCP/UI yet.

## Methodological constraint

No item in E2, E3 or E4 is a demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts, splits and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment and cannot use LOCKED_TEST before final evaluation.
