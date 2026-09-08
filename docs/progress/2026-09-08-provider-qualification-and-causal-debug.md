# Provider qualification and causal-debug episode — 2026-09-08

**Status:** APPEND-ONLY PROGRESS EVIDENCE  
**Scope:** provider tournament finalization, Groq-only qualification, causal failure diagnosis, strict-output design and experiment-infrastructure findings.

This note records the 2026-09-08 episode prospectively. It does not rewrite prior provider experiments, Release 0 acceptance, old preregistrations or failed attempts.

## Starting point

Repository production baseline for provider comparison:

`4364364266c6a88d4affd85cb3a734c774cd42c8`

Frozen V3 decision population:

`17 scenarios × 5 repetitions`

Population SHA-256:

`4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9`

The objective was to close the final provider decision with no retries, no fallback, no JSON repair, failures in the denominator and hard reliability/contract gates.

## V4 Cloudflare × Groq preparation

The final V4 protocol compared the same GPT-OSS-120B weights over two providers:

- Cloudflare `@cf/openai/gpt-oss-120b`;
- Groq `openai/gpt-oss-120b`.

The protocol kept the same decision instruction, application schema semantics, temperature 0 and deterministic post-generation validation. Provider-native tools, web search, state, fallback and repair remained disabled.

Pre-scored transport work found:

- Cloudflare calls reached Workers AI but returned 429 / error 4006 because the daily free allocation was exhausted;
- Groq's edge rejected the default Python `urllib` signature with Cloudflare error 1010;
- an explicit application `User-Agent` plus `Accept: application/json` restored Groq model-list/chat access;
- Groq response headers exposed an 8,000-token rate bucket in the observed account context.

The transport/pacing amendment was frozen before any scored V4 attempt:

`22ef052b292bb77618973cc6447f08970dc13159`

Pinned bootstrap:

`a34f1c6cce26219df6c06772ec2ea5599637e391`

No Cloudflare/Groq preflight call was counted in the final denominator.

## Cloudflare removed from the requested path

Cloudflare remained quota-blocked. The user explicitly requested proceeding without Cloudflare.

The experiment was therefore reclassified as **Groq-only qualification** rather than pretending a paired tournament had completed.

## Groq-only final qualification

Frozen qualification manifest:

`research/experiments/provider-qualification-v4-1-groq-final-manifest.json`

Runner:

`1ad041fdcbe4424a79239fff6382df67e8bc2bfe`

Bootstrap:

`6fc9d84262efaf6d57925a83ba59f07425cfc717`

Protocol remained:

- 85 attempts;
- same frozen 17×5 population;
- temperature 0;
- reasoning medium;
- max completion 512;
- no automatic retry/fallback/repair;
- failures remain denominator;
- raw provider material excluded.

### Result

`NO_SELECTION`

Final metrics recorded from the completed 85/85 run:

- rubric pass: 69/85 = 81.18%;
- reliability: 70/85 = 82.35%;
- contract failures: 9;
- repeat stability: 11/17 = 64.71%;
- p50 latency: 1.154 s;
- p95 latency: 2.904 s;
- estimated list-price total cost: US$ 0.04051.

Unknown-tool proposals, invalid known-tool arguments and private/identity-material attempts were not the limiting class. Structural/terminal decision reliability was.

Reproduced failure families included upstream-unavailable, action-governance, analysis-detail, model, spectrum and knowledge-search cases.

## Causal-debug hypothesis

Rather than lower the hard gates, the next work decomposed failures into:

1. 512-token truncation / finish behavior;
2. `strict:false` structured-output conformance;
3. reasoning-effort effects.

The diagnostic matrix targets seven scenarios and three configurations:

```text
B0  best-effort / medium / 512
B1  best-effort / medium / 2048
B2  best-effort / low / 2048
```

Runner commit:

`426b0ecacf8b794199b78380a5de5837603e29e3`

Frozen bootstrap:

`7826a46d0209c1072a75b59f527dac82b3437a82`

Health-preserving bootstrap:

`b71172bf1f42d4be074560336e58c42539cbfe1c`

## Causal evidence obtained

Useful exploratory/partial observations showed:

- clean controls passed across medium/512, medium/2048 and low/2048;
- low reasoning used dramatically fewer reasoning tokens in observed controls and roughly halved latency;
- `ANALYSIS_DETAIL` can return HTTP 200 + `finish_reason=stop` + valid JSON and still violate `ProviderDecisionPayload` relational invariants;
- increasing the output ceiling to 2048 therefore cannot by itself solve structural payload failures;
- the same scenario can pass or fail under best-effort structured output even at temperature 0.

Conclusion: 512 likely contributes to some finish failures, but the structural failure class independently justifies testing constrained `strict:true` output.

## Strict-output direction

The project already has canonical ToolSpecs/Release 0 structures. The proposed strict challenger should derive legal closed variants from those contracts:

```text
TOOL::<canonical tool> | FINAL | CLARIFY | ESCALATE | ABSTAIN
```

Every object should be closed; legal tool arguments should derive from the canonical registry/OpenAPI; `ProviderDecisionPayload` stays as a second deterministic barrier.

The exact supplied `ActionRequest` request-body definition still needs to be recovered before strict action-schema coverage can be declared complete.

## Railway experiment interference

Railway account/project capacity is currently five services. Creating a sixth dedicated experiment service failed due resource/service limit.

The shared `qa-live-prompt-matrix` service was concurrently repurposed by OpenRouter/Nemotron diagnostics. Multiple 21-call causal attempts were interrupted by overlapping deployments and were deliberately discarded rather than stitched together.

One partially completed clean causal deployment reached multiple useful observations, including an `ANALYSIS_DETAIL` root validation failure, before being removed by another deployment.

A later non-overlapping attempt showed benchmark-shaped Groq requests receiving HTTP 429 even after the previous emitted-token pacing and 60-second cooldown. The simplified remaining-token header was insufficient to predict admission.

This means the causal 21/21 matrix remains incomplete and must be re-run only after the account's effective admission behavior is understood.

## Rate/admission diagnostic prepared

To avoid confusing provider capacity with model quality, a sanitized one-shot benchmark-shaped admission diagnostic was added:

`8cec9f8d7e596bda27a4459ac4130319547d2f5e`

Pinned bootstrap:

`0ecc8365f3908f6ddc8521998436a30eee2d5507`

It records status, sanitized rate headers/error class and usage while excluding raw prompt/response/credentials.

The diagnostic was frozen but had not produced a result at the time this progress note was written.

## OpenRouter side observation

A concurrent OpenRouter key-capacity probe reported the configured key as free tier with published free-model daily capacity 50 requests, below the 85 calls required by the final qualification population. This makes that current route ineligible as a simple drop-in final 85-call replacement under the observed tier.

## Production boundary

No provider experiment in this episode changed `production-api` or `production-web`. No new provider was promoted. Consequential action execution remains disabled.

## Continuation contract

The approved next sequence is:

1. complete a clean isolated 21/21 causal matrix;
2. recover exact `ActionRequest`;
3. generate canonical `strict:true` schema;
4. run minimal strict eligibility preflights;
5. freeze only causally justified B0/B1/C1/C2 challengers;
6. evaluate with unchanged rubrics;
7. enforce unchanged hard gates;
8. give only a gate-passing winner a fresh 85/85 run;
9. require Academy live E2E before any production promotion.

No gate is relaxed to manufacture a winner.
