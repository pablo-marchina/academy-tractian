# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 00:37 BRT  
**Canonical main basis:** `bde8ff21d7a6c91c970b397d760d94d3f4ac26c3`  
**Scientific gate:** `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`  
**Product decision state:** ADR-008 comparison design frozen; live comparison not authorized  
**Provider/model calls authorized now:** `0`  
**Production provider/model selected:** `NO`  
**Production mutating actions:** `DISABLED`

This file is the canonical short-horizon execution plan. It does not authorize a scientific gate or provider/model call by itself.

## Track A — close the current scientific reporting gate

Current blocker: exact original evaluator-side deterministic score artifact is still unavailable to the reporting runner.

Required identity:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

Do not reconstruct, rescore or replace it.

When the exact bytes are provisioned:

1. verify SHA-256, byte size, schema and 144-row / 36-parent × 4-arm geometry;
2. run only the existing reporting-only runner over frozen score rows + public/frozen classifications;
3. produce per-group, `investigate` / `execute` / `contextualize`, safety/failure-family and operational-failure summaries with explicit denominators;
4. independently validate classifications, denominators and aggregate reconstruction;
5. freeze the reporting result/provenance;
6. reconcile canonical status and advance only to the next gate explicitly authorized by that freeze.

Still forbidden on Track A: candidate regeneration, rescoring, provider calls, survivor/PREFERRED before reporting freeze, semantic evaluation, FRESH_BLIND and LEGACY_LOCKED_TEST.

## Track B — prepare the separately governed live provider comparison

ADR-008 now freezes the exact **design**, not its execution.

Frozen future comparison inputs:

```text
baseline        baseline_scripted_null_v1
quality route   openai / gpt-5.6-sol / openai.responses.v1.standard
cost route      google / gemini-3.7-flash / google.interactions.v1beta.stateless
public probes   8
repetitions     2 per probe/candidate
live candidates 2
future max calls 32
warm-ups        0
retries         0
fallbacks       0
parallel calls  false
```

Frozen public population SHA-256:

`561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251`

Frozen design/decision records:

- `research/experiments/provider-model-comparison-design-manifest-v1.json`;
- `research/experiments/provider-model-comparison-dev-population-v1.json`;
- `research/provider-model-comparison-design-2026-08-28.md`;
- `docs/adr/008-provider-model-comparison-design-2026-08-28.md`.

### Next P0 product task

Open a focused Class C task for **live-comparison authorization and provider-client readiness**.

That task should, while still provider-free initially:

1. implement the minimum OpenAI and Google `ProviderDecisionClient` adapters behind ADR-006 without changing `ProductionRuntime` or controller ownership;
2. pin exact HTTP/API request/response translation and structured-output schemas for the frozen route IDs;
3. prove one invocation per `decide()`, zero retry, zero fallback and ADR-007 sanitized provenance with deterministic fake transports;
4. prove identity/seed/action-authorization/private evaluator state remain absent from provider payloads;
5. prove provider-specific errors map to the existing fail-closed `DECISION_SOURCE_FAILURE` path;
6. freeze account/credential custody and usage-accounting procedure **without probing credentials yet**;
7. freeze exact execution runner/result schema for the 32-call packet and deterministic M1–M10 computation;
8. add an independent validator for the live result packet and `NO_SELECTION` decision rule;
9. request explicit live-call authorization only after all provider-free client/runner/validator CI is green.

A future authorization must explicitly state the call budget and credential/account scope. ADR-008 alone authorizes **zero** calls.

## After a live comparison is separately authorized

Only then:

1. verify frozen model/route identities and approved account/custody without changing the design;
2. execute the local baseline first;
3. execute at most the frozen 32 live calls, no warm-up/retry/fallback;
4. preserve every operational failure in denominators;
5. independently validate M1–M10, hard gates, usage/cost and ADR-007 provenance;
6. apply the deterministic selection rule exactly;
7. freeze one of:
   - a selected live candidate, or
   - `NO_SELECTION`;
8. reconcile the canonical state before using any candidate as the production `DecisionSource`.

Do not infer a winner from provider documentation, historical C4 serving-route evidence or incomplete live packets.

## Parallel safe P0/P1 work

The following can continue without contaminating either gate:

- reliability/failure-continuity tests using fake/scripted clients;
- customer-safe response shaping and EV-011 coverage without semantic/model judges;
- observability/redaction/trace storage design;
- deployment/reproducibility/runbook work that does not freeze a provider-specific topology prematurely;
- trusted action authorization/scope/confirmation/idempotency-source design while actions remain globally disabled;
- real supplied TRACTIAN API contract/regression coverage;
- final demo scenario inventory and evidence mapping, without executing blocked scientific/private partitions.

## Deferred unless evidence creates a requirement

Do not spend the critical path on:

- RAG/vector DB/reranking;
- persistent memory;
- MCP;
- multi-agent topology;
- framework-owned model/tool loop;
- rich UI;
- action enablement;
- semantic judge architecture;
- speculative provider fallback/routing.

LangGraph remains the first qualified orchestration upgrade path only if durable cross-process state/checkpoint/HITL becomes a demonstrated requirement.

## Critical path

```text
SCIENTIFIC
frozen scoring
→ frozen bootstrap
→ frozen LOGO
→ REQUIRED_PER_GROUP_AND_SLICE_REPORTING        [current / blocked on exact artifact]
→ survivor/no-survivor                         [only after reporting freeze]
→ semantic child gate                          [only if explicitly opened]
→ candidate/evaluator freeze
→ independent validation

PRODUCT
ADR-004 controller
→ production runtime
→ deterministic evaluator
→ ADR-005 action safety
→ ADR-006 provider-neutral DecisionSource
→ ADR-007 model-call provenance + preregistration
→ ADR-008 exact comparison design              [complete]
→ provider-client readiness + live authorization [next]
→ separately authorized 32-call comparison
→ provider/model selection OR NO_SELECTION
→ integrated reliability/security/observability
→ final architecture freeze when evidence is sufficient
→ P0/P1 regression + real-path demonstration
→ final delivery
```

## Deadline discipline

```text
2026-08-27 → 2026-08-29   close scientific path where artifact custody permits
2026-08-30 → 2026-09-02   close remaining material product decisions + core
2026-09-03 → 2026-09-05   reliability/security/integrated evidence
2026-09-06 → 2026-09-07   documentation + final demo
2026-09-08                delivery
```

After 2026-09-05, default against P2 additions unless they fix a demonstrated delivery blocker.
