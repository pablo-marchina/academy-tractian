# Post-E0/E1 Execution Backlog — E2 Active

Status: **E0 + E1 FROZEN; E2 IN EXECUTION**

This file supersedes the pre-freeze task statuses in `research/06-research-backlog.md` for the active execution sequence. The older file is retained as historical research planning evidence.

## Completed gates

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` semantics frozen.
- 16 scenarios / 17 tickets / 10 leakage groups frozen as grouping constraints.
- Partner scenario audit incorporated as source evidence.

## E2 active work

### E2.1 Canonical ToolSpec

- [x] Executable ScenarioSchema v1 models.
- [x] 18-operation Canonical ToolSpec registry.
- [x] 5 action tools mapped to permission/impact/justification metadata.
- [x] Runner-owned identity and seed boundary.
- [ ] Generate ToolSpec directly from the frozen contract manifest and compare against registry.
- [ ] Add strict argument validation implementation for B1.
- [ ] Add deterministic resource/company policy guard for B2.
- [ ] Add evidence-aware action/escalation policy interface for B3.

### E2.2 Evaluation harness

- [x] Deterministic evaluator result contract.
- [x] Trajectory evaluator using required/forbidden calls rather than exact reference sequence.
- [x] Decision evaluator.
- [x] Policy evaluator.
- [x] Action evaluator with accepted-event semantics.
- [x] Evidence evaluator interface.
- [x] Safety evaluator for identity/seed integrity.
- [ ] Structured argument evaluator.
- [ ] Structured conclusion/fact evaluator.
- [ ] Escalation/handoff evaluator.
- [ ] Evaluator fixture suite covering canonical pass/fail cases.

### E2.3 Trace/replay/provenance

- [x] TraceSchema v1 runtime models.
- [x] Trace sequence/terminal invariants.
- [x] Deterministic observation replay store.
- [x] Canonical configuration hashing.
- [x] Run manifest hashing.
- [ ] Normalize volatile action IDs and timestamps for replay comparison.
- [ ] Add model/tool proposal vs executed-argument trace events.
- [ ] Add seed/response-mode provenance events without exposing seed as a model argument.

## E3 unlock condition

E3 can start only when:

1. all E2 contracts validate against representative scenarios;
2. B0 can execute one full scenario end-to-end through a transport adapter;
3. B1/B2/B3 guard interfaces have deterministic fixtures;
4. traces can be replayed and compared;
5. evaluator outputs are stable on handcrafted pass/fail cases.

E3 then freezes the actual dev/validation/locked-test assignment across the 10 already-frozen asset/story groups.
