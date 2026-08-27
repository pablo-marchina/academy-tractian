# E14l — DEV-only 120B medium reasoning under strict schema + 4096

**Status:** real DEV measurement complete; hard gate failed  
**Date:** 2026-08-18  
**Scope:** DEV only

## Single intervention

Relative to E14k, E14l changed exactly one model request field:

```text
reasoning_effort: high
→ reasoning_effort: medium
```

Everything else remained frozen: Groq, `openai/gpt-oss-120b`, strict JSON Schema Structured Outputs, the exact existing public E10b output schema, `max_completion_tokens=4096`, temperature 0, real pacing 25 seconds, E14f repair, E14c/E14d/E14e/E10e/E10g/E11/E14 policies, E9 v3 scorer, DEV split, and hard-gate thresholds.

## Real result

The capture completed 6/6 with zero retries and zero repair calls. E9 v3 then ran exactly once and returned the following aggregate-only quality result:

```text
real_task_quality:             0.6190
decision_correctness:          0.3333
evidence_correctness:          1.0000
action_correctness:            0.0000
escalation_correctness:        0.0000
premature_action_rate:         0.0000
unsupported_final_claim_rate:  0.0000
proxy_vs_real_disagreement:    1.0000
```

The unchanged DEV gate failed. VALIDATION remains blocked. LOCKED_TEST remains untouched.

Public post-model diagnostics also showed zero semantic-repair triggers, zero E10d/E10e/E10g/E11 output changes, six concrete public-read equivalents, normalized public evidence-family counts of 5–9, and zero selective-reprocess checks.

## Decision

The reasoning/budget/response-format tuning family is closed. Both high and medium reasoning are operational under strict schema + 4096, but neither passes the semantic task gate. No further reasoning-effort, completion-budget, JSON-format or guard relaxation is justified from current public evidence.

Before preregistering the next candidate, inspect only the fixed E14l model outputs' public decision fields using `scripts/research/e14l_public_decision_distribution_diagnostic.py`. Do not use E9 rows or infer per-row private labels from aggregate metrics.
