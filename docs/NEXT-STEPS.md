# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-31 — ADR-019 Cloudflare provider-free client implementation frozen  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Frozen preregistration:** [`adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md`](adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md)  
**Frozen provider-free client:** [`adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md`](adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md)

This file is the short-horizon execution plan. It does not authorize provider inference, credential probing, customer mutation or C4 advancement.

## 1. Completed

```text
historical evidence audit                     DONE
current USD-0 provider fact refresh           DONE
four provider pre-benchmark factual gates     DONE
material D01 benchmark gap                    DEMONSTRATED
minimum Cloudflare comparison preregistration FROZEN / ADR-018
provider-free Cloudflare client               IMPLEMENTED + FROZEN / ADR-019
provider-free client/regression CI            PASS
provider/model inference calls                0
credential/account probes                     0
live network validation                       0
comparison attempts consumed                  0 / 32
```

Frozen core models remain:

```text
@cf/zai-org/glm-4.7-flash
@cf/nvidia/nemotron-3-120b-a12b
```

ADR-018 population, metrics, selection and zero-cost envelope remain unchanged.

## 2. NOW — audit existing live-execution evidence before creating anything new

Permanent evidence-first rule applies again.

Do **not** immediately create a new Cloudflare executor, custody system or live wrapper. First audit the repository's existing ADR-010/ADR-011 execution/custody machinery and associated code/tests/results against ADR-018/ADR-019.

The audit question is:

> Which existing live-comparison components already answer the Cloudflare execution need, which require only a bounded adapter, and which contain OpenAI/Gemini-specific assumptions that create a real material gap?

## 3. Mandatory audit inventory

For every relevant component, record exact file/blob/evidence identity, what it proves, what it does not prove and one of:

```text
REUSE_UNCHANGED
REUSE_WITH_BOUNDED_ADAPTER
INCOMPATIBLE_HISTORICAL_ASSUMPTION
MISSING_MATERIAL_CAPABILITY
```

Audit at least:

1. ADR-010 comparison executor and plan generation;
2. ADR-011 governed live task/custody wrapper;
3. write-ahead attempt ledger and `CLAIMED`/uncertain-attempt behavior;
4. deterministic 8 × 2 × 2 execution order;
5. operational failures remaining in denominators;
6. M1–M10 aggregation and threshold logic;
7. Pareto / `NO_SELECTION` implementation;
8. ADR-007 model-call provenance generation/validation;
9. provider/client injection interfaces;
10. secret names/account prerequisites;
11. route/model verification assumptions;
12. fixed OpenAI/Gemini candidate assumptions;
13. M8 generic token/cost accounting versus ADR-018 Cloudflare neuron accounting;
14. pre-attempt free-tier and >=9,000-neuron proof;
15. durable custody-root identity and final sanitized result freeze;
16. no retry/fallback/warm-up/parallel/provider-state guarantees.

Search existing code, tests, frozen artifacts and historical failures before classifying a gap.

## 4. Audit outcomes

If all required live-execution machinery is reusable unchanged or with bounded Cloudflare injection:

- do not rewrite it;
- document exact reuse;
- authorize only the minimum adapter/configuration work still missing.

If material incompatibilities exist:

- document the specific assumption/gap;
- preregister the minimal implementation amendment needed;
- preserve all historical ADR-010/011 bytes/evidence;
- do not broaden scope beyond the demonstrated gap.

If evidence is already sufficient and no new implementation is needed, proceed directly to the **separate live-execution authorization design**, still without inference.

## 5. Live inference remains forbidden

Current authorization remains:

```text
provider/model inference       NOT AUTHORIZED
credential/account probes      NOT AUTHORIZED FOR EVIDENCE
live network validation        NOT AUTHORIZED
comparison execution           NOT AUTHORIZED
production provider selection  NO
production actions              DISABLED
```

The Cloudflare client being implemented/frozen does not authorize a call.

## 6. What a later live authorization must prove

Only after the execution/custody audit and any minimum provider-free gaps are closed may a separate live task freeze the final pre-attempt conditions.

Before attempt 1 it must prove without inference:

- exact ADR-018 and ADR-019 frozen identities;
- Workers Free path only;
- Workers Paid not used;
- prepaid AI Gateway not used;
- at least 9,000 free neurons remain for the current UTC day;
- exact GLM/Nemotron model IDs and direct route;
- one durable custody root;
- write-ahead claim semantics before network invocation;
- no replay of `CLAIMED`/uncertain attempts;
- zero retry/fallback/warm-up/parallel/provider-state behavior;
- production actions remain disabled;
- secrets cannot enter persisted/sanitized evidence;
- maximum 32 live attempts and frozen per-attempt bounds remain enforceable.

Only that later authorization may make attempt 1 admissible.

## 7. Historical/excluded roles remain unchanged

```text
Groq GPT-OSS                 HISTORICAL_CONTROL_ONLY
Gemini 3.7 Flash Free        PUBLIC/SYNTHETIC ONLY UNDER CURRENT DATA-USE BOUNDARY
Cloudflare Gemma 4 26B       EXCLUDED FROM MINIMUM FIRST PACKET
Ollama qwen3:4b              CONDITIONAL LOCAL BASELINE / OUTSIDE CORE PACKET
old ADR-008/#44 live packet  MUST NOT EXECUTE AS-IS
```

## 8. Agent topology — queued

The single-agent controller remains a strong qualified baseline. The single-vs-multi comparative gap remains real, but do not implement planner→executor or critic/reviewer before the provider/model basis is selected or an honest provider `NO_SELECTION` is frozen.

## 9. Runtime/orchestration — queued

Do not restart generic runtime research. E6 already qualifies LangGraph and ADR-004 qualifies the explicit controller. Reopen only if provider/topology results or an ADR-004 reversal trigger make runtime choice materially unresolved.

## 10. C4 — parallel unchanged track

Required exact artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
```

Only exact-byte recovery is authorized. No reconstruction, rescoring, substitution or downstream scientific gate advancement.

## 11. Ordered queue

```text
DONE      evidence audit
DONE      provider fact refresh
DONE      four factual gates
DONE      preregister/freeze minimum Cloudflare comparison
DONE      implement/validate/freeze provider-free Cloudflare client
NOW       audit ADR-010/011 + code/tests/custody for Cloudflare reuse
THEN      close only demonstrated provider-free execution gaps, if any
THEN      separate live-execution authorization design/freeze
THEN      execute exact 32-attempt-max packet once
THEN      freeze candidate selection or honest NO_SELECTION
PARALLEL  exact C4 artifact recovery
LATER     topology comparison if still material
LATER     runtime/adaptive work only on reversal trigger/material gap
FINAL     integrate best-supported configuration + full regression + architecture freeze
```

## 12. Still forbidden

- provider inference before separate live authorization;
- credential/account probing merely to prove availability;
- inventing/replacing executor/custody machinery before the historical evidence audit;
- executing the old ADR-008/#44 OpenAI/Gemini packet;
- Paid Workers or prepaid AI Gateway;
- changing ADR-018 candidate/population/metrics/thresholds/budget without prospective amendment;
- changing ADR-019 frozen client semantics to fit future outputs post hoc;
- Groq rerun for freshness;
- hidden retries/fallbacks/warm-ups/provider state;
- weakening deterministic safety, `HarnessRunner` ownership or evaluator isolation;
- C4 reconstruction/rescoring;
- premature multi-agent/runtime implementation;
- final architecture or production-readiness claims before evidence supports them.
