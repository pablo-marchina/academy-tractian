# ADR-022 — Cloudflare reset-window Neuron evidence amendment

**Status:** ACCEPTED CANDIDATE / FINAL PR REGRESSION PENDING  
**Decision state:** `PROSPECTIVE_EVIDENCE_SOURCE_AMENDMENT / PROVIDER_FREE_VALIDATED / LIVE_NOT_AUTHORIZED`  
**Date:** 2026-09-01  
**Trigger issue:** #80  
**Implementation issue:** #82  
**PR:** #84  
**Provider/model inference calls:** 0  
**Credential/account probes:** 0  
**Live network validation:** 0  
**Comparison attempts consumed:** 0 / 32  
**Real reset-window evidence captured:** NO  
**Real authorization receipt issued:** NO  
**Attempt 1 authorized:** NO

## Decision question

ADR-021 requires an explicit current Neuron balance, but the target account's current `AI → Workers AI` dashboard does not expose that meter. What is the smallest defensible non-inference fallback that preserves the same USD 0/resource guarantees without inventing usage values?

## Decision

Preserve ADR-021 byte-for-byte and add one prospective alternative evidence mode:

```text
RESET_WINDOW_ATTESTATION
```

This fallback may derive a 10,000-Neuron starting allocation only when all of the following are true:

```text
Cloudflare primary docs still state 10,000 Neurons/day
Cloudflare primary docs still state reset at 00:00 UTC
Workers Free / Active is proven
Workers Paid is false
observation occurs from 00:00:00 through 00:10:00 UTC
no Workers AI calls occurred since reset
no automated/background Workers AI consumer ran since reset
exclusive Workers AI account use is attested through packet completion
direct Workers AI route only
AI Gateway / prepaid unified billing absent
comparison attempts consumed = 0
provider inference used to obtain evidence = 0
credential/account probe used to obtain evidence = 0
```

Under these conditions, the starting state is derived as:

```text
00:00 UTC documented reset
+ Workers Free daily allocation = 10,000 Neurons
+ no post-reset Workers AI consumption
= 10,000 Neurons remaining at evidence observation
```

If any premise is uncertain, authorization fails closed.

## Historical preservation

ADR-021 remains immutable:

```text
docs/adr/021-cloudflare-live-execution-authorization-protocol-2026-09-01.md
blob 9627219e5b9c64dda83d23e0f3e99f4c9b953519
```

The original explicit dashboard-balance path remains valid if the target UI later exposes the required Neuron values. ADR-022 adds a fallback; it does not rewrite the original evidence.

## Primary-source basis checked 2026-09-01

Cloudflare Workers AI pricing documentation:

`https://developers.cloudflare.com/workers-ai/platform/pricing/`

Current facts used by the amendment:

- Workers Free receives 10,000 Neurons per day at no charge;
- all limits reset daily at 00:00 UTC;
- exceeding the Free allocation causes further operations to fail; Workers Paid is required to continue above the free allocation.

Cloudflare Workers AI errors:

`https://developers.cloudflare.com/workers-ai/platform/errors/`

- exhausted daily free allocation is HTTP 429 / internal code 3036.

Cloudflare Workers AI changelog:

`https://developers.cloudflare.com/changelog/post/2026-07-28-models-require-workers-paid/`

- both frozen candidates remain listed as available on Workers Free:
  - `@cf/zai-org/glm-4.7-flash`;
  - `@cf/nvidia/nemotron-3-120b-a12b`.

If any material fact changes before a real reset-window observation, this amendment must be revalidated before receipt issuance.

## Frozen candidate implementation identities

Provider-free candidate validated before freeze documentation:

```text
research/experiments/cloudflare-live-authorization-reset-window-amendment-v1.json
blob 0da205900cb3cfdef3f4129a9549c007acc91bf9

src/academy_tractian/cloudflare_live_authorization_reset_v2.py
blob e30b6a473fd9f738c046377bc52bd689360ff2f7

scripts/research/validate_cloudflare_reset_window_amendment_v1.py
blob 830307700cfd68b6758218c42284fe8e4f9ea4fd

scripts/research/issue_cloudflare_reset_window_receipt_v1.py
blob 76faf82e70fe89c87e17a4c79564540e20d5604a

tests/test_cloudflare_live_authorization_reset_v2.py
blob ae316deddb98c681cfcc4190737d3d79c0c8ffb5
```

The final workflow blob is frozen after the documentation-aware PR regression completes.

## Time semantics

### Reset observation window

A reset-window observation is admissible only during:

```text
00:00:00 UTC <= observed_at_utc <= 00:10:00 UTC
```

The ten-minute cap is intentionally conservative. It minimizes the interval in which an unobserved/background consumer could invalidate the no-use premise and gives a simple operational procedure.

### Evidence freshness

At receipt issuance:

```text
evidence age <= 600 seconds
```

### Receipt lifetime

```text
receipt lifetime <= 300 seconds
receipt expiry <= evidence validity
same UTC day required
```

Crossing the next UTC day invalidates the authorization context.

## Required real source artifact

The real reset-window evidence must still include a private/out-of-repo source artifact proving:

```text
Workers Free / Active
Workers Paid not active
```

Only the source artifact SHA-256 is serialized. Account ID, email, billing details and secrets remain outside evidence/receipt artifacts.

The Neuron balance itself is not read from the missing meter under this fallback; it is derived from the documented reset plus the explicit no-use attestations.

## Mandatory operator attestations

The operator must be able to attest all three without qualification:

```text
1. no Workers AI calls have occurred on the target account since 00:00 UTC;
2. no automated/background Worker, application, user or integration capable of consuming Workers AI has run since reset;
3. no unrelated Workers AI usage will occur until the governed comparison finishes or aborts.
```

If the account cannot be placed under this exclusive-use custody, use neither this fallback nor a fabricated balance. The correct result is external blocker.

## Resource semantics

The amendment does not weaken ADR-018/020 resource guards.

Starting state under an admissible reset-window receipt:

```text
free_neurons_remaining = 10000
```

ADR-020 still owns:

- exact observed usage accounting;
- H8/H9/H10;
- input/output ceilings;
- projection before the next attempt;
- stop-before-next-attempt semantics;
- missing usage fail-closed behavior;
- 32-entry write-ahead ledger and no replay.

The preregistered packet worst case remains `7937.522688` Neurons, so the reset-derived state is stronger than the historical `>=9000` start gate rather than weaker.

## Explicitly rejected alternatives

Still forbidden as canonical quota evidence:

- interpreting a missing dashboard meter as `used=0`;
- DevTools/private dashboard APIs;
- Alpha/Restricted generic billable usage API;
- sacrificial inference call;
- credential/account API probe merely to discover quota;
- reducing the 9000-Neuron requirement;
- relying on operator memory without explicit no-use/exclusive-use attestation.

## Provider-free validation

Initial candidate head:

```text
90913cc23b1baa021ec89ddd316bf55d452fae3c
```

Dedicated workflow:

```text
cloudflare-reset-window-amendment-provider-free
run 33519145953
SUCCESS
```

The dedicated job confirmed:

- provider credentials absent;
- amendment validator passed;
- reset-window authorization tests passed;
- ADR-021 authorization regressions passed;
- Cloudflare executor/client/provenance regressions passed.

All PR-associated workflows on that initial candidate completed successfully before freeze documentation was added.

## What this ADR does not prove

It does not prove:

- that no Workers AI use has actually occurred on a future reset day;
- that the target account can be held exclusively during the live packet;
- that Cloudflare credentials exist or work;
- that either model is reachable at live execution time;
- model quality/reliability/latency;
- that attempt 1 is currently authorized;
- that either candidate should be selected.

## Current state

```text
provider/model inference calls       0
credential/account probes            0
live network validation              0
comparison attempts consumed         0 / 32
real reset-window evidence captured  NO
real receipt issued                  NO
provider credentials provisioned     NO
attempt 1 authorized                 NO
production provider selected         NO
```

## Next admissible step after final PR freeze

At a future daily reset, an account-side operator may capture Workers Free evidence within the first ten minutes after 00:00 UTC and provide the required no-use/exclusive-use attestations. Only then may the provider-free reset-window receipt be issued.

For America/Sao_Paulo on 2026-09-01, 00:00 UTC corresponds to 21:00 local time on the preceding calendar date relationship for the active UTC day. Operational instructions must always use UTC as the canonical clock to avoid DST/time-zone ambiguity.
