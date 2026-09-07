# Technical Presentation Pack — 5-minute video

**Purpose:** operational material for recording the final technical presentation.  
**Not a source of truth:** current runtime facts remain in [`../ACTIVE-PROJECT-STATUS.md`](../ACTIVE-PROJECT-STATUS.md) and architecture remains in [`../ARCHITECTURE.md`](../ARCHITECTURE.md).

This pack is intentionally optimized for a **5-minute, architecture-first, deeply technical walkthrough**. It is not a product tour and not a business pitch.

## Use these files in order

1. [`05-MIN-TECHNICAL-SCREENPLAY.md`](05-MIN-TECHNICAL-SCREENPLAY.md) — exact timeline, screen state and narration intent.
2. [`SCREEN-SHOT-LIST.md`](SCREEN-SHOT-LIST.md) — exact UI/visuals that must be captured.
3. [`ARCHITECTURE-OVERLAYS.md`](ARCHITECTURE-OVERLAYS.md) — simplified diagrams/overlays to animate while the live run progresses.
4. [`RECORDING-CHECKLIST.md`](RECORDING-CHECKLIST.md) — preflight, run selection, safety and fallback checklist.

## Presentation thesis

The video must prove one thing end-to-end:

```text
authenticated request
→ server-owned identity/tenant boundary
→ AgentController
→ provider-neutral structured decision
→ HarnessRunner + canonical ToolSpec
→ typed remote TRACTIAN API read
→ normalized evidence + RunTrace
→ safe terminal decision
→ isolated ProductionEvaluator
→ durable PostgreSQL projection
→ authenticated SSE/frontend inspection
```

The presenter should explain **responsibility boundaries and failure/safety semantics**, not enumerate libraries.

## Non-negotiable claims

- The browser is not authority for tenant, role or permissions.
- The model does not directly execute network calls.
- `HarnessRunner` is the canonical tool execution boundary.
- Runtime evidence and `RunTrace` are observable artifacts; hidden chain-of-thought is not exposed.
- Evaluation is post-runtime and evaluator-private truth is not given to the model.
- Release 0 exposes **13 live reads** and **5 proposal-only actions**; consequential external execution is disabled.
- The hosted product is remote; repository merge identity and hosted component identities are distinct.

## What this video is not

Do not spend time on:

- feature-by-feature tab tour;
- CSS or visual design details;
- every endpoint/tool individually;
- dependency versions;
- CI history;
- every research experiment;
- unpromoted LangGraph, multi-agent, RAG, MCP, Redis/Kafka or Kubernetes challengers.

If a detail does not clarify a runtime boundary, evaluation boundary, safety property or deployment path, it should probably stay off-screen.