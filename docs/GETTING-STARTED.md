# Getting Started — Release 0

**Audience:** first-time product user or reviewer  
**Goal:** complete one safe industrial investigation and understand the result without needing runtime knowledge  
**Public product:** https://production-web-production-c9d1.up.railway.app

## What Release 0 does

Release 0 investigates industrial questions with a live hosted model and the supplied TRACTIAN **read** API surface. It grounds its output in persisted evidence and can stop safely instead of guessing.

It may return:

- **FINAL / ORIENT** — a customer-safe conclusion is available;
- **CLARIFY** — required context is missing;
- **ABSTAIN** — the evidence does not justify a conclusion;
- **ESCALATE** — uncertainty/conflict should be handed to a qualified human.

External consequential actions are disabled. The product may expose action proposals/policy evidence for inspection, but Release 0 does not execute them against TRACTIAN.

## 1. Sign in

Open the public product and create/sign into a managed account. Tenant scope is determined by the server; do not expect browser headers or request fields to control organization/permissions.

## 2. Start in **Results**

The product intentionally opens at the lowest-complexity layer.

Before a run, Results explains:

- what the product can do;
- the read-only Release 0 boundary;
- useful starting postures;
- which guarantees are active.

When server-owned guided intents are available, Quick Start uses them. In environments where that manifest is unavailable, the UI labels local starter prompts as **examples only**; they are not presented as runtime capabilities.

You can always write your own request. Include concrete asset, analysis, telemetry or time identifiers when you have them.

Example shape:

```text
Investigate why this asset/analysis produced the observed alert.
Use only evidence you can actually inspect, state uncertainty,
and tell me what I should verify next.
```

## 3. Follow live progress

For a live investigation, the user-facing stages are:

```text
Preparing
→ AI deciding
→ Reading TRACTIAN
→ Reviewing evidence
→ Evaluating
→ Complete
```

These are derived from safe runtime events. They are **not chain-of-thought** and do not expose hidden model reasoning.

## 4. Read the outcome first

When complete, Results foregrounds:

1. the terminal outcome;
2. the customer-safe message;
3. response/evidence semantics when available;
4. what to do next;
5. compact supporting evidence references.

Mode-specific behavior:

- **FINAL:** review conclusion + evidence; no external change is executed for you.
- **CLARIFY:** provide the missing context identified by the message and run again.
- **ABSTAIN:** add the missing evidence/identifier rather than treating the absence of a conclusion as failure.
- **ESCALATE:** hand the reason and evidence context to a qualified human reviewer.

## 5. Go deeper only when useful

The four layers keep the **same persisted run context**.

### Results — Answer & next step

Use this for normal operation and first review.

### Evidence — Why this answer

Use this to inspect the canonical safe event trail, evidence IDs, tool names, safe HTTP status/latency metadata and persisted terminal output.

Raw secret-bearing upstream payloads are not exposed.

### Investigation — Runtime & operations

Use this for run history, execution state, event/tool/policy metrics, Trace Graph and governed action proposal/control state.

### Engineering — Architecture & evals

Use this for deep observability: capability contract, architecture overlay, post-runtime evaluator, system analytics and controlled semantic/operational-value research collectors.

These research collectors are **not** casual thumbs-up/down feedback. Their protocols must remain controlled.

## 6. Historical runs

Open Investigation to select a persisted run. Selecting history keeps the same depth model and returns you to Results first so the outcome is not hidden behind engineering detail.

## 7. What the product does not claim

Release 0 does not claim:

- final provider/model superiority;
- consequential external action readiness;
- exhaustive semantic accuracy;
- completed full SECURITY-V1 campaign;
- final capacity/SLO/HA/RTO/RPO;
- measured human time savings;
- adaptive-policy superiority.

For exact current status, use [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md).