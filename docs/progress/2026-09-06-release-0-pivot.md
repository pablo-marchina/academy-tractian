# 2026-09-06 — Release 0 execution pivot

## Decision

The project execution objective changed from completing every final-production evidence gate before exposure to users to releasing the smallest safe real production slice immediately, then using real-user telemetry to accelerate quality and UX improvement.

This does **not** relax hard safety/cost boundaries. It changes only which final-delivery gates block first-user access.

## Starting point

Starting implementation branch before this pivot:

`release/production-final` at `6026e6aea7e6a6574640ba383fb742c62e01826e`.

Known state at pivot:

- G2 remote backend/deployment foundation: PASS;
- Railway/Caddy frontend: hosted;
- Neon PostgreSQL/RLS substrate: hosted;
- immutable release identity + hosted smoke: PASS;
- Neon Auth: implemented/provisioned, minimum hosted user-isolation acceptance still open;
- production TRACTIAN transport: implemented and recent identity/header binding fixes landed, real bounded-read release proof still open;
- production provider state: `NO_SELECTION`;
- `remote_server.py`: infrastructure-probe composition with `NoSelectedProviderDecisionSource` and consequential actions denied;
- full Provider Tournament v3: preregistered but intentionally authorizes zero calls in its frozen final-selection protocol;
- consequential action infrastructure: source implemented, but remote execution remains deny-all.

## New release target

Release 0 is a real read-only multi-user pilot:

```text
authenticated remote user
→ hosted provider
→ AgentController
→ typed TRACTIAN read tool
→ real TRACTIAN evidence
→ FINAL | CLARIFY | ABSTAIN | ESCALATE
→ deterministic evaluation
→ durable PostgreSQL
→ SSE + frontend
```

Consequential external action execution remains disabled.

## Immediate critical path

1. synchronize Release 0 plan/acceptance/PR state;
2. close minimum hosted IAM release negatives;
3. prove bounded real TRACTIAN read path;
4. provisionally qualify an existing USD0 provider candidate with a small governed campaign;
5. compose real production DecisionSource behind fail-closed configuration;
6. execute genuine read-only public E2E;
7. release to users;
8. prioritize real-user correctness/reliability/UX failures, then resume full final-delivery evidence program.

## Scope moved behind Release 0

The following remain required for the strongest final delivery but do not block first-user read-only access:

- full 170-attempt Provider Tournament v3;
- governed consequential action execution;
- full SECURITY-V1 hosted population;
- full remote load staircase/SLO derivation;
- restore/RTO/RPO campaign;
- human semantic calibration;
- operational-value study;
- adaptive runtime challengers;
- final evidence freeze.

## Guardrails retained

- project actual cash cost USD 0;
- no automatic paid spillover;
- no local serving dependency;
- no browser-owned tenant/role/permission authority;
- zero accepted cross-tenant disclosure in release campaign;
- no mock/provider-free decision source or TRACTIAN transport in user release;
- no consequential external action execution in Release 0;
- evidence-honest claims and immutable historical research artifacts.
