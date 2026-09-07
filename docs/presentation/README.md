# Technical Presentation Pack — 5-minute video

**Last synchronized with hosted product:** 2026-09-07 BRT  
**Current backend/runtime source:** `3545d75c00ca30419e0f47e8b1950aa50cbbf462`  
**Current frontend:** `1bc124a8d4dbd029178ff8129b25452129445de7`  
**Purpose:** operational material for the final technical presentation.

Current runtime facts remain owned by [`../ACTIVE-PROJECT-STATUS.md`](../ACTIVE-PROJECT-STATUS.md) and canonical architecture by [`../ARCHITECTURE.md`](../ARCHITECTURE.md).

This pack is optimized for a **5-minute architecture-first technical walkthrough**. It is not a business pitch and must use the real hosted task-driven product.

## Use these files in order

1. [`EXACT-5-MIN-RECORDING-SCRIPT.md`](EXACT-5-MIN-RECORDING-SCRIPT.md) — exact screens/clicks/words/timestamps.
2. [`05-MIN-TECHNICAL-SCREENPLAY.md`](05-MIN-TECHNICAL-SCREENPLAY.md) — technical intent behind the timing.
3. [`SCREEN-SHOT-LIST.md`](SCREEN-SHOT-LIST.md) — exact current UI/visual evidence to capture.
4. [`ARCHITECTURE-OVERLAYS.md`](ARCHITECTURE-OVERLAYS.md) — simplified truthful overlays.
5. [`RECORDING-CHECKLIST.md`](RECORDING-CHECKLIST.md) — preflight, run selection, claim discipline and fallback.

## Current UI vocabulary

The hosted task-driven product uses:

```text
Home        primary question entry
Result      contextual selected-run outcome/evidence
Analyses    persisted run history
Technical   analysis / Quality / Data / System / Actions / Studies
```

Do not revert to the superseded global Results / Evidence / Investigation / Engineering script.

The next frontend simplification target is one main question/action per screen with fewer simultaneous cards/statuses. That direction is not a completed human-usability claim.

## Recommended persisted read runs

Use existing live V13 evidence instead of repeatedly consuming provider quota during rehearsal:

- **PRIMARY TECHNICAL RUN:** `run_97b91f6e0feb91184283` — R310 spectrum investigation, `partial`, condition evidence + point-specific drill-down;
- **DATA-QUALITY ALTERNATIVE:** `run_21813cb7b4ad9adbdc5e` — data quality + RMS drill-down, `complete`;
- **SAFE BOUNDED-UNAVAILABLE RUN:** `run_547b2a62d84ef56a3d3d` — R420 absent from authorized fleet, `unavailable`.

Do not describe the R420 run as an API outage: its important behavior is **authorized inventory fail-closed**.

## Presentation thesis

Prove one end-to-end read path and one action-safety boundary:

```text
authenticated request
→ managed-session / server-owned tenant
→ V13 grounded DecisionSource
→ AgentController
→ HarnessRunner + canonical ToolSpec
→ typed remote TRACTIAN read
→ normalized evidence + RunTrace
→ terminal decision + response_mode
→ isolated ProductionEvaluator
→ durable PostgreSQL projection
→ authenticated SSE / task-driven UI
```

Then show consequential action governance separately:

```text
proposal
→ exact private custody
→ explicit confirmation
→ server-owned grant/resource authorization
→ idempotency + lease/fencing
→ server-owned vendor actor
→ one typed write
→ explicit acceptance OR safe non-success/uncertain state
```

## Current governed-action truth

PR #211 enabled the five canonical governed actions. PR #213 added the auditable production smoke. Required CI for #213 was green.

However, the fresh live write gate did **not** pass 5/5: `update_asset_config` returned HTTP 403 / `accepted=false`, and the validation deployment failed before replacing healthy production.

Investigation showed the supplied runtime has distinct vendor actors for low-impact and high-impact/escalation permissions in the tested company scope. Corrective routing now separates local product identity from a server-owned TRACTIAN actor selected by company + required permission.

Therefore the presentation should claim:

- governed action safety architecture is implemented and CI-qualified;
- production composition can enable it;
- the live five-action gate correctly failed closed;
- complete five-action vendor readiness is **not yet proven**.

Do **not** say actions are still globally disabled/read-only, and do **not** say all five actions work.

## Non-negotiable claims

- Browser is not authority for tenant, role, permissions or vendor action actor.
- Model does not directly execute network calls.
- `HarnessRunner` is the canonical tool execution boundary.
- Human asset labels are resolved against authorized fleet observations.
- Diagnostic answers require the evidence class needed by the question.
- `response_mode` communicates evidence completeness; it does not grant authority.
- Evaluation is post-runtime; evaluator-private truth is not given to the model.
- The contract contains 13 reads and 5 governed action operations.
- Action proposal is not execution; explicit confirmation and deterministic server-owned controls are required.
- `ACCEPTED` requires explicit upstream acceptance; `UNCERTAIN` is not blindly retried.
- Same-name RMS/spectrum calls can be legitimate asset→point drill-down; compare arguments/resource before calling them loops.
- Cloudflare is a provisional Release 0 provider, not final tournament winner.
- The current live action limitation is a vendor actor/permission integration gap surfaced by an honest fail-closed smoke.

## What this video is not

Do not spend time on CSS, every endpoint, CI history or unpromoted LangGraph/multi-agent/RAG/MCP challengers. If a detail does not clarify runtime, evidence, safety, auth, action authority, deployment or evaluation, keep it off-screen.

For exact governed-action evidence, use [`../progress/2026-09-07-production-governed-actions-ux-and-validation.md`](../progress/2026-09-07-production-governed-actions-ux-and-validation.md).