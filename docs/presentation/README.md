# Technical Presentation Pack — 5-minute video

**Last synchronized:** 2026-09-08 BRT  
**Purpose:** final technical presentation using the real hosted product.  
**Current state:** [`../ACTIVE-PROJECT-STATUS.md`](../ACTIVE-PROJECT-STATUS.md)  
**Provider state:** [`../PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](../PROVIDER-QUALIFICATION-STATUS-2026-09-08.md)

This pack is architecture-first, evidence-first and claim-bounded. It is not a business pitch and must not turn an unsuccessful provider experiment into a success claim.

## Use these files in order

1. [`EXACT-5-MIN-RECORDING-SCRIPT.md`](EXACT-5-MIN-RECORDING-SCRIPT.md)
2. [`05-MIN-TECHNICAL-SCREENPLAY.md`](05-MIN-TECHNICAL-SCREENPLAY.md)
3. [`SCREEN-SHOT-LIST.md`](SCREEN-SHOT-LIST.md)
4. [`ARCHITECTURE-OVERLAYS.md`](ARCHITECTURE-OVERLAYS.md)
5. [`RECORDING-CHECKLIST.md`](RECORDING-CHECKLIST.md)

If a nested script contains a provider claim inconsistent with the current provider-status document, the provider-status document wins.

## Current UI vocabulary

```text
Home        primary question entry
Result      selected-run outcome/evidence
Analyses    persisted history
Technical   Current analysis / Quality / Data / System / Actions / Studies
```

Do not revert to the superseded global Results / Evidence / Investigation / Engineering navigation in the recording.

## Recommended persisted production runs

Prefer already-persisted Release 0/V13 evidence during rehearsal instead of consuming provider quota:

- R310 spectrum investigation — `partial`, condition evidence + point drill-down;
- data-quality + RMS investigation — `complete`;
- bounded unavailable R420 case — requested asset absent from authorized fleet.

The R420 case is an authorized-inventory fail-closed example, not a generic API outage.

## Presentation thesis

```text
authenticated request
→ server-owned tenant context
→ provisional Release 0 DecisionSource
→ AgentController
→ HarnessRunner + canonical ToolSpec
→ typed remote TRACTIAN read
→ normalized evidence + RunTrace
→ terminal + response_mode
→ deterministic post-runtime evaluation
→ PostgreSQL durable projection
→ authenticated SSE / task-driven UI
```

## Provider/evaluation story — updated 2026-09-08

A strong final technical story is that the evaluation framework can **reject** an attractive provider configuration rather than merely score it.

Groq `openai/gpt-oss-120b` completed the frozen 85-attempt qualification and returned:

```text
NO_SELECTION
rubric pass       69/85 = 81.18%
reliability       70/85 = 82.35%
contract failures 9
repeat stability  11/17 = 64.71%
```

The important conclusion is not “Groq is bad”; it is:

> the current Groq GPT-OSS-120B serving configuration did not satisfy the project's unchanged structural/reliability gates, so it was not promoted.

Cloudflare GPT-OSS-120B was quota-blocked in non-scored preflight and then removed from the requested final path. Therefore do **not** present the Groq run as a completed Cloudflare-vs-Groq tournament.

Current follow-up research is causal:

```text
completion budget
vs structured-output strictness
vs reasoning effort
```

An observed failure returned HTTP 200 + `finish_reason=stop` + valid JSON but violated `ProviderDecisionPayload`, demonstrating that output budget alone is not the complete explanation.

## Non-negotiable claims

- Browser is not authority for tenant, role or permissions.
- Model does not directly execute network calls.
- `HarnessRunner` is the canonical tool execution boundary.
- Internal resource IDs must come from authorized structured evidence.
- `response_mode` communicates evidence completeness; it does not grant authority.
- Evaluation is post-runtime; private benchmark/gold truth is not given to the model.
- Release 0 exposes 13 reads and 5 proposal-only action operations; consequential external execution is disabled.
- Same-name RMS/spectrum calls can be legitimate asset→point drill-down.
- Production provider is provisional.
- **No final provider winner currently exists.**
- Groq GPT-OSS-120B 85/85 result is `NO_SELECTION`, not `PROMOTE`.
- Strict structured output is a challenger under investigation, not production behavior.
- A provider tournament/qualification alone never authorizes production promotion; Academy live E2E is still required.

## What this video is not

Do not spend the 5 minutes on every experiment, CSS, CI history or unpromoted framework. Mention the provider rejection only to demonstrate evaluation rigor, failure analysis and claim discipline.
