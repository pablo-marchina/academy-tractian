# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-09-01 — provider-free delivery/demo/security audits complete; PFG-01 escalation-handoff gap closed; D01 reset-window evidence is the next operational gate  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Immediate plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**D01 preflight:** [`CLOUDFLARE-D01-PREFLIGHT-2026-09-01.md`](CLOUDFLARE-D01-PREFLIGHT-2026-09-01.md)

This is the canonical human-readable current authorization state. Historical frozen ADRs/artifacts remain authoritative for their exact scopes.

## Executive state

```text
external API / hosted-service project cost      USD 0 HARD CONSTRAINT
evidence audit before new experiment             REQUIRED

historical evidence audit                        COMPLETE
provider factual refresh                         COMPLETE
Cloudflare comparison preregistration             FROZEN / ADR-018
Cloudflare provider client                        FROZEN / ADR-019
Cloudflare executor/custody v2                    FROZEN / ADR-020
Cloudflare original authorization protocol        FROZEN / ADR-021
reset-window Neuron evidence amendment            FROZEN / ADR-022
governed entrypoint audit/contract                ACCEPTED / ADR-023
minimal governed live launcher                    MERGED / PROVIDER-FREE VALIDATED
standalone production wheel reproduction          PROVED / PR #91
delivery-acceptance audit 2026-09-01             COMPLETE / PR #96
final-demo audit 2026-09-01                      COMPLETE / PR #96
security/trace/failure audit 2026-09-01          COMPLETE / PR #96
structured escalation handoff PFG-01             CLOSED / PROVED / PR #96
D01 operator preflight                           PREPARED

stable implementation baseline after PR #91      a93854dd5e70edf8084bdaae1762dd64cdb6aa48
provider-free readiness merge PR #96             f383bbe0e87e6927411c14fd67ba8dbda9e57cbc
standalone-wheel-smoke                            PASSED
PR #96 final workflow set                         13 / 13 SUCCESS

Workers Free / Active account state               PROVED MANUALLY
explicit current Neuron meter in target UI        NOT AVAILABLE
ADR-021 explicit-balance path                     PRESERVED BUT NOT OPERABLE ON TARGET UI
ADR-022 reset-window fallback                     PROVIDER-FREE VALIDATED
ADR-023 receipt→ADR-020 composition               PROVIDER-FREE VALIDATED
issue #44 OpenAI/Gemini path                      CLOSED / HISTORICAL / SUPERSEDED
issue #79 real evidence/receipt                    READY PENDING VALID RESET WINDOW
issue #89 standalone wheel gap                    CLOSED / PROVED
issue #92 architecture materiality/Pareto         PLANNING ONLY / STARTS AFTER D01
issue #95 escalation-handoff completeness         CLOSED / PROVED
issue #9 C4 exact artifact                        EXTERNALLY BLOCKED / EXACT BYTES ONLY

provider/model inference calls                    0
credential/account probes                         0
live network validation                           0
comparison attempts consumed                      0 / 32
real reset-window evidence captured               NO
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
packet max 7937.522688 Neurons
Workers Free documented allocation 10000 Neurons/day
historical start gate >=9000 Neurons remaining
reset-window derived start state 10000 Neurons
```

## 1. Provider-free readiness audit result

The current final-delivery acceptance wording was re-audited against repository-resident evidence rather than inheriting historical `PASS_BOUNDED` labels.

The audit concluded:

```text
core runtime/evaluator/security boundaries       EVIDENCED
standalone distribution                          EVIDENCED
provider-free failure/stability evidence         EVIDENCED
customer-safe communication                      EVIDENCED
structured trace observability                   EVIDENCED
clarify / abstain / fail-closed behavior         EVIDENCED
escalation handoff completeness                  GAP FOUND → CLOSED BY PR #96
final real non-scripted provider demo            PARTIAL / D01 DEPENDENT
provider/model quality                           BLOCKED / D01 DEPENDENT
provider-specific latency/resource evidence      PARTIAL / D01 DEPENDENT
EV-012 / C4 exact evidence                       BLOCKED / EXACT ARTIFACT MISSING
final deployment/rollback evidence               LATER FINAL-INTEGRATION DECISION
```

Audit artifacts:

- `docs/DELIVERY-ACCEPTANCE-AUDIT-2026-09-01.md`
- `docs/DEMO-AUDIT-2026-09-01.md`
- `docs/SECURITY-TRACE-AUDIT-2026-09-01.md`

These documents are current audit evidence, not retroactive rewrites of frozen 2026-08-28 experiment results.

## 2. Structured escalation handoff closure

The audit found the frozen EV-011 `C10_ESCALATION_HAS_SAFE_HANDOFF` predicate proved safe human-review wording but did not enforce the stronger current requirement for a useful operational handoff.

PR #96 closed this prospectively without changing frozen controller/provider/evaluator results:

```text
ProductionRequest
+ exact captured RunTrace
+ ESCALATE_HUMAN outcome
↓
HumanEscalationHandoff
  unresolved request
  exact reason/message
  deterministic observation references + hashes
  COLLECTED / NONE_COLLECTED state
  fixed safe reviewer continuation instruction
↓
deterministic handoff validation
```

The handoff does not serialize raw observation bodies, identity binding, user id, seed, credentials, provider raw material or evaluator-private truth.

The initial PR CI correctly caught one JSON-canonicalization defect. It was fixed without weakening a gate; the final head then completed all 13 associated workflows successfully.

## 3. Final-demo state

The frozen provider-free five-scenario demo remains useful integrated evidence because it executes the real runtime, tool boundary, trace and evaluator. Its decision source is nevertheless scripted.

Therefore:

```text
provider-free integrated demo          VALID / PRESERVED
final real non-scripted provider demo  NOT YET PROVED
```

Do not relabel scripted evidence as live-provider evidence.

After D01 resolves or is explicitly bounded, the final demonstration must use the resulting real/bounded decision-source path where feasible, preserve per-run evaluation separation, and visibly surface at least one uncertainty/failure path plus the structured escalation handoff when escalation is demonstrated.

## 4. Security / trace state

Current supported invariants:

```text
identity outside model control
seed outside model control
authorization outside model control
HarnessRunner sole real tool-execution boundary
strict argument validation before transport
permission/project-policy separation
consequential-action claim/idempotency containment
sanitized scalar-only model-call provenance
no evaluator-private truth in runtime/provider request
trace lifecycle + execution-chain integrity
policy denial containment
provider/tool failures fail closed
bounded turns/tool calls
no hidden retry/fallback on governed paths
no raw secrets/private provider material in canonical artifacts
customer-safe failure communication
```

No current security evidence justifies adding LangGraph, persistent memory, MCP migration, RAG/vector infrastructure, external observability SaaS or another authorization framework before D01.

## 5. Current D01 sequence

The provider path requires no additional implementation before the reset.

Next real window:

```text
2026-09-01 21:00:00–21:10:00 America/Sao_Paulo
=
2026-09-02 00:00:00–00:10:00 UTC
```

Before the window, only operator-side private preparation remains:

```text
choose one private local root outside repository
choose one canonical custody root
prepare private Workers Free source path
prepare fresh evidence/receipt output paths
ensure no background Workers AI consumer can run
ensure provider credentials are absent before evidence/receipt
```

Receipt issuance rejects these provider environment variables if present:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
OPENAI_API_KEY
GEMINI_API_KEY
GROQ_API_KEY
```

Use `docs/CLOUDFLARE-D01-PREFLIGHT-2026-09-01.md` for the exact PowerShell sequence.

## 6. Real reset-window authorization gate

Proceed only if all are truthful:

```text
Cloudflare primary docs still state 10000 Neurons/day
Cloudflare primary docs still state reset at 00:00 UTC
observation occurs <=00:10:00 UTC
Workers Free / Active is proved
Workers Paid is false
no Workers AI calls since reset
no automated/background Workers AI consumers since reset
exclusive account usage through packet completion
direct Workers AI route only
AI Gateway/prepaid unified billing absent
comparison attempts = 0
inference/probes used to obtain evidence = 0
```

Any uncertainty fails closed.

The governed sequence remains:

```text
private Workers Free source artifact
↓
reset-window evidence JSON
↓
<=5-minute provider-free receipt bound to exact custody root
↓
ONLY THEN Cloudflare token/account ID
↓
ADR-022 receipt/evidence/custody validation
↓
ADR-023 governed launcher
↓
ADR-020 GovernedCloudflareLiveTaskV2
↓
attempt 1
```

Attempt 1 remains unauthorized until the real evidence and receipt exist and the operator explicitly invokes the launcher while every attestation remains true.

## 7. Evidence freshness and custody

```text
reset observation window       00:00:00–00:10:00 UTC
evidence maximum age           600 seconds
receipt maximum lifetime       300 seconds
same UTC day                    required
source artifact                 retained privately outside repo
serialized source evidence      SHA-256 only
account ID / token              never serialized
```

No warm-up, quota probe, alternate custody root, hidden retry/fallback or sacrificial inference is authorized.

## 8. Allowed D01 outcomes

```text
A  governed live packet → GLM supported
B  governed live packet → Nemotron supported
C  governed live packet → NO_SELECTION
D  truthful reset-window/exclusive-custody gate unavailable → LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
```

Forced provider selection remains forbidden.

## 9. Architecture decision state

```text
single-agent controller      STRONG QUALIFIED BASELINE
standalone packaging         EVIDENCE SUFFICIENT / REGRESSION OBLIGATION
structured escalation handoff EVIDENCE SUFFICIENT / REGRESSION OBLIGATION
native tools vs MCP          EVIDENCE SUFFICIENT CURRENT SCOPE
stopping/evidence policy     EVIDENCE SUFFICIENT CURRENT SCOPE
RAG/vector/reranking         NO MATERIAL CURRENT GAP / NO EXPERIMENT
persistent memory            NO MATERIAL CURRENT GAP / NO EXPERIMENT
multi-agent comparison       CONDITIONAL AFTER PROVIDER D01
runtime comparison           CONDITIONAL AFTER TOPOLOGY/MATERIALITY AUDIT
adaptive routing             UNASSESSED / NOT CURRENTLY MATERIAL
rich UI/deployment           P2 UNLESS FINAL ACCEPTANCE GAP APPEARS
issue #92                    PLANNING-ONLY HARD-GATE + PARETO PROTOCOL
```

The architecture is not claimed globally optimal. It is the strongest qualified current baseline.

## 10. Post-D01 architecture protocol

Issue #92 activates only after:

```text
provider D01 result
OR
LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED frozen
```

Then:

```text
re-audit topology materiality
→ if no P0/P1 topology gap: preserve single-agent baseline
→ if material: preregister minimum controlled topology comparison
→ only after topology closure assess runtime/orchestration
```

Any alternative must first preserve P0 coverage, deterministic safety, evaluator isolation, trace integrity, clean reproduction, USD 0 feasibility and fail-safe behavior before entering a Pareto comparison.

No arbitrary weighted architecture score is authorized.

## 11. C4 parallel track

```text
required SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes             177350
rows              144
geometry          36 common parents × 4 arms
```

Only exact-byte recovery is authorized. Reconstruction, rescoring or substitution remains forbidden.

Issue #9 remains the explicit external scientific blocker.

## 12. Deadline state

```text
09-01 provider-free readiness audits/fix          COMPLETE
09-01 21:00–21:10 D01 reset gate                 NEXT IF TRUTHFUL CUSTODY EXISTS
09-02 → 09-03 provider result/blocker + #92       PENDING
09-03 → 09-05 only still-material architecture    CONDITIONAL
09-05 → 09-07 freeze/demo/runbook/reproduction    PENDING
09-08 delivery                                    TARGET
```

After 2026-09-05, default against speculative P2 work.

## 13. Still forbidden

- provider inference before real valid evidence + receipt + explicit governed launcher invocation;
- credential/account probes merely to obtain quota or verify secrets;
- fabricated quota values;
- concurrent/unaccounted Workers AI use during reset-window custody;
- Paid Workers / prepaid AI Gateway / paid spillover;
- changing ADR-018 packet post hoc;
- retry/replay of claimed/uncertain attempts;
- C4 reconstruction/rescoring/substitution;
- unnecessary RAG/memory/multi-agent/runtime/UI complexity;
- topology/runtime work before D01 is resolved or explicitly bounded;
- claiming the scripted provider-free demo is a live-model demonstration;
- final provider/architecture/production-readiness claims beyond evidence.
