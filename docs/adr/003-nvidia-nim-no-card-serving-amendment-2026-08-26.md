# ADR-003 — NVIDIA NIM no-card serving amendment for P12-C4

**Date:** 2026-08-26  
**Status:** ACCEPTED_FOR_PROVIDER_QUALIFICATION_ONLY  
**Scope:** P12-C4 infrastructure/provider qualification. This ADR does not authorize EXPOSED_POOL generation, private scoring, semantic evaluation, FRESH_BLIND access, or production-readiness claims.

## Context

The P12-C4 Cerebras synthetic authorization was consumed after the first live request failed with HTTP 402 before any model output. The subsequent OpenRouter + OpenInference route was prospectively frozen and independently authorized, but its first live synthetic request failed with HTTP 404 because `openai/gpt-oss-120b:free` was no longer available for free. That authorization is also consumed.

No P12-C4 benchmark parent has been generated and no candidate outcome was observed in either provider-qualification failure.

NVIDIA currently exposes a hosted NVIDIA NIM endpoint for the same underlying model family, `openai/gpt-oss-120b`, through the OpenAI-compatible Chat Completions endpoint:

- `https://integrate.api.nvidia.com/v1/chat/completions`
- credential: `NVIDIA_API_KEY`
- model: `openai/gpt-oss-120b`

The current first-party NVIDIA model page labels a free prototype endpoint as available. The current model-specific API reference documents `temperature`, `max_tokens`, `stream`, `reasoning_effort`, `tools`, and `tool_choice`. The published request schema does not explicitly list `seed`, `response_format`, or `parallel_tool_calls`, even though the model overview advertises structured-output capability.

## Decision

Use the hosted NVIDIA NIM route only as a new, independent P12-C4 provider-qualification candidate.

The serving path is frozen as:

```text
GitHub Actions
  -> https://integrate.api.nvidia.com/v1/chat/completions
  -> NVIDIA hosted NIM
  -> openai/gpt-oss-120b
```

No provider gateway, alternate upstream, automatic failover, model fallback, warming request, or automatic retry is permitted.

The required request semantics remain:

- model `openai/gpt-oss-120b`;
- `temperature=0`;
- `max_tokens=4096`;
- `stream=false`;
- `reasoning_effort=medium`;
- per-request synthetic/live seed field present;
- strict JSON-schema structured output for the structured-output path;
- forced named function tool call for the tool path;
- `parallel_tool_calls=false`.

Because `seed`, `response_format`, and `parallel_tool_calls` are not explicitly listed in the current model-specific request schema, they are **compatibility hypotheses, not assumed capabilities**. The one-shot synthetic gate must prove the complete frozen request contract. Rejection, silent semantic failure, or malformed output blocks activation.

NVIDIA may return `reasoning_content`. Reasoning traces are not evaluation outputs and must never be persisted or exposed. The live runner hashes the raw response for provenance, then stores only a sanitized response projection containing final content/tool-call semantics, model identifier, finish reason, and usage.

## Experimental-validity interpretation

Changing the serving path is an explicit infrastructure confound. It does not change the candidate arms, C4 seed map, frozen prompts, evaluator, scoring gates, or factorial design.

The NVIDIA route may not be used to reinterpret C1/C2/C3, the Cerebras synthetic failure, or the OpenRouter synthetic failure.

Synthetic provider qualification uses synthetic prompts only and must load zero benchmark inputs, zero private-oracle data, zero FRESH_BLIND data, and zero LEGACY_LOCKED_TEST data.

## Authorization sequence

```text
1. ADR-003 + NVIDIA serving contract + synthetic preregistration frozen
2. provider-free self-check PASS
3. separate NVIDIA one-shot authorization frozen
4. exactly 2 preregistered NVIDIA synthetic calls
5. semantic 2/2 PASS
6. separate full C4 activation/capacity gate
7. live manifest freeze
8. exactly 36/36 common parents
9. local A00/A10/A01/A11 expansion -> exactly 144/144 outputs
10. only then deterministic scoring
```

A 2/2 synthetic PASS is necessary but not sufficient for the 36-call collection. Before EXPOSED_POOL generation, a separate provider-free activation gate must establish that the currently available NVIDIA trial/free capacity is operationally sufficient or otherwise freeze a valid bounded execution plan. No private scoring is allowed on incomplete packets.

## Stop rules

- Cerebras and OpenRouter synthetic authorizations remain consumed and may never be reused or rerun.
- NVIDIA authorization is one-shot and `run_attempt=1` only.
- At most two synthetic provider requests may be attempted under that authorization.
- Any failure in either synthetic call consumes the authorization and blocks activation.
- Automatic retries = 0.
- Provider fallbacks = 0.
- Model fallbacks = 0.
- Any unsupported required parameter reopens the serving contract.
- Any auth/access/capacity failure reopens provider readiness.
- No EXPOSED_POOL call occurs before audited 2/2 synthetic PASS, activation PASS, and live-manifest freeze.
- No partial C4 packet may be scored.

## Evidence sources reviewed

- NVIDIA hosted model page for `openai/gpt-oss-120b`, showing the free prototype endpoint and OpenAI-compatible example: `https://build.nvidia.com/openai/gpt-oss-120b/build`.
- NVIDIA model-specific Chat Completions API reference, current 2026-08-26: `https://docs.api.nvidia.com/nim/reference/openai-gpt-oss-120b-infer`.
- NVIDIA model overview/model card describing configurable reasoning, tool use, and structured-output capability: `https://build.nvidia.com/openai/gpt-oss-120b/modelcard`.
