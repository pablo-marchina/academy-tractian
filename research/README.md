# Systematic Research Hub

**Status: E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 ACTIVE**  
**Date:** 2026-08-16

The project now has the updated TAPI, kickoff evidence, the actual TRACTIAN package, frozen contract/gold semantics, a validated framework-neutral experimental harness, a frozen leakage-aware benchmark split and the first DEV model-proposal boundary run.

## Frozen evidence/contracts

### E0 — Contract

- `research/34-e0-contract-freeze-v1.md`
- `research/frozen/e0-contract-freeze.manifest.json`
- `research/frozen/API-BEHAVIOR-MAP-v1.json`

Frozen facts include 18 operations / 17 path templates, the duplicate `/assets/{assetId}` GET+PATCH mapping, explicit `camelCase → snake_case` canonical argument transformation, runner-bound identity/seed and accepted-event/non-persistent action semantics.

### E1 — Gold / ScenarioSchema

- `research/35-e1-gold-freeze-v1.md`
- `research/frozen/e1-gold-freeze.manifest.json`

Frozen benchmark structure: 16 narrative scenarios, 17 tickets and 10 asset/story groups. Machine trajectories are references, not scripts. Gold remains evaluator-only and is not copied into agent context.

### E2 — Executable harness

`research/e2/` contains framework-neutral contracts and validated experimental infrastructure:

- executable ScenarioSchema v1 models;
- 18-operation Canonical ToolSpec registry;
- runner-owned identity/seed binding;
- B0 HTTP transport;
- strict B1 argument validation;
- deterministic B2 permission/resource guard;
- evidence-aware B3 action gate;
- integrated `HarnessRunner`;
- TraceSchema v1 and deterministic replay;
- integrated deterministic evaluator suite.

Completion report: `research/39-e2-integrated-completion-report.md`.

### E3 — Benchmark split

Frozen split artifacts:

- `research/40-e3-benchmark-split-freeze-v1.md`
- `research/frozen/benchmark-split-v1.json`
- `scripts/research/e3_validate_split.py`

Assignment:

- **DEV:** `asset_G501`, `asset_C710`, `asset_S420`, `asset_M208`, `asset_M101` — 5 groups / 8 scenarios.
- **VALIDATION:** `asset_B204`, `asset_M102` — 2 groups / 3 scenarios.
- **LOCKED_TEST:** `asset_V301`, `asset_M605`, `asset_M205` — 3 groups / 5 scenarios.

The split is group-level, coverage-aware and locked before any runtime/model/prompt/architecture optimization. Locked-test groups may be used only for metadata counting, coverage inspection and leakage assertions until final evaluation.

### E4 — Guarded-boundary experiment

Active artifacts:

- `research/41-e4-guarded-boundary-experiment-preregistration.md`
- `research/42-e4-execution-start-report.md`
- `research/43-e4-first-dev-model-proposal-results.md`
- `research/experiments/e4-b0-b3-experiment-manifest.json`
- `research/experiments/e4-dev-model-proposal-plan-gpt-5-5-thinking-2026-08-16.json`
- `research/results/e4-dev-model-proposal-boundary-summary-2026-08-16.json`
- `scripts/research/e4_validate_experiment_manifest.py`
- `scripts/research/e4_dev_runner.py`
- `scripts/research/e4_model_proposal_adapter.py`

First DEV model-proposal boundary result:

| Variant | Proposals | Executed calls | Blocked calls | Permission/scope executions | Contained unsafe proposals | Uncontained safety failures |
|---|---:|---:|---:|---:|---:|---:|
| B0 | 27 | 27 | 0 | 1 | 0 | 1 |
| B1 | 27 | 27 | 0 | 1 | 0 | 1 |
| B2 | 27 | 26 | 1 | 0 | 1 | 0 |
| B3 | 27 | 26 | 1 | 0 | 1 | 0 |

Interpretation: B2 contained one permission/resource-scope unsafe model proposal that B0/B1 would execute. B1 had no effect in this first plan because arguments were structurally valid. B3 did not add blocking beyond B2 because action proposals were placed after declared evidence requirements.

This is boundary evidence only. Full task/conclusion success requires the private DEV evaluator and cannot expose evaluator-only gold in the public repository.

## Explicit non-decisions

No agent runtime, model provider selection, MCP topology, RAG stack, vector DB, multi-agent design, routing strategy, persistent-memory design, observability vendor or presentation UI has been selected.

## Source hierarchy

1. Updated TAPI / written Student Guide / explicit partner requirements.
2. Executable supplied API behavior/source.
3. Raw OpenAPI and supplied agent/eval/data artifacts.
4. Kickoff guidance when not contradicted by delivered artifacts.
5. Primary research and official framework documentation.
6. Reproducible project experiments.
7. Hypotheses.

## Central hypothesis

> **Does a guarded, contract-aware tool boundary materially improve argument correctness and safety over a minimally wrapped baseline while preserving task success and acceptable efficiency?**

Variants B0–B3 are the core attribution experiment; B4 confirmation remains a separate safety extension unless partner policy changes.

## Critical path

`E0 freeze → E1 freeze → E2 complete → E3 split frozen → B0–B3 boundary evidence → private DEV evaluator → VALIDATION → evidence/stopping → runtime/MCP → statistical pilot/model benchmark → conditional techniques → ADRs → FROZEN-v1`

## Important methodological rules

- Do not freeze a framework because implementation has started.
- Framework-neutral infrastructure may be implemented before architecture selection; architecture-changing choices require project-specific evidence and an ADR.
- Boundary metrics do not equal task/conclusion success.
- Test doubles and scripted reference paths may validate instrumentation/transport/evaluators, but they are never evidence that the agent solves the task.
- The final demonstration is downstream of the experiments and must show measured behavior rather than hand-scripted success.
- Locked-test groups are off-limits for architecture/model/prompt/runtime selection.

If schedule pressure appears, cut optional complexity first. Do not weaken contract conformance, gold isolation, evaluator validity, split integrity or locked-test discipline.
