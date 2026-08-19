# E14n paired public identifier-provenance result

**Date:** 2026-08-18  
**Scope:** historical fixed E14l DEV capture only  
**Provider calls:** 0  
**Private oracle/scorer rows:** not used

## Before

The preregistered one-sided public groundedness-surface audit on the original fixed E14l capture found:

```text
fixed / parsed / assessed:                   6 / 6 / 6
complete surface coverage:                   true
calls with concrete provenance violation:    2 / 6
concrete identifier mentions:                37
unsupported identifier mentions:              2
public METHOD+path mentions:                 43
unrecognized METHOD+path mentions:             0
unit-bearing numeric mentions:                 0
unsupported unit-bearing numeric mentions:    0
false trace self-check flags:                  0
```

This established a real public provenance failure without using private expected paths, scorer rows, VALIDATION or LOCKED_TEST.

## E14n intervention

E14n was preregistered before applying the transform. The deterministic guard:

- preserves concrete identifiers already present in the exact runner-selected visible case;
- preserves public placeholders;
- replaces only unsupported concrete namespaced IDs/UUIDs with typed placeholders;
- does not alter decision/action/escalation semantics;
- makes no model/provider call.

Observed paired transform:

```text
status:                                      E14N_PUBLIC_IDENTIFIER_PROVENANCE_GUARD_TRANSFORM_PASS
fixed calls consumed:                        6
parsed outputs:                              6
assessed calls:                              6
complete surface coverage:                   true
calls changed:                               2
changed text fields:                         2
unsupported identifier mentions before:     2
unsupported identifier replacements:        2
replacement occurrences:                    2
unsupported identifier mentions after:      0
calls with provenance violation before:      2
calls with provenance violation after:       0
decision/action/escalation semantic changes: 0
provider calls made:                         0
```

## Same-audit after result

Rerunning the exact same groundedness-surface diagnostic on the transformed local capture produced:

```text
fixed / parsed / assessed:                   6 / 6 / 6
complete surface coverage:                   true
calls with concrete provenance violation:    0 / 6
concrete identifier mentions:                35
unsupported identifier mentions:              0
public METHOD+path mentions:                 43
unrecognized METHOD+path mentions:             0
unit-bearing numeric mentions:                 0
unsupported unit-bearing numeric mentions:    0
false trace self-check flags:                  0
concrete provenance violation count:           0
```

## Interpretation

This is an exactly paired deterministic improvement on the **identifier-provenance surface**: `2 -> 0` unsupported identifier mentions and `2 -> 0` affected calls, with zero decision/action/escalation semantic changes and zero provider calls.

It is not evidence that the underlying model became better; the model output generation did not change. It validates a generic public post-model provenance guard for concrete identifiers.

It also does **not** establish general free-text groundedness. Semantic claims can still be unsupported without containing a concrete identifier, unit-bearing number, invalid endpoint or false self-check flag. Therefore:

```text
general_free_text_groundedness = UNRESOLVED_BY_ONE_SIDED_SURFACE_AUDIT
validation_gate_authorized = false
```

VALIDATION remains blocked and LOCKED_TEST remains final-only.
