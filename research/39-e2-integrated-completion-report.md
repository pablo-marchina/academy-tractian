# E2 — Integrated Harness Completion Report

**Date:** 2026-08-16  
**Status:** COMPLETE — E3 UNLOCKED

E2 was completed as experimental infrastructure, not as an agent demo and not as an architecture selection.

## Delivered executable components

- ScenarioSchema v1 runtime models;
- 18-operation Canonical ToolSpec registry;
- explicit runner-owned identity and seed binding;
- explicit per-tool seed support derived from the supplied OpenAPI;
- B0 HTTP request/transport boundary;
- strict B1 argument validation;
- deterministic B2 permission/resource-scope policy;
- deterministic B3 evidence-aware action gate;
- integrated `HarnessRunner` with separate proposal/execution/result/observation trace events;
- deterministic live capture and replay;
- TraceSchema v1 invariants and volatile-value normalization;
- deterministic evaluator suite covering trajectory, decision, arguments, evidence, policy, action, conclusion, escalation/handoff and identity/seed safety;
- separate metrics for **contained unsafe proposals** and **uncontained/executed policy violations**;
- configuration/artifact provenance hashing;
- registry-vs-contract conformance checker;
- reproducible real-API CEN-01 transport/trace/replay probe script;
- GitHub Actions E2 unit/integration workflow.

## Validation evidence

### CI

The first CI execution was intentionally retained as evidence: it failed 3 tests and exposed a real metadata defect — action ToolSpecs were not marked resource-scoped — plus a fixture whose action target did not match the endpoint resource. The implementation/fixture were corrected rather than suppressing the tests.

Subsequent GitHub Actions runs on Python 3.13.15 completed successfully:

- **24 tests passed**;
- runtime: approximately **0.26 s**;
- deterministic runner/replay tests passed;
- B1/B2/B3 guard tests passed;
- evaluator tests passed;
- registry-conformance unit semantics passed;
- a blocked B3 proposal is recorded as `contained=true` and does not masquerade as an executed system-safety failure.

### Contract conformance against supplied artifact

An independent check against the uploaded TRACTIAN OpenAPI, using the frozen `camelCase -> snake_case` transformations, runner-bound `seed`, and synthetic canonical `body` parameter for request bodies, found:

- **18/18 operation IDs matched**;
- methods matched;
- route templates matched;
- canonical parameter tuples matched;
- **12** read operations support runner-bound seed;
- no registry/contract mismatch was observed.

The reproducible repository command is:

```bash
python scripts/research/e2_registry_conformance.py --partner-root /path/to/inteli-tractian-project
```

### Supplied API probe

The supplied FastAPI handlers were exercised with the supplied synthetic seed source for the CEN-01 reference transport path. The five steps returned HTTP 200 and the final escalation action returned `accepted=true`. Capture produced one replay observation per request. The repository probe routes this infrastructure check through `HarnessRunner`:

```bash
python scripts/research/e2_b0_real_api_probe.py --partner-root /path/to/inteli-tractian-project
```

This is a transport/trace/replay conformance check only. It is not evidence of agent quality.

## Methodological invariant

No test double, scripted reference path, fixture or transport probe in E2 is a demo. They validate instrumentation and experimental validity only. The project still has **no selected agent runtime, model, MCP topology, RAG design, multi-agent design, routing strategy, memory strategy or presentation UI**.

## E2 exit criteria

1. executable contracts: PASS;
2. runner-owned identity/seed: PASS;
3. B0 transport: PASS;
4. B1/B2/B3 deterministic boundaries: PASS;
5. trace/replay: PASS;
6. integrated evaluator suite: PASS;
7. canonical pass/fail fixtures: PASS;
8. registry conformance: PASS;
9. CI: PASS;
10. supplied API transport path: PASS.

**E3 is now unlocked.** Its only purpose is to freeze a leakage-aware development/validation/locked-test assignment before any model/runtime/prompt optimization begins.
