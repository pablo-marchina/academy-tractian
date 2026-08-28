# Decision Revalidation Addendum 003 — Zero-Cost Provider Fact Refresh

**Date:** 2026-08-28  
**Status:** ACCEPTED FOR FACT-REFRESH SCOPE  
**Changes scientific state:** no  
**Provider/model inference calls:** 0  
**Credential/account probes:** 0

## Decision question

After consolidating historical provider evidence, what current first-party facts materially change the USD-0 provider/model feasible set, and is broad provider discovery still necessary before any prospective live comparison?

## Evidence basis

This addendum reads the current external-fact refresh together with the existing repository evidence:

- E8 zero-cost candidate discovery and Groq operational run;
- E14 GPT-OSS operational/negative quality evidence;
- P12-C2/C3 capacity failures and later serving work;
- ADR-001→003 provider-serving evidence;
- ADR-006→011 provider-neutral production comparison infrastructure;
- `MATERIAL-DECISION-HISTORICAL-EVIDENCE-AUDIT-2026-08-28.md`.

No inference output, credential probe, private evaluator material or scientific rescore is introduced.

## Decision

Broad zero-cost provider discovery is **complete enough for the current decision scope**. The project should not continue adding providers merely to enlarge the candidate list.

The current primary hosted feasible set is:

1. `gemini-3.7-flash` — `CONDITIONAL_ELIGIBLE`, pending exact Free Tier data-use/privacy acceptance;
2. Cloudflare Workers AI Free — `ELIGIBLE`, but the future packet must pin only the minimum materially distinct representative model(s);
3. Groq Free — `ELIGIBLE_WITH_HISTORICAL_PENALTY`, to be treated as historical/control evidence rather than a new frontier from scratch.

Conditional baselines:

- Ollama local, if no-inference hardware/model feasibility is realistic;
- a fixed OpenRouter `:free` route only if exact model/provider behavior and fallback suppression can be pinned.

Screened out of the primary final hosted production comparison:

- NVIDIA free hosted NIM: development/testing path, not free hosted production;
- Cerebras Free Trial: bounded trial, with historical project evidence already present;
- Hugging Face routed free credits: too small for default production selection absent an ultra-low-volume proof;
- Groq Qwen 3.8 Preview: preview/evaluation lifecycle.

## Material changes from historical planning

- ADR-008 already used `gemini-3.7-flash`; this refresh does **not** invent a new Gemini candidate. It confirms the current GA/free state and introduces an explicit Free Tier data-use gate.
- Cloudflare Workers AI Free becomes a materially credible new candidate because the Free allocation is bounded/fail-closed and current agentic models expose the needed API contract primitives.
- Groq's current catalog changed, but historical GPT-OSS quality/capacity failures remain binding.
- OpenRouter's generic `openrouter/free` router is excluded from controlled evaluation because model identity is dynamic and provider fallback may hide upstream failure.

## What remains unresolved

D01 stays `PARTIALLY_ASSESSED`; its gap is narrower:

1. Gemini payload data-use/privacy eligibility;
2. minimal Cloudflare representative selection;
3. Groq live-control vs historical-only role;
4. optional Ollama hardware/model feasibility;
5. only then: whether a minimal new live provider comparison remains necessary.

These are planning/factual decisions. **No new benchmark is authorized by this addendum.**

## Hard boundaries preserved

- USD 0 external-service hard constraint;
- zero hidden paid spillover;
- zero provider calls until a prospective packet is separately frozen;
- zero credential/account probing merely to verify connection state;
- no provider-native TRACTIAN execution outside `HarnessRunner.execute_tool()`;
- existing failed/negative Groq evidence cannot be erased by a rerun;
- C4 remains scientifically separate and unchanged.

## Reversal triggers

Reopen this factual screening if a primary candidate changes lifecycle/free-tier status, a new materially distinct zero-cost production-capable provider emerges, the Free Tier data-use terms change, or a selected candidate loses the required structured decision contract.