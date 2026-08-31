# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-31 — ADR-018 minimum Cloudflare comparison preregistered/frozen  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Frozen preregistration:** [`adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md`](adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md)  
**Protocol:** [`../research/provider-model-comparison-design-v2-2026-08-31.md`](../research/provider-model-comparison-design-v2-2026-08-31.md)

This file is the short-horizon execution plan. It does not authorize provider inference, customer mutation or C4 advancement.

## 1. Completed

```text
historical evidence audit                   DONE
current USD-0 provider fact refresh         DONE
four provider pre-benchmark factual gates   DONE
material D01 benchmark gap                  DEMONSTRATED
minimum Cloudflare live candidate set       FROZEN
public population / geometry                FROZEN
M1-M10 mapping / hard gates                 FROZEN
zero-cost neuron envelope                   FROZEN
selection / NO_SELECTION semantics          FROZEN
custody / amendment rules                   FROZEN
provider/model inference calls               0
credential/account probes                    0
Cloudflare client implementation             0
```

## 2. ADR-018 frozen packet

Core candidates:

```text
C1  @cf/zai-org/glm-4.7-flash
C2  @cf/nvidia/nemotron-3-120b-a12b
```

Public population is reused unchanged:

```text
units                         8
repetitions / unit / model    2
attempts / model             16
maximum future live attempts 32
population SHA-256            561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251
```

Frozen zero-cost envelope:

```text
max prompt tokens / attempt       8000
max completion tokens / attempt    512
max packet neurons              7937.522688
Workers Free allocation        10000
headroom                        2062.477312 / 20.6248%
minimum remaining before run    9000 neurons
```

Workers Paid and prepaid AI Gateway are forbidden.

## 3. NOW — no more design changes unless CI exposes a defect

The preregistration itself is complete. Until the ADR-018 PR is merged with provider-free CI green, do not start provider implementation.

If CI exposes a defect in the preregistered bytes, fix only that defect prospectively before merge; do not change candidates, metrics, thresholds or budget for convenience.

## 4. THEN — separate provider-free Cloudflare implementation task

After the freeze is merged, the next provider task is a **separate governed implementation authorization**. Its scope may be only:

- implement the direct Cloudflare Workers AI OpenAI-compatible client needed by ADR-018;
- map the frozen `ProviderDecisionRequest` to the frozen strict `ProviderDecisionPayload` response contract;
- preserve `AgentController` and `HarnessRunner` ownership;
- enforce `temperature=0`, `max_completion_tokens=512`, no seed, no stream, no AI Gateway, no provider-side state, no provider-native execution, no repair/retry/fallback/warm-up;
- implement zero-cost/resource accounting guards required by ADR-018;
- validate all behavior provider-free with mocks/fakes only;
- preserve ADR-007 sanitized provenance and custody interfaces.

That task must still authorize:

```text
provider/model inference      0
credential/account probes     0
production provider selection NO
```

Implementation may not rewrite the ADR-018 population, candidates, thresholds or budget to fit the code.

## 5. AFTER IMPLEMENTATION — separate live-execution authorization

Only after the client passes provider-free validation may a later task decide whether all ADR-018 pre-live gates are satisfied and explicitly authorize attempt 1.

Before attempt 1 it must prove without inference:

- Workers Free account path;
- no Paid-plan or prepaid Gateway billing;
- at least 9,000 free neurons remain for the UTC day;
- exact model/route identities still match ADR-018;
- one durable custody root exists;
- write-ahead attempt claims work;
- zero retries/fallbacks/warm-ups/provider state remain true;
- production actions remain disabled.

A connected API token is only an operational prerequisite; it is not evidence and does not authorize a call.

## 6. Historical/excluded roles remain unchanged

```text
Groq GPT-OSS                 HISTORICAL_CONTROL_ONLY
Gemini 3.7 Flash Free        PUBLIC/SYNTHETIC ONLY UNDER CURRENT DATA-USE BOUNDARY
Cloudflare Gemma 4 26B       EXCLUDED FROM MINIMUM FIRST PACKET
Ollama qwen3:4b              CONDITIONAL LOCAL BASELINE / OUTSIDE CORE PACKET
old ADR-008/#44 live packet  MUST NOT EXECUTE AS-IS
```

## 7. Agent topology — queued

The single-agent controller remains a strong qualified baseline. The single-vs-multi comparative gap remains real, but do not implement planner→executor or critic/reviewer before the provider/model basis is selected or an honest provider `NO_SELECTION` is frozen.

## 8. Runtime/orchestration — queued

Do not restart runtime research. E6 already qualifies LangGraph and ADR-004 qualifies the explicit controller. Reopen only if provider/topology results or an ADR-004 reversal trigger make runtime choice materially unresolved.

## 9. C4 — parallel unchanged track

Required exact artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
```

Only exact-byte recovery is authorized. No reconstruction, rescoring, substitution or downstream scientific gate advancement.

## 10. Ordered queue

```text
DONE      evidence audit
DONE      provider fact refresh
DONE      four factual gates
DONE      preregister/freeze minimum Cloudflare comparison
NOW       merge ADR-018 only after provider-free CI is green
THEN      separate provider-free Cloudflare client implementation task
THEN      separate live-execution authorization
THEN      execute exact 32-attempt-max packet once
THEN      freeze candidate selection or honest NO_SELECTION
PARALLEL  exact C4 artifact recovery
LATER     topology comparison if still material
LATER     runtime/adaptive work only on reversal trigger/material gap
FINAL     integrate best-supported configuration + full regression + architecture freeze
```

## 11. Still forbidden

- any provider inference in ADR-018/preregistration work;
- writing the Cloudflare client before the preregistration freeze is merged;
- credential/account probing merely to inspect availability;
- executing the old ADR-008/#44 packet;
- Paid Workers or prepaid AI Gateway usage;
- changing the frozen candidates/population/metrics/thresholds/budget without a prospective amendment;
- Groq rerun for freshness;
- adding extra candidates without a material new reason;
- hidden retries/fallbacks/warm-ups/provider state;
- weakening deterministic safety, `HarnessRunner` ownership or evaluator isolation;
- C4 reconstruction/rescoring;
- premature multi-agent/runtime implementation;
- final architecture or production-readiness claims before evidence supports them.
