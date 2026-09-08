# Technical Presentation Pack — 5-minute video

**Last synchronized with hosted product:** 2026-09-07 BRT  
**Current backend/runtime:** `08866da60245f58f217981b7ae668b10be45cc67` (V13)  
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

Do not record using the superseded global `Results / Evidence / Investigation / Engineering` tab script.

The hosted task-driven product now uses:

```text
Home        primary question entry
Result      contextual selected-run outcome/evidence
Analyses    persisted run history
Technical   Current analysis / Quality / Data / System / Actions / Studies
```

Evidence remains available contextually for the selected result and inside technical analysis surfaces.

## Recommended persisted runs

Use existing live V13 evidence instead of repeatedly consuming provider quota during rehearsal:

- **PRIMARY TECHNICAL RUN:** `run_97b91f6e0feb91184283` — R310 spectrum investigation, `partial`, condition evidence + point-specific drill-down;
- **DATA-QUALITY ALTERNATIVE:** `run_21813cb7b4ad9adbdc5e` — data quality + RMS drill-down, `complete`;
- **SAFE BOUNDED-UNAVAILABLE RUN:** `run_547b2a62d84ef56a3d3d` — R420 absent from authorized fleet, `unavailable`.

Do not describe the R420 run as an API outage: its important behavior is **authorized inventory fail-closed**.

## Presentation thesis

Prove one end-to-end path:

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

## Non-negotiable claims

- Browser is not authority for tenant, role or permissions.
- Model does not directly execute network calls.
- `HarnessRunner` is canonical tool execution boundary.
- Human asset labels are resolved against authorized fleet observations.
- Diagnostic answers require the evidence class needed by the question.
- `response_mode` communicates evidence completeness; it does not grant authority.
- Evaluation is post-runtime; evaluator-private truth is not given to the model.
- Release 0 exposes 13 read operations and 5 action operations in the contract; consequential external action execution is disabled.
- Same-name RMS/spectrum calls can be legitimate asset→point drill-down; do not call them loops without comparing arguments.
- Cloudflare is provisional Release 0 provider, not final tournament winner.

## What this video is not

Do not spend time on CSS, every endpoint, CI history, all experiments, or unpromoted LangGraph/multi-agent/RAG/MCP/infrastructure challengers. If a detail does not clarify a runtime, evidence, safety, auth or evaluation boundary, keep it off-screen.