# Wave 4 — Post-Artifact Experiment Program

Status: **PRE-REGISTERED PROGRAM / EXECUTION PENDING IMPLEMENTATION**

Date: 2026-08-15

## Why the experiment program changes now

Before the partner package, many decisions were necessarily generic. The supplied API/gold now exposes project-specific failure surfaces that can support stronger causal experiments.

Most important findings:

- raw action validation is weak;
- backend company/resource isolation is not enforced;
- user identity and response seed would be dangerous if model-controlled;
- action endpoints return accepted execution events but do not persist state;
- response modes are deterministically seedable;
- machine reference paths are incomplete relative to narrative success criteria;
- only 10 primary asset/story groups support 17 cases, creating leakage risk;
- knowledge corpus is small and already queryable through API tools.

Therefore the central architecture hypothesis should be tested around **contract-aware guarded tool use and evidence-driven behavior**, rather than around adding framework complexity for its own sake.

## Primary architecture hypothesis candidate

### H1 — Guarded contract-aware tool boundary

A system that binds identity/environment context outside model control, validates tool arguments against typed project schemas, and applies deterministic resource/action policy gates will reduce invalid/unsafe action execution and improve argument correctness versus a minimally wrapped tool-calling baseline, without materially reducing task success.

This remains a hypothesis until tested.

### Proposed staged variants

To attribute gains, avoid comparing only two monolithic systems.

#### B0 — Minimal benchmark-valid tool exposure

- same canonical semantic operation names;
- case user and evaluation seed already bound externally (required for benchmark integrity, not an optional safety enhancement);
- minimal request transformation needed to call API;
- no project-owned semantic argument validator beyond unavoidable serialization;
- no cross-company resource guard;
- no advanced evidence/stopping policy.

#### B1 — Typed argument validation

B0 +:

- strict schemas/enums/required structures;
- rejection before API call on invalid action arguments.

#### B2 — Deterministic policy/resource guard

B1 +:

- permission metadata checks;
- company/resource ownership policy where applicable;
- forbidden-action/resource constraints;
- action-specific preconditions derived from normalized scenarios/policy.

#### B3 — Evidence-aware action/escalation policy

B2 +:

- minimum required evidence predicates;
- explicit handling of partial/inconclusive/conflict/unavailable observations;
- evidence-based act vs investigate vs escalate behavior.

#### B4 — Optional confirmation gate experiment

B3 + explicit confirmation for selected state-changing actions.

This is **not part of the canonical benchmark unless clarified by the partner**. It is a safety extension motivated by kickoff guidance and should be reported separately from canonical task correctness.

## Primary outcomes for H1

Hard/safety outcomes:

- invalid action execution rate;
- cross-company/forbidden action execution rate;
- unauthorized action execution rate;
- duplicate action rate;
- benchmark identity/seed integrity violations.

Quality outcomes:

- task/conclusion success;
- tool selection correctness;
- argument correctness;
- action correctness;
- evidence coverage;
- escalation correctness.

Efficiency outcomes:

- tool calls;
- model calls;
- latency;
- token/resource use.

Do not combine these into one arbitrary weighted score. Compare constrained safety first, then Pareto trade-offs among quality and efficiency.

## E0 — Contract normalization and conformance

Goal: create a trustworthy machine contract before client/tool generation.

Steps:

1. hash/archive raw YAML;
2. run duplicate-key-aware parse;
3. normalize duplicate path mapping without modifying raw source;
4. compare normalized operations against FastAPI runtime `/openapi.json`;
5. compare input parameters/body constraints against executable probes;
6. emit transformation manifest;
7. freeze `NORMALIZED-CONTRACT-v1` only after conformance tests pass.

Decision output:

- generated client feasibility;
- manual typed adapter need;
- exact Canonical ToolSpec generation strategy.

## E1 — ScenarioSchema v1 / gold normalization

Goal: convert partner material into executable, non-leaky oracles.

Per base scenario, human-review:

- input/case provenance;
- asset/story split group;
- expected high-level outcome;
- required/acceptable evidence sets;
- required/allowed/forbidden tools/actions;
- authority requirements;
- expected conclusion facts;
- uncertainty/escalation requirements;
- environment mode/seed profile;
- narrative P1 success criterion;
- P2 diagnostic metrics.

Do not encode one exact read trajectory unless a policy truly requires it.

## E2 — Deterministic seed catalog

Goal: systematically produce controlled API perturbations.

For every resource/category used in a benchmark scenario:

- search small explicit seed space until each reachable response mode is found;
- store `resource × category × mode -> seed` mapping;
- verify mode by actual API response metadata;
- version/hash the catalog.

This enables targeted complete/partial/inconclusive/conflict/unavailable experiments without pretending randomness is uncontrolled.

## E3 — Evidence/stopping experiment

Compare:

- fixed/reference-like investigation policy;
- model-only free-form investigation;
- explicit evidence-sufficiency/stopping policy.

Use actual scenario overrides and seed catalog.

Measure:

- task conclusion success;
- premature-stop rate;
- unnecessary-tool rate;
- correct escalation under insufficient evidence;
- tool/latency cost.

Only add a learned/calibrated risk predictor after a rule-based baseline demonstrates a real residual problem.

## E4 — Runtime discriminating spike

Finalists remain candidates until identical project-specific implementation:

- LangGraph;
- Pydantic AI/Graph;
- OpenAI Agents SDK.

Control:

- same Canonical ToolSpec;
- same model/provider;
- same prompt/policy content;
- same scenarios/seeds;
- same evaluator;
- same TraceSchema.

Evaluate:

- pre-action interception;
- safe pause/resume;
- duplicate-action resistance;
- deterministic testability;
- normalized trace completeness;
- provider portability;
- implementation complexity;
- runtime overhead.

The winner is selected in an ADR only after this experiment.

## E5 — Native tools vs MCP adapter

Compare the exact same Canonical ToolSpec through:

- native runtime tools;
- MCP v2 adapter.

Measure:

- schema fidelity;
- argument fidelity;
- trace propagation;
- policy interception compatibility;
- latency overhead;
- implementation/operational complexity;
- portability value.

MCP-first remains a separate hypothesis only if evidence/partner need justifies it.

## E6 — Model benchmark

After evaluator and tool layer are stable:

1. re-check currently accessible tool-capable models/provider constraints;
2. use public tool benchmarks only to shortlist;
3. screen candidates on project development scenarios;
4. compare surviving models on validation groups;
5. report Pareto frontier: quality, reliability, safety, latency/resource use;
6. do not touch locked final test during selection.

## E7 — Reliability decomposition

Separate two sources of variability.

### Agent/model reliability

- fixed API seed/observations;
- repeated independent agent runs;
- estimate scenario-level consistency/pass-style reliability.

### Environment robustness

- fixed agent/model config;
- deterministic seeds chosen to induce different API modes;
- estimate robustness drop by perturbation.

Do not mix both in one undifferentiated repeated-run metric.

## E8 — RAG decision

Default baseline:

- use the supplied knowledge-search + knowledge-document API operations.

Only if error analysis shows retrieval failures:

1. evaluate lexical/local indexing;
2. dense retrieval;
3. hybrid;
4. rerank only if needed.

Because the corpus currently contains five documents, external vector infrastructure must demonstrate measurable end-to-end benefit to survive the ADR.

## E9 — Multi-agent decision

Establish strongest single structured baseline first.

Only introduce planner/executor or specialists if failure analysis shows a decomposition-specific problem that cannot be addressed more simply.

Required comparison:

- same tools/model budget/evaluator;
- quality/reliability gains vs increased trajectory length, failure surface and cost.

## E10 — Optimization/routing

Only after benchmark + validation objective are frozen.

- prompt optimization: development/validation only;
- threshold tuning: development/validation only;
- routing: only if model benchmark reveals complementary strengths;
- no optimizer may alter hard safety constraints.

## Benchmark split program

A naive case-level random split is prohibited because related cases share assets/storylines.

Candidate grouping level:

- primary `asset_id`, refined by explicit storyline if needed.

Before freezing split:

- ensure all variants of a base scenario remain in one group;
- inspect action/evidence/permission coverage per split;
- reserve locked groups before prompt/model/architecture optimization;
- document any coverage compromise caused by only 10 primary asset groups.

The exact proportions remain an experimental-design decision, not a pre-artifact assumption.

## Statistical pilot

The package now allows the previously deferred pilot.

Pilot outputs needed before choosing final `N/k`:

- within-scenario agent variability under fixed environment;
- between-group variability;
- discordance between main architecture variants;
- latency/token distribution;
- provider quota/cost;
- severe-event frequency;
- robustness drop across seeded response modes.

Use the pilot to choose repetitions/precision targets, then freeze the confirmatory protocol.

## Definition of post-artifact research completion

Architecture may move toward `FROZEN-v1` only after:

- normalized API contract passes conformance audit;
- ScenarioSchema v1/gold oracles are human-reviewed;
- benchmark split is frozen and leakage-aware;
- B0–B3 guarded-boundary experiment is complete;
- runtime ADR complete;
- MCP ADR complete;
- model benchmark complete enough to select deployment candidate;
- conditional techniques are accepted/rejected with evidence;
- exact statistical protocol frozen from pilot;
- no major artifact inconsistency remains silently unresolved.
