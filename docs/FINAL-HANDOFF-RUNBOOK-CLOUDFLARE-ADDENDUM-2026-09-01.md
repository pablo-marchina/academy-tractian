# Final Handoff Runbook — Cloudflare Provider Addendum (2026-09-01)

**Status:** CURRENT / prospective operational addendum  
**Applies to:** provider-comparison guidance only  
**Historical runbook preserved:** `docs/FINAL-HANDOFF-RUNBOOK.md` blob `c7df131f555e3b07161fd1d518965958d245555c`  
**Live execution authorized by this document:** NO

## Why this addendum exists

`docs/FINAL-HANDOFF-RUNBOOK.md` is byte-pinned by the ADR-017 final-handoff freeze and must remain unchanged for historical reproducibility.

Its section 7 describes the historical issue #44 OpenAI/Gemini comparison as the then-current provider fallback. That statement is valid historical evidence for the ADR-017 handoff baseline, but it is no longer the current provider execution guidance after ADR-018 through ADR-023.

This addendum prospectively supersedes **only** the provider-comparison operational guidance in the frozen historical runbook. It does not rewrite or invalidate ADR-017.

## Current governed provider path

The current candidate packet is:

```text
@cf/zai-org/glm-4.7-flash                    16 maximum attempts
@cf/nvidia/nemotron-3-120b-a12b              16 maximum attempts
total                                          32 maximum attempts
consumed                                        0 / 32 at current baseline
automatic retries                               0
fallbacks                                       0
warm-ups                                        0
parallel provider calls                         0
packet worst-case                               7937.522688 Neurons
Workers Paid / prepaid spillover                forbidden
```

Current governance layers:

```text
ADR-018   Cloudflare comparison preregistration
ADR-019   direct Workers AI client
ADR-020   executor/custody/resource accounting
ADR-021   original live authorization protocol
ADR-022   reset-window evidence fallback
ADR-023   entrypoint sufficiency audit + minimal launcher contract
```

The historical issue #44 OpenAI/Gemini packet remains evidence only and must not be substituted for this path.

## Current operational sequence

A live comparison may be attempted only after all applicable ADR-022/023 gates are true:

```text
admissible reset-window evidence
→ short-lived receipt bound to exact custody root
→ only then provision CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID
→ confirm exclusive Workers AI account custody still holds
→ explicit operator live-execution decision
→ canonical ADR-023 launcher
→ frozen ADR-020 packet
```

If evidence, freshness, exact-root binding or exclusive custody cannot be established, do not weaken the protocol. The correct terminal state is:

```text
LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
```

## Canonical live command

Only after every gate remains true:

```text
python scripts/research/execute_cloudflare_live_comparison_v2.py --evidence <evidence.json> --receipt <receipt.json> --custody-root <canonical-root>
```

The launcher accepts no provider/model/retry/fallback/budget/fixture options. It reads only:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

from the runtime environment after receipt issuance and delegates to the frozen ADR-022 authorization adapter and ADR-020 governed task with `fixture_result=False`.

## Provider-free reproduction remains unchanged

The ADR-017 historical runbook remains the canonical provider-free reproduction artifact for its frozen baseline. Do not edit its expected blobs or frozen evidence to incorporate this addendum.

A provider-free regression failure is never authorization to invoke the live Cloudflare packet.

## Reviewer interpretation

For current delivery review:

- use the frozen `FINAL-HANDOFF-RUNBOOK.md` for ADR-017 provider-free reproduction evidence;
- use this addendum plus `NEXT-STEPS.md` for current provider-comparison execution guidance;
- treat issue #44 OpenAI/Gemini as historical only;
- treat ADR-018→023 Cloudflare as the current governed provider path;
- keep provider calls at `0 / 32` unless a separately authorized launcher invocation actually records consumed attempts.
