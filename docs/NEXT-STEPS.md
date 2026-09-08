# Superseded Compatibility Path — Next Steps

**Status:** SUPERSEDED  
**Canonical current plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Latest progress:** [`progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`](progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md)

This filename is retained so historical links do not break. It no longer carries an independent task list because duplicated mutable priorities caused documentation drift.

Current immediate gate, as of 2026-09-08:

```text
safely measure OpenRouter key-tier/rate-limit eligibility
→ reproduce the V14 `finish_reason=length` failure under eligible conditions
→ compare only bounded fixes without weakening USD0/model/schema/provenance gates
→ required CI on exact candidate SHA
→ deploy exact SHA
→ rerun authenticated B204 F01/F02/F03
→ require 3/3 with real TRACTIAN calls + valid terminal/evaluation
```

After that: broaden 13-read coverage, full governed-action SECURITY-V1, load/soak + evidence-derived SLO, restore/RTO/RPO, human semantic calibration, MANUAL vs AGENT-ASSISTED value evidence, branch protection and final evidence freeze.