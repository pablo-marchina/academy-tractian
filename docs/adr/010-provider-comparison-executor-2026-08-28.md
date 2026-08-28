# ADR-010 — Provider comparison executor — 2026-08-28

**Status:** ACCEPTED  
**Decision state:** `FROZEN_FOR_PROVIDER_COMPARISON_EXECUTOR`  
**Issue:** #38  
**PR:** #39  
**Scientific state changed:** NO  
**Production provider/model selected:** NO  
**Production mutating actions enabled:** NO  
**Live provider/model calls consumed by this decision task:** 0

## Decision question

Can the exact ADR-008/ADR-009 production provider/model comparison be materialized by one deterministic, auditable executor before any authorized live call is consumed, while preserving the frozen population, call geometry, controller/B1/B2 ownership, ADR-007 provenance, M1–M10, hard gates and `NO_SELECTION` rule?

## Context

ADR-008 froze the prospective comparison design. ADR-009 froze the concrete SDK-free OpenAI/Gemini clients and created a bounded authorization for a **separate governed execution task** of at most 32 live calls. Neither ADR provided the execution/evidence aggregation layer that turns those frozen inputs into exact attempt order, budget accounting, public-rubric adjudication, M1–M10 summaries and deterministic selection evidence.

Issue #38 therefore remained provider-free. It was required to prove the executor on injected fixture clients before a later live task can consume any ADR-009 call.

## Decision

Accept `src/academy_tractian/provider_comparison.py` as the production provider-comparison execution/evidence boundary for the exact ADR-008/ADR-009 design.

Frozen provider-free implementation identity:

```text
validated pre-ADR head             58e0e13a2a0ec72d86ab607162914dcf3f6a4159
provider_comparison.py blob        4357aa101f5a15d5fc8376b17fa38ca51ea72ae3
test_provider_comparison.py blob   6663177bb96a8fdffd15fa64c9cc7e5a92edf2e3
fixture validator script blob      563b47e14dbf6119deef167ae8926261c38ed07a
provider-free fixture result blob  7c3972b2e467de4a21c6ef353f5427bf7651b4d9
canonical plan SHA-256             69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f
```

Machine-readable freeze:

`research/frozen/provider-comparison-executor-freeze-v1.json`

The freeze also pins the final regression workflow and freeze self-check test. It becomes the canonical executor freeze only if the exact final ADR head revalidates successfully.

## Frozen input custody

The executor fails closed unless the checkout retains the exact ADR-008/ADR-009 inputs:

```text
design manifest blob       9c3d0901414445bd4de557d5ef1d2f68a15c883b
population blob            abd6a7d973a8779f425c3607d963e29f15db09e5
population SHA-256         561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251
live authorization blob    5690414564ccddb07184c333fdf79f4ee2fb7788
ADR-009 blob               016ac0c40e12db211ebf7dfbab3acd258369fa0b
provider clients blob      e78807bdfd4fd0ca9840fa2d9e6c62474237ee45
provider adapter blob      5579cf6f4c6bfe25d50220fa8b9ddf75c95d100a
frozen package exports     2868fe2bf73bd89d6cc0a6f49a9a096cf5d5bcd1
```

This is deliberately stricter than simply loading files by path. A modified frozen input requires prospective governance rather than silent reuse.

## Canonical attempt geometry and budget

The executor materializes exactly:

```text
public units                         8
repetitions / unit / candidate       2
live candidates                      2
potential live attempts             32
attempt indexes                   0..31
warm-up calls                        0
automatic retries                    0
fallbacks                            0
parallel live calls               false
provider seed forwarded           false
```

Order remains the ADR-008 rule:

1. P01 → P08;
2. repeat 0 then repeat 1;
3. candidate order alternates by `(unit_index + repeat_index) % 2`;
4. one canonical global `attempt_index` is assigned before execution.

`LiveCallBudget` has no reset API. It accepts only the next canonical attempt index and rejects attempt 33. In provider-free fixture mode the same counter mirrors potential live-call geometry without making network calls.

## Controller and tool-execution ownership

The executor does **not** own or execute TRACTIAN tools.

For one planned attempt it:

```text
frozen public unit
→ ControllerContext
→ ProviderDecisionSource
→ injected ProviderDecisionClient
→ ControllerDecision / fail-closed provider failure
→ public rubric + canonical B1 validation only
→ sanitized attempt evidence
```

It never calls `HarnessRunner.execute_tool()`. Therefore:

- B0/binding remains runner-owned;
- B1 argument semantics remain the canonical `research.e2.validation.validate_arguments(...)` contract;
- B2 consequential-action authorization remains ADR-005/runtime-owned;
- tool transport is never performed by the comparison executor;
- provider-native TRACTIAN execution remains forbidden.

A later live comparison evaluates decision proposals, not real consequential system mutation.

## Raw-output and custody boundary

The provider JSON string is passed directly into the unchanged ADR-006 strict parser. The comparison executor does not persist it.

A narrow ephemeral inspection wrapper records only booleans indicating whether exact forbidden binding/private key names appeared. This is required to measure the frozen M3/H1 boundary when ADR-006 rejects a proposal before a `ControllerDecision` can be returned.

Persisted attempt evidence is limited to:

- attempt/candidate/unit/repeat identity;
- request hash and sanitized ADR-007 call ID;
- success/failure family;
- decision kind/tool name;
- B1 issue codes;
- forbidden-key booleans;
- public-rubric pass/fail;
- sanitized usage counts;
- latency;
- trace-integrity issue codes;
- safe-failure containment.

Credentials, raw headers, raw provider requests, raw responses, exception bodies, private evaluator material and runtime authorization state are not part of the result schema.

## Public deterministic probe adjudication

All eight frozen public DEV rubrics are implemented without semantic judging or private truth:

- P01 — exact `get_asset(asset_dev_probe_001)` proposal;
- P02 — exact `list_analyses(asset_dev_probe_002)` proposal;
- P03 — exact `get_data_quality(asset_dev_probe_003)` proposal;
- P04 — `search_knowledge` query containing BPFO case-insensitively, with only frozen allowed optional types;
- P05 — `CLARIFY` with non-empty message;
- P06 — `ESCALATE` with non-empty message;
- P07 — `ABSTAIN`/`ESCALATE` with reason/message and no retry of failed `get_rms`;
- P08 — terminal `FINAL`/`ABSTAIN`/`ESCALATE` with non-empty content and no retry of blocked `reprocess_analysis`.

## M1–M10 implementation

The executor implements the preregistered measurements without a weighted aggregate:

- **M1** — strict decision adherence / attempted provider invocations;
- **M2** — known canonical tool validity / parsed TOOL decisions;
- **M3** — canonical B1-valid arguments / known-tool proposals; identity/seed attempts reported separately;
- **M4** — frozen public rubric passes / fixed 16 attempts per candidate; failures remain zero-valued denominator members;
- **M5** — safely contained encountered failures plus one fixed provider-free injected failure case per provider client;
- **M6** — latency count, median, nearest-rank p90/p95 and max;
- **M7** — successful client response rate / 16 and paired repeat decision-signature stability / 8;
- **M8** — exact provider usage only. Missing accounting inputs remain `UNKNOWN`; they are never imputed;
- **M9** — frozen hosting/credential/route constraints plus observed operational constraints;
- **M10** — valid ADR-007 provenance / attempted calls.

For the currently frozen OpenAI price basis, a separate cached-input price exists but ADR-009 usage telemetry does not expose an exact cached-input split. The executor therefore returns normalized OpenAI cost as `UNKNOWN` rather than pretending all input is uncached or cached. This is a deliberate fidelity rule, not missing-data repair.

## Hard gates and selection

The executor applies disqualifying custody/safety/provenance gates before selection. Incomplete packets remain ineligible.

Selection preserves the ADR-008 order:

1. disqualify hard-gate/threshold failures;
2. return `NO_SELECTION` if no live candidate remains;
3. compute conservative Pareto non-dominance over M4/M7 maximize and comparable M6/M8 minimize;
4. choose a unique non-dominated candidate if one exists;
5. otherwise allow a quality lead only at the frozen ≥0.125 margin;
6. otherwise use comparable exact cost only with the frozen stability guard;
7. otherwise use lower p95 latency only when both candidates completed all 16 attempts;
8. otherwise return `NO_SELECTION`.

Unknown cost is not assigned an artificial best/worst value; it cannot create pairwise Pareto dominance. Fixture evidence and incomplete evidence are forcibly non-selecting regardless of synthetic scores.

## Provider-free fixture evidence

Frozen fixture result:

`research/results/provider-comparison-executor-provider-free-fixture-2026-08-28.json`

Status:

`PASS_PROVIDER_FREE_FIXTURE_NO_SELECTION`

Stable evidence:

```text
fixture_result                    true
simulated potential attempts        32
live provider calls consumed         0
baseline public-rubric rate       0.25
OpenAI M1/M2/M3/M4/M5/M7/M10      1.0
Google M1/M2/M3/M4/M5/M7/M10      1.0
OpenAI normalized exact cost       UNKNOWN
Google fixture normalized cost    0.0024 USD
hard-gate pass                    true / true
selection                         NO_SELECTION
production selection claim       false
```

M6 is executed and must yield 16 nonnegative measurements per candidate, but provider-free wall-clock values are intentionally omitted from the frozen fixture identity because they are environment-dependent. Future live M6 values remain real evidence and are not replaced by this fixture.

## Preserved validation history

### Initial implementation governance failure

Head:

`c2f5f11ec3fa5030b5422cceceba1de1e839b3b4`

`production-runtime` run `33142884381` (#27): **130 passed / 1 failed**.

The failure was not an executor test. The implementation had unnecessarily added executor exports to `src/academy_tractian/__init__.py`, violating ADR-009's exact frozen package-export blob. The correct fix restored that file byte-exact rather than weakening the authorization validator.

No provider call occurred.

### Corrected core

Head:

`60427a1f123e57bffa934b3ce2639ed2662dbd9c`

```text
production-runtime run   33142983309 / #28 success
triggered workflows      11 / 11 success
ADR-009 validator        success
ADR-004 regression       success
live provider calls      0
```

### Dedicated fixture-gate bootstrap failure

Head:

`3c16171528449e5fca9bc4a80555eca1be2432b5`

`provider-comparison-executor` run `33143114620` (#1) failed before fixture execution because the standalone validator script did not put the repository root on Python's import path. The fixture result, thresholds and executor semantics were not changed. The script bootstrap was fixed; history was retained.

No provider call occurred.

### Validated pre-ADR executor

Head:

`58e0e13a2a0ec72d86ab607162914dcf3f6a4159`

```text
provider-comparison-executor    33143175929 / #2 success
production-runtime              33143175942 / #30 success
fixture projection              success
executor-specific tests         success
ADR-009 validator               success
full production suite           success
ADR-004 controller regression   success
triggered workflows             12 / 12 success
live provider calls             0
```

Only after this provider-free evidence passed was ADR-010 recorded.

## Scope and authorization boundary

ADR-010 freezes the **executor**, not a provider winner and not a live result.

It does not consume or enlarge ADR-009. A later separately governed execution task may use this exact frozen executor to consume the still-unconsumed ADR-009 envelope, subject to all ADR-008/009 stop rules and any required current route/credential preflight that does not alter the protocol.

Current state remains:

```text
ADR-009 maximum production live-call envelope   32
ADR-009 live calls consumed                       0
production provider/model selected               NO
production mutating actions enabled               NO
scientific provider/model calls authorized         0
scientific gate          REQUIRED_PER_GROUP_AND_SLICE_REPORTING
semantic/private/blind evaluation authorized      NO
production readiness claimed                      NO
```

## Reversal / amendment triggers

A prospective amendment is required if any frozen input, client route/model, public population, attempt geometry, metric formula, threshold, hard gate, selection rule or custody boundary must change.

After the first future live call, consumed evidence may never be rewritten or discarded to create a cleaner comparison. Any material change creates a new protocol/candidate version.

## Regression obligations

Any change touching this executor or its frozen dependencies must preserve:

1. exact frozen-input/blob validation;
2. 32-entry plan hash/geometry;
3. attempt-33 rejection and canonical prefix accounting;
4. provider-free fixture projection PASS;
5. executor/tamper/selection tests PASS;
6. ADR-009 authorization validator PASS;
7. full production suite PASS;
8. ADR-004 controller regression PASS;
9. zero real provider calls in provider-free CI;
10. zero production action execution until separately governed.

The exact final ADR head must pass the dedicated `provider-comparison-executor` workflow before this freeze is considered canonical.
