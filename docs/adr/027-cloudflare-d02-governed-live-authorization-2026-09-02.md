# ADR-027 — Cloudflare D02 governed live authorization

**Date:** 2026-09-02  
**Status:** ACCEPTED_PROVIDER_FREE / CURRENT_WINDOW_BLOCKED

## Context

D01 completed its governed 32-attempt Workers AI packet on the 2026-09-02 UTC allocation at USD 0 and recorded `2813.628464` Neurons. The prospective D02 contract in ADR-026 changes only the completion-token ceiling from 512 to 1024 and adds sanitized client-failure subtype evidence. Its derived 32-attempt worst-case resource requirement is `9352.805376` Neurons.

The maximum remaining allocation implied by the D01 accounting is therefore `7186.371536` Neurons, which is below D02's start gate. D02 cannot truthfully reuse the D01 zero-use attestation or run again in the current UTC allocation window.

## Decision

Adopt a distinct D02 authorization/custody path governed by:

`research/experiments/cloudflare-d02-live-authorization-protocol-v1.json`

The D02 path SHALL:

1. require a new same-UTC-day operator attestation captured only after a Workers AI daily reset;
2. require explicit attestation that no Workers AI calls and no automated/background Workers AI consumers have used the target account since that reset;
3. require Workers Free active, Workers Paid disabled, direct Workers AI routing, no AI Gateway and no prepaid unified billing route;
4. derive exactly `10000.0` free Neurons only from that explicit zero-use reset-window attestation, never from an account/quota probe;
5. require `>=9352.805376` free Neurons before attempt 1;
6. issue a D02-specific receipt lasting at most 300 seconds and never beyond the 600-second evidence lifetime or UTC day;
7. bind the receipt to the D02 plan, D02 protocol, ADR-026, D02 contract and custody root;
8. validate evidence and receipt before reading provider credentials in the execution entrypoint;
9. durably persist `CLAIMED` before each possible provider request and forbid replay/resume after a claimed or uncertain attempt;
10. preserve only sanitized attempt evidence and `failure_subtype`, never raw generated text, raw request/response, exception text, credential, token or account identifier;
11. preserve the D01 frozen artifacts and result byte-for-byte and never rescore D01;
12. keep the single-agent architecture, prompt/schema, provider/models, population, repeats, evaluator, tool surface, no-retry and no-fallback policies unchanged.

## Current-window block

For UTC day `2026-09-02`:

```text
Workers Free allocation              10000.000000
D01 observed Neurons consumed         2813.628464
maximum implied remaining             7186.371536
D02 worst-case packet                 9352.805376
D02 current-window eligibility        BLOCKED
```

The next possible reset is `2026-09-03T00:00:00Z` (`2026-09-02 21:00` in America/Sao_Paulo). That reset is only a necessary condition. A D02 run remains unauthorized until a fresh post-reset zero-use attestation and matching short-lived receipt are issued.

## Resource and call safety

D02 retains a hard USD 0 budget and forbids paid spillover. The executor recomputes the worst-case cost of every remaining canonical attempt before permitting the next claim. If observed usage plus remaining worst-case capacity would exceed the attested free allocation, execution stops before the next attempt.

Every attempt follows:

```text
resource gate -> durable CLAIMED -> at most one provider request -> usage/audit capture -> COMPLETED
```

An unexpected exception after `CLAIMED` produces `UNCERTAIN` and terminates the packet. No blind rerun or resume is allowed.

## Diagnostic boundary

D02 keeps the canonical trace's generic `CLIENT_FAILURE` semantics while the D02 custody ledger records a bounded sanitized subtype from `ProviderHttpClientError.code`, for example `CLOUDFLARE_FINISH_REASON_INVALID`. No provider output text is required or permitted for this diagnosis.

## Architecture materiality

D01 does not establish an architecture bottleneck. This ADR authorizes no LangGraph, multi-agent, RAG, persistent memory, MCP or adaptive-routing change. Issue #92 remains gated on measured evidence after the D02 completion-budget question is resolved.

## Authorization boundary

This ADR and its implementation work authorize **zero live provider calls now**. Live D02 execution is conditional on a future fresh reset-window attestation, a valid D02 receipt, sufficient derived free allocation, and provider-free CI remaining green.
