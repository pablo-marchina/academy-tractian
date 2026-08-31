# Progress 038 — Cloudflare provider client provider-free implementation

**Date:** 2026-08-31  
**Issue:** #71  
**PR:** #72  
**Parent design:** ADR-018  
**Implementation freeze:** ADR-019  
**Provider/model inference calls:** 0  
**Credential/account probes:** 0  
**Live network validation:** 0  
**Scientific/C4 state changed:** no

## Completed

- implemented a separate Cloudflare Workers AI DecisionSource client without modifying historical ADR-009 provider client bytes;
- allowed only the two ADR-018 models;
- froze direct Workers AI OpenAI-compatible request semantics and strict response containment;
- required explicit constructor token/account/model and injected transport;
- performed no environment lookup, SDK integration or bundled network access;
- added provider-free tests for request shape, strict DecisionSource integration, drift/tool/refusal rejection, sanitized failure paths and usage recording without fabrication;
- added a dedicated provider-free workflow that also validates ADR-018 and historical provider-client/DecisionSource regressions;
- first CI attempt exposed only a test false positive caused by substring matching `environ` inside the word `environment`; the test was corrected to inspect real AST name/attribute references;
- final implementation head passed the dedicated client workflow, production runtime, final handoff, final provider-free reproduction and the triggered historical research regressions;
- frozen exact implementation identities in ADR-019.

## Frozen implementation identities

```text
client
src/academy_tractian/cloudflare_provider_client.py
a5c814b519584b6d4346e3b0567bbc3da8ba0bf4

tests
tests/test_cloudflare_provider_client.py
4c455b35d3949e809848017d478507141f278e42

workflow
.github/workflows/cloudflare-provider-client-provider-free.yml
88b0542acf9c2de2916484f3b435e8ed7ad8b191
```

## Non-claims

This checkpoint does not prove live Cloudflare compatibility, token/account validity, free-quota availability, latency, task quality, production-provider selection or production readiness.

## Next evidence-first step

Audit ADR-010/ADR-011 executor/custody implementation and associated code/tests/results against ADR-018/ADR-019 before creating any new live execution machinery. Only concrete incompatibilities or missing capabilities found by that audit may authorize additional implementation.

Live attempt 1 remains separately governed and unauthorized.