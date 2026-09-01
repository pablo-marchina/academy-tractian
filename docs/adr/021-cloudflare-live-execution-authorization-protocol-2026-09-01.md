# ADR-021 — Cloudflare live-execution authorization protocol

**Status:** ACCEPTED  
**Decision state:** `FROZEN_AUTHORIZATION_PROTOCOL / REAL_EVIDENCE_PENDING / ATTEMPT_1_NOT_AUTHORIZED`  
**Date:** 2026-09-01  
**Issue:** #77  
**PR:** #78  
**Provider/model inference calls:** 0  
**Credential/account probes:** 0  
**Live network validation:** 0  
**Comparison attempts consumed:** 0 / 32  
**Real account evidence captured:** NO  
**Real authorization receipt issued:** NO  
**Real provider credentials provisioned:** NO  
**Production provider/model selected:** NO

## Decision question

Can the project freeze an operational, fail-closed authorization protocol for the ADR-018/019/020 Cloudflare comparison before any real credential/account probe, live network validation or provider inference occurs?

## Decision

Yes. Freeze the provider-free authorization capability described here and in the machine-readable protocol. A future real attempt may become admissible only after fresh account/dashboard evidence is supplied and a short-lived receipt is issued against one exact custody root.

This ADR freezes **how authorization may be issued**. It does **not** itself authorize attempt 1.

## Exact frozen identities

```text
research/experiments/cloudflare-live-authorization-protocol-v1.json
blob c641a9c98e84385dcfa8e5f14c09f4a29edf75a9

src/academy_tractian/cloudflare_live_authorization_v1.py
blob f5573e4cca51614d6c3b9139fb5bfd8fc6b2c676

scripts/research/validate_cloudflare_live_authorization_protocol_v1.py
blob 0b809c0160cb97ab4ff2c639126913b5d6362aa0

scripts/research/issue_cloudflare_live_authorization_receipt_v1.py
blob 56adc69a21be4d54cb8342c1411e6156cee8ae7a

tests/test_cloudflare_live_authorization_v1.py
blob 33dc736f6d40a50bbf1276c5567e3e63df8a1def

.github/workflows/cloudflare-live-authorization-v1-provider-free.yml
blob bfcec3a2b041175ec01ea505640b95a0e8fdf33f

research/results/cloudflare-live-authorization-v1-provider-free-validation-2026-09-01.json
blob dd78847564eabd0bf88d353a569de350f0d0f3d8
```

Upstream frozen pins remain unchanged:

```text
ADR-018 blob   e075ab4ff21904b9412769496dd2680c049cdaa8
ADR-019 blob   b8f76831aceb13f5f3ffb5d7da0e12b595d9dd1a
ADR-020 blob   857eaab01e02f4615e0a4ec3b2a74f4e16faa90e
plan SHA-256   092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb
```

## Current primary-source facts frozen for this protocol

The mutable Cloudflare facts were checked on 2026-09-01 against primary documentation:

- Workers AI pricing: `https://developers.cloudflare.com/workers-ai/platform/pricing/`
  - Free allocation: 10,000 neurons/day;
  - reset: 00:00 UTC;
  - on Workers Free, exhausting the free allocation causes further operations to fail unless the account is upgraded;
  - Workers Paid can bill usage beyond included allocation.
- Workers AI errors: `https://developers.cloudflare.com/workers-ai/platform/errors/`
  - free-allocation exhaustion is represented as HTTP 429 / internal code 3036.
- Workers AI through AI Gateway: `https://developers.cloudflare.com/ai-gateway/usage/providers/workersai/`
  - Gateway routing can be identified via `cf-aig-gateway-id`;
  - Unified Billing can consume prepaid credits.
- REST authentication: `https://developers.cloudflare.com/ai-gateway/usage/rest-api/`
  - the frozen least-privilege target for this direct Workers AI path is `Account > Workers AI > Read` on the exact target account.

If these facts materially change before real evidence capture, the protocol must be prospectively revalidated before issuing a receipt.

## Three-object authorization design

### 1. Real evidence packet

A future operator must create a sanitized evidence object from a manual Cloudflare Workers AI dashboard observation. The source screenshot/export itself remains outside the repository; only its SHA-256 is recorded in the evidence packet.

Required evidence state:

```text
Workers plan                         Workers Free
Workers Paid enabled                 false
free allocation/day                  10000 neurons
free neurons remaining               >= 9000
same UTC day                         required
observation maximum age              600 seconds
comparison attempts already used     0
provider inference to obtain evidence 0
credential/account probe             0
direct Workers AI route              true
AI Gateway route                     false
prepaid/unified billing route        false
cf-aig-gateway-id present             false
exclusive Workers AI usage window    attested
account identifier persisted         false
secret persisted                     false
```

The evidence model also requires:

```text
neurons_used_today + free_neurons_remaining = 10000
```

within the defined numeric tolerance. This makes the quota statement internally self-consistent rather than accepting a standalone remaining-value claim.

### 2. Authorization receipt

A receipt is issued locally and provider-free only after the evidence packet passes all gates.

It is:

- valid for at most 300 seconds;
- never valid beyond the 600-second evidence window;
- confined to the same UTC day;
- bound to the canonical SHA-256 of the evidence packet;
- bound to the SHA-256 of exactly one canonical custody root;
- bound to ADR-018/019/020, the v2 plan SHA, direct route and exact two model IDs;
- non-portable to another custody root;
- invalid after expiry;
- free of token, account ID and raw local path.

A synthetic receipt can be produced in provider-free tests. **No real receipt was issued in this ADR.**

### 3. Future governed live entrypoint

The already frozen ADR-020 path remains the only intended execution capability:

```text
academy_tractian.cloudflare_provider_live_v2.GovernedCloudflareLiveTaskV2.prepare(...).execute_all()
```

The authorization layer converts a valid real receipt + evidence packet to ADR-020 `CloudflarePreLiveEvidence`. It does not replace the ADR-020 custody/write-ahead/no-replay machinery.

## Secret provisioning order

Provider secrets are deliberately outside the evidence/receipt creation phase.

Required future sequence:

```text
manual dashboard evidence
→ validate evidence locally
→ select canonical custody root
→ issue short-lived receipt locally
→ only then provision CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID
→ validate receipt against exact root/evidence/time
→ separate execution decision
→ ADR-020 prepare/claim/execute path
```

Frozen secret policy:

- API token permission: `Account > Workers AI > Read`;
- resource scope: exact target account only;
- AI Gateway permission: not required and should not be granted for this task;
- Global API Key: forbidden;
- token/account ID: never serialized into evidence or receipt;
- credential probe before attempt 1: forbidden.

## Canonical receipt command

The frozen provider-free issuer is:

```text
python scripts/research/issue_cloudflare_live_authorization_receipt_v1.py --evidence <evidence.json> --custody-root <canonical-root> --output <receipt.json>
```

The issuer refuses to operate if provider credential environment variables are already present. This enforces the intended order: evidence and receipt first; secrets later.

## Freshness and concurrency rule

The evidence and receipt assume an exclusive Workers AI usage window for the target account during the authorization/execution interval.

Any other Workers AI use after the evidence observation and before/during the comparison invalidates the quota statement. In that case the receipt must not be used; capture new evidence and issue a new receipt.

Crossing the 00:00 UTC allocation reset also requires fresh evidence and a new receipt.

## Provider-free validation

Validated head before ADR freeze:

```text
0d61e7908b5e9511e851bcd2c8e1e02e2299a682
```

Dedicated workflow:

```text
cloudflare-live-authorization-v1-provider-free
run 33512426906
SUCCESS
```

Tests on that candidate:

```text
authorization protocol/evidence/receipt        8 passed
Cloudflare v2 client/executor/provenance      32 passed
ADR-010/011 executor/custody regressions      29 passed
```

All 14 PR-associated workflows on the validated head completed successfully, including `production-runtime`, `final-handoff-acceptance-audit` and `final-delivery-provider-free-reproduction`.

## Failed validation history preserved

Two provider-free failures preceded the successful candidate:

1. run `33511597396` — standalone validator lacked a repo-root bootstrap and could not import `research`; no policy change resulted;
2. run `33512055375` — receipt hashing used `+00:00` while canonical Pydantic JSON normalized UTC to `Z`, and a cross-day test reached the stale check before the UTC-day check; canonicalization/check ordering were corrected without changing policy.

No failed run consumed provider inference, credentials or comparison attempts.

## What this ADR does not prove

It does not prove:

- that the target Cloudflare account is actually on Workers Free today;
- that >=9000 neurons are actually available;
- that a token/account ID exists or works;
- that either model is reachable from the target account;
- live model quality, reliability or latency;
- that attempt 1 is currently authorized;
- which provider/model should be selected.

Those claims require future real evidence and, for model behavior, the preregistered live packet.

## Current state after freeze

```text
provider/model inference calls       0
credential/account probes            0
live network validation              0
comparison attempts consumed         0 / 32
real account evidence captured       NO
real authorization receipt issued    NO
real provider credentials provisioned NO
attempt 1 authorized                 NO
production provider/model selected   NO
customer mutations                   0
C4 changes                           0
```

## Next admissible step

A separate operational task must capture **fresh real manual Cloudflare dashboard evidence** satisfying this ADR. Only after that evidence exists may the short-lived receipt be issued. Provider credentials are provisioned only after the receipt.

That next task requires user/account-side action because this repository workflow intentionally has no access to the private Cloudflare account, dashboard state or secrets.
