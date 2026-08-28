# 026 — Provider comparison executor — FROZEN / PROVIDER-FREE — 2026-08-28

Issue #38 / PR #39 closed the missing execution/evidence layer between the frozen ADR-008 comparison design and the ADR-009 bounded live-call authorization without consuming any provider call.

## Delivered boundary

The accepted executor is:

`src/academy_tractian/provider_comparison.py`

Frozen source blob:

`4357aa101f5a15d5fc8376b17fa38ca51ea72ae3`

It verifies exact ADR-008/009 input identities before planning, creates the canonical 32-attempt order, enforces a non-resettable attempt budget, converts the 8 frozen public probes into `ControllerContext`, invokes only an injected ADR-006 `ProviderDecisionSource`, and records sanitized comparison evidence.

It deliberately does **not** call `HarnessRunner.execute_tool()` or execute TRACTIAN reads/actions. B1 argument semantics remain owned by the canonical validator and B2 action authorization remains ADR-005/runtime-owned.

Canonical plan:

```text
SHA-256                            69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f
public units                       8
repeats / unit / candidate         2
live candidates                    2
potential live attempts           32
attempt indexes                 0..31
warmups                            0
automatic retries                  0
fallbacks                          0
parallel provider calls            0
provider seed                      none
```

## Public evaluation surface

The executor implements all eight frozen public DEV rubrics and ADR-008 M1–M10 without a semantic/private judge.

Important fidelity behavior:

- operational failures stay in denominators;
- fixture/incomplete evidence cannot select a production provider;
- unknown cost is not imputed;
- the currently frozen OpenAI exact normalized cost remains `UNKNOWN` when cached-input split is unavailable in ADR-009 telemetry;
- hard-gate failures disqualify rather than being compensated by quality/cost;
- unresolved evidence returns `NO_SELECTION`.

## Provider-free fixture

Frozen result:

`research/results/provider-comparison-executor-provider-free-fixture-2026-08-28.json`

Git blob:

`7c3972b2e467de4a21c6ef353f5427bf7651b4d9`

Status:

`PASS_PROVIDER_FREE_FIXTURE_NO_SELECTION`

```text
simulated potential attempts             32
live provider calls                        0
baseline public-rubric rate             0.25
OpenAI M1/M2/M3/M4/M5/M7/M10            1.0
Google M1/M2/M3/M4/M5/M7/M10            1.0
Google normalized fixture cost          0.0024 USD
OpenAI normalized exact cost            UNKNOWN
hard-gate pass                          true / true
selection                               NO_SELECTION
production selection claim             false
raw provider material recorded         false
```

M6 latency is exercised and checked nonnegative for every fixture attempt, but provider-free wall-clock values are intentionally excluded from frozen fixture identity.

## Preserved failure 1 — ADR-009 export mutation

Initial implementation head:

`c2f5f11ec3fa5030b5422cceceba1de1e839b3b4`

`production-runtime` run `33142884381` (#27):

```text
production tests  130 passed / 1 failed
```

The failure came from changing `src/academy_tractian/__init__.py`, whose exact blob was already frozen by ADR-009. Executor tests themselves did not fail. The fix restored the exact ADR-009 export blob instead of weakening the authorization validator.

Live provider calls: **0**.

Corrected core head:

`60427a1f123e57bffa934b3ce2639ed2662dbd9c`

```text
production-runtime             33142983309 / #28 success
triggered workflows            11 / 11 success
live provider calls            0
```

## Preserved failure 2 — standalone validator import bootstrap

First dedicated-gate head:

`3c16171528449e5fca9bc4a80555eca1be2432b5`

`provider-comparison-executor` run `33143114620` (#1) failed before fixture comparison because the direct Python script did not put repository root on `sys.path`. No metric, candidate, threshold or fixture semantics changed. Import bootstrap was corrected.

Live provider calls: **0**.

## Pre-ADR validation

Head:

`58e0e13a2a0ec72d86ab607162914dcf3f6a4159`

```text
provider-comparison-executor     33143175929 / #2 success
production-runtime               33143175942 / #30 success
fixture projection               success
executor-specific tests          success
ADR-009 validator                success
full production suite            success
ADR-004 regression               success
triggered workflows              12 / 12 success
live provider calls              0
```

Only after that provider-free PASS was ADR-010 written.

## Final freeze

ADR:

`docs/adr/010-provider-comparison-executor-2026-08-28.md`

Machine-readable freeze:

`research/frozen/provider-comparison-executor-freeze-v1.json`

Final branch head:

`dd15ce32362247066edf0a476f8a9e93eb6cdbe8`

Final exact-head validation:

```text
provider-comparison-executor     33143341273 / #3 success
production-runtime               33143341274 / #31 success
provider-model-comparison-design 33143341229 / #6 success
provider-live-authorization      33143341282 / #3 success
all triggered workflows          14 / 14 success
live provider calls              0
production action calls          0
```

PR #39 was merged with an expected-head guard as:

`903b977928ff19bc63c6ff35acd92f233af813be`

ADR-010 state:

`FROZEN_FOR_PROVIDER_COMPARISON_EXECUTOR`

## Post-merge boundary

```text
ADR-009 authorized live-call maximum          32
ADR-009 calls consumed                         0
provider comparison executor                   frozen / ADR-010
production provider/model selected             NO
production mutating actions enabled             NO
scientific provider/model calls authorized       0
scientific gate        REQUIRED_PER_GROUP_AND_SLICE_REPORTING
semantic/private/blind access                   NO
production readiness claimed                    NO
```

The next product step is a separate live execution task. It may use this exact executor and the still-unconsumed ADR-009 envelope only when required secrets are explicitly provisioned. Missing secrets must stop the task before attempt 0; credential/account probing, silent route substitution and warm-up requests remain forbidden.
