# Progress 040 — Cloudflare executor/custody v2 provider-free — 2026-09-01

## Scope

Issue #75 / PR #76 implements only the execution/custody gaps demonstrated by the ADR-010/011 reuse audit. No provider inference, credential/account probe, live network validation, customer mutation or C4 change is part of this work.

## Implemented

- ADR-018/019 exact bundle loader and new Cloudflare v2 plan SHA;
- 32-attempt v2 executor reusing public P01-P08, B1, ADR-007 semantics and historical attempt evidence shape;
- result/summary v2 with observed-neuron M8 and H8/H9/H10;
- per-attempt 8000/512 limits and observed + worst-case remaining resource guard;
- exact two-model provider-free M5 failure probes;
- explicit Cloudflare token/account client factory with injected one-shot transport;
- one-root authorization marker, fixed run/, durable 32-entry write-ahead ledger, uncertain/no-replay behavior;
- provider-free pre-live evidence contract for Workers Free / no Paid or prepaid Gateway / >=9000 free neurons;
- bounded exact-Cloudflare provenance extension for the official `@cf/...` model IDs.

## CI discovery and correction

The first dedicated provider-free run (`33506528408`) produced 23 passing and 6 failing tests. The failures all occurred before any provider invocation because the historical `ProviderCallIdentity` / `ProviderModelCallRecord` regex required model IDs to begin with an alphanumeric character, while Workers AI's exact IDs begin with `@cf/`.

The project did not strip `@`, modify historical `decision_source.py`, or disable provenance. A new Cloudflare-only adapter preserves the `provider-model-call-v1` event shape, historical call-id derivation, failure codes and sanitized invariants while allowing only the two exact ADR-018 model IDs.

Corrected dedicated run `33507169465` passed:

```text
new Cloudflare v2/client/provenance tests      32 passed
historical ADR-010/011 executor/custody tests  29 passed
provider credentials present                   false
provider/model calls                           0
```

All 14 workflows on corrected implementation head `9c25143c1b37c7728d4c3130263607e6e6b0f1ed` passed.

## Frozen implementation

ADR-020 freezes:

```text
comparison v2   e12b1dfa03eb1c50bc97848821235ef422516092
live/custody v2 70d8e0ccc4d4eb003d78cdd152b1dffd30b43f29
provenance v2   e7f8bdc60910ef0acf7b14c71616448338eeefc2
comparison test b9d02070ed0d17a66a5e9aed69bf3ff6cd4d2b39
provenance test f9e752523d50876f88a6de100afb33948c602157
workflow        752f9c8906b124578164ee21885a90387842ff19
validation      d7a9d04028408d2492e0d11e20c90430709f0a3a
plan SHA-256    092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb
```

## Authorization boundary

```text
provider/model inference calls       0
credential/account probes            0
live network validation              0
comparison attempts consumed         0 / 32
production provider selected         NO
attempt 1 authorized                  NO
```

## Next

Design and freeze a separate live-execution authorization, still without inference. It must specify admissible genuine non-inference evidence for Workers Free/no Paid or prepaid Gateway/>=9000 free neurons, secret provisioning, canonical custody root and exact one-shot entrypoint. Only that later authorization may make attempt 1 admissible.
