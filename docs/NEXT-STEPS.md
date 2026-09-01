# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-09-01 — provider-free delivery/demo/security audits complete; PFG-01 escalation-handoff gap closed by PR #96; D01 is the next operational gate  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**D01 operator preflight:** [`CLOUDFLARE-D01-PREFLIGHT-2026-09-01.md`](CLOUDFLARE-D01-PREFLIGHT-2026-09-01.md)  
**Current provider handoff addendum:** [`FINAL-HANDOFF-RUNBOOK-CLOUDFLARE-ADDENDUM-2026-09-01.md`](FINAL-HANDOFF-RUNBOOK-CLOUDFLARE-ADDENDUM-2026-09-01.md)

This file is the short-horizon authorization plan. It does not itself authorize provider inference, credential probing or attempt 1.

`FINAL-HANDOFF-RUNBOOK.md` remains byte-pinned ADR-017 historical evidence. Do not rewrite it.

## 1. Provider-free work completed before D01

```text
historical evidence audit                         DONE
provider factual refresh                         DONE
Cloudflare comparison preregistration             FROZEN / ADR-018
Cloudflare direct client                         FROZEN / ADR-019
Cloudflare executor/custody v2                   FROZEN / ADR-020
original live authorization protocol             FROZEN / ADR-021
reset-window evidence amendment                  FROZEN / ADR-022
governed entrypoint contract                     ACCEPTED / ADR-023
minimal governed launcher                       MERGED / PROVIDER-FREE VALIDATED
standalone production wheel                     PROVED / PR #91
2026-09-01 delivery-acceptance audit             DONE
2026-09-01 final-demo audit                      DONE
2026-09-01 security/trace/failure audit          DONE
structured escalation handoff PFG-01            CLOSED / PR #96
D01 operator preflight                          PREPARED

provider inference                              0
credential/account probes                       0
live network validation                         0
comparison attempts consumed                    0 / 32
```

PR #96 merged the current provider-free readiness closure as:

```text
f383bbe0e87e6927411c14fd67ba8dbda9e57cbc
```

Its final head passed all 13 PR-associated workflows, including `production-runtime`, `final-delivery-provider-free-reproduction` and `final-handoff-acceptance-audit`.

## 2. What the audits concluded

### Delivery acceptance

No new provider-independent authorization/security blocker remains.

The strongest remaining bounded areas are:

```text
final non-scripted real-provider demo      D01 dependent
provider/model quality comparison          D01 dependent
provider-specific latency/resource data    D01 dependent
EV-012 exact C4 evidence                    external exact-byte blocker
final deployment/rollback evidence         later final-integration choice
```

### Demo

The frozen five-scenario provider-free demo remains valid integration evidence, but its decisions are scripted. It must not be relabeled as a final live-provider demo.

Final `PROVED` status for the real integrated agent path requires D01 to resolve or be explicitly bounded, followed by the appropriate final provider-path demonstration/limitation.

### Security / trace

Current deterministic boundaries remain supported:

```text
identity outside model control
seed outside model control
authorization outside model control
HarnessRunner sole execution boundary
strict argument validation
permission/action containment
idempotency / no replay
sanitized model-call provenance
evaluator-private truth isolated
trace lifecycle integrity
provider/tool failures fail closed
no hidden retry/fallback on governed paths
```

### Escalation handoff

The one provider-free gap found by the audit was closed prospectively by PR #96:

```text
ProductionRequest + exact RunTrace
→ ESCALATE_HUMAN
→ structured trace-linked HumanEscalationHandoff
→ deterministic validation
```

Raw observation bodies, identity/user/seed, credentials, provider raw material and evaluator-private material do not enter the handoff.

## 3. NOW — prepare only the operator-side D01 preflight

Before 21:00 BRT, use the dedicated preflight document to prepare:

- one private local root outside the repository;
- private Workers Free source-artifact path;
- fresh evidence output path;
- fresh receipt output path;
- one canonical custody root;
- assurance that no background Worker/application/integration can consume Workers AI during the governed window.

Before evidence capture and receipt issuance, provider credentials must be absent from the process. The receipt helper explicitly rejects:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
OPENAI_API_KEY
GEMINI_API_KEY
GROQ_API_KEY
```

Do not print their values merely to check whether they exist.

No more provider-path code or architecture experimentation is justified before D01.

## 4. NEXT LIVE GATE — reset window

Target window:

```text
2026-09-02 00:00:00–00:10:00 UTC
=
2026-09-01 21:00:00–21:10:00 America/Sao_Paulo
```

Proceed only if every statement is truthful:

```text
Workers Free / Active                         proven
Workers Paid                                  false
no Workers AI calls since reset               attested
no automated/background Workers AI consumer   attested
exclusive Workers AI account use              attested through packet completion
direct Workers AI route                       required
AI Gateway/prepaid unified billing            absent
comparison attempts                           0 / 32
provider inference/probe to obtain evidence   0
```

Any uncertainty fails closed to:

```text
LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
```

## 5. Capture real reset-window evidence

Retain the source artifact privately/outside the repository, then within the first ten minutes after reset run:

```powershell
python scripts/research/capture_cloudflare_reset_window_evidence_v1.py `
  --workers-free-source "<PATH_TO_PRIVATE_WORKERS_FREE_SCREENSHOT>" `
  --output "<PATH_TO_PRIVATE_EVIDENCE_JSON>" `
  --attest-workers-free-active `
  --attest-workers-paid-disabled `
  --attest-no-workers-ai-calls-since-reset `
  --attest-no-automated-workers-ai-consumers-since-reset `
  --attest-exclusive-workers-ai-window-until-packet-completion `
  --attest-direct-workers-ai-route `
  --attest-no-ai-gateway-or-prepaid-unified-billing
```

The helper uses the real UTC clock, serializes only sanitized evidence and refuses overwrite.

Evidence age at receipt issuance must be `<=600` seconds.

## 6. Issue the reset-window receipt — still provider-free

Before any provider secret is provisioned:

```powershell
python scripts/research/issue_cloudflare_reset_window_receipt_v1.py `
  --evidence "<PATH_TO_PRIVATE_EVIDENCE_JSON>" `
  --custody-root "<CANONICAL_CUSTODY_ROOT>" `
  --output "<PATH_TO_PRIVATE_RECEIPT_JSON>"
```

Receipt lifetime is `<=300` seconds and remains bound to the exact evidence/custody/ADR/plan/model/route identities.

If the receipt expires, do not reuse it.

## 7. Only after a valid receipt — provision Cloudflare secrets

Then provide locally at runtime:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

Policy remains:

```text
permission       Account > Workers AI > Read
resource scope   exact target account only
AI Gateway perms not required
Global API Key   forbidden
```

Never commit, log, serialize, paste into chat or pass either secret as a launcher argument.

## 8. Final operator gate and explicit live invocation

Immediately before invocation verify:

```text
receipt unexpired                              YES
evidence <=600 seconds old                     YES
same UTC day                                   YES
custody root exact                             YES
evidence/receipt bindings exact                YES
ADR/model/route/plan bindings exact            YES
no unrelated Workers AI use since reset       YES
exclusive account window still intact         YES
attempts consumed                              0 / 32
```

Only then invoke:

```powershell
python scripts/research/execute_cloudflare_live_comparison_v2.py `
  --evidence "<PATH_TO_PRIVATE_EVIDENCE_JSON>" `
  --receipt "<PATH_TO_PRIVATE_RECEIPT_JSON>" `
  --custody-root "<CANONICAL_CUSTODY_ROOT>"
```

The launcher remains hard-pinned to `fixture_result=False` and delegates to the frozen ADR-022→ADR-020 path.

No warm-up, credential probe, retry, fallback, parallel call, alternate model/provider/custody root or ad-hoc Python composition is authorized.

## 9. Frozen live packet / valid outcomes

```text
@cf/zai-org/glm-4.7-flash
VS
@cf/nvidia/nemotron-3-120b-a12b

8 public probes × 2 repeats × 2 candidates
max attempts        32
packet maximum      7937.522688 Neurons
selection           Pareto / NO_SELECTION allowed
```

Valid terminal outcomes:

```text
cloudflare_glm_4_7_flash_workers_free
cloudflare_nemotron_3_120b_a12b_workers_free
NO_SELECTION
LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
```

## 10. After D01

Activate issue #92 only after a governed provider result or explicit external-blocker freeze.

Sequence:

```text
D01 resolved/bounded
→ re-audit agent-topology materiality
→ if no material P0/P1 topology gap: preserve single-agent baseline
→ if material: preregister minimum controlled topology comparison
→ only after topology closure assess runtime/orchestration materiality
```

Do not add absent a measured gap:

```text
RAG/vector/reranking
persistent memory
MCP migration
adaptive routing
rich observability backend
rich UI
```

## 11. C4 parallel track

Exact artifact only:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
```

No reconstruction, rescoring or substitution is authorized.

## 12. Stop rules

Still forbidden:

- provider inference before real evidence + valid receipt + explicit launcher invocation;
- provider/account probes merely to inspect quota or credentials;
- fabricated quota/use evidence;
- uncertain exclusivity attestations;
- Workers Paid / prepaid AI Gateway / paid spillover;
- replay of claimed/uncertain attempts;
- changing ADR-018 packet after live results begin;
- bypassing the governed launcher;
- C4 reconstruction/rescoring;
- topology/runtime/RAG/memory work before D01;
- claiming the scripted provider-free demo is a live-model demonstration;
- final provider/architecture claims beyond evidence.
