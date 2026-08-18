# E14f Structural Dry-run Result

**Date:** 2026-08-17 / 2026-08-18 UTC  
**Scope:** DEV-only structural fixture  
**Status:** PASS

GitHub Actions run `32090619168` passed after a fixture-only correction to make the weak synthetic reprocess example genuinely lack a human-readable causal reason. The first run failed because the weak fixture itself contained the word `because`, which the unchanged E14 public policy correctly recognizes as a causal marker. No E14f trigger, threshold, repair rule, model setting, or downstream policy changed in that correction.

Successful run output:

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

## Interpretation

The dry fixture contains three strong and three weak reprocess proposals. E14f leaves the three strong drafts untouched. The three weak drafts trigger the preregistered public consistency repair and are deterministically downgraded in dry-run mode before downstream guards. Therefore only the three strong reprocess proposals remain immediate E14 targets, and all three are authorized by the unchanged E14 selective-reprocess boundary.

This is structural evidence only. It demonstrates:

- conditional trigger behavior rather than an always-on prompt expansion;
- at most one semantic repair pass per triggered draft;
- zero residual preregistered public contradictions in the dry repaired outputs;
- preservation of completeness and schema validity;
- preservation of E14c/E14d/E14e plus E10e/E10g/E11/E14 downstream policies;
- no VALIDATION or LOCKED_TEST use.

It does **not** establish model-quality improvement. A complete real E14f DEV measurement followed by unchanged private E9 v3 scoring is still required.

## Real-run boundary

Real E14f must retain:

- Groq `openai/gpt-oss-20b`;
- temperature `0`;
- reasoning effort `medium`;
- max completion tokens `1600`;
- JSON Object Mode;
- the existing E14 provider retry/completeness policy;
- one semantic repair call maximum per parseable contradictory draft;
- no oracle/scorer/VALIDATION/LOCKED_TEST input to model or repair;
- unchanged E14 acceptance gate.

Only a full DEV gate pass may authorize measurement-only DEV+VALIDATION.
