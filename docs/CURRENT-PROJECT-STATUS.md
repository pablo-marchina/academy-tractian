# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-09-01 — ADR-021 frozen; Neuron evidence-source assumption blocked and under prospective revalidation (#80)  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Immediate plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)

This is the sole canonical human-readable current authorization state. Historical frozen ADRs/artifacts remain authoritative for their exact scopes.

## Executive state

```text
external API / hosted-service project cost      USD 0 HARD CONSTRAINT
evidence audit before new experiment             REQUIRED

historical evidence audit                        COMPLETE
provider factual refresh                         COMPLETE
Cloudflare comparison preregistration             FROZEN / ADR-018
Cloudflare provider client                        FROZEN / ADR-019
Cloudflare executor/custody v2                    FROZEN / ADR-020
Cloudflare live authorization protocol            FROZEN / ADR-021

Workers Free / Active account state               PROVED MANUALLY
explicit current Neuron meter in target UI        NOT AVAILABLE
ADR-021 original Neuron evidence source            NOT OPERABLE ON TARGET UI
issue #79 real evidence/receipt                    BLOCKED
issue #80 evidence-source amendment                ACTIVE CRITICAL PATH

provider/model inference calls                    0
credential/account probes                         0
live network validation                           0
comparison attempts consumed                      0 / 32
real authorization receipt issued                 NO
Cloudflare credentials provisioned                NO
attempt 1 authorized                              NO
production provider/model selected                NO
```

Frozen candidates/packet:

```text
@cf/zai-org/glm-4.7-flash
@cf/nvidia/nemotron-3-120b-a12b
8 public probes × 2 repeats × 2 candidates = max 32 calls
plan SHA 092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb
packet max 7937.522688 neurons
Workers Free documented allocation 10000 neurons/day
frozen start gate >=9000 neurons remaining
```

## 1. Current D01 sequence

Completed:

```text
historical evidence audit                    DONE
current USD-0 factual refresh                DONE
minimum provider gap demonstrated            DONE
comparison preregistration                   FROZEN / ADR-018
Cloudflare direct client                     FROZEN / ADR-019
ADR-010/011 reuse audit                      DONE
executor/custody v2                          FROZEN / ADR-020
live authorization protocol                  FROZEN / ADR-021
```

Current blocker:

```text
ADR-021 assumed explicit current Neuron usage/remaining evidence
↓
target Workers AI dashboard does not expose that meter
↓
DO NOT infer used=0 / remaining=10000
DO NOT probe credentials/accounts
DO NOT use sacrificial inference
DO NOT use undocumented private dashboard endpoints as canonical evidence
↓
issue #80 prospective evidence-source revalidation
```

Only after #80 freezes a defensible path may #79 resume.

## 2. What the manual account evidence does prove

The supplied billing/subscription screen proves:

```text
Workers plan   Workers Free
status         Active
Workers Paid   not active
```

It does **not** prove the frozen ADR-021 condition:

```text
free_neurons_remaining >= 9000
```

Absence of a visible usage meter is not evidence of zero usage.

## 3. ADR-018→021 remain frozen historical/current evidence

ADR-018 freezes the scientific packet; ADR-019 freezes the direct client; ADR-020 freezes executor/custody/resource guards; ADR-021 freezes the original authorization protocol.

Issue #80 must be a **prospective amendment/revalidation**. It must not rewrite ADR-021 history or silently weaken the start gate.

## 4. Allowed provider outcomes

```text
A  defensible amendment → live packet authorized/executed → GLM / Nemotron / NO_SELECTION
B  no defensible path before deadline → LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
C  live packet executes but no candidate qualifies → NO_SELECTION
```

All three are legitimate evidence-backed outcomes. Forced provider selection is forbidden.

## 5. Other architecture decisions

```text
single-agent controller      STRONG QUALIFIED BASELINE
multi-agent comparison       CONDITIONAL AFTER PROVIDER D01
runtime comparison           CONDITIONAL AFTER TOPOLOGY/MATERIALITY AUDIT
native tools vs MCP          EVIDENCE SUFFICIENT CURRENT SCOPE
stopping/evidence policy     EVIDENCE SUFFICIENT CURRENT SCOPE
RAG/vector/reranking         NO MATERIAL CURRENT GAP / NO EXPERIMENT
persistent memory            NO MATERIAL CURRENT GAP / NO EXPERIMENT
adaptive routing             UNASSESSED / NOT CURRENTLY MATERIAL
rich UI/deployment work      P2 UNLESS ACCEPTANCE GAP APPEARS
```

Topology/runtime experiments are no longer automatic deadline tasks. They require a fresh evidence sufficiency check after D01 is resolved or bounded.

## 6. C4 parallel track

```text
required SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes             177350
rows              144
geometry          36 common parents × 4 arms
```

Only exact-byte recovery is authorized. Reconstruction/rescoring/substitution remains forbidden.

## 7. Deadline state

```text
09-01 → 09-02  close/bound issue #80
09-02 → 09-03  execute provider packet if admissible OR freeze external blocker
09-03 → 09-05  close only still-material architecture decisions + full reliability/regression
09-05 → 09-07  architecture freeze + acceptance/demo/runbook/reproduction
09-08          delivery
```

After 2026-09-05, default against speculative P2 experiments.

## 8. Still forbidden

- provider inference before defensible authorization;
- credential/account probes merely to obtain quota evidence;
- fabricating `used=0` or `remaining=10000`;
- Paid Workers / AI Gateway prepaid or paid spillover;
- changing ADR-018 packet post hoc;
- retry/replay of claimed/uncertain attempts;
- C4 reconstruction/rescoring;
- unnecessary RAG/memory/multi-agent/runtime/UI complexity;
- final provider/architecture/production-readiness claims beyond evidence.
