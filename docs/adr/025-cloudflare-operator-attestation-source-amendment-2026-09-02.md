# ADR-025 — Cloudflare operator-attestation source amendment

**Status:** ACCEPTED CANDIDATE  
**Decision state:** `PROSPECTIVE_OPERATOR_ATTESTATION / PROVIDER_FREE_VALIDATION_PENDING / LIVE_NOT_AUTHORIZED`  
**Date:** 2026-09-02  
**Trigger issue:** #100

## Problem

ADR-024 still requires a private file intended to prove `Workers Free / Active` and `Workers Paid disabled`. The target account UI does not expose the requested plan/usage screen, so that source requirement is operationally unavailable. Requiring a fabricated, empty, or unrelated file would be worse than explicitly recording the evidence boundary.

No provider inference, credential/account probe, live validation, or comparison attempt has occurred before this amendment.

## Decision

Preserve ADR-021, ADR-022, ADR-023 and ADR-024 byte-for-byte and add one new prospective evidence mode:

```text
OPERATOR_PLAN_STATE_ATTESTATION
```

The account-side operator may explicitly attest, without an external screenshot/file:

```text
Workers Free / Active
Workers Paid disabled
no Workers AI calls since current 00:00 UTC reset
no automated/background Workers AI consumer since reset
exclusive Workers AI account custody through packet completion/abort
direct Workers AI route only
no AI Gateway / prepaid unified billing route
comparison attempts consumed = 0
provider inference used to obtain evidence = 0
credential/account probe used to obtain evidence = 0
```

The evidence object records that account-plan state is **operator-attested**, not independently dashboard-proved. No source-artifact hash is invented.

## External resource basis

Cloudflare primary pricing documentation, rechecked 2026-09-02, states:

- Workers AI has a 10,000-Neuron/day free allocation;
- limits reset daily at 00:00 UTC;
- usage above the free allocation requires Workers Paid and is billable;
- the frozen candidates `@cf/zai-org/glm-4.7-flash` and `@cf/nvidia/nemotron-3-120b-a12b` remain Workers Free-accessible.

The operator attestation establishes account-specific state; Cloudflare documentation establishes the allocation/reset semantics. Neither substitutes for the other.

## Freshness and execution boundary

```text
evidence age <= 600 seconds
receipt lifetime <= 300 seconds
same UTC day required
```

Before receipt issuance, provider credential environment variables remain forbidden. Attempt 1 remains unauthorized until a valid receipt is issued and the explicit launcher is invoked.

## Existing runtime preserved

ADR-020 remains unchanged and continues to own:

- exact observed Neuron accounting;
- minimum 9,000 free Neurons before attempt 1;
- frozen packet and model identities;
- stop-before-next-attempt projection;
- missing-usage fail-closed behavior;
- write-ahead `CLAIMED` ledger;
- no replay for claimed/uncertain attempts;
- zero hidden retry/fallback;
- USD 0 / no paid spillover semantics.

The new adapter produces the same existing `CloudflarePreLiveEvidence` only after every operator attestation and receipt binding passes.

## Windows portability correction

Two provider-free operator failures exposed CLI portability gaps that CI did not catch:

1. root scripts added the repository root but not `src/` to `sys.path`;
2. historical ADR pin validation hashed worktree bytes, which can differ on Windows because Git may materialize CRLF while the canonical Git blob is LF.

ADR-025 scripts add both `src/` and repo root explicitly. Historical pins are checked against `git rev-parse HEAD:<path>` object IDs, not mutable worktree line endings. This preserves the Git blob identity rather than weakening it.

## Explicitly rejected

- asking again for a dashboard screen that is unavailable;
- creating an empty/dummy source file;
- pretending an operator attestation is independent dashboard evidence;
- provider/credential probes to discover plan or quota;
- sacrificial inference;
- changing the frozen packet, models, retry policy, custody, or executor;
- authorizing live execution before provider-free validation and merge.

## Pre-live state

```text
provider inference          0
credential/account probes   0
live network validation     0
comparison attempts         0 / 32
real ADR-025 evidence       NONE
real ADR-025 receipt        NONE
attempt 1                   NOT AUTHORIZED
production provider         NOT SELECTED
```
