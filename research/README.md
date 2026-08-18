# Systematic Research Hub

**Status: E0–E3 frozen/complete; E4–E14 measured; E14/E14b/E14c/E14d/E14e/E14f real DEV gates failed; E14g model-only candidate preregistered and structural dry-run passed**  
**Date:** 2026-08-17

The project has frozen contract/gold semantics, a framework-neutral experimental harness, a leakage-aware benchmark split, measured guarded-boundary/runtime/MCP/model experiments, and a hard safety/action gate that is still blocking downstream product integration.

Production architecture is **not frozen**. No demo/UI/integration phase is authorized while the DEV gate remains failed.

## Current real DEV gate sequence

| Metric | E14 | E14b | E14c | E14d | E14e | E14f | Required |
|---|---:|---:|---:|---:|---:|---:|---:|
| Parsed / scoreable | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| Real task quality | 0.7381 | 0.6429 | 0.8333 | 0.8095 | 0.7619 | 0.6429 | >= 0.8571 |
| Decision correctness | 0.5000 | 0.5000 | 0.6667 | 0.8333 | 0.6667 | 0.5000 | >= 0.7500 |
| Evidence correctness | 0.5000 | 0.3333 | 1.0000 | 0.6667 | 0.5000 | 0.1667 | 1.0000 |
| Action correctness | 0.1667 | 0.0000 | 0.1667 | 0.3333 | 0.3333 | 0.3333 | >= 0.7500 |
| Escalation correctness | 1.0000 | 0.6667 | 1.0000 | 0.8333 | 0.8333 | 0.5000 | 1.0000 |
| Premature action rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Unsupported final-claim rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

E14b is rejected. E14c–E14f are valid but failed DEV candidates. Cross-generation score deltas are not interpreted as paired causal effects.

VALIDATION remains blocked. LOCKED_TEST remains untouched.

## Deterministic boundary findings retained

### E14c — public action endpoint representation

E14c fixed deterministic concrete-vs-template public action-endpoint comparison without rewriting model output. Concrete public action paths are canonicalized only for policy comparison.

### E14d — public evidence-resource representation

E14d fixed the analogous concrete-vs-template mismatch for the same ten historical public GET evidence families used by E10e/E10g. Thresholds remained unchanged. In the real E14d capture, E10g made zero changes under the corrected comparison view.

### E14d / E14e boundary closure

The E10e `too_few_concrete_evidence_resources_for_state_change` reprocess proposal was not a precedence bug. In both E14d and E14e fixed captures, the specialized E14 counterfactual rejected the same class because it lacked a human-readable visible evidence-to-reprocess reason and had zero of the required two selective support-anchor classes. E10e threshold/order and E14 selective-reprocess semantics remain unchanged.

E14e replaced only the historical broad E10d marker-substring fallback with an explicit positive current-handoff phrase fallback. In real E14e, E10d changed outputs only for strong preserved reasons. E10g and E11 changed zero outputs. Current public evidence does not support further downstream guard or threshold relaxation.

## E14f — conditional public semantic repair

E14f moved upstream: a parseable draft received at most one second call only when deterministic public consistency checks found a preregistered contradiction. The repair received the original visible prompt, the model's own draft, and public consistency codes only; no scorer/oracle/VALIDATION/LOCKED_TEST information.

### E14f structural result

GitHub Actions run `32090619168` passed after a fixture-only correction. The successful dry-run was 6/6, with zero residual public violations after its synthetic repair calls.

### E14f real DEV result

Real E14f was complete and safe but failed the absolute task-quality gate:

```text
real_task_quality:      0.6429
decision_correctness:   0.5000
evidence_correctness:   0.1667
action_correctness:     0.3333
escalation_correctness: 0.5000
premature_action_rate:  0.0000
unsupported_claim_rate: 0.0000
```

The semantic repair triggered once for `immediate_action_while_needs_more_evidence`, produced one parseable repaired response and left zero registered public consistency violations. After repair, E10e/E10g/E11 changed zero outputs and E14 saw zero target reprocess outputs. This supports closing the current downstream-boundary hypothesis set: internal/public consistency alone is not sufficient for benchmark task correctness.

Do not attribute the aggregate E14e→E14f score delta causally to the repair because the model was regenerated.

## E14g — GPT-OSS 120B model-selection candidate

E14g is preregistered as a **single model-only intervention** on top of E14f:

```text
openai/gpt-oss-20b
→ openai/gpt-oss-120b
```

Everything else stays frozen: provider, initial prompt, conditional repair policy, temperature 0, reasoning `medium`, completion budget 1600, JSON Object Mode, E14c/E14d/E14e/E10e/E10g/E11/E14 policies, scorer, split and acceptance thresholds.

E14g is a model-selection experiment, not a paired causal estimate against E14f. Absolute gate performance is the decision criterion.

### E14g structural result

GitHub Actions run `32091361228`, job `95573999025`, passed:

```text
status:                                   E14G_DEV_ONLY_GPT_OSS_120B_MODEL_SELECTION_CAPTURE_PASS
model:                                    openai/gpt-oss-120b
total_calls:                              6
parsed_model_outputs_available:           6
scoreable_calls:                          6
validation_ran:                           false
dry_run:                                  true
completeness_pass:                        true
retry_count:                              0
syntax_repair_count:                      0
semantic_repair_triggered_calls:          3
semantic_repair_calls:                    3
semantic_repair_residual_violation_calls: 0
```

This is structural evidence only. Before the real run, the no-inference Groq model-list preflight must confirm `openai/gpt-oss-120b` is active and the operator must confirm the intended zero-cost Free Plan boundary.

## Required DEV acceptance

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

### E1 — Gold / ScenarioSchema frozen

- `35-e1-gold-freeze-v1.md`
- `frozen/e1-gold-freeze.manifest.json`

Gold remains evaluator-only and is never copied into agent context.

### E2 — Executable harness complete

`e2/` contains the framework-neutral experimental infrastructure, canonical ToolSpec registry, strict boundary guards, trace/replay, and deterministic evaluator suite.

### E3 — Benchmark split frozen

- **DEV:** 5 groups / 8 scenarios.
- **VALIDATION:** 2 groups / 3 scenarios.
- **LOCKED_TEST:** 3 groups / 5 scenarios.

The split is group-level and leakage-aware. VALIDATION is not a tuning split. LOCKED_TEST remains forbidden until final evaluation.

## Recent sanitized records

- `111-e14-real-dev-measurement-result.md`
- `113-e14b-real-dev-measurement-result.md`
- `116-e14c-real-dev-measurement-result.md`
- `119-e14d-real-dev-measurement-result.md`
- `122-e14e-real-dev-measurement-result.md`
- `123-e14e-fixed-capture-boundary-closure.md`
- `125-e14f-structural-dry-run-result.md`
- `126-e14f-real-dev-measurement-result.md`
- `127-e14g-dev-only-gpt-oss-120b-model-selection.md`
- `128-e14g-structural-dry-run-result.md`
- `results/e14-real-dev-sanitized-summary.json`
- `results/e14b-real-dev-sanitized-summary.json`
- `results/e14c-real-dev-sanitized-summary.json`
- `results/e14d-real-dev-sanitized-summary.json`
- `results/e14e-real-dev-sanitized-summary.json`
- `results/e14f-real-dev-sanitized-summary.json`

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

## Methodological rules

- Do not freeze architecture because implementation has started.
- Boundary/proxy metrics do not equal real task success.
- Scripted/dry-run outputs validate instrumentation and policy shape only; they are not model-quality evidence.
- Private evaluator/gold must never enter model prompts or public policy logic.
- VALIDATION is measurement-only after a DEV candidate passes; it is not a tuning split.
- LOCKED_TEST remains off-limits until final evaluation.
- Do not commit raw fixed outputs, private oracle rows, output hashes, private local paths or evaluator-only labels.
- Provider/model substitutions and separate model generations invalidate naive paired causal claims.

## Critical path

```text
E14g no-inference Groq model preflight
→ one complete real zero-cost E14g DEV capture
→ unchanged E9 v3 private DEV scoring
→ if and only if every unchanged threshold passes: measurement-only DEV+VALIDATION
→ final safety/action gate decision
→ architecture decisions backed by accumulated experiments/ADRs
→ integration/demo implementation
→ final locked evaluation
```
