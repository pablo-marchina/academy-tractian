# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; **E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 NATIVE TOOLS VS MCP PASS**  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 11:27 BRT  
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
- E6 live API integration implementation path and CI contract gate complete.
- E6 local live API execution passed against the supplied TRACTIAN API.
- E7 native tools vs MCP-compatible surface comparison passed.

### Current candidate bundle

- **Boundary:** B3 guarded boundary.
- **Evidence/stopping:** evidence-sufficiency policy.
- **Runtime candidate:** LangGraph.
- **Transport path:** `HttpxTransport` against the supplied TRACTIAN API, live execution passed locally.
- **Internal tool surface candidate:** native ToolSpec calls.
- **External interoperability surface candidate:** MCP-compatible `tools/list` + `tools/call` adapter.
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

### E6 runtime/live decision

| Gate | Result |
|---|---:|
| Runtime scorecard winner | LangGraph |
| Adaptive ToolSpec/HarnessRunner graph | pass |
| Live API status | `LIVE_PASS` |
| Live request count | 37 |
| Live success rate | 1.000 |
| Action execution proxy | 4/4 |
| RunTrace-compatible output | true |
| LOCKED_TEST accessed | false |

Decision: promote LangGraph + adaptive evidence planning + B3 + HarnessRunner + `HttpxTransport` as the current live integration candidate. This is still not a final architecture freeze.

### E7 native tools vs MCP-compatible surface

| Metric | Native tools | MCP-compatible |
|---|---:|---:|
| Tool coverage | 18 | 18 |
| Representative scenarios | 4 | 4 |
| Splits | DEV + VALIDATION | DEV + VALIDATION |
| Request count | 18 | 18 |
| Successful request count | 18 | 18 |
| Trace complete | true | true |
| RunTrace-compatible output | true | true |
| B3 policy events | 2 | 2 |
| B3 allows actions | true | true |
| Evidence-sufficiency events | 4 | 4 |
| Action execution proxy | 2/2 | 2/2 |
| Avg latency ms | 1.9855 | 1.8158 |
| Complexity proxy | 1.0 | 2.0 |
| Portability proxy | 3.0 | 4.5 |

Comparison result: schema equivalence, invocation equivalence, guard-fidelity equivalence and trace-completeness equivalence all passed. Native remains the lower-complexity internal candidate. MCP-compatible remains the external interoperability candidate. MCP topology is not frozen.

## 3. Non-negotiable integrity rules

- Raw partner artifacts remain immutable.
- `x-user-id` and evaluation `seed` are runner-bound, never model-selected.
- Related scenarios remain grouped by asset/storyline; no case-level random split.
- Locked-test groups are unavailable during architecture/model/prompt/runtime selection until the final locked evaluation gate.
- Reference trajectories are not exact-match gold unless an explicit policy requires ordering.
- Hard identity/schema/policy constraints remain deterministic where possible.
- Action success follows supplied `accepted_event_non_persistent` semantics; no invented final-state oracle.
- Optional complexity survives only if required or supported by experiment evidence.
- No demo-first development: test doubles and scripted paths validate instrumentation, contracts, splits and evaluator behavior only.

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

Reports:

- `research/47-e5-evidence-stopping-preregistration.md`
- `research/48-e5-evidence-stopping-results.md`

### E6 — LIVE PASS

Reports:

- `research/49-e6-runtime-spike-preregistration.md`
- `research/50-e6-runtime-spike-results-adr.md`
- `research/51-e6-langgraph-integration-spike-preregistration.md`
- `research/52-e6-langgraph-integration-spike-results.md`
- `research/53-e6-real-toolspec-langgraph-preregistration.md`
- `research/54-e6-real-toolspec-langgraph-results.md`
- `research/55-e6-live-api-integration-contract-results.md`
- `research/56-e6-live-api-integration-live-results.md`

### E7 — NATIVE TOOLS VS MCP PASS

Artifacts:

- `research/57-e7-native-tools-vs-mcp-preregistration.md`
- `research/58-e7-native-tools-vs-mcp-results.md`
- `research/experiments/e7-native-tools-vs-mcp-manifest.json`
- `research/results/e7-native-tools-vs-mcp-summary-2026-08-16.json`
- `scripts/research/e7_native_vs_mcp_runner.py`

### E7 ADR / topology decision prep — NEXT

- keep native tools as internal default candidate;
- keep MCP-compatible as external interoperability candidate;
- decide whether MCP is required for final delivery or remains optional adapter;
- preserve B3 + evidence-sufficiency + adaptive evidence planning;
- preserve `HttpxTransport` live API path;
- keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- keep LOCKED_TEST blocked;
- do not freeze final architecture yet.

### E8 — Statistical pilot + model benchmark

Separate model/agent stochasticity at fixed observations from environment robustness across deterministic seeds/modes.

### E9 — Conditional techniques

Only test RAG/reranking, multi-agent, routing, persistent memory, prompt optimization or other complexity when residual failure analysis provides a concrete hypothesis.

## 5. Milestones

| Target | Gate |
|---|---|
| **16 Aug** | E0/E1/E2/E3 complete; E4 DEV+VALIDATION; E5; E6 live pass; E7 native/MCP pass |
| **17–20 Aug** | native/MCP ADR + statistical pilot prep |
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

The architecture is frozen only after E0/E1/E3 freezes, B0-B3 DEV+VALIDATION evidence, evidence/stopping evidence, runtime and MCP ADRs, statistical pilot/model benchmark, conditional technique decisions, package inconsistency documentation and the approved live API execution gate.
