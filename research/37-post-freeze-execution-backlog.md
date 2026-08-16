# Post-E0/E1 Execution Backlog — E2 Active

Status: **E0 + E1 FROZEN; E2 IN EXECUTION**

This file supersedes the pre-freeze task statuses in `research/06-research-backlog.md` for active execution. The older file is retained as historical planning evidence.

## Completed gates

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` semantics frozen.
- 16 scenarios / 17 tickets / 10 leakage groups frozen as grouping constraints.

## E2 active work

### Canonical ToolSpec

- [x] executable ScenarioSchema v1 models;
- [x] 18-operation Canonical ToolSpec registry;
- [x] 5 action tools mapped to permission/impact/justification metadata;
- [x] runner-owned identity and seed boundary;
- [ ] generate ToolSpec directly from the frozen contract manifest and compare against registry;
- [x] strict argument validation foundation;
- [x] deterministic resource/company policy guard foundation;
- [ ] evidence-aware action/escalation policy interface.

### Evaluation harness

- [x] deterministic evaluator result contract;
- [x] trajectory evaluator without exact reference-sequence matching;
- [x] decision evaluator;
- [x] policy evaluator;
- [x] action evaluator with accepted-event semantics;
- [x] evidence evaluator interface;
- [x] safety evaluator for identity/seed integrity;
- [ ] structured argument evaluator;
- [ ] structured conclusion/fact evaluator;
- [ ] escalation/handoff evaluator;
- [ ] evaluator fixture suite with canonical pass/fail cases.

### Trace/replay/provenance

- [x] TraceSchema v1 runtime models;
- [x] trace sequence/terminal invariants;
- [x] deterministic observation replay;
- [x] canonical configuration hashing;
- [x] run manifest hashing;
- [ ] normalize volatile action IDs/timestamps for replay comparison;
- [ ] add model proposal vs executed-argument trace events;
- [ ] add seed/response-mode provenance events without exposing seed to the model.

## E3 unlock condition

E3 starts only when E2 contracts validate against representative scenarios, B0 can execute one complete scenario through a transport adapter, guard interfaces have deterministic fixtures, traces can be replayed and evaluator outputs are stable on handcrafted pass/fail cases.
