# Research Backlog Before Architecture Freeze

Status: **Wave 4 complete — project-specific experiment execution unlocked**

Planning reference: [`../docs/PROJECT-PLAN.md`](../docs/PROJECT-PLAN.md)

The updated TAPI requires both agent construction and evaluation. The kickoff supplied partner workflow guidance. The delivered project ZIP now provides the actual API implementation, contract, canonical cases and evaluation material.

## Critical-path targets

These dates are internal project targets, not partner requirements.

| Target | Gate |
|---|---|
| Aug 16–17 | `NORMALIZED-CONTRACT-v1` candidate + ScenarioSchema v1 reviewed draft |
| Aug 18–20 | Canonical ToolSpec/evaluator/trace/replay harness operational |
| Aug 21–22 | leakage-aware benchmark split frozen + B0/B1/B2 runnable |
| Aug 23–24 | B3 + evidence/stopping experiments completed |
| Aug 25 | runtime + MCP discriminating spikes completed |
| Aug 26 | statistical pilot/model screening; `k` and confirmatory protocol frozen |
| Aug 27 | Research Gate target → `FROZEN-v1` |
| Aug 28–Sep 1 | final selected architecture integrated end-to-end |
| Sep 2–5 | final evaluation, adversarial/robustness/reliability, locked test |
| Sep 6–7 | documentation/reproducibility/demo rehearsal |
| Sep 8 | final delivery/presentation |

If schedule slips, cut P2/optional complexity before compromising contract/gold/split/evaluator integrity.

## P0 — Artifact normalization and benchmark ground truth

### R01 — Requirements / source-of-truth audit

- [x] Extract updated TAPI requirements.
- [x] Capture kickoff guidance with confidence labels.
- [x] Receive/hash partner package.
- [x] Inventory API/cases/eval/data artifacts.
- [x] Record package inconsistencies rather than silently fixing them.
- [ ] Resolve remaining instructor/partner constraints: hidden eval, model access, public artifact policy, final-demo conditions, confirmation policy.

### R02 — API contract normalization

- [x] Enumerate actual runtime operations/resources/actions.
- [x] Detect duplicate `/assets/{assetId}` raw YAML key.
- [x] Identify weak response/action schemas and executable-contract differences.
- [ ] Implement duplicate-key-aware contract loader.
- [ ] Produce immutable raw-contract manifest/hashes.
- [ ] Generate project normalized OpenAPI contract with explicit transformation log.
- [ ] Conformance-test normalized operations against FastAPI runtime `/openapi.json` and probes.
- [ ] Freeze `NORMALIZED-CONTRACT-v1`.

**Exit gate:** no tool/client generation from the raw duplicate-key contract.

### R03 — Domain/action/policy map

- [x] Inventory synthetic resources/counts/relationships.
- [x] Map action endpoints to coarse API permission classes.
- [x] Confirm accepted-action semantics.
- [x] Confirm supplied actions do not persist state.
- [x] Identify lack of backend company/resource isolation.
- [x] Establish bound user identity as benchmark-integrity requirement.
- [x] Establish bound environment seed as benchmark-integrity requirement.
- [ ] Produce machine-readable resource/action metadata for Canonical ToolSpec.
- [ ] Define guarded company/resource policy precisely from observable relationships.

### R04 — Golden-set normalization

- [x] Inventory 17 cases / 16 narrative scenarios.
- [x] Confirm reference trajectory is not a script.
- [x] Detect material differences between machine expected paths and narrative scenarios.
- [x] Identify only 10 primary asset/story groups → leakage risk.
- [x] Separate scenario labels (`pending`, `stale`) from API response-mode enum.
- [ ] Human-review every narrative P1 success criterion/expected resolution.
- [ ] Produce ScenarioSchema v1 oracles: decisions, evidence, actions, policy, conclusion, uncertainty/escalation.
- [ ] Produce change/provenance manifest for normalized gold.
- [ ] Freeze group-aware dev/validation/locked-test split.

**Exit gate:** no model/prompt/runtime selection against unreviewed narrative gold or a random ticket split.

### R05 — Seed/robustness catalog

- [x] Confirm response mode is deterministic for explicit seed and resource/category.
- [x] Confirm omitted seed is also deterministic in executable implementation.
- [x] Inventory fixed scenario overrides.
- [ ] Implement resource/category/mode seed-catalog generator.
- [ ] Verify reachable modes against live API.
- [ ] Version/hash seed catalog.

## P1 — Canonical tool/evaluator architecture

### R06 — Canonical ToolSpec

- [x] Stable agent-facing contract supported by kickoff/package findings.
- [x] Define that `x-user-id` and `seed` are runtime-bound, not model arguments.
- [ ] Define strict request/response models from normalized contract + executable payloads.
- [ ] Add action metadata: permission, target-resource scope, impact, event/non-persistent semantics.
- [ ] Implement minimal benchmark-valid adapter B0.
- [ ] Implement strict typed validator B1.
- [ ] Implement deterministic policy/resource guard B2.
- [ ] Implement evidence-aware action/escalation B3.

### R07 — Evaluator v1

- [x] ScenarioSchema v0 / TraceSchema v0 research contracts.
- [x] Action oracle corrected from generic final-state equality to accepted-event/action correctness for supplied API.
- [ ] Implement tool-choice evaluator.
- [ ] Implement argument/schema/semantic evaluator.
- [ ] Implement evidence evaluator.
- [ ] Implement trajectory/policy evaluator without strict raw sequence matching.
- [ ] Implement structured conclusion/fact evaluator.
- [ ] Implement action evaluator.
- [ ] Implement escalation evaluator.
- [ ] Implement safety/resource-policy evaluator.
- [ ] Validate evaluator itself with handcrafted pass/fail fixtures before using it to rank agents.

### R08 — Trace / replay / provenance

- [x] OTel-first + project-owned TraceSchema principle.
- [ ] Implement TraceSchema v1 models.
- [ ] Add raw/normalized tool proposal vs executed-argument events.
- [ ] Add API mode/seed provenance without model exposure.
- [ ] Normalize volatile action IDs for replay.
- [ ] Implement config/artifact hashes.
- [ ] Implement observation replay format.

## P1 — Central project-specific experiments

### R09 — Guarded contract-aware boundary experiment

Pre-registered variants:

- B0 benchmark-valid minimal wrapper;
- B1 + strict typed validation;
- B2 + deterministic permission/company/resource policy;
- B3 + evidence-aware action/escalation;
- B4 confirmation extension reported separately unless partner promotes it to canonical policy.

- [ ] Build adversarial invalid-argument cases.
- [ ] Build cross-company/permission cases.
- [ ] Build duplicate/unnecessary action cases.
- [ ] Execute paired comparisons.
- [ ] Report safety constraints + quality/efficiency Pareto trade-offs.

### R10 — Evidence acquisition / stopping

- [ ] Compare reference-like/fixed investigation, free model loop and explicit evidence-sufficiency policy.
- [ ] Use fixed scenario overrides + deterministic seed perturbations.
- [ ] Measure premature stop, unnecessary calls, task success and escalation correctness.
- [ ] Only consider learned/calibrated risk after a strong rule baseline leaves a measured residual problem.

### R11 — Runtime comparison

Finalists remain:

- LangGraph;
- Pydantic AI/Graph;
- OpenAI Agents SDK.

- [ ] Implement identical ToolSpec/scenario contract.
- [ ] Test pre-action interception and safe pause/resume.
- [ ] Test duplicate-action resistance.
- [ ] Test deterministic fake-model/tool support.
- [ ] Test normalized trace completeness.
- [ ] Measure provider portability/complexity/overhead.
- [ ] Write runtime ADR.

### R12 — MCP topology

- [ ] Compare native tools vs MCP v2 adapter using same ToolSpec.
- [ ] Measure schema/argument fidelity, trace propagation, policy interception, latency and complexity.
- [ ] Write MCP ADR.

## P1 — Benchmark/statistics/models

### R13 — Split design

- [x] Independent random ticket split prohibited due shared asset/story leakage.
- [ ] Define final grouping by asset/storyline.
- [ ] Check modality/action/evidence coverage across candidate splits.
- [ ] Freeze locked test before architecture/model/prompt optimization.
- [ ] Hash/version split manifest.

### R14 — Statistical pilot

- [x] Separate agent/model reliability from environment robustness.
- [ ] Estimate within-scenario variability at fixed API seed.
- [ ] Estimate environment robustness across controlled modes/seeds.
- [ ] Estimate architecture discordance, latency/tokens and severe-event rates.
- [ ] Freeze final `k`, precision targets and confirmatory analysis.

### R15 — Model benchmark

- [x] Project-native Pareto protocol defined.
- [ ] Confirm permitted/available student providers immediately before execution.
- [ ] Screen candidates on development groups only.
- [ ] Validate survivors on validation groups.
- [ ] Select via hard safety constraints + quality/reliability/latency/resource Pareto evidence.
- [ ] Do not touch locked test during selection.

## P2 — Conditional techniques

### R16 — Retrieval/RAG

- [x] Actual corpus = 5 docs + dedicated knowledge API.
- [x] Direct API retrieval is mandatory baseline.
- [ ] Only test external lexical/dense/hybrid/rerank if retrieval error analysis shows need.
- [ ] Reject external RAG if no measurable end-to-end gain.

### R17 — Multi-agent

- [x] No multi-agent assumption.
- [ ] Establish strong single structured baseline first.
- [ ] Test decomposition only if failure analysis motivates it.

### R18 — Routing / prompt optimization

- [ ] Only after benchmark/evaluator freeze.
- [ ] Routing only if model benchmark shows complementary strengths.
- [ ] Optimization only on development/validation; hard safety constraints are not optimizer objectives.

### R19 — Observability backend / UI

- [ ] Compare Phoenix/Langfuse only after normalized TraceSchema v1 works independently of them.
- [ ] Select demo UI based on ability to prove agent + evaluator, not frontend novelty.

## Research Gate completion definition

`FROZEN-v1` requires:

1. normalized/conformance-tested API contract;
2. human-reviewed ScenarioSchema v1/gold oracles;
3. leakage-aware frozen split;
4. guarded-boundary experiment completed;
5. evidence/stopping experiment completed sufficiently to choose policy;
6. runtime + MCP ADRs completed;
7. statistical pilot completed and confirmatory protocol frozen;
8. project-native model evidence sufficient for a deployment candidate;
9. conditional complexity accepted/rejected with evidence;
10. no material artifact inconsistency silently unresolved;
11. remaining partner/instructor dependencies explicitly documented.

## Immediate execution sequence

**E0 contract normalization + E1 gold normalization in parallel → E2 ToolSpec/evaluator/trace harness → E3 split freeze → E4 B0–B3 → E5 evidence/stopping → E6/E7 runtime/MCP → E8 pilot/model benchmark → E9 conditional techniques → ADRs → `FROZEN-v1`.**