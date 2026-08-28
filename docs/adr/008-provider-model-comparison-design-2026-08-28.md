# ADR-008 — Production provider/model comparison design

**Status:** ACCEPTED  
**Decision state:** `FROZEN_FOR_LIVE_COMPARISON_AUTHORIZATION_DESIGN`  
**Date:** 2026-08-28  
**Issue:** #32  
**Scientific state changed:** NO  
**Provider/model calls authorized by this ADR:** 0  
**Production provider/model selected:** NO  
**Production actions enabled:** NO

## 1. Decision question

What exact, current and reproducible comparison design should govern a later production provider/model selection behind the frozen ADR-006 `ProviderDecisionSource`, without using private evaluator truth, changing the C4 scientific gate or making any live provider request during the design phase?

## 2. Decision

Freeze the exact provider-free design validated on implementation head:

`0dc3753f7beb9753b762221b66efb1664dec7a66`

The frozen design contains exactly three candidate identities:

1. `baseline_scripted_null_v1` — provider-free deterministic lower bound, ineligible for production selection;
2. `openai_gpt_5_6_sol_responses_standard` — quality-frontier hosted candidate using model `gpt-5.6-sol` through the application-owned standard Responses API route;
3. `google_gemini_3_7_flash_interactions_stateless` — lower-cost hosted candidate using model `gemini-3.7-flash` through a stateless Interactions API route.

This ADR freezes **eligibility and comparison protocol only**. It does not rank or select either live candidate. Documentation claims are not production-selection evidence.

## 3. Frozen artifacts

The following already-validated bytes are frozen by reference rather than rewritten after green CI:

| Artifact | Identity |
|---|---|
| machine-readable design | `research/experiments/provider-model-comparison-design-manifest-v1.json` — Git blob `9c3d0901414445bd4de557d5ef1d2f68a15c883b` |
| public DEV population | `research/experiments/provider-model-comparison-dev-population-v1.json` — Git blob `abd6a7d973a8779f425c3607d963e29f15db09e5`; file SHA-256 `561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251` |
| human-readable protocol | `research/provider-model-comparison-design-2026-08-28.md` — Git blob `c43b11d3c25a209f20e40ee90007a9e1e504ae5d` |
| provider-free validator | `scripts/research/validate_provider_model_comparison_design.py` — Git blob `4f6bc39b44e8eb27987f7312335dfe35a65b146a` |

The manifest status remains `DESIGN_CANDIDATE_PROVIDER_FREE_ONLY` inside those immutable validated bytes. This ADR is the authority that promotes that exact candidate design to the scoped frozen decision state above; mutating the already-tested manifest only to rewrite its status would weaken provenance.

## 4. Public development population decision

Do not reuse historical E9/E10/E14 `real_task_quality` as public production-provider selection truth.

The historical six-call DEV pattern used three DEV groups × two repeats, but real task-quality scoring depended on evaluator-side private oracle material. The public historical runner can also fall back to a proxy packet when an agent-visible case file is absent. Those facts make the old measurement useful as research history, not as a clean public M4 ground truth for this new production-provider comparison.

Freeze instead eight prospective synthetic DecisionSource probes derived only from public delivery requirements and the canonical 18-operation ToolSpec. They cover contextualization, investigation, data-quality-first behavior, knowledge use, clarification, escalation, unavailable evidence and action-policy containment.

M4 is therefore explicitly **public decision-task quality**. It is not C4 scientific evidence, semantic response-quality evidence or a substitute for the final integrated demonstration.

## 5. Execution geometry

A later separately authorized live comparison is bounded to:

```text
live candidates                     2
public probe units                  8
repetitions per unit/candidate      2
maximum live provider calls        32
hidden warm-up calls                0
automatic retries                   0
provider/model fallbacks            0
provider seed forwarded             NO
parallel live execution             NO
```

Operational failures remain in all applicable denominators.

The deterministic order is P01 through P08, repeats 0 then 1, with candidate order alternated by unit/repeat parity. The provider-free baseline executes first and consumes zero provider requests.

## 6. Hard gates

The later comparison must disqualify, rather than score-compensate, any candidate with:

- private/evaluator/runtime-binding leakage;
- unauthorized mutating-action transport;
- hidden retry, fallback or warm-up;
- invalid/missing ADR-007 model-call provenance;
- provider/framework ownership replacing ADR-004 controller or HarnessRunner execution ownership;
- raw request, raw response or exception-text recording in trace provenance;
- material model/route change during the frozen run.

ADR-004, ADR-005, ADR-006 and ADR-007 remain authoritative for their respective boundaries.

## 7. Frozen measurements and selection semantics

M1 through M10 are frozen in the machine-readable design before the first live call:

- structured-decision adherence;
- known-tool selection validity;
- canonical argument validity/B1 containment;
- public allowed-development task quality;
- safe failure behavior;
- latency;
- reliability and repeated-run stability;
- exact usage/resource/cost where observable;
- portability/operational constraints;
- trace integrity.

Hard-gate failures and minimum-threshold failures are disqualifying. Remaining live candidates are compared by Pareto non-dominance across quality/stability and latency/cost. The deterministic tie-breaking rules are frozen in the manifest and explicitly permit `NO_SELECTION` whenever evidence is incomplete, non-comparable or unresolved.

There is no weighted global score and no post-result threshold tuning.

## 8. Alternatives considered

### OpenAI Terra/Luna in the initial live set

Rejected for the minimum first comparison. They belong to the same current provider/model family and do not justify additional live calls before the Sol-versus-lower-cost cross-provider trade-off is measured. They may enter only through a prospective amendment before execution.

### Groq `openai/gpt-oss-120b`

Rejected from this exact comparison because current primary-source documentation does not provide the same strict Structured Outputs + tool-use fit required by the frozen adapter contract. The protocol is not weakened to accommodate a cheaper route.

### Historical E9/E10/E14 private DEV task score

Rejected for M4 because it would couple this production-provider design to evaluator-private ground truth and because the current public input population is not a clean reconstruction of the historical private-scoring input.

### No task-quality metric

Rejected because provider selection based only on schema adherence, latency and cost would not establish useful decision behavior. The new prospective public probes provide a narrower but legitimate production decision-contract measure without opening semantic/private evaluation.

## 9. Validation evidence

First implementation head `617ed300d5d4fc7aa13f0e1ada9564b79a2841ce` exposed a validator path-normalization defect in `production-runtime` run #17: the frozen repository-relative path was compared with the checkout's absolute filesystem path. The failure was preserved and fixed without force-push; no candidate, population, metric, threshold or authorization was changed.

Corrected implementation head:

`0dc3753f7beb9753b762221b66efb1664dec7a66`

Validation on that exact head:

- `provider-model-comparison-design` run #2 / Actions run `33139265212`: SUCCESS;
- `production-runtime` run #18 / Actions run `33139265204`: SUCCESS, including ADR-004 regression;
- all 12 workflows associated with the head: SUCCESS;
- provider/model requests executed by the comparison design: 0;
- provider credentials required/read by the validator: 0; the validator fails closed if a provider credential environment variable is present.

## 10. Non-authorization

This ADR does **not** authorize:

- any real OpenAI, Google, Groq, Anthropic or other provider/model request;
- API-key or account-capability probing;
- production provider/model selection;
- production action enablement;
- semantic judge evaluation;
- C4 score mutation/rescoring;
- survivor/PREFERRED inference;
- FRESH_BLIND or LEGACY_LOCKED_TEST access;
- global final-architecture freeze;
- production-readiness claims.

The scientific gate remains `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`.

## 11. Reversal / amendment triggers

A new prospective design amendment is required before live execution if any of the following materially changes:

- a frozen provider model or serving route is deprecated, unavailable or changes required structured-output/tool-use semantics;
- official pricing/resource basis changes enough to alter the intended Pareto comparison;
- the public probe population is found ambiguous, leaky or invalid;
- ADR-004 through ADR-007 contract ownership changes;
- a newly available candidate provides a materially distinct credible Pareto trade-off worth the added call budget;
- the planned 32-call packet cannot be executed without retry/fallback behavior that is currently forbidden.

After the first live call, any material protocol change must preserve already-consumed evidence and be recorded prospectively; it cannot silently rewrite or pool the run.

## 12. Next authorized product step

The next admissible product task is a **separate governed live-comparison authorization packet**. It may implement provider-specific clients and validate them provider-free, but credentials/account probing and the first real inference request remain prohibited until that future task explicitly authorizes them.

Until then:

```text
provider/model calls authorized now       0
production provider/model selected        NO
production mutating actions enabled       NO
scientific gate changed                   NO
```
