# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; **E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED — evidence-sufficiency policy promoted**  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 09:36 BRT  
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

E4 promoted B3 as the current guarded-boundary candidate:

- **B0:** baseline only; rejected as deployment boundary due uncontained safety failures.
- **B1:** required validation sublayer; not sufficient alone.
- **B2:** required resource/permission sublayer.
- **B3:** current guarded-boundary candidate.

This is not a runtime/model/prompt/MCP/RAG/UI freeze.

### E5 executed

E5 compared evidence-acquisition/stopping strategies over DEV + VALIDATION only, with LOCKED_TEST blocked.

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

Decision: promote `evidence_sufficiency_policy` as the current evidence-acquisition/stopping candidate, keep `free_tool_loop` as behavioral baseline, and keep `fixed_reference_like` as infrastructure/reference anchor only.

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

## 4. Current candidate policy bundle

Current evidence supports:

- B3 guarded boundary: B1 validation + B2 resource/permission guard + B3 evidence-before-action gate.
- Evidence-sufficiency/stopping policy: current candidate acquisition/stopping policy.
- B0 and free tool loop: retained as baselines where useful.
- Fixed/reference-like investigation: retained only as infrastructure/reference anchor.

This bundle is still not an architecture/runtime/model freeze.

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

Completed reports:

- `research/45-e4-dev-scoreable-proposal-results.md`
- `research/46-e4-validation-boundary-results.md`

### E5 — Evidence acquisition / stopping — EXECUTED

Completed outputs:

- `research/47-e5-evidence-stopping-preregistration.md`
- `research/48-e5-evidence-stopping-results.md`
- `research/experiments/e5-evidence-stopping-experiment-manifest.json`
- `research/results/e5-evidence-stopping-summary-2026-08-16.json`
- `scripts/research/e5_evidence_stopping_runner.py`

### E6 — Runtime discriminating spike — NEXT

Candidates remain: LangGraph; Pydantic AI/Graph; OpenAI Agents SDK.

The runtime spike must hold constant B3 boundary + evidence-sufficiency policy, ToolSpec, scenario inputs, split policy and evaluator assumptions. It must not use LOCKED_TEST or freeze architecture before ADR evidence.

### E7 — Native tools vs MCP

Expose the same ToolSpec through native tools and MCP v2.

### E8 — Statistical pilot + model benchmark

Separate model/agent stochasticity at fixed observations from environment robustness across deterministic seeds/modes.

### E9 — Conditional techniques

Only test RAG/reranking, multi-agent, routing, persistent memory, prompt optimization or other complexity when residual failure analysis provides a concrete hypothesis.

## 6. Milestones

| Target | Gate |
|---|---|
| **16 Aug** | E0 + E1 frozen; E2 complete; E3 split frozen; E4 DEV+VALIDATION boundary evidence; E5 executed |
| **17–20 Aug** | runtime/MCP discriminating spikes under fixed B3 + evidence-sufficiency policy |
| **21–22 Aug** | runtime/MCP ADRs + error analysis |
| **23–24 Aug** | statistical pilot preparation |
| **25 Aug** | statistical pilot/model screening |
| **26 Aug** | architecture candidates narrowed |
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
