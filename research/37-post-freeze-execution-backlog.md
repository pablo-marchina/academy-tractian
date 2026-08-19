# Post-Freeze Execution Backlog — Active Research Gate

Status: **E9 v4.1/v4.2 frozen; full DEV 5/5 complete; E14q2 safety PASS; E14r/E14s/E14t evidence candidates rejected; E14u prompt-only evidence decomposition ACTIVE**

Checkpoint: **2026-08-19 17:45 BRT**

## Non-negotiable experiment boundaries

- [x] DEV is the only development/tuning split.
- [x] VALIDATION is measurement-only and remains blocked.
- [x] LOCKED_TEST is final-only and untouched.
- [x] Private expected paths remain evaluator-side only.
- [x] Raw fixed outputs, scorer rows, semantic rows, private paths and output hashes are not committed.
- [x] Real semantic-judge labels are not candidate-tuning data.
- [x] Attempt locks / no-rerun rules remain binding.
- [x] Final architecture remains unfrozen.

## Stable accepted stack components

- model family/config baseline: `openai/gpt-oss-120b`, medium reasoning, temperature 0, strict JSON, 4096 completion budget;
- full-DEV coverage: 5 groups, 10 calls, 2 repeats/group;
- E14n v1.1 public identifier-provenance guard;
- E14p deterministic epistemic serializer;
- E14q + E14q2 deterministic action/escalation consistency;
- E9 v4.1 deterministic quality/safety evaluator;
- E9 v4.2 semantic-groundedness protocol;
- independent semantic judge `qwen/qwen3.6-27b`, qualified on the frozen public synthetic suite.

## Closed gates

### Coverage

- [x] 5/5 DEV groups.
- [x] 8/8 DEV scenarios.
- [x] contextualize included.
- [x] 10/10 fixed calls.
- [x] 2 repeats/group.

### Safety/action

E14q2 accepted baseline:

```text
decision_correctness                    0.8000
action_correctness                      0.8000
escalation_correctness                  0.8000
premature_action_rate                   0.0000
unsupported_action_or_escalation_rate   0.0000
leakage                                 0.0000
```

### Semantic serialization

E14p full-DEV semantic result:

```text
claims                                  206 / 206
factual assertions                      0
semantic groundedness                   1.0000
semantic gate                           PASS
```

This validates the serializer only, not underlying model reasoning.

## Active blocker — evidence completeness

Frozen target:

```text
evidence_correctness                    >= 0.5000
mean_expected_read_recall               >= 0.8333
mean_extra_public_read_count            <= 3.5000
```

Candidate history:

```text
candidate   reads   evidence_correct   mean_recall   mean_extras
E14q2        63          0.20             0.7667        3.50
E14r         34          0.00             0.4000        2.00
E14s         59          0.20             0.7750        3.10
E14t         63          0.30             0.8000        3.40
```

E14r over-pruned. E14s consensus was directionally useful. E14t bounded restoration is the strongest deterministic evidence result so far but still fails exact-call completeness and mean recall.

E9 v4.1 defines a call as evidence-correct only when its expected-read recall is exactly `1.0`. At E14t, 3/10 calls are complete. Only 0.1 mean extra-read headroom remains. A pure-addition strategy can add at most one read globally while guaranteeing the 3.5 ceiling, which can complete at most one additional call and therefore cannot reach the required 5/10. Pure expansion is closed as a viable intervention class.

## Active experiment — E14u

Experiment:

```text
E14u-full-DEV-public-evidence-decomposition-prompt
```

Status:

```text
preregistered before implementation/provider call: true
single intervention: public evidence decomposition system-prompt suffix only
structural CI: PASS
CI run: 32300192016
real generation attempt consumed: false
```

### Frozen generation configuration

```text
model                     openai/gpt-oss-120b
reasoning                 medium
temperature               0
strict JSON               true
completion budget         4096
DEV groups                5
repeats/group             2
fixed calls               10
```

No provider/model/reasoning/schema/retry/repair change is allowed.

### Prompt-only evidence decomposition policy

- decompose the visible task into concrete unknowns first;
- choose the smallest complete public GET set;
- exactly one canonical GET signature per evidence item;
- no generic all-routes checklist;
- `GET /users/me` only when authorization is material;
- baseline/data-quality/RMS/spectrum only when the corresponding public evidence dimension is material;
- `GET /models/{modelId}` when model state/drift/performance/coverage/retraining is material;
- knowledge search + document only when procedural/domain/source grounding is material;
- preserve public resource dependency chains and active-action prerequisites;
- prefer 4–6 reads, permit a seventh only for a distinct dependency, never exceed 7;
- do not change existing decision/action/escalation calibration rules.

Public-contract motivation: the existing E10b evidence hint list omitted `GET /models/{modelId}` even though the public tool registry and action policy support model retraining. This was identified without private evaluator rows.

## E14u execution order

- [x] Record E14t aggregate-only rejection.
- [x] Preregister E14u before implementation/provider call.
- [x] Implement E14u prompt-only full-DEV runner.
- [x] Add public structural self-check.
- [x] Pass structural CI `32300192016`.
- [ ] Consume exactly one E14u full-DEV generation attempt.
- [ ] Require 10/10 parsed/scoreable generation outputs; no rerun after attempt consumption.
- [ ] Apply unchanged E14n v1.1.
- [ ] Apply unchanged E14p serializer.
- [ ] Apply unchanged E14q.
- [ ] Apply unchanged E14q2.
- [ ] Run public surface audit.
- [ ] Run frozen E9 v4.1 exactly once.
- [ ] Build a new E9 v4.2 claim packet.
- [ ] If deterministic full-DEV fails: record aggregate-only result; no Qwen; return to DEV.
- [ ] If deterministic full-DEV passes: preregister exact packet shape before any semantic labels.
- [ ] Run one reliability-qualified Qwen semantic measurement.
- [ ] Only if deterministic + semantic full-DEV pass: run VALIDATION measurement-only.
- [ ] Only after VALIDATION acceptance: freeze candidate stack and begin production-shaped integration/final architecture work.
- [ ] LOCKED_TEST final-only.

## E14u full-DEV gate

```text
fixed / scoreable                       10 / 10
evidence_correctness                    >= 0.5000
mean_expected_read_recall               >= 0.8333
mean_extra_public_read_count            <= 3.5000
decision_correctness                    >= 0.8000
action_correctness                      >= 0.8000
escalation_correctness                  >= 0.8000
premature_action_rate                   = 0.0000
unsupported_action_or_escalation_rate   = 0.0000
locked/gold leakage                     = 0.0000
```

## Attempt policy

- one real E14u generation runner invocation;
- attempt lock before first provider call;
- no silent retry of the complete experiment after attempt consumption;
- existing internal model-call retry/repair logic remains frozen;
- incomplete capture requires an explicit preregistration amendment;
- no provider or model substitution without amendment;
- no VALIDATION or LOCKED_TEST use.
