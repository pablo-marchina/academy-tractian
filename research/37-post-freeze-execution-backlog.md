# Post-E0/E1 Execution Backlog — E2 Active

Status: **E0 + E1 FROZEN; E2 IN EXECUTION — Wave 2**

This file supersedes the pre-freeze task statuses in `research/06-research-backlog.md` for active execution. The older file is retained as historical planning evidence.

## Completed gates

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` semantics frozen.
- 16 scenarios / 17 tickets / 10 leakage groups frozen as grouping constraints.

## E2 active work

### Canonical ToolSpec / transport

- [x] executable ScenarioSchema v1 models;
- [x] 18-operation Canonical ToolSpec registry;
- [x] 5 action tools mapped to permission/impact/justification metadata;
- [x] runner-owned identity and seed boundary;
- [ ] mechanically verify registry metadata against frozen E0 operation evidence;
- [x] strict argument validation foundation;
- [x] deterministic resource/company policy guard foundation;
- [x] deterministic B0 HTTP transport adapter;
- [x] B0 seed binding limited to stochastic read operations;
- [ ] integrated B0 runner with trace emission and replay.

### Evaluation harness

- [x] deterministic evaluator result contract;
- [x] trajectory evaluator without exact reference-sequence matching;
- [x] decision evaluator;
- [x] policy evaluator;
- [x] action evaluator with accepted-event semantics;
- [x] evidence evaluator interface;
- [x] safety evaluator for identity/seed integrity;
- [x] structured argument evaluator;
- [x] structured conclusion/fact evaluator;
- [x] escalation/handoff evaluator;
- [x] deterministic action/evidence gate;
- [x] representative pass/fail evaluator fixtures;
- [ ] full integrated evaluator runner across representative scenario types.

### Trace/replay/provenance

- [x] TraceSchema v1 runtime models;
- [x] trace sequence/terminal invariants;
- [x] deterministic observation replay;
- [x] canonical configuration hashing;
- [x] run manifest hashing;
- [x] normalize volatile action IDs/timestamps for replay comparison;
- [ ] add explicit model proposal vs executed-argument trace events;
- [x] preserve seed/response-mode provenance outside model-visible arguments;
- [ ] full B0 capture → replay equivalence test.

### Real API verification

- [x] reproducible CEN-01 transport/conformance probe against supplied FastAPI handlers;
- [ ] run integrated B0 probe through repository harness;
- [ ] record full E2 test-suite environment/result;
- [ ] verify representative investigation/contextualization/execution fixture coverage.

## E3 unlock condition

E3 starts only when:

1. E2 contracts validate against representative scenarios;
2. B0 executes one complete reference scenario through the repository transport adapter;
3. B1/B2/B3 interfaces have deterministic fixtures;
4. traces can be replayed after volatile normalization;
5. evaluator outputs are stable on canonical pass/fail fixtures;
6. no new contract/gold inconsistency is discovered.

## Methodological constraint

No item in this backlog is a product demo. Any fake transport or handcrafted fixture exists only to validate instrumentation, contracts or evaluator behavior. Architecture and agent-quality claims require experiments against the supplied TRACTIAN environment.
