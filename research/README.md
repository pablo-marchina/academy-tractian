# Systematic Research Hub

Status: **ACTIVE — Wave 5 / E0 + E1 executing in parallel / Research Gate not passed**

The project now has the updated TAPI, kickoff evidence and the actual TRACTIAN project package. Production architecture is still **not frozen**: partner artifacts have replaced many hypotheses with executable facts, and E0/E1 are now converting those facts into trustworthy contract and benchmark representations before framework selection.

## Current execution — 2026-08-16

### E0 — contract normalization/conformance

Implemented and executed:

- `scripts/research/e0_contract_pipeline.py`
- `31-e0-contract-normalization-execution.md`

Current result:

- duplicate-aware parsing works;
- duplicate `/assets/{assetId}` GET/PATCH mapping is merged losslessly in a private candidate;
- normalized route surface and FastAPI runtime match structurally at **18 operations / 17 path templates**;
- runtime semantic probes executed;
- declared-vs-runtime differences are classified rather than silently reconciled;
- `NORMALIZED-CONTRACT-v1` is **not frozen yet** while final naming/transformation manifest and API behavior metadata are completed.

### E1 — gold normalization / ScenarioSchema v1

Implemented and executed:

- `scripts/research/e1_normalize_gold.py`
- `schemas/scenario-v1-draft.schema.json`
- `32-e1-gold-normalization-execution.md`
- `33-e1-cross-modality-pilot-review.md`

Current result:

- **16/16** narrative scenarios mechanically source-normalized;
- **17/17** tickets mapped;
- **10** split groups retained;
- no missing expected narrative sections;
- **10/16** scenarios show machine-vs-narrative endpoint-set divergence, confirming that raw `expected_path` cannot be the complete oracle;
- cross-modality review complete for **4/16** scenarios;
- action-oracle semantics refined after the pilot;
- remaining **12/16** scenarios still require review before benchmark authority.

Evaluator-only normalized outputs stay under private/ignored paths until publication policy is clarified.

## Source hierarchy

1. Updated TAPI / written Student Guide and partner package.
2. Executable supplied API behavior/source.
3. Raw OpenAPI + agent/eval/data artifacts.
4. Confidence-labeled kickoff guidance where not contradicted by artifacts.
5. Primary research/specifications/official framework docs.
6. Reproducible experiments in this repository.

Raw package hash and derived findings are recorded in `26-tractian-artifact-ingestion-wave-4.md`. The raw package/eval gold is not copied into the public branch until publication policy is confirmed.

## What the delivered artifacts resolve

- 17 agent-input cases and 16 narrative evaluation scenarios are available.
- Agent-visible material and evaluator-only gold are explicitly separated.
- Reference engineer trajectories are references, **not scripts**.
- The local FastAPI runtime exposes 18 operations across 17 path templates.
- Actual permission/action classes, synthetic entities and response-mode implementation are inspectable.
- Actions return accepted execution events and do not persist state in the supplied store.
- API response modes are controllable through deterministic explicit seeds; omitted seed is also deterministic in executable code.
- Knowledge corpus is five documents with dedicated search/document endpoints.
- Only 10 primary asset/story groups support 17 cases, so random ticket splitting would leak related stories.

## High-impact package findings

### Contract integrity

The raw OpenAPI YAML contains `/assets/{assetId}` twice (GET and PATCH). A naïve YAML loader can silently overwrite one operation. Therefore raw contract → duplicate-aware audit → normalized derived contract → runtime conformance is mandatory before tool/code generation.

### Raw API is intentionally/coarsely permissive

The supplied action handlers mainly enforce resource existence, coarse permission and justification length. Independent probes show malformed semantic action payloads can still be accepted.

This creates a strong project-specific experiment around a **guarded contract-aware tool boundary** rather than assuming raw API acceptance equals correct agent behavior.

### Backend does not enforce company/resource ownership

User context exposes company/permissions, but the simplified backend does not reject cross-company action targets when the caller has the coarse permission. Agent/system policy and API enforcement must therefore be evaluated separately.

### Benchmark integrity requires bound context

- `x-user-id` must be bound by the case/session, not selected by the model.
- response `seed` must be bound by the runner/evaluator, not exposed as a semantic tool argument.

These are experiment-integrity/security constraints, not optional agent reasoning choices.

### Action oracle changed from pre-API assumption

Because accepted actions do not persist state, final-state equality is not the correct primary oracle for these action scenarios. Evaluate decision/tool/target/args/policy/justification/accepted response/no duplicate instead.

### Gold requires normalization

`eval/expected-paths.json` is useful but materially less complete than narrative scenario policies, expected resolutions and P1/P2 criteria. Exact sequence match must not be the benchmark. ScenarioSchema v1 merges both sources into separate structured oracles.

### Kickoff confirmation guidance is demoted

The kickoff described requester confirmation for mutations, but canonical delivered action scenarios do not model confirmation as a universal precondition. Confirmation remains a **separate guarded safety experiment** unless partner clarification promotes it to official case policy.

## Research status

| Area | Status after E0/E1 start |
|---|---|
| Requirements/scope | Strongly resolved; a few instructor/model/publication questions remain |
| API/domain | Actual runtime/source mapped (`API-MAP-v0`) |
| Contract | E0 executable pipeline active; 18/17 structural conformance achieved; final normalization freeze pending |
| Package/gold | Inventory/audit complete; E1 source normalization 16/16 complete; review 4/16 complete |
| Canonical ToolSpec | Exact constraints known; waits on E0/E1 freeze |
| Evaluation | ScenarioSchema v1 draft source-derived and refined; final oracle review pending |
| Safety/policy | Real raw-API weaknesses support controlled guarded-boundary experiment |
| Evidence/stopping | Actual response modes/overrides known; experiment ready after harness |
| Reliability | Fixed-environment model reliability and seed-based API robustness can be separated |
| Runtime | LangGraph / Pydantic AI/Graph / OpenAI Agents SDK remain candidates; project spike pending |
| MCP | Same ToolSpec native-vs-MCP experiment pending |
| Models | Project benchmark method ready; provider availability to confirm at execution time |
| RAG | Direct knowledge API baseline favored; external RAG conditional |
| Multi-agent/routing/optimization | Conditional; no evidence yet to add them |
| Statistics | Pilot unlocked after harness/split; exact `k` still not guessed |

## Central experiment program

The strongest current hypothesis candidate remains:

> **Does a guarded, contract-aware tool boundary materially improve argument correctness and safety over a minimally wrapped baseline while preserving task success and acceptable efficiency?**

Staged variants:

- B0 benchmark-valid minimal wrapper;
- B1 + strict typed argument validation;
- B2 + deterministic permission/company/resource policy guard;
- B3 + explicit evidence-aware action/escalation policy;
- B4 confirmation extension, separately reported unless official policy changes.

After this, runtime/MCP/model choices are evaluated while holding canonical tools/scenarios/evaluator constant.

## Files

### Waves 1–3

`00`–`23` contain research protocol, requirements, literature/evidence synthesis, candidate stack, safety/reliability/statistics, state/memory/context, observability, model/RAG methodology, runtime/MCP deep dives, ScenarioSchema v0, TraceSchema v0, spikes and Swagger-audit preparation.

### 2026-08-13 evidence updates

- `24-updated-tapi-impact-2026-08-13.md`
- `25-kickoff-evidence-2026-08-13.md`

### Wave 4 — delivered TRACTIAN artifacts

- `26-tractian-artifact-ingestion-wave-4.md`
- `27-api-map-v0-wave-4.md`
- `28-gold-map-v0-wave-4.md`
- `29-contract-and-package-quality-audit-wave-4.md`
- `30-post-artifact-experiment-program-wave-4.md`

### Wave 5 — E0/E1 execution

- `31-e0-contract-normalization-execution.md`
- `32-e1-gold-normalization-execution.md`
- `33-e1-cross-modality-pilot-review.md`
- `schemas/scenario-v1-draft.schema.json`
- `../scripts/research/e0_contract_pipeline.py`
- `../scripts/research/e1_normalize_gold.py`

### Schemas / decisions

- `schemas/scenario-v0.schema.json`
- `schemas/trace-v0.schema.json`
- `sources.md`
- `../docs/adr/000-template.md`

## Immediate sequence

**Finish E0 naming/manifest/API-BEHAVIOR-MAP-v1 + review remaining 12 E1 scenarios → freeze contract/scenario candidates → Canonical ToolSpec/evaluator/TraceSchema v1 → leakage-aware split → B0–B3 → evidence/stopping → runtime/MCP → pilot/model benchmark → conditional techniques only if justified → ADRs → `FROZEN-v1`.**
