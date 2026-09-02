# ADR-027 — Cloudflare D02 fresh-reset live authorization

**Date:** 2026-09-02  
**Status:** ACCEPTED_PROVIDER_FREE / LIVE_ONLY_WITH_FRESH_RECEIPT

## Context

ADR-026 froze D02 as the prospective completion-budget experiment: same provider, models, public population, prompt/schema, evaluator and single-agent architecture as D01, with only the completion cap changed from 512 to 1024 plus a sanitized failure subtype. The governed D02 executor subsequently established a worst-case packet bound of `9352.805376` Neurons, write-ahead custody, no replay and provider-free regression coverage.

D01 already executed during the 2026-09-02 UTC allocation window. Therefore no evidence captured in that same window may truthfully attest zero Workers AI use since reset. D02 implementation readiness must not be conflated with same-day live authorization.

## Decision

D02 live execution SHALL require a D02-specific fresh-reset receipt derived exclusively from an operator attestation that all of the following are true for the evidence UTC day:

1. the observation is after that day's 00:00 UTC Workers AI reset and no more than 600 seconds old;
2. Workers Free is active and Workers Paid is disabled;
3. no Workers AI call has occurred on the target account since that reset;
4. no automated/background process has consumed Workers AI since reset;
5. the account is exclusively reserved for the D02 packet until completion or abort;
6. the route is direct Workers AI, without AI Gateway or prepaid unified billing;
7. evidence capture used no provider inference, credential/account probe or external plan screenshot;
8. provider credentials are absent while evidence and receipt are created.

Those attestations derive exactly `10000.0` free Neurons. D02 intentionally does not accept partial same-day capacity, even if a separate source estimates more than the numerical minimum of `9352.805376`. This removes ambiguity around remaining-quota inference and leaves modeled headroom of `647.194624` Neurons.

## Frozen identities

The D02 authorization receipt pins:

- D02 plan SHA-256: `e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958`;
- ADR-026 Git blob: `c5d00a1668613cacd3b520cd241a8b969a262119`;
- D02 experiment protocol Git blob: `eda022821c4ffe08b28b80b814d0da28f84580f6`;
- D02 implementation module Git blob: `c6cc416c4201a30961861c852aaa746e6c5c9113`;
- governed D02 executor Git blob: `24baaa914765e90d85a4d6f265eb2d43cf769825`;
- fresh-reset authorization protocol Git blob: `8588284963b96970b997e6afa2bd1cbcc08ea012`.

The launcher additionally validates these identities from canonical Git objects, not worktree newline bytes.

## Receipt lifetime

Evidence expires after 600 seconds. A receipt expires after at most 300 seconds and never later than the evidence expiry. It is bound to a canonical hash of the intended custody root. A receipt for one custody root cannot authorize another.

Any UTC-day rollover invalidates the evidence and receipt.

## Credential boundary

Capture and receipt issuance fail closed if provider credentials are present in the process environment. The live launcher validates the D02 protocol, evidence, receipt, freshness, plan/source pins and custody binding **before** reading `CLOUDFLARE_API_TOKEN` or `CLOUDFLARE_ACCOUNT_ID`.

Credentials and account identifiers are never persisted to evidence, receipt, custody, ledger, result or canonical trace.

## Execution boundary

After authorization, the launcher may create the one-shot direct Workers AI transport and invoke only the governed D02 executor. There are:

- 0 warmups;
- 0 automatic retries;
- 0 provider fallbacks;
- 0 parallel live calls;
- at most 32 canonical attempts;
- no resume after a claimed or uncertain attempt;
- no raw provider material persistence.

The write-ahead ledger is authoritative for whether an attempt may have been consumed. If an outcome becomes uncertain after claim, blind rerun is forbidden.

## Current-day prohibition

This ADR's acceptance on 2026-09-02 does **not** authorize D02 in the 2026-09-02 UTC window because D01 already consumed Workers AI after that day's reset. The first possible real D02 run is a later UTC day for which the zero-use attestation is truthful and fresh.

## Architecture

No LangGraph, multi-agent, RAG, memory, MCP or adaptive-routing change is authorized. Architecture remains `NO_CHANGE` pending D02 evidence and issue #92's materiality rules.
