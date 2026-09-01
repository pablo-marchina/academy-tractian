# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-09-01 — ADR-023 merged/provider-free validated; standalone production wheel reproduction proved by PR #91; D01 reset-window gate still pending  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Current provider handoff addendum:** [`FINAL-HANDOFF-RUNBOOK-CLOUDFLARE-ADDENDUM-2026-09-01.md`](FINAL-HANDOFF-RUNBOOK-CLOUDFLARE-ADDENDUM-2026-09-01.md)

This file is the short-horizon plan. It does not authorize provider inference, credential probing or attempt 1.

`FINAL-HANDOFF-RUNBOOK.md` remains byte-pinned ADR-017 historical evidence. Current Cloudflare provider-comparison guidance is prospective and lives in this file plus the linked addendum; do not rewrite the frozen ADR-017 runbook to update provider guidance.

## 1. Completed / frozen before the real gate

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
entrypoint sufficiency audit                     ACCEPTED / ADR-023
minimal governed launcher                       MERGED / PROVIDER-FREE VALIDATED
standalone production wheel                     PROVED / PR #91

provider inference                              0
credential/account probes                       0
live network validation                         0
comparison attempts consumed                    0 / 32
```

Current canonical `main`:

```text
a93854dd5e70edf8084bdaae1762dd64cdb6aa48
```

PR #91 closed a concrete clean-reproduction gap without changing runtime/evaluator/provider semantics. Its new `standalone-wheel-smoke` job:

```text
build root wheel
→ create clean virtualenv
→ install only root wheel
→ change cwd outside repository checkout
→ import academy_tractian + research.e2.controller
→ validate canonical 18-operation registry
→ validate read-only production default
```

The job passed together with the existing production runtime regression suite.

ADR-023 freezes the entrypoint conclusion:

```text
substantive composition sufficient
operational entrypoint was the only material provider-path gap
no executor/custody/client/authorization rewrite authorized
```

The only prospective execution surface is:

```text
scripts/research/execute_cloudflare_live_comparison_v2.py
```

## 2. NOW — provider-free work before the reset

Do not add provider-path code. The safe short-horizon work is to close or classify remaining delivery gaps that are independent of provider choice.

Run these audits in order:

### A. Delivery-acceptance gap audit

Use `DELIVERY-ACCEPTANCE.md` as the row-level contract and classify each applicable P0/P1 item:

```text
PROVED
PARTIAL
BLOCKED
MISSING
```

For every `PARTIAL` or `MISSING`, record:

- exact requirement/acceptance row;
- existing repository evidence;
- missing proof or behavior;
- whether the gap is provider-independent;
- smallest provider-free validation/fix if one exists;
- whether the gap must wait for D01/#92.

Do not infer that a component is complete merely because code exists.

### B. Real-demo path completeness audit

Verify that the final integrated path can eventually demonstrate, with real runtime traces rather than scripted prose:

```text
contextualize
investigate with read tools
safe consequential-action behavior
clarify / insufficient evidence
human escalation + handoff
conflicting/inconclusive evidence
partial/unavailable tool or provider failure
customer-safe final response
per-run integrated evaluation
aggregate/reliability view
```

Before D01, this is an evidence audit. Implement only provider-independent P0/P1 omissions that do not alter frozen provider or post-D01 architecture decisions.

### C. Security / trace / failure-containment audit

Confirm provider-free evidence for:

```text
identity outside model control
seed outside model control
authorization outside model control
HarnessRunner sole tool-execution boundary
action permission/target/argument validation
idempotency / duplicate-action containment
model-call provenance sanitization
no evaluator-private truth in runtime
trace lifecycle integrity
safe failure → clarify / abstain / escalate
no credentials/private oracle in persisted traces
```

### D. Reproduction audit

Standalone wheel distribution is now `PROVED`. Preserve this as a regression obligation; do not redesign packaging unless the clean-wheel test later fails.

## 3. Rule for fixing anything found before D01

A pre-D01 change is allowed only if all conditions hold:

```text
maps to concrete P0/P1 or reproducibility/security risk
AND provider-independent
AND no ADR-018→023 semantic change
AND no provider/model call or credential probe
AND no topology/runtime/RAG/memory decision is pre-empted
AND smallest provider-free fix can be tested
```

Otherwise log the finding and defer it.

Issue #92 is planning-only until D01 resolves/bounds. It defines the later hard-gate + Pareto decision protocol for topology/runtime and optional architecture complexity.

## 4. NEXT LIVE GATE — reset window

Target window:

```text
2026-09-02 00:00:00–00:10:00 UTC
=
2026-09-01 21:00:00–21:10:00 America/Sao_Paulo
```

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

## 5. Capture Workers Free source evidence

During the reset window, retain privately/outside the repository one source artifact showing:

```text
Workers Free / Active
Workers Paid not active
```

Do not serialize account ID, email, billing details or secrets. The evidence JSON records only the source artifact SHA-256.

The canonical helper is:

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

Evidence age at receipt issuance must be <=600 seconds.

## 6. Issue the reset-window receipt provider-free

Before any provider secret is provisioned:

```powershell
python scripts/research/issue_cloudflare_reset_window_receipt_v1.py `
  --evidence "<PATH_TO_PRIVATE_EVIDENCE_JSON>" `
  --custody-root "<CANONICAL_CUSTODY_ROOT>" `
  --output "<PATH_TO_PRIVATE_RECEIPT_JSON>"
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

If it expires, do not reuse it. Wait for the next 00:00 UTC reset and capture fresh evidence.

## 7. Only after a valid receipt — provision secrets

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

Do not commit, log or serialize these values. Do not pass either value as a launcher argument.

## 8. Final pre-attempt validation

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

Attempt 1 remains unauthorized until all conditions are true and the operator separately invokes the launcher.

## 9. THEN — explicit governed live execution decision

Only after every gate above remains true may the operator explicitly invoke:

```powershell
python scripts/research/execute_cloudflare_live_comparison_v2.py `
  --evidence "<PATH_TO_PRIVATE_EVIDENCE_JSON>" `
  --receipt "<PATH_TO_PRIVATE_RECEIPT_JSON>" `
  --custody-root "<CANONICAL_CUSTODY_ROOT>"
```

The launcher is hard-pinned to:

```text
fixture_result = false
```

and delegates directly to:

```text
reset_window_authorization_to_adr020_pre_live_evidence(...)
→ CloudflareLiveSecrets(...)
→ build_cloudflare_one_shot_transport_v2()
→ GovernedCloudflareLiveTaskV2.prepare(...)
→ execute_all()
```

No retry, fallback, warm-up, parallel call, alternate model, alternate provider, alternate custody or ad-hoc Python composition is authorized.

## 10. Frozen live packet

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

## 11. After provider D01 is resolved or bounded

Activate issue #92 and run another evidence-sufficiency audit, not an automatic experiment queue.

### Hard gates before any alternative architecture is eligible

No candidate may regress:

```text
P0 behavior coverage
deterministic authorization/action safety/evaluator isolation
trace integrity and diagnosability
clean reproduction
USD 0 feasibility
bounded retry/fallback/state semantics
safe failure/clarify/abstain/escalate behavior
```

### Agent topology

Ask whether single-agent vs multi-agent can still materially change a P0/P1/final architecture decision.

- if no: keep qualified single-agent baseline and document bounded non-claim;
- if yes: preregister the minimum controlled topology comparison.

### Runtime/orchestration

Only assess after topology/materiality is closed. Compare a graph/runtime framework only if a measured requirement such as durable execution, checkpoint/resume or persistent human interruption is actually missing.

### Pareto decision

For hard-gate-passing candidates, compare correctness, tool/argument/evidence quality, escalation/fallback, stability, latency/resource use, coordination failures, operational complexity and debuggability. Do not invent an arbitrary weighted total score.

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

## 12. Parallel C4 track

Exact artifact only:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
```

No reconstruction/rescoring/substitution is authorized.

## 13. Deadline sequence

```text
09-01 before 21:00  action-plan reconciliation + provider-free acceptance/demo/security audits
09-01 21:00–21:10 D01 reset-window evidence/receipt/live gate if truthful custody exists
09-02 → 09-03       live provider result OR external-blocker freeze; activate #92
09-03 → 09-05       only still-material architecture decisions + reliability/regression
09-05 → 09-07       architecture freeze + acceptance evidence + demo/runbook/reproduction
09-08               delivery
```

After 2026-09-05, no speculative P2 experiment unless it closes a demonstrated delivery blocker.

## 14. Still forbidden

- provider inference before real receipt + explicit launcher invocation;
- token/account provisioning merely to inspect quota;
- fabricated quota values;
- using reset fallback outside the first ten minutes after 00:00 UTC;
- uncertain attestation about calls/background consumers/exclusive custody;
- Workers Paid / prepaid AI Gateway / paid spillover;
- retry/replay of claimed or uncertain attempts;
- changing ADR-018 packet post hoc;
- bypassing the governed launcher with an ad-hoc execution wrapper;
- modifying frozen executor/custody/client/authorization semantics for launcher convenience;
- C4 reconstruction/rescoring;
- topology/runtime/RAG/memory implementation before D01 unless a distinct provider-independent P0/P1 gap explicitly requires it and governance is updated first;
- final provider/architecture claims beyond evidence.
