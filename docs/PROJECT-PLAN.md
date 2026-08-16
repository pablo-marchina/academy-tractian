# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; **E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 FREE-ANYWHERE CANDIDATE DISCOVERY**  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 12:40 BRT  
**Target final delivery:** 2026-09-08

This is the active execution plan after the real TRACTIAN package was audited. It separates frozen evidence/contracts from experimental architecture decisions, explicitly forbids demo-first development and records that E8 is not local-only: any remote API, hosted service or local system is allowed if the total project cost remains USD 0.

## 1. Current state

### Frozen / complete

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` and gold/evaluator boundary frozen.
- `BENCHMARK-SPLIT-v1` frozen before runtime/model/prompt/architecture selection.
- E2 framework-neutral ToolSpec/Trace/Replay/Evaluator harness complete.
- E4 B0-B3 guarded-boundary DEV+VALIDATION comparison complete.
- E5 evidence acquisition/stopping comparison executed.
- E6 LangGraph runtime path selected as current candidate and live API execution passed locally.
- E7 native tools vs MCP-compatible surface comparison passed.
- E7 topology ADR recorded: native ToolSpec calls are the internal default candidate; MCP-compatible adapter remains the external interoperability candidate.
- E8 statistical pilot/model benchmark prep registered and validated without model calls.
- E8 free-only pilot execution smoke passed with zero paid calls.
- E8 free-anywhere candidate scope/discovery recorded: remote free APIs, free hosted systems and local systems are all eligible if guarded to USD 0.

### Current candidate bundle

- **Boundary:** B3 guarded boundary.
- **Evidence/stopping:** evidence-sufficiency policy.
- **Evidence planning:** adaptive from missing evidence requirements.
- **Runtime candidate:** LangGraph.
- **Transport path:** `HttpxTransport` against the supplied TRACTIAN API.
- **Internal tool surface candidate:** native ToolSpec calls.
- **External interoperability surface candidate:** MCP-compatible `tools/list` + `tools/call` adapter.
- **Budget stance:** completely free; paid OpenAI/Anthropic reference candidates disabled.
- **Free candidate universe:** no-model policy baseline, free remote APIs, free hosted routers/credits and local runtimes.
- **Remote/free candidates to check:** Groq free API, Gemini free API, OpenRouter free router, Hugging Face free inference credits.
- **Local candidate to check:** Ollama, only if latency is acceptable.
- **Baselines/comparators retained:** B0, free tool loop, fixed/reference-like anchor, Pydantic AI/Graph, OpenAI Agents SDK.

This is still not a final model/provider, MCP topology, RAG/vector DB, multi-agent, observability, memory, prompt, UI or final architecture freeze.

## 2. Decision evidence so far

### E4 boundary decision

- B3 remains the current guarded-boundary candidate after the B0-B3 comparison.
- B0 remains a baseline only; B1/B2 remain validation/resource sublayers.

### E5 evidence/stopping decision

- `evidence_sufficiency_policy` remains the current acquisition/stopping candidate.
- Fixed/reference-like remains an infrastructure/reference anchor.
- Free tool loop remains a behavioral baseline, not the preferred stopping policy.

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

### E7 topology decision

| Decision item | Result |
|---|---|
| Internal default candidate | native ToolSpec calls |
| External interoperability candidate | MCP-compatible adapter |
| MCP required for final delivery at this gate | false |
| MCP requirement condition | require only if future delivery/evaluator/partner/deployment/tooling constraint requires MCP |
| Final architecture frozen | false |

### E8 free-only pilot execution smoke

| Metric | Result |
|---|---:|
| Status | `E8_FREE_PILOT_SMOKE_PASS` |
| Free-only mode | true |
| Project cost limit USD | 0 |
| Paid models enabled | false |
| External model calls made in CI | false |
| Executed candidate slot | `no_model_policy_baseline` |
| DEV smoke before VALIDATION | true |
| Fixed observation packets used | true |
| Stochastic repeat harness executed | true |
| DEV groups | `asset_G501`, `asset_C710`, `asset_S420` |
| VALIDATION groups | `asset_B204`, `asset_M102` |
| Task success proxy | 1.0 |
| Action/escalation correctness proxy | 1.0 |
| Evidence coverage proxy | 1.0 |
| RunTrace completeness | true |
| Cost USD | 0.0 |
| LOCKED_TEST accessed | false |

Interpretation: E8 has a zero-cost pilot execution smoke. This validates the free-only benchmark harness, not external model quality.

### E8 free-anywhere candidate discovery

| Metric | Result |
|---|---:|
| Status | `E8_FREE_ANYWHERE_CANDIDATE_DISCOVERY_PASS` |
| Locality required | false |
| Remote free APIs allowed | true |
| Local systems allowed | true |
| Project cost limit USD | 0 |
| Paid models enabled | false |
| Default CI external model calls | false |
| Free candidate slots | 6 |
| Paid candidate slots blocked | OpenAI, Anthropic |
| LOCKED_TEST accessed | false |

Interpretation: the next E8 model-quality run may use any API or system, local or remote, but only with explicit zero-cost guardrails and opt-in.

## 3. Non-negotiable integrity rules

- Raw partner artifacts remain immutable.
- `x-user-id` and evaluation `seed` are runner-bound, never model-selected.
- Related scenarios remain grouped by asset/storyline; no case-level random split.
- LOCKED_TEST remains unavailable until the final locked evaluation gate.
- No evaluator-only gold, reference final answers or scorer-only oracles may enter model prompts.
- Hard identity/schema/policy constraints remain deterministic where possible.
- Optional complexity survives only if required or supported by experiment evidence.
- No paid model execution without explicit approval; current project constraint is fully free.
- Remote free APIs are allowed, but only with explicit `E8_CONFIRM_ZERO_COST=1` and provider-specific opt-in.

## 4. Execution sequence

### Completed gates

- E0/E1 freeze.
- E2 harness.
- E3 benchmark split.
- E4 boundary comparison.
- E5 evidence/stopping comparison.
- E6 runtime/live API integration.
- E7 native/MCP-compatible surface and topology ADR.
- E8 prep and free-only pilot smoke.
- E8 free-anywhere candidate discovery.

### E8 free-anywhere candidate run — NEXT

- check any fully free remote API or hosted system, not just local systems;
- candidate examples: Groq free API, Gemini free API, OpenRouter free router, Hugging Face free inference credits, Ollama local;
- require explicit zero-cost confirmation for remote providers;
- keep OpenAI/Anthropic disabled;
- run DEV smoke before VALIDATION;
- preserve fixed observation packets and repeated outputs;
- measure task-success/model output quality, action/escalation correctness, evidence coverage, trace completeness, latency and cost;
- keep native ToolSpec + optional MCP-compatible adapter;
- keep LOCKED_TEST blocked;
- do not freeze model/provider or architecture.

### E9 — Conditional techniques

Only test RAG/reranking, multi-agent, routing, persistent memory, prompt optimization or other complexity when residual failure analysis provides a concrete hypothesis.

## 5. Milestones

| Target | Gate |
|---|---|
| **16 Aug** | E0/E1/E2/E3 complete; E4 DEV+VALIDATION; E5; E6 live pass; E7 topology ADR; E8 prep + free-only pilot smoke + free-anywhere discovery |
| **17–20 Aug** | free-anywhere model candidate availability + E8 DEV smoke with enabled free candidates |
| **21–22 Aug** | runtime/MCP/model ADRs + error analysis |
| **23–24 Aug** | statistical pilot continuation |
| **25 Aug** | statistical pilot/model screening |
| **26 Aug** | architecture candidates narrowed |
| **27 Aug** | target `FROZEN-v1` |
| **28 Aug–1 Sep** | selected architecture integrated |
| **2–5 Sep** | robustness/adversarial/reliability + locked test |
| **6–7 Sep** | documentation, reproducibility and demo rehearsal |
| **8 Sep** | final delivery/presentation |

## 6. Research Gate → `FROZEN-v1`

The architecture is frozen only after E0/E1/E3 freezes, B0-B3 DEV+VALIDATION evidence, evidence/stopping evidence, runtime and MCP ADRs, statistical pilot/model benchmark, conditional technique decisions, package inconsistency documentation and the approved live API execution gate.
