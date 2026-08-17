# Systematic Research Hub

**Status: E0–E3 frozen/complete; E4–E14 measured; E14 real DEV gate failed; E14b rejected; E14c real DEV failed; E14d preregistered and structural dry-run passed**  
**Date:** 2026-08-17

The project has frozen contract/gold semantics, a framework-neutral experimental harness, a leakage-aware benchmark split, measured guarded-boundary/runtime/MCP/model experiments, and a hard safety/action gate that is still blocking downstream product integration.

Production architecture is **not frozen**. No demo/UI/integration phase is authorized while the E14 gate remains failed.

## Current gate — E14 / E14b / E14c / E14d

The first complete recovered E14 real DEV measurement on Groq `openai/gpt-oss-20b` is valid and failed the unchanged quality gate:

| Metric | E14 real DEV | Required | Gate |
|---|---:|---:|---|
| Parsed outputs | 6 | 6 | PASS |
| Scoreable outputs | 6 | 6 | PASS |
| Real task quality | 0.7381 | >= 0.8571 | **FAIL** |
| Decision correctness | 0.5000 | >= 0.7500 | **FAIL** |
| Evidence correctness | 0.5000 | 1.0000 | **FAIL** |
| Action correctness | 0.1667 | >= 0.7500 | **FAIL** |
| Escalation correctness | 1.0000 | 1.0000 | PASS |
| Premature action rate | 0.0000 | 0.0000 | PASS |
| Unsupported final-claim rate | 0.0000 | 0.0000 | PASS |

E14b then changed only prompt policy on the same recovered GPT-OSS model/settings and was measured on the same DEV-only gate. It also completed 6/6 and was rejected:

| Metric | E14b real DEV | Required | Gate |
|---|---:|---:|---|
| Parsed outputs | 6 | 6 | PASS |
| Scoreable outputs | 6 | 6 | PASS |
| Real task quality | 0.6429 | >= 0.8571 | **FAIL** |
| Decision correctness | 0.5000 | >= 0.7500 | **FAIL** |
| Evidence correctness | 0.3333 | 1.0000 | **FAIL** |
| Action correctness | 0.0000 | >= 0.7500 | **FAIL** |
| Escalation correctness | 0.6667 | 1.0000 | **FAIL** |
| Premature action rate | 0.0000 | 0.0000 | PASS |
| Unsupported final-claim rate | 0.0000 | 0.0000 | PASS |

E14b is therefore **rejected**.

E14c then changed only deterministic public action-endpoint comparison semantics relative to recovered E14. The complete real DEV measurement again produced 6/6 scoreable outputs:

| Metric | E14c real DEV | Required | Gate |
|---|---:|---:|---|
| Parsed outputs | 6 | 6 | PASS |
| Scoreable outputs | 6 | 6 | PASS |
| Real task quality | 0.8333 | >= 0.8571 | **FAIL** |
| Decision correctness | 0.6667 | >= 0.7500 | **FAIL** |
| Evidence correctness | 1.0000 | 1.0000 | PASS |
| Action correctness | 0.1667 | >= 0.7500 | **FAIL** |
| Escalation correctness | 1.0000 | 1.0000 | PASS |
| Premature action rate | 0.0000 | 0.0000 | PASS |
| Unsupported final-claim rate | 0.0000 | 0.0000 | PASS |

E14c therefore remains a valid but failed DEV candidate. VALIDATION remains blocked and LOCKED_TEST remains untouched.

### E14c boundary diagnosis

E14c successfully recognized the public action endpoint representation mismatch: four concrete public action endpoints plus one already-canonical endpoint all resolved to the supported comparison form `POST /cases/{case_id}/escalate` where applicable.

The real fixed-capture boundary diagnostic then showed:

```text
E10d outputs changed: 0
E10e outputs changed: 2
E10g outputs changed: 3
E11 outputs changed: 0
E14 reprocess targets: 0
```

All three E10g changes had exactly one reason:

```text
balanced_guard_handoff_without_minimum_visible_evidence
```

A first sanitized evidence diagnostic showed the historical literal-template counter saw the three blocked handoffs as 0 / 0 / 1 distinct accepted public evidence families. That result did not justify lowering the existing E10g threshold of two.

A second shape diagnostic then compared only the same ten public GET evidence families already accepted by E10e/E10g while recognizing concrete frozen public routes as equivalent to their canonical route templates. The same three blocked handoffs became:

```text
2 / 5 / 8 distinct existing public evidence families
```

All three meet the unchanged E10g handoff threshold after representation normalization; none remains below threshold. This isolates a second deterministic representation mismatch rather than a threshold deficiency.

### E14d candidate

E14d is preregistered as a **single deterministic public evidence-resource comparison canonicalization change relative to E14c**.

E14d:

- preserves E14c public action-endpoint canonicalization;
- preserves exactly the existing ten E10e public GET evidence families;
- derives concrete-route equivalence from the frozen public ToolSpec source;
- counts canonical-template or equivalent concrete-path representation as the same distinct evidence family;
- does **not** rewrite stored model `evidence_plan` text;
- keeps the E10g human-handoff threshold at 2 distinct public evidence families;
- keeps the E10e autonomous state-change threshold at 3 distinct public evidence families;
- rejects wrong methods, unrelated routes and longer unknown route suffixes;
- changes no model, prompt, reasoning effort, completion budget, scorer, acceptance threshold or split.

Structural GitHub Actions run `32050822095` passed on commit `257630dae9206dfa1832d871b31ccdd16e60fd91` with 6/6 parsed/scoreable dry outputs, completeness pass, zero retries/repairs, VALIDATION false, ten accepted evidence families unchanged, and the inherited selective-reprocess fixture remaining selective at 3 authorized / 3 blocked.

The E14d-specific self-check separately proves threshold preservation:

- handoff with 2 equivalent concrete public GET families: allowed by the evidence minimum;
- handoff with 1 or 0 families: still blocked;
- state change with 3 equivalent concrete public GET families: satisfies the evidence minimum;
- state change with only 2: still blocked;
- wrong method / unknown longer route: contributes zero family.

E14d artifacts:

- `117-e14d-dev-only-public-evidence-resource-canonicalization.md`
- `118-e14d-structural-dry-run-result.md`
- `experiments/e14d-dev-only-public-evidence-resource-canonicalization-manifest.json`
- `../scripts/research/e14d_public_evidence_resource_normalization.py`
- `../scripts/research/e14d_dev_only_public_evidence_resource_canonicalization.py`
- `../.github/workflows/research-e14d.yml`

Sanitized prior records:

- `111-e14-real-dev-measurement-result.md`
- `results/e14-real-dev-sanitized-summary.json`
- `113-e14b-real-dev-measurement-result.md`
- `results/e14b-real-dev-sanitized-summary.json`
- `116-e14c-real-dev-measurement-result.md`
- `results/e14c-real-dev-sanitized-summary.json`
- `../scripts/research/e14_semantic_boundary_diagnostic.py`
- `../scripts/research/e14c_e10g_handoff_evidence_diagnostic.py`
- `../scripts/research/e14c_e10g_handoff_evidence_shape_diagnostic.py`

Required DEV acceptance remains unchanged:

| Target | Required |
|---|---:|
| Parsed outputs | 6 |
| Scoreable calls | 6 |
| Premature action rate | 0.0 |
| Unsupported final-claim rate | 0.0 |
| Real task quality | >= 0.8571 |
| Decision correctness | >= 0.75 |
| Action correctness | >= 0.75 |
| Evidence correctness | 1.0 |
| Escalation correctness | 1.0 |
| LOCKED_TEST accessed | false |

## Frozen evidence/contracts

### E0 — Contract frozen

- `34-e0-contract-freeze-v1.md`
- `frozen/e0-contract-freeze.manifest.json`
- `frozen/API-BEHAVIOR-MAP-v1.json`

Frozen facts include 18 operations / 17 path templates, duplicate `/assets/{assetId}` GET+PATCH handling, explicit canonical argument transformation, runner-bound identity/seed, and accepted-event/non-persistent action semantics.

### E1 — Gold / ScenarioSchema frozen

- `35-e1-gold-freeze-v1.md`
- `frozen/e1-gold-freeze.manifest.json`

Frozen benchmark structure: 16 narrative scenarios, 17 tickets and 10 asset/story groups. Machine trajectories are references, not scripts. Gold remains evaluator-only and is never copied into agent context.

### E2 — Executable harness complete

`e2/` contains the framework-neutral experimental infrastructure:

- executable ScenarioSchema models;
- 18-operation Canonical ToolSpec registry;
- runner-owned identity/seed binding;
- B0 HTTP transport;
- strict B1 argument validation;
- deterministic B2 permission/resource guard;
- evidence-aware B3 action gate;
- integrated `HarnessRunner`;
- TraceSchema and deterministic replay;
- deterministic evaluator suite.

Completion report: `39-e2-integrated-completion-report.md`.

### E3 — Benchmark split frozen

- **DEV:** `asset_G501`, `asset_C710`, `asset_S420`, `asset_M208`, `asset_M101` — 5 groups / 8 scenarios.
- **VALIDATION:** `asset_B204`, `asset_M102` — 2 groups / 3 scenarios.
- **LOCKED_TEST:** `asset_V301`, `asset_M605`, `asset_M205` — 3 groups / 5 scenarios.

The split is group-level and leakage-aware. LOCKED_TEST remains forbidden for architecture/model/prompt/runtime selection.

## Experiment progression

### E4–E7 — boundary, runtime and MCP

The guarded-boundary experiment established that deterministic policy/resource guards can contain unsafe proposals that minimally wrapped variants execute. Subsequent runtime/MCP spikes were used as project-specific evidence rather than architecture commitments.

Relevant records begin at `41-e4-guarded-boundary-experiment-preregistration.md` and continue through `59-e7-topology-adr.md`.

### E8–E9 — model candidate and evaluator-side quality

E8 established a zero-cost real model path and fixed-output capture. E9 added evaluator-side semantic scoring while preserving strict separation between agent-visible inputs and private gold.

Relevant records: `60`–`73`.

### E10–E11 — DEV calibration and full safety remeasurement

DEV-only iterations improved evidence/action/escalation behavior, but full DEV+VALIDATION remeasurements exposed a persistent premature-action regression. E11 introduced independent action authorization and passed DEV-only, yet the full safety gate still failed because the authorization remained over-permissive for reprocess.

Relevant records: `74`–`98`.

### E12–E14d — root cause, provider recovery, completeness and public representation

E12 identified the dominant class as:

```text
policy_executed_but_over_permissive_or_wrong_authorization_class
```

E13 then overcorrected and blocked every parsed reprocess target. E14 added complete capture and selective reprocess authorization. During real E14 measurement, the originally configured Groq model was externally shut down; the replacement `openai/gpt-oss-20b` required a documented compatibility recovery for completion budget before a valid 6/6 measurement was possible.

Recovered E14 failed DEV quality. E14b prompt reconciliation regressed and was rejected. E14c then fixed concrete-vs-template action endpoint comparison and substantially improved quality while preserving safety, but the fixed-capture diagnosis exposed an analogous concrete-vs-template mismatch in the evidence-family counter used by E10e/E10g. E14d is the corresponding single-change deterministic evidence comparison correction. Its structural dry-run passed; real DEV measurement is the next authorized step.

Relevant records: `99`–`118` plus the sanitized boundary/evidence diagnostics.

## Explicit non-decisions

The following remain intentionally unfrozen:

- final model/provider choice;
- final agent runtime/framework;
- final MCP topology;
- RAG/vector DB;
- multi-agent decomposition/routing;
- persistent memory;
- observability backend/vendor;
- UI/demo flow;
- final production architecture.

## Source hierarchy

1. Updated TAPI / written Student Guide / explicit partner requirements.
2. Executable supplied API behavior/source.
3. Raw OpenAPI and supplied agent/eval/data artifacts.
4. Kickoff guidance when not contradicted by delivered artifacts.
5. Primary research and official framework documentation.
6. Reproducible project experiments.
7. Hypotheses.

## Methodological rules

- Do not freeze architecture because implementation has started.
- Framework-neutral infrastructure may precede architecture selection; architecture-changing choices require project-specific evidence and an ADR.
- Boundary/proxy metrics do not equal real task success.
- Scripted/dry-run outputs validate instrumentation and policy shape only; they are not model-quality evidence.
- Private evaluator/gold must never enter model prompts or public policy logic.
- VALIDATION is measurement-only after a DEV candidate passes; it is not a tuning split.
- LOCKED_TEST remains off-limits until final evaluation.
- Do not commit raw fixed outputs, private oracle rows, output hashes, private local paths or evaluator-only labels.
- Provider-forced model substitutions must be documented; historical cross-model deltas must not be interpreted causally.

## Critical path

```text
E14d complete real zero-cost DEV capture
→ E9 v3 private DEV scoring
→ if and only if every unchanged E14 gate threshold passes: measurement-only DEV+VALIDATION rerun
→ safety/action gate decision
→ architecture decisions backed by accumulated experiments/ADRs
→ integration/demo implementation
→ final locked evaluation
```

If schedule pressure appears, cut optional complexity first. Do not weaken contract conformance, gold isolation, evaluator validity, split integrity, completeness gates or locked-test discipline.
