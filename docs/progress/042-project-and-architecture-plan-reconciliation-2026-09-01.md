# Progress 042 — Project and architecture plan reconciliation

**Date:** 2026-09-01  
**Scope:** planning/documentation only; no provider inference, credential/account probe, live network validation or scientific execution

## Trigger

`PROJECT-PLAN.md` and `ARCHITECTURE-ROADMAP.md` still described the 2026-08-28 revalidation program as if provider discovery/preregistration, broad topology/runtime experimentation and zero-cost candidate screening were future work.

The actual project state has advanced materially:

- repository-wide historical evidence audit completed;
- current USD-0 provider facts refreshed;
- Cloudflare comparison preregistered/frozen by ADR-018;
- direct Cloudflare client frozen by ADR-019;
- ADR-010/011 reuse audit completed;
- executor/custody v2 frozen by ADR-020;
- live-authorization protocol frozen by ADR-021;
- the target account proves Workers Free / Active;
- the current dashboard does not expose an explicit Neuron meter required by ADR-021;
- issue #79 is blocked and issue #80 prospectively revalidates the unavailable evidence-source assumption;
- provider/model inference remains 0 and comparison attempts remain 0/32.

## Reconciliation principles

1. Replace stale discovery language with the actual ADR-018→021 state.
2. Treat issue #80 as the current D01 critical path; do not force a live comparison before the authorization evidence path is defensible.
3. Remove automatic topology/runtime experiments from the deadline-critical sequence. They remain conditional on a post-provider evidence audit showing a material unresolved decision.
4. Preserve existing evidence-sufficient decisions instead of rerunning them.
5. Protect the 2026-09-08 delivery by defining a fallback delivery path if external/account-side evidence blocks live provider comparison.
6. Keep C4 as a separate recovery track; do not let it silently block all other delivery evidence.
7. Continue to prohibit optional RAG, memory, richer UI or framework complexity absent a demonstrated material gap.

## New deadline strategy

```text
2026-09-01 → 09-02
  close ADR-021 evidence-source revalidation (#80)
  or formally freeze Cloudflare live comparison as externally blocked

2026-09-02 → 09-03
  if authorized: execute minimum frozen Cloudflare packet
  else: freeze bounded non-claim and use strongest provider-free/historical evidence

2026-09-03 → 09-05
  integrate/freeze only decisions still materially unresolved
  topology/runtime experiments only if evidence audit says they can change final architecture
  full production-path regression/reliability closure

2026-09-05 → 09-07
  architecture freeze, acceptance reconciliation, demo/runbook/reproduction
  no speculative P2 work

2026-09-08
  deliver strongest evidence-backed scope with explicit blockers/non-claims
```

## Hard boundaries preserved

```text
provider/model inference calls       0
credential/account probes            0
live network validation              0
comparison attempts consumed         0 / 32
production provider selected         NO
real customer mutations              0
C4 reconstruction/rescoring          FORBIDDEN
```
