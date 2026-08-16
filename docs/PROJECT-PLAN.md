# Academy × TRACTIAN — Project Action Plan

Status: **ACTIVE — post-artifact research and experimental execution**

Planning date: **2026-08-16**  
Final delivery: **2026-09-08**

This plan converts the updated TAPI, kickoff evidence and delivered TRACTIAN package into an execution sequence. It is a **project plan**, not an architecture freeze: runtime, MCP topology, model, RAG, multi-agent decomposition, observability backend and optimization remain undecided until the corresponding project-specific experiment/ADR is complete.

## 1. Project objective

Deliver one integrated system containing both mandatory components:

1. **Industrial agent** capable of contextualizing, investigating, executing and escalating against the supplied industrial API.
2. **Agent evaluation/reliability framework** capable of measuring tool choice, arguments, trajectory, evidence use, conclusion, safety, robustness, repeated-run stability and high-impact/action behavior.

The evaluation framework is part of the engineering loop of the agent, not a disconnected second product.

## 2. Evidence hierarchy

When artifacts disagree, use the following order and record the discrepancy instead of silently rewriting history:

1. updated TAPI / written Student Guide and explicit written partner requirements;
2. executable supplied API behavior/source;
3. raw OpenAPI and delivered agent/eval/data artifacts;
4. confidence-labeled kickoff guidance where not contradicted by delivered artifacts;
5. primary research, standards and official framework documentation;
6. reproducible experiments in this repository;
7. project hypotheses.

Every architecture-changing decision must end in an ADR with alternatives, evidence, trade-offs and measured consequences.

## 3. Source-derived facts that now constrain the design

The delivered package establishes the following facts:

- 17 agent-input cases and 16 richer narrative evaluation scenarios;
- 10 primary asset/story groups, making random ticket splitting unsafe due to leakage;
- agent-visible and evaluator-only material are explicitly separated;
- 18 runtime operations across 17 unique HTTP path templates;
- reference trajectories are references, not mandatory scripts;
- action endpoints return accepted execution events and do not persist mutation state in the supplied store;
- `x-user-id` and evaluation `seed` must be runner-bound, not model-selected, to preserve identity/benchmark integrity;
- response modes can be controlled reproducibly through explicit deterministic seeds;
- the raw OpenAPI YAML has a duplicate `/assets/{assetId}` mapping and cannot be naively used for code/tool generation;
- raw action handlers perform coarse validation and can accept semantically invalid/incomplete payloads;
- backend action authorization checks coarse permission but does not enforce company/resource ownership;
- the knowledge corpus contains five documents and already has API search/document operations;
- machine expected paths are materially less complete than narrative scenario policies, expected resolutions and P1 success criteria;
- universal requester confirmation is not encoded in canonical delivered action scenarios, so confirmation remains a separate safety extension unless clarified by the partner.

These facts replace pre-artifact assumptions wherever they conflict.

## 4. Non-negotiable experiment-integrity rules

These are methodology/integrity requirements, not framework preferences:

- gold/evaluator-only files never enter model context;
- case identity (`user_id`) is bound outside the model;
- environment response seed is bound outside the model;
- related cases/variants remain in the same split group;
- locked-test groups are not used for prompt/model/runtime selection;
- raw partner artifacts remain immutable; derived corrections use explicit transformation manifests and hashes;
- action success is not inferred from final-state mutation the supplied API does not persist;
- exact trajectory sequence is not the canonical oracle unless a real policy requires the order;
- hard schema/identity/policy constraints are evaluated deterministically when possible;
- LLM judging is used only where deterministic/structured evaluation is insufficient and must be validated separately;
- no optional complexity survives solely because it is fashionable or technically impressive.

## 5. Central research hypothesis

### H1 — Guarded contract-aware tool boundary

A tool boundary that binds identity/environment outside model control, validates arguments with strict project-owned schemas and applies deterministic resource/action policies will reduce invalid/unsafe action execution and improve argument correctness compared with a minimally wrapped baseline, without materially reducing task success.

### Staged variants

- **B0 — benchmark-valid minimal wrapper:** bound identity/seed; minimal transport transformation; no extra semantic validation/policy.
- **B1 — strict typed validation:** B0 + strict schemas/enums/required structures and pre-API rejection of invalid arguments.
- **B2 — deterministic policy/resource guard:** B1 + permission/company/resource and action-policy enforcement.
- **B3 — evidence-aware action/escalation:** B2 + explicit evidence sufficiency and degraded-response handling before act/escalate.
- **B4 — confirmation extension:** B3 + explicit requester confirmation for selected actions; reported separately unless official policy is clarified.

The purpose of staged variants is attribution: we must know which layer produced a measured gain or regression.

## 6. Experiment program

### E0 — Contract normalization and conformance

**Goal:** produce `NORMALIZED-CONTRACT-v1` suitable for tool/client generation.

Done when:

- duplicate YAML keys are detected before parsing;
- raw contract and package hashes are recorded;
- duplicate asset GET/PATCH mapping is normalized without modifying the raw artifact;
- transformation manifest is generated;
- normalized operations are compared with FastAPI runtime `/openapi.json`;
- request/response semantics used by the project pass conformance probes.

### E1 — Gold normalization / ScenarioSchema v1

**Goal:** turn machine + narrative gold into executable, reviewed oracles.

For each base scenario capture:

- source/provenance and split group;
- high-level expected decision;
- required/acceptable evidence;
- required/allowed/forbidden tools/actions;
- permission/policy constraints;
- conclusion facts and forbidden claims;
- uncertainty/escalation requirements;
- environment mode/seed/override profile;
- narrative P1 success criterion and P2 diagnostics.

A human review pass is mandatory before the normalized gold becomes benchmark-authoritative.

### E2 — Canonical ToolSpec + evaluation harness

Build framework-neutral contracts first:

- canonical typed operation definitions;
- external identity/seed binding;
- ToolSpec action metadata;
- ScenarioSchema v1 models;
- TraceSchema v1 models;
- evaluator interfaces and deterministic evaluator fixtures;
- replay/observation format;
- config/artifact hashing.

No runtime winner is selected during this stage.

### E3 — Split freeze

A random case-level split is prohibited. Candidate grouping is primary asset/storyline.

Before freezing:

- ensure all controlled variants inherit the base split group;
- inspect contextualize/investigate/execute coverage;
- inspect action type, permission and evidence-mode coverage;
- reserve locked groups before architecture/model/prompt optimization;
- record unavoidable coverage compromises caused by only 10 base groups.

Output: `BENCHMARK-SPLIT-v1` + manifest/hashes.

### E4 — Guarded boundary experiment B0–B3

Primary outcomes:

**Safety/integrity**

- invalid action execution rate;
- unauthorized/forbidden action execution rate;
- cross-company action execution rate;
- duplicate/unnecessary action rate;
- identity/seed integrity violations.

**Quality**

- task/conclusion success;
- tool-choice correctness;
- argument correctness;
- evidence coverage;
- action correctness;
- escalation correctness.

**Efficiency**

- tool/model calls;
- latency;
- tokens/resource use.

Do not collapse these into one arbitrary weighted score. Treat hard safety constraints first and analyze quality/efficiency through effect sizes and Pareto trade-offs.

### E5 — Evidence acquisition / stopping

Compare, on the same scenarios and controlled API modes:

1. fixed/reference-like investigation;
2. model-only free-form tool loop;
3. explicit evidence-sufficiency/stopping policy.

Measure task success, premature stopping, unnecessary calls, escalation correctness and latency/tool cost.

Only consider learned/calibrated risk prediction if a strong rule-based evidence policy leaves a demonstrated residual failure mode.

### E6 — Runtime discriminating spike

Finalists remain candidates until tested with identical project contracts:

- LangGraph;
- Pydantic AI/Graph;
- OpenAI Agents SDK.

Hold constant: Canonical ToolSpec, model/provider, prompt/policy content, scenario, seed, evaluator and normalized TraceSchema.

Measure:

- pre-action interception;
- pause/resume safety;
- duplicate-action resistance;
- deterministic testing support;
- normalized trace completeness;
- provider portability;
- implementation complexity;
- runtime overhead.

Output: runtime ADR.

### E7 — Native tools vs MCP v2

Expose the exact same Canonical ToolSpec through native runtime tools and an MCP v2 adapter.

Measure schema fidelity, argument fidelity, policy interception, trace propagation, latency overhead, portability and operational complexity.

Output: MCP ADR. MCP-first is not selected unless partner need or experiment evidence justifies it.

### E8 — Statistical pilot and model benchmark

First run a pilot to estimate:

- within-scenario stochastic agent variability at fixed API observations;
- between-group variability;
- architecture discordance;
- severe-event frequency;
- latency/token distribution;
- robustness drop across deterministic API modes.

Use the pilot to freeze repetition count `k`, precision targets and confirmatory analysis.

Then evaluate currently permitted/available tool-capable models on development/validation groups only. Select with hard safety constraints plus a quality/reliability/latency/resource Pareto analysis.

### E9 — Conditional techniques

Only after the core architecture/evaluator is stable:

- **external RAG:** only if direct knowledge API retrieval exhibits measured retrieval failures;
- **multi-agent:** only if a strong single structured baseline has a decomposition-specific residual problem;
- **adaptive routing:** only if model benchmarking reveals complementary strengths;
- **prompt/threshold optimization:** development/validation only after objective freeze;
- **observability backend:** compare after project-owned TraceSchema works independently of the backend.

A rejected optional technique is a valid research result and should be documented in an ADR/decision note.

## 7. Calendar and critical path

Dates below are **project targets**, not partner requirements. They exist to protect enough time for final evaluation, documentation and demo quality.

| Target | Work package | Exit condition |
|---|---|---|
| **Aug 16–17** | Contract + gold normalization | `NORMALIZED-CONTRACT-v1` candidate; reviewed ScenarioSchema v1 draft; known inconsistencies explicit |
| **Aug 18–20** | Canonical ToolSpec, evaluators, trace/replay, seed catalog | framework-neutral harness executes representative canonical scenarios |
| **Aug 21–22** | Split freeze + B0/B1/B2 | locked split frozen; validation/policy experiments runnable |
| **Aug 23–24** | B3 + evidence/stopping | core guarded/evidence hypotheses measured |
| **Aug 25** | Runtime + MCP spikes | runtime ADR and MCP ADR have experiment evidence |
| **Aug 26** | Statistical pilot + model screening | `k`/confirmatory protocol frozen; viable model shortlist selected |
| **Aug 27** | **Research Gate / `FROZEN-v1` target** | architecture ADR set closed enough for final implementation |
| **Aug 28–Sep 1** | Implement/integrate final selected architecture | complete agent + evaluation workflow end-to-end |
| **Sep 2–4** | Validation/fault/reliability/adversarial runs | full result set, CIs/slices/failure analysis generated |
| **Sep 5** | Locked final test | one untouched final evaluation pass archived |
| **Sep 6** | Documentation/reproducibility audit | README, architecture, methods, results, limits and runbook complete |
| **Sep 7** | Final demo rehearsal / contingency | clean-machine reproduction and presentation flow verified |
| **Sep 8** | Final presentation/delivery | submitted artifact matches documented configuration/results |

If an upstream gate slips, protect the locked-test/documentation/demo window by cutting **optional complexity**, not by weakening benchmark integrity.

## 8. Priority classes

### MUST — required before final delivery

- trustworthy normalized contract;
- agent/evaluator gold separation;
- leakage-aware benchmark split;
- complete canonical agent over supplied API;
- evaluation across all TAPI analysis surfaces materially applicable to the cases;
- reproducible traces/configs/results;
- robust handling of partial/inconclusive/conflict/unavailable modes;
- safe action boundary and permission/policy evaluation;
- repeated-run reliability + fault/robustness analysis;
- hypothesis, baselines, ablations/comparisons and limitations;
- final README/runbook/demo.

### SHOULD — strong grade maximizers if supported by evidence

- B0–B3 causal/staged experiment;
- runtime and MCP controlled ADRs;
- validated semantic conclusion evaluator;
- adversarial cross-company/invalid-argument/duplicate-action cases;
- replay system;
- project-native model Pareto benchmark;
- interactive trace/experiment inspection UI.

### CONDITIONAL — include only if experiments justify them

- external RAG/vector database;
- reranking;
- multi-agent orchestration;
- adaptive model routing;
- persistent cross-session memory;
- automatic prompt optimization;
- learned risk/calibration model;
- B4 universal confirmation policy;
- heavyweight observability infrastructure.

## 9. Definition of `FROZEN-v1`

Architecture may be frozen only when:

1. normalized API contract passes conformance checks;
2. ScenarioSchema v1/gold oracles are human-reviewed;
3. benchmark split is leakage-aware and locked;
4. central guarded-boundary and evidence/stopping experiments have produced interpretable results;
5. runtime and MCP choices have experiment-backed ADRs;
6. statistical protocol is frozen from a pilot;
7. a model/deployment candidate has project-native evidence;
8. conditional complexity is explicitly accepted, rejected or deferred with rationale;
9. no material package inconsistency remains silent;
10. remaining external questions are explicitly documented.

`FROZEN-v1` freezes the architecture/configuration used for the final confirmatory evaluation; it does not prohibit bug fixes that preserve experiment semantics and are versioned/re-run appropriately.

## 10. Final evaluation package

The final repository should make it possible to answer, with evidence:

- What problem did the agent solve?
- Why was this architecture selected over alternatives?
- Which parts are deterministic and which rely on the model?
- How well does it choose tools and construct arguments?
- Does it gather enough evidence and stop at the right time?
- Does it respond with the correct operational conclusion?
- Does it act safely under invalid permissions/targets/arguments?
- How does it behave under partial, inconclusive, conflicting and unavailable information?
- How stable is it across repeated runs with fixed observations?
- What changes when the environment mode changes?
- What component caused each observed improvement/regression?
- What limitations remain and what should be tested next?

## 11. Immediate next action

Start with **E0 + E1 in parallel**:

1. normalize/conformance-test the OpenAPI contract;
2. normalize every partner scenario into reviewed ScenarioSchema v1 oracles;
3. only then implement the canonical ToolSpec/evaluator harness against those two trusted contracts.

This is the shortest path from research to implementation without hard-coding assumptions or contaminating the benchmark.