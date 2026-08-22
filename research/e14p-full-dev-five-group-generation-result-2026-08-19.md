# E14p full-DEV five-group generation result — 2026-08-19

## Status

`E14O_FULL_DEV_FIVE_GROUP_CAPTURE_PASS`

This records only aggregate operational/structural evidence from the preregistered full-DEV generation. The real fixed capture remains local and uncommitted.

## Frozen candidate and scope

- Candidate stack at generation time: E14o public factual-grounding prompt over the frozen GPT-OSS 120B medium / strict 4096 stack.
- Required DEV groups: 5/5.
- Repeats per DEV group: 2.
- Expected fixed calls: 10.
- VALIDATION: not run.
- LOCKED_TEST: not used.
- Private oracle supplied to model: no.

## Observed aggregate generation result

```text
required_dev_groups:                    5
observed_dev_groups:                    5
repeats_per_group:                      2
total_calls:                           10
parsed_model_outputs_available:        10
scoreable_calls:                       10
completeness_pass:                   true
each_group_exactly_two_calls:        true
real_generation_attempt_consumed:    true
rerun_allowed:                       false
```

The inherited status chain was fully PASS:

```text
E11   E11_DEV_ONLY_INDEPENDENT_ACTION_AUTHORIZATION_CAPTURE_PASS
E14   E14_DEV_ONLY_COMPLETENESS_SELECTIVE_REPROCESS_CAPTURE_PASS
E14c  E14C_DEV_ONLY_PUBLIC_ENDPOINT_CANONICALIZATION_CAPTURE_PASS
E14d  E14D_DEV_ONLY_PUBLIC_EVIDENCE_RESOURCE_CANONICALIZATION_CAPTURE_PASS
E14e  E14E_DEV_ONLY_EXPLICIT_CURRENT_HANDOFF_SEMANTICS_CAPTURE_PASS
E14f  E14F_DEV_ONLY_PUBLIC_SEMANTIC_REPAIR_CAPTURE_PASS
E14l  E14L_DEV_ONLY_120B_MEDIUM_REASONING_STRICT_4096_CAPTURE_PASS
```

## Interpretation

This closes the full-DEV generation completeness requirement only. It is not yet a full-DEV quality/groundedness PASS and does not authorize VALIDATION.

The fixed local capture must now be processed in the preregistered order, without new candidate tuning:

1. E14n v1.1 identifier-provenance guard;
2. E14p deterministic epistemic serializer;
3. public one-sided groundedness surface audit;
4. frozen E9 v4.1 measurement-only evaluation over all 10 calls;
5. E9 v4.2 semantic claim-packet construction;
6. preregister full-DEV semantic judge transport after observing only aggregate packet shape and before any semantic labels.

No raw model outputs, identifiers, output hashes, private expected paths, scorer rows, semantic judge rows, or claim text are committed here.
