# E4 — Execution Start Report

**Date:** 2026-08-16  
**Status:** ACTIVE / MODEL-PROPOSAL-ADAPTER-GREEN  
**Scope:** DEV + VALIDATION only; `LOCKED_TEST` blocked

E4 has started with a preregistered B0-B3 manifest, CI-level validation, a DEV-only runner smoke execution and a DEV-only model-proposal adapter. This report records the transition from E3 split freeze to E4 controlled execution.

## What was executed

Created:

- `research/41-e4-guarded-boundary-experiment-preregistration.md`
- `research/experiments/e4-b0-b3-experiment-manifest.json`
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
3. E4 model-proposal adapter tests;
4. E3 frozen split;
5. E4 experiment manifest;
6. E4 DEV runner smoke execution.

Latest green CI run:

- E2 suite: 24 passed;
- E4 test suite: DEV runner + model-proposal adapter tests passed;
- E3 split validator: PASS;
- E4 experiment manifest validator: PASS;
- E4 DEV smoke execution: success.

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

- consumes a recorded model/agent proposal plan;
- requires `proposal_source_class=model_agent`;
- requires a non-scripted provider/model identity in the proposal plan;
- loads only public `BENCHMARK-SPLIT-v1` metadata;
- permits only DEV in the adapter;
- rejects `LOCKED_TEST` and non-DEV groups by construction;
- uses runner-bound identity and seed;
- runs B0/B1/B2/B3 over the same model proposal stream;
- exports per-variant boundary metrics;
- reports `agent_quality_evidence=true` but `task_success_evidence=false` because private evaluator-only gold is not loaded by this adapter.

This distinction is intentional. The adapter can now evaluate whether B1/B2/B3 contain unsafe model proposals on DEV, but task/conclusion success still requires the private DEV evaluator path.

## E4 scope

The experiment compares:

| Variant | Meaning |
|---|---|
| B0 | minimal benchmark-valid wrapper |
| B1 | B0 + strict typed validation |
| B2 | B1 + deterministic permission/resource guard |
| B3 | B2 + evidence-aware action/escalation gate |

B4 confirmation remains outside the main experiment.

## Smoke-run interpretation

The current DEV runner smoke uses a deterministic scripted/reference proposal source. Therefore:

- it validates execution plumbing, split blocking, metric export and guard behavior;
- it is not agent-quality evidence;
- it cannot select a runtime/model/prompt/architecture;
- it does not access evaluator-only gold;
- it does not use `LOCKED_TEST`.

Expected smoke progression:

- B0 executes invalid/cross-company/premature risky actions because it has no B1/B2/B3 guard;
- B1 blocks invalid arguments;
- B2 blocks cross-company/resource violations;
- B3 blocks premature action before required evidence and allows the valid action after evidence.

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
- VALIDATION for selection after DEV harness and model proposal source are ready.

## Non-demo protection

The manifest, runner and adapter explicitly reject demo-first development:

- scripted reference paths are not agent-quality evidence;
- test doubles are not agent-quality evidence;
- quality claims require a non-demo proposal source;
- hard safety is reported separately from quality metrics;
- contained unsafe proposals are not treated as executed safety failures, but remain visible as agent-layer failures;
- boundary metrics are not silently promoted to full task success.

## Next executable step

The next E4 task is to connect the first actual DEV model/agent proposal generator to produce a proposal plan compatible with `scripts/research/e4_model_proposal_adapter.py`:

```text
E4 DEV model-proposal generation
├── consume only DEV cases
├── keep LOCKED_TEST blocked by construction
├── bind identity/seed through runner
├── emit proposal_source_class=model_agent
├── write recorded proposal plan
├── run e4_model_proposal_adapter.py
├── export boundary metrics by B0/B1/B2/B3
└── then combine with private DEV evaluator for task/conclusion success
```

No runtime/prompt/architecture decision is allowed until non-demo DEV evidence exists and is then checked on VALIDATION.
