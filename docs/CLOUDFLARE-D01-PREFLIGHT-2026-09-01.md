# Cloudflare D01 Preflight — 2026-09-01

**Live observation window:** `2026-09-01 21:00:00–21:10:00 America/Sao_Paulo` = `2026-09-02 00:00:00–00:10:00 UTC`  
**Live attempts before window:** `0 / 32`  
**This document authorizes no provider call by itself.**

## 1. Prepare local private paths before 21:00

Use a location outside the repository for all real account evidence and custody state.

Example PowerShell variables (replace the root with your preferred private local path):

```powershell
$privateRoot = "$HOME\Documents\academy-tractian-private\cloudflare-d01-2026-09-01"
$source      = Join-Path $privateRoot "workers-free-active.png"
$evidence    = Join-Path $privateRoot "reset-window-evidence.json"
$receipt     = Join-Path $privateRoot "reset-window-receipt.json"
$custodyRoot = Join-Path $privateRoot "custody"

New-Item -ItemType Directory -Force $privateRoot | Out-Null
New-Item -ItemType Directory -Force $custodyRoot | Out-Null
```

Before capture, `$evidence` and `$receipt` must not already exist. The canonical helpers intentionally refuse overwrite/replay.

## 2. Ensure provider credentials are absent before evidence/receipt

Both evidence capture and receipt issuance are provider-free and must happen before provider secrets are provisioned.

The receipt helper explicitly forbids these environment variables at issuance time:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
OPENAI_API_KEY
GEMINI_API_KEY
GROQ_API_KEY
```

PowerShell check:

```powershell
$forbidden = @(
  "CLOUDFLARE_API_TOKEN",
  "CLOUDFLARE_ACCOUNT_ID",
  "OPENAI_API_KEY",
  "GEMINI_API_KEY",
  "GROQ_API_KEY"
)

$present = $forbidden | Where-Object { [Environment]::GetEnvironmentVariable($_, "Process") }
if ($present) { throw "Provider credentials must be absent before receipt: $($present -join ', ')" }
```

Do not print secret values. If a variable is present in the current process, remove it from that process before the reset-window evidence capture rather than logging it.

## 3. Manual account-custody check

Do not proceed unless all are truthful at the real reset:

```text
Workers plan = Free / Active
Workers Paid = disabled
no Workers AI calls since 00:00 UTC
no automated/background Worker/app/integration consuming Workers AI since reset
no unrelated Workers AI usage until packet completion/abort
direct Workers AI route only
no AI Gateway / prepaid unified billing
comparison attempts = 0 / 32
```

Disable or otherwise ensure exclusivity for any background Worker/application/integration that could call Workers AI. Do not infer exclusivity from lack of visible traffic.

## 4. Retain the private Workers Free source artifact

During the admissible window, retain a private screenshot/source artifact showing the target account is Workers Free / Active and Workers Paid is not active. Save it at `$source` or another private path.

The repository receives only its SHA-256 through the sanitized evidence JSON; the screenshot itself stays outside the repository.

## 5. Capture evidence — first 10 minutes after reset

```powershell
python scripts/research/capture_cloudflare_reset_window_evidence_v1.py `
  --workers-free-source $source `
  --output $evidence `
  --attest-workers-free-active `
  --attest-workers-paid-disabled `
  --attest-no-workers-ai-calls-since-reset `
  --attest-no-automated-workers-ai-consumers-since-reset `
  --attest-exclusive-workers-ai-window-until-packet-completion `
  --attest-direct-workers-ai-route `
  --attest-no-ai-gateway-or-prepaid-unified-billing
```

Success must report provider inference `0`, credential/account probes `0`, and live network validation `0`.

If the helper rejects the time window or any attestation cannot truthfully be made, stop. Do not override the clock or weaken validation.

## 6. Issue receipt immediately — still no provider secrets

Evidence age must be `<=600s`; receipt lifetime is `<=300s`.

```powershell
python scripts/research/issue_cloudflare_reset_window_receipt_v1.py `
  --evidence $evidence `
  --custody-root $custodyRoot `
  --output $receipt
```

If receipt issuance fails or the receipt expires before invocation, do not reuse it and do not improvise another custody root. The reset-window evidence is not a generic same-day authorization token.

## 7. Only after valid receipt — provision Cloudflare secrets locally

Set the two Cloudflare variables in the local process without pasting them into chat, source control, command history where avoidable, logs or artifacts:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

Required token policy remains exact target account with `Account > Workers AI > Read`; Global API Key and AI Gateway permissions are not required.

## 8. Final operator gate before attempt 1

Confirm all:

```text
receipt unexpired                              YES
evidence <=600 seconds old                     YES
same UTC day                                   YES
custody root exact                             YES
evidence/receipt exact                         YES
ADR/model/route/plan bindings exact            YES
no unrelated Workers AI usage since reset     YES
exclusive account window still intact         YES
attempts consumed                              0 / 32
```

Any uncertainty means `LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED`, not an exploratory provider request.

## 9. Explicit live execution

Only after the preceding checks:

```powershell
python scripts/research/execute_cloudflare_live_comparison_v2.py `
  --evidence $evidence `
  --receipt $receipt `
  --custody-root $custodyRoot
```

There is no warm-up, credential probe, retry, fallback, alternate model/provider/custody root or ad-hoc Python execution path.

## 10. Terminal outcomes

Only these outcomes are legitimate:

```text
cloudflare_glm_4_7_flash_workers_free
cloudflare_nemotron_3_120b_a12b_workers_free
NO_SELECTION
LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
```

Preserve all custody/output artifacts exactly as produced. Do not replay a claimed or uncertain attempt.