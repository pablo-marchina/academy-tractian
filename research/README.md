# Systematic Research Hub

**Status: E0–E3 frozen/complete; E4–E14 measured; E14 real DEV gate failed; E14b DEV-only candidate implemented and structural dry-run passed**  
**Date:** 2026-08-17

The project has frozen contract/gold semantics, a framework-neutral experimental harness, a leakage-aware benchmark split, measured guarded-boundary/runtime/MCP/model experiments, and a hard safety/action gate that is still blocking downstream product integration.

Production architecture is **not frozen**. No demo/UI/integration phase is authorized while the E14 gate remains failed.

## Current gate — E14 / E14b

The first complete recovered E14 real DEV measurement on Groq `openai/gpt-oss-20b` is now valid:

| Capture validity metric | Result |
|---|---:|
| Fixed DEV calls | 6 |
| Parsed outputs | 6 |
| Scoreable outputs | 6 |
| Retries | 0 |
| Syntax repairs | 0 |
| VALIDATION ran | false |
| LOCKED_TEST accessed | false |

Private E9 v3 scoring then produced the following sanitized aggregate result:

| Metric | E14 real DEV | Required | Gate |
|---|---:|---:|---|
| Real task quality | 0.7381 | >= 0.8571 | **FAIL** |
| Decision correctness | 0.5000 | >= 0.7500 | **FAIL** |
| Evidence correctness | 0.5000 | 1.0000 | **FAIL** |
| Action correctness | 0.1667 | >= 0.7500 | **FAIL** |
| Escalation correctness | 1.0000 | 1.0000 | PASS |
| Premature action rate | 0.0000 | 0.0000 | PASS |
| Unsupported final-claim rate | 0.0000 | 0.0000 | PASS |

The real run produced zero target reprocess outputs, so the E14 selective-reprocess boundary was not exercised by the model outputs. The active blocker is therefore upstream: evidence coverage, endpoint/action selection, and decision reconciliation.

Sanitized record:

- `111-e14-real-dev-measurement-result.md`
- `results/e14-real-dev-sanitized-summary.json`

E14b is the next candidate **inside the same E14 hard gate**. It changes prompt policy only for the provider-forced GPT-OSS replacement model:

```text
visible packet
→ concrete evidence plan
→ supported-endpoint consideration
→ decision/action/escalation reconciliation
→ existing E14 selective-reprocess boundary
→ fixed output
→ private E9 v3 scorer
```

E14b preserves:

- Groq `openai/gpt-oss-20b`;
- temperature `0`;
- reasoning effort `medium`;
- max completion tokens `1600`;
- JSON Object Mode;
- E14 completeness behavior;
- E14 selective reprocess boundary;
- DEV groups/repeats;
- E9 v3 scorer;
- every acceptance threshold;
- no VALIDATION tuning and no LOCKED_TEST.

E14b artifacts:

- `112-e14b-dev-only-evidence-action-decision-reconciliation.md`
- `experiments/e14b-dev-only-evidence-action-decision-reconciliation-manifest.json`
- `../scripts/research/e14b_dev_only_evidence_action_decision_reconciliation.py`
- `../.github/workflows/research-e14b.yml`

Structural E14b dry-run has passed in GitHub Actions. This is instrumentation/policy-shape evidence only; real model quality remains unmeasured until the next complete DEV capture and private E9 v3 score.

Required E14b DEV acceptance remains unchanged:

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

### E12–E14b — root cause, provider recovery, completeness and upstream reconciliation

E12 identified the dominant class as:

```text
policy_executed_but_over_permissive_or_wrong_authorization_class
```

E13 then overcorrected and blocked every parsed reprocess target. E14 added complete capture and selective reprocess authorization. During real E14 measurement, the originally configured Groq model was externally shut down; the replacement `openai/gpt-oss-20b` required a documented compatibility recovery for completion budget before a valid 6/6 measurement was possible.

That complete E14 measurement failed the DEV quality gate while preserving safety/escalation and produced no reprocess-target outputs. E14b therefore moves the active DEV intervention upstream to evidence→endpoint→decision reconciliation without changing the post-output boundary or scorer.

Relevant records: `99`–`112`.

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
E14b real zero-cost DEV capture
→ E9 v3 private DEV scoring
→ if and only if every unchanged E14 gate threshold passes: measurement-only DEV+VALIDATION rerun
→ safety/action gate decision
→ architecture decisions backed by accumulated experiments/ADRs
→ integration/demo implementation
→ final locked evaluation
```

If schedule pressure appears, cut optional complexity first. Do not weaken contract conformance, gold isolation, evaluator validity, split integrity, completeness gates or locked-test discipline.
