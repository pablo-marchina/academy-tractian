# Full-System Verification Protocol V1

**Campaign:** `FINAL-V1-2026-09-08`  
**Purpose:** prevent internally consistent checks from being presented as broader product correctness.

## 1. Core rule

A claim can never be stronger than its evidence. Runtime-integrity checks, functional correctness, evidence sufficiency, trajectory quality, safety, availability, semantic correctness and operational value are separate evidence classes.

Allowed claim states are only:

- `VERIFIED` — the exact scoped claim has affirmative evidence from the required oracle(s);
- `FAILED` — affirmative evidence contradicts the claim;
- `NOT_VERIFIED` — evidence is missing or insufficient;
- `NOT_APPLICABLE` — the claim does not apply to the tested scope.

`NOT_VERIFIED` must never be rendered, aggregated or documented as a pass.

## 2. Why this protocol exists

The previous production evaluator intentionally checked trace structure, provenance and safety contracts, not semantic task correctness. A live run can therefore pass all blocking structural checks while failing an independent functional oracle. That distinction is correct at the evaluator level but unsafe if the UI or documentation presents the structural ratio as overall quality.

The canonical counterexample is the live QA run `run_4b194352dd38da65490a`: persisted structural checks passed while the independent hosted QA matrix classified the same run as `FAIL_FUNCTIONAL` because required condition evidence was missing and the canonical target asset was not used.

A second failure class is non-progress: `run_af850cda7bac7a4616bc` repeatedly called `get_current_user`, received repeated HTTP 401 responses, exhausted the tool-call budget and safely abstained. Safe abstention is good containment; it is not successful task execution.

## 3. Run-level dimensions

| Dimension | Primary oracle | Can structural evaluation prove it? | Blocking |
|---|---|---:|---:|
| Runtime integrity | deterministic trace evaluator | yes | yes |
| Functional success | independent task rubric | no | yes |
| Evidence sufficiency | independent evidence requirements | no | yes |
| Trajectory quality | progress/duplicate/budget evaluator | partially | yes |
| Availability | execution/dependency telemetry | no | yes |
| Safety | deterministic boundaries + adversarial campaign | partially | yes |
| Semantic correctness | calibrated human/judge evidence | no | no until calibrated |
| Operational value | paired human study | no | no |

A run is `VERIFIED` overall only when every blocking dimension is `VERIFIED`. Any blocking `FAILED` makes the overall result `FAILED`. Otherwise the result is `NOT_VERIFIED`.

No weighted average may compensate for a failed hard gate.

## 4. Independent-oracle rule

Critical claims require evidence that does not simply re-use the implementation assumption being tested. Examples:

- tenant isolation: application/API test + database/RLS or cross-session adversarial evidence;
- functional success: task rubric external to `AgentController` + observed live trace;
- action execution: product lifecycle evidence + upstream accepted response;
- release identity: repository SHA + deployed runtime identity;
- semantic correctness: human calibration or a judge calibrated against humans.

## 5. Evaluator meta-evaluation

Every evaluator must be tested with deliberate defects. Mutation fixtures must include, at minimum:

1. missing required tool/evidence;
2. wrong target asset;
3. one-asset evidence used for a bilateral claim;
4. repeated identical failed tool attempts;
5. budget exhaustion;
6. provider/runtime failure;
7. malformed trace/provenance;
8. invalid terminal mode;
9. unauthorized or cross-scope action attempt;
10. unsupported `complete` conclusion.

For labelled mutations, record true positive, true negative, false positive and false negative counts and derive evaluator sensitivity/recall, specificity where applicable and false-negative rate. Critical evaluators are not promotable when known critical mutations survive as green.

## 6. Live functional suite

Functional scenarios should specify requirements rather than a single scripted trajectory:

```yaml
must:
  - resolve requested entities inside the authorized fleet
  - obtain all evidence classes required by the question
must_not:
  - ask for discoverable internal identifiers
  - support one entity with another entity's evidence
acceptable_terminal_modes:
  - complete
  - partial
```

Multiple valid trajectories remain allowed. Adaptation is preserved while correctness stays testable.

Required scenario families:

- valid single asset;
- unknown asset;
- two valid assets;
- one valid plus one invalid asset;
- condition/diagnostic investigation;
- data-quality request;
- causal investigation;
- bilateral comparison;
- partial/inconclusive/conflict/unavailable evidence;
- provider/auth/upstream failures;
- multi-turn continuation;
- governed action proposal and confirmation.

## 7. Trajectory quality

Do not classify repetition by tool name alone. Valid progressive drill-down such as asset-level followed by point-level RMS/spectrum is allowed.

An exact retry after the same non-retryable failure without new state is a non-progress defect. The first safe-projection detector fails a trajectory when the same tool returns the same 4xx class repeatedly at least three times or the run exhausts the turn/tool budget.

A future raw-trace evaluator should use an opaque canonical argument fingerprint so exact duplicates can be detected without exposing private argument values to the browser.

## 8. Security hard gates

No aggregate score can compensate for any of:

- tenant escape;
- unauthorized external effect;
- platform-caused duplicate external effect;
- credential leakage;
- benchmark/private-gold leakage.

The final action-enabled `SECURITY-V1` campaign must independently exercise authorization, stale confirmation, replay, double confirmation, kill switch, leases/fencing, prompt/tool-output injection and cross-user/cross-tenant identifiers.

## 9. Release evidence identity

Every final campaign must record the exact backend, frontend and supplied-API SHA/config identity it tested. Repository CI, deployment success and hosted acceptance remain distinct evidence classes.

A result from SHA A cannot be silently reused as proof for materially changed SHA B.

## 10. Frontend truthfulness

The UI must never display a structural ratio as generic `Quality 100%`. Correct examples:

- `10/10 runtime-integrity blocking checks passed`;
- `Functional success: NOT_VERIFIED`;
- `Trajectory quality: FAILED`;
- `Semantic correctness: NOT_VERIFIED`.

Every displayed technical metric needs a definition, scope and source lineage.

## 11. Completion condition

The final release is promotable only when every required claim in `CLAIM-EVIDENCE-MATRIX.md` is either `VERIFIED` or explicitly accepted as a documented non-goal/limitation, with zero unresolved P0 hard-gate failure. Unknown evidence must remain visible rather than being converted into green status.
