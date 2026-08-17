# Systematic Research Hub

**Status: E0–E3 frozen/complete; E4–E14 measured; E14/E14b/E14c/E14d real DEV gates failed; E14e preregistered, implemented, and structural dry-run passed**  
**Date:** 2026-08-17

The project has frozen contract/gold semantics, a framework-neutral experimental harness, a leakage-aware benchmark split, measured guarded-boundary/runtime/MCP/model experiments, and a hard safety/action gate that is still blocking downstream product integration.

Production architecture is **not frozen**. No demo/UI/integration phase is authorized while the DEV gate remains failed.

## Current DEV gate progression

All values below are complete six-call DEV measurements on the recovered Groq `openai/gpt-oss-20b` configuration unless noted otherwise.

| Metric | E14 | E14b | E14c | E14d | Required |
|---|---:|---:|---:|---:|---:|
| Parsed outputs | 6 | 6 | 6 | 6 | 6 |
| Scoreable calls | 6 | 6 | 6 | 6 | 6 |
| Real task quality | 0.7381 | 0.6429 | 0.8333 | 0.8095 | >= 0.8571 |
| Decision correctness | 0.5000 | 0.5000 | 0.6667 | 0.8333 | >= 0.7500 |
| Evidence correctness | 0.5000 | 0.3333 | 1.0000 | 0.6667 | 1.0000 |
| Action correctness | 0.1667 | 0.0000 | 0.1667 | 0.3333 | >= 0.7500 |
| Escalation correctness | 1.0000 | 0.6667 | 1.0000 | 0.8333 | 1.0000 |
| Premature action rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Unsupported final-claim rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

E14b is rejected. E14c and E14d are valid but failed DEV candidates. Cross-generation score differences are not treated as paired causal effects because each real candidate used a new model generation; E14d also required two provider retries. Deterministic policy behavior is interpreted separately from model-quality deltas.

VALIDATION remains blocked. LOCKED_TEST remains untouched.

## What E14c established

A fixed-capture diagnosis showed that historical guards compared canonical action endpoint templates literally and could reject equivalent concrete public action paths. E14c corrected only that comparison view while leaving stored model output unchanged.

The real E14c capture then showed E10g as the dominant downstream blocker: three handoff proposals were downgraded for `balanced_guard_handoff_without_minimum_visible_evidence`.

## What E14d established

A sanitized fixed-capture evidence-shape diagnostic showed those three E10g handoffs were counted historically as `0 / 0 / 1` accepted public evidence families but became `2 / 5 / 8` when concrete public GET paths were recognized as equivalent to the same ten already-accepted frozen route families.

E14d therefore preserved the family set and thresholds while canonicalizing only the evidence comparison view. Structural CI passed and the real DEV capture exercised the correction on all six calls.

Real E14d boundary effects:

```text
E10d escalation consistency:       2 outputs changed
E10e premature action guard:       2 outputs changed
E10g balanced action guard:        0 outputs changed
E11 independent authorization:     0 outputs changed
E14 selective reprocess targets:   0
```

Thus the E14d structural hypothesis about E10g was supported: under the corrected public evidence-family view, E10g made zero changes.

### E14d remaining-boundary diagnosis

The two E10e reasons were:

- one `visible_rubric_needs_more_evidence` — explicit model-visible safety and therefore preserved;
- one `too_few_concrete_evidence_resources_for_state_change` on canonical reprocess with two normalized public evidence families.

A public-policy counterfactual showed the specialized E14 selective-reprocess boundary would also reject that reprocess because it had no human-readable evidence-to-reprocess reason and zero selective support anchors. Therefore E10e threshold/order and E14 two-anchor semantics remain unchanged.

The two E10d reasons were:

- one `state_changing_action_requires_visible_human_loop_guard` — preserved;
- one `visible_human_escalation_marker` — diagnosed further because historical E10d accepts broad marker substrings such as `risk`, `safety`, `severity`, and `escalation`.

The fixed-capture polarity diagnostic for that one marker-triggered call found:

```text
requires_human_escalation before E10d: false
rubric needs_human_escalation:         false
decision escalation_candidate:         false
specialist/case-escalate endpoint:      false
explicit positive current handoff:     0
explicit negative handoff:             0
conditional/contingent handoff:         0
bare/generic marker context only:       1
```

This supplies a public-policy basis for E14e without using private scorer labels.

## E14e candidate

E14e is preregistered as one deterministic intervention relative to E14d:

```text
deterministic_explicit_current_handoff_semantics_refinement_only
```

Only the historical E10d free-text marker fallback changes.

E14e requires an **explicit positive current human-handoff phrase** for that fallback. Bare risk/escalation tokens, explicit negation, or conditional/contingent escalation language do not by themselves create a current handoff.

The following E10d conditions remain unchanged and authoritative:

1. `requires_human_escalation=true`;
2. rubric `needs_human_escalation=true`;
3. `decision_class=escalation_candidate`;
4. specialist/case-escalate endpoint;
5. state-changing immediate action requiring the existing visible human-loop guard.

E14c action-endpoint canonicalization and E14d public evidence-family canonicalization remain active. E10e, E10g, E11, E14, every threshold, prompt, model setting, scorer, and split remain unchanged.

### E14e structural result

GitHub Actions run `32061728940` passed on commit `b00b1d36c67f263678c3b6973a7424ce942aa9b0`:

```text
status:                                   E14E_DEV_ONLY_EXPLICIT_CURRENT_HANDOFF_SEMANTICS_CAPTURE_PASS
total_calls:                              6
parsed_model_outputs_available:           6
scoreable_calls:                          6
validation_ran:                           false
dry_run:                                  true
completeness_pass:                        true
retry_count:                              0
repair_count:                             0
target_reprocess_outputs_checked:         6
authorized_target_reprocess_outputs:      3
blocked_target_reprocess_outputs:         3
```

Candidate-specific self-checks separately proved that bare, negative, and conditional handoff language does not trigger the refined fallback; explicit positive current-handoff language does; and every stronger structured E10d branch plus the state-changing-action human-loop branch remains preserved.

E14e artifacts:

- `120-e14e-dev-only-explicit-current-handoff-semantics.md`
- `121-e14e-structural-dry-run-result.md`
- `experiments/e14e-dev-only-explicit-current-handoff-semantics-manifest.json`
- `../scripts/research/e14e_explicit_current_handoff_semantics.py`
- `../scripts/research/e14e_dev_only_explicit_current_handoff_semantics.py`
- `../.github/workflows/research-e14e.yml`

Recent sanitized records:

- `111-e14-real-dev-measurement-result.md`
- `113-e14b-real-dev-measurement-result.md`
- `116-e14c-real-dev-measurement-result.md`
- `119-e14d-real-dev-measurement-result.md`
- `results/e14-real-dev-sanitized-summary.json`
- `results/e14b-real-dev-sanitized-summary.json`
- `results/e14c-real-dev-sanitized-summary.json`
- `results/e14d-real-dev-sanitized-summary.json`
- `../scripts/research/e14_semantic_boundary_diagnostic.py`
- `../scripts/research/e14d_remaining_boundary_diagnostic.py`
- `../scripts/research/e14d_e10d_escalation_marker_polarity_diagnostic.py`

## Unchanged acceptance gate

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

`e2/` contains the framework-neutral experimental infrastructure: executable ScenarioSchema models; the 18-operation Canonical ToolSpec registry; runner-owned identity/seed binding; B0 HTTP transport; strict B1 argument validation; deterministic B2 permission/resource guard; evidence-aware B3 action gate; integrated `HarnessRunner`; TraceSchema/replay; and deterministic evaluators.

Completion report: `39-e2-integrated-completion-report.md`.

### E3 — Benchmark split frozen

- **DEV:** 5 groups / 8 scenarios.
- **VALIDATION:** 2 groups / 3 scenarios.
- **LOCKED_TEST:** 3 groups / 5 scenarios.

The split is group-level and leakage-aware. LOCKED_TEST remains forbidden for architecture/model/prompt/runtime selection.

## Methodological rules

- Boundary/proxy metrics do not equal real task success.
- Dry-run outputs validate instrumentation and policy shape only; they are not model-quality evidence.
- Private evaluator/gold must never enter model prompts or public policy logic.
- VALIDATION is measurement-only after a DEV candidate passes; it is not a tuning split.
- LOCKED_TEST remains off-limits until final evaluation.
- Do not commit raw fixed outputs, private oracle rows, output hashes, private local paths, or evaluator-only labels.
- Provider/model substitutions must be documented; incomparable cross-model deltas are not causal evidence.
- Separate model generations under the same model are also not treated as paired causal estimates for policy deltas.

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

## Critical path

```text
E14e complete real zero-cost DEV capture
→ E9 v3 private DEV scoring
→ if and only if every unchanged E14 gate threshold passes: measurement-only DEV+VALIDATION rerun
→ safety/action gate decision
→ architecture decisions backed by accumulated experiments/ADRs
→ integration/demo implementation
→ final locked evaluation
```

If schedule pressure appears, cut optional complexity first. Do not weaken contract conformance, gold isolation, evaluator validity, split integrity, completeness gates, or locked-test discipline.
