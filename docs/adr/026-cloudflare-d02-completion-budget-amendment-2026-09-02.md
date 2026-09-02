# ADR-026 — Cloudflare D02 completion-budget censoring amendment

**Date:** 2026-09-02  
**Status:** ACCEPTED_PROVIDER_FREE / LIVE_NOT_AUTHORIZED

## Context

D01 completed 32/32 governed Cloudflare Workers AI calls at USD 0 with complete resource accounting and `NO_SELECTION`. Post-run sanitized ledger analysis found a deterministic output-ceiling pattern:

- GLM: 16/16 `CLIENT_FAILURE` attempts reported exactly 512 output tokens.
- Nemotron: 8/8 `CLIENT_FAILURE` attempts reported exactly 512 output tokens.
- Nemotron accepted outputs were 297–495 tokens.
- Nemotron's single `RESPONSE_PAYLOAD_INVALID` attempt reported 476 output tokens.
- Therefore 24/24 generic `CLIENT_FAILURE` attempts hit the exact D01 completion cap.

The D01 Cloudflare client records usage after a successful HTTP/JSON response but before output-envelope validation. It rejects any response whose `finish_reason` is not `stop`. The provider-neutral adapter then collapses all client exceptions into `CLIENT_FAILURE`, so D01 cannot distinguish token-limit termination from another sanitized client-envelope rejection without raw provider material.

This is strong evidence that the dominant D01 failure mode is completion-budget censoring. It is not evidence that single-agent topology, ToolSpec, HarnessRunner, RAG, memory, MCP, LangGraph or multi-agent orchestration is causal.

## Decision

Create a prospective D02 experiment that changes only the minimum variables needed to test the censoring hypothesis.

D02 SHALL:

1. preserve all D01 frozen artifacts and the D01 result unchanged;
2. use the same provider, two models, public eight-unit population, two repeats, tool surface, evaluator, prompt/system instruction, JSON decision schema, temperature, no-retry policy, no-fallback policy and single-agent architecture;
3. increase `max_completion_tokens` from 512 to exactly 1024;
4. persist a sanitized client failure subtype in addition to the existing generic `CLIENT_FAILURE`, while continuing to prohibit raw request, raw response and exception-text persistence;
5. preserve `CLOUDFLARE_FINISH_REASON_INVALID` as a distinguishable sanitized subtype;
6. retain a hard USD 0 budget and forbid paid spillover;
7. require a fresh live authorization after all provider-free D02 tests are green.

The canonical D02 protocol is:

`research/experiments/cloudflare-d02-completion-budget-protocol-v1.json`

## Resource derivation

D02 keeps the D01 maximum accounted prompt size of 8000 tokens and raises only completion capacity to 1024 tokens.

Published/frozen candidate Neuron rates used by D01 remain unchanged:

| Candidate | Input Neurons / 1M tokens | Output Neurons / 1M tokens |
|---|---:|---:|
| GLM 4.7 Flash | 5500 | 36400 |
| Nemotron 3 120B A12B | 45455 | 136364 |

For one attempt:

`worst_case = 8000 * input_rate / 1e6 + 1024 * output_rate / 1e6`

For sixteen attempts per candidate:

- GLM: `1300.3776` Neurons.
- Nemotron: `8052.427776` Neurons.
- Full 32-attempt D02 packet: `9352.805376` Neurons.

Therefore the D01 start gate of 9000 Neurons is insufficient for D02. The D02 start gate is exactly the derived worst-case full packet: **9352.805376 free Neurons remaining before attempt 1**. A run with less available capacity is ineligible and must fail closed before attempt 1.

The 10,000-Neuron Workers Free daily allocation leaves a maximum modeled headroom of `647.194624` Neurons when D02 starts from a verified 10,000-Neuron zero-use state.

## Diagnostic contract

D02 retains `failure_code="CLIENT_FAILURE"` for compatibility with the provider-neutral adapter but adds a separate sanitized `failure_subtype` when the client raises `ProviderHttpClientError`.

Allowed diagnostic material is limited to a bounded code such as:

- `CLOUDFLARE_FINISH_REASON_INVALID`
- `CLOUDFLARE_OUTPUT_TEXT_INVALID`
- `CLOUDFLARE_MODEL_MISMATCH`
- `HTTP_STATUS`
- `TRANSPORT_FAILURE`

No response body, generated text, exception string, token, account identifier or credential may be written to the canonical trace/ledger by this feature.

## Interpretation rule

D01 remains the authoritative D01 result and is not rescored or retroactively repaired.

D02 asks one question only: whether the 512-token ceiling materially censored otherwise useful model decisions. If D02 removes `CLIENT_FAILURE` censoring but task-quality failures remain, subsequent work may investigate prompt/schema/model behavior. Architecture work remains `NO_CHANGE` unless separate measured evidence satisfies issue #92's materiality gate.

## Authorization boundary

This ADR and its implementation authorize **zero live provider calls**. They establish a provider-free D02 contract only.

A live D02 run requires a separate fresh same-UTC-day authorization/custody path proving sufficient free allocation for the `9352.805376`-Neuron worst-case packet and preserving USD 0 / no-paid-spillover semantics.
