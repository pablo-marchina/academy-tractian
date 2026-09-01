# Academy × TRACTIAN — Architecture Roadmap

**Status:** ACTIVE / canonical macro architecture roadmap  
**Architecture checkpoint:** 2026-09-01 — ADR-022 reset-window evidence amendment  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate execution:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This document describes the production-path architecture and which choices are already supported, conditional, or blocked. It does not authorize live provider execution.

## 1. Target architecture

Two coupled planes share structured traces while preserving evaluator-private truth:

```text
                   AGENT RUNTIME PLANE

User / request
      ↓
Request Context Boundary
  identity / authorization / request state
      ↓
AgentController / selected topology
  evidence sufficiency / stopping / clarification / escalation
      ↓
Stable typed Tool Contract
      ↓
TRACTIAN API Adapter
      ↓
Supplied industrial API
      ↓
Normalized observations
      ↓
AgentController
      ↓
customer-safe outcome
      ↓
RunTrace
      │
      │ sanitized runtime evidence only
      ▼
             EVALUATION & RELIABILITY PLANE

scenario/requirement contract + evaluator-only references
      ↓
deterministic evaluators where possible
      ↓
validated semantic/human judgment only where necessary
      ↓
quality / tool / arguments / evidence / decision /
action / escalation / safety / robustness / stability
      ↓
reports + trace inspection + architecture evidence
```

Hard boundary:

```text
runtime ─X─> private oracle / evaluator-only gold / hidden outcomes
```

Hidden chain-of-thought is not required; inspectable structured state is.

## 2. Strongly supported architectural invariants

### HarnessRunner is the execution boundary

`HarnessRunner.execute_tool()` remains the sole real tool-execution boundary. Provider output proposes a decision; provider-native tools never execute real actions.

### Native typed tools remain the current integration surface

Historical Native Tools × MCP evidence is sufficient for this scope:

```text
native typed ToolSpec   preferred
MCP                     optional portability adapter
new Native-vs-MCP test  not justified now
```

### Deterministic authorization/action safety is non-negotiable

Permission checks, action validation, idempotency, write-ahead claims and no-replay semantics may be preserved or strengthened, never weakened for convenience.

### RunTrace/evaluator separation is an architecture foundation

The current structured trace and deterministic operational evaluator are sufficient foundations. Richer observability backends are optional absent a measured diagnostic/delivery gap.

### Human fallback is first-class

Valid outcomes include:

```text
clarify
abstain
escalate with evidence handoff
```

rather than fabricated certainty or unsafe mutation.

## 3. Current provider serving path

Historical OpenAI/Gemini/Groq paths remain evidence; they are not the current candidate production packet.

The frozen current experimental serving path is:

```text
ProviderDecisionSource
      ↓
CloudflareWorkersAIChatCompletionsDecisionClient
      ↓
direct Workers AI endpoint
      ↓
ONE OF
  @cf/zai-org/glm-4.7-flash
  @cf/nvidia/nemotron-3-120b-a12b
      ↓
strict ProviderDecisionPayload
      ↓
Cloudflare exact provenance adapter
      ↓
AgentController
      ↓
HarnessRunner
```

Frozen layers:

```text
ADR-018  provider comparison preregistration
ADR-019  direct client
ADR-020  executor/custody/resource accounting
ADR-021  original live authorization protocol
ADR-022  reset-window Neuron evidence fallback
```

Scientific packet remains:

```text
8 public probes × 2 repeats × 2 models
max attempts       32
input ceiling      8000 tokens/attempt
output ceiling     512 tokens/attempt
packet maximum     7937.522688 Neurons
selection          Pareto / NO_SELECTION allowed
```

## 4. ADR-022 changes authorization evidence, not serving architecture

The target account proves `Workers Free / Active`, but the current Workers AI UI does not expose the explicit Neuron meter assumed by ADR-021.

The architecture/client/executor were already ready provider-free. ADR-022 only adds an evidence mode:

```text
RESET_WINDOW_ATTESTATION
```

Derived start state:

```text
Cloudflare documented 10000 Neurons/day
+ documented daily reset at 00:00 UTC
+ observation <=00:10 UTC
+ no Workers AI calls since reset
+ no background/automated Workers AI consumer since reset
+ exclusive account custody through packet completion
= 10000 Neurons remaining at evidence observation
```

Any uncertain premise fails closed.

The original ADR-021 explicit-balance path remains preserved for a UI/account where the balance is actually exposed.

## 5. Authorization/custody architecture after ADR-022

```text
manual Workers Free source evidence
+ reset-window no-use/exclusive-use attestation
      ↓
CloudflareResetWindowEvidenceV1
      ↓
provider-free validation
      ↓
short-lived reset-window receipt
  evidence SHA
  custody-root SHA
  ADR-018/019/020/021 pins
  plan/model/route pins
      ↓
ONLY THEN provider credentials
      ↓
ADR-020 governed prepare/claim/execute
```

Time boundaries:

```text
reset observation    first 600 seconds after 00:00 UTC
evidence age         <=600 seconds at receipt issuance
receipt life         <=300 seconds
same UTC day         required
```

No account ID, token or raw custody path is serialized into evidence/receipt.

## 6. Resource safety remains ADR-020-owned

ADR-022 does not replace execution-time accounting.

ADR-020 continues to enforce:

- actual reported usage only;
- Neuron accounting for GLM/Nemotron;
- H8/H9/H10;
- per-attempt input/output ceilings;
- projected worst-case remaining budget before the next call;
- missing usage fail-closed;
- durable 32-attempt write-ahead ledger;
- `CLAIMED` before network-capable call;
- uncertain/no-replay behavior.

Reset-window start state `10000` is stronger than the historical `>=9000` start gate.

## 7. Production architecture decision register

| Decision | Current state | Architecture consequence |
|---|---|---|
| Provider/model | `PARTIALLY_ASSESSED`; live result pending | current operational decision |
| Tool topology | `EVIDENCE_SUFFICIENT` | native typed ToolSpec standard; MCP conditional |
| Stopping/evidence policy | `EVIDENCE_SUFFICIENT` | preserve |
| Safety/authorization/idempotency | strong hard boundary | preserve/strengthen only |
| RunTrace/operational evaluator | `EVIDENCE_SUFFICIENT` current scope | preserve |
| Retrieval/RAG/vector/reranking | no material gap | do not add |
| Persistent memory | no material task need | do not add |
| Agent topology | strong single-agent qualified baseline | conditional post-provider audit |
| Runtime/orchestration | historical evidence strong but asymmetric | conditional after topology/materiality |
| Adaptive model routing | unassessed, not currently material | defer |
| Rich observability | optional | defer unless measured need appears |
| Hosted deployment | simplest reproducible zero-cost path | no paid dependency required |
| Rich UI | optional | only if acceptance/demo benefit is material |

## 8. Agent topology is conditional, not automatic

Current baseline:

```text
single AgentController
+ explicit state
+ evidence-sufficiency stopping
+ typed tools
+ HarnessRunner execution boundary
```

After provider D01 resolves or is bounded:

```text
re-audit topology evidence
→ can topology still materially change P0/P1/final architecture?
   ├─ NO → preserve simple baseline; document comparative limitation
   └─ YES → preregister minimum controlled comparison
```

If comparison is justified, hold provider/model, ToolSpecs, HarnessRunner, safety, evaluator definitions and task population constant where feasible.

Adopt multi-agent only if measured benefit survives coordination errors, latency/quota cost, trace complexity and debugging overhead.

## 9. Runtime/orchestration is one gate later

Do not perform generic framework research.

After topology/materiality is closed, ask whether changing runtime can still materially improve:

- correctness;
- recovery;
- observability;
- maintainability;
- deterministic safety.

Only then compare the minimum credible runtime alternatives with topology/provider held fixed.

## 10. Retrieval, memory, routing and optional infrastructure

### Retrieval/RAG

No measured retrieval-recall bottleneck currently justifies RAG/vector DB/reranking. Direct typed tool/evidence routing remains preferred.

### Persistent memory

No current task requires cross-request learned memory strongly enough to justify contamination/privacy/reproducibility risk. Explicit request-local state remains preferred.

### Adaptive model routing

Deferred until multiple final-eligible models exist and a routing decision could materially improve quality/resource use.

### Observability

Structured RunTrace is sufficient current scope. OTel/hosted backends require a demonstrated diagnostic or acceptance benefit.

### Deployment/UI

Use the simplest reproducible zero-cost delivery surface. Richer hosted deployment/UI is P2 unless needed for final acceptance/demo quality.

## 11. Provider outcomes and architecture consequences

### Live winner

If GLM or Nemotron is supported by the frozen packet, freeze that serving configuration prospectively and regress the integrated path.

### NO_SELECTION

Do not force a provider. Preserve provider-free/historical evidence and deliver the strongest defensible architecture with explicit limitation.

### LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED

If exclusive reset-window custody cannot be established, freeze the external blocker. Do not weaken architecture/security/evidence guarantees merely to obtain a provider result.

## 12. C4 remains a separate scientific recovery track

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
```

Only exact-byte recovery is authorized. C4 limitation must remain explicit in final claims if unresolved.

## 13. Architecture freeze criteria

Final architecture may freeze only when applicable material choices have:

1. requirement/risk rationale;
2. hard constraints including USD 0;
3. repository evidence audit;
4. credible alternatives or a documented reason they are not material;
5. controlled evidence where a comparison remains necessary;
6. robustness/failure evidence;
7. production-fit evidence;
8. explicit trade-offs/reversal triggers;
9. regression obligations;
10. no uncovered P0 acceptance row introduced by the choice.

Implementation effort, framework popularity or novelty are not selection evidence.

## 14. Productionization sequence

```text
provider D01 result/bounded blocker
→ materiality audit of remaining architecture decisions
→ minimum additional comparison only if needed
→ final architecture ADR/freeze
→ integrated regression/reliability
→ clean reproduction
→ demo/runbook/fallback/limitations
→ delivery
```

## 15. Architecture quality rule

The final architecture is the **simplest architecture on the best-supported zero-cost quality/production Pareto frontier that fully covers the requested delivery**.

Evidence decides complexity; neither more nor fewer components are inherently better.
