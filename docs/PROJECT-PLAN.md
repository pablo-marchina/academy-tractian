# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; **E2 COMPLETE; E3 FROZEN; E4 ACTIVE — private DEV proxy evaluator combined**  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 09:07 BRT  
**Target final delivery:** 2026-09-08

This is the active execution plan after the real TRACTIAN package was audited. It deliberately separates **frozen evidence/contracts** from **experimental architecture decisions** and explicitly forbids demo-first development.

## 1. Current state

### Frozen

- `NORMALIZED-CONTRACT-v1` — raw/normalized/runtime hashes, duplicate-key policy, explicit parameter transformation and 18-operation conformance.
- `API-BEHAVIOR-MAP-v1` — executable challenge-environment behavior, including weak action validation, non-persistent accepted actions, coarse permission behavior and deterministic seed semantics.
- `ScenarioSchema v1` semantics — 16 scenarios / 17 tickets / 10 asset-story groups; machine paths are reference supervision, not exact scripts.
- Gold/evaluator boundary — evaluator-only material never enters model context.
- `BENCHMARK-SPLIT-v1` — group-level DEV / VALIDATION / LOCKED_TEST assignment, frozen before model/runtime/prompt/architecture selection.

### E2 complete

- executable ScenarioSchema/ToolSpec/Trace contracts;
- runner-owned identity/seed boundary;
- explicit seed capability per canonical tool;
- B0 HTTP transport + integrated trace/replay runner;
- strict B1 argument validation;
- deterministic B2 permission/resource guard;
- deterministic B3 evidence-aware action gate;
- integrated deterministic evaluator suite;
- registry-vs-contract conformance tooling;
- provenance/config hashing;
- GitHub Actions verification: 24 tests passed on Python 3.13.15;
- supplied CEN-01 transport path independently validated against the supplied API.

### E3 frozen

- DEV: 5 groups / 8 scenarios;
- VALIDATION: 2 groups / 3 scenarios;
- LOCKED_TEST: 3 groups / 5 scenarios;
- all 10 asset/story groups assigned exactly once;
- all 16 scenarios assigned exactly once;
- every split has investigation, contextualization and execution/action coverage;
- locked-test groups are unavailable for architecture/model/prompt/runtime selection.

### E4 active

Completed so far:

- guarded-boundary B0-B3 experiment preregistered;
- DEV + VALIDATION are the only allowed experiment splits;
- LOCKED_TEST remains unavailable for selection/tuning;
- hard safety metrics are separated from quality metrics;
- scripted/reference paths and test doubles remain infrastructure-only, not agent-quality evidence;
- DEV-only runner implemented and validated;
- model-proposal adapter implemented and validated;
- first DEV model proposal plan generated with `proposal_source_class=model_agent`;
- first DEV boundary run executed across B0/B1/B2/B3;
- boundary metrics exported and recorded;
- private DEV evaluator combiner implemented;
- first private DEV proxy evaluator summary generated locally and recorded in redacted aggregate form.

First DEV boundary result:

| Variant | Proposals | Executed calls | Blocked calls | Permission/scope executions | Contained unsafe proposals | Uncontained safety failures |
|---|---:|---:|---:|---:|---:|---:|
| B0 | 27 | 27 | 0 | 1 | 0 | 1 |
| B1 | 27 | 27 | 0 | 1 | 0 | 1 |
| B2 | 27 | 26 | 1 | 0 | 1 | 0 |
| B3 | 27 | 26 | 1 | 0 | 1 | 0 |

Private DEV proxy evaluator result:

| Variant | Scenarios | Proxy pass | Proxy partial | Proxy fail | Decision OK | Action OK | Safety OK | Avg evidence coverage | Avg conclusion marker coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 8 | 0 | 7 | 1 | 6 | 6 | 7 | 0.498 | 0.292 |
| B1 | 8 | 0 | 7 | 1 | 6 | 6 | 7 | 0.498 | 0.292 |
| B2 | 8 | 0 | 8 | 0 | 6 | 6 | 8 | 0.498 | 0.292 |
| B3 | 8 | 0 | 8 | 0 | 6 | 6 | 8 | 0.498 | 0.292 |

Current interpretation:

- B2 already showed boundary value by containing one unsafe permission/resource-scope proposal that B0/B1 would execute.
- B1 had no visible effect in the first DEV plan because generated arguments were structurally valid.
- B3 did not add blocking beyond B2 because generated action proposals occurred after declared evidence requirements.
- The private DEV evaluator could be combined without committing evaluator-only gold.
- Full task/conclusion success is **not scoreable yet** because the first plan stores structured final tags, not natural-language final answers or handoff text.
- The next DEV run must include scoreable final responses/handoff text and pressure cases that actually exercise B1 and B3.

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
- Locked-test groups are unavailable during architecture/model/prompt/runtime selection.
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

### E2 — Canonical ToolSpec + evaluation harness — COMPLETE

Exit evidence:

- 18-operation registry mechanically aligned to the supplied OpenAPI after frozen transformations;
- 12 runner-seeded read operations explicitly represented;
- B0 live transport + replay integrated into `HarnessRunner`;
- B1/B2/B3 deterministic boundaries executable;
- proposal vs executed-call trace separation;
- integrated evaluator suite executable;
- representative pass/fail fixtures;
- GitHub Actions: **24 passed**;
- reproducible registry and supplied-API conformance scripts retained.

Completion report: `research/39-e2-integrated-completion-report.md`.

### E3 — Benchmark split freeze — COMPLETE

Frozen assignment:

- **DEV:** `asset_G501`, `asset_C710`, `asset_S420`, `asset_M208`, `asset_M101`.
- **VALIDATION:** `asset_B204`, `asset_M102`.
- **LOCKED_TEST:** `asset_V301`, `asset_M605`, `asset_M205`.

Outputs:

- `research/40-e3-benchmark-split-freeze-v1.md`;
- `research/frozen/benchmark-split-v1.json`;
- `scripts/research/e3_validate_split.py`;
- CI validation in `.github/workflows/research-e2.yml`.

No runtime/model/prompt/architecture decision may use locked-test groups.

### E4 — Guarded boundary experiment B0–B3 — ACTIVE

Completed outputs:

- `research/41-e4-guarded-boundary-experiment-preregistration.md`;
- `research/42-e4-execution-start-report.md`;
- `research/43-e4-first-dev-model-proposal-results.md`;
- `research/44-e4-private-dev-evaluator-integration.md`;
- `research/experiments/e4-b0-b3-experiment-manifest.json`;
- `research/experiments/e4-dev-model-proposal-plan-gpt-5-5-thinking-2026-08-16.json`;
- `research/results/e4-dev-model-proposal-boundary-summary-2026-08-16.json`;
- `research/results/e4-private-dev-evaluator-redacted-summary-2026-08-16.json`;
- `scripts/research/e4_validate_experiment_manifest.py`;
- `scripts/research/e4_dev_runner.py`;
- `scripts/research/e4_model_proposal_adapter.py`;
- `scripts/research/e4_private_dev_evaluator.py`.

Primary outcomes remain:

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

Next executable task: generate a scoreable DEV model-proposal run with natural-language final answers/handoff text, plus B1/B3 pressure cases, then rerun boundary + private DEV evaluator before considering VALIDATION.

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
| **16 Aug** | E0 + E1 frozen; E2 complete; E3 split frozen; E4 preregistered; DEV runner/adapter implemented; first DEV boundary run executed; private DEV proxy evaluator combined |
| **17–20 Aug** | scoreable DEV model proposal with final responses + B0/B1/B2/B3 DEV task/conclusion metrics |
| **21–22 Aug** | VALIDATION comparison for promoted E4 components |
| **23–24 Aug** | B3/evidence-stopping follow-up and error analysis |
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
4. B0–B3 boundary and task/conclusion evidence;
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
- `research/39-e2-integrated-completion-report.md`
- `research/40-e3-benchmark-split-freeze-v1.md`
- `research/frozen/benchmark-split-v1.json`
- `research/41-e4-guarded-boundary-experiment-preregistration.md`
- `research/42-e4-execution-start-report.md`
- `research/43-e4-first-dev-model-proposal-results.md`
- `research/44-e4-private-dev-evaluator-integration.md`
- `research/experiments/e4-b0-b3-experiment-manifest.json`
- `research/experiments/e4-dev-model-proposal-plan-gpt-5-5-thinking-2026-08-16.json`
- `research/results/e4-dev-model-proposal-boundary-summary-2026-08-16.json`
- `research/results/e4-private-dev-evaluator-redacted-summary-2026-08-16.json`
- `research/37-post-freeze-execution-backlog.md`
- `research/e2/`
- `research/e4/tests/`
- `scripts/research/e2_registry_conformance.py`
- `scripts/research/e2_b0_real_api_probe.py`
- `scripts/research/e3_validate_split.py`
- `scripts/research/e4_validate_experiment_manifest.py`
- `scripts/research/e4_dev_runner.py`
- `scripts/research/e4_model_proposal_adapter.py`
- `scripts/research/e4_private_dev_evaluator.py`
- `.github/workflows/research-e2.yml`
