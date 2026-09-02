# Final Delivery Output Inventory

**Checkpoint:** 2026-09-02  
**Source alignment:** `docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md`

This inventory is the explicit final-output checklist for the TRACTIAN delivery. Items may be marked complete only when the artifact/executable path exists and its acceptance evidence is recorded.

## Executable/product outputs

- [ ] O1 Functional industrial agent runtime demonstrated on declared support use cases.
- [x] O2 Typed TRACTIAN integration: canonical tool registry, schemas, HTTP transport and safety boundary.
- [x] O3 Evaluation framework: scenario runner, evaluators, trace validation, failure/stability campaigns.
- [ ] O4 Final governed experiment package including D01 and D02 disposition.
- [ ] O5 Realtime Observability Control Room.
- [ ] O6 Architecture Explorer with selected-run path highlighting.
- [ ] O7 Per-run Output Lineage / Explain This Run.
- [ ] O8 Schema-driven Dynamic Data Explorer.
- [ ] O9 Realtime production telemetry stream with persistence/reconnect/catch-up.
- [ ] O10 Final technical documentation/reproduction package.

## Frontend screens

- [ ] Mission Control
- [ ] Live Runs
- [ ] Run Explorer
- [ ] Trace Timeline / Waterfall
- [ ] Trace Graph
- [ ] Tools & Policy
- [ ] Quality & Providers
- [ ] Dynamic Data Explorer
- [ ] Architecture Explorer
- [ ] Explain This Run / Output Lineage

## Required demonstrated behavior

- [ ] Contextualize / orient.
- [ ] Investigate through typed tools.
- [ ] Ask clarification.
- [ ] Abstain safely on unavailable/insufficient evidence.
- [ ] Escalate with structured human handoff.
- [ ] Contain invalid/unauthorized/high-impact action.
- [ ] Demonstrate controlled authorized action where supplied/test authorization permits.
- [ ] Handle complete API result.
- [ ] Handle partial API result.
- [ ] Handle inconclusive API result.
- [ ] Handle conflicting sources.
- [ ] Handle unavailable/provider/tool failure.
- [ ] Show repeat/stability evidence.

## Realtime acceptance

- [ ] Genuine runtime events update UI without page reload.
- [ ] Trace graph/timeline grows only from emitted runtime events.
- [ ] SSE connection state shown explicitly.
- [ ] Reconnect performs persisted cursor catch-up.
- [ ] Duplicate event delivery is idempotent in UI.
- [ ] Slow/disconnected browser cannot block runtime.
- [ ] Terminal UI state appears only after genuine terminal evidence.

## Safe observability acceptance

- [ ] No identity binding in browser payloads.
- [ ] No user id/seed in browser payloads.
- [ ] No credentials/account id/auth headers in browser payloads.
- [ ] No raw provider request/response material in browser payloads.
- [ ] No forbidden raw tool/observation bodies in browser payloads.
- [ ] No hidden chain-of-thought.
- [ ] No evaluator-private gold/oracle/truth available at runtime/front boundary.
- [ ] Runtime-time and evaluator-time information visually separated.

## Experimental outputs

- [x] Provider-free baseline evidence.
- [x] D01 frozen live comparison: 32/32 attempts, USD0, NO_SELECTION.
- [x] D01 post-run censoring diagnosis: 24/24 CLIENT_FAILURE at exact 512-token cap.
- [ ] D02 governed 1024-cap result or explicit bounded blocker.
- [ ] Final provider decision or NO_SELECTION justification.
- [ ] Final architecture materiality decision.
- [ ] Final limitations/risk statement.

## Documentation outputs

- [x] TAPI stack/framework/technique/output coverage matrix.
- [ ] README declares combined Track A + Track B scope.
- [ ] README lists exact final stack and frozen dependency versions.
- [ ] README records exact model/provider/configuration.
- [ ] README explains agent techniques independently from libraries.
- [ ] README describes experimental hypotheses/methods/results.
- [ ] README records limitations/risks and consciously rejected optional frameworks.
- [ ] Clean installation/run instructions include backend + frontend.
- [ ] Final architecture diagram matches implementation manifest.
- [ ] Final demo/reproduction runbook includes provider-independent fallback.

## Testing/reproduction outputs

- [x] pytest runtime/evaluation regression.
- [ ] Observability sanitizer/API contract tests.
- [ ] Realtime ordering/reconnect/idempotency tests.
- [ ] Frontend Vitest/component tests.
- [ ] Playwright end-to-end tests.
- [ ] Frontend production build gate.
- [ ] Clean-checkout backend + frontend reproduction.
- [ ] Presentation viewport/demo rehearsal.

## Freeze condition

Hard visual + feature freeze cannot occur until all remaining unchecked P0 items required by issues #114, #119, #121, #122, #123, #124 and #125 are either passing or explicitly documented as a non-P0 bounded limitation.
