# ADR-018 — Minimum USD-0 Cloudflare provider/model comparison preregistration

**Status:** ACCEPTED  
**Decision state:** `FROZEN_PREREGISTRATION / LIVE_NOT_AUTHORIZED`  
**Date:** 2026-08-31  
**Issue:** #68  
**Scientific state changed:** NO  
**Provider/model calls authorized by this ADR:** 0  
**Credential/account probes authorized:** 0  
**Cloudflare client implementation authorized:** 0  
**Production provider/model selected:** NO  
**Production actions enabled:** NO

## 1. Decision question

What exact minimum prospective comparison should govern the next production provider/model decision under the repository-wide evidence-first and USD-0 constraints, after the historical evidence audit and provider factual gates demonstrated a remaining project-specific gap between the retained current Cloudflare Workers AI Free candidates?

## 2. Decision

Freeze the exact provider-free preregistration represented by these already-materialized bytes:

| Artifact | Frozen Git blob |
|---|---|
| machine-readable design | `research/experiments/provider-model-comparison-design-manifest-v2.json` — `f70837fca46fa8ecf1e63b33ea41dec73fc051e3` |
| human-readable protocol | `research/provider-model-comparison-design-v2-2026-08-31.md` — `badb3d86853ab8ec44e596f39f1ff633c30b41a6` |
| provider-free validator | `scripts/research/validate_provider_model_comparison_design_v2.py` — `601400eeadc0f3340c1da6ca8594cb3d7f6278da` |
| reused public population | `research/experiments/provider-model-comparison-dev-population-v1.json` — SHA-256 `561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251` |

The manifest remains internally labelled `DESIGN_CANDIDATE_PROVIDER_FREE_ONLY`; this ADR is the authority that promotes those exact bytes to the scoped frozen preregistration state after provider-free CI validation. The design bytes must not be rewritten merely to change their status label.

## 3. Prospective relationship to ADR-008 through ADR-011

ADR-008 through ADR-011 remain immutable historical evidence. Their OpenAI/Gemini live candidate packet consumed `0/32` calls and is not executable under the current USD-0 hard constraint.

ADR-018 prospectively supersedes only the future provider-comparison candidate/resource design:

- old live candidates are replaced by the current minimum Cloudflare set;
- M8 is specialized from generic monetary cost to exact zero-cash + neuron accounting;
- the old 32-call geometry, public population, M1-M7/M9/M10 concepts, hard-gate philosophy, provenance, custody and `NO_SELECTION` semantics are retained where still valid.

No historical result is erased, rescored or reinterpreted as if it came from the new candidates.

## 4. Frozen live candidate set

Exactly two production-selection-eligible live candidates are preregistered:

1. `cloudflare_glm_4_7_flash_workers_free`
   - model: `@cf/zai-org/glm-4.7-flash`;
   - direct Workers AI OpenAI-compatible Chat Completions route;
   - 131,072 context;
   - current neuron rates: 5,500/M input, 36,400/M output.

2. `cloudflare_nemotron_3_120b_a12b_workers_free`
   - model: `@cf/nvidia/nemotron-3-120b-a12b`;
   - same direct route;
   - 256,000 context;
   - current neuron rates: 45,455/M input, 136,364/M output.

The provider-free scripted/null baseline remains ineligible for production selection.

Excluded/non-live roles are frozen prospectively:

- Cloudflare Gemma 4 26B A4B — excluded from the **minimum first packet**, not globally rejected;
- Groq GPT-OSS — historical control only; no freshness rerun;
- Gemini 3.7 Flash Free — public/synthetic evaluation eligible but not a final arbitrary-production-payload candidate under the current data-use boundary;
- Ollama `qwen3:4b` — conditional local baseline outside the core packet.

## 5. Frozen public population

Reuse without mutation:

`research/experiments/provider-model-comparison-dev-population-v1.json`

SHA-256:

`561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251`

The 8 units are public/synthetic DEV-only and use no private oracle, validation, locked-test, fresh-blind or historical private task-quality truth.

## 6. Frozen execution geometry

```text
live candidates                     2
public units                        8
repetitions / unit / candidate      2
attempts / candidate               16
max live attempts                  32
warm-ups                            0
automatic retries                   0
fallbacks                           0
parallel calls                      0
provider seed                       none
```

Order is deterministic and balanced exactly as defined in the manifest. Operational failures remain in all applicable denominators.

## 7. Frozen request boundary

Both candidates must use the direct Workers AI OpenAI-compatible Chat Completions endpoint, not AI Gateway.

Frozen controls:

```text
stream                        false
n                             1
temperature                   0
max_completion_tokens         512
provider seed                 none
provider-native tool execution disabled
provider conversation state   disabled
AI Gateway                    disabled
built-in web search           disabled
store                         false
response format               strict ProviderDecisionPayload JSON Schema
automatic repair              disabled
```

The provider remains a decision source only. `AgentController` owns orchestration and `HarnessRunner.execute_tool()` remains the exclusive real execution boundary.

If provider-free implementation later proves any frozen request field incompatible with either exact route, inference remains blocked and this ADR must be amended prospectively; implementation cannot silently change the design.

## 8. Frozen USD-0 resource envelope

Cloudflare's current Workers Free allocation is 10,000 neurons/day. This preregistration requires Workers Free and forbids Workers Paid and prepaid AI Gateway billing.

Per-attempt ceilings:

```text
prompt/input tokens       <= 8,000
completion/output tokens  <=   512
```

Frozen worst-case calculation:

```text
GLM max / attempt             62.636800 neurons
GLM 16 attempts             1002.188800 neurons
Nemotron max / attempt       433.458368 neurons
Nemotron 16 attempts        6935.333888 neurons
------------------------------------------------
max complete packet         7937.522688 neurons
Workers Free allocation    10000.000000 neurons
headroom                    2062.477312 neurons
headroom                         20.6248%
```

A later live authorization must prove without inference that at least 9,000 free neurons remain for the current UTC day before attempt 1. If live authoritative usage exceeds the frozen input/output ceilings, or cumulative observed usage plus worst-case remaining attempts can exceed the available free allocation, execution stops before the next call and the packet becomes incomplete/`NO_SELECTION`.

Any Paid-plan, prepaid-credit or billable execution is disqualifying.

## 9. Metrics and hard gates

M1-M7, M9 and M10 retain the ADR-008 definitions/thresholds because the provider-neutral contract and public population are unchanged.

M8 is prospectively specialized to:

- actual cash cost = exactly USD 0;
- exact neurons derived from provider-reported prompt/completion usage using frozen model rates;
- total observed neurons as the resource Pareto axis;
- no imputation when exact usage is missing.

Hard gates include the historical leakage/action/provenance/ownership/raw-recording/route-change gates plus:

- no paid or non-free route;
- complete resource accounting;
- packet remains inside the frozen free allocation envelope.

## 10. Selection semantics

The deterministic rule is frozen in the manifest:

- threshold/hard-gate failures disqualify;
- `NO_SELECTION` is valid if no candidate survives;
- otherwise compare Pareto non-dominance over M4/M7 maximize and M6 p95/M8 neurons minimize;
- M4 lead, neuron use and latency tie-breaks are applied only in the frozen order;
- any unresolved tie, incomplete accounting, incomplete packet or protocol uncertainty yields `NO_SELECTION`;
- weighted global scores and post-result threshold tuning are forbidden.

## 11. Custody and attempt identity

A later live task must preserve the existing governed custody principles:

- one durable custody root;
- write-ahead claim before every network-capable attempt;
- no automatic replay of claimed/uncertain attempts;
- sanitized persisted result/provenance only;
- no persisted provider secrets, raw requests, raw responses or exception text;
- valid ADR-007 provenance for every attempted live invocation.

## 12. Validation requirement

Before merge/freeze is accepted, the branch must pass:

- `provider-model-comparison-design-v2` provider-free validator and regression tests;
- existing repository regression workflows required by the final handoff/reproduction boundary.

CI validation itself must run with provider/account credential environment variables absent and executes zero model calls.

## 13. Non-authorization

ADR-018 does **not** authorize:

- Cloudflare client/runtime implementation;
- Cloudflare credential/account probing;
- any provider/model inference request;
- execution of issue #44;
- provider selection;
- production action enablement;
- semantic judge work;
- C4 reconstruction/rescoring;
- FRESH_BLIND or LEGACY_LOCKED_TEST access;
- topology/runtime experiments;
- global architecture freeze or production-readiness claims.

## 14. Next admissible step

After this exact preregistration is merged and all provider-free CI is green, a **separate governed implementation task** may implement the minimal Cloudflare client/adapter required to satisfy these frozen bytes and validate it provider-free.

That implementation task still authorizes zero inference. A further explicit live-execution authorization is required before attempt 1.

## 15. Reversal triggers

Reopen prospectively before attempt 1 if:

- either exact Cloudflare model changes lifecycle or loses Workers Free availability;
- official neuron rates/free allocation materially change;
- the direct OpenAI-compatible route loses required JSON-schema semantics;
- provider-free implementation cannot satisfy the frozen request contract without repair/fallback;
- the public population is shown to contain a material defect;
- a newly evidenced requirement makes an excluded candidate materially distinct;
- the 7,937.522688-neuron complete-packet upper bound is no longer valid;
- any other repository hard constraint changes materially.

Historical ADRs remain unchanged even if ADR-018 is later superseded.
