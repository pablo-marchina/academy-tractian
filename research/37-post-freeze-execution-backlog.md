# Post-E0/E1 Execution Backlog — E4 Active

Status: **E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 ACTIVE**

This file supersedes the pre-freeze task statuses in `research/06-research-backlog.md` for active execution. The older file is retained as historical planning evidence.

## Completed gates

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` semantics frozen.
- 16 scenarios / 17 tickets / 10 leakage groups frozen as grouping constraints.
- E2 integrated framework-neutral harness complete.
- `BENCHMARK-SPLIT-v1` frozen before runtime/model/prompt/architecture selection.

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

Frozen assignment:

- [x] **DEV:** `asset_G501`, `asset_C710`, `asset_S420`, `asset_M208`, `asset_M101` — 5 groups / 8 scenarios;
- [x] **VALIDATION:** `asset_B204`, `asset_M102` — 2 groups / 3 scenarios;
- [x] **LOCKED_TEST:** `asset_V301`, `asset_M605`, `asset_M205` — 3 groups / 5 scenarios.

Artifacts:

- `research/40-e3-benchmark-split-freeze-v1.md`
- `research/frozen/benchmark-split-v1.json`
- `scripts/research/e3_validate_split.py`

## E4 completion so far

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
- [x] upload full boundary metrics as CI artifact;
- [x] record aggregate boundary metrics in `research/results/e4-dev-model-proposal-boundary-summary-2026-08-16.json`;
- [x] implement `scripts/research/e4_private_dev_evaluator.py` as a private-gold combiner;
- [x] combine the first DEV boundary metrics with private DEV expectations locally;
- [x] preserve evaluator-only gold outside the public repository;
- [x] record only redacted aggregate private proxy metrics in `research/results/e4-private-dev-evaluator-redacted-summary-2026-08-16.json`;
- [x] document the result in `research/44-e4-private-dev-evaluator-integration.md`.

First DEV model-proposal boundary result:

| Variant | Proposals | Executed calls | Blocked calls | Permission/scope executions | Contained unsafe proposals | Uncontained safety failures |
|---|---:|---:|---:|---:|---:|---:|
| B0 | 27 | 27 | 0 | 1 | 0 | 1 |
| B1 | 27 | 27 | 0 | 1 | 0 | 1 |
| B2 | 27 | 26 | 1 | 0 | 1 | 0 |
| B3 | 27 | 26 | 1 | 0 | 1 | 0 |

Private DEV proxy evaluator result:

| Variant | Scenarios | Proxy pass | Proxy partial | Proxy fail | Decision OK | Action OK | Safety OK | Avg evidence coverage | Avg conclusion marker coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 8 | 0 | 7 | 1 | 6 | 6 | 7 | 0.498 | 0.292 |
| B1 | 8 | 0 | 7 | 1 | 6 | 6 | 7 | 0.498 | 0.292 |
| B2 | 8 | 0 | 8 | 0 | 6 | 6 | 8 | 0.498 | 0.292 |
| B3 | 8 | 0 | 8 | 0 | 6 | 6 | 8 | 0.498 | 0.292 |

Interpretation: B2 contained one unsafe permission/resource-scope proposal that B0/B1 would execute. B1 had no effect in this first plan because arguments were structurally valid. B3 did not add blocking beyond B2 because the generated action proposals were placed after declared evidence. The private evaluator pipeline is integrated, but full task/conclusion success is not scoreable yet because the first proposal plan lacks natural-language final responses/handoff text.

## E4 next active task

Generate and evaluate a scoreable DEV proposal run.

Required work:

- [ ] generate DEV-only model proposals that include tool calls **and** natural-language final response/handoff text;
- [ ] include B1 pressure cases for malformed/invalid action arguments;
- [ ] include B3 pressure cases for premature action before evidence;
- [ ] rerun `scripts/research/e4_model_proposal_adapter.py`;
- [ ] rerun the private DEV evaluator combiner locally;
- [ ] preserve boundary metrics separately from task/conclusion success;
- [ ] report contained unsafe proposals separately from executed safety failures;
- [ ] decide whether B1/B2/B3 have enough DEV evidence to advance to VALIDATION;
- [ ] repeat eligible comparison on VALIDATION;
- [ ] promote/reject B1/B2/B3 components with evidence.

## Methodological constraint

No item in E2, E3 or the E4 smoke/model-proposal infrastructure is a demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts, splits and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment and cannot use LOCKED_TEST before final evaluation.
