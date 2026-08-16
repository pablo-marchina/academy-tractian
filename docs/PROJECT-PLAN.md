# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; **E2 ACTIVE — Wave 2**  
**Planning date:** 2026-08-16  
**Target final delivery:** 2026-09-08

This is the active execution plan after the real TRACTIAN package was audited. It deliberately separates **frozen evidence/contracts** from **experimental architecture decisions** and explicitly forbids demo-first development.

## 1. Current state

### Frozen

- `NORMALIZED-CONTRACT-v1` — raw/normalized/runtime hashes, duplicate-key policy, explicit parameter transformation and 18-operation conformance.
- `API-BEHAVIOR-MAP-v1` — executable challenge-environment behavior, including weak action validation, non-persistent accepted actions, coarse permission behavior and deterministic seed semantics.
- `ScenarioSchema v1` semantics — 16 scenarios / 17 tickets / 10 asset-story groups; machine paths are reference supervision, not exact scripts.
- Gold/evaluator boundary — evaluator-only material never enters model context.

### E2 active

- executable ScenarioSchema/ToolSpec/Trace contracts;
- runner-owned identity/seed boundary;
- replay and provenance;
- deterministic B0 HTTP transport boundary;
- strict argument validation foundation;
- deterministic permission/resource guard;
- evidence-aware action gate;
- structured argument, conclusion and escalation/handoff evaluators;
- volatile trace normalization.

### Not frozen

Runtime, model/provider, MCP, RAG, multi-agent decomposition, routing, memory, observability backend and optimization remain experimental choices.

## 2. Evidence hierarchy

1. Updated TAPI / written Student Guide / explicit partner requirements.
2. Executable supplied API behavior/source.
3. Raw OpenAPI and supplied agent/eval/data artifacts.
4. Kickoff guidance when not contradicted by delivered artifacts.
5. Primary research and official framework documentation.
6. Reproducible project experiments.
7. Hypotheses.

Architecture-changing choices require an ADR containing alternatives, hypothesis, protocol, results, trade-offs and decision.

## 3. Non-negotiable integrity rules

- Raw partner artifacts remain immutable.
- `x-user-id` and evaluation `seed` are runner-bound, never model-selected.
- Related scenarios remain grouped by asset/storyline; no case-level random split.
- Locked-test groups are unavailable during architecture/model/prompt selection.
- Reference trajectories are not exact-match gold unless an explicit policy requires ordering.
- Hard identity/schema/policy constraints are deterministic where possible.
- Action success follows supplied `accepted_event_non_persistent` semantics; no invented final-state oracle.
- LLM judging is used only when structured/deterministic evaluation is insufficient and must be validated separately.
- Optional complexity survives only if required or supported by experiment evidence.
- **No demo-first development:** a test double may validate infrastructure, but it is never evidence that the agent solves the partner problem.
- Final demonstration is downstream of experimental decisions and must show measured behavior, not hand-scripted success.

## 4. Central hypothesis

### H1 — Guarded contract-aware tool boundary

A boundary that keeps identity/environment outside model control, validates arguments with strict project-owned schemas and applies deterministic resource/action policy should reduce invalid/unsafe action execution and improve argument correctness relative to a minimally wrapped baseline without materially reducing task success.

Variants:

- **B0:** minimal benchmark-valid wrapper.
- **B1:** B0 + strict typed argument validation.
- **B2:** B1 + deterministic permission/company/resource guard.
- **B3:** B2 + evidence-aware action/escalation policy.
- **B4:** requester confirmation as a separate safety extension unless official canonical policy changes.

## 5. Execution sequence

### E2 — Canonical ToolSpec + evaluation harness — ACTIVE

Implemented:

- executable ScenarioSchema v1 models;
- 18-operation Canonical ToolSpec registry;
- runner-owned identity/seed binding;
- TraceSchema v1 models and invariants;
- replay/observation store;
- canonical configuration/artifact hashing;
- deterministic baseline evaluators;
- B0 contract-valid HTTP transport adapter;
- deterministic evidence-aware action gate;
- structured argument/conclusion/escalation evaluators;
- volatile trace normalization;
- reproducible CEN-01 real-API transport probe.

Remaining before E3:

1. integrate B0 + trace emission + replay into one harness runner;
2. add representative investigation/contextualization/execution fixtures;
3. mechanically verify the 18-operation registry against frozen E0 operation evidence;
4. complete full E2 test-suite execution and record the environment/result;
5. verify one complete reference scenario through the integrated B0 runner;
6. confirm evaluator outputs are stable on canonical pass/fail fixtures.

### E3 — Benchmark split freeze

Use the already frozen 10 asset/story groups. Before assigning dev/validation/locked-test:

- preserve every controlled variant inside its base group;
- inspect investigation/contextualize/execute coverage;
- inspect action/permission/evidence-mode coverage;
- reserve locked groups before any model/runtime/prompt optimization;
- document coverage compromises caused by only 10 independent groups.

Output: `BENCHMARK-SPLIT-v1` + manifest/hash.

### E4 — Guarded boundary experiment B0–B3

Primary outcomes:

- invalid action execution;
- unauthorized/cross-company action execution;
- duplicate/unnecessary actions;
- argument correctness;
- tool-choice correctness;
- evidence coverage;
- task/conclusion success;
- escalation correctness;
- latency/calls/tokens.

Hard safety failures are reported separately; do not hide them inside an arbitrary weighted score.

### E5 — Evidence acquisition / stopping

Compare:

1. fixed/reference-like investigation;
2. free model tool loop;
3. explicit evidence-sufficiency/stopping policy.

Measure premature stopping, unnecessary calls, task success, escalation correctness and efficiency under controlled API modes.

### E6 — Runtime discriminating spike

Candidates remain:

- LangGraph;
- Pydantic AI/Graph;
- OpenAI Agents SDK.

Hold constant ToolSpec, model, scenario, prompt/policy, seed and evaluator. Measure safety interception, pause/resume, duplicate-action resistance, deterministic testing, trace completeness, portability, complexity and overhead.

Output: runtime ADR.

### E7 — Native tools vs MCP

Expose the same ToolSpec through native tools and MCP v2. Measure schema/argument fidelity, policy interception, trace propagation, latency and complexity.

Output: MCP ADR.

### E8 — Statistical pilot + model benchmark

Separate:

- model/agent stochasticity at fixed environment observations;
- environment robustness across deterministic seeds/modes.

Use the pilot to determine repetition count `k` and confirmatory analysis. Screen models only on development groups, validate survivors on validation groups, then lock the test.

Selection uses hard safety constraints plus quality/reliability/latency/resource Pareto evidence.

### E9 — Conditional techniques

Only test RAG/reranking, multi-agent, routing, persistent memory, prompt optimization or other complexity when residual failure analysis provides a concrete hypothesis. Reject any component without measurable end-to-end value.

## 6. Milestones

| Target | Gate |
|---|---|
| **16 Aug** | E0 + E1 freezes complete; E2 Wave 1–2 active |
| **17–20 Aug** | integrated E2 harness + B0 transport operational |
| **21–22 Aug** | E3 benchmark split frozen + B0/B1/B2 runnable |
| **23–24 Aug** | B3 + evidence/stopping |
| **25 Aug** | runtime + MCP spikes |
| **26 Aug** | statistical pilot + model screening |
| **27 Aug** | target `FROZEN-v1` |
| **28 Aug–1 Sep** | selected architecture integrated |
| **2–5 Sep** | robustness/adversarial/reliability + locked test |
| **6–7 Sep** | documentation, reproducibility and demo rehearsal |
| **8 Sep** | final delivery/presentation |

If schedule pressure appears, cut optional complexity first. Never weaken gold isolation, split integrity, conformance, evaluator validity or locked-test discipline.

## 7. Research Gate → `FROZEN-v1`

The architecture is frozen only after:

1. E0 contract freeze;
2. E1 ScenarioSchema/gold semantics freeze;
3. leakage-aware dev/validation/locked-test split;
4. B0–B3 evidence;
5. evidence/stopping evidence;
6. runtime and MCP ADRs;
7. statistical pilot and confirmatory protocol;
8. project-native model benchmark;
9. conditional techniques accepted/rejected by evidence;
10. material package inconsistencies documented with no silent corrections.

## 8. Active artifacts

- `research/34-e0-contract-freeze-v1.md`
- `research/frozen/e0-contract-freeze.manifest.json`
- `research/frozen/API-BEHAVIOR-MAP-v1.json`
- `research/35-e1-gold-freeze-v1.md`
- `research/frozen/e1-gold-freeze.manifest.json`
- `research/36-e2-execution-report.md`
- `research/37-post-freeze-execution-backlog.md`
- `research/38-e2-wave-2-execution-report.md`
- `research/e2/`
- `scripts/research/e2_b0_real_api_probe.py`
