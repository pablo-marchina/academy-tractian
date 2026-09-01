# Progress 043 — Cloudflare reset-window evidence amendment

**Date:** 2026-09-01  
**Trigger:** #80  
**Implementation:** #82  
**PR:** #84

## Trigger

The target Cloudflare account proves `Workers Free / Active`, but its current Workers AI UI does not expose the explicit current Neuron balance assumed by ADR-021.

The project refused to infer `used=0`, use private dashboard endpoints, perform a credential probe or spend an inference call to manufacture quota evidence.

## Primary-source revalidation

Cloudflare primary documentation checked 2026-09-01 confirms:

- 10,000 Neurons/day free allocation;
- reset at 00:00 UTC;
- Workers Free fails closed on exhaustion;
- frozen GLM 4.7 Flash and Nemotron 3 120B remain listed as available on Workers Free.

## Prospective amendment

ADR-022 adds `RESET_WINDOW_ATTESTATION` while preserving ADR-021 byte-for-byte.

Required conditions:

```text
observation <=00:10:00 UTC
Workers Free / Active
Workers Paid false
no Workers AI calls since reset
no automated/background Workers AI consumers since reset
exclusive target-account Workers AI custody through packet completion
direct Workers AI route
no AI Gateway/prepaid unified billing
0 / 32 comparison attempts
0 inference/probes used to obtain evidence
```

Only under these conditions is `10000` derived as the starting free-Neuron state.

## Provider-free implementation

Added:

- machine-readable reset-window amendment;
- `CloudflareResetWindowEvidenceV1`;
- short-lived root/evidence-bound reset-window receipt;
- conversion to ADR-020 pre-live evidence;
- provider-free receipt issuer;
- static validator;
- fail-closed tests;
- dedicated provider-free workflow.

## Initial validation

Initial candidate head:

`90913cc23b1baa021ec89ddd316bf55d452fae3c`

Dedicated workflow:

`cloudflare-reset-window-amendment-provider-free` / run `33519145953` / `SUCCESS`.

All PR-associated workflows on the initial candidate were successful. No provider credential was present in the dedicated workflow.

## Hard boundaries preserved

```text
provider/model inference calls       0
credential/account probes            0
live network validation              0
comparison attempts consumed         0 / 32
real reset-window evidence captured  NO
real receipt issued                  NO
attempt 1 authorized                 NO
production provider selected         NO
```

## Next gate

Complete the final documentation-aware PR regression. If green, merge ADR-022, close #80/#82, and resume #79 only during a real admissible reset window. If exclusive account custody cannot be established, freeze the external blocker rather than weaken the amendment.
