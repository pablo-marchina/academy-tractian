# E9 v4.2 Qwen real DEV semantic judge capture result

**Date:** 2026-08-19  
**Scope:** DEV-only semantic-groundedness measurement transport

The preregistered reliability-qualified Qwen judge completed the single authorized real DEV capture over the already-built E14n semantic claim packet.

Aggregate operational result:

```text
status:                               E9_V4_2_QWEN_REAL_DEV_SEMANTIC_JUDGE_CAPTURE_PASS
judge model:                          qwen/qwen3.6-27b
fixed calls consumed:                 6 / 6
claim units consumed:                69 / 69
valid prediction rows written:       69
provider attempts made:               6
completed provider calls:             6
response format:                     json_object
reasoning effort:                    none
temperature:                         0
system prompt reused without edits:  true
provider contract reused case_id:    true
case_id mapped back locally:         true
real measurement attempt consumed:   true
rerun allowed:                       false
semantic metrics authorized:         true
validation gate authorized:          false
```

Scope/safety invariants remained satisfied:

- private oracle used: false
- private scorer rows used: false
- VALIDATION feedback used: false
- LOCKED_TEST used: false
- raw provider responses printed: false
- claim text printed: false
- visible-case values printed: false
- judge rows printed: false
- identifiers/group IDs/hashes/API key printed: false

This record establishes only that the frozen real DEV semantic-judge capture completed with full operational coverage. It does **not** state whether semantic groundedness passed; that is determined separately by the frozen aggregate scorer over the local 69-row judge result.

The local raw judge result and claim packet remain uncommitted. The real measurement attempt is consumed and must not be rerun.