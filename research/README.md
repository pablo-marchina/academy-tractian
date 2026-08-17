# Systematic Research Hub

**Status: E0–E3 frozen/complete; E4–E14 measured; E14/E14b/E14c/E14d/E14e real DEV gates failed; no E14f candidate preregistered**  
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

### E14d remaining-boundary diagnosis

The one E10e `too_few_concrete_evidence_resources_for_state_change` reprocess proposal was not a precedence bug: even if restored to its pre-E10e immediate-action state, the specialized E14 reprocess policy rejected it for `missing_human_readable_evidence_to_reprocess_reason` with zero support anchors. Therefore E10e threshold/order remains unchanged.

A separate E10d diagnostic found one historical `visible_human_escalation_marker` change where every stronger handoff condition was false and no explicit positive/negative/conditional handoff phrase existed; only bare escalation/risk context remained.

### E14e — explicit current-handoff semantics

E14e replaced only the historical broad E10d marker-substring fallback with an explicit positive current-handoff phrase fallback. It preserved all stronger E10d branches, E14c endpoint canonicalization, E14d evidence canonicalization, E10e/E10g/E11/E14 policies and all thresholds.

Structural GitHub Actions run `32061728940` passed. The complete real E14e DEV capture then produced:

```text
E10d outputs changed: 2
  explicit_current_handoff_phrase:                         1
  state_changing_action_requires_visible_human_loop_guard: 1
E10e outputs changed: 2
E10g outputs changed: 0
E11 outputs changed: 0
E14 reprocess targets: 0
```

The refined E10d policy therefore exercised only intended strong reasons in the real run. E14e still failed the overall quality gate, so no further E10d relaxation is supported by current public evidence.

## Current blocker

The next step is **fixed-capture diagnosis of the two E10e changes in E14e**. No new provider call, no private rescoring, no VALIDATION and no E14f preregistration should occur until those public reason classes are known.

If both E10e changes are explicit visible safety contradictions or otherwise structurally justified, the remaining failure should be treated as upstream model semantic behavior rather than another deterministic boundary-representation defect.

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
E14e fixed-capture E10e reason diagnosis
→ decide whether any public structural policy defect remains
→ if no structural defect remains: stop boundary relaxation and address upstream model semantic behavior with a separately preregistered intervention, if justified
→ only after a DEV candidate passes every unchanged threshold: measurement-only DEV+VALIDATION
→ final safety/action gate decision
→ architecture decisions backed by accumulated experiments/ADRs
→ integration/demo implementation
→ final locked evaluation
```
