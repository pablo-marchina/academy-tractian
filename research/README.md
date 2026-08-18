# Systematic Research Hub

**Status: E0–E3 frozen/complete; E4–E14 measured; E14/E14b/E14c/E14d/E14e real DEV gates failed; E14f preregistered, implemented, and structural dry-run passed**  
**Date:** 2026-08-17

The project has frozen contract/gold semantics, a framework-neutral experimental harness, a leakage-aware benchmark split, measured guarded-boundary/runtime/MCP/model experiments, and a hard safety/action gate that is still blocking downstream product integration.

Production architecture is **not frozen**. No demo/UI/integration phase is authorized while the DEV gate remains failed.

## Current real DEV gate sequence

| Metric | E14 | E14b | E14c | E14d | E14e | Required |
|---|---:|---:|---:|---:|---:|---:|
| Parsed / scoreable | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| Real task quality | 0.7381 | 0.6429 | 0.8333 | 0.8095 | 0.7619 | >= 0.8571 |
| Decision correctness | 0.5000 | 0.5000 | 0.6667 | 0.8333 | 0.6667 | >= 0.7500 |
| Evidence correctness | 0.5000 | 0.3333 | 1.0000 | 0.6667 | 0.5000 | 1.0000 |
| Action correctness | 0.1667 | 0.0000 | 0.1667 | 0.3333 | 0.3333 | >= 0.7500 |
| Escalation correctness | 1.0000 | 0.6667 | 1.0000 | 0.8333 | 0.8333 | 1.0000 |
| Premature action rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Unsupported final-claim rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

E14b is rejected. E14c, E14d and E14e are valid but failed DEV candidates. Cross-generation score deltas are not interpreted as paired causal effects.

VALIDATION remains blocked. LOCKED_TEST remains untouched.

## Structural findings retained

### E14c — public action endpoint representation

E14c fixed deterministic concrete-vs-template public action-endpoint comparison without rewriting model output. Concrete public action paths are canonicalized only for policy comparison.

### E14d — public evidence-resource representation

E14d fixed the analogous concrete-vs-template mismatch for the same ten historical public GET evidence families used by E10e/E10g. Thresholds remained unchanged. In the real E14d capture, E10g made zero changes under the corrected comparison view.

### E14d / E14e boundary closure

The E10e `too_few_concrete_evidence_resources_for_state_change` reprocess proposal was not a precedence bug. In both the E14d and E14e fixed captures, the specialized E14 counterfactual rejected the same class because it lacked a human-readable visible evidence-to-reprocess reason and had zero of the required two selective support-anchor classes. Therefore E10e threshold/order and E14 selective-reprocess semantics remain unchanged.

E14e replaced only the historical broad E10d marker-substring fallback with an explicit positive current-handoff phrase fallback. In the real E14e run, E10d changed two outputs only for strong preserved reasons:

```text
explicit_current_handoff_phrase:                         1
state_changing_action_requires_visible_human_loop_guard: 1
```

E10g and E11 changed zero outputs. The remaining E10e changes were one explicit `visible_rubric_needs_more_evidence` contradiction and one weak reprocess that E14 would also reject. This closes the current deterministic post-model boundary hypotheses. Further threshold relaxation is not supported by public evidence.

## E14f — conditional public semantic repair

E14f is preregistered as a single upstream intervention relative to E14e:

```text
conditional_public_semantic_consistency_repair_before_guards_only
```

The unchanged initial E14e model call runs first. Only a parseable draft containing a preregistered public contradiction receives one second call to the same GPT-OSS model. The repair receives only the original visible prompt, the model's own draft, and deterministic public consistency codes. It receives no scorer/oracle/VALIDATION/LOCKED_TEST information.

Repair triggers are limited to immediate-action contradictions already represented by the existing public policies: model-declared need for more evidence or unsafe-to-act, unsupported endpoint, decision/action conflict, autonomous state change below the unchanged public evidence minimum, or reprocess lacking the unchanged human-readable reason / two public support anchors.

The repair prompt is deliberately narrow: it forbids invented evidence, forbids adding irrelevant reads just to satisfy counts, treats planned GETs as plans rather than observations, preserves non-conflicting fields where possible, and does not enumerate all endpoints or the full evidence surface. This avoids repeating rejected E14b's broad always-on prompt expansion.

### E14f structural result

GitHub Actions run `32090619168` passed after a fixture-only correction. The first dry-run failure was caused by the weak synthetic fixture itself containing the causal word `because`, which the unchanged E14 policy correctly recognized as a human-readable reason; no E14f policy changed.

Successful structural output:

```text
status:                                   E14F_DEV_ONLY_PUBLIC_SEMANTIC_REPAIR_CAPTURE_PASS
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
target_reprocess_outputs_checked:         3
authorized_target_reprocess_outputs:      3
blocked_target_reprocess_outputs:         0
```

This is structural evidence only, not quality evidence. The next authorized step is one complete real E14f DEV-only capture followed by unchanged private E9 v3 scoring.

E14f artifacts:

- `123-e14e-fixed-capture-boundary-closure.md`
- `124-e14f-dev-only-public-semantic-repair.md`
- `125-e14f-structural-dry-run-result.md`
- `experiments/e14f-dev-only-public-semantic-repair-manifest.json`
- `../scripts/research/e14f_public_semantic_consistency.py`
- `../scripts/research/e14f_dev_only_public_semantic_repair.py`
- `../.github/workflows/research-e14f.yml`

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
- `results/e14-real-dev-sanitized-summary.json`
- `results/e14b-real-dev-sanitized-summary.json`
- `results/e14c-real-dev-sanitized-summary.json`
- `results/e14d-real-dev-sanitized-summary.json`
- `results/e14e-real-dev-sanitized-summary.json`

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
E14f complete real zero-cost DEV capture
→ unchanged E9 v3 private DEV scoring
→ if and only if every unchanged threshold passes: measurement-only DEV+VALIDATION
→ final safety/action gate decision
→ architecture decisions backed by accumulated experiments/ADRs
→ integration/demo implementation
→ final locked evaluation
```
