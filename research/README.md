# Systematic Research Hub

**Status: E0–E3 frozen/complete; E4–E14 measured; E14/E14b/E14c/E14d/E14e/E14f/E14g real DEV gates failed; E14h failed operationally; E14i provider-compatibility candidate preregistered/implemented and structural dry-run passed**  
**Date:** 2026-08-18

The project has frozen contract/gold semantics, a framework-neutral experimental harness, a leakage-aware benchmark split, measured guarded-boundary/runtime/MCP/model experiments, and a hard safety/action gate that is still blocking downstream product integration.

Production architecture is **not frozen**. No demo/UI/integration phase is authorized while the DEV gate remains failed.

## Current valid real DEV quality measurements

| Metric | E14 | E14b | E14c | E14d | E14e | E14f | E14g | Required |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Parsed / scoreable | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| Real task quality | 0.7381 | 0.6429 | 0.8333 | 0.8095 | 0.7619 | 0.6429 | 0.6667 | >= 0.8571 |
| Decision correctness | 0.5000 | 0.5000 | 0.6667 | 0.8333 | 0.6667 | 0.5000 | 0.5000 | >= 0.7500 |
| Evidence correctness | 0.5000 | 0.3333 | 1.0000 | 0.6667 | 0.5000 | 0.1667 | 0.8333 | 1.0000 |
| Action correctness | 0.1667 | 0.0000 | 0.1667 | 0.3333 | 0.3333 | 0.3333 | 0.1667 | >= 0.7500 |
| Escalation correctness | 1.0000 | 0.6667 | 1.0000 | 0.8333 | 0.8333 | 0.5000 | 0.1667 | 1.0000 |
| Premature action rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Unsupported final-claim rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

E14h is intentionally excluded from this quality table because it produced zero parsed outputs and therefore no valid quality measurement. Cross-generation score deltas are not interpreted as deterministic paired causal effects.

VALIDATION remains blocked. LOCKED_TEST remains untouched.

## Retained deterministic findings

### E14c — public action endpoint representation

E14c fixed deterministic concrete-vs-template public action-endpoint comparison without rewriting model output.

### E14d — public evidence-resource representation

E14d fixed the analogous concrete-vs-template mismatch for the same ten historical public GET evidence families used by E10e/E10g. Thresholds remained unchanged.

### E14d / E14e boundary closure

The E10e `too_few_concrete_evidence_resources_for_state_change` reprocess proposal was not a precedence bug. In both E14d and E14e fixed captures, the specialized E14 counterfactual rejected the same class because it lacked a human-readable evidence-to-reprocess reason and had zero required selective support-anchor classes. E10e threshold/order and E14 selective-reprocess semantics remain unchanged.

E14e replaced only the historical broad E10d marker-substring fallback with explicit-current-handoff semantics. Current public evidence does not support further downstream guard or threshold relaxation.

## E14f — conditional public semantic repair

E14f moved upstream: a parseable draft received at most one second call only when deterministic public consistency checks found a preregistered contradiction. The repair received the original visible prompt, the model's own draft, and public consistency codes only; no scorer/oracle/VALIDATION/LOCKED_TEST information.

Real E14f was complete and safe but failed the absolute task-quality gate. Its one repair removed the targeted public contradiction, yet task quality remained low. Internal/public consistency alone is therefore insufficient for benchmark correctness.

## E14g — GPT-OSS 120B model selection

E14g changed only the model from `openai/gpt-oss-20b` to `openai/gpt-oss-120b`, preserving E14f, temperature 0, reasoning `medium`, completion budget 1600, JSON Object Mode, deterministic policies, scorer and gate.

Real E14g was 6/6 complete with zero semantic-repair or downstream guard changes but failed the gate. All six outputs contained concrete public-read equivalents and normalized evidence-family counts were 6, 7 or 8; bigger model capacity at unchanged medium reasoning was not sufficient.

## E14h — high reasoning operational failure

E14h changed only:

```text
E14_REASONING_EFFORT=medium
→ E14_REASONING_EFFORT=high
```

while preserving GPT-OSS 120B, JSON Object Mode, temperature 0 and the 1600 completion-token budget.

The real E14h attempt did **not** produce a valid quality measurement:

```text
total_calls: 6
parsed_calls: 0
schema_valid_calls: 0
attempts_per_call: 3
provider_attempt_failures: 18
provider_failure_category: json_generation_validation_failure (18/18)
provider_usage_observed_calls: 0
completion_budget_exhaustion_supported: false
```

E9 subsequently saw `scoreable_calls=0`; its null metrics are not quality scores. The fixed-capture diagnostic concluded `provider_failure_present_budget_exhaustion_not_isolated`, so no token-budget increase is justified from E14h.

Current Groq reasoning documentation states that when JSON mode is used with reasoning models, `reasoning_format` must be `parsed` or `hidden`. The E14h transport omitted this field, creating a specific provider-compatibility hypothesis.

## E14i — hidden reasoning format compatibility correction

E14i is preregistered as exactly one provider-configuration change relative to E14h:

```text
E14_REASONING_FORMAT: unset/provider-default
→ E14_REASONING_FORMAT: hidden
```

Everything else remains frozen:

- Groq provider;
- `openai/gpt-oss-120b`;
- `reasoning_effort=high`;
- `max_completion_tokens=1600`;
- temperature 0;
- JSON Object Mode;
- initial prompt and E14f conditional repair;
- E14c/E14d/E14e/E10e/E10g/E11/E14 policies and thresholds;
- E9 v3 scorer;
- DEV split and hard gate.

`hidden` was chosen because only final JSON is consumed; it satisfies the provider JSON-mode requirement without exposing reasoning in the capture or changing the final schema.

The transport change is retrocompatible: `reasoning_format` is added to the Groq payload only when `E14_REASONING_FORMAT` is explicitly set, so historical candidates with the variable unset preserve their previous payload shape.

### E14i structural result

GitHub Actions run `32123377075`, job `95668510359`, passed:

```text
status:                                   E14I_DEV_ONLY_GPT_OSS_120B_HIGH_REASONING_HIDDEN_FORMAT_CAPTURE_PASS
model:                                    openai/gpt-oss-120b
reasoning_effort:                         high
reasoning_format:                         hidden
max_completion_tokens:                    1600
total_calls:                              6
parsed_model_outputs_available:           6
scoreable_calls:                          6
validation_ran:                           false
dry_run:                                  true
completeness_pass:                        true
retry_count:                              0
repair_count:                             0
semantic_repair_triggered_calls:          3
semantic_repair_calls:                    3
semantic_repair_residual_violation_calls: 0
```

This is structural evidence only.

### Mandatory provider compatibility precondition

Before any real benchmark capture, run exactly one synthetic non-benchmark inference using `120B + high + reasoning_format=hidden + json_object + 1600`. It uses no TRACTIAN task packet, oracle, scorer rows, VALIDATION or LOCKED_TEST material.

Required status:

```text
E14I_GROQ_HIGH_JSON_HIDDEN_COMPATIBILITY_PREFLIGHT_PASS
```

Only a passing compatibility preflight authorizes one real E14i DEV capture.

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

- E0 contract: `34-e0-contract-freeze-v1.md`, `frozen/e0-contract-freeze.manifest.json`, `frozen/API-BEHAVIOR-MAP-v1.json`
- E1 gold: `35-e1-gold-freeze-v1.md`, `frozen/e1-gold-freeze.manifest.json`
- E2 executable harness: `e2/`
- E3 group-level leakage-aware split: DEV 5 groups / 8 scenarios; VALIDATION 2 / 3; LOCKED_TEST 3 / 5

Gold remains evaluator-only and is never copied into agent context. VALIDATION is not a tuning split.

## Recent sanitized records

- `129-e14g-real-dev-measurement-result.md`
- `130-e14h-dev-only-gpt-oss-120b-high-reasoning.md`
- `131-e14h-structural-dry-run-result.md`
- `132-e14h-real-dev-operational-failure.md`
- `133-e14i-dev-only-gpt-oss-120b-high-reasoning-hidden-format.md`
- `134-e14i-structural-dry-run-result.md`
- `results/e14g-real-dev-sanitized-summary.json`
- `results/e14h-real-dev-sanitized-operational-summary.json`

## Explicit non-decisions

The following remain intentionally unfrozen: final model/provider choice, final agent runtime/framework, MCP topology, RAG/vector DB, multi-agent decomposition/routing, persistent memory, observability backend/vendor, UI/demo flow, and final production architecture.

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
E14i one-call non-benchmark Groq compatibility preflight
→ only if PASS: one complete real zero-cost E14i DEV capture
→ only if capture is 6/6: unchanged E9 v3 private DEV scoring exactly once
→ only if every unchanged threshold passes: measurement-only DEV+VALIDATION
→ final safety/action gate decision
→ architecture decisions backed by accumulated experiments/ADRs
→ integration/demo implementation
→ final locked evaluation
```
