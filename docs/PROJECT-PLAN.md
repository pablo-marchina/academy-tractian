# Academy × TRACTIAN — Project Action Plan

**Status:** full-DEV safety/authorization gate closed; evidence-selection gate active at E14s  
**Planning date:** 2026-08-19  
**Progress checkpoint:** 2026-08-19 16:34 BRT  
**Target final delivery:** 2026-09-08

## Executive status

The project has progressed from the original E14 completeness/action blocker to a much narrower remaining problem.

The current evaluated stack is based on the fixed `openai/gpt-oss-120b` medium-reasoning strict-JSON candidate plus deterministic public post-processing layers. The major methodological boundaries remain unchanged:

- DEV is the only tuning/development split.
- VALIDATION is measurement-only and has not been used to tune the current candidate.
- LOCKED_TEST remains untouched and final-only.
- Private expected paths and scorer rows are evaluator-side only.
- Semantic-judge rows are never used to tune candidates.
- Raw fixed outputs, private labels, hashes and private paths are not committed.

The project is **not yet eligible for VALIDATION** because the remaining full-DEV evidence gate has not passed.

## Current gate

The current blocker is isolated to **evidence acquisition / evidence-route selection**.

E14q2 closed the deterministic action/escalation safety blocker on all five DEV groups without changing evidence planning:

```text
fixed / parsed / scoreable:                 10 / 10 / 10
reference_quality:                              0.8000
decision_correctness:                           0.8000
evidence_correctness:                           0.2000
mean_expected_read_recall:                      0.7667
mean_extra_public_read_count:                   3.5000
action_correctness:                             0.8000
escalation_correctness:                         0.8000
premature_action_rate:                          0.0000
unsupported_action_or_escalation_rate:          0.0000
locked_test_or_gold_leakage_rate:               0.0000
```

Therefore the remaining full-DEV gate is:

```text
evidence_correctness                    >= 0.5000
mean_expected_read_recall               >= 0.8333
mean_extra_public_read_count            <= 3.5000
```

while preserving:

```text
decision_correctness                    = 0.8000
action_correctness                      = 0.8000
escalation_correctness                  = 0.8000
premature_action_rate                   = 0.0000
unsupported_action_or_escalation_rate   = 0.0000
locked_test_or_gold_leakage_rate        = 0.0000
```

## Progress since the original E14 gate

### Evaluator and semantic-groundedness validity

- E9 v4.1 fixed structural evaluator bugs and now uses exact visible-ticket alignment, exact public METHOD+path normalization, evidence credit from `evidence_plan` only, and complete-scoreability gates.
- E9 v4.2 added an independent semantic-groundedness protocol for free text.
- `qwen/qwen3.6-27b` passed the frozen public synthetic reliability suite and is authorized as the independent semantic judge under the frozen protocol.
- The public one-sided groundedness-surface diagnostic remains separate from general semantic groundedness.

### E14n — identifier-provenance guard

E14n v1.1 is retained as a deterministic public provenance safeguard. It removes unsupported concrete identifiers while preserving placeholders and decision/action/escalation semantics.

### E14o — prompt-only factual grounding

Representative DEV E14o preserved strong v4.1 metrics but failed the semantic target:

```text
factual claims:             4
supported factual claims:   2
unsupported factual claims: 2
factual groundedness:        0.5000
semantic gate:               FAIL
```

Conclusion: prompt-only factual-grounding discipline did not solve the semantic issue.

### E14p — deterministic epistemic serializer

E14p reserialized only public free-text fields over the same fixed E14o outputs.

Representative DEV:

```text
semantic claims:           126 / 126
factual assertions:          0
semantic groundedness:     1.0000
semantic gate:             PASS
```

Full DEV, five groups / ten calls:

```text
semantic claims:           206 / 206
factual assertions:          0
semantic groundedness:     1.0000
semantic gate:             PASS
```

This validates the deterministic serializer effect, **not** improved model reasoning.

However, the E14p full-DEV candidate stack failed deterministic quality/safety acceptance:

```text
evidence_correctness:                    0.2000
mean_expected_read_recall:               0.7667
premature_action_rate:                   0.1000
unsupported_action_or_escalation_rate:   0.1000
```

Therefore E14p did not authorize VALIDATION.

### E14q — public action-authorization consistency

E14q changed one of the ten fixed calls and removed one unauthorized active action caused by a missing public authorization prerequisite.

Result:

```text
decision_correctness:                    0.7000
action_correctness:                      0.8000
escalation_correctness:                  0.7000
premature_action_rate:                   0.0000
unsupported_action_or_escalation_rate:   0.1000
```

E14q was a partial success: premature action was eliminated, but one unsupported action/escalation inconsistency remained.

### E14q2 — route-role / purpose consistency

E14q2 applied a second fail-closed public consistency rule over the same fixed outputs. It changed one call, demoted one escalation and changed one decision class. It did not alter `evidence_plan` or the v4.2 free-text claim sources.

E14q2 full-DEV result:

```text
reference_quality:                       0.8000
decision_correctness:                    0.8000
evidence_correctness:                    0.2000
mean_expected_read_recall:               0.7667
mean_extra_public_read_count:            3.5000
action_correctness:                      0.8000
escalation_correctness:                  0.8000
premature_action_rate:                   0.0000
unsupported_action_or_escalation_rate:   0.0000
leakage:                                 0.0000
```

**Decision: E14q2 PASS for its preregistered safety/action target.**

This closes the deterministic action/escalation blocker. Evidence is now the only active DEV quality blocker.

### E14r — visible-case evidence-route replacement

E14r tested a deterministic replacement of the broad evidence plan using public visible-case cues and the public tool registry.

Transform:

```text
public read signatures before: 63
public read signatures after:  34
added:                         13
removed:                       42
```

Result:

```text
evidence_correctness:          0.0000
mean_expected_read_recall:     0.4000
mean_extra_public_read_count:  2.0000
```

Decision/action/escalation remained `0.8 / 0.8 / 0.8` and safety remained `0 / 0`.

**Decision: E14r FAIL.**

The aggregate result shows that full replacement using sparse lexical route cues removed too much useful evidence. No private row was inspected and no group/ticket failure was inferred.

The E14r semantic packet was built successfully with 114 claims, but no semantic judge is authorized for this rejected candidate.

### E14s — candidate-pool consensus selection

E14s is the active next experiment.

It is preregistered and structurally validated in CI. It starts from the accepted E14q2 fixed outputs, not from the rejected E14r transformed outputs.

Single intervention class:

```text
deterministic_public_evidence_candidate_pool_consensus_selection_only
```

Candidate sources:

1. the fixed E14q2 `evidence_plan` as a public model-proposed route ordering;
2. the deterministic E14r public selector as an independent public candidate source.

Frozen selection tiers:

1. active-action authorization and target-dependency reads;
2. reads present in both candidate sources;
3. remaining E14r deterministic reads;
4. remaining original E14q2 reads in first-occurrence order.

The selection cap is frozen at **6 reads per call**. No route outside the public candidate pool may be synthesized.

E14s CI status:

```text
workflow run: 32285078034
compile: PASS
synthetic self-check: PASS
preregistration constants: PASS
forbidden selector checks: PASS
```

No E14s real transform or v4.1 measurement has been consumed yet at this checkpoint.

## DEV coverage status

The active full-DEV requirement is now satisfied structurally:

```text
DEV groups:       5 / 5
DEV scenarios:    8 / 8
fixed calls:     10 / 10
repeats/group:    2
```

This includes the previously omitted contextualize modality.

Full DEV is therefore no longer blocked by coverage; it is blocked only by the evidence-quality threshold.

## Current action checklist

### Completed

- [x] Freeze evaluator v4.1 structural fixes and exact visible-ticket alignment.
- [x] Freeze semantic-groundedness protocol v4.2.
- [x] Qualify independent Qwen semantic judge on the public synthetic suite.
- [x] Close E14m / E14m-R1 without unauthorized reruns.
- [x] Retain E14n v1.1 public identifier-provenance guard.
- [x] Measure E14o representative DEV and reject prompt-only semantic grounding.
- [x] Preregister and measure E14p representative DEV semantic serializer.
- [x] Expand the fixed candidate to full DEV 5/5 groups and 10/10 calls.
- [x] Measure E14p full-DEV v4.1 and semantic groundedness.
- [x] Reject the E14p stack despite semantic PASS because full-DEV quality/safety failed.
- [x] Preregister, implement and measure E14q.
- [x] Eliminate full-DEV premature actions with E14q.
- [x] Preregister, implement and measure E14q2.
- [x] Close full-DEV action/escalation safety: premature=0, unsupported=0.
- [x] Preregister, implement and measure E14r evidence-route replacement.
- [x] Reject E14r from aggregate-only evidence failure.
- [x] Build E14r semantic packet for characterization only; do not judge it.
- [x] Preregister and implement E14s candidate-pool consensus selector.
- [x] Pass E14s structural CI before any real E14s transform.
- [x] Keep VALIDATION protected from tuning.
- [x] Keep LOCKED_TEST blocked.
- [x] Keep final architecture unfrozen.

### Active — E14s

- [ ] Apply E14s once to the same fixed E14q2 full-DEV outputs.
- [ ] Verify 10/10 transform completeness and zero non-evidence-field changes.
- [ ] Run the public surface audit and require zero concrete provenance violations.
- [ ] Run frozen E9 v4.1 exactly once on E14s.
- [ ] Require evidence correctness >= 0.5.
- [ ] Require expected-read recall >= 0.8333.
- [ ] Require mean extra public reads <= 3.5.
- [ ] Require decision/action/escalation to remain exactly 0.8 / 0.8 / 0.8.
- [ ] Require premature and unsupported action/escalation rates to remain 0 / 0.
- [ ] Build the new E9 v4.2 claim packet after E14s because `evidence_plan` changes.
- [ ] Stop before semantic judging and preregister the observed packet shape.

## Plan after E14s

### Branch A — E14s v4.1 FAIL

If any frozen E14s deterministic gate fails:

1. record aggregate-only failure;
2. do not inspect private scorer rows or infer failing groups/tickets;
3. do not run a semantic judge for candidate selection;
4. do not touch VALIDATION;
5. design the next DEV candidate only from public invariants and aggregate results;
6. preregister the next intervention before applying it.

### Branch B — E14s v4.1 PASS

If E14s passes the full deterministic DEV gate:

1. freeze the new semantic packet shape before labels;
2. reuse the already-qualified independent Qwen judge only under the frozen v4.2 protocol;
3. make one full-DEV semantic measurement attempt;
4. require full packet coverage and semantic groundedness PASS;
5. keep VALIDATION blocked until the semantic result is complete.

### Branch C — full DEV v4.1 + semantic PASS

Only after both deterministic and semantic full-DEV gates pass:

1. freeze the candidate stack for VALIDATION;
2. run VALIDATION **measurement-only** on the two frozen validation groups / three scenarios;
3. do not tune prompts, guards, routes, thresholds, model choice or architecture from validation feedback;
4. evaluate the same deterministic quality, safety, leakage and semantic-groundedness surfaces under a preregistered validation measurement plan.

A validation failure rejects the frozen candidate for promotion. It does not authorize a validation-tuned repair.

### Branch D — VALIDATION PASS

After a complete preregistered VALIDATION PASS:

1. freeze the candidate decision/policy/post-processing stack;
2. integrate it into the production-shaped runtime without changing evaluated semantics;
3. run contract, trace, error-path, retry, observability and live-API integration checks that do not use LOCKED_TEST for tuning;
4. if integration changes any evaluated semantic behavior, return to DEV before final evaluation;
5. freeze final architecture and the final evaluation artifact.

### Final — LOCKED_TEST

LOCKED_TEST remains final-only.

Once candidate semantics and architecture are frozen:

1. preregister the final LOCKED_TEST measurement;
2. execute LOCKED_TEST once under the frozen scorer/judge protocol;
3. do not repair or rerun based on locked-test results;
4. record final metrics and limitations;
5. finish README, architecture documentation, experiment report and demo/presentation artifacts from the frozen evaluated system.

## Promotion gate summary

```text
E14s full-DEV v4.1 PASS
        ↓
full-DEV semantic PASS
        ↓
VALIDATION measurement-only PASS
        ↓
candidate + architecture freeze / integration verification
        ↓
final-only LOCKED_TEST
        ↓
final documentation + demo/presentation
```

No step may be skipped.

## Methodological constraints

- The model must never see private expected paths, evaluator gold, scorer rows, reference trajectories, semantic labels or LOCKED_TEST material.
- VALIDATION must not be used for candidate tuning.
- LOCKED_TEST remains unavailable until final evaluation.
- Real semantic-judge labels are measurement outputs, not tuning data.
- Deterministic post-processing improvements support causal claims only about that post-processing layer, not about underlying model reasoning.
- A semantic PASS cannot rescue a deterministic quality/safety FAIL.
- A public surface-audit PASS does not establish general free-text groundedness.
- No repeated real measurement attempt is allowed when the relevant preregistration/attempt-lock policy says the attempt was consumed.
- Final architecture remains unfrozen until the candidate passes the required pre-final gates.
