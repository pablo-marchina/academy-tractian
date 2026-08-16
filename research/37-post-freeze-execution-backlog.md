# Post-E0/E1 Execution Backlog — E5 Executed

Status: **E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 NEXT**

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

## E4 component decision

- **B0:** retain as baseline only; reject as deployment boundary due uncontained safety failures.
- **B1:** promote as a required validation sublayer; reject as sufficient standalone boundary.
- **B2:** promote as a required resource/permission sublayer based on DEV scope-safety evidence.
- **B3:** promote as the current guarded-boundary candidate for the next experimental stage.

## E5 completion

Completed work:

- [x] preregister E5 evidence/stopping experiment;
- [x] use B3 as current guarded-boundary candidate;
- [x] keep B0 as baseline where useful;
- [x] compare fixed/reference-like investigation, free tool loop and evidence-sufficiency/stopping policy;
- [x] measure premature stopping, unnecessary calls, task success, escalation correctness and efficiency;
- [x] keep LOCKED_TEST blocked;
- [x] run the E5 evidence/stopping runner in CI;
- [x] record a public aggregate summary without freezing runtime/model/MCP/UI.

E5 result:

| Strategy | Scenarios | Task success | Premature stops | Unnecessary calls | Total calls | Required evidence coverage | Agent-quality evidence? |
|---|---:|---:|---:|---:|---:|---:|---|
| `fixed_reference_like` | 11 | 11 | 0 | 0 | 36 | 1.000 | No |
| `free_tool_loop` | 11 | 7 | 4 | 9 | 36 | 0.786 | Yes |
| `evidence_sufficiency_policy` | 11 | 10 | 1 | 2 | 35 | 0.964 | Yes |

Delta of `evidence_sufficiency_policy` vs `free_tool_loop`:

- task success: +3;
- premature stopping: -3;
- unnecessary calls: -7;
- total tool calls: -1.

E5 decision:

- `fixed_reference_like`: retain as infrastructure/reference anchor only;
- `free_tool_loop`: retain as behavioral baseline, not preferred;
- `evidence_sufficiency_policy`: promote as the current evidence-acquisition/stopping candidate.

Artifacts:

- `research/47-e5-evidence-stopping-preregistration.md`
- `research/48-e5-evidence-stopping-results.md`
- `research/experiments/e5-evidence-stopping-experiment-manifest.json`
- `research/results/e5-evidence-stopping-summary-2026-08-16.json`
- `scripts/research/e5_evidence_stopping_runner.py`

## Current candidate policy bundle

- B3 guarded boundary.
- Evidence-sufficiency/stopping policy.
- B0 and free tool loop retained as baselines where useful.
- Fixed/reference-like strategy retained only as infrastructure/reference anchor.

This is not an architecture/runtime/model freeze.

## E6 next active task

Move to runtime discriminating spike only after holding the policy bundle constant.

Required work:

- [ ] preregister E6 runtime spike;
- [ ] compare LangGraph, Pydantic AI/Graph and OpenAI Agents SDK;
- [ ] hold ToolSpec, B3 boundary, evidence-sufficiency policy, split policy and evaluator assumptions constant;
- [ ] measure trace completeness, guard integration, pause/resume/HITL support, replay determinism, complexity, portability and overhead;
- [ ] keep LOCKED_TEST blocked;
- [ ] produce runtime ADR evidence;
- [ ] do not freeze model/MCP/UI yet.

## Methodological constraint

No item in E2, E3, E4 or E5 is a demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts, splits and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment and cannot use LOCKED_TEST before final evaluation.
