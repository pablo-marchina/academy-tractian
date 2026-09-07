# Getting Started — Current Release 0 Product

**Audience:** first-time product user or reviewer  
**Goal:** complete one safe industrial investigation without needing runtime knowledge  
**Public product:** https://production-web-production-c9d1.up.railway.app

## What the product does

The hosted product investigates industrial questions with a live model and the supplied TRACTIAN API. It grounds answers in authorized structured observations and can stop safely instead of guessing.

The normal first-user journey is still investigation-first. Consequential external actions now exist behind a separate **governed confirmation** path: an action is not executed merely because the model proposes it or because the UI shows it. Exact confirmation, server-owned permission/resource scope, idempotency and execution ownership are required before a remote attempt.

Complete live acceptance of all five action endpoints is still being validated; the current production status is documented in [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md).

## 1. Sign in

Open the public product and sign in/create an account. Tenant scope is server-owned. Browser headers or request text cannot choose organization, role or permissions.

If sign-in/session infrastructure is temporarily unavailable, the UI shows a retryable authentication state. Invalid/expired sessions and temporary auth-service outages are deliberately different conditions.

## 2. Start on **Home**

Home's primary task is simple: **what do you want to understand?**

Write a normal equipment question. You do **not** need to know internal `company_id` or `asset_id` values when the requested asset can be discovered through your authorized fleet.

Useful examples:

```text
Which equipment needs attention today, and why?

Investigate R310 and tell me what the technical data indicate about its condition.

Is the data quality for R310 sufficient to trust the current diagnosis?

What is the most likely cause of the problem on R310, and how certain is that conclusion?
```

Human-readable labels such as `R310` are resolved through authenticated identity → company → fleet discovery. If a label is not in the accessible fleet, the safe result is to say it was not found — not to invent another scope.

## 3. Follow live progress

User-facing stages are human-readable summaries derived from safe runtime events and are **not chain-of-thought**.

A run may include identity/fleet discovery followed by analysis, RMS, spectrum, baseline, data-quality or knowledge reads depending on the question.

A repeated tool name is not automatically a loop. An asset-level RMS/spectrum call may be followed by a more specific `point_id` call when the first response exposes a point that materially improves the investigation.

## 4. Read the result and evidence status

Two different concepts matter:

### Terminal decision

The controller may orient/answer, clarify, abstain or escalate depending on the runtime state.

### `response_mode`

This describes how completely the inspected evidence supports the customer-visible answer:

- **complete** — every material part of the request is supported;
- **partial** — a useful conclusion is supported but a material part remains probabilistic/incomplete;
- **inconclusive** — evidence was inspected but does not support a reliable directional answer;
- **conflict** — material observations contradict one another;
- **unavailable** — required authorized evidence could not be obtained.

A likely mechanism can be useful without being fully proven. A supported asset prioritization plus a probable causal mechanism should normally be `partial`, not `inconclusive`.

## 5. Navigate the product

### Home

Start a new equipment question.

### Result / evidence detail

After submission, the selected run opens its customer-safe conclusion, next step and supporting evidence. Evidence is contextual to the result rather than a permanent top-level destination.

### Analyses

Browse/select persisted prior runs. Selecting one opens that run's result context.

### Technical

Use specialist depth only when needed. Current sections include:

- **Current analysis** — trace, evidence, tools and policy;
- **Quality** — post-runtime evaluation/provider evidence;
- **Data** — persisted quantitative views;
- **System** — health, architecture and capabilities;
- **Actions** — governed action proposal/confirmation/state boundary;
- **Studies** — controlled human semantic/operational-value research.

Controlled research collectors are **not** casual feedback channels.

## 6. If an action is proposed

A consequential action is intentionally different from a normal answer.

Before confirming, verify the visible impact/target/summary. The backend keeps the exact private action payload and authorization facts server-side.

The confirmation control must not ask you to reconstruct permissions, internal authorization grants, idempotency keys or vendor actor identities.

Action states are intentionally explicit:

```text
waiting for confirmation
confirmed
running
accepted by external service
blocked for safety
not accepted
outcome needs verification
```

Important rules:

- “sent” is not the same as “accepted”;
- external success is shown only when the backend has explicit upstream acceptance;
- a blocked/not-accepted action is not silently retried;
- an uncertain outcome requires reconciliation rather than clicking retry blindly;
- current production does not yet claim that every one of the five vendor action endpoints has passed live acceptance.

## 7. Evidence discipline

Treat claims at the strength the evidence supports:

- metadata/criticality can prioritize investigation but does not alone prove a fault mechanism;
- baseline/data quality can support trust/context but are not substitutes for current condition evidence when the question asks what is happening;
- RMS supports magnitude/trend conclusions but should not be forced into an unsupported precise causal diagnosis;
- spectrum can support frequency-mechanism hypotheses, but causal certainty still depends on the available evidence;
- unavailable/missing asset labels must fail closed;
- a configured capability is not proof that an external vendor accepted a write.

## 8. Current UX direction

The product is task-driven, but additional simplification is still planned. The design target is one primary question/action per screen, with evidence and technical detail opened only when they help the current decision.

This is an implementation direction, not a claim that representative human usability testing is complete.

## 9. What the product does not claim

The project does not currently claim final provider superiority, universal five-action vendor acceptance, completed full SECURITY-V1, final capacity/SLO/HA/RTO/RPO, calibrated human semantic accuracy, measured human time savings, completed human usability validation or adaptive-policy superiority.

For exact current status, use [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md). For governed action operations, see [`GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md`](GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md).