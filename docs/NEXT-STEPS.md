# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-09-01 — ADR-021 frozen; explicit Neuron evidence unavailable in target UI; issue #80 is the current gate  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)

This file is the short-horizon plan. It does not authorize provider inference, credential probing or attempt 1.

## 1. Completed

```text
historical evidence audit                         DONE
provider factual refresh                         DONE
Cloudflare comparison preregistration             FROZEN / ADR-018
Cloudflare direct client                         FROZEN / ADR-019
ADR-010/011 reuse audit                          DONE
Cloudflare executor/custody v2                   FROZEN / ADR-020
live authorization protocol                     FROZEN / ADR-021
Workers Free / Active                           PROVED MANUALLY

provider inference                              0
credential/account probes                       0
live network validation                         0
comparison attempts consumed                    0 / 32
```

## 2. NOW — issue #80: revalidate ADR-021 Neuron evidence source

Observed blocker:

```text
ADR-021 requires explicit current Neuron usage/remaining
↓
target AI → Workers AI UI exposes no such meter
↓
Workers Free is proved, but >=9000 remaining is not
```

Do not:

- infer zero usage from a missing meter;
- use undocumented/private dashboard endpoints as canonical evidence;
- use Alpha/Restricted billing APIs as the authoritative gate without prospective justification;
- perform a credential/account probe;
- make a sacrificial model call;
- weaken the 9000-Neuron start threshold post hoc.

Issue #80 must prospectively determine the smallest defensible non-inference fallback.

## 3. Candidate fallback to evaluate prospectively

Current candidate hypothesis:

```text
Workers Free / Active proof
+
documented 10000-Neuron daily reset at 00:00 UTC
+
operator attestation of no Workers AI calls since reset
+
exclusive Workers AI usage window
+
0 / 32 comparison attempts consumed
=
starting allocation treated as 10000 for the bounded execution window
```

This is **not authorized yet**. The amendment must freeze exact timing, source evidence, TTL, attestation and failure semantics before use.

## 4. Decision deadline for provider path

By 2026-09-02, choose one evidence-backed branch:

### Branch A — defensible amendment freezes

```text
freeze prospective ADR-021 amendment
→ obtain admissible real evidence
→ select canonical custody root
→ issue short-lived receipt provider-free
→ only then provision Cloudflare token/account ID
→ explicit execution authorization
→ run frozen ADR-018 packet
```

### Branch B — no defensible evidence path

```text
freeze LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
→ no token needed
→ no provider inference
→ continue final delivery from provider-free/historical evidence
```

Do not let the project wait indefinitely on the external quota-evidence surface.

## 5. If live packet becomes authorized

Packet remains unchanged:

```text
@cf/zai-org/glm-4.7-flash
VS
@cf/nvidia/nemotron-3-120b-a12b

8 public probes × 2 repeats × 2 candidates
max 32 attempts
```

Valid outcomes:

```text
cloudflare_glm_4_7_flash_workers_free
cloudflare_nemotron_3_120b_a12b_workers_free
NO_SELECTION
```

No candidate, metric, threshold, population or budget may change after results begin.

## 6. After provider D01 is resolved or bounded

Run another **evidence sufficiency audit**, not an automatic experiment queue.

### Agent topology

Ask whether single-agent vs multi-agent can still materially change a P0/P1/final architecture decision.

- if no: keep qualified single-agent baseline and document bounded non-claim;
- if yes: preregister the minimum controlled topology comparison.

### Runtime/orchestration

Only assess after topology/materiality is closed. Do not conduct generic LangGraph/framework research.

### No-current-gap areas

Do not experiment on these absent new evidence:

```text
native tools vs MCP
RAG/vector/reranking
persistent memory
rich observability backend
rich UI
adaptive routing
```

## 7. Parallel C4 track

Exact artifact only:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
```

No reconstruction/rescoring/substitution is authorized.

## 8. Deadline sequence

```text
09-01 → 09-02   close/bound #80
09-02 → 09-03   live provider result OR external-blocker freeze
09-03 → 09-05   only still-material architecture decisions + reliability/regression
09-05 → 09-07   architecture freeze + acceptance evidence + demo/runbook/reproduction
09-08           delivery
```

After 2026-09-05, no speculative P2 experiment unless it closes a demonstrated delivery blocker.

## 9. Still forbidden

- provider inference before defensible authorization;
- token/account provisioning merely to test account state;
- fabricated quota values;
- Workers Paid / prepaid AI Gateway / paid spillover;
- retry/replay of claimed or uncertain attempts;
- changing ADR-018 packet post hoc;
- C4 reconstruction/rescoring;
- premature multi-agent/runtime work;
- final provider/architecture claims beyond evidence.
