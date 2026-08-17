# Systematic Research Hub

**Status: E0–E3 frozen/complete; E4–E14 measured; E14 real DEV gate failed; E14b rejected; E14c preregistered and structural dry-run passed**  
**Date:** 2026-08-17

The project has frozen contract/gold semantics, a framework-neutral experimental harness, a leakage-aware benchmark split, measured guarded-boundary/runtime/MCP/model experiments, and a hard safety/action gate that is still blocking downstream product integration.

Production architecture is **not frozen**. No demo/UI/integration phase is authorized while the E14 gate remains failed.

## Current gate — E14 / E14b / E14c

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

E14b is therefore **rejected**. VALIDATION remains blocked and LOCKED_TEST remains untouched.

### E14b semantic/boundary diagnostic

A sanitized no-provider-call diagnostic over the already-fixed E14b capture established:

- 6/6 outputs parsed;
- final outputs contained zero immediate actions;
- E10e changed 3 outputs: 2 because of `unsupported_action_endpoint_visible`, 1 because of `visible_rubric_not_safe_to_act`;
- E10g changed zero outputs;
- E11 changed zero outputs;
- E14 selective reprocess changed zero outputs and saw zero target reprocess actions;
- one output was changed by the E10d escalation-consistency guard;
- all three non-`none` action endpoints had the public shape `POST /cases/<concrete-id>/escalate`.

Because E10e only applies when `should_take_action_now=true`, its three changed outputs prove that three model-produced immediate-action proposals existed before E10e and all were downgraded before E10g/E11/E14 could evaluate the original action state.

The frozen public ToolSpec registry declares case escalation as `POST /cases/{caseId}/escalate`, while historical guards compare against snake-case template forms such as `post /cases/{case_id}/escalate`. Exact-template equality therefore rejects a valid concrete path even though it represents the same public action operation.

### E14c candidate

E14c is preregistered as a **single deterministic public-contract endpoint-comparison normalization change relative to recovered E14**. It does not inherit the rejected E14b prompt-policy change.

E14c:

- derives the five action endpoint shapes from the literal frozen `action(...)` declarations in `research/e2/tool_registry.py`;
- canonicalizes only a temporary policy-comparison view;
- does **not** rewrite the stored model endpoint or other model output;
- applies that comparison view before E10d, E10e, E10g, E11 and E13/E14 endpoint decisions;
- rejects wrong methods, query/fragment additions, extra text and unknown shapes;
- preserves the explicit `safe_to_act=false` blocking condition;
- changes no model, prompt, reasoning effort, completion budget, scorer, threshold or split.

Structural GitHub Actions run `32033397539` passed on commit `8f1705eaf332eb3f1eedcb51e15b0f5794c6f97f` with 6/6 parsed/scoreable dry outputs, completeness pass, zero retries/repairs, VALIDATION false, and the inherited selective-reprocess fixture remaining selective at 3 authorized / 3 blocked. The structural self-check separately verifies that a concrete case-escalation endpoint is recognized while the same endpoint with `safe_to_act=false` remains blocked.

E14c artifacts:

- `114-e14c-dev-only-public-endpoint-canonicalization.md`
- `115-e14c-structural-dry-run-result.md`
- `experiments/e14c-dev-only-public-endpoint-canonicalization-manifest.json`
- `../scripts/research/e14c_public_action_endpoint_normalization.py`
- `../scripts/research/e14c_dev_only_public_endpoint_canonicalization.py`
- `../.github/workflows/research-e14c.yml`

Sanitized prior records:

- `111-e14-real-dev-measurement-result.md`
- `results/e14-real-dev-sanitized-summary.json`
- `113-e14b-real-dev-measurement-result.md`
- `results/e14b-real-dev-sanitized-summary.json`
- `../scripts/research/e14_semantic_boundary_diagnostic.py`

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

### E12–E14c — root cause, provider recovery, completeness and boundary representation

E12 identified the dominant class as:

```text
policy_executed_but_over_permissive_or_wrong_authorization_class
```

E13 then overcorrected and blocked every parsed reprocess target. E14 added complete capture and selective reprocess authorization. During real E14 measurement, the originally configured Groq model was externally shut down; the replacement `openai/gpt-oss-20b` required a documented compatibility recovery for completion budget before a valid 6/6 measurement was possible.

The complete recovered E14 measurement failed the DEV quality gate. E14b moved the intervention upstream to evidence→endpoint→decision prompt reconciliation but regressed quality and was rejected. The fixed-capture diagnostic then isolated a brittle public endpoint representation mismatch in E10e. E14c is the corresponding single-change deterministic correction, structurally validated but not yet real-model measured.

Relevant records: `99`–`115` plus the sanitized semantic-boundary diagnostic.

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
E14c complete real zero-cost DEV capture
→ E9 v3 private DEV scoring
→ if and only if every unchanged E14 gate threshold passes: measurement-only DEV+VALIDATION rerun
→ safety/action gate decision
→ architecture decisions backed by accumulated experiments/ADRs
→ integration/demo implementation
→ final locked evaluation
```

If schedule pressure appears, cut optional complexity first. Do not weaken contract conformance, gold isolation, evaluator validity, split integrity, completeness gates or locked-test discipline.