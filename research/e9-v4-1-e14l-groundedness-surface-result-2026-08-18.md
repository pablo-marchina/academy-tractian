# E14l public groundedness-surface result

**Date:** 2026-08-18  
**Capture:** fixed historical E14l DEV capture, unchanged  
**Oracle/scorer rows:** not read  
**VALIDATION / LOCKED_TEST:** not used

The preregistered one-sided concrete-provenance audit completed over all six fixed E14l calls.

```text
fixed calls / parsed / assessed:            6 / 6 / 6
fixed groups / selected visible cases:      3 / 3
complete surface coverage:                  true
calls with provenance violation:            2 / 6
concrete identifier mentions:               37
unsupported identifier mentions:             2
public METHOD+path mentions:                43
unrecognized METHOD+path mentions:           0
unit-bearing numeric mentions:               0
unsupported unit-bearing numeric mentions:   0
false trace self-check flags:                 0
concrete provenance violations:               2
```

Interpretation: `CONCRETE_PROVENANCE_VIOLATIONS_FOUND_GENERAL_GROUNDEDNESS_BLOCKED`.

This is a real public-groundedness failure surface: two fixed outputs contain concrete identifiers that are not present in the runner-selected visible case. Because the diagnostic does not read the private oracle, this finding may motivate a generic public-provenance safeguard without using hidden per-row correctness feedback.

The audit is intentionally one-sided. It does not establish general semantic groundedness when no concrete violation is found, so `general_free_text_groundedness` remains unresolved and VALIDATION stays blocked.

No raw outputs, identifiers, group labels, visible case values, numeric claims, hashes, private paths, expected paths or per-call results are recorded here.
