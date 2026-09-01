# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-09-01 — ADR-020 Cloudflare executor/custody v2 provider-free implementation frozen  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Frozen preregistration:** [`adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md`](adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md)  
**Frozen provider-free client:** [`adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md`](adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md)  
**Frozen executor/custody v2:** [`adr/020-cloudflare-executor-custody-v2-provider-free-implementation-2026-09-01.md`](adr/020-cloudflare-executor-custody-v2-provider-free-implementation-2026-09-01.md)

This is the short-horizon execution plan. It does **not** authorize provider inference, credential/account probing for evidence, customer mutation or C4 advancement.

## 1. Completed provider decision work

```text
historical evidence audit                         DONE
current USD-0 provider factual refresh           DONE
four provider pre-benchmark factual gates         DONE
material D01 comparison gap                       DEMONSTRATED
minimum Cloudflare comparison preregistration     FROZEN / ADR-018
provider-free Cloudflare client                   FROZEN / ADR-019
ADR-010/011 execution/custody reuse audit         DONE
bounded Cloudflare executor/custody v2            FROZEN / ADR-020
exact @cf provenance compatibility                FROZEN / ADR-020
provider-free v2 validation                       PASS
provider/model inference calls                    0
credential/account probes                         0
live network validation                           0
comparison attempts consumed                      0 / 32
production provider selected                      NO
```

All seven execution gaps demonstrated by the reuse audit are closed at the provider-free capability level.

## 2. NOW — separate live-execution authorization design/freeze

The next task is **authorization design only**, not a live run.

It must answer one question:

> Under exactly which externally verifiable, non-inference preconditions may the already-frozen ADR-018/019/020 machinery consume comparison attempt 1?

No Cloudflare inference is admissible while this authorization is being designed or frozen.

## 3. Required authorization packet

The prospective live authorization must pin at minimum:

### A. Exact code/protocol identities

```text
ADR-018 preregistration
ADR-019 exact Cloudflare client
ADR-020 comparison/provenance/custody v2
Cloudflare v2 plan SHA
092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb
```

It must fail closed if any pinned byte or plan identity changes.

### B. Exact provider/model/route identities

Only:

```text
@cf/zai-org/glm-4.7-flash
@cf/nvidia/nemotron-3-120b-a12b
provider: cloudflare
route: cloudflare.workers_ai.openai_compat.chat_completions.v1
```

Any model or route drift is a stop condition, not a fallback opportunity.

### C. Genuine zero-cost pre-live evidence

Before attempt 1, the future authorization must establish **without model inference**:

```text
workers_plan                       Workers Free
workers_paid_enabled               false
prepaid_ai_gateway_enabled         false
direct_workers_ai_route            true
actual_cash_cost_usd               0
free_neurons_remaining             >= 9000
free_neurons_remaining             <= 10000
credential_account_probe_used      false, unless a prospective amendment explicitly proves a safe non-inference account-state read is necessary and admissible
```

Do not invent or self-attest account state. The authorization design must specify what artifact/UI/export/configuration evidence is acceptable and how its provenance is preserved.

### D. Secret provisioning boundary

The authorization must specify how these two execution-owned values are supplied:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

Requirements:

- explicit provisioning only;
- no repo persistence;
- no result/ledger/marker persistence;
- no secret in repr/errors/logs;
- secret presence alone is not evidence that account gates pass;
- no provider capability/model call merely to test the credential.

If GitHub Actions is chosen for the later execution, secrets must be supplied through GitHub Actions secrets by the operator; the current ChatGPT GitHub connector cannot create repository secrets.

### E. Canonical custody root

Freeze exactly one durable execution root and preserve:

```text
exclusive authorization marker
fixed run/
32 canonical entries
CLAIMED fsync before invocation
no retry/replay after claimed or uncertain attempt
no alternate run root to reset budget
immutable sanitized result
```

### F. Resource guard

Before every next claim, the already-implemented ADR-020 rule must remain:

```text
observed neurons
+
frozen worst-case remaining-attempt neurons
<=
validated available free neurons
```

Also preserve:

```text
prompt <= 8000
completion <= 512
packet <= 7937.522688 neurons
missing exact usage -> fail closed
paid/nonfree route -> disqualifying
```

## 4. Authorization design acceptance criteria

Before any real request can be authorized:

- exact ADR-018/019/020 blobs and v2 plan SHA pinned;
- exact two `@cf/...` model IDs pinned;
- source and timestamp/UTC-day semantics for pre-live free-plan/quota evidence defined;
- evidence freshness/reversal condition defined;
- secret delivery method defined without persistence;
- canonical custody root defined;
- exact command/entrypoint defined;
- attempt-1 transition explicitly separated from authorization preparation;
- no hidden warm-up/test call;
- no credential/account inference probe;
- no retry/fallback/parallel path;
- `NO_SELECTION` remains valid;
- provider/model calls during authorization-design task remain 0.

## 5. What the authorization task must NOT do

```text
call Cloudflare model endpoint             NO
consume attempt 1                          NO
check token by making inference            NO
change candidate/model/route               NO
change M1-M10 thresholds                   NO
change population                          NO
change 32-attempt geometry                 NO
change resource budget                     NO
change ADR-020 after seeing model output    NO
select provider                            NO
```

If the real-account evidence mechanism cannot be established cleanly, the correct result is an authorization blocker — not a workaround call.

## 6. After live authorization freezes

Only then can a separate execution task:

1. provision the exact approved credentials;
2. materialize the approved pre-live evidence;
3. reserve the canonical custody root once;
4. invoke the exact ADR-020 governed entrypoint;
5. consume at most the remaining 32-attempt envelope;
6. stop fail-closed on any resource/provenance/custody violation;
7. freeze either the selected candidate or honest `NO_SELECTION` evidence.

Execution and selection remain separate from the current authorization-design step.

## 7. Provider/model roles remain

```text
Cloudflare GLM 4.7 Flash      LIVE CANDIDATE / NOT YET EXECUTED
Cloudflare Nemotron 3 120B    LIVE CANDIDATE / NOT YET EXECUTED
Groq GPT-OSS                  HISTORICAL_CONTROL_ONLY
Gemini 3.7 Flash Free         PUBLIC/SYNTHETIC ONLY UNDER CURRENT DATA-USE BOUNDARY
Cloudflare Gemma 4 26B        EXCLUDED FROM MINIMUM FIRST PACKET
Ollama qwen3:4b               CONDITIONAL LOCAL BASELINE / OUTSIDE CORE PACKET
old ADR-008/#44 packet        MUST NOT EXECUTE AS-IS
```

## 8. Agent topology — queued

The single-agent controller remains a strong qualified baseline. Do not implement planner→executor or critic/reviewer until the provider/model basis is selected or an honest provider `NO_SELECTION` is frozen.

## 9. Runtime/orchestration — queued

Do not restart generic runtime research. E6 already qualifies LangGraph and ADR-004 qualifies the explicit controller. Reopen only on a material reversal trigger after provider/topology evidence.

## 10. C4 — parallel unchanged track

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
gate     REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

Only exact-byte recovery is authorized. No reconstruction, rescoring, substitution or downstream scientific gate advancement.

## 11. Ordered queue

```text
DONE      evidence audit
DONE      provider fact refresh
DONE      four factual gates
DONE      preregister/freeze minimum Cloudflare comparison
DONE      implement/validate/freeze provider-free Cloudflare client
DONE      audit ADR-010/011 reuse
DONE      implement/validate/freeze bounded Cloudflare executor/custody v2
NOW       design/validate/freeze separate live-execution authorization — zero inference
THEN      operator supplies required real-account evidence + secrets
THEN      execute exact <=32-attempt packet once
THEN      freeze selected candidate or honest NO_SELECTION
PARALLEL  exact C4 artifact recovery
LATER     topology comparison if still material
LATER     runtime/adaptive work only on reversal trigger/material gap
FINAL     integrate best-supported configuration + full regression + architecture freeze
```

## 12. Still forbidden

- provider inference during live-authorization design;
- credential validation via inference;
- self-invented/free-quota evidence;
- Paid Workers or prepaid AI Gateway;
- changing ADR-018 candidates/population/metrics/thresholds/budget without prospective amendment;
- changing ADR-019/020 frozen behavior after seeing future model output;
- hidden retries/fallbacks/warm-ups/provider state;
- weakening deterministic safety, `HarnessRunner` ownership or evaluator isolation;
- C4 reconstruction/rescoring;
- premature multi-agent/runtime implementation;
- final architecture or production-readiness claims before evidence supports them.
