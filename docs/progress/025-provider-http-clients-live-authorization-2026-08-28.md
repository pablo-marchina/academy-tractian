# Progress 025 — Concrete provider clients and bounded live-comparison authorization

**Date:** 2026-08-28  
**Issue:** #35  
**PR:** #36  
**ADR:** ADR-009  
**State:** `FROZEN_FOR_PROVIDER_HTTP_CLIENTS_AND_BOUNDED_LIVE_COMPARISON_AUTHORIZATION`  
**Scientific gate changed:** NO  
**Live provider calls executed:** 0  
**Production provider/model selected:** NO  
**Production mutating actions enabled:** NO

## Scope completed

Issue #35 / PR #36 implemented the exact ADR-008 live routes behind the already-frozen ADR-006 provider-neutral boundary without executing live inference.

New production/evidence surfaces:

- `src/academy_tractian/provider_clients.py` — SDK-free OpenAI Responses and Google Interactions clients using an injected one-shot JSON transport;
- `tests/test_provider_clients.py` — exact request shape, secret isolation, SDK/env isolation, one-call, no-retry, response extraction, route/model drift, unexpected provider-tool output and sanitized usage tests;
- `research/frozen/provider-model-live-comparison-authorization-v1.json` — exact bounded production comparison envelope;
- `scripts/research/validate_provider_live_authorization.py` — provider-free exact-blob/geometry/privacy/budget validator;
- `tests/test_provider_live_authorization.py` — authorization tamper regressions;
- `.github/workflows/provider-live-authorization.yml` — provider-free validator + tamper + full production + ADR-004 regression gate;
- `docs/adr/009-provider-http-clients-live-comparison-authorization-2026-08-28.md`.

## Preserved first implementation failure

Initial implementation head:

`b0a5bc8c2dbea0041ac0324e6471b09b9e68b644`

Validation:

```text
production-runtime run     33140883236 / #22
production tests           105 PASS / 2 FAIL
live provider calls        0
credential probes          0
```

The two failures were privacy assertions. The provider system instruction contained the internal word `idempotency`, even though no idempotency value/state was serialized. The test was not weakened. The prompt was hardened to remove unnecessary internal control vocabulary.

## Corrected concrete clients

Corrected implementation head:

`3b823c498811a138de60acd65b280cef5dfd2bb1`

Frozen identities:

```text
provider_clients.py blob       e78807bdfd4fd0ca9840fa2d9e6c62474237ee45
provider-client tests blob     16d4165b966ae47f1117fa72f87e35b0522a64ac
package exports blob           2868fe2bf73bd89d6cc0a6f49a9a096cf5d5bcd1
provider-neutral adapter blob  5579cf6f4c6bfe25d50220fa8b9ddf75c95d100a
```

Validation:

```text
production-runtime run     33140957622 / #23 success
ADR-004 regression         success
triggered workflows        11 / 11 success
live provider calls        0
```

The clients preserve:

- explicit constructor credentials only; no environment lookup in `provider_clients.py`;
- no provider SDK ownership;
- credentials only in transport headers, never in provider body/repr/usage/RunTrace;
- exactly one HTTP transport invocation per `complete()`;
- zero automatic retry/fallback/warm-up;
- no provider seed;
- stateless routes;
- no provider-native TRACTIAN tool execution;
- fail-closed route/model/status/output handling;
- separate sanitized usage accounting keyed by request SHA.

## Authorization packet validation

Frozen packet:

`research/frozen/provider-model-live-comparison-authorization-v1.json`

Git blob:

`5690414564ccddb07184c333fdf79f4ee2fb7788`

Provider-free packet-validation head:

`ad1c427a00a518424fa058c008ffc661df980c60`

```text
provider-live-authorization run  33141147959 / #1 success
production-runtime run            33141147898 / #24 success
validator                         success
tamper tests                      success
full production suite             success
ADR-004 regression                success
triggered workflows               12 / 12 success
live provider calls               0
```

Only after that packet passed was ADR-009 recorded.

## Final ADR head and merge

Final ADR head:

`a9b3b3221e132c08a2806685ac60c7d8db0d375f`

```text
provider-live-authorization run  33141264612 / #2 success
production-runtime run            33141264638 / #25 success
provider-comparison-design run    33141264586 / #5 success
triggered workflows               13 / 13 success
live provider calls               0
```

PR #36 was merged with expected-head protection into `main` as:

`c3d7ecbaf02a20276f84e4f6ff756c0bdf3779d9`

## Effective production authorization boundary

ADR-009 makes the already-validated packet effective **only for a separate governed production-comparison execution task**:

```text
live candidates                         2
public deterministic probes             8
repetitions / probe / candidate         2
maximum authorized live calls          32
live calls consumed                      0
warm-ups                                 0
retries                                  0
fallbacks                                0
parallel calls                           0
provider seed                         none
production actions                  disabled
production provider selected            NO
NO_SELECTION valid                      YES
```

This production envelope does not alter C4 scientific authorization. The current scientific gate remains `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`, and scientific provider/model calls remain 0.

## Next admissible production step

Implement and provider-free validate a separate comparison executor that:

1. verifies the exact ADR-008/009 design, population and authorization blobs;
2. materializes the exact 32-call order without consuming it in CI;
3. injects credentials outside the provider-client module;
4. captures only sanitized attempt/usage/provenance artifacts;
5. computes public-probe adjudication plus ADR-008 M1–M10/hard gates;
6. applies the exact deterministic selection rule including `NO_SELECTION`;
7. proves budget, stopping and failure handling provider-free before any authorized network execution.

The scientific score-row artifact blocker is unchanged and must continue in parallel without reconstruction or rescoring.