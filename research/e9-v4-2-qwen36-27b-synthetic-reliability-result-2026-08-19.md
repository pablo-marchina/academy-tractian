# E9 v4.2 Qwen 3.6 27B synthetic reliability result

**Date:** 2026-08-19  
**Scope:** public synthetic judge reliability only; no real DEV semantic labels

The preregistered independent judge `qwen/qwen3.6-27b` was run once on the frozen public 24-case semantic-groundedness reliability suite. The capture completed in one provider attempt with HTTP 200, 24/24 valid prediction rows, JSON Object Mode, `reasoning_effort=none`, and `temperature=0`.

Aggregate reliability result:

```text
status:                           PASS
synthetic cases:                  24
valid unique results:             24
missing / duplicate / invalid:     0 / 0 / 0
full coverage:                    true
support-label exact accuracy:     0.9583
claim-type exact accuracy:        1.0000
critical false-support rate:      0.0000
factual safety recall:            1.0000
SUPPORTED precision:              1.0000
NOT_APPLICABLE precision:         1.0000
```

All preregistered reliability thresholds passed. Gold support counts were 6 `CONTRADICTED`, 5 `NOT_APPLICABLE`, 6 `NOT_SUPPORTED`, and 7 `SUPPORTED`; predictions were 7, 5, 5, and 7 respectively. The single support-label error was therefore conservative at the aggregate distribution level: it did not create a false `SUPPORTED` prediction. No per-case result, claim text, rationale, identifier, or raw provider response is committed.

The judge is now authorized for the already-built **DEV** semantic claim packet under the frozen v4.2 protocol. This authorization does **not** authorize VALIDATION or LOCKED_TEST.

The real DEV semantic measurement must preserve the frozen judge identity and rubric, must not use private expected paths/scorer rows, and must not tune the judge or candidate from real per-claim labels.
