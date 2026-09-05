# Hosted provider feasibility → EDD promotion protocol

**Status:** preregistered P0 protocol  
**Date:** 2026-09-04  
**Scope:** final hosted-only Academy × TRACTIAN product  
**Hard constraints:** required local components = 0; external cash cost required by the selected path = USD 0

## Decision question

Which hosted provider/model candidate is admissible for controlled live evaluation, has enough verified free capacity for the required experiment and final product demonstration, and is then justified for promotion by the existing eval-driven quality gate?

A candidate must pass every phase below. No weighted score can compensate for a failed hard constraint.

## Phase F0 — code-owned identity

Every candidate is identified by an exact tuple:

`provider_id + model_id + route_id + adapter_version + client_version`

Changing a model or serving route changes runtime provenance/config hash and requires new evidence. Provider name alone is not a candidate identity.

Current controlled set:

- `openai:gpt-5.6-sol`;
- `google:gemini-3.7-flash`;
- `google:gemini-3.8-flash`;
- `groq:openai/gpt-oss-120b`.

## Phase F1 — static pilot admission

The deterministic feasibility gate requires:

- hosted service;
- zero required local components;
- GA model and GA provider API/product boundary;
- structured-output support compatible with the provider-neutral decision contract;
- verified zero-cost execution path;
- external evidence no older than seven days.

Unknown is not pass. Account-specific facts that have not been verified remain `unknown`.

The F1 policy intentionally sets daily capacity minima to zero. F1 only answers whether spending controlled free quota on a live pilot is justified. It does **not** establish production capacity and cannot promote a provider.

Current evidence snapshot is bound to `research/provider-feasibility-source-manifest-2026-09-04.json` and executed by `tests/test_provider_feasibility_research_snapshot.py`.

## Phase F2 — live capacity characterization

Before quality promotion, execute a bounded pilot for every F1-admitted candidate using the exact runtime decision adapter and a fixed, public, non-private subset of scenarios.

Record per agent run:

- provider client invocations;
- input tokens;
- output tokens;
- reasoning/thought tokens where exposed;
- total tokens;
- end-to-end provider latency;
- 429/rate-limit responses;
- malformed/invalid structured responses;
- terminal outcome;
- number of tool turns.

Do not infer account capacity from public generic documentation when the provider states that limits are account/project-specific. Capture the effective account/project quota before the full experiment.

### Capacity threshold derivation

The final free-capacity threshold must be derived after the pilot and before the full benchmark from frozen pilot statistics, not selected after seeing benchmark quality.

Let:

- `S` = required scenario count from the promotion policy;
- `R` = required repeated runs per scenario;
- `C95` = pilot p95 provider calls per agent run;
- `T95` = pilot p95 total provider tokens per agent run;
- `D` = calendar days allocated to execute the benchmark with safety margin;
- `M` = preregistered multiplicative reserve factor (`M > 1`) for reruns caused by infrastructure failures only; model-quality failures are not retried into a better score.

Then preregister:

`required_requests_per_day = ceil(S × R × C95 × M / D)`

`required_tokens_per_day = ceil(S × R × T95 × M / D)`

A provider whose verified free capacity is below either threshold is `INELIGIBLE_FOR_FULL_BENCHMARK`, independent of model quality.

The existing promotion policy currently requires at least 50 scenarios and 3 repeats. These values remain owned by the EDD promotion policy; this protocol does not weaken them.

## Phase F3 — paired quality EDD

Only F2-capable candidates enter the full provider benchmark.

Use the existing provider benchmark assembly and promotion gate:

- identical scenario/repeat coverage across candidates;
- independent group IDs preserved for paired bootstrap;
- complete pairwise comparison matrix;
- deterministic hard safety gates;
- no composite score that trades correctness/safety for latency or price;
- `NO_SELECTION` when there is no unique evidence-backed winner.

Latency and token efficiency are optimization metrics only after correctness/safety constraints pass.

## Phase F4 — human semantic calibration

No provider can be promoted without the existing held-out human calibration requirements, including minimum case count, human agreement, operational-conclusion accuracy and lower confidence-bound gates.

Human labels remain unavailable to the runtime/model prompt.

## Phase F5 — production configuration

A production environment may select only a candidate that has:

1. current F1 feasibility evidence;
2. F2 verified capacity for the intended workload/demo window;
3. F3 EDD promotion evidence;
4. F4 human calibration evidence;
5. exact candidate identity matching the deployed runtime config hash.

Deployment configuration itself is never model-selection evidence.

## Current source findings — not a provider winner

At the 2026-09-04 snapshot:

- GPT-5.6 Sol has structured outputs and published metered API pricing. A conditional OpenAI daily-free-token program exists for eligible organizations that opt into qualifying traffic, so zero-cost availability for this project remains account-level `unknown` until verified.
- Gemini 3.7 Flash and Gemini 3.8 Flash are stable, support structured outputs, and have free-tier token pricing. Google documents active rate limits as project/account-specific; their usable free daily capacity therefore remains unverified until measured for the project.
- Groq `openai/gpt-oss-120b` supports JSON Schema structured outputs and is listed in the Free Plan with 1,000 requests/day and 200,000 tokens/day. These published limits justify F1 admission but do not yet prove they are sufficient for the final 50 × 3 EDD workload.

The current F1 outcome is therefore a **pilot frontier**, not a final selection.

## Evidence hygiene

- External facts are timestamped and source-manifest-bound.
- Feasibility evidence expires instead of being silently refreshed.
- Historical provider experiments remain historical and do not automatically certify a new candidate identity.
- No raw credentials, prompts containing private evaluator truth, or raw provider responses enter feasibility artifacts.
- Any newly discovered hard-constraint violation reopens the affected decision.
