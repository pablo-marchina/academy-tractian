# ADR-020 — Cloudflare executor/custody v2 provider-free implementation

**Status:** ACCEPTED  
**Decision state:** `FROZEN_IMPLEMENTATION / LIVE_NOT_AUTHORIZED`  
**Date:** 2026-09-01  
**Issue:** #75  
**PR:** #76  
**Provider/model inference calls:** 0  
**Credential/account probes:** 0  
**Live network validation:** 0  
**Comparison attempts consumed:** 0 / 32  
**Production provider/model selected:** NO

## Decision question

Can the seven concrete execution/custody gaps demonstrated by the ADR-010/011 reuse audit be closed for ADR-018/019 while preserving the historical frozen executor/custody bytes, using only provider-free fakes/mocks and without authorizing attempt 1?

## Decision

Yes. Freeze the new Cloudflare-specific v2 execution/custody capability as a bounded prospective implementation. It reuses the provider-neutral ADR-010/011 invariants and closes only the gaps demonstrated by issue #73/#75.

This ADR freezes capability only. It does **not** authorize a real Cloudflare request.

## Exact frozen implementation identities

```text
src/academy_tractian/cloudflare_provider_comparison_v2.py
blob e12b1dfa03eb1c50bc97848821235ef422516092

src/academy_tractian/cloudflare_provider_live_v2.py
blob 70d8e0ccc4d4eb003d78cdd152b1dffd30b43f29

src/academy_tractian/cloudflare_provider_provenance_v2.py
blob e7f8bdc60910ef0acf7b14c71616448338eeefc2

tests/test_cloudflare_provider_comparison_v2.py
blob b9d02070ed0d17a66a5e9aed69bf3ff6cd4d2b39

tests/test_cloudflare_provider_provenance_v2.py
blob f9e752523d50876f88a6de100afb33948c602157

.github/workflows/cloudflare-executor-custody-v2-provider-free.yml
blob 752f9c8906b124578164ee21885a90387842ff19

research/results/cloudflare-executor-custody-v2-provider-free-validation-2026-09-01.json
blob d7a9d04028408d2492e0d11e20c90430709f0a3a
```

Upstream frozen identities remain:

```text
ADR-018 blob             e075ab4ff21904b9412769496dd2680c049cdaa8
ADR-019 blob             b8f76831aceb13f5f3ffb5d7da0e12b595d9dd1a
Cloudflare client blob   a5c814b519584b6d4346e3b0567bbc3da8ba0bf4
design-v2 blob           f70837fca46fa8ecf1e63b33ea41dec73fc051e3
population SHA-256       561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251
```

## Canonical v2 plan

The public population remains unchanged. The two exact candidates remain:

```text
cloudflare_glm_4_7_flash_workers_free
@cf/zai-org/glm-4.7-flash

cloudflare_nemotron_3_120b_a12b_workers_free
@cf/nvidia/nemotron-3-120b-a12b
```

Geometry remains:

```text
8 public units × 2 repeats × 2 candidates = 32 maximum attempts
```

The new candidate identities require a new canonical plan SHA rather than reusing ADR-010's historical plan identity:

```text
Cloudflare v2 plan SHA-256
092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb
```

## Closed gap 1 — current frozen bundle and plan

The v2 bundle verifies the exact ADR-018 design, public population, ADR-018, ADR-019 and Cloudflare client blobs. It accepts only the two production-selection candidates frozen by ADR-018 and preserves the alternating `(unit_index + repeat_index) % 2` order.

It does not mutate or reinterpret the historical ADR-010 bundle.

## Closed gap 2 — result/summary v2

The v2 result keeps the provider-neutral M1-M7 and M10 evidence structure and adds the ADR-018 resource fields:

- exact usage-record completeness;
- total observed neurons per candidate;
- packet observed neurons;
- required actual cash cost USD 0 state;
- Cloudflare-specific M9 operational fields;
- H8/H9/H10 failure codes.

Raw provider request/response/exception content remains absent.

## Closed gap 3 — M8 neurons and H8/H9/H10

Frozen rates and ceilings:

```text
GLM input       5,500 neurons / 1M input tokens
GLM output     36,400 neurons / 1M output tokens
Nemotron input 45,455 neurons / 1M input tokens
Nemotron output 136,364 neurons / 1M output tokens

prompt ceiling / attempt       8,000 tokens
completion ceiling / attempt     512 tokens
complete packet ceiling       7,937.522688 neurons
Workers Free daily allocation 10,000 neurons
```

The implementation fails closed when exact usage is missing, when an observed attempt exceeds either token ceiling, or when resource accounting becomes incomplete. Before the next attempt it verifies:

```text
cumulative observed neurons
+
frozen worst-case remaining-attempt neurons
<=
available free-neuron evidence
```

No missing value is fabricated.

## Closed gap 4 — provider-free M5 probes

The fixed failure probe invariant from ADR-011 is reused for both exact ADR-019 model configurations. Each probe uses an injected local failing transport and requires:

- exactly one client invocation;
- zero retry;
- zero fallback;
- one sanitized provenance event;
- `CLIENT_FAILURE` containment;
- no raw request/response/exception persistence;
- zero network calls.

## Closed gap 5 — exact Cloudflare client factory

The v2 factory accepts explicit `api_token` and `account_id`, constructs exactly two ADR-019 clients, and receives an injected transport. It performs no environment lookup and no credential/account probe.

`build_cloudflare_one_shot_transport_v2()` reuses the provider-neutral historical `UrllibProviderJsonTransport` construction semantics. Constructing it performs no network operation.

## Closed gap 6 — authorization/custody v2

The ADR-011 security invariants are preserved prospectively:

```text
one canonical durable custody root
exclusive custody marker
fixed internal run/
32 canonical ledger entries
CLAIMED persisted before network-capable invocation
claimed exception -> uncertain
no automatic resume
no replay of uncertain attempt
second run in same root refused
sanitized immutable result
credentials persisted false
raw provider material persisted false
```

The current marker is `cloudflare-adr018-live-comparison-custody-v2.json` and pins ADR-018, ADR-019, Cloudflare client, v2 plan identity and the sanitized pre-live evidence hash.

## Closed gap 7 — pre-live evidence gate capability

`CloudflarePreLiveEvidence` can represent the evidence a later separately governed live-authorization task must provide. It fails closed unless all of these are true:

```text
workers_plan                         Workers Free
workers_paid_enabled                 false
prepaid_ai_gateway_enabled           false
direct_workers_ai_route              true
actual_cash_cost_usd                 0
free_neurons_remaining               >= 9000 and <= 10000
inference_used_to_obtain_evidence    false
credential_account_probe_used        false
```

This task did not populate that object from a real Cloudflare account. The implementation proves the gate, not the real account state.

## Prospective Cloudflare provenance compatibility extension

The first provider-free CI run exposed a real historical compatibility assumption: ADR-007's historical `ProviderCallIdentity` / `ProviderModelCallRecord` model-id regex requires the first character to be alphanumeric, while both exact Workers AI model IDs begin with `@cf/`.

The following resolutions were rejected:

- strip `@` or otherwise rewrite the model identity;
- modify the frozen historical `decision_source.py` bytes;
- disable M10 provenance.

The accepted bounded resolution is `cloudflare_provider_provenance_v2.py`.

It preserves:

- persisted `schema_version = provider-model-call-v1`;
- `adapter_version = provider-decision-adapter-v1`;
- the exact ADR-007 call-id payload and SHA-256 derivation;
- provider/model/route/request-hash identity checks;
- one invocation;
- zero retry/fallback;
- sanitized response hash/failure code semantics;
- raw request/response/exception flags fixed false.

It expands only the accepted model-id domain, and only to the two exact ADR-018 values:

```text
@cf/zai-org/glm-4.7-flash
@cf/nvidia/nemotron-3-120b-a12b
```

No candidate, population, metric, threshold, route, request contract, resource budget or call geometry changed because of this compatibility fix.

## Selection semantics preserved

No global weighted score is introduced. Selection remains:

1. hard-gate/threshold eligibility;
2. Pareto non-dominance over M4/M7 maximize and M6 p95/M8 neurons minimize;
3. M4 margin >= 0.125 when unique;
4. otherwise lower observed neurons if stability remains within 0.125;
5. otherwise lower p95 when both are complete;
6. otherwise `NO_SELECTION`.

Fixture/provider-free runs can never select a production provider.

## Provider-free validation

### Initial run

Dedicated run `33506528408` produced `23 passed / 6 failed`. All six failures had the same cause: the historical provenance model-id regex rejected the exact `@cf/...` IDs before any model call. Credential absence and ADR-018 validation had already passed.

No provider/model call or credential/account probe occurred during the failed run.

### Corrected run

Head `9c25143c1b37c7728d4c3130263607e6e6b0f1ed`:

```text
cloudflare-executor-custody-v2-provider-free   SUCCESS
new Cloudflare v2/client/provenance tests       32 passed
historical ADR-010/011 executor/custody tests   29 passed
provider credentials present                    false
provider/model inference calls                  0
credential/account probes                       0
live network validation                         0
```

All 14 workflows triggered on the corrected head completed successfully, including:

- `production-runtime`;
- `final-handoff-acceptance-audit`;
- `final-delivery-provider-free-reproduction`;
- E9/E14/benchmark-split regressions.

## What this ADR proves

It proves provider-free capability for the exact ADR-018/019 execution/custody requirements, including the seven audited gaps and the exact-Cloudflare provenance compatibility discovered by CI.

It does **not** prove:

- Cloudflare credential validity;
- actual account plan;
- current free-neuron balance;
- live route behavior;
- live latency/reliability/model quality;
- production provider selection.

## Still not authorized

```text
real Cloudflare HTTP request                 NO
credential/account probe for evidence        NO
comparison attempt 1                         NO
provider/model selection                     NO
production actions                           DISABLED
customer mutation                            NO
C4 change                                    NO
semantic/FRESH_BLIND/LEGACY_LOCKED_TEST      NO
```

## Next admissible step

The next provider task is a **separate live-execution authorization design/freeze**, still without inference. It must define how genuine non-inference evidence for Workers Free / no Paid or prepaid Gateway / >=9,000 free neurons is obtained and frozen, how explicit secrets are provisioned without persistence, the canonical custody root, and the exact one-shot invocation command.

Only after that separate authorization is accepted and frozen may attempt 1 become admissible.
