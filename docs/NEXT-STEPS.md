# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-09-01 — ADR-022 reset-window evidence fallback provider-free validated; real reset-window evidence pending  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)

This file is the short-horizon plan. It does not authorize provider inference, credential probing or attempt 1.

## 1. Completed

```text
historical evidence audit                         DONE
provider factual refresh                         DONE
Cloudflare comparison preregistration             FROZEN / ADR-018
Cloudflare direct client                         FROZEN / ADR-019
ADR-010/011 reuse audit                          DONE
Cloudflare executor/custody v2                   FROZEN / ADR-020
original live authorization protocol             FROZEN / ADR-021
Neuron evidence-source revalidation              RESOLVED / ADR-022
Workers Free / Active                           PROVED MANUALLY

provider inference                              0
credential/account probes                       0
live network validation                         0
comparison attempts consumed                    0 / 32
```

## 2. NOW — use a real reset-window only if exclusive custody is possible

ADR-022 adds one fallback:

```text
RESET_WINDOW_ATTESTATION
```

Required real observation:

```text
00:00:00 UTC <= observation <= 00:10:00 UTC
Workers Free / Active                         proven
Workers Paid                                  false
no Workers AI calls since reset               attested
no automated/background Workers AI consumer   attested
exclusive Workers AI account use              attested through packet completion
direct Workers AI route                       required
AI Gateway/prepaid unified billing            forbidden
comparison attempts                           0 / 32
provider inference/probe to obtain evidence   0
```

Under those exact premises:

```text
documented daily reset at 00:00 UTC
+ documented Workers Free allocation 10000 Neurons/day
+ zero post-reset Workers AI use
= derived 10000 Neurons remaining
```

If any no-use/exclusive-use statement cannot be made with confidence, stop and freeze `LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED` instead.

## 3. Capture Workers Free source evidence

During the reset window, retain privately/outside the repository one source artifact showing:

```text
Workers Free / Active
Workers Paid not active
```

Do not serialize account ID, email, billing details or secrets. The evidence JSON records only the source artifact SHA-256.

The missing Neuron meter is no longer required under the reset-window fallback.

## 4. Create reset-window evidence JSON

Use schema:

```text
cloudflare-live-authorization-reset-window-evidence-v1
```

The evidence must include:

- exact UTC observation timestamp;
- exact reset timestamp `00:00:00Z` on the same UTC day;
- Workers Free/no Paid flags;
- fixed 10000 free allocation + derived 10000 remaining;
- all no-use/exclusive-use attestations;
- no Gateway/prepaid route;
- zero attempts/probes/inference;
- source artifact SHA-256;
- no account identifier or secret.

Evidence age at receipt issuance must be <=600 seconds.

## 5. Issue the reset-window receipt provider-free

Before any provider secret is provisioned:

```text
python scripts/research/issue_cloudflare_reset_window_receipt_v1.py --evidence <evidence.json> --custody-root <canonical-root> --output <receipt.json>
```

Receipt rules:

```text
lifetime <=300 seconds
expiry <= evidence validity
same UTC day
bound to evidence SHA
bound to custody-root SHA
bound to ADR-018/019/020/021 + plan + route + model IDs
contains no token/account ID/raw path
```

If it expires, do not reuse it. The reset-window itself is not replayable later in the day; wait for the next 00:00 UTC reset and capture fresh evidence.

## 6. Only after a valid receipt — provision secrets

Then securely provide at runtime:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

Policy remains:

```text
permission       Account > Workers AI > Read
resource scope   exact target account only
AI Gateway perms not required / should not be granted
Global API Key   forbidden
```

Do not commit, log or serialize these values.

## 7. Final pre-attempt validation

Immediately before attempt 1:

```text
receipt unexpired                              YES
evidence <=600 seconds old                     YES
same UTC day                                   YES
custody-root SHA exact                         YES
evidence SHA exact                             YES
ADR-018/019/020/021 pins exact                 YES
plan/model/route IDs exact                     YES
no unrelated Workers AI use since reset        YES
exclusive account window still intact          YES
comparison attempts consumed                   0
```

Any concurrent/unaccounted Workers AI usage invalidates the receipt.

## 8. THEN — explicit live execution decision

Only after all gates above are true may a separate execution action authorize:

```text
fixture_result = false
attempt 1 = admissible
```

The live path remains the ADR-020 governed executor/custody implementation.

## 9. Frozen live packet

```text
@cf/zai-org/glm-4.7-flash
VS
@cf/nvidia/nemotron-3-120b-a12b

8 public probes × 2 repeats × 2 candidates
max 32 attempts
packet worst-case 7937.522688 Neurons
```

Valid terminal outcomes:

```text
cloudflare_glm_4_7_flash_workers_free
cloudflare_nemotron_3_120b_a12b_workers_free
NO_SELECTION
LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
```

No candidate, metric, threshold, population or budget may change after results begin.

## 10. After provider D01 is resolved or bounded

Run another evidence-sufficiency audit, not an automatic experiment queue.

### Agent topology

Ask whether single-agent vs multi-agent can still materially change a P0/P1/final architecture decision.

- if no: keep qualified single-agent baseline and document bounded non-claim;
- if yes: preregister the minimum controlled topology comparison.

### Runtime/orchestration

Only assess after topology/materiality is closed. Do not conduct generic framework research.

### No-current-gap areas

Do not experiment absent new evidence:

```text
native tools vs MCP
RAG/vector/reranking
persistent memory
rich observability backend
rich UI
adaptive routing
```

## 11. Parallel C4 track

Exact artifact only:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
```

No reconstruction/rescoring/substitution is authorized.

## 12. Deadline sequence

```text
09-01 → 09-02   freeze ADR-022 + use next admissible reset if custody is possible
09-02 → 09-03   live provider result OR external-blocker freeze
09-03 → 09-05   only still-material architecture decisions + reliability/regression
09-05 → 09-07   architecture freeze + acceptance evidence + demo/runbook/reproduction
09-08           delivery
```

After 2026-09-05, no speculative P2 experiment unless it closes a demonstrated delivery blocker.

## 13. Still forbidden

- provider inference before real receipt + explicit authorization;
- token/account provisioning merely to inspect quota;
- fabricated quota values;
- using reset fallback outside the first ten minutes after 00:00 UTC;
- uncertain attestation about calls/background consumers/exclusive custody;
- Workers Paid / prepaid AI Gateway / paid spillover;
- retry/replay of claimed or uncertain attempts;
- changing ADR-018 packet post hoc;
- C4 reconstruction/rescoring;
- premature multi-agent/runtime work;
- final provider/architecture claims beyond evidence.
