# Progress 041 — Cloudflare live authorization protocol

**Date:** 2026-09-01  
**Issue:** #77  
**PR:** #78  
**Scope:** provider-free authorization protocol only

## Objective

Design, validate and freeze how a future ADR-018/019/020 live comparison may be authorized without making any provider inference, credential/account probe or live network request in this task.

## Implemented

- machine-readable authorization protocol v1;
- sanitized real-evidence schema;
- 10-minute evidence freshness gate;
- 5-minute receipt TTL bounded by evidence validity;
- same-UTC-day gate;
- Workers Free / >=9000-neuron gate;
- direct-route/no-Gateway/no-prepaid-unified gate;
- source-artifact SHA custody without storing account identifier or secret;
- canonical custody-root hash binding;
- exact ADR-018/019/020 + plan/model/route binding;
- least-privilege token policy;
- provider-free receipt issuer that refuses to run when provider credentials are already present;
- conversion to ADR-020 pre-live evidence;
- dedicated provider-free workflow and tests.

## Validation history

### Failure 1 — run 33511597396

The standalone validator could not import the repository `research` namespace because the editable install does not package it. Fixed by bootstrapping the repo root in the two standalone authorization scripts. No policy/gate changed.

### Failure 2 — run 33512055375

The receipt SHA was computed from UTC `+00:00` strings while Pydantic canonical JSON normalizes UTC to `Z`, causing hash mismatch. The cross-day test also reached the stale gate first. Fixed by canonical UTC `Z` serialization and checking UTC day before age. No authorization threshold or policy changed.

### Passing candidate

Head `0d61e7908b5e9511e851bcd2c8e1e02e2299a682`:

```text
cloudflare-live-authorization-v1-provider-free  SUCCESS / run 33512426906
authorization tests                             8 passed
Cloudflare v2 regressions                       32 passed
ADR-010/011 regressions                         29 passed
all workflows                                   14/14 success
provider credentials                            absent
provider calls                                  0
```

## Freeze

ADR-021 freezes the successful protocol/tooling bytes and records the state:

`FROZEN_AUTHORIZATION_PROTOCOL / REAL_EVIDENCE_PENDING / ATTEMPT_1_NOT_AUTHORIZED`

No real evidence packet or authorization receipt was created.

## Hard boundaries preserved

```text
provider/model inference calls       0
credential/account probes            0
live network validation              0
comparison attempts consumed         0 / 32
real account evidence captured       NO
real authorization receipt issued    NO
provider secrets provisioned         NO
attempt 1 authorized                 NO
production provider selected         NO
customer mutations                   0
C4 changes                           0
```

## Next step

Real manual Cloudflare Workers AI dashboard evidence must be captured by an account-side operator, one canonical custody root selected, and a short-lived receipt issued provider-free before secrets are provisioned. This is the first point in the provider path requiring user/account-side access.
