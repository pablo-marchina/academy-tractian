# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 — post zero-cost provider/model fact refresh  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Provider fact refresh:** [`PROVIDER-ZERO-COST-FACT-REFRESH-2026-08-28.md`](PROVIDER-ZERO-COST-FACT-REFRESH-2026-08-28.md)  
**Provider refresh addendum:** [`DECISION-REVALIDATION-ADDENDUM-003-ZERO-COST-PROVIDER-FACT-REFRESH.md`](DECISION-REVALIDATION-ADDENDUM-003-ZERO-COST-PROVIDER-FACT-REFRESH.md)  
**Evidence-first gate:** [`EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md`](EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md)

This file is the short-horizon execution plan. It authorizes no scientific gate, provider call, credential probe, real-customer mutation or new experiment by itself.

## 1. Completed

```text
repository historical evidence audit      DONE
20-decision material matrix               DONE
current first-party USD-0 provider refresh DONE
provider/model inference calls              0
credential/account probes                   0
new provider benchmark authorized           NO
```

Broad provider discovery is no longer the next task. The feasible set is narrow enough to make the remaining pre-experiment decisions explicit.

## 2. NOW — close provider eligibility/selection facts without inference

### 2.1 Gemini Free Tier data-use gate

Current technical state:

```text
model                                  gemini-3.7-flash
lifecycle                              GA / stable
Free Tier input/output                 free
function calling                      supported
structured outputs                    supported
provider call authorization           NO
```

Current first-party pricing states that Free Tier content is used to improve Google products. Before carrying Gemini into a live prospective packet, determine whether the **exact intended payload** can be sent under that policy without violating project/customer/privacy expectations.

This is a policy/data-classification decision, not an inference experiment. Do not test Gemini merely to decide whether its terms are acceptable.

### 2.2 Select minimum Cloudflare representative set

Workers AI Free is currently eligible under the USD-0 boundary. The refresh identified three materially different current model/capacity points:

| Candidate | Context | Neuron input/output cost | Role to screen |
|---|---:|---:|---|
| `@cf/zai-org/glm-4.7-flash` | 131k | 5,500 / 36,400 per M | lowest-neuron-cost agentic point |
| `@cf/google/gemma-4-26b-a4b-it` | 256k | 9,091 / 27,273 per M | larger context / different model family |
| `@cf/nvidia/nemotron-3-120b-a12b` | 256k | 45,455 / 136,364 per M | much heavier model/capacity point |

Do **not** automatically include all three. Use current documented capabilities and the intended call budget to choose the smallest set that represents a genuinely distinct expected quality/capacity trade-off.

No inference is authorized during this selection.

### 2.3 Decide Groq's role

Groq Free stays in the feasible set only with historical evidence attached.

```text
E8 operational evidence             preserved
E14 GPT-OSS negative quality        preserved
P12-C2/C3 capacity failures         preserved
Qwen 3.8 Preview                    excluded from final production claims
```

Decide prospectively whether GPT-OSS/Groq should be:

- `HISTORICAL_CONTROL_ONLY`, with no new live call; or
- one `LIVE_CONTROL` in a minimum future packet because a controlled contemporaneous baseline remains scientifically necessary.

The decision must explicitly explain why old evidence is or is not sufficient; a rerun for freshness alone is forbidden.

### 2.4 Optional local baseline factual feasibility

Ollama is a valid zero-external-charge baseline, but do not execute a model yet. First determine from hardware/model metadata whether a realistically runnable tool/structured-output model exists for the available environment.

If no realistic model fits, exclude local execution prospectively with that factual reason. If one fits, it becomes a candidate for the **future preregistration**, not immediate execution.

## 3. DECIDE — is a live provider comparison still necessary?

Only after Section 2 is complete, classify D01 again.

A new live provider comparison is justified only if the remaining eligible set contains two or more materially credible candidates for which the repository lacks the exact quality/reliability/latency evidence needed to select a production Pareto point.

If existing evidence plus current facts is sufficient, select without a redundant experiment and document the bounded claim.

If a gap remains, create the **minimum** prospective provider packet. It must preregister before attempt 1:

- exact provider/model IDs and routes;
- exact candidate inclusion/exclusion rationale;
- exact case/probe population;
- fixed controller/ToolSpecs/HarnessRunner/evaluator basis;
- call budget and repetition geometry;
- quality, decision, evidence, safety, stability, latency, quota/token and zero-cost metrics;
- no hidden retry/fallback/warm-up/provider-conversation state;
- fail-closed zero-cost containment;
- hard gates and Pareto/tie-break semantics;
- provider-visible/private-state boundaries;
- exact output/provenance custody.

Until that packet exists and is frozen:

```text
provider/model inference calls       NOT AUTHORIZED
credential/account probes            NOT AUTHORIZED FOR EVIDENCE
old ADR-008/#44 execution            FORBIDDEN AS-IS
```

## 4. Agent topology — remain queued

Current single-agent controller remains a strong qualified baseline. The single-vs-multi comparative gap is real, but do not implement planner→executor or critic/reviewer before provider/model control exists and topology remains material.

Any future topology experiment must hold provider/model, cases, ToolSpecs, HarnessRunner, authorization and evaluators constant enough to isolate topology.

## 5. Runtime/orchestration — remain queued

Do not restart runtime research. E6 already qualifies LangGraph and ADR-004 qualifies the explicit controller. Reopen only if provider/topology resolution or an ADR-004 reversal trigger makes runtime orchestration materially unresolved.

## 6. Decisions closed to new experiments in the current scope

No new experiment absent a reversal trigger for:

- Groq/GPT-OSS reasoning-budget/response-format tuning family;
- native ToolSpec vs MCP adapter;
- evidence-sufficiency stopping;
- RAG/vector DB/reranking;
- persistent memory;
- deterministic safety/authorization/action custody;
- provider-free failure/stability/communication campaigns;
- deterministic operational evaluator stack;
- normalized RunTrace observability;
- hosted deployment;
- richer UI.

## 7. C4 — exact recovery in parallel

Scientific gate remains:

`REQUIRED_PER_GROUP_AND_SLICE_REPORTING`

Required artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
```

Authorized: search/recover the exact bytes and verify hash/size/geometry.

Not authorized: reconstruction, rescoring, substitution, semantic evaluation, FRESH_BLIND, LEGACY_LOCKED_TEST or downstream preferred/survivor inference.

## 8. Ordered queue

```text
DONE      historical evidence audit
DONE      current primary-source provider/model fact refresh
NOW       resolve Gemini Free Tier data-use gate
NOW       choose minimum Cloudflare representative set using facts only
NOW       decide Groq historical-only vs live-control role
OPTIONAL  no-inference Ollama hardware/model feasibility
DECIDE    whether D01 still requires a minimum live provider comparison
IF YES    preregister/freeze minimum packet before any inference
PARALLEL  exact C4 artifact recovery
LATER     topology comparison only after controlled provider/model basis
LATER     runtime/adaptive work only if still material
FINAL     integrate best-supported configuration + full regression + evidence-honest architecture freeze
```

## 9. Development authorization checklist

Before a new provider experiment:

- [ ] exact material gap remains after historical evidence + current fact reconciliation;
- [ ] Gemini data-use eligibility is resolved if Gemini is included;
- [ ] candidate set is minimal and each inclusion/exclusion is documented;
- [ ] no preview/development-only path is used for a final production claim;
- [ ] any OpenRouter route is fixed/pinned and uncontrolled fallback is disallowed;
- [ ] Groq negative historical evidence is incorporated rather than reset;
- [ ] local candidate is hardware-feasible if included;
- [ ] USD-0 containment is fail-closed;
- [ ] exact population, metrics, hard gates, repetitions and custody are preregistered;
- [ ] no hidden retries/fallbacks/warm-ups/provider state exist;
- [ ] regression/reversal obligations are explicit.

If any applicable item is false, remain in planning/factual work.

## 10. Still forbidden

- executing ADR-008/#44 as currently frozen;
- inference calls merely to inspect availability before a prospective packet;
- treating a connected API key as evaluation evidence or authorization;
- paid provider/service production usage;
- credential/account probing merely to confirm connection state;
- redundant reruns of historical negative/failed experiments;
- multi-agent implementation before topology preregistration and controlled basis;
- RAG/memory/routing/deployment/UI experiments without a new material trigger;
- reconstructing/rescoring/substituting C4 without a separately authorized scientific amendment;
- weakening `HarnessRunner`/authorization/idempotency/private-truth boundaries;
- claiming provider selection, C4 completion, global architecture freeze or unconditional production readiness before evidence supports them.
