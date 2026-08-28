# ADR-009 — Provider HTTP clients and bounded live-comparison authorization — 2026-08-28

**Status:** ACCEPTED  
**Decision state:** `FROZEN_FOR_PROVIDER_HTTP_CLIENTS_AND_BOUNDED_LIVE_COMPARISON_AUTHORIZATION`  
**Issue:** #35  
**PR:** #36  
**Scientific state changed:** NO  
**Production provider/model selected:** NO  
**Production mutating actions enabled:** NO  
**Live provider/model calls executed by this decision task:** 0

## Decision question

Can the exact ADR-008 provider/model comparison move from provider-free design into a separately executed, tightly bounded live comparison without weakening ADR-004 through ADR-008, leaking runtime/evaluator state, introducing provider-owned orchestration, hidden retries/fallbacks, or post-result discretion?

## Context

ADR-008 froze the comparison design but intentionally left real provider clients absent and live execution unauthorized. Before live evidence can be collected, the application needs concrete clients for the exact frozen routes while preserving the existing provider-neutral `ProviderDecisionClient` contract.

The accepted clients are deliberately small HTTP adapters rather than provider SDKs or provider-hosted agent loops. They translate the already-sanitized `ProviderDecisionRequest` into one stateless provider request and return one JSON string to the existing ADR-006 `ProviderDecisionSource`. `AgentController`, `HarnessRunner`, B1 validation, ADR-005/B2 action safety and ADR-007 trace provenance retain ownership of their existing responsibilities.

## Current primary-source route facts

Primary-source contract review date: **2026-08-28**.

### OpenAI route

- provider: OpenAI;
- model: `gpt-5.6-sol`;
- endpoint: `POST https://api.openai.com/v1/responses`;
- route ID: `openai.responses.v1.standard`;
- stateless request: `store=false`, no conversation/previous response state;
- reasoning effort: `medium`;
- structured output: Responses `text.format` JSON Schema;
- REST text extraction: completed `output[]` message → `content[]` → `output_text`;
- authentication remains transport-header-only and is constructor supplied.

Official sources:

- https://developers.openai.com/api/docs/models/gpt-5.6-sol
- https://developers.openai.com/api/reference/cli/resources/responses/methods/create

The provider-level JSON Schema uses `strict=false` intentionally because ADR-006 leaves nested `arguments` and `final` as open JSON objects whose canonical relational semantics are validated by the application. This is **not** adapter repair: the returned JSON must still pass the unchanged strict `ProviderDecisionPayload` with no transformation. If the live route requires schema repair or cannot preserve that boundary, the run stops and requires a prospective amendment.

### Google route

- provider: Google;
- model: `gemini-3.7-flash`;
- endpoint: `POST https://generativelanguage.googleapis.com/v1beta/interactions`;
- route ID: `google.interactions.v1beta.stateless`;
- `store=false`, no `previous_interaction_id`;
- thinking level: `medium`;
- thinking summaries: `none`;
- tool choice: `none`;
- structured output: `response_format` text with `mime_type=application/json` and JSON Schema;
- REST text extraction: completed `steps[]` → `model_output` → text content;
- authentication remains transport-header-only and is constructor supplied.

Official sources:

- https://ai.google.dev/api/interactions-api
- https://ai.google.dev/gemini-api/docs/structured-output

## Provider-free implementation decision

Accept `src/academy_tractian/provider_clients.py` as the concrete P0 HTTP client boundary for the two ADR-008 live candidates.

Frozen validated implementation identity:

```text
validated implementation head  3b823c498811a138de60acd65b280cef5dfd2bb1
provider_clients.py git blob    e78807bdfd4fd0ca9840fa2d9e6c62474237ee45
test_provider_clients.py blob   16d4165b966ae47f1117fa72f87e35b0522a64ac
package __init__.py blob        2868fe2bf73bd89d6cc0a6f49a9a096cf5d5bcd1
decision_source.py blob         5579cf6f4c6bfe25d50220fa8b9ddf75c95d100a
```

The accepted implementation guarantees provider-free by construction and regression evidence:

- no provider SDK dependency;
- no `os`/environment credential lookup in the client module;
- credentials are explicit constructor inputs only;
- credentials are present only in transport headers, not body/repr/usage records/RunTrace;
- one `_invoke_once(...)` per `complete(...)`;
- one transport `post_json(...)` inside that boundary;
- zero automatic retry/fallback/warm-up;
- no provider seed;
- no provider-side conversation state;
- no provider-native TRACTIAN tool execution;
- provider route/model/status drift fails closed;
- unexpected provider tool/server/refusal-like output shapes fail closed;
- raw provider request/response/exception content is not copied into canonical trace telemetry;
- token usage is kept in a separate sanitized drainable record keyed by the existing request SHA.

## Preserved failed implementation attempt

The first implementation head is intentionally retained:

`b0a5bc8c2dbea0041ac0324e6471b09b9e68b644`

`production-runtime` run `33140883236` (#22) returned **105 passed / 2 failed**. Both failures were privacy assertions: the provider system instruction named the internal word `idempotency`, even though no idempotency value/state was serialized. The fix removed unnecessary internal control vocabulary from the provider prompt rather than weakening the tests.

Corrected implementation head:

`3b823c498811a138de60acd65b280cef5dfd2bb1`

Validation:

```text
production-runtime run     33140957622 / #23 success
ADR-004 regression         success
triggered workflows        11 / 11 success
real provider calls        0
credential probes          0
```

## Bounded authorization packet

The following already-validated packet becomes effective only when this ADR exists as `ACCEPTED` **and the exact final ADR head passes the provider-free revalidation workflow**:

`research/frozen/provider-model-live-comparison-authorization-v1.json`

Git blob:

`5690414564ccddb07184c333fdf79f4ee2fb7788`

Provider-free packet-validation head:

`ad1c427a00a518424fa058c008ffc661df980c60`

Validation on that head:

```text
provider-live-authorization run  33141147959 / #1 success
production-runtime run            33141147898 / #24 success
triggered workflows               12 / 12 success
validator                         success
tamper tests                      success
full production suite             success
ADR-004 regression                success
real provider calls               0
```

The ADR does not rewrite that packet after successful validation.

## Authorized future execution envelope

Once the final ADR head is provider-free revalidated, a **separate governed execution task** may consume this authorization with exactly:

```text
live candidates                         2
public DEV probes                       8
repetitions / probe / candidate         2
maximum live provider calls            32
warm-up calls                            0
automatic retries                        0
provider/model fallbacks                 0
parallel live calls                   false
provider seed forwarded               false
provider-side conversation state      false
production mutating actions enabled   false
semantic/private/blind evaluation     false
```

Execution order remains ADR-008: P01→P08, repeats 0→1, alternating the two live candidates by `unit_index + repeat_index` parity; provider-free baseline runs locally first.

The execution task may provision credentials out-of-band and pass them explicitly to the client constructors. It may not change the client code, route/model IDs, population, M1–M10, hard gates, selection rule, call budget, retry/fallback policy or custody boundary without a prospective amendment.

## Hard-stop rules

Stop without selection if any of these occur:

- route or model identity changes materially;
- provider behavior requires adapter repair not preregistered;
- a hidden retry/fallback/warm-up would be needed;
- ADR-007 provenance cannot be produced exactly;
- private/runtime binding state enters provider-visible content;
- raw secret/request/response/exception material would enter canonical trace/reporting;
- provider attempts native TRACTIAN tool execution or server-side state becomes required;
- the 32-call budget cannot complete the frozen packet.

Operational failures remain in denominators. An incomplete packet resolves to `NO_SELECTION`, not to a post-hoc smaller comparison.

## Measurements and selection

ADR-008 M1–M10, hard gates and selection logic remain unchanged. In particular:

- safety/custody/trace violations are disqualifying;
- M1/M4/M5/M7/M10 thresholds are frozen;
- M2/M3 retain canonical tool/B1 ownership;
- M6 latency and M8 exact usage/cost remain visible rather than compensated into one score;
- `NO_SELECTION` is mandatory when evidence is incomplete or tie-break evidence cannot resolve the Pareto set;
- post-result threshold changes are forbidden.

## Non-decisions and non-authorizations

ADR-009 does **not**:

- execute any live provider request itself;
- select OpenAI, Google or any other provider for production;
- authorize production mutating actions;
- alter the C4 scientific gate;
- authorize C4 rescoring/survivor decisions;
- authorize semantic judging, FRESH_BLIND or LEGACY_LOCKED_TEST;
- freeze global architecture;
- claim production readiness;
- add RAG, memory, MCP or multi-agent orchestration.

Scientific provider/model calls authorized by the current C4 gate remain **0**. ADR-009 creates only the bounded, production-comparison execution envelope described above after final provider-free revalidation.

## Reversal / amendment triggers

A prospective amendment is required before execution if official provider documentation or behavior changes any frozen request/response shape, model/route ID, statelessness guarantee or structured-output contract.

After the first authorized live call, any material change creates a new candidate/protocol version and must preserve already-consumed evidence. Never rewrite a failed or partially consumed packet to look clean.

## Regression obligations

Any change to provider clients, ADR-006/007 integration, authorization packet, ADR-008 design/population or this ADR must retain:

1. provider-live authorization validator PASS;
2. authorization tamper tests PASS;
3. full production suite PASS;
4. ADR-004 controller regression PASS;
5. exact provider-client source/route/blob pins unless prospectively amended;
6. zero provider calls during provider-free CI;
7. action execution disabled until separately governed.
