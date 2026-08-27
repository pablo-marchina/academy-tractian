# ADR-002 — No-card OpenRouter serving amendment for P12-C4

Status: `ACCEPTED_PRE_OUTCOME_AMENDMENT`
Date: 2026-08-26
Decision state: `CONDITIONAL_GO_TO_OPENROUTER_SYNTHETIC_QUALIFICATION`
Live EXPOSED_POOL generation: `NOT_AUTHORIZED`

## Context

ADR-001 selected Cerebras Free Trial for P12-C4 provider qualification. The one-shot Cerebras synthetic probe was consumed in GitHub Actions run `32901958789` before any model output: the first generation request returned HTTP 402 `payment_required`, the second call was not attempted, and no benchmark/private/FRESH_BLIND/LEGACY_LOCKED_TEST input was loaded. The canonical closure is `research/results/p12-c4-cerebras-synthetic-live-probe-closure-2026-08-25.json`.

The project now has an explicit no-card constraint. Retrying Cerebras under the consumed authorization is forbidden. Groq Free remains rejected for the current confirmatory cycle because P12-C2 and P12-C3 were consumed on that capacity path.

This amendment changes only the prospective serving path. It does not change candidate arms, evaluator, benchmark geometry, fresh C4 seeds, deterministic gates, bootstrap/LOGO contract, or complete-packet-only scoring rule.

## New selected qualification path

Use OpenRouter with the concrete free variant `openai/gpt-oss-120b:free`, pinned to the OpenInference backend.

Frozen routing:

```json
{
  "provider": {
    "only": ["open-inference"],
    "order": ["open-inference"],
    "allow_fallbacks": false,
    "require_parameters": true
  }
}
```

The free-variant model page reviewed 2026-08-26 shows OpenInference as the only free backend for `openai/gpt-oss-120b:free`. OpenRouter documents `provider.only`, `provider.order`, `allow_fallbacks=false`, and `require_parameters=true` as request-level routing controls.

## Scientific continuity

The underlying model family remains `openai/gpt-oss-120b`. The OpenRouter transport maps the prior serving semantics as follows:

| Frozen semantic | Cerebras representation | OpenRouter representation |
|---|---|---|
| model family | `gpt-oss-120b` | `openai/gpt-oss-120b:free` |
| temperature | `0` | `0` |
| reasoning effort | `reasoning_effort="medium"` | `reasoning.effort="medium"` |
| hidden reasoning | `reasoning_format="hidden"` | `reasoning.exclude=true` |
| completion ceiling | `max_completion_tokens=4096` | `max_tokens=4096` |
| seed binding | integer seed | integer seed |
| strict structured output | JSON Schema strict | JSON Schema strict |
| tools | function tools + required tool choice | function tools + required tool choice |

These are treated as serving-API translations, not candidate changes. The provider/gateway change remains an explicit cross-cycle confound; C4 may support preregistered within-cycle arm comparisons, not clean provider-independent comparisons to C1/C2/C3.

## Free-tier feasibility boundary

Current OpenRouter documentation reviewed 2026-08-26 states:

- free accounts with less than $10 purchased credits are limited to 50 free-model requests/day;
- free models are limited to 20 requests/minute;
- `openai/gpt-oss-120b:free` is priced at $0 input / $0 output;
- free model availability is not guaranteed like paid serving.

Planned provider-backed generation budget:

```text
new synthetic qualification calls   2
P12-C4 common-parent calls          36
--------------------------------------
maximum planned generation calls    38
published free daily allowance      50
nominal request headroom             12
```

This feasibility claim assumes no unrelated free-model calls consume the same account's daily allowance during the packet. Failed live requests may consume request allowance, so automatic retry is forbidden.

## Transport decision

Use direct HTTPS to `https://openrouter.ai/api/v1/chat/completions` with exactly pinned `httpx==0.28.1`.

- credential: `OPENROUTER_API_KEY`;
- no OpenAI/OpenRouter SDK dependency in the live probe;
- `httpx` automatic retries: none;
- explicit application retries: zero;
- OpenRouter fallback: false;
- provider allowlist: OpenInference only;
- model fallback list: absent;
- streaming: false.

A direct HTTP client is selected to minimize hidden client behavior and make the exact request body auditable.

## Mandatory gates before EXPOSED_POOL

1. Freeze the OpenRouter serving contract and synthetic preregistration.
2. Pass a provider-free compatibility/self-check with zero credential reads, zero network I/O and zero benchmark/private/blind access.
3. Generate a new one-shot OpenRouter authorization artifact; the consumed Cerebras authorization is never reused or reinterpreted.
4. Execute at most the two preregistered OpenRouter synthetic generation calls under that authorization, with no retry/fallback.
5. Require both synthetic calls to complete and pass semantic validation; partial success does not authorize C4.
6. Only after a 2/2 PASS may the full provider-free C4 activation/live-manifest gate be frozen and executed.
7. P12-C4 must then reach 36/36 common parents and 144/144 fixed arm outputs before any scoring.
8. Private scoring, FRESH_BLIND and LEGACY_LOCKED_TEST remain blocked during generation.

## Reversal / stop triggers

Reopen the serving decision before benchmark generation if any of the following occurs:

- `openai/gpt-oss-120b:free` is no longer free or available;
- OpenInference is no longer an eligible backend for that free variant;
- routing cannot be restricted to OpenInference with fallbacks disabled;
- `seed`, reasoning, strict JSON Schema, required tool calling, or `parallel_tool_calls=false` cannot be honored without candidate-visible changes;
- either synthetic call receives auth/permission/rate-limit/capacity/transport/semantic failure;
- the account does not have enough remaining free request allowance for the complete 36-parent packet;
- the API or response contract changes after freeze.

No failure under this amendment authorizes fallback to another provider or model. A new route requires another prospectively frozen amendment.

## Sources reviewed 2026-08-26

- OpenRouter free variant: https://openrouter.ai/openai/gpt-oss-120b:free/providers
- OpenRouter provider routing: https://openrouter.ai/docs/guides/routing/provider-selection
- OpenRouter reasoning: https://openrouter.ai/docs/guides/best-practices/reasoning-tokens
- OpenRouter FAQ / free-model limits: https://openrouter.ai/docs/faq
- OpenRouter pricing: https://openrouter.ai/pricing
