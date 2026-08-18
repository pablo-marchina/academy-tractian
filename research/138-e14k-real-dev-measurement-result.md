# E14k real DEV measurement result

**Date:** 2026-08-18  
**Scope:** DEV only  
**Status:** complete real measurement; unchanged hard gate failed

E14k resolved the prior operational completeness blocker at the preregistered 4096 completion-token budget. The real capture completed 6/6 calls with zero retries and zero parse failures, so unchanged E9 v3 was allowed to score the fixed outputs exactly once.

## Sanitized aggregate result

```text
parsed / scoreable:       6 / 6
real_task_quality:        0.6429   FAIL
decision_correctness:     0.3333   FAIL
evidence_correctness:     0.8333   FAIL
action_correctness:       0.1667   FAIL
escalation_correctness:   0.1667   FAIL
premature_action_rate:    0.0000   PASS
unsupported_claim_rate:   0.0000   PASS
proxy_vs_real_disagreement: 0.8333
LOCKED_TEST accessed:     false
```

The candidate therefore fails the unchanged DEV hard gate and does not authorize VALIDATION.

## Public-only structural interpretation

The capture had:

- six concrete public-read equivalents;
- normalized public evidence-family counts of 5, 6, 7, or 8 for every call;
- zero E14f semantic-repair triggers;
- zero E10d/E10e/E10g/E11 output changes;
- zero selective-reprocess checks.

Thus, for this fixed E14k capture, the remaining failure is not explained by the closed deterministic representation/guard boundaries. The outputs were already internally acceptable under the public consistency checks but still missed the evaluator task on decision, action, and escalation selection.

This supports classifying the next research problem as upstream semantic selection rather than additional deterministic guard relaxation.

## Comparison discipline

E14k is not treated as a paired causal comparison with E14g, E14h, E14i, or E14j. Separate model generations and configuration differences prevent naive attribution of score deltas. The only strong conclusion from E14k itself is:

1. 4096 completion tokens were sufficient for 6/6 operational completeness under the frozen E14k stack; and
2. that complete candidate still failed the absolute DEV quality gate.

No private per-row labels, expected paths, output hashes, trajectories, or raw fixed outputs are recorded here.

VALIDATION remains blocked. LOCKED_TEST remains untouched.
