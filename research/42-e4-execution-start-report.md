# E4 — Execution Start Report

**Date:** 2026-08-16  
**Status:** ACTIVE / FIRST-DEV-MODEL-PROPOSAL-RUN-COMPLETE  
**Scope:** DEV + VALIDATION only; `LOCKED_TEST` blocked

E4 has started with a preregistered B0-B3 manifest, CI-level validation, a DEV-only runner smoke execution and the first DEV model-proposal boundary run. This report records the transition from E3 split freeze to E4 controlled execution.

## What was executed

Created:

- `research/41-e4-guarded-boundary-experiment-preregistration.md`
- `research/experiments/e4-b0-b3-experiment-manifest.json`
- `research/experiments/e4-dev-model-proposal-plan-gpt-5-5-thinking-2026-08-16.json`
- `research/results/e4-dev-model-proposal-boundary-summary-2026-08-16.json`
- `research/43-e4-first-dev-model-proposal-results.md`
- `scripts/research/e4_validate_experiment_manifest.py`
- `scripts/research/e4_dev_runner.py`
- `scripts/research/e4_model_proposal_adapter.py`
- `research/e4/tests/test_dev_runner.py`
- `research/e4/tests/test_model_proposal_adapter.py`

Updated:

- `.github/workflows/research-e2.yml`

The workflow now validates:

1. E2 unit suite;
2. E4 DEV runner tests;
3. E3 frozen split;
4. E4 experiment manifest;
5. E4 DEV runner smoke execution;
6. E4 DEV model-proposal adapter execution;
7. E4 DEV model-proposal metric artifact upload.

Latest green CI run:

- E2 suite: 24 passed;
- E4 DEV/model-proposal tests: passed;
- E3 split validator: PASS;
- E4 experiment manifest validator: PASS;
- E4 DEV smoke execution: success;
- E4 DEV model-proposal adapter: success;
- artifact uploaded: `e4-dev-model-proposal-boundary`.

## DEV-only runner behavior

The E4 DEV runner:

- loads `BENCHMARK-SPLIT-v1`;
- permits only `DEV` in this debug runner;
- rejects `LOCKED_TEST` at runtime;
- rejects `VALIDATION` in the DEV-only runner so selection cannot be mixed with debugging;
- requires explicit `proposal_source_class`;
- marks `scripted_reference` and `scripted_fixture` as `infrastructure_only` and `agent_quality_evidence=false`;
- executes B0/B1/B2/B3 variants through the framework-neutral `HarnessRunner`;
- exports per-variant metrics as JSON;
- records contained unsafe proposals separately from uncontained/executed safety failures.

## Model-proposal adapter behavior

The E4 model-proposal adapter:

- consumes a recorded proposal plan;
- requires `proposal_source_class=model_agent`;
- requires provider/model identity;
- rejects `LOCKED_TEST`;
- rejects non-DEV groups;
- binds identity/seed through the runner;
- runs B0/B1/B2/B3 on DEV;
- exports per-variant boundary metrics;
- does not call an LLM provider itself;
- does not load evaluator-only gold.

## First DEV model-proposal boundary result

First plan: `research/experiments/e4-dev-model-proposal-plan-gpt-5-5-thinking-2026-08-16.json`  
Result summary: `research/results/e4-dev-model-proposal-boundary-summary-2026-08-16.json`  
Detailed report: `research/43-e4-first-dev-model-proposal-results.md`

Aggregate boundary metrics:

| Variant | Proposals | Executed calls | Blocked calls | Permission/scope executions | Contained unsafe proposals | Uncontained safety failures |
|---|---:|---:|---:|---:|---:|---:|
| B0 | 27 | 27 | 0 | 1 | 0 | 1 |
| B1 | 27 | 27 | 0 | 1 | 0 | 1 |
| B2 | 27 | 26 | 1 | 0 | 1 | 0 |
| B3 | 27 | 26 | 1 | 0 | 1 | 0 |

Interpretation: B2 contained one unsafe permission/resource-scope model proposal that B0/B1 would execute. B1 had no effect in this first plan because the generated arguments were structurally valid. B3 did not add blocking beyond B2 because actions were proposed after declared evidence.

## E4 scope

The experiment compares:

| Variant | Meaning |
|---|---|
| B0 | minimal benchmark-valid wrapper |
| B1 | B0 + strict typed validation |
| B2 | B1 + deterministic permission/resource guard |
| B3 | B2 + evidence-aware action/escalation gate |

B4 confirmation remains outside the main experiment.

## Locked-test protection

`LOCKED_TEST` remains unavailable for:

- prompt tuning;
- model selection;
- runtime selection;
- agent policy debugging;
- architecture ablation;
- threshold fitting;
- optimizer feedback.

Allowed E4 splits are:

- DEV for debugging;
- VALIDATION for selection after DEV harness and proposal source are ready.

## Non-demo protection

The manifest, runner and adapter explicitly reject demo-first development:

- scripted reference paths are not agent-quality evidence;
- test doubles are not agent-quality evidence;
- boundary metrics do not equal task/conclusion success;
- hard safety is reported separately from quality metrics;
- contained unsafe proposals are not treated as executed safety failures, but remain visible as agent-layer failures.

## Next executable step

The next E4 task is to combine the DEV model-proposal traces with the private DEV evaluator:

```text
E4 DEV private evaluator integration
├── use only DEV normalized gold locally
├── keep evaluator-only gold out of the public repo
├── combine boundary metrics with task/conclusion success
├── preserve contained-vs-uncontained safety metrics
├── keep LOCKED_TEST blocked
└── decide whether B1/B2/B3 should advance to VALIDATION
```

No runtime/prompt/architecture decision is allowed until DEV results are evaluated and then checked on VALIDATION.
