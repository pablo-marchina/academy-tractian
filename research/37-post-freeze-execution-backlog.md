# Post-E0/E1 Execution Backlog — E6 Executed

Status: **E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 EXECUTED; LANGGRAPH INTEGRATION SPIKE NEXT**

This file supersedes the pre-freeze task statuses in `research/06-research-backlog.md` for active execution. The older file is retained as historical planning evidence.

## Completed gates

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` semantics frozen.
- 16 scenarios / 17 tickets / 10 leakage groups frozen as grouping constraints.
- E2 integrated framework-neutral harness complete.
- `BENCHMARK-SPLIT-v1` frozen before runtime/model/prompt/architecture selection.
- E4 B0-B3 guarded-boundary DEV+VALIDATION comparison complete.
- E5 evidence acquisition/stopping comparison complete.
- E6 runtime discriminating spike complete.

## E4 component decision

- **B0:** retain as baseline only; reject as deployment boundary due uncontained safety failures.
- **B1:** promote as a required validation sublayer; reject as sufficient standalone boundary.
- **B2:** promote as a required resource/permission sublayer based on DEV scope-safety evidence.
- **B3:** promote as the current guarded-boundary candidate for the next experimental stage.

## E5 decision

- `fixed_reference_like`: retain as infrastructure/reference anchor only;
- `free_tool_loop`: retain as behavioral baseline, not preferred;
- `evidence_sufficiency_policy`: promote as the current evidence-acquisition/stopping candidate.

## E6 completion

Completed work:

- [x] preregister E6 runtime spike;
- [x] compare LangGraph, Pydantic AI/Graph and OpenAI Agents SDK;
- [x] hold ToolSpec, B3 boundary, evidence-sufficiency policy, split policy and evaluator assumptions constant;
- [x] measure trace completeness, guard integration, pause/resume/HITL support, replay determinism, complexity, portability and overhead;
- [x] keep LOCKED_TEST blocked;
- [x] produce runtime ADR evidence;
- [x] avoid freezing model/MCP/RAG/multi-agent/UI.

E6 runtime scorecard:

| Runtime | Weighted score | Decision |
|---|---:|---|
| LangGraph | 4.404 | Promote as current runtime candidate |
| Pydantic AI/Graph | 4.328 | Retain as typed/schema-native fallback and comparator |
| OpenAI Agents SDK | 4.188 | Retain as provider-native comparator |

Decision:

- **LangGraph:** promote as current runtime candidate for the next integration stage.
- **Pydantic AI/Graph:** keep as fallback/comparator because of strong typed schema/eval fit.
- **OpenAI Agents SDK:** keep as provider-native comparator and revisit if the model/provider later becomes OpenAI-centered.

Artifacts:

- `research/49-e6-runtime-spike-preregistration.md`
- `research/50-e6-runtime-spike-results-adr.md`
- `research/experiments/e6-runtime-spike-manifest.json`
- `research/results/e6-runtime-spike-summary-2026-08-16.json`
- `scripts/research/e6_runtime_spike_runner.py`

## Current candidate policy/runtime bundle

- B3 guarded boundary.
- Evidence-sufficiency/stopping policy.
- LangGraph as current runtime candidate.
- B0/free loop/fixed reference retained as baselines or infrastructure anchors.

Still not frozen:

- model/provider;
- MCP topology;
- RAG/vector DB;
- multi-agent decomposition;
- persistent memory;
- observability backend;
- UI/demo flow.

## Next active task

Implementation-grade LangGraph integration spike.

Required work:

- [ ] implement minimal LangGraph graph around the existing ToolSpec;
- [ ] keep B3 boundary external and deterministic;
- [ ] keep evidence-sufficiency policy explicit;
- [ ] emit TraceSchema-compatible events;
- [ ] test checkpoint/replay/pause-resume behavior;
- [ ] compare overhead against the current harness;
- [ ] keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- [ ] keep LOCKED_TEST blocked;
- [ ] do not freeze model/MCP/UI yet.

## Methodological constraint

No item in E2, E3, E4, E5 or E6 is a demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts, splits and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment and cannot use LOCKED_TEST before final evaluation.
