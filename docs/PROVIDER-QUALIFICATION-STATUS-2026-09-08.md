# Provider Qualification Status — 2026-09-08

**Status:** ACTIVE provider-selection source of truth  
**Production promotion:** **NOT AUTHORIZED**  
**Current provider-selection result:** **NO_SELECTION**  
**Source baseline:** `4364364266c6a88d4affd85cb3a734c774cd42c8`  
**Frozen population:** `4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9`

This document owns the current provider-selection state. It is prospective documentation; frozen manifests, attempts, results and older progress evidence are not rewritten.

## 1. Decision boundary

The current production Release 0 provider remains provisional. None of the provider experiments executed on 2026-09-08 authorized a production provider change.

The required final sequence is:

```text
causal diagnosis
→ justified challenger(s)
→ unchanged rubric + unchanged hard gates
→ winner-only 85/85 qualification
→ Academy live E2E
→ only then consider production promotion
```

A provider/model is not promoted because it is faster, cheaper, newer or operationally available. It must satisfy the frozen functional and reliability gates.

## 2. Frozen population and hard gates

The provider work reuses the V3 frozen population:

```text
17 scenarios × 5 repetitions = 85 attempts per candidate
```

Population SHA-256:

`4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9`

Hard gates remain:

```text
identity/private-material attempts = 0
unknown-tool proposals = 0
invalid known-tool arguments = 0
schema/adapter contract failures = 0
trace provenance failures = 0
successful attempts missing usage = 0
reliability >= 93.75%
```

No failed attempt may be silently repaired, retried away or removed from the denominator.

## 3. V4 paired tournament attempt

The V4 manifest was frozen for two serving paths of the same GPT-OSS-120B weights:

- Cloudflare Workers AI — `@cf/openai/gpt-oss-120b`;
- Groq — `openai/gpt-oss-120b`.

Canonical V4 manifest:

`research/experiments/provider-tournament-v4-final-manifest.json`

Important identities from the final pre-scored protocol work:

- transport/pacing amendment: `22ef052b292bb77618973cc6447f08970dc13159`;
- pinned tournament bootstrap: `a34f1c6cce26219df6c06772ec2ea5599637e391`.

The population, rubric and hard gates did not change during the transport amendment. Zero scored attempts had been completed before it.

### Cloudflare preflight

Cloudflare GPT-OSS-120B reached the provider but returned HTTP 429 with provider error `4006` indicating the daily Workers AI allocation had been exhausted. Those calls were explicitly preflight-only and never entered the final denominator.

The user subsequently chose to continue **without Cloudflare**. Therefore there is no valid paired Cloudflare-vs-Groq final result and the repository must not describe the Groq run as a comparative provider victory.

### Groq transport preflight

The first Groq access attempt returned HTTP 403 because the provider edge rejected Python `urllib`'s default HTTP signature. Adding an explicit application `User-Agent` and `Accept: application/json` restored normal API access:

- model catalog: HTTP 200;
- `openai/gpt-oss-120b`: visible;
- chat completion: HTTP 200.

This was treated as a serving/transport normalization, not a model-quality change.

## 4. Final Groq-only qualification — COMPLETE

After Cloudflare was removed by explicit user decision, the experiment was reclassified as a **single-provider qualification**, not a tournament.

Frozen artifacts:

- manifest: `research/experiments/provider-qualification-v4-1-groq-final-manifest.json`;
- qualification runner: `1ad041fdcbe4424a79239fff6382df67e8bc2bfe`;
- pinned bootstrap: `6fc9d84262efaf6d57925a83ba59f07425cfc717`;
- candidate: `groq-gpt-oss-120b` / `openai/gpt-oss-120b`;
- 85 attempts;
- temperature `0`;
- reasoning `medium`;
- `max_completion_tokens=512`;
- no automatic retry;
- no fallback;
- no JSON repair;
- raw provider material not persisted.

### Official result

**`NO_SELECTION`**

| Metric | Result |
|---|---:|
| attempts | 85/85 |
| rubric pass | 69/85 = **81.18%** |
| reliability | 70/85 = **82.35%** |
| contract failures | **9** |
| repeat stability | 11/17 = **64.71%** |
| p50 provider latency | **1.154 s** |
| p95 provider latency | **2.904 s** |
| estimated list-price total cost | **US$ 0.04051** |

Observed hard-gate positives:

- unknown-tool proposals: 0;
- invalid known-tool argument failures: 0;
- private/identity-material attempts: 0;
- trace-integrity failures were not the limiting class.

The disqualifying classes were reliability and schema/decision-contract stability.

### Reproduced failure modes

Failures were not confined to a single scenario or repetition. They appeared across:

- `T3-15-UPSTREAM-UNAVAILABLE` — repeated invalid finish behavior;
- `T3-17-ACTION-GOVERNANCE` — invalid payload/finish behavior;
- `T3-06-ANALYSIS-DETAIL` — structural payload failures in some runs;
- `T3-11-MODEL` — structural payload failure;
- `T3-09-SPECTRUM` — structural payload failure;
- `T3-12-KNOWLEDGE-SEARCH` — structural payload failure.

Normal read selection was much stronger than the final aggregate score. The qualification therefore identifies a **structured decision / terminal stability problem**, not a general inability to choose common read tools.

## 5. Causal diagnosis

After `NO_SELECTION`, the next question became: **why is GPT-OSS/Groq failing the contract?**

Three hypotheses were isolated:

1. 512 completion tokens truncate difficult decisions;
2. best-effort structured output (`strict:false`) permits relationally invalid decision objects;
3. reasoning effort changes output length, latency and structural stability.

Diagnostic runner:

`scripts/verification/provider_failure_diagnostic_v1.py`

Diagnostic commit:

`426b0ecacf8b794199b78380a5de5837603e29e3`

Frozen bootstrap:

`7826a46d0209c1072a75b59f527dac82b3437a82`

Health-preserving isolated bootstrap:

`b71172bf1f42d4be074560336e58c42539cbfe1c`

### Planned 21-call matrix

Seven scenarios:

- `T3-01-COMPANY-CONTEXT` — clean control;
- `T3-06-ANALYSIS-DETAIL`;
- `T3-09-SPECTRUM`;
- `T3-11-MODEL`;
- `T3-12-KNOWLEDGE-SEARCH`;
- `T3-15-UPSTREAM-UNAVAILABLE`;
- `T3-17-ACTION-GOVERNANCE`.

Three configurations:

```text
B0  best-effort / medium / 512
B1  best-effort / medium / 2048
B2  best-effort / low / 2048
```

The order is rotated by scenario to reduce temporal confounding.

## 6. What the causal evidence already proves

### 512 tokens are not the sole cause

In `ANALYSIS_DETAIL`, an observed `medium/2048` call returned:

- HTTP 200;
- `finish_reason=stop`;
- syntactically valid JSON;
- hundreds of reasoning tokens;
- **Pydantic root `value_error`**.

Therefore a payload can fail the application decision contract with ample output budget and a normal provider stop. Increasing 512 → 2048 alone does not solve the structural problem.

A later isolated run also reproduced a `medium/512` `ANALYSIS_DETAIL` failure with HTTP 200, `finish_reason=stop`, JSON parsing success and root relational validation failure, while other configurations on the same scenario passed. This confirms variance in best-effort structural conformance even at temperature zero.

### Reasoning effort is material

On clean controls, `low/2048` reduced observed reasoning from hundreds of tokens to a few dozen and roughly halved provider latency in sampled calls while preserving the correct decision.

That makes `low` a legitimate challenger variable. It does **not** prove `low` is globally superior.

### Best-effort schema is strongly implicated

The existing response schema leaves generic `arguments` and `final` objects open and relies on `ProviderDecisionPayload` for relational invariants after generation. In `strict:false`, the provider can emit syntactically valid JSON that still represents an impossible controller state.

The correct response is not to weaken `ProviderDecisionPayload`; it is to investigate a stricter generated schema while keeping the deterministic application validator as a second barrier.

## 7. Strict-output design direction

The project already has canonical typed ToolSpecs and more strongly typed Release 0 structures. A strict Groq challenger must derive from these existing contracts rather than introduce an independent hand-written ontology.

Target shape:

```text
anyOf
├── TOOL::<get_current_user>
├── TOOL::<get_company>
├── TOOL::<list_assets_by_company>
├── ... one closed variant per canonical tool
├── FINAL
├── CLARIFY
├── ESCALATE
└── ABSTAIN
```

For every variant:

- `additionalProperties=false`;
- only legal fields are present;
- tool name is fixed to the variant;
- arguments use the canonical ToolSpec/OpenAPI shape;
- terminal variants cannot contain tool-only state;
- optional tool parameters are represented by closed legal variants rather than a generic open object.

The application-side `ProviderDecisionPayload`, argument validation, controller policy and safety layers remain authoritative after constrained decoding.

### `ActionRequest` blocker

The five proposal/action operations reference a supplied TRACTIAN `ActionRequest` request-body schema. The exact literal schema has **not yet been recovered** from the packed supplied-API/OpenAPI artifact during this episode. The strict action variant must not be guessed.

Until `ActionRequest` is recovered from the canonical supplied contract, strict action-schema coverage is **PENDING**.

## 8. Infrastructure and rate-limit findings

Railway project:

`academy-tractian-hosted-pilot`

Provider experiments used the disposable QA service and deliberately did not change `production-api` or `production-web`.

The account currently has five services; attempts to allocate a sixth experimental service failed due the Railway resource/service limit.

The shared `qa-live-prompt-matrix` service was repeatedly overwritten by another concurrent OpenRouter/Nemotron experiment. Partial causal matrices affected by overlapping deployments were discarded rather than merged.

A clean subsequent Groq causal attempt showed another confounder: benchmark-shaped 2048-token requests could receive HTTP 429 even when the simplified token header appeared to show available capacity. A 60-second cooldown did not consistently eliminate the rejection.

Therefore the earlier pacing formula based only on emitted `total_tokens / 8000 TPM` is **not sufficient as an admission model for this benchmark request shape**.

Current rate/admission diagnostic artifacts:

- `scripts/verification/groq_benchmark_rate_diagnostic_v2.py` — commit `8cec9f8d7e596bda27a4459ac4130319547d2f5e`;
- pinned bootstrap — commit `0ecc8365f3908f6ddc8521998436a30eee2d5507`.

At the time this document was written, this new one-shot diagnostic had been frozen but **not yet executed**, so no result is claimed.

## 9. OpenRouter side observation

A concurrent OpenRouter capacity diagnostic found the currently configured key on the free tier with published free-model daily capacity of 50 requests, below the 85 attempts required by the final population. This route is not a valid replacement for the required final 85-call qualification under the observed account tier.

No OpenRouter/Nemotron result is treated as the final provider decision in this document.

## 10. Current hypothesis ledger

| Hypothesis | Current state |
|---|---|
| 512 contributes to some finish failures | **probable** |
| 512 explains structural payload failures | **refuted as sole cause** |
| 2048 alone fixes Groq | **refuted** |
| `strict:false` contributes to invalid payloads | **strongly supported** |
| reasoning effort materially changes behavior | **confirmed** |
| `low` is superior to `medium` | **promising, not proven** |
| strict + low/2048 is the winner | **not yet authorized to claim** |
| current hard gates should be weakened | **no supporting evidence** |

## 11. Required continuation sequence

The sequence is frozen at the decision/process level:

1. execute a clean **21/21 causal matrix** in one uncontaminated experiment window;
2. recover the exact canonical `ActionRequest` schema;
3. generate `strict:true` variants from canonical ToolSpecs/OpenAPI;
4. run only small strict-schema eligibility preflights;
5. freeze only challengers justified by the causal evidence, expected candidate set:
   - B0 — best-effort / medium / 512;
   - B1 — best-effort / medium / 2048;
   - C1 — strict / medium / 2048, only if eligible/justified;
   - C2 — strict / low / 2048, only if eligible/justified;
6. evaluate challengers using the **unchanged rubrics**;
7. require the **original hard gates** without relaxation;
8. only a hard-gate winner receives a fresh **85/85** qualification;
9. only an 85/85 winner proceeds to **Academy live E2E**, causal/RMS regression, auth/tenant/persistence/SSE smoke and action-safety gate where applicable;
10. production promotion remains a separate explicit decision after those gates.

## 12. Current non-claims

Do not claim:

- a final provider winner;
- Groq superiority over Cloudflare;
- successful strict structured output before the strict preflight exists;
- that 2048 fixes the qualification failure;
- that `low` reasoning is globally better;
- that the 21/21 causal matrix has completed;
- that the benchmark-shaped Groq rate diagnostic has produced a result;
- that production is using Groq;
- that provider experiments changed the production serving topology.

The correct current provider state is: **Groq-only 85/85 completed with `NO_SELECTION`; causal serving improvements are under controlled investigation; production provider remains provisional and unchanged by this work.**
