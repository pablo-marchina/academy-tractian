# BIG-B4 — Freeze Evaluation Protocol

**Status:** COMPLETE — `FROZEN`  
**Date:** 2026-08-22  
**Protocol:** `P12_FRESH_BLIND_HYBRID_EXTERNAL_FIRST`  
**Agent optimization:** may resume only under this frozen protocol  
**Fresh blind / legacy final access:** still fail-closed; no source or final measurement currently authorized

## 1. Freeze result

BIG-B4 converts the BIG-B3 `PREFERRED` P12 design into an executable, versioned, fail-closed evaluation protocol.

Canonical manifest:

- [`frozen/big-b4-evaluation-protocol-v1.json`](frozen/big-b4-evaluation-protocol-v1.json)

Supporting frozen control artifacts:

- [`frozen/big-b4-blind-source-registry-v1.json`](frozen/big-b4-blind-source-registry-v1.json)
- [`frozen/big-b4-candidate-freeze-template-v1.json`](frozen/big-b4-candidate-freeze-template-v1.json)
- [`frozen/big-b4-final-access-authorization-template-v1.json`](frozen/big-b4-final-access-authorization-template-v1.json)
- [`experiments/validation-usage-superseding-correction-2026-08-22.json`](experiments/validation-usage-superseding-correction-2026-08-22.json)

Executable enforcement:

- [`../scripts/research/big_b4_protocol_guard.py`](../scripts/research/big_b4_protocol_guard.py)
- [`../scripts/research/big_b4_protocol_self_check.py`](../scripts/research/big_b4_protocol_self_check.py)
- [`.github/workflows/research-big-b4-protocol-self-check.yml`](../.github/workflows/research-big-b4-protocol-self-check.yml)

Self-check evidence:

- [`results/big-b4-protocol-self-check-2026-08-22.json`](results/big-b4-protocol-self-check-2026-08-22.json)

## 2. Frozen partition roles

```text
EXPOSED_POOL
  historical DEV + historical VALIDATION
  7 independent asset/story groups
  adaptive development / selection / ablation / regression
  no blind-generalization claim

FRESH_BLIND
  primary independent real-domain generalization evidence
  Tier A partner-held external source preferred
  Tier B independently authored + independently adjudicated fallback
  no source currently authorized

LEGACY_LOCKED_TEST
  3 historical groups
  qualified supplementary held-out domain characterization only
  no candidate execution before final authorization
  never described as pristine/untouched

SYNTHETIC_ADVERSARIAL
  robustness / evaluator-judge qualification / regression
  never a substitute for real-domain blind evidence
```

The indivisible assignment and primary generalization unit is `asset_story_group`.

## 3. Access control — fail closed

The access guard defaults to `DENY`.

Key rules now executable:

- candidate private-oracle access is always denied;
- EXPOSED_POOL adaptive candidate use is allowed;
- evaluator private scoring on exposed data requires candidate outputs to be fixed first;
- LOCKED_TEST development, selection, ablation and developer semantic inspection are denied;
- LOCKED_TEST candidate execution/private scoring require a frozen candidate generation plus final authorization;
- FRESH_BLIND requires a registered unbreached source, frozen candidate/evaluator/judge/outcome policy and one-shot final authorization;
- a breached source is denied;
- a consumed authorization is denied;
- an unknown partition is denied.

No current final authorization exists.

## 4. Candidate-generation freeze contract

Every candidate generation entering any final path must freeze, at minimum:

- candidate code/config/prompt hashes;
- model/provider/runtime identity;
- stochastic vs deterministic status;
- retrieval and guard policy hashes;
- evaluator version + qualification evidence;
- semantic judge manifest/qualification or explicit `NOT_APPLICABLE`;
- seed policy;
- primary outcomes and hard safety constraints;
- repetitions per scenario;
- uncertainty method;
- selection evidence provenance;
- freeze timestamp.

A material change after blind access creates a new generation. The previous blind measurement cannot establish independent generalization for the changed generation.

## 5. Repeated-run and statistical freeze

The hierarchy is:

`asset_story_group → scenario → repeated_run`

Rules:

- stochastic candidates require at least **3 repetitions per scenario** before a stability/reliability claim;
- repetition count is preregistered before candidate outcomes and is matched across paired candidates;
- matched seeds are required where supported;
- changing repetition count after observing results requires a new preregistration;
- groups receive equal weight in primary generalization estimates;
- material candidate comparisons are paired at group level;
- LOGO group-sensitivity reporting is mandatory;
- modality slices include `investigate`, `execute` and `contextualize`;
- for `n >= 5` independent groups, the primary interval is a 95% group-cluster percentile bootstrap with 20,000 resamples and frozen seed `20260822`;
- for `n < 5`, all per-group outcomes and limitations are reported and no population-style bootstrap interval is promoted as primary evidence;
- naive fold standard error is not described as a universal unbiased uncertainty estimate.

This supersedes the older provisional scenario-as-primary-unit language where multiple scenarios belong to the same asset/story lineage.

## 6. Primary outcomes and safety constraints

Primary quality families:

- task quality / task success;
- decision correctness;
- evidence correctness;
- action correctness;
- escalation correctness.

Efficiency metrics such as latency/tool/model calls are secondary or explicit Pareto dimensions.

Hard safety events are non-compensable. A confirmed hard safety violation blocks candidate promotion; quality gains cannot offset it.

## 7. Evaluator and semantic-judge freeze

A candidate may not enter final measurement unless:

- deterministic evaluator validity/qualification is established;
- the exact evaluator hash is frozen for the generation;
- outputs are fixed before private scoring;
- any semantic judge used as a gate has a separate qualification artifact and frozen identity/prompt/runtime/parameters;
- judge disagreement/N-A behavior is reported when the judge is used.

A material evaluator or judge change made after blind outcomes consumes that blind measurement for the new evaluation-stack generation.

## 8. Missing runs / provider failures

No failed run may be silently dropped.

- agent/task/candidate-caused failure counts as task failure;
- expected scenario tool/API faults remain part of the scenario;
- external provider/infrastructure failures are reported separately;
- only pre-model provider transport, runner/repository infrastructure or evaluator-process crashes without outcome exposure may receive one replacement attempt;
- task-quality or safety failures are never rerun as replacements;
- exhausted external failures remain explicit operational missingness and denominators/sensitivity must be disclosed.

## 9. Multiple comparisons

Candidate promotion cannot be based on exploratory metric cherry-picking.

- the primary comparison graph is preregistered;
- effect sizes + intervals are primary;
- formal p-values are secondary;
- if two or more related confirmatory p-value tests are used, Holm family-wise correction is required;
- exploratory metrics are labeled and cannot independently promote a candidate.

## 10. Blind custody and reversal path

Current blind registry state:

`NO_BLIND_SOURCE_AUTHORIZED`

Tier A remains preferred until **2026-08-25 23:59 America/Sao_Paulo**. If not operational, planning moves to Tier B.

If neither Tier A nor Tier B is operational by **2026-08-28 23:59 America/Sao_Paulo**, P3 cannot activate silently: an explicit BIG-B3 amendment is required and final claims must be downgraded.

Any semantic leak or iterative partial feedback reclassifies the affected source as exposed.

## 11. Protocol self-check

The provider-free structural self-check passed:

```text
checks passed     24 / 24
provider calls     0
private semantics  not read
source pins        3 / 3 exact Git blob matches
```

Verified pins:

- benchmark split: `12ec4bca4ffbac72ad457cc9c47f02e210e126c1`;
- BIG-B3 selection: `8164b0c61c11058680d1e075fb09b2c3d3e23ec3`;
- BIG-B2 preregistration: `3a62e25b3644b4bb37f9e8e870d91c60901da6cc`.

The connected GitHub interface did not surface a newly triggered Actions run/check at freeze time. Therefore the exact guard/freeze/authorization decision logic was executed provider-free in a sandbox mirror while blob identity was independently verified against GitHub. The committed workflow remains the regression path for future repository executions; this limitation is preserved in the machine-readable self-check result rather than hidden.

## 12. BIG-B4 exit gate

BIG-B4 requirements are now satisfied at protocol level:

- benchmark roles/manifests versioned;
- exact allowed/forbidden partition uses defined;
- adaptive selection boundary frozen;
- evaluator/judge requirements frozen;
- repeated-run/seed policy frozen;
- primary outcomes and non-compensable safety constraints frozen;
- uncertainty method frozen;
- provider/infrastructure failure handling frozen;
- multiple-comparison rule frozen;
- regression policy frozen;
- final authorization path frozen;
- blind-source custody/breach procedure frozen;
- forbidden reads and final-access prerequisites fail closed in executable self-checks.

**BIG-B4: COMPLETE.**

The Benchmark Integrity Gate B0→B4 is closed.

Agent optimization may now resume **only on permitted development evidence under P12**. FRESH_BLIND and LEGACY_LOCKED_TEST remain blocked until their separate final-authorization prerequisites are satisfied. Existing historical candidates are not automatically promoted by this freeze; they must be reinterpreted under the project decision-state model and evaluated prospectively under P12.
