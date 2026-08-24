# ADR-001 — Provider capacity and serving path for the next prospective EXPOSED_POOL cycle

Status: `ACCEPTED`
Date: 2026-08-24
Decision state: `CONDITIONAL_GO_TO_P12_C4_PREREGISTRATION`
Live EXPOSED_POOL generation: `NOT_AUTHORIZED`

## Context

P12-C2 and P12-C3 both failed operationally before a complete prospective packet existed. P12-C2 attempted all 36 common-parent generations, completed 31 and failed 5 with `rate_limit_long_window`; its 144-output factorial packet was therefore never frozen and no scoring was allowed. P12-C3 retained the same scientific candidate definitions, introduced prospective capacity control, then reached only 3/36 completed cells before a provider rate-limit/transport event placed the experiment in a terminal state.

Both consumed experiments used Groq Free with `openai/gpt-oss-120b`, `reasoning_effort=medium`, hidden reasoning, strict JSON-schema output, temperature 0 and a maximum completion budget of 4,096 tokens. C2 also observed 10 internal retries. The current project contract deliberately requires a materially stronger provider-capacity feasibility argument before any P12-C4 preregistration.

The provider-capacity problem is therefore a hard experimental prerequisite, not a request-timing bug. P12-C1, C2 and C3 remain consumed and must not be rerun.

Canonical project evidence:

- `research/results/p12-c2-live-cycle-closure-2026-08-23.json`
- `research/results/p12-c3-live-cycle-closure-2026-08-23.json`
- `docs/CURRENT-PROJECT-STATUS.md`
- `docs/PROJECT-PLAN.md`

## Requirements affected

- `REQ-003` — reproducible technical experiment.
- `REQ-004` — documented results and trade-offs.
- `REQ-016` — inspectable calls/results.
- `REQ-017` — integrated agent and evaluation framework.
- `REQ-018` / `REQ-019` — preserve agent/gold isolation throughout provider changes.
- `KO-010` — provider failure must not break the workflow unsafely.
- `KO-011` — no development/final-evaluation leakage.
- `KO-012` — explicit architecture choices and trade-offs.
- `EV-007` — performance under failures.
- `EV-008` — repeated-run stability.

## Decision criteria

| Criterion | Measurement / importance |
|---|---|
| Complete-packet feasibility | Must be materially stronger than the C2/C3 path and support 36/36 common parents before any scoring. |
| Capacity headroom | Published TPM/TPD/RPM limits plus account-level verification before live use. |
| Scientific comparability | Prefer the same `openai/gpt-oss-120b` model family and frozen prompt/candidate definitions; characterize serving-provider confounds explicitly. |
| Zero-cost compatibility | Preferred because the consumed P12 runs were explicitly configured for zero-cost provider use. |
| API-contract compatibility | Must support seed, max completion tokens, reasoning effort/format, strict structured output and the request features used by the frozen candidate. |
| Reproducibility | Provider/model/config/version must be frozen in the P12-C4 manifest; no adaptive provider switching inside a measurement packet. |
| Operational simplicity | Must be runnable from GitHub Actions without new heavyweight infrastructure. |
| Production fit | Prefer a route that remains plausible for the final production-path demonstration, while keeping architecture unfrozen until measured. |

## Quantitative capacity boundary

The prospective geometry requires 36 provider-backed common-parent generations. At the frozen C2/C3 maximum of 4,096 completion tokens per parent, the maximum completion-token budget alone is:

```text
36 × 4,096 = 147,456 completion tokens
```

Groq Free currently documents 200,000 tokens/day and 8,000 tokens/minute for `openai/gpt-oss-120b`. Therefore the worst-case completion budget alone can consume 73.7% of the published daily allowance, leaving only 52,544 tokens for all input tokens, retries and other organization usage. This is consistent with the observed C2 failure mode and gives insufficient safety margin for a one-shot confirmatory packet.

Cerebras Free currently documents 1,000,000 tokens/day, 1,000,000 tokens/hour and 64,000 tokens/minute for `gpt-oss-120b`. Relative to the same 147,456-token maximum completion budget, this leaves 852,544 daily tokens for inputs and operational variance before considering other account usage. The published daily headroom is 5× Groq Free and the published TPM headroom is 8×.

These calculations are feasibility bounds, not a claim about actual token consumption. Exact account-level limits and a pre-live request-budget estimate remain mandatory because provider documentation notes that organization-specific limits can differ.

## Alternatives considered

### Option A — Groq Free, same model/config

**Evidence**

- Published Free limit for `openai/gpt-oss-120b`: 8K TPM, 200K TPD, 30 RPM, 1K RPD.
- P12-C2: 31/36 successful common parents, 5 `rate_limit_long_window` failures, 10 internal retries.
- P12-C3: 3/36 completed before terminal provider-capacity failure later the same day.

**Advantages**

- Lowest serving-path confound relative to C1/C2/C3.
- Zero cost.
- Existing runner integration already proven.

**Risks / costs**

- The exact capacity boundary already failed twice under prospective execution.
- More delay/retry logic does not remove the 200K daily ceiling.
- A new cycle on the same capacity contract would violate the project stop rule unless the account quota itself changes materially.

**Decision:** `REJECTED` for P12-C4 under the current Free quota.

### Option B — Groq Developer or verified higher Groq quota

**Evidence**

- Groq documents a Developer baseline of 250K TPM and 1K RPM for `openai/gpt-oss-120b`, with higher limits available for some workloads.
- The same model endpoint and provider would minimize the serving-path change.

**Advantages**

- Lowest scientific confound among capacity-changing options.
- Existing integration and request semantics remain closest to the consumed experiments.
- Stronger throughput boundary than Free.

**Risks / costs**

- Requires a payment method/pay-as-you-go or separately verified quota.
- Exact organization-level limits must still be captured before preregistration.
- Violates the current zero-cost operational preference unless explicitly authorized.

**Decision:** `PARETO_BACKUP`. Prefer this route if paid capacity becomes authorized and the exact quota is demonstrably sufficient before P12-C4 freezes.

### Option C — Cerebras Free, same OpenAI GPT-OSS 120B weights/model family

**Evidence**

- Cerebras publishes `gpt-oss-120b` with Hugging Face id `openai/gpt-oss-120b`.
- Free limits: 64K TPM, 1M TPH, 1M TPD, 30 RPM, 14.4K RPD.
- The public model contract advertises structured outputs, tools, reasoning, `seed` and `max_completion_tokens` support.
- Current docs support `reasoning_effort` for GPT-OSS, including `medium`, `reasoning_format`, including `hidden`, and strict JSON Schema structured outputs.

**Advantages**

- Preserves the underlying GPT-OSS 120B model family while changing the serving provider rather than the candidate logic.
- 5× published daily token headroom and 8× published TPM headroom versus Groq Free.
- Zero-cost path remains available.
- No new persistent serving infrastructure is required.

**Risks / costs**

- Provider implementation/quantization and OpenAI-compatible transport can change numerical behavior even with the same underlying model family.
- Provider API/version semantics must be qualified before benchmark generation.
- Published limits are not a substitute for checking the actual account limits.

**Decision:** `SELECTED_CONDITIONAL_GO`.

### Option D — Dedicated endpoint for the same open-weight model

Together documents dedicated endpoints as reserved hardware with predictable performance and no shared-fleet rate limits; a single H100 80GB endpoint is published at $3.99/hour. The OpenAI GPT-OSS release states that GPT-OSS 120B fits on a single 80GB GPU.

**Advantages**

- Strongest hard-capacity argument among evaluated routes.
- Removes shared-fleet rate-limit uncertainty.
- Same open-weight model can be retained.

**Risks / costs**

- Paid infrastructure and additional provisioning/operational complexity.
- Serving stack still changes relative to Groq.
- Unnecessary for the next cycle if the zero-cost Cerebras path passes all pre-live gates.

**Decision:** `PARETO_BACKUP` for a capacity-guaranteed paid path.

### Option E — Local/self-hosted GPT-OSS 120B

OpenAI documents that the MXFP4 model can fit on one 80GB GPU.

**Advantages**

- Full capacity/control and no third-party request quota.
- Open weights preserve model identity and improve long-term reproducibility.

**Risks / costs**

- No 80GB GPU availability or end-to-end throughput evidence has been established for this project.
- Provisioning a new serving stack now adds schedule and operations risk.
- Local quantization/runtime choices introduce their own serving confounds.

**Decision:** `REJECTED_FOR_CURRENT_SCHEDULE`; revisit only with already-available hardware and measured throughput.

### Option F — Alternative model/provider

Changing the model as well as the provider could increase capacity but creates a larger scientific confound than a same-model serving-path change.

**Decision:** `DEFERRED`. Do not introduce a new model while a same-model, materially higher-capacity path remains credible.

## Pareto frontier

| Route | Cost | Capacity confidence | Scientific continuity | Operational burden | Frontier role |
|---|---:|---|---|---|---|
| Cerebras Free / GPT-OSS 120B | $0 under Free tier | High enough on published limits, account verification pending | Medium-high; same model family, different serving stack | Low | **Selected zero-cost frontier** |
| Groq Developer / GPT-OSS 120B | Pay-as-you-go | High if exact org quota verifies | **Highest** among changed-capacity routes | Low | Scientific-continuity backup |
| Dedicated same-model endpoint | Paid per provisioned hardware | **Highest**; reserved hardware | Medium-high; serving stack changes | Medium-high | Capacity-guarantee backup |

Groq Free is dominated for the current experiment because it preserves continuity but has already demonstrated inadequate capacity. Local/self-hosted is dominated on schedule because no hardware/throughput evidence is currently available.

## Decision

Select **Cerebras Free + `gpt-oss-120b`** as the capacity path for **P12-C4 preregistration and provider compatibility qualification**, while keeping the candidate definitions, prompt policy, evaluator, seeds policy and complete-packet requirement prospectively controlled.

This ADR returns **GO for drafting/freezing P12-C4**, but it does **not** authorize live EXPOSED_POOL generation. The serving-path change must be treated as an explicit experimental confound; C4 results may be compared internally across its preregistered arms, while cross-cycle claims against C1/C2/C3 must distinguish candidate effects from serving-provider effects.

No automatic failover is allowed inside a C4 packet. One provider/model/config must be frozen for the complete prospective packet.

## Mandatory pre-live gates for P12-C4

Before the first EXPOSED_POOL provider call:

1. freeze fresh seeds and prove no C2/C3 partial-parent reuse;
2. freeze the exact Cerebras model id, API version/endpoint, decoding/reasoning settings and request schema;
3. verify actual account limits are at least the feasibility values used by this ADR or recompute the capacity decision;
4. run a **non-benchmark synthetic compatibility probe** that contains no EXPOSED_POOL, private-oracle, FRESH_BLIND or LEGACY_LOCKED_TEST outcome information;
5. prove support for the exact frozen request features used by C4: deterministic seed binding, `max_completion_tokens`, reasoning effort/format, strict JSON Schema and required tool semantics;
6. provider-free activation and all benchmark-integrity isolation checks must PASS;
7. freeze complete-packet/missingness/failure semantics before any benchmark outcome exists;
8. capture provider rate-limit/usage metadata in sanitized operational telemetry without exposing raw benchmark outputs publicly;
9. keep private-oracle, FRESH_BLIND and LEGACY_LOCKED_TEST accesses at zero during generation.

A synthetic provider compatibility probe is infrastructure qualification only. It cannot be used for candidate selection, scoring or claims about P12 quality.

## Consequences

- **Positive:** materially larger documented zero-cost capacity boundary without changing the underlying GPT-OSS model family.
- **Negative:** a provider/serving-stack confound is introduced and must be explicit in all cross-cycle interpretation.
- **Operational:** a Cerebras adapter/compatibility gate and `CEREBRAS_API_KEY` secret will be required before live qualification; Groq Free must not be used as silent fallback.
- **Evaluation impact:** P12-C4 remains a new prospective generation. C2/C3 data are not reused, no partial scoring is allowed, and deterministic/semantic/blind gates remain unchanged in order.
- **Architecture:** this does not freeze Cerebras as the final production provider. Production-fit selection remains a separate evidence track.

## Reversal triggers

Reopen this ADR before any P12-C4 live generation if any of the following occurs:

- the actual Cerebras account exposes materially lower limits than 64K TPM / 1M TPD for `gpt-oss-120b`;
- the synthetic compatibility probe cannot reproduce required request semantics without changing the scientific candidate definition;
- strict JSON Schema, seed, tool or reasoning behavior requires a candidate-visible workaround;
- request-size/context measurements show the full 36-parent packet lacks a defensible capacity margin;
- the provider/model/version changes before the live manifest is frozen;
- paid Groq capacity becomes authorized and exact limits demonstrate a sufficient packet margin, making the lower-confound route preferable;
- a dedicated same-model endpoint becomes available at acceptable cost and schedule risk;
- production-fit evidence later disqualifies Cerebras for the final architecture.

If the selected path fails a pre-live gate, do not consume P12-C4. Reopen the ADR and choose another prospectively qualified route.

## Sources

Official/current provider and model documentation reviewed 2026-08-24:

- Groq rate limits: https://console.groq.com/docs/rate-limits
- Groq supported models / Developer limits: https://console.groq.com/docs/models
- Groq GPT-OSS 120B model page: https://console.groq.com/docs/model/openai/gpt-oss-120b
- Cerebras rate limits: https://inference-docs.cerebras.ai/support/rate-limits
- Cerebras public model contract: https://inference-docs.cerebras.ai/api-reference/models/public-models
- Cerebras reasoning: https://inference-docs.cerebras.ai/capabilities/reasoning
- Cerebras structured outputs: https://inference-docs.cerebras.ai/capabilities/structured-outputs
- Together dedicated endpoints: https://docs.together.ai/docs/dedicated-endpoints/overview
- OpenAI GPT-OSS release/model sizing: https://openai.com/index/introducing-gpt-oss/
