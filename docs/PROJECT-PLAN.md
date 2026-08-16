# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; **E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE — B3 boundary candidate promoted**  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 09:26 BRT  
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
- B0 HTTP transport + integrated trace/replay runner;
- strict B1 argument validation;
- deterministic B2 permission/resource guard;
- deterministic B3 evidence-aware action gate;
- integrated deterministic evaluator suite;
- registry-vs-contract conformance tooling;
- GitHub Actions retained.

### E3 frozen

- DEV: 5 groups / 8 scenarios;
- VALIDATION: 2 groups / 3 scenarios;
- LOCKED_TEST: 3 groups / 5 scenarios;
- all 10 asset/story groups assigned exactly once;
- all 16 scenarios assigned exactly once;
- every split has investigation, contextualization and execution/action coverage;
- locked-test groups are unavailable for architecture/model/prompt/runtime selection.

### E4 validation complete

Completed:

- B0-B3 guarded-boundary experiment preregistered;
- DEV-only runner implemented and validated;
- model-proposal adapter implemented and validated;
- private DEV proxy evaluator combiner implemented;
- first DEV boundary run executed;
- scoreable DEV run executed with B1/B3 pressure cases;
- VALIDATION-only proposal adapter implemented;
- VALIDATION scoreable proposal plan generated using only `asset_B204` and `asset_M102`;
- VALIDATION B0/B1/B2/B3 boundary run executed in CI;
- private VALIDATION redacted aggregate recorded;
- component decision recorded.

Scoreable DEV result:

| Variant | Scoreable pass | Scoreable fail | Decision OK | Action OK | Safety OK | Uncontained safety failures |
|---|---:|---:|---:|---:|---:|---:|
| B0 | 6/8 | 2/8 | 8/8 | 6/8 | 6/8 | 2 |
| B1 | 7/8 | 1/8 | 8/8 | 7/8 | 7/8 | 1 |
| B2 | 7/8 | 1/8 | 8/8 | 7/8 | 7/8 | 1 |
| B3 | 8/8 | 0/8 | 8/8 | 8/8 | 8/8 | 0 |

Scoreable VALIDATION result:

| Variant | Scoreable pass | Scoreable fail | Decision OK | Action OK | Safety OK | Uncontained safety failures |
|---|---:|---:|---:|---:|---:|---:|
| B0 | 2/3 | 1/3 | 3/3 | 2/3 | 2/3 | 2 |
| B1 | 2/3 | 1/3 | 3/3 | 2/3 | 2/3 | 1 |
| B2 | 2/3 | 1/3 | 3/3 | 2/3 | 2/3 | 1 |
| B3 | 3/3 | 0/3 | 3/3 | 3/3 | 3/3 | 0 |

Component decision:

- **B0:** keep as baseline only; reject as deployment boundary because it permits uncontained safety failures.
- **B1:** promote as required validation sublayer; reject as sufficient standalone boundary.
- **B2:** promote as required resource/permission sublayer because DEV evidence showed scope-safety value; this VALIDATION run did not include new scope-denial pressure.
- **B3:** promote as the current guarded-boundary candidate for the next experimental stage.

This is **not** a runtime/model/prompt/MCP/RAG/UI freeze.

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

## 4. Central hypothesis status

### H1 — Guarded contract-aware tool boundary

Current evidence supports the guarded B3 boundary bundle for the next experimental stage: B1 contains invalid action arguments, B2 supplies the resource/permission safety layer, and B3 adds evidence-before-action gating. B0 remains the baseline.

Variants:

- **B0:** baseline only.
- **B1:** required sublayer, not sufficient alone.
- **B2:** required sublayer, especially for resource/permission containment.
- **B3:** current guarded-boundary candidate.
- **B4:** requester confirmation remains separate unless canonical policy changes.

## 5. Execution sequence

### E2 — Canonical ToolSpec + evaluation harness — COMPLETE

Completion report: `research/39-e2-integrated-completion-report.md`.

### E3 — Benchmark split freeze — COMPLETE

Frozen assignment:

- **DEV:** `asset_G501`, `asset_C710`, `asset_S420`, `asset_M208`, `asset_M101`.
- **VALIDATION:** `asset_B204`, `asset_M102`.
- **LOCKED_TEST:** `asset_V301`, `asset_M605`, `asset_M205`.

No runtime/model/prompt/architecture decision may use locked-test groups.

### E4 — Guarded boundary experiment B0-B3 — VALIDATION COMPLETE

Completed outputs:

- `research/41-e4-guarded-boundary-experiment-preregistration.md`;
- `research/42-e4-execution-start-report.md`;
- `research/43-e4-first-dev-model-proposal-results.md`;
- `research/44-e4-private-dev-evaluator-integration.md`;
- `research/45-e4-dev-scoreable-proposal-results.md`;
- `research/46-e4-validation-boundary-results.md`;
- `research/experiments/e4-b0-b3-experiment-manifest.json`;
- `research/experiments/e4-dev-model-proposal-plan-gpt-5-5-thinking-2026-08-16.json`;
- `research/experiments/e4-dev-scoreable-proposal-plan-gpt-5-5-thinking-2026-08-16.json`;
- `research/experiments/e4-validation-scoreable-proposal-plan-gpt-5-5-thinking-2026-08-16.json`;
- `research/results/e4-dev-model-proposal-boundary-summary-2026-08-16.json`;
- `research/results/e4-private-dev-evaluator-redacted-summary-2026-08-16.json`;
- `research/results/e4-private-dev-scoreable-evaluator-redacted-summary-2026-08-16.json`;
- `research/results/e4-private-validation-scoreable-evaluator-redacted-summary-2026-08-16.json`;
- `scripts/research/e4_validate_experiment_manifest.py`;
- `scripts/research/e4_dev_runner.py`;
- `scripts/research/e4_model_proposal_adapter.py`;
- `scripts/research/e4_validation_proposal_adapter.py`;
- `scripts/research/e4_private_dev_evaluator.py`;
- `scripts/research/e4_private_validation_evaluator.py`.

### E5 — Evidence acquisition / stopping — NEXT

Compare fixed/reference-like investigation, free model tool loop and explicit evidence-sufficiency/stopping policy while using B3 as the current guarded-boundary candidate and B0 as baseline where useful.

### E6 — Runtime discriminating spike

Candidates remain: LangGraph; Pydantic AI/Graph; OpenAI Agents SDK.

### E7 — Native tools vs MCP

Expose the same ToolSpec through native tools and MCP v2.

### E8 — Statistical pilot + model benchmark

Separate model/agent stochasticity at fixed observations from environment robustness across deterministic seeds/modes.

### E9 — Conditional techniques

Only test RAG/reranking, multi-agent, routing, persistent memory, prompt optimization or other complexity when residual failure analysis provides a concrete hypothesis.

## 6. Milestones

| Target | Gate |
|---|---|
| **16 Aug** | E0 + E1 frozen; E2 complete; E3 split frozen; E4 DEV+VALIDATION boundary evidence recorded |
| **17–20 Aug** | E5 evidence acquisition/stopping setup and execution |
| **21–22 Aug** | runtime/MCP discriminating spikes if E5 is stable |
| **23–24 Aug** | error analysis + statistical pilot preparation |
| **25 Aug** | runtime + MCP ADRs |
| **26 Aug** | statistical pilot + model screening |
| **27 Aug** | target `FROZEN-v1` |
| **28 Aug–1 Sep** | selected architecture integrated |
| **2–5 Sep** | robustness/adversarial/reliability + locked test |
| **6–7 Sep** | documentation, reproducibility and demo rehearsal |
| **8 Sep** | final delivery/presentation |

If schedule pressure appears, cut optional complexity first. Never weaken gold isolation, split integrity, conformance, evaluator validity or locked-test discipline.

## 7. Research Gate → `FROZEN-v1`

The architecture is frozen only after E0/E1/E3 freezes, B0-B3 DEV+VALIDATION evidence, evidence/stopping evidence, runtime and MCP ADRs, statistical pilot/model benchmark, conditional technique decisions and package inconsistency documentation.

## 8. Active artifacts

See `research/README.md` and `research/37-post-freeze-execution-backlog.md` for the current artifact index.
