# Post-E0/E1 Execution Backlog — E2 Complete, E3 Next

Status: **E0 + E1 FROZEN; E2 COMPLETE; E3 UNLOCKED**

This file supersedes the pre-freeze task statuses in `research/06-research-backlog.md` for active execution. The older file is retained as historical planning evidence.

## Completed gates

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` semantics frozen.
- 16 scenarios / 17 tickets / 10 leakage groups frozen as grouping constraints.
- E2 integrated framework-neutral harness complete.

## E2 completion

### Canonical ToolSpec / transport

- [x] executable ScenarioSchema v1 models;
- [x] 18-operation Canonical ToolSpec registry;
- [x] 5 action tools mapped to permission/impact/justification metadata;
- [x] action tools explicitly marked resource-scoped;
- [x] runner-owned identity and seed boundary;
- [x] mechanically verify registry metadata against supplied/frozen E0 operation evidence;
- [x] explicit per-tool seed support;
- [x] strict argument validation foundation;
- [x] deterministic resource/company policy guard foundation;
- [x] deterministic B0 HTTP transport adapter;
- [x] integrated B0 runner with trace emission and replay.

### Evaluation harness

- [x] deterministic evaluator result contract;
- [x] trajectory evaluator without exact reference-sequence matching;
- [x] decision evaluator;
- [x] policy evaluator separating contained unsafe proposals from uncontained/executed violations;
- [x] action evaluator with accepted-event semantics;
- [x] evidence evaluator interface;
- [x] safety evaluator for identity/seed integrity;
- [x] structured argument evaluator;
- [x] structured conclusion/fact evaluator;
- [x] escalation/handoff evaluator;
- [x] deterministic action/evidence gate;
- [x] integrated evaluator suite;
- [x] representative pass/fail fixtures.

### Trace/replay/provenance

- [x] TraceSchema v1 runtime models;
- [x] trace sequence/terminal invariants;
- [x] separate tool proposal vs executed call events;
- [x] deterministic live capture and observation replay;
- [x] canonical configuration hashing;
- [x] run manifest hashing;
- [x] normalize volatile action IDs/timestamps for replay comparison;
- [x] preserve seed provenance outside model-visible arguments;
- [x] B0 live-capture/replay equivalence fixture.

### Validation

- [x] GitHub Actions E2 workflow;
- [x] **24 tests passed** on Python 3.13.15 in the latest integrated safety-semantics run;
- [x] initial failing CI exposed a real action-scope metadata defect; defect fixed and rerun green;
- [x] independent OpenAPI registry check: 18/18 operations, methods, paths and canonical parameters matched;
- [x] 12 read operations independently confirmed seed-capable;
- [x] supplied CEN-01 API transport path: 5/5 HTTP 200, final escalation `accepted=true`, one replay record per request;
- [x] reproducible repository commands retained for registry and real-API conformance.

Completion report: `research/39-e2-integrated-completion-report.md`.

## E3 — next active gate

Freeze `DEV / VALIDATION / LOCKED_TEST` across the already frozen 10 asset/story groups before any model/runtime/prompt optimization.

Required work:

- [ ] construct a group-level coverage matrix for contextualization / investigation / execution;
- [ ] map action types, permission classes, response modes and uncertainty behaviors by group;
- [ ] generate candidate group assignments without splitting any storyline;
- [ ] choose a split using explicit coverage objectives, not random ticket-level sampling;
- [ ] document unavoidable coverage compromises caused by only 10 independent groups;
- [ ] freeze `BENCHMARK-SPLIT-v1` + SHA-256 manifest;
- [ ] add a programmatic leakage assertion;
- [ ] make locked-test assignment unavailable to later architecture/model/prompt selection code.

## Methodological constraint

No item in E2 was an agent demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment.
