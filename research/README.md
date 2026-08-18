# Systematic Research Hub

**Status: E0–E3 frozen/complete; E4–E14 measured; E14/E14b/E14c/E14d/E14e/E14f/E14g/E14k real DEV gates failed; E14h/E14i/E14j failed operationally; E14l preregistered/implemented and structural dry-run passed**  
**Date:** 2026-08-18

The project has frozen contract/gold semantics, a framework-neutral experimental harness, a leakage-aware benchmark split, measured guarded-boundary/runtime/MCP/model experiments, and a hard safety/action gate that is still blocking downstream product integration.

Production architecture is **not frozen**. No demo/UI/integration phase is authorized while the DEV gate remains failed.

## Current valid real DEV quality measurements

| Metric | E14 | E14b | E14c | E14d | E14e | E14f | E14g | E14k | Required |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Parsed / scoreable | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| Real task quality | 0.7381 | 0.6429 | 0.8333 | 0.8095 | 0.7619 | 0.6429 | 0.6667 | 0.6429 | >= 0.8571 |
| Decision correctness | 0.5000 | 0.5000 | 0.6667 | 0.8333 | 0.6667 | 0.5000 | 0.5000 | 0.3333 | >= 0.7500 |
| Evidence correctness | 0.5000 | 0.3333 | 1.0000 | 0.6667 | 0.5000 | 0.1667 | 0.8333 | 0.8333 | 1.0000 |
| Action correctness | 0.1667 | 0.0000 | 0.1667 | 0.3333 | 0.3333 | 0.3333 | 0.1667 | 0.1667 | >= 0.7500 |
| Escalation correctness | 1.0000 | 0.6667 | 1.0000 | 0.8333 | 0.8333 | 0.5000 | 0.1667 | 0.1667 | 1.0000 |
| Premature action rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Unsupported final-claim rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

E14h/E14i/E14j are intentionally excluded because they produced zero parsed real outputs and therefore no valid task-quality measurement. Cross-generation score deltas are descriptive only; they are not deterministic paired causal effects.

VALIDATION remains blocked. LOCKED_TEST remains untouched.

## Retained deterministic findings

### E14c — public action endpoint representation

E14c fixed deterministic concrete-vs-template public action-endpoint comparison without rewriting model output.

### E14d — public evidence-resource representation

E14d fixed the analogous concrete-vs-template mismatch for the same historical public GET evidence families used by E10e/E10g. Thresholds remained unchanged.

### E14d / E14e boundary closure

The E10e `too_few_concrete_evidence_resources_for_state_change` reprocess proposal was not a precedence bug. The specialized E14 counterfactual rejected the same class because it lacked a human-readable evidence-to-reprocess reason and the required selective support anchors. E10e threshold/order and E14 selective-reprocess semantics remain unchanged.

E14e replaced only the historical broad E10d marker-substring fallback with explicit-current-handoff semantics. Current public evidence does not support further downstream guard or threshold relaxation.

## E14f — conditional public semantic repair

E14f moved upstream: a parseable draft received at most one second call only when deterministic public consistency checks found a preregistered contradiction. The repair received the original visible prompt, the model's own draft, and public consistency codes only; no scorer/oracle/VALIDATION/LOCKED_TEST information.

Real E14f was complete and safe but failed the absolute task-quality gate. Internal/public consistency alone is therefore insufficient for benchmark correctness.

## E14g — GPT-OSS 120B model selection

E14g changed only the model from `openai/gpt-oss-20b` to `openai/gpt-oss-120b`, preserving E14f, temperature 0, reasoning `medium`, completion budget 1600, JSON Object Mode, deterministic policies, scorer and gate.

Real E14g was 6/6 complete with zero semantic-repair or downstream guard changes but failed the gate. All six outputs contained concrete public-read equivalents and normalized evidence-family counts were 6, 7 or 8.

## E14h / E14i / E14j — operational failures at high reasoning + 1600

E14h changed only reasoning effort `medium -> high`. E14i preserved that candidate while recording `E14_REASONING_FORMAT=hidden`. E14j preserved high reasoning and 1600 tokens while switching to strict JSON Schema Structured Outputs.

All three real captures produced 0/6 parsed outputs. Their null scorer metrics are not quality scores. Historical provider telemetry also over-classified generic `failed_generation` payloads as JSON validation failures; that telemetry was refined without changing request semantics.

## E14k — 4096 completion-budget recovery

E14k changed only:

```text
max_completion_tokens: 1600
→ max_completion_tokens: 4096
```

while keeping 120B, `reasoning_effort=high`, strict JSON Schema, temperature 0, prompts, repair, policies, scorer, and gate frozen.

The real E14k capture restored operational completeness:

```text
parsed / scoreable:       6 / 6
retry_count:               0
real_task_quality:         0.6429
decision_correctness:      0.3333
evidence_correctness:      0.8333
action_correctness:        0.1667
escalation_correctness:    0.1667
premature_action_rate:     0.0000
unsupported_claim_rate:    0.0000
```

All six calls had concrete public-read equivalents, evidence-family counts ranged from 5 to 8, and E14f/E10d/E10e/E10g/E11 made zero changes. E14k therefore resolved the operational blocker but still failed the absolute quality gate. The remaining problem class is upstream semantic decision/action/escalation selection, not another deterministic guard relaxation.

## E14l — medium reasoning inside the operational strict-4096 stack

E14l is preregistered as exactly one change relative to E14k:

```text
reasoning_effort: high
→ reasoning_effort: medium
```

Frozen unchanged:

- Groq provider;
- `openai/gpt-oss-120b`;
- `E14_REASONING_FORMAT=hidden` environment value (no GPT-OSS effect claimed);
- strict JSON Schema Structured Outputs;
- exact existing public E10b output schema;
- `max_completion_tokens=4096`;
- temperature 0;
- real pacing 25 seconds;
- E14f repair and E14c/E14d/E14e/E10e/E10g/E11/E14 policies;
- E9 v3 scorer;
- DEV split and hard gate.

### E14l structural result

GitHub Actions run `32133232144`, job `95698738513`, passed:

```text
status:                                   E14L_DEV_ONLY_120B_MEDIUM_REASONING_STRICT_4096_CAPTURE_PASS
model:                                    openai/gpt-oss-120b
parent_reasoning_effort:                  high
reasoning_effort:                         medium
response_format:                          json_schema
strict:                                   true
max_completion_tokens:                    4096
total_calls:                              6
parsed_model_outputs_available:           6
scoreable_calls:                          6
validation_ran:                           false
dry_run:                                  true
completeness_pass:                        true
retry_count:                              0
repair_count:                             0
```

Artifact ID: `9322971501`. This is structural evidence only.

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
- `132-e14h-real-dev-operational-failure.md`
- `136-e14k-dev-only-high-reasoning-4096-completion-budget.md`
- `137-e14k-structural-dry-run-result.md`
- `138-e14k-real-dev-measurement-result.md`
- `139-e14l-dev-only-120b-medium-reasoning-strict-4096.md`
- `140-e14l-structural-dry-run-result.md`
- `results/e14g-real-dev-sanitized-summary.json`
- `results/e14h-real-dev-sanitized-operational-summary.json`
- `results/e14k-real-dev-sanitized-summary.json`

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
one real zero-cost E14l DEV capture
→ only if capture is 6/6: unchanged E9 v3 private DEV scoring exactly once
→ only if every unchanged threshold passes: measurement-only DEV+VALIDATION
→ final safety/action gate decision
→ architecture decisions backed by accumulated experiments/ADRs
→ integration/demo implementation
→ final locked evaluation
```
