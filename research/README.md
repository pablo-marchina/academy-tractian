# Systematic Research Hub

**Status: E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 ACTIVE**  
**Date:** 2026-08-16

The project now has the updated TAPI, kickoff evidence, the actual TRACTIAN package, frozen contract/gold semantics, a validated framework-neutral experimental harness, a frozen leakage-aware benchmark split and a preregistered B0-B3 guarded-boundary experiment. Research has moved from generic architecture exploration to controlled, project-specific experimentation.

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
- explicit per-tool runner-bound seed support;
- runner-owned identity boundary;
- deterministic B0 HTTP transport;
- strict B1 argument validation;
- deterministic B2 permission/resource guard;
- evidence-aware B3 action gate;
- integrated `HarnessRunner` with separate proposal/call/result/observation events;
- TraceSchema v1 and deterministic trace invariants;
- live capture, replay and volatile trace normalization;
- configuration/artifact hashing;
- integrated deterministic evaluator suite;
- registry-vs-contract conformance tooling;
- reproducible real-API transport/trace/replay probe;
- GitHub Actions verification.

Validation evidence:

- **24 tests passed** on Python 3.13.15 in GitHub Actions;
- independent registry check matched all **18/18** operations, methods, paths and canonical parameters;
- **12** seed-capable reads confirmed from the supplied OpenAPI;
- supplied CEN-01 transport path returned 5/5 HTTP 200 with final escalation `accepted=true`.

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

Preregistered artifacts:

- `research/41-e4-guarded-boundary-experiment-preregistration.md`
- `research/42-e4-execution-start-report.md`
- `research/experiments/e4-b0-b3-experiment-manifest.json`
- `scripts/research/e4_validate_experiment_manifest.py`

E4 compares:

- **B0:** minimal benchmark-valid wrapper;
- **B1:** B0 + strict typed validation;
- **B2:** B1 + deterministic permission/resource guard;
- **B3:** B2 + evidence-aware action/escalation gate.

E4 uses DEV for debugging and VALIDATION for selection. LOCKED_TEST remains unavailable. Hard safety metrics are reported separately, and scripted/reference proposal sources remain infrastructure-only.

## Explicit non-decisions

No agent runtime, model, MCP topology, RAG stack, vector DB, multi-agent design, routing strategy, persistent-memory design, observability vendor or presentation UI has been selected.

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

`E0 freeze → E1 freeze → E2 complete → E3 split frozen → E4 B0–B3 → evidence/stopping → runtime/MCP → statistical pilot/model benchmark → conditional techniques → ADRs → FROZEN-v1`

## Important methodological rules

- Do not freeze a framework because implementation has started.
- Framework-neutral infrastructure may be implemented before architecture selection; architecture-changing choices require project-specific evidence and an ADR.
- Test doubles and scripted reference paths may validate instrumentation/transport/evaluators, but they are never evidence that the agent solves the task.
- The final demonstration is downstream of the experiments and must show measured behavior rather than hand-scripted success.
- Locked-test groups are off-limits for architecture/model/prompt/runtime selection.

If schedule pressure appears, cut optional complexity first. Do not weaken contract conformance, gold isolation, evaluator validity, split integrity or locked-test discipline.
