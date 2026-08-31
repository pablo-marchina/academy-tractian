# Minimum USD-0 Cloudflare provider/model comparison — 2026-08-31

Status: `PREREGISTERED_CANDIDATE / PROVIDER_FREE_ONLY`  
Issue: #68  
Scientific state changed: `NO`  
Provider/model calls authorized by this document: `0`  
Credential/account probes authorized: `0`  
Cloudflare client implementation authorized: `0`  
Production provider selected: `NO`

## Decision question

Between the two current production-eligible Cloudflare Workers AI Free candidates retained by the completed provider factual gates, which is the strongest project-specific Pareto point behind the frozen ADR-006 `ProviderDecisionSource` on public decision quality, reliability/stability, latency and zero-cost resource use while preserving all deterministic safety/provenance boundaries?

Core live candidates:

1. `@cf/zai-org/glm-4.7-flash`;
2. `@cf/nvidia/nemotron-3-120b-a12b`.

The machine-readable manifest `research/experiments/provider-model-comparison-design-manifest-v2.json` is authoritative for exact formulas, thresholds, budgets and amendment rules.

## Why a new experiment is justified

The repository historical evidence audit prevents blank-slate provider research. Groq has preserved operational, negative quality and capacity evidence; Gemini Free is not eligible for arbitrary production payload under the current provider-visible data path; Gemma is not materially distinct enough for the minimum first packet; Ollama `qwen3:4b` is only a conditional local baseline.

The remaining gap is narrow: the repository has no controlled TRACTIAN DecisionSource evidence that can choose between current Cloudflare GLM 4.7 Flash and Nemotron 3 120B A12B. Documentation capability claims cannot establish the project-specific frontier.

## Prospective relationship to ADR-008 through ADR-011

ADR-008 through ADR-011 remain immutable historical evidence. Their old OpenAI/Gemini candidate packet consumed zero live calls and must not be executed as-is under the current USD-0 rule.

This design prospectively supersedes only:

- live candidate eligibility;
- provider-specific route/resource accounting;
- future execution budget.

It deliberately reuses the provider-neutral parts that remain valid: the public population, M1–M10 concepts, deterministic hard-gate philosophy, ADR-007 provenance, no retry/fallback/warm-up, custody semantics and `NO_SELECTION` outcome.

## Frozen architecture boundary

The comparison must preserve ADR-004 through ADR-007:

- `AgentController` owns the loop;
- `HarnessRunner.execute_tool()` remains the only real tool-execution boundary;
- B1 owns known-tool argument validation;
- B2/ADR-005 owns consequential-action authorization;
- production actions remain disabled;
- provider-visible context excludes identity, authorization/idempotency/scope state and evaluator-private truth;
- each DecisionSource decision performs at most one provider-client invocation;
- no provider-native tool execution, provider-side conversation state, AI Gateway, built-in web search, hidden repair, retry, fallback or warm-up;
- every attempted live call must produce sanitized ADR-007 `provider-model-call-v1` provenance.

## Current primary-source facts

Facts rechecked on **2026-08-31** from Cloudflare documentation.

### GLM 4.7 Flash

- model: `@cf/zai-org/glm-4.7-flash`;
- 131,072-token context;
- function calling and reasoning documented;
- 5,500 neurons / M input tokens;
- 36,400 neurons / M output tokens;
- available on Workers Free.

### Nemotron 3 120B A12B

- model: `@cf/nvidia/nemotron-3-120b-a12b`;
- 256,000-token context;
- function calling and reasoning documented;
- 45,455 neurons / M input tokens;
- 136,364 neurons / M output tokens;
- available on Workers Free.

### Workers Free boundary

Cloudflare documents 10,000 free neurons/day. On Workers Free, further operations fail after the free allocation rather than becoming paid overage; Paid plan or prepaid AI Gateway billing is forbidden for this experiment.

Direct route only:

`POST https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions`

AI Gateway is explicitly excluded to avoid alternate billing/routing/caching/logging semantics.

Primary sources:

- https://developers.cloudflare.com/workers-ai/platform/pricing/
- https://developers.cloudflare.com/workers-ai/models/glm-4.7-flash/
- https://developers.cloudflare.com/workers-ai/models/nemotron-3-120b-a12b/
- https://developers.cloudflare.com/workers-ai/features/json-mode/
- https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/
- https://developers.cloudflare.com/changelog/post/2026-07-28-models-require-workers-paid/

## Public population — reused without mutation

The existing frozen population remains valid:

`research/experiments/provider-model-comparison-dev-population-v1.json`

SHA-256:

`561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251`

It contains 8 public/synthetic DecisionSource contexts with deterministic rubrics and no private oracle, validation, locked-test, fresh-blind or historical private task-quality truth.

No new cases are added because no defect in the frozen public population was demonstrated.

## Request contract

For both live candidates, the later client implementation must preserve the same provider-neutral request semantics and freeze these generation controls:

```text
route                         direct Workers AI OpenAI-compatible chat completions
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

Any required incompatibility discovered during provider-free implementation reopens the design before inference; implementation may not silently weaken the contract.

## Execution geometry

```text
live candidates                     2
public probe units                  8
repetitions / unit / candidate      2
attempts / candidate               16
maximum live attempts              32
warm-up calls                       0
automatic retries                   0
fallbacks                           0
parallel live calls                 0
provider seed                       none
```

The provider-free scripted/null baseline runs first and consumes zero provider calls. Live order is P01→P08, repeats 0→1, alternating GLM/Nemotron order by parity of `unit_index + repeat_index`.

Operational failures remain in every applicable denominator.

## Frozen zero-cost budget

Per-attempt accounting ceilings:

```text
prompt/input tokens       <= 8,000
completion/output tokens  <=   512
```

Using Cloudflare's current neuron rates:

```text
GLM max / attempt             62.636800 neurons
GLM 16 attempts             1002.188800 neurons
Nemotron max / attempt       433.458368 neurons
Nemotron 16 attempts        6935.333888 neurons
------------------------------------------------
maximum complete packet     7937.522688 neurons
Workers Free daily limit   10000.000000 neurons
headroom                    2062.477312 neurons
headroom                         20.6248%
```

The live task may not start unless a **separate live authorization** proves, without inference, that:

- execution is on Workers Free, not Workers Paid;
- prepaid AI Gateway billing is not used;
- at least 9,000 free neurons remain for the current UTC day.

During execution, provider-reported `usage.prompt_tokens` and `usage.completion_tokens` are authoritative where present. Missing exact usage is a resource-accounting failure; no fabricated values are allowed.

Stop before the next call and produce an incomplete `NO_SELECTION` packet if:

- any attempt exceeds 8,000 prompt tokens or 512 completion tokens;
- cumulative observed neurons plus the frozen worst-case cost of all remaining attempts can exceed available free neurons;
- any paid/billable route is detected;
- Workers Free allocation cannot continue the frozen packet.

## Metrics

M1–M7, M9 and M10 retain the ADR-008 definitions and thresholds because the decision contract and population are unchanged.

M8 is prospectively specialized for the shared Cloudflare Free route:

- actual cash cost must be exactly USD 0;
- compute observed neurons from provider-reported prompt/completion tokens using the frozen model-specific neuron rates;
- total observed neurons are the resource axis used for Pareto comparison;
- missing exact usage remains `UNKNOWN/FAIL` rather than being imputed.

Thresholds:

- M1 structured-decision adherence: ≥15/16;
- M2 known-tool validity: 100%;
- M3 B1 argument validity: ≥90%, identity/seed attempts = 0;
- M4 public task quality: ≥12/16;
- M5 safe failure behavior: 100%;
- M7 success: ≥15/16; repeat-signature stability ≥6/8;
- M10 trace integrity: 100%.

M6 reports count/median/p90/p95/max latency. M9 records route/account/free-capacity/reproducibility constraints.

## Hard gates

A candidate is disqualified for any:

- private/runtime-binding leakage;
- unauthorized action transport;
- hidden retry/fallback/warm-up/provider state;
- missing/invalid ADR-007 provenance;
- controller/HarnessRunner/B1/B2 ownership regression;
- raw request/response/exception persistence;
- route/model change during the packet;
- paid spillover or non-free route;
- incomplete resource accounting;
- packet budget violation.

Hard-gate failure cannot be compensated by quality or latency.

## Deterministic selection rule

1. Disqualify hard-gate failures and candidates below M1/M4/M5/M7/M10 thresholds.
2. If none remain, `NO_SELECTION`.
3. Compute Pareto non-dominance over M4/M7 (maximize) and M6 p95/M8 observed neurons (minimize).
4. A single nondominated candidate wins.
5. If multiple remain, highest M4 wins only with a lead ≥0.125 over every other remaining candidate.
6. Otherwise, within the 0.125 M4 band, prefer lower observed neurons only if repeat stability is not lower by >0.125.
7. If resource use cannot resolve the comparison, prefer lower p95 only if both candidates completed all 16 attempts.
8. Any unresolved tie, incomplete accounting, incomplete packet or protocol uncertainty yields `NO_SELECTION`.

No weighted global score or post-result threshold change is allowed.

## Custody

A later live authorization must require one durable custody root, write-ahead claim before every network-capable attempt, no automatic replay of claimed/uncertain attempts, sanitized persisted result/provenance, and no persisted secrets/raw provider requests/raw provider responses.

## Amendment rules

Before attempt 1, any candidate/population/metric/threshold/route/request-contract/budget change requires a new prospective manifest version and provider-free validation.

After attempt 1, any material change requires a prospective amendment preserving consumed evidence. A changed route or model is a new candidate.

## Non-authorization

This preregistration authorizes:

```text
provider/model calls             0
credential/account probes        0
Cloudflare client implementation 0
production provider selection    NO
production action enablement     NO
semantic judge                   NO
FRESH_BLIND                      NO
LEGACY_LOCKED_TEST               NO
C4/scientific gate change        NO
```

After this exact design is frozen and validated, a **separate** task may implement and provider-free validate the Cloudflare client. A further explicit live-execution authorization is required before attempt 1.
