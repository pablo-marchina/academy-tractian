# ADR-024 — Cloudflare same-day zero-use Neuron evidence amendment

**Status:** PROPOSED / PROVIDER-FREE VALIDATION REQUIRED  
**Decision state:** `PROSPECTIVE_SAME_DAY_ZERO_USE_AMENDMENT / LIVE_NOT_AUTHORIZED_UNTIL_MERGED`  
**Date:** 2026-09-01  
**Issue:** #98  
**Provider/model inference calls before this amendment:** 0  
**Credential/account probes before this amendment:** 0  
**Live network validation before this amendment:** 0  
**Comparison attempts consumed:** 0 / 32

## Decision question

ADR-022 permits reset-derived 10,000-Neuron evidence only during the first ten minutes after 00:00 UTC. The target Workers AI dashboard does not expose the explicit Neuron meter required by ADR-021. If the account-side operator can attest with absolute certainty that no Workers AI call or automated/background consumer has run since the current UTC-day reset, can the same documented reset arithmetic remain valid later in the same UTC day without weakening the cost/resource controls?

## Decision

Yes, prospectively, through a new additive evidence mode:

```text
SAME_DAY_ZERO_USE_ATTESTATION
```

ADR-021, ADR-022 and ADR-023 remain byte-for-byte unchanged. This amendment does not reinterpret an already-observed provider result: no provider inference, credential/account probe, live network validation or comparison attempt occurred before this decision.

The ten-minute rule in ADR-022 was explicitly conservative rather than a Cloudflare billing/reset boundary. ADR-024 removes only that capture-offset cap. It does not remove evidence freshness or receipt freshness.

## Primary-source facts rechecked before the decision

Cloudflare Workers AI pricing, rechecked 2026-09-01:

- Workers Free receives 10,000 Neurons/day at no charge;
- limits reset daily at 00:00 UTC;
- Workers Free cannot continue beyond the free allocation without upgrade/paid capacity.

Source: `https://developers.cloudflare.com/workers-ai/platform/pricing/`

Cloudflare Workers AI plan-access changelog, rechecked 2026-09-01:

- `@cf/zai-org/glm-4.7-flash` remains Workers Free-accessible;
- `@cf/nvidia/nemotron-3-120b-a12b` remains Workers Free-accessible.

Source: `https://developers.cloudflare.com/changelog/post/2026-07-28-models-require-workers-paid/`

## Same-day derivation

A fresh observation may derive the full allocation only when every premise below is explicitly true:

```text
Workers plan = Workers Free / Active
Workers Paid = false
current UTC day reset occurred at 00:00:00 UTC
no Workers AI calls since that reset
no automated/background Workers AI consumer since that reset
exclusive Workers AI account custody maintained until packet completion/abort
direct Workers AI route only
AI Gateway route absent
prepaid/unified billing absent
comparison attempts consumed = 0
provider inference used to obtain evidence = 0
credential/account probe used to obtain evidence = 0
```

Then:

```text
documented daily allocation = 10,000
+ documented reset at 00:00 UTC
+ attested consumption since reset = 0
= derived free Neurons remaining = 10,000
```

If any premise becomes uncertain, the derivation is invalid and execution fails closed.

## Freshness remains strict

The attestation covers the interval from reset to observation, but the evidence object itself must be fresh:

```text
evidence age at receipt issuance <= 600 seconds
receipt lifetime <= 300 seconds
receipt expiry <= evidence expiry
receipt and evidence stay in the same UTC day
```

Crossing 00:00 UTC requires a new observation/evidence/receipt.

## Required private source artifact

The operator retains outside the repository a source artifact proving the target account is Workers Free / Active and Workers Paid is not active. Only its SHA-256 enters the evidence object.

The artifact does not need to expose a Neuron meter: the meter is absent on the target UI, which is the reason ADR-022/024 exist.

No account ID, email, billing detail, token, secret or raw local source path may be serialized in evidence/receipt.

## Secret provisioning order

Provider secrets remain forbidden during evidence capture and receipt issuance:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
OPENAI_API_KEY
GEMINI_API_KEY
GROQ_API_KEY
```

Required order:

```text
fresh same-day source + attestations
→ sanitized evidence
→ exact custody root
→ provider-free receipt
→ only then provision CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID
→ validate receipt/evidence/root/time
→ explicit live launcher decision
```

## Execution architecture

ADR-024 adds no executor. Its evidence/receipt adapter produces the existing ADR-020 `CloudflarePreLiveEvidence`, after which the existing frozen task owns all live behavior:

```text
ADR-024 evidence + receipt + exact custody root
→ same_day_zero_use_authorization_to_adr020_pre_live_evidence(...)
→ CloudflareLiveSecrets from environment only
→ build_cloudflare_one_shot_transport_v2()
→ GovernedCloudflareLiveTaskV2.prepare(..., fixture_result=False)
→ execute_all()
```

The dedicated operator-facing launcher is:

```text
scripts/research/execute_cloudflare_live_comparison_same_day_v1.py
```

## Unchanged ADR-020 controls

This amendment does not change:

- 8 public probes × 2 repeats × 2 candidates = max 32 attempts;
- packet worst-case `7937.522688` Neurons;
- 8000 input / 512 output ceilings;
- exact usage/Neuron accounting;
- stop-before-next-attempt projection;
- missing-usage fail-closed behavior;
- write-ahead `CLAIMED` ledger;
- uncertain/no-replay semantics;
- USD 0 / no paid spillover;
- direct Workers AI route;
- no retry/fallback/warm-up/alternate model/provider/custody.

The derived 10,000-Neuron state remains stronger than the original `>=9000` start gate.

## Provider-free implementation surface

```text
research/experiments/cloudflare-live-authorization-same-day-zero-use-amendment-v1.json
src/academy_tractian/cloudflare_live_authorization_same_day_v3.py
scripts/research/capture_cloudflare_same_day_zero_use_evidence_v1.py
scripts/research/issue_cloudflare_same_day_zero_use_receipt_v1.py
scripts/research/execute_cloudflare_live_comparison_same_day_v1.py
scripts/research/validate_cloudflare_same_day_zero_use_amendment_v1.py
tests/test_cloudflare_live_authorization_same_day_v3.py
tests/test_cloudflare_same_day_governed_live_entrypoint.py
.github/workflows/cloudflare-same-day-zero-use-amendment-provider-free.yml
```

## Explicitly rejected alternatives

Still forbidden:

- treating a missing usage meter alone as proof of `used=0`;
- claiming zero use without explicit account-side attestation;
- sacrificial inference to test the token/quota;
- private/undocumented dashboard endpoints as quota evidence;
- credential/account probing before the receipt;
- reducing the 9000-Neuron start requirement;
- enabling Workers Paid or prepaid AI Gateway;
- changing the frozen packet after any result exists;
- replaying claimed or uncertain attempts.

## Authorization state

This ADR is not live authorization merely because the operator provided the attestation. Attempt 1 remains unauthorized until:

1. this prospective amendment passes provider-free CI and is merged;
2. fresh real evidence is captured using the merged helper;
3. the short-lived real receipt is issued against the exact custody root;
4. Cloudflare secrets are provisioned only after receipt issuance;
5. the operator explicitly invokes the same-day governed launcher while all attestations remain true.

Until then:

```text
provider inference          0
credential/account probes   0
live network validation     0
attempts                    0 / 32
attempt 1                   NOT AUTHORIZED
```
