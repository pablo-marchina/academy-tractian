# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; **E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 ADAPTIVE TOOLSPEC LANGGRAPH EXECUTED**  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 10:12 BRT  
**Target final delivery:** 2026-09-08

This is the active execution plan after the real TRACTIAN package was audited. It separates frozen evidence/contracts from experimental architecture decisions and explicitly forbids demo-first development.

## 1. Current state

### Frozen / complete

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` and gold/evaluator boundary frozen.
- `BENCHMARK-SPLIT-v1` frozen before runtime/model/prompt/architecture selection.
- E2 framework-neutral ToolSpec/Trace/Replay/Evaluator harness complete.
- E4 B0-B3 guarded-boundary DEV+VALIDATION comparison complete.
- E5 evidence acquisition/stopping comparison executed.
- E6 runtime discriminating spike executed.
- E6 minimal LangGraph integration spike executed.
- E6 adaptive real ToolSpec/HarnessRunner LangGraph spike executed.

### Current candidate bundle

- **Boundary:** B3 guarded boundary.
- **Evidence/stopping:** evidence-sufficiency policy.
- **Runtime candidate:** LangGraph.
- **Baselines/comparators retained:** B0, free tool loop, fixed/reference-like anchor, Pydantic AI/Graph, OpenAI Agents SDK.

This is still not a final model/provider, MCP topology, RAG/vector DB, multi-agent, observability, memory, prompt or UI freeze.

## 2. Decision evidence so far

### E4 boundary decision

- **B0:** baseline only; rejected as deployment boundary due uncontained safety failures.
- **B1:** required validation sublayer; not sufficient alone.
- **B2:** required resource/permission sublayer.
- **B3:** current guarded-boundary candidate.

### E5 evidence/stopping decision

| Strategy | Scenarios | Task success | Premature stops | Unnecessary calls | Evidence coverage | Decision |
|---|---:|---:|---:|---:|---:|---|
| `fixed_reference_like` | 11 | 11 | 0 | 0 | 1.000 | Infrastructure/reference anchor only |
| `free_tool_loop` | 11 | 7 | 4 | 9 | 0.786 | Behavioral baseline, not preferred |
| `evidence_sufficiency_policy` | 11 | 10 | 1 | 2 | 0.964 | Current stopping candidate |

### E6 runtime scorecard

| Runtime | Weighted score | Decision |
|---|---:|---|
| LangGraph | 4.404 | Promote as current runtime candidate |
| Pydantic AI/Graph | 4.328 | Retain as typed/schema-native fallback and comparator |
| OpenAI Agents SDK | 4.188 | Retain as provider-native comparator |

### E6 minimal LangGraph integration spike

| Metric | Result |
|---|---:|
| LangGraph imported | true |
| Graph compiled | true |
| Graph invoked | true |
| Trace-compatible events | true |
| B3 external guard preserved | true |
| Evidence-sufficiency policy explicit | true |
| Deterministic replay equal | true |
| Checkpoint pause/resume roundtrip | true |
| Direct harness avg ms | 0.0076 |
| LangGraph avg ms | 9.2244 |

### E6 adaptive real ToolSpec/HarnessRunner spike

| Metric | Result |
|---|---:|
| Adaptive mode | true |
| ToolSpec registry wired | true |
| ToolSpec registry size | 18 |
| HarnessRunner used | true |
| B3 external guard preserved | true |
| Evidence-sufficiency policy explicit | true |
| RunTrace-compatible output | true |
| Representative scenarios | 4 |
| Splits used | DEV + VALIDATION |
| Adaptive path count | 3 |
| Required evidence coverage | 1.000 |
| Action execution proxy | 2/2 |
| Deterministic replay equal | true |
| Checkpoint pause/resume roundtrip | true |
| Direct HarnessRunner avg ms | 1.3582 |
| LangGraph avg ms | 20.3439 |
| Overhead ratio | 14.979 |

Decision: LangGraph advances to real DEV/VALIDATION integration implementation, with Pydantic AI/Graph and OpenAI Agents SDK retained as comparators. The adaptive spike is more realistic than the toy micro-spike because it uses the existing ToolSpec registry and HarnessRunner and chooses evidence tools from missing evidence requirements.

## 3. Non-negotiable integrity rules

- Raw partner artifacts remain immutable.
- `x-user-id` and evaluation `seed` are runner-bound, never model-selected.
- Related scenarios remain grouped by asset/storyline; no case-level random split.
- Locked-test groups are unavailable during architecture/model/prompt/runtime selection until the final locked evaluation gate.
- Reference trajectories are not exact-match gold unless an explicit policy requires ordering.
- Hard identity/schema/policy constraints remain deterministic where possible.
- Action success follows supplied `accepted_event_non_persistent` semantics; no invented final-state oracle.
- Optional complexity survives only if required or supported by experiment evidence.
- No demo-first development: test doubles and scripted paths validate infrastructure only.

## 4. Execution sequence

### E2 — COMPLETE

Completion report: `research/39-e2-integrated-completion-report.md`.

### E3 — COMPLETE

Frozen split:

- **DEV:** `asset_G501`, `asset_C710`, `asset_S420`, `asset_M208`, `asset_M101`.
- **VALIDATION:** `asset_B204`, `asset_M102`.
- **LOCKED_TEST:** `asset_V301`, `asset_M605`, `asset_M205`.

### E4 — VALIDATION COMPLETE

Reports:

- `research/45-e4-dev-scoreable-proposal-results.md`
- `research/46-e4-validation-boundary-results.md`

### E5 — EXECUTED

Artifacts:

- `research/47-e5-evidence-stopping-preregistration.md`
- `research/48-e5-evidence-stopping-results.md`
- `research/experiments/e5-evidence-stopping-experiment-manifest.json`
- `research/results/e5-evidence-stopping-summary-2026-08-16.json`
- `scripts/research/e5_evidence_stopping_runner.py`

### E6 — EXECUTED

Artifacts:

- `research/49-e6-runtime-spike-preregistration.md`
- `research/50-e6-runtime-spike-results-adr.md`
- `research/51-e6-langgraph-integration-spike-preregistration.md`
- `research/52-e6-langgraph-integration-spike-results.md`
- `research/53-e6-real-toolspec-langgraph-preregistration.md`
- `research/54-e6-real-toolspec-langgraph-results.md`
- `research/experiments/e6-runtime-spike-manifest.json`
- `research/experiments/e6-langgraph-integration-spike-manifest.json`
- `research/experiments/e6-real-toolspec-langgraph-manifest.json`
- `research/results/e6-runtime-spike-summary-2026-08-16.json`
- `research/results/e6-langgraph-integration-summary-2026-08-16.json`
- `research/results/e6-real-toolspec-langgraph-summary-2026-08-16.json`
- `scripts/research/e6_runtime_spike_runner.py`
- `scripts/research/e6_langgraph_integration_spike.py`
- `scripts/research/e6_langgraph_toolspec_runner.py`
- `scripts/research/e6_langgraph_toolspec_runner_v3.py`

### E6 real integration continuation — NEXT

- replace deterministic stub transport with live supplied API transport;
- connect model proposal generation without leaking evaluator-only gold;
- keep adaptive evidence planning;
- keep B3 and evidence-sufficiency deterministic;
- run representative DEV + VALIDATION scenarios end-to-end;
- measure task success, trace completeness and live latency;
- keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- keep LOCKED_TEST blocked.

### E7 — Native tools vs MCP

Expose the same ToolSpec through native tools and MCP v2 after the real integration continuation.

### E8 — Statistical pilot + model benchmark

Separate model/agent stochasticity at fixed observations from environment robustness across deterministic seeds/modes.

### E9 — Conditional techniques

Only test RAG/reranking, multi-agent, routing, persistent memory, prompt optimization or other complexity when residual failure analysis provides a concrete hypothesis.

## 5. Milestones

| Target | Gate |
|---|---|
| **16 Aug** | E0/E1/E2/E3 complete; E4 DEV+VALIDATION; E5; E6 runtime + minimal + adaptive ToolSpec LangGraph spikes |
| **17–20 Aug** | live API LangGraph integration + native/MCP discriminating setup |
| **21–22 Aug** | runtime/MCP ADRs + error analysis |
| **23–24 Aug** | statistical pilot preparation |
| **25 Aug** | statistical pilot/model screening |
| **26 Aug** | architecture candidates narrowed |
| **27 Aug** | target `FROZEN-v1` |
| **28 Aug–1 Sep** | selected architecture integrated |
| **2–5 Sep** | robustness/adversarial/reliability + locked test |
| **6–7 Sep** | documentation, reproducibility and demo rehearsal |
| **8 Sep** | final delivery/presentation |

## 6. Research Gate → `FROZEN-v1`

The architecture is frozen only after E0/E1/E3 freezes, B0-B3 DEV+VALIDATION evidence, evidence/stopping evidence, runtime and MCP ADRs, statistical pilot/model benchmark, conditional technique decisions and package inconsistency documentation.
