# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 — provider pre-benchmark factual gates closed  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Factual gate record:** [`PROVIDER-PREBENCHMARK-FACTUAL-GATES-2026-08-28.md`](PROVIDER-PREBENCHMARK-FACTUAL-GATES-2026-08-28.md)  
**Latest addendum:** [`DECISION-REVALIDATION-ADDENDUM-004-PROVIDER-PREBENCHMARK-GATES.md`](DECISION-REVALIDATION-ADDENDUM-004-PROVIDER-PREBENCHMARK-GATES.md)

This file is the short-horizon execution plan. It does not authorize provider inference, customer mutation or C4 advancement.

## 1. Completed

```text
historical evidence audit                   DONE
current USD-0 provider fact refresh         DONE
Gemini payload data-use gate                DONE
Cloudflare minimum representative selection DONE
Groq historical-vs-live-control decision    DONE
Ollama baseline spec feasibility            DONE
material D01 benchmark gap                  DEMONSTRATED
provider/model inference calls                0
```

Closed decisions:

- Gemini Free: public/synthetic evaluation only; arbitrary production payload is ineligible by default under the current unsanitized provider request/data-use boundary.
- Cloudflare minimum core: GLM 4.7 Flash + Nemotron 3 120B A12B.
- Gemma 4 26B A4B: excluded from the minimum first packet, not globally rejected.
- Groq: `HISTORICAL_CONTROL_ONLY`; no freshness rerun.
- Ollama: `qwen3:4b` is a spec-feasible local baseline; exact host performance remains unverified.

## 2. NOW — preregister the minimum provider/model comparison

A precise remaining gap exists: no repository evidence selects between the two retained current production-eligible Cloudflare models on project-specific decision quality, reliability and latency.

The next task is **planning only**: create/freeze a prospective amendment that supersedes the old ADR-008 candidate set without rewriting historical evidence.

### Core candidates

```text
C1  @cf/zai-org/glm-4.7-flash
C2  @cf/nvidia/nemotron-3-120b-a12b
```

### Conditional local baseline

`qwen3:4b` may be included only if a no-inference host inventory is completed before the packet freezes and demonstrates sufficient local storage/memory/runtime availability. Do not download or run it merely to decide the preregistration.

### Historical / excluded roles

```text
Groq GPT-OSS                 HISTORICAL_CONTROL_ONLY
Gemini 3.7 Flash Free        OUTSIDE FINAL PRODUCTION SELECTION UNDER CURRENT DATA-USE BOUNDARY
Cloudflare Gemma 4 26B       EXCLUDED FROM MINIMUM FIRST PACKET
OpenRouter generic free      EXCLUDED / uncontrolled model routing
preview/development paths    EXCLUDED FROM FINAL PRODUCTION CLAIMS
```

## 3. Reuse before inventing anything new

The prospective packet should audit/reuse the frozen provider-comparison components already in the repository:

- eight public synthetic DecisionSource probes from `provider-model-comparison-dev-population-v1.json`;
- M1–M10 definitions and hard-gate logic from ADR-008 / the frozen provider comparison design;
- ADR-006 provider-neutral `ProviderDecisionSource` contract;
- ADR-007 model-call provenance;
- ADR-010 comparison executor concepts where provider-neutral;
- ADR-011 custody/no-retry/no-fallback principles;
- EV-007/008/011 metric definitions for failure/stability/communication where applicable.

Do not copy an old candidate-specific assumption merely because infrastructure exists. Any reused artifact must be checked against the new Cloudflare routes and USD-0 boundary.

## 4. Mandatory prospective packet fields

Before the first inference request, freeze:

- exact candidate IDs/routes;
- explicit exclusions and reversal triggers;
- exact public probe population and hash/blob identity;
- exact repetitions and call ceiling;
- exact output/token ceiling per call;
- a conservative Cloudflare neuron upper-bound proving the complete packet fits inside Workers Free without paid spillover;
- model/provider conversation-state policy;
- hidden warm-up, retry and fallback count: zero;
- execution order;
- M1–M10 mapping and any prospectively justified amendment;
- quality/safety/stability/latency/resource hard gates;
- Pareto and `NO_SELECTION` semantics;
- provider-visible/private-state boundary;
- durable claim/custody/output provenance;
- regression obligations after selection.

If the free-neuron upper bound cannot prove attempt completion, do not start the run.

## 5. Inference remains forbidden until freeze

```text
provider/model inference                    NOT AUTHORIZED
credential/account probing for evidence     NOT AUTHORIZED
old ADR-008/#44 packet                       MUST NOT EXECUTE AS-IS
new comparison implementation/execution      ONLY AFTER PREREGISTRATION FREEZE
```

A connected credential is an operational prerequisite only; it is not evaluation evidence or authorization.

## 6. After provider/model comparison

Only after a provider/model basis is selected or a bounded `NO_SELECTION` is frozen:

1. revisit the single-agent vs multi-agent topology gap;
2. preregister topology comparison only if still material;
3. revisit runtime/orchestration only if provider/topology evidence or an ADR-004 reversal trigger requires it;
4. leave RAG/memory/routing/deployment/UI closed unless new measured triggers appear.

## 7. C4 — parallel unchanged track

Required exact artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
```

Only exact-byte recovery is authorized. No reconstruction, rescoring, substitution or downstream scientific gate advancement.

## 8. Ordered queue

```text
DONE      evidence audit
DONE      current provider fact refresh
DONE      four pre-benchmark factual gates
NOW       preregister/freeze minimum Cloudflare provider/model comparison
OPTIONAL  include Ollama qwen3:4b only after no-inference host inventory
PARALLEL  exact C4 artifact recovery
THEN      execute provider comparison only under frozen packet
THEN      select candidate or honest NO_SELECTION
LATER     topology comparison if still material
LATER     runtime/adaptive work only on reversal trigger/material gap
FINAL     integrate best-supported configuration + full regression + architecture freeze
```

## 9. Still forbidden

- inference before the prospective packet freezes;
- executing the old ADR-008/#44 candidate packet;
- Gemini Free for arbitrary production payload under the current provider-visible contract;
- Groq rerun for freshness;
- adding extra candidates without a material documented reason;
- hidden retries/fallbacks/warm-ups/provider state;
- paid production usage;
- weakening deterministic safety, `HarnessRunner` ownership or evaluator isolation;
- C4 reconstruction/rescoring;
- premature multi-agent/runtime implementation;
- final architecture or production-readiness claims before the evidence supports them.
