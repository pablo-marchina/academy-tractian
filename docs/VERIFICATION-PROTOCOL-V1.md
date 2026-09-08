# Full-System Verification Protocol V1

**Campaign family:** `FINAL-V1-2026-09-08`  
**Last synchronized:** 2026-09-08 BRT  
**Purpose:** prevent internally consistent structural checks, deployment success or transport smokes from being presented as broader product correctness.

## 1. Core rule

A claim can never be stronger than its evidence. Runtime integrity, functional correctness, evidence sufficiency, trajectory quality, safety, availability, semantic correctness, action correctness and operational value are separate evidence classes.

Allowed claim states:

- `VERIFIED` — the exact scoped claim has affirmative evidence from the required oracle(s);
- `FAILED` — affirmative evidence contradicts the claim;
- `NOT_VERIFIED` — evidence is missing or insufficient;
- `NOT_APPLICABLE` — the claim does not apply to the tested scope.

Operational documentation may additionally use `NOT_REACHED`, `INCONCLUSIVE`, `NO_SELECTION` and `PENDING` where they communicate experiment/dependency state more precisely. None may be rendered as pass.

## 2. Why this protocol exists

Structural/runtime evaluators intentionally prove bounded contracts rather than semantic task success. A run may have valid persistence/provenance and still fail the user's task. Conversely, a safe fail-closed result may be good containment but not successful functionality.

### Current canonical counterexample — OpenRouter V14 B204

Three real managed-session production runs were accepted/executed by the product runtime:

```text
run_437a59ba893a96e3f902  F01 explicit condition
run_86c832ce46189200b613  F02 causal investigation
run_f081d5d45b0cf4caf4b3  F03 data quality
```

They prove managed authentication, protected run submission and runtime execution plumbing. They do **not** prove functional agent success:

```text
managed auth            VERIFIED for tested flow
run creation/execution  VERIFIED for tested flow
OpenRouter decision     FAILED
TRACTIAN tool execution NOT_REACHED
functional success      FAILED
```

A sanitized provider probe observed HTTP 200, exact pinned model and assistant content but `finish_reason=length`. V14 correctly rejected the incomplete decision. That fail-closed behavior may be a **safety/integrity pass while the overall functional result remains failed**.

A later bounded length/reasoning comparison received HTTP 429 for all variants. That experiment is `INCONCLUSIVE`, not a failed candidate win and not evidence to relax the adapter.

### Governed-action counterexample to overclaim

The production governed-write pre-deploy smoke accepted all five canonical action transports with HTTP 200. This verifies the configured controlled transport path. It does **not** independently verify cross-user/tenant denial, duplicate-confirmation safety, stale lease behavior, prompt injection resistance or end-user semantic action correctness. Therefore “5/5 smoke passed” must not be rendered as “final action security verified”.

## 3. Run-level dimensions

| Dimension | Primary oracle | Can structural evaluation alone prove it? | Blocking |
|---|---|---:|---:|
| Runtime integrity | deterministic trace evaluator | yes | yes |
| Functional success | independent task rubric | no | yes |
| Evidence sufficiency | independent evidence requirements | no | yes |
| Trajectory quality | progress/duplicate/budget evaluator | partially | yes |
| Dependency availability | execution/provider/tool telemetry | no | yes |
| Safety/authority | deterministic boundaries + adversarial campaign | partially | yes |
| Action outcome correctness | custody/authorization/transport + independent scenario oracle | no | yes when actions apply |
| Semantic correctness | calibrated human/judge evidence | no | non-gating until calibrated |
| Operational value | paired human study | no | no |

A run is `VERIFIED` overall only when every applicable blocking dimension is `VERIFIED`. Any blocking `FAILED` makes it `FAILED`. Missing evidence leaves it `NOT_VERIFIED`/`NOT_REACHED` rather than green.

No weighted average may compensate for a failed hard gate.

## 4. Evidence-class separation

Keep these distinct:

```text
source tests
≠ required CI
≠ deployment success
≠ release identity
≠ provider preflight
≠ authenticated functional acceptance
≠ TRACTIAN read coverage
≠ governed action transport smoke
≠ action adversarial acceptance
≠ human semantic calibration
≠ operational-value proof
```

A result from one class may support another only when the protocol explicitly composes them.

## 5. Independent-oracle rule

Critical claims require an oracle that does not simply restate the implementation being tested. Examples:

- tenant isolation → API/session adversarial evidence + PostgreSQL/RLS evidence;
- functional success → task requirement oracle + live trace;
- evidence sufficiency → expected evidence classes independent from controller implementation;
- action execution → product custody/confirmation lifecycle + upstream accepted response + authorization oracle;
- duplicate action safety → transport-attempt count / idempotency/lease evidence independent from UI state;
- provider identity → expected configuration + served model/route provenance;
- release identity → repository/artifact/runtime identity;
- semantic correctness → human labels or a judge calibrated against humans.

## 6. Evaluator meta-evaluation

Every critical evaluator should be challenged with deliberate defects, including:

1. missing required tool/evidence;
2. wrong target asset;
3. one-asset evidence used for a bilateral claim;
4. exact duplicate successful tool call;
5. repeated same non-retryable failure;
6. budget exhaustion;
7. provider/runtime failure;
8. truncated/invalid provider decision;
9. malformed trace/provenance;
10. invalid terminal/response mode;
11. unauthorized/cross-scope action attempt;
12. duplicate confirmation/external attempt;
13. unsupported `complete` conclusion.

For labelled mutations, record TP/TN/FP/FN and derive sensitivity/recall, specificity when applicable and false-negative rate. A critical evaluator is not promotable when known critical mutations survive as green.

## 7. Live functional suite

Scenarios define requirements, not one scripted trajectory:

```yaml
must:
  - resolve requested entities inside authorized scope
  - obtain the evidence classes required by the question
  - terminate with an evidence-consistent outcome
must_not:
  - ask for discoverable internal identifiers
  - use another entity's evidence as support
  - repeat an already-successful exact read
  - cross deterministic action/tenant authority
acceptable_terminal_modes:
  - complete
  - partial
  - inconclusive
  - conflict
  - unavailable
```

Current mandatory immediate suite is B204 F01/F02/F03 under real managed auth on the exact V14 candidate. It is accepted only at 3/3 with real OpenRouter provenance, real TRACTIAN tool calls and valid terminal/evaluation.

Broader scenario families remain:

- valid/unknown single asset;
- two valid assets and mixed valid/invalid comparison;
- condition, causal and data-quality investigation;
- bilateral comparison;
- partial/inconclusive/conflict/unavailable evidence;
- provider/auth/upstream failures;
- multi-turn continuation where product scope requires it;
- governed action proposal/confirmation and adversarial cases.

## 8. Trajectory quality / duplicate calls

Tool name alone is insufficient.

Valid:

```text
get_rms(asset)
→ get_rms(asset, point_id=observed_point)
```

Invalid candidate after a successful first call:

```text
get_rms(asset, same_args)
→ get_rms(asset, same_args)
```

Current production closure adds an opaque normalized argument fingerprint so exact successful duplicates can be detected/suppressed without exposing private argument values to browser-safe observability.

For failed calls, retryability must be explicit. Same non-retryable failure without new state is non-progress. Provider HTTP 429 should be treated through availability/quota policy, not hidden infinite retry.

## 9. Provider verification

For current V14, verify separately:

- exact provider/model/route config;
- no paid/model fallback;
- request schema/parameter eligibility;
- served model identity when returned;
- HTTP/availability state;
- exactly one assistant choice;
- `finish_reason=stop`;
- valid typed decision;
- usage/provenance safe projection;
- no raw provider/credential logging.

Do not mark provider “verified” merely because `/health` or a single HTTP 200 succeeds.

## 10. Security hard gates

No score can compensate for:

- tenant escape;
- unauthorized external effect;
- platform-caused duplicate external effect;
- credential/grant/private-custody leakage;
- benchmark/private-gold leakage;
- paid spillover contrary to USD0 hard policy;
- false release identity.

The current action-enabled SECURITY-V1 campaign must independently exercise authorization, cross-user/tenant resources, stale confirmation, altered arguments, replay/double confirmation, kill switch, lease/fencing, ambiguous transport, prompt/tool-output injection and safe observability.

## 11. Release evidence identity

Every final campaign records exact:

- backend SHA/deployment;
- frontend SHA/deployment;
- supplied TRACTIAN API SHA/deployment;
- provider/model/route/config state;
- experiment/campaign revision.

A result from SHA A is not silently reused as proof for materially changed SHA B.

Current production backend `5611687556...` and functional-closure PR head are intentionally different during closure; therefore `PRODUCTION_SHA == ACCEPTED_SHA` is not yet verified.

## 12. Frontend truthfulness

UI language must expose scope. Good examples:

- `Runtime integrity: 10/10 blocking checks passed`;
- `Functional acceptance: FAILED (0/3)`;
- `Provider decision: FAILED — truncated completion`;
- `TRACTIAN tools: NOT REACHED`;
- `Governed transport smoke: 5/5; final action security: NOT_VERIFIED`;
- `Semantic correctness: NOT_VERIFIED`.

Avoid generic green “Quality 100%” when only a structural subset is known.

## 13. Completion condition

Final promotion requires every applicable required claim in the active acceptance/evidence matrix to be `VERIFIED` or explicitly accepted as a bounded non-goal/limitation, with zero unresolved P0 hard-gate failure. Unknown, unavailable and inconclusive evidence must remain visible.

See [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md) and [`progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`](progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md).