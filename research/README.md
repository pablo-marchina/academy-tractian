# Systematic Research Hub

Status: **ACTIVE — Wave 4 / Research Gate not passed**

The project now has the updated TAPI, kickoff evidence and the actual TRACTIAN project package. Production architecture is still **not frozen**: partner artifacts have replaced many hypotheses with executable facts, but runtime/model/MCP/policy/evidence strategy decisions must now be resolved through project-specific experiments.

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

`eval/expected-paths.json` is useful but materially less complete than narrative scenario policies, expected resolutions and P1/P2 criteria. Exact sequence match must not be the benchmark. ScenarioSchema v1 must merge both sources into structured oracles.

### Kickoff confirmation guidance is now demoted

The kickoff described requester confirmation for mutations, but canonical delivered action scenarios do not model confirmation as a universal precondition. Confirmation remains a **separate guarded safety experiment** unless partner clarification promotes it to official case policy.

## Research status

| Area | Status after Wave 4 |
|---|---|
| Requirements/scope | Strongly resolved; a few instructor/model/publication questions remain |
| API/domain | Actual runtime/source mapped (`API-MAP-v0`) |
| Package/gold | Inventory and divergence audit complete (`GOLD-MAP-v0`) |
| Contract | Critical duplicate-key/typing issues identified; normalization implementation pending |
| Canonical ToolSpec | Exact constraints now known; implementation/experiment pending |
| Evaluation | v0 contracts exist; v1 normalization from actual scenarios pending |
| Safety/policy | Real raw-API weaknesses now support controlled guarded-boundary experiment |
| Evidence/stopping | Actual response modes/overrides known; experiment ready to implement |
| Reliability | Can now cleanly separate fixed-environment agent reliability from seed-based API robustness |
| Runtime | LangGraph / Pydantic AI/Graph / OpenAI Agents SDK still candidates; project spike pending |
| MCP | Same ToolSpec native-vs-MCP experiment pending |
| Models | Project benchmark method ready; provider availability still to confirm at execution time |
| RAG | Direct knowledge API baseline strongly favored; external RAG conditional |
| Multi-agent/routing/optimization | Still conditional; no evidence yet to add them |
| Statistics | Pilot now unlocked; exact `k` still not guessed |

## Central experiment program

The strongest current hypothesis candidate is not “framework X is best”; it is:

> **Does a guarded, contract-aware tool boundary materially improve argument correctness and safety over a minimally wrapped baseline while preserving task success and acceptable efficiency?**

Staged variants:

- B0 benchmark-valid minimal wrapper;
- B1 + strict typed argument validation;
- B2 + deterministic permission/company/resource policy guard;
- B3 + explicit evidence-aware action/escalation policy;
- B4 confirmation extension, separately reported unless official policy changes.

After this, runtime/MCP/model choices are evaluated while holding the canonical tools/scenarios/evaluator constant.

## Experiment decomposition enabled by actual seed semantics

### Canonical task correctness

Use a fixed environment (typically explicit complete seed where not overridden) and normalized scenario oracles.

### Environment robustness

Vary deterministic explicit seeds to induce targeted complete/partial/inconclusive/conflict/unavailable observations.

### Agent/model reliability

Hold environment seed/observations fixed and repeat stochastic agent/model runs.

This prevents API variability and model variability from being mixed into one uninterpretable score.

## Files

### Waves 1–3

`00`–`23` contain research protocol, requirements, literature/evidence synthesis, candidate stack, safety/reliability/statistics, state/memory/context, observability, model/RAG methodology, runtime/MCP deep dives, ScenarioSchema v0, TraceSchema v0, spikes and Swagger-audit preparation.

### 2026-08-13 evidence updates

- `24-updated-tapi-impact-2026-08-13.md`
- `25-kickoff-evidence-2026-08-13.md`

### Wave 4 — delivered TRACTIAN artifacts

- `26-tractian-artifact-ingestion-wave-4.md` — package inventory, hash, source hierarchy and validation notes.
- `27-api-map-v0-wave-4.md` — actual endpoints/actions/permissions/state/seed semantics.
- `28-gold-map-v0-wave-4.md` — cases/scenarios/reference-path analysis and split/oracle implications.
- `29-contract-and-package-quality-audit-wave-4.md` — contract/data/documentation inconsistencies and normalization policy.
- `30-post-artifact-experiment-program-wave-4.md` — pre-registered implementation/experiment sequence.

### Schemas / decisions

- `schemas/scenario-v0.schema.json`
- `schemas/trace-v0.schema.json`
- `sources.md`
- `../docs/adr/000-template.md`

## Immediate sequence

**Normalize/conformance-test OpenAPI → human-review gold into ScenarioSchema v1 → implement canonical ToolSpec/evaluator/TraceSchema v1 → freeze leakage-aware split → run B0–B3 guarded-boundary experiment → evidence/stopping experiment → runtime/MCP spike → statistical pilot/model benchmark → conditional techniques only if justified → ADRs → `FROZEN-v1`.**
