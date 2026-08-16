# Systematic Research Hub

**Status: E0 + E1 FROZEN; E2 ACTIVE — Wave 2**  
**Date:** 2026-08-16

The project now has the updated TAPI, kickoff evidence and the actual TRACTIAN package. Research has moved from generic architecture exploration to controlled, project-specific experimentation.

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

## E2 — Active executable harness

`research/e2/` now contains framework-neutral contracts and testable infrastructure:

- executable ScenarioSchema v1 models;
- 18-operation Canonical ToolSpec registry;
- runner-owned identity/seed binding;
- deterministic B0 HTTP transport;
- TraceSchema v1 and deterministic trace invariants;
- observation replay and volatile trace normalization;
- configuration/artifact hashing;
- deterministic B1/B2 foundations;
- evidence-aware B3 action gate;
- structured argument, conclusion/fact and escalation/handoff evaluators;
- deterministic pass/fail fixtures.

A reproducible CEN-01 real-API transport/conformance probe lives at `scripts/research/e2_b0_real_api_probe.py`. It validates infrastructure only; it is not a demo and is not evidence of agent quality.

E2 intentionally does **not** choose the agent runtime, model, MCP, RAG, multi-agent design, routing or observability vendor.

Execution reports:

- `research/36-e2-execution-report.md`
- `research/38-e2-wave-2-execution-report.md`

Active backlog: `research/37-post-freeze-execution-backlog.md`

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

`E0 freeze → E1 freeze → E2 integrated runner → E3 leakage-aware split → B0–B3 → evidence/stopping → runtime/MCP → statistical pilot/model benchmark → conditional techniques → ADRs → FROZEN-v1`

## Important methodological rules

- Do not freeze a framework because implementation has started.
- Framework-neutral infrastructure can be built now; architecture-changing choices require project-specific evidence and an ADR.
- Test doubles and scripted reference paths may validate instrumentation/transport/evaluators, but they are never evidence that the agent solves the task.
- The final demonstration is downstream of the experiments and must show measured behavior rather than hand-scripted success.

If schedule pressure appears, cut optional complexity first. Do not weaken contract conformance, gold isolation, evaluator validity, split integrity or locked-test discipline.
