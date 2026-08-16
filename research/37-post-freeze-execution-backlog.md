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

## E3 completion

Frozen assignment:

- [x] **DEV:** `asset_G501`, `asset_C710`, `asset_S420`, `asset_M208`, `asset_M101` — 5 groups / 8 scenarios;
- [x] **VALIDATION:** `asset_B204`, `asset_M102` — 2 groups / 3 scenarios;
- [x] **LOCKED_TEST:** `asset_V301`, `asset_M605`, `asset_M205` — 3 groups / 5 scenarios.

Completed work:

- [x] construct a group-level coverage matrix for contextualization / investigation / execution;
- [x] map action types, permission classes, response modes and uncertainty behaviors by group;
- [x] generate group assignment without splitting any storyline;
- [x] choose a split using explicit coverage objectives, not random ticket-level sampling;
- [x] document unavoidable coverage compromises caused by only 10 independent groups;
- [x] freeze `BENCHMARK-SPLIT-v1` public manifest;
- [x] add a programmatic leakage assertion;
- [x] make locked-test assignment unavailable to later architecture/model/prompt selection by policy.

Artifacts:

- `research/40-e3-benchmark-split-freeze-v1.md`
- `research/frozen/benchmark-split-v1.json`
- `scripts/research/e3_validate_split.py`

## E4 — active gate

Run the guarded-boundary experiment B0-B3 using DEV for development/debugging and VALIDATION for selection. Do not inspect or optimize against LOCKED_TEST.

Preregistered:

- [x] define the B0-B3 experiment manifest;
- [x] explicitly exclude B4 from the main E4 experiment;
- [x] encode DEV/VALIDATION-only policy;
- [x] encode LOCKED_TEST forbidden uses;
- [x] encode no-demo policy;
- [x] encode hard-safety metrics separately from quality metrics;
- [x] add manifest validation script;
- [x] add CI step for E4 manifest validation.

Next required work:

- [ ] bind DEV/VALIDATION groups into the runner without exposing locked-test gold;
- [ ] implement the first DEV-only E4 run harness;
- [ ] require every run to declare `proposal_source_class`;
- [ ] block LOCKED_TEST by construction in the run harness;
- [ ] run B0 minimal wrapper on DEV;
- [ ] run B1 strict typed validation on DEV;
- [ ] run B2 permission/resource guard on DEV;
- [ ] run B3 evidence-aware action/escalation on DEV;
- [ ] report contained unsafe proposals separately from executed safety failures;
- [ ] compute task/conclusion success, argument correctness, evidence coverage, action correctness and efficiency;
- [ ] repeat eligible comparison on VALIDATION for component promotion/rejection;
- [ ] promote/reject each boundary component by measured value.

## Methodological constraint

No item in E2, E3 or E4 preregistration is an agent demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts, splits and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment.
