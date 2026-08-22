# Wave 4 — TRACTIAN Artifact Ingestion

Status: **SOURCE INGESTED / RESEARCH GATE ADVANCED**

Date: 2026-08-15

## Source package

Received partner package: `inteli-tractian-project.zip`.

Package SHA-256:

`37546f7abad4c573ab36384a171161f3ba6c7258024341cc42f0881d9606d134`

The raw partner package is **not copied into this public research branch yet**. We retain hashes and derived research artifacts until redistribution/public-artifact policy is explicitly confirmed. This prevents accidental publication of evaluation material while preserving provenance.

## Delivered structure

The package contains:

- `STUDENT-GUIDE.md` — written project specification;
- `docs/api-contract.openapi.yaml` — intended OpenAPI 3.1 contract;
- `docs/support-tickets.md` — 17 support requests;
- `docs/test-scenarios.md` — 16 benchmark scenarios with policies, reference paths, expected resolutions and suggested metrics;
- `docs/data-schema.md` — synthetic data schema and probabilistic behavior documentation;
- `agent-input/` — material intended to be visible to the agent;
- `eval/` — evaluation-only material / gold reference;
- `api/` — FastAPI implementation, synthetic-data generator and functional tests;
- `data/` — generated parquet data + `seed.json`.

## Agent/evaluation boundary is now authoritative

The written guide explicitly separates:

### Agent-visible

- `agent-input/cases.json`;
- `agent-input/api-contract.openapi.yaml`;
- live HTTP API observations.

### Evaluator-only

- `eval/expected-paths.json`;
- `eval/test-scenarios.md`;
- source `data/cases.parquet` / narrative test material.

This resolves a major research question: **gold trajectories, root questions and expected resolutions must never be injected into the runtime agent context.**

Implementation consequence:

- evaluation runner owns the gold package;
- agent receives only normalized case input + bound user/environment context + canonical tools;
- traces are evaluated after execution;
- no runtime component should import evaluation/gold modules or files.

## Actual synthetic-data inventory

The source generator (`api/seed_data.py`) currently defines:

| Resource | Count |
|---|---:|
| Companies | 8 |
| Users | 10 |
| Assets | 26 |
| Points | 27 |
| Analyses | 10 |
| Baselines | 26 |
| RMS samples | 775 |
| Spectra | 9 |
| Data-quality rows | 26 |
| Models | 1 |
| Knowledge documents | 5 |
| Cases | 17 |
| Narrative scenarios | 16 |

Important: some written material says **24 analyses**, while the supplied generator contains **10**. Treat executable source/data as authoritative for runtime inventory and record the mismatch rather than silently correcting it.

## Case distribution

17 agent cases:

- Contextualizar: 3;
- Investigar: 9;
- Executar: 5.

10 unique primary assets are reused across the cases. Several assets deliberately connect investigation and execution stories, e.g.:

- G501: break-without-warning + human escalation;
- C710: delayed insight + specialist request;
- S420: false positive + retraining request;
- B204: stale post-maintenance analysis + reprocess;
- V301: data quality / RMS threshold / criticality update.

This means a random case split would create strong asset/story leakage. Split design must account for shared assets/base storylines.

## Independent package validation performed

The supplied FastAPI test suite contains **39 tests**. In the research environment, package dependencies could not be downloaded from PyPI because outbound DNS/network access is unavailable; therefore the already-supplied synthetic source constants were loaded into in-memory pandas tables and injected into the same API store boundary. Under that equivalent data source, the original test suite passed:

`39 passed`

This validates the application logic without changing the API handlers or tests. It does **not** replace a normal `make setup && make test` run in the user's local environment; that remains a reproducibility check to run on the actual workstation.

## Evidence hierarchy after artifact delivery

For project semantics, use this order:

1. written TAPI / Student Guide + explicit partner guidance;
2. executable API behavior and source implementation;
3. intended raw OpenAPI contract;
4. agent-input package;
5. machine-readable eval gold;
6. narrative scenarios / support-ticket documentation;
7. our derived hypotheses and experiments.

When two supplied artifacts conflict, do not silently choose one. Record the conflict and design the evaluator/tool layer around the executable semantics or ask for clarification if the difference affects grading.

## Research Gate impact

Now resolved or substantially narrowed:

- actual API surface is available;
- actual entities/fields are available;
- action permission classes can be mapped;
- seed/reproducibility mechanics are inspectable;
- knowledge corpus size/content class is known;
- canonical/gold case inventory is known;
- reference trajectory semantics are explicitly described as **reference, not script** in the scenario documentation;
- the API is local/synthetic and no external API credentials are required for the industrial environment itself.

Still unresolved outside the artifacts:

- student model/provider restrictions beyond the written feasibility guidance;
- hidden instructor/partner evaluation cases, if any;
- permission to publish the raw partner package/eval material publicly;
- exact expected final-demo conditions;
- final architecture decisions that require project-specific experiments.

## Next outputs

This ingestion unlocks:

- `API-MAP-v0`;
- `GOLD-MAP-v0`;
- contract/package quality audit;
- ScenarioSchema v1 normalization;
- canonical ToolSpec implementation;
- controlled runtime/MCP/model experiments.
