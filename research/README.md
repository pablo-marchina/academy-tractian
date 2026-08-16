# Systematic Research Hub

**Status: E0 + E1 FROZEN; E2 COMPLETE; E3 UNLOCKED**  
**Date:** 2026-08-16

The project now has the updated TAPI, kickoff evidence, the actual TRACTIAN package, frozen contract/gold semantics and a validated framework-neutral experimental harness. Research has moved from generic architecture exploration to controlled, project-specific experimentation.

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

## E2 — Complete executable harness

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

E2 intentionally selected **no** agent runtime, model, MCP topology, RAG stack, multi-agent design, routing strategy, persistent-memory design or observability vendor.

## E3 — Benchmark split freeze

E3 is the next gate. It must assign the frozen 10 asset/story groups to development, validation and locked test before any architecture/model/prompt optimization begins.

The split must be group-aware and coverage-aware, not ticket-random. It must preserve controlled variants inside their storyline group and explicitly document coverage compromises caused by the small number of independent groups.

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

`E0 freeze → E1 freeze → E2 complete → E3 leakage-aware split → B0–B3 → evidence/stopping → runtime/MCP → statistical pilot/model benchmark → conditional techniques → ADRs → FROZEN-v1`

## Important methodological rules

- Do not freeze a framework because implementation has started.
- Framework-neutral infrastructure may be implemented before architecture selection; architecture-changing choices require project-specific evidence and an ADR.
- Test doubles and scripted reference paths may validate instrumentation/transport/evaluators, but they are never evidence that the agent solves the task.
- The final demonstration is downstream of the experiments and must show measured behavior rather than hand-scripted success.

If schedule pressure appears, cut optional complexity first. Do not weaken contract conformance, gold isolation, evaluator validity, split integrity or locked-test discipline.
