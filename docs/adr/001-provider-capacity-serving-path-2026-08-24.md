# ADR-001 — Provider capacity and serving path for the next prospective EXPOSED_POOL cycle

Status: `ACCEPTED`
Date: 2026-08-24
Decision state: `CONDITIONAL_GO_TO_P12_C4_PREREGISTRATION`
Live EXPOSED_POOL generation: `NOT_AUTHORIZED`

## Context

P12-C2 and P12-C3 were consumed before a complete prospective packet existed. C2 completed 31/36 common parents and failed 5 with `rate_limit_long_window`; C3 completed 3/36 before a terminal provider rate-limit/transport failure. Neither packet was scored. P12-C1/C2/C3 remain consumed and must not be rerun.

The consumed runs used Groq Free with `openai/gpt-oss-120b`, `temperature=0`, `reasoning_effort=medium`, hidden reasoning, strict JSON Schema and `max_completion_tokens=4096`. The next cycle therefore requires a materially stronger capacity path without silently changing the scientific candidate.

Canonical project evidence:

- `research/results/p12-c2-live-cycle-closure-2026-08-23.json`
- `research/results/p12-c3-live-cycle-closure-2026-08-23.json`
- `docs/CURRENT-PROJECT-STATUS.md`
- `docs/PROJECT-PLAN.md`

## Requirements affected

`REQ-003`, `REQ-004`, `REQ-016`, `REQ-017`, `REQ-018`, `REQ-019`, `KO-010`, `KO-011`, `KO-012`, `EV-007`, `EV-008`.

## Decision criteria

| Criterion | Requirement |
|---|---|
| Complete-packet feasibility | Materially stronger than the failed C2/C3 path and capable of 36/36 parents before scoring. |
| Capacity headroom | Published limits plus exact organization-level verification before provider use. |
| Scientific continuity | Preserve the GPT-OSS 120B model family and frozen candidate/prompt/evaluator semantics where possible. |
| Cost | Prefer no cash spend for the research cycle, but represent trials/credits accurately. |
| API compatibility | `seed`, `max_completion_tokens`, reasoning effort/format, strict structured output and function tools. |
| Reproducibility | Freeze provider, model, SDK/API semantics and disable implicit/hidden network calls. |
| Isolation | Provider qualification cannot read EXPOSED_POOL/private/FRESH_BLIND/LEGACY_LOCKED_TEST inputs. |
| Failure safety | No partial scoring, silent fallback or adaptive provider switching. |

## Current published capacity boundary

The prospective packet needs 36 provider-backed common-parent generations. With the frozen 4,096-token maximum completion budget:

```text
36 × 4,096 = 147,456 maximum reserved completion tokens
```

### Groq Free baseline

Current Groq documentation for `openai/gpt-oss-120b` lists 30 RPM, 1K RPD, 8K TPM and 200K TPD. The maximum completion allocation alone would consume 73.7% of the daily token allowance, leaving only 52,544 tokens for all prompts, retries and other organization usage. This boundary already failed prospectively in C2/C3.

### Cerebras Free Trial boundary

Current Cerebras documentation for `gpt-oss-120b` lists **5 RPM, 30K TPM, 1M TPH and 1M TPD** for the Free Trial. This is a 5× larger published daily token boundary and a 3.75× larger TPM boundary than Groq Free, but with a lower RPM ceiling.

The Cerebras Free Trial is **not a permanent free tier**. Current documentation states that new accounts receive $5 in free credits after adding a verified payment method; those credits expire after 30 days. API/Playground access is inactive without the required account setup. Therefore “zero-cost” here means **zero cash spend only while valid trial credit remains**, not permanently free infrastructure.

Cerebras also documents an important rate-limit rule: request admission estimates input tokens plus `max_completion_tokens`. With `max_completion_tokens=4096`, safe pacing cannot be inferred from RPM alone. Before C4 live generation, measure or upper-bound prompt tokens per parent and derive a pacing rate that satisfies both verified RPM and TPM with explicit headroom.

For a prompt-size upper bound `P`, the theoretical request-rate ceiling is bounded by:

```text
requests_per_minute <= min(verified_RPM, floor(verified_TPM / (P + 4096)))
```

The live plan must use a stricter prospectively frozen rate with safety margin; it must not simply run at the 5 RPM account maximum.

## Alternatives considered

### A — Groq Free, same model/config

**Pros:** lowest serving-path confound, existing runner, permanently zero-cash under current Free access.

**Cons:** 8K TPM / 200K TPD and the exact route already failed in two consumed prospective cycles.

**Decision:** `REJECTED` under the current organization limits.

### B — Groq Developer / verified higher Groq quota

**Pros:** smallest provider confound; existing integration; materially higher published Developer capacity.

**Cons:** pay-as-you-go or separately granted quota; exact organization limits still need evidence.

**Decision:** `PARETO_BACKUP`, and preferred over a provider switch if paid capacity becomes authorized before C4 freezes and exact quota is sufficient.

### C — Cerebras Free Trial / GPT-OSS 120B

**Pros:** same underlying GPT-OSS 120B family; 1M TPD and 30K TPM published Free Trial boundary; strict structured outputs, reasoning, `seed`, `max_completion_tokens` and function tools are documented; no persistent serving infrastructure.

**Cons:** different serving implementation is an explicit experimental confound; only 5 RPM; the trial is time/credit bounded and requires account setup/payment-method verification; exact organization limits can vary; prompt + max-completion reservation requires measured pacing.

**Decision:** `SELECTED_CONDITIONAL_GO` for provider qualification and P12-C4 preregistration only.

### D — Dedicated same-model endpoint

**Pros:** strongest reserved-capacity argument.

**Cons:** paid infrastructure, added provisioning/operations, different serving stack.

**Decision:** `PARETO_BACKUP` if shared-provider capacity cannot be qualified.

### E — Local/self-hosted GPT-OSS 120B

**Pros:** full capacity/control and open weights.

**Cons:** no project evidence of available 80GB-class hardware or end-to-end throughput; new serving stack and schedule risk.

**Decision:** `REJECTED_FOR_CURRENT_SCHEDULE` unless appropriate hardware is already available and measured.

### F — Different model/provider

Changes both model and provider, producing a larger scientific confound than a same-model serving-path change.

**Decision:** `DEFERRED` while a same-model route remains credible.

## Pareto frontier

| Route | Cash cost | Capacity confidence | Scientific continuity | Operational burden | Role |
|---|---:|---|---|---|---|
| Cerebras Free Trial / GPT-OSS 120B | $0 only while trial credit is active | Conditional; published 30K TPM / 1M TPD, org verification pending | Medium-high | Low | **Selected qualification path** |
| Groq Developer / GPT-OSS 120B | Pay-as-you-go | High if org quota verifies | **Highest** | Low | Scientific-continuity backup |
| Dedicated same-model endpoint | Paid | **Highest** | Medium-high | Medium-high | Capacity-guarantee backup |

## Decision

Select **Cerebras Free Trial + `gpt-oss-120b`** as the path for **P12-C4 preregistration and synthetic provider compatibility qualification**, not as a permanent production provider and not yet for EXPOSED_POOL generation.

The serving-provider change is an explicit confound. C4 can support internal preregistered arm comparisons; cross-cycle claims against C1/C2/C3 must separate candidate effects from serving-provider effects.

No automatic failover is allowed. One provider/model/SDK/request contract must be frozen for a complete packet.

## Mandatory pre-live gates

Before the first EXPOSED_POOL provider call:

1. freeze 36 fresh common-parent seeds and prove no P12-C1/C2/C3 seed/partial-parent reuse;
2. pass the provider-free request-contract and benchmark-isolation checks;
3. verify exact Cerebras organization limits and active Free Trial/Developer access from the account Limits page or equivalent first-party evidence;
4. measure or conservatively upper-bound prompt tokens for every common-parent request and freeze safe pacing from verified RPM/TPM plus the 4,096 completion reservation;
5. freeze `gpt-oss-120b`, exact SDK version/API semantics, `temperature=0`, `reasoning_effort=medium`, `reasoning_format=hidden`, strict JSON Schema, seed binding and tool semantics;
6. when using the official SDK, construct the client with `warm_tcp_connection=False` so client initialization cannot add unpreregistered warming requests;
7. run only the separately preregistered synthetic compatibility probe, containing no benchmark/private outcome information;
8. classify any auth/rate-limit/semantic/transport failure before any retry and do not let partial probe success authorize C4;
9. freeze complete-packet/missingness/failure semantics;
10. pass the full provider-free C4 activation gate and freeze the live manifest before the first benchmark call;
11. keep private-oracle, FRESH_BLIND and LEGACY_LOCKED_TEST accesses at zero during generation.

## Probe semantics already verified from current provider documentation

Current Cerebras documentation states that:

- `gpt-oss-120b` supports `reasoning_effort` values including `medium`;
- `reasoning_format=hidden` removes reasoning text/logprobs from the response while reasoning tokens still count;
- `max_completion_tokens` includes reasoning tokens;
- `seed` is best-effort deterministic, not guaranteed deterministic;
- strict JSON Schema Structured Outputs and function tools / `tool_choice=required` are supported.

Therefore byte-identical replay is **not** a valid hard success criterion for the seed field; acceptance and stable seed binding are the relevant contract checks.

## Consequences

- **Positive:** materially more daily/token headroom than the failed Groq Free route while preserving the GPT-OSS 120B model family.
- **Negative:** lower RPM and a provider/serving-stack confound.
- **Cost:** trial-only zero-cash path; not a renewable free tier.
- **Operational:** requires `CEREBRAS_API_KEY`, exact account-limit evidence, prompt-size/pacing evidence, and disabled SDK warming.
- **Evaluation:** P12-C4 remains a wholly new prospective generation. No C2/C3 output or score reuse; no partial scoring.
- **Architecture:** Cerebras is not frozen as final production architecture.

## Reversal triggers

Reopen this ADR before any P12-C4 live generation if:

- actual account limits are below 30K TPM / 1M TPH / 1M TPD / 5 RPM, or API access is inactive;
- trial credit is unavailable/expired and cash spend has not been authorized;
- measured `prompt_tokens + 4096` leaves no defensible TPM safety margin at a practical prospective pacing rate;
- the synthetic probe cannot satisfy required request semantics without changing the candidate;
- SDK/API/model/version changes after freeze;
- strict schema, seed, tool or reasoning behavior requires a candidate-visible workaround;
- paid Groq capacity becomes authorized with a sufficient exact quota and the lower-confound route becomes preferable;
- a dedicated same-model endpoint becomes available at acceptable cost/schedule risk.

If a pre-live gate fails, do not consume P12-C4. Reopen this ADR and choose another prospectively qualified route.

## Sources

Official/current documentation reviewed 2026-08-24:

- Groq rate limits: https://console.groq.com/docs/rate-limits
- Groq models: https://console.groq.com/docs/models
- Cerebras rate limits: https://inference-docs.cerebras.ai/support/rate-limits
- Cerebras Chat Completions: https://inference-docs.cerebras.ai/api-reference/chat-completions
- Cerebras reasoning: https://inference-docs.cerebras.ai/capabilities/reasoning
- Cerebras structured outputs: https://inference-docs.cerebras.ai/capabilities/structured-outputs
- Cerebras Python SDK package: https://pypi.org/project/cerebras-cloud-sdk/
- OpenAI GPT-OSS release/model sizing: https://openai.com/index/introducing-gpt-oss/
