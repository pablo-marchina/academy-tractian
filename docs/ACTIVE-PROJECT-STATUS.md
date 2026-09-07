# Academy × TRACTIAN — Current Project Status

**Status:** Release 0 **PROMOTED** / UX pilot active  
**Checkpoint:** 2026-09-06 BRT  
**Promoted runtime SHA:** `082d6f115c070fdc898df749b4b3018efd9ceeab`  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Implementation branch:** `release/production-final`  
**Integration PR:** `#196`  
**Release 0 plan:** [`RELEASE-0-PLAN.md`](RELEASE-0-PLAN.md)  
**Release 0 acceptance:** [`RELEASE-0-ACCEPTANCE.md`](RELEASE-0-ACCEPTANCE.md)  
**Final delivery plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Decision registry:** [`decision-registry.yaml`](decision-registry.yaml)

This file is the mutable source of truth for active execution state. Historical and frozen evidence remains immutable.

## 1. Current objective

Release 0 is no longer blocked on infrastructure or the initial real-agent vertical slice. The active objective is to improve first-user product quality using real-user friction and correctness evidence while preserving the promoted safety boundaries.

```text
authenticated remote user
→ public HTTPS product
→ server-owned tenant context
→ live Cloudflare Release 0 provider
→ AgentController + HarnessRunner
→ typed TRACTIAN read
→ persisted evidence
→ FINAL | CLARIFY | ABSTAIN | ESCALATE
→ deterministic post-runtime evaluation
→ Neon PostgreSQL
→ REST/SSE + React UX
```

Consequential external action execution remains disabled.

## 2. Release 0 promotion record

Release 0 was promoted on runtime SHA `082d6f115c070fdc898df749b4b3018efd9ceeab` after the same candidate passed the remotely hosted Release 0 acceptance and the reproducible required gates.

| Gate | State | Evidence / boundary |
|---|---|---|
| Remote frontend/API | **PASS** | Railway public HTTPS product |
| Durable PostgreSQL | **PASS** | Neon production substrate |
| Immutable release identity | **PASS** | exact promoted SHA |
| Managed browser auth | **PASS** | real signup/session/logout path |
| Cross-tenant negatives | **PASS** | two-user REST/SSE isolation; forged browser authority rejected |
| Real hosted provider | **PASS — PROVISIONAL** | Cloudflare live provider; final tournament still `NO_SELECTION` |
| Real TRACTIAN read path | **PASS** | typed remote read observed with HTTP 2xx |
| Genuine read-only agent slice | **PASS** | provider → tool → TRACTIAN → evidence → terminal → evaluation |
| FINAL | **PASS** | hosted Release 0 acceptance |
| CLARIFY | **PASS** | hosted Release 0 modes acceptance |
| ABSTAIN | **PASS** | hosted Release 0 modes acceptance |
| ESCALATE | **PASS** | hosted Release 0 modes acceptance |
| Evidence / lineage / persistence | **PASS** | durable run artifacts and reload path |
| SSE / live progress | **PASS** | authenticated public path |
| 18-operation capability contract | **PASS** | 13 reads + 5 actions represented |
| Consequential action execution | **DISABLED** | zero external action calls in release campaign |
| Cash-cost policy | **USD0** | no automatic paid fallback |
| Local/mock serving dependency | **ZERO** | remote serving path only |
| Required reproducible CI | **PASS** | `final-ci-required`, clean clone, Playwright, runtime and handoff gates |

Hosted Release 0 workflow: `hosted-production-release0-agent`, run `34069562818`.

## 3. Provider decision state

Release 0 uses Cloudflare `@cf/zai-org/glm-4.7-flash` as a **provisional Release 0 provider**. This is not a claim that it is the best or final provider.

The frozen Provider Tournament v3 remains unchanged:

```text
final provider decision = NO_SELECTION
full campaign = 17 scenarios × 5 repetitions × 2 candidates = 170 attempts
```

`DP-004` therefore intentionally remains `NO_SELECTION`; the Release 0 provisional serving decision does not rewrite the preregistered final provider decision.

## 4. Promoted product boundary

### Available now

- managed user authentication;
- server-owned tenant identity;
- live Cloudflare model calls;
- 13 canonical TRACTIAN read operations at the production boundary;
- real remote TRACTIAN reads;
- customer-safe FINAL / CLARIFY / ABSTAIN / ESCALATE outcomes;
- evidence, lineage, timeline and trace graph;
- deterministic post-runtime evaluation;
- persisted run history and reload;
- authenticated SSE/live progress;
- architecture and engineering observability surfaces.

### Deliberately not promoted

- consequential action execution;
- final Provider Tournament winner;
- exhaustive semantic-accuracy claims;
- full SECURITY-V1 completion;
- final production SLO/capacity/HA/RTO/RPO claims;
- human-calibrated semantic judge;
- measured operational time savings;
- adaptive policy superiority.

## 5. Active phase — UX pilot

The product is technically usable; the priority is now to make the first-user experience understandable without developer guidance.

```text
login
→ understand what the product can do
→ choose or write an investigation
→ understand live progress
→ understand the terminal result
→ understand supporting evidence
→ know what to do next
→ provide lightweight feedback
```

### UX work order

1. **First-run onboarding** — explain the product, read-only boundary and best first action.
2. **Guided investigations first** — surface useful intents before the engineering capability catalog.
3. **Readable progress** — translate runtime events into user-facing stages such as Preparing, AI deciding, Reading TRACTIAN, Evaluating and Complete.
4. **Customer-first outcome** — emphasize conclusion/message and evidence before engineering metadata.
5. **Mode-specific next steps** — CLARIFY asks a clear question; ABSTAIN states what is missing; ESCALATE explains the handoff; FINAL summarizes evidence.
6. **Evidence summary** — expose safe, comprehensible evidence before the raw timeline/trace.
7. **Feedback loop** — reuse or extend existing review/value collectors for lightweight usefulness feedback and product telemetry.
8. **Progressive disclosure** — keep trace, architecture, raw capability catalog and evaluator detail available but secondary for ordinary users.

## 6. Post-release engineering priority

```text
P0 auth / isolation / broken run / provider / TRACTIAN defect
→ P1 wrong conclusion / wrong tool / weak evidence / bad clarify-escalate UX
→ P1 user friction / latency / reliability
→ full Provider Tournament v3
→ SECURITY-V1 / load / recovery
→ governed actions
→ human calibration / operational-value study
→ adaptive challengers only after measured gaps
```

Do not add LangGraph, multi-agent, RAG/vector DB, MCP, Redis/Kafka, microservices, Kubernetes or persistent memory unless measured post-release evidence demonstrates a blocker the current architecture cannot solve.

## 7. Evidence discipline

- The promoted runtime remains `082d6f115c070fdc898df749b4b3018efd9ceeab` until a later candidate independently clears the applicable promotion gates.
- Documentation-only commits do not imply a new production artifact.
- Frozen evidence is never rewritten to make current code appear historically valid.
- Release 0 telemetry and user feedback may prioritize changes, but production claims remain evidence-backed.
