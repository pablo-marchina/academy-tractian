# ADR-019 — Cloudflare provider client provider-free implementation

**Status:** ACCEPTED  
**Decision state:** `FROZEN_IMPLEMENTATION / LIVE_NOT_AUTHORIZED`  
**Date:** 2026-08-31  
**Issue:** #71  
**Parent preregistration:** ADR-018  
**Scientific state changed:** NO  
**Provider/model inference calls authorized by this ADR:** 0  
**Credential/account probes authorized:** 0  
**Live network validation authorized:** 0  
**Provider/model selected:** NO  
**Production actions enabled:** NO

## 1. Decision question

What is the minimum provider-specific Cloudflare Workers AI client implementation required to satisfy the exact ADR-018 preregistered request/response boundary while preserving historical provider implementation evidence and proving behavior without any provider/model call?

## 2. Decision

Freeze the following already-materialized implementation bytes after provider-free CI and full repository regression validation:

| Artifact | Frozen Git blob |
|---|---|
| Cloudflare client | `src/academy_tractian/cloudflare_provider_client.py` — `a5c814b519584b6d4346e3b0567bbc3da8ba0bf4` |
| provider-free tests | `tests/test_cloudflare_provider_client.py` — `4c455b35d3949e809848017d478507141f278e42` |
| dedicated CI workflow | `.github/workflows/cloudflare-provider-client-provider-free.yml` — `88b0542acf9c2de2916484f3b435e8ed7ad8b191` |

ADR-018 remains immutable and authoritative for candidate eligibility, population, execution geometry, metrics, zero-cost envelope and future live comparison rules. ADR-019 freezes only the minimal provider-specific client boundary needed to implement that preregistration.

## 3. Historical implementation preservation

`src/academy_tractian/provider_clients.py` is retained unchanged as historical ADR-009 OpenAI/Gemini implementation evidence.

The Cloudflare client is isolated in a new module rather than mutating those historical bytes. It reuses only provider-neutral types/contracts already exposed by the repository:

- `ProviderDecisionRequest`;
- `PROVIDER_DECISION_SYSTEM_INSTRUCTION`;
- `PROVIDER_DECISION_JSON_SCHEMA`;
- `ProviderHttpRequest` / `ProviderHttpResponse`;
- `ProviderJsonTransport`;
- `ProviderUsageRecord`;
- `ProviderHttpClientError`.

No historical provider result, threshold, candidate or execution artifact is rewritten.

## 4. Frozen candidate / route allowlist

The client accepts exactly the two ADR-018 model IDs:

```text
@cf/zai-org/glm-4.7-flash
@cf/nvidia/nemotron-3-120b-a12b
```

Any other model ID fails at construction.

Frozen provider/route identity:

```text
provider_id  cloudflare
route_id     cloudflare.workers_ai.openai_compat.chat_completions.v1
endpoint     https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions
```

The account ID is constructor-supplied and restricted to ASCII letters/digits before interpolation into the endpoint.

## 5. Credential / transport boundary

The implementation performs no environment lookup and contains no Cloudflare/OpenAI SDK or concrete HTTP/network transport.

Constructor inputs are explicit:

```text
api_token
account_id
model_id
transport
```

The `ProviderJsonTransport` is injected. Provider-free tests use a scripted fake transport only.

The client representation redacts both token and account ID. Request bodies contain no token; HTTP/transport errors are converted to bounded `ProviderHttpClientError` reason codes and raw exception/provider response material is never serialized into the raised error.

This implementation does **not** prove credential validity, Cloudflare account availability or live API compatibility. Those remain future operational gates.

## 6. Frozen request mapping

For every `ProviderDecisionRequest`, the client constructs exactly one `POST` request with:

```text
model                       exact frozen model ID
messages                    system + serialized ProviderDecisionRequest
response_format             ProviderDecisionPayload JSON Schema
temperature                 0
n                           1
stream                      false
max_completion_tokens       512
store                       false
tool_choice                 none
parallel_tool_calls          false
```

Explicitly absent:

- provider-native tool definitions/execution;
- AI Gateway route/headers;
- provider seed;
- conversation/previous-response state;
- built-in web search;
- automatic repair;
- warm-up;
- retry;
- fallback.

The application-owned `ProviderDecisionSource` remains responsible for strict payload validation. `AgentController` remains the orchestration owner and `HarnessRunner.execute_tool()` remains the exclusive real tool-execution boundary.

## 7. Frozen response/failure mapping

A successful response must satisfy all of the following before its text reaches `ProviderDecisionSource`:

- top-level `object == "chat.completion"`;
- returned `model` exactly equals the requested frozen model ID;
- exactly one choice;
- choice index is `0` or omitted;
- `finish_reason == "stop"`;
- message role is `assistant`;
- provider-native `tool_calls` absent/empty;
- legacy `function_call` absent;
- refusal absent/empty;
- content is a non-empty string.

Any violation fails closed. The client performs exactly one injected-transport invocation per `complete()` call and contains no retry loop.

Transport exceptions are sanitized to `TRANSPORT_FAILURE`. Non-2xx responses produce only `HTTP_STATUS:<status>` semantics without provider response bodies.

## 8. Frozen usage boundary

The implementation records only provider-reported integer token counts when present and valid:

```text
prompt_tokens      -> input_tokens
completion_tokens  -> output_tokens
total_tokens       -> total_tokens
reasoning_tokens   -> reasoning_tokens when supplied
```

Missing, non-integer, boolean or negative values become `None`; they are never fabricated or imputed.

This is compatible with future ADR-018 M8 neuron accounting, but ADR-019 does not execute or validate real Cloudflare accounting.

## 9. Provider-free validation evidence

The final implementation head passed the dedicated provider-free workflow and all repository workflows triggered by the change, including:

- `cloudflare-provider-client-provider-free`;
- `production-runtime`;
- `final-handoff-acceptance-audit`;
- `final-delivery-provider-free-reproduction`;
- E9/E14 and benchmark-split regressions.

The dedicated suite validates both frozen models, exact request shape, strict `ProviderDecisionSource` integration, model/route/finish drift rejection, provider-native tool/function/refusal rejection, sanitization, one-attempt failures, usage accounting without fabrication and absence of environment/SDK/network access in the new module.

The first CI attempt exposed a false-positive test that matched the substring `environ` inside the docstring word `environment`; the test was corrected to inspect actual AST name/attribute references. No client behavior was changed to accommodate that test.

## 10. Non-authorization

ADR-019 authorizes:

```text
provider/model inference       0
credential/account probes      0
live network validation        0
comparison execution           0
production provider selection  NO
customer mutations             0
C4/scientific changes          0
```

The existence of this client does not authorize attempt 1.

## 11. Next evidence-first gate

Before creating any new live executor/custody implementation, audit the existing ADR-010/ADR-011 executor, provenance, write-ahead claim and custody machinery against ADR-018/ADR-019.

For each component classify:

- reusable unchanged;
- reusable with a bounded provider-specific adapter;
- incompatible due to frozen OpenAI/Gemini assumptions;
- missing and therefore requiring a prospective implementation amendment.

Only concrete gaps found by that audit may authorize new live-execution code.

Even after that audit/implementation, a separate explicit live-execution authorization must freeze account/free-tier proof, remaining-neuron proof, durable custody root, exact client/route identities and attempt-claim semantics before the first real Cloudflare request.

## 12. Reversal triggers

Reopen ADR-019 prospectively if any of the following occurs:

- ADR-018 candidate/route/request semantics change;
- live documentation/evidence proves the frozen request shape is incompatible;
- Cloudflare returns a materially different response envelope that cannot be represented without changing the frozen parser;
- provider-free regression finds a safety/provenance leak;
- live custody/resource accounting requires a provider-specific field not exposed by the frozen client;
- a new route is needed to satisfy the USD-0 hard constraint.

Do not edit ADR-019 or its frozen implementation bytes after live evidence begins. Any material change requires a prospective ADR/version preserving consumed evidence.