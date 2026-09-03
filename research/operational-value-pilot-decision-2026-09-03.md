# Blinded DEV operational-value pilot — decision record

**Decision ID:** `OV-PILOT-001`  
**Date:** 2026-09-03  
**Issue:** #158  
**Parent decision:** `OV-001`  
**Status:** `IMPLEMENTED CONTRACT / NO REAL OPERATOR MEASUREMENTS COLLECTED / NO VALUE CLAIM AUTHORIZED`

## Purpose

Create the data-collection boundary required to measure manual engineer effort against agent-assisted human effort without leaking evaluator truth into the operator workflow.

The pilot measures **effort and operator outputs**. It does not decide whether those outputs are correct. Operational correctness remains evaluator-side and is joined later under the frozen EDD/scorer boundary.

## Selected pilot design

`INDEPENDENT_MATCHED`

For every eligible DEV case, the host packet creates:

- one `MANUAL` task containing the sanitized ticket/request only; and
- one `ASSISTED` task containing the same ticket/request plus the explicitly safe agent terminal projection and safe evidence context.

The two tasks in a matched case must be completed by different operator references. The resolver rejects same-operator reuse rather than accepting a learning-contaminated pair.

A crossover design remains a valid future experiment, but it is not used in this pilot because the current objective is to establish a clean initial effort baseline with the lowest avoidable carryover risk.

## Delivery boundary

The aggregate `OperationalPilotPacket` is **host-side experiment state**. It is not intended to be handed wholesale to a participant because it contains all randomized tasks. A collection UI/API must render only the single task assigned to the authenticated operator at that moment.

Each individual task is safe to render and contains only:

- opaque `task_id`;
- condition (`MANUAL` or `ASSISTED`);
- sanitized ticket/request;
- safe agent assistance only for `ASSISTED`.

An individual task does **not** contain:

- scenario id;
- asset/story group id;
- split;
- pair id;
- expected path;
- gold/private truth;
- evaluator score;
- operator identity;
- model/provider raw response;
- chain-of-thought;
- agent runtime duration.

The separate evaluator manifest stores the scenario/group/pair mapping, source hashes, frozen split hash and agent runtime duration.

## Split policy

Packet preparation requires the frozen `benchmark-split-v1` manifest.

Only authoritative `DEV` scenarios are accepted. `VALIDATION`, `LOCKED_TEST` and unknown scenarios fail closed. Group assignment is derived from the frozen manifest rather than caller metadata.

The pilot requires at least two distinct DEV story groups by default so a single story cannot masquerade as a general effort result.

## Measurement contract

Every valid completion requires:

- opaque operator reference represented only by SHA-256;
- `measurement_source=HOST_MONOTONIC_TIMER`;
- positive elapsed seconds;
- operator terminal decision;
- operator conclusion summary.

Interrupted, withdrawn or technical-failure trials require an explicit invalid reason and are never converted into valid timing observations.

Duplicate, missing and invalid tasks remain visible in the resolution report. A pair is emitted only when both arms are uniquely present and valid.

## Integrity binding

`prepare` creates deterministic identities over the evidence boundary:

```text
source material
→ ticket_sha256 + assistance_sha256
→ pair_id
→ MANUAL/ASSISTED task_id
→ packet_id bound to frozen split hash + protocol + shuffle seed
```

`resolve` does not trust the serialized files merely because they have valid shapes. It revalidates the packet, manifest and completion models and recomputes:

- pair identities;
- task identities;
- ticket content hashes;
- assisted-projection content hashes; and
- packet identity from the evaluator manifest.

A public-safe but substituted ticket or assistance therefore fails closed instead of silently becoming part of the measured experiment.

## Resolved effort pair

A valid pair exposes evaluator-side lineage without operator identity:

- protocol and pair id;
- scenario/case/group, DEV only;
- manual and assisted task ids;
- ticket and assistance hashes;
- manual seconds;
- assisted seconds;
- agent runtime seconds when available;
- hashes of the operator-visible conclusions.

The raw operator conclusion text is deliberately not copied into the effort-pair artifact. It remains in the controlled completion input for subsequent evaluator-only correctness scoring.

## Hard gates

- `LOCKED_TEST`/`VALIDATION` source accepted: `0`;
- manual task containing agent assistance: `0`;
- same operator used for both matched arms: `0`;
- aggregate host packet exposed as one participant's task surface: `0` in the collection product;
- private/gold/runtime markers in sanitized public material: `0`;
- packet/manifest content hash mismatch accepted: `0`;
- invalid trial silently treated as valid: `0`;
- missing/duplicate task silently ignored: `0`;
- provider/model invocation in packet preparation/resolution: `0`;
- fabricated project timing values: `0`.

## Current non-claims

This implementation does not claim that the current agent saves engineer time. No real operator measurement has been collected by this slice.

The contract also does not yet constitute the authenticated collection product; a host-side task-assignment/timer surface is the next implementation step before real measurements are collected.

## Next evidence step

Build the authenticated host-side collection surface that serves one assigned DEV task per operator and records server-owned monotonic timing. Then generate safe DEV sources from actual production-path runs, freeze the packet, collect independent matched completions, resolve effort pairs, and join those pairs with evaluator-only operational correctness labels before any business-value claim or VALIDATION threshold is selected.
