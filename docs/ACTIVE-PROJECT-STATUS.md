# Academy × TRACTIAN — Active Project Status

**Status:** Release 0 **PROMOTED** / UX pilot live / `main` integrated  
**Last verified:** 2026-09-06 BRT  
**Promoted backend/runtime SHA:** `082d6f115c070fdc898df749b4b3018efd9ceeab`  
**Current hosted frontend UX SHA:** `2ca6215ccc07664a9551e8363e438f0930a4d995`  
**Current hosted supplied-API SHA:** `47561c1175181b508139e23e6e39b555c1347d57`  
**Validated PR #196 head:** `d7e941b1e0ee380f3cca43816521c88eddc20e9c`  
**Main integration merge:** `9fbfbe0c5b5b80dc23941ac2850125834641e32b`  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Branch:** `main`  
**PR:** `#196 (MERGED)`

This file is the mutable source of truth for **current execution state**. Frozen/history files remain immutable.

Repository integration identity and hosted component identities are intentionally tracked separately. Merging PR #196 into `main` does not by itself imply that every hosted service was redeployed from the merge commit.

## 1. Current objective

The infrastructure/read-only vertical slice is no longer the blocker. Release 0 is live and technically usable. The active objective is now:

> **make first-use quality excellent, collect uncontaminated real-user evidence, and close the remaining final-delivery hardening/research gates without weakening the promoted safety boundary.**

Current user path:

```text
authenticated remote user
→ Results
→ guided/custom industrial investigation
→ live provider + typed TRACTIAN reads
→ persisted evidence
→ FINAL | CLARIFY | ABSTAIN | ESCALATE
→ deterministic post-runtime evaluation
→ optional depth: Evidence → Investigation → Engineering
```

Consequential external action execution remains disabled.

## 2. Release 0 promotion — PASS

Release 0 was promoted on backend/runtime SHA `082d6f115c070fdc898df749b4b3018efd9ceeab`.

| Gate | State | Evidence/boundary |
|---|---|---|
| public HTTPS frontend/API | **PASS** | Railway |
| durable PostgreSQL | **PASS** | Neon |
| immutable backend release identity | **PASS** | exact promoted SHA |
| managed browser auth | **PASS** | hosted signup/session/logout |
| two-user/tenant isolation | **PASS** | REST/SSE negatives; forged browser authority rejected |
| hosted provider | **PASS — PROVISIONAL** | Cloudflare Release 0 route |
| typed real TRACTIAN read | **PASS** | remote HTTP 2xx through canonical transport |
| provider → agent → evidence E2E | **PASS** | hosted acceptance |
| FINAL / CLARIFY / ABSTAIN / ESCALATE | **PASS** | hosted modes acceptance |
| persistence / lineage / evaluation | **PASS** | Neon-backed run artifacts |
| authenticated SSE / reconnect | **PASS** | public path |
| 18-operation capability contract | **PASS** | 13 live reads + 5 proposal-only actions |
| external consequential action execution | **DISABLED** | 0 release-campaign calls |
| cash-cost policy | **USD0** | no automatic paid fallback |
| local/mock serving dependency | **ZERO** | remote serving only |

Hosted Release 0 acceptance: `hosted-production-release0-agent`, run `34069562818`.

## 3. UX pilot — implemented and hosted

The hosted frontend UX baseline remains `2ca6215ccc07664a9551e8363e438f0930a4d995`. The supplied TRACTIAN API identity bridge is hosted at `47561c1175181b508139e23e6e39b555c1347d57`.

The complete PR #196 source head `d7e941b1e0ee380f3cca43816521c88eddc20e9c` passed the required regression surface and was merged into `main` as `9fbfbe0c5b5b80dc23941ac2850125834641e32b`. These identities are deliberately separate: repository integration is not represented as an application redeploy.

The validated PR #196 regression surface included:

- `frontend-provider-free`;
- `full-product-playwright`;
- `clean-clone-full-product-reproduction`;
- `final-ci-required`;
- production-runtime, Postgres, observability, EDD, IaC and handoff regressions.

### Completed UX work

| UX workstream | State | Current implementation |
|---|---|---|
| first-run orientation | **DONE** | product purpose, read-only boundary and guarantees before engineering detail |
| guided investigation entry | **DONE** | server-owned guided intents; explicitly labelled local starter examples only when unavailable |
| human-readable live progress | **DONE** | Preparing → Deciding → Reading → Reviewing → Evaluating → Complete |
| customer-first terminal outcome | **DONE** | outcome/message/next step/evidence before trace internals |
| mode-specific recovery | **DONE** | distinct FINAL/CLARIFY/ABSTAIN/ESCALATE guidance |
| evidence summary | **DONE** | compact evidence first; canonical trail in Evidence layer |
| progressive disclosure | **DONE** | Results → Evidence → Investigation → Engineering |
| keyboard-accessible depth navigation | **DONE** | tab semantics + Arrow/Home/End focus behavior |
| preserve full engineering observability | **DONE** | runtime/evals/architecture/capabilities remain available in deeper layers |
| lightweight casual run feedback | **NEXT** | must be separate from controlled semantic/value collectors |
| first-time-user pilot iteration | **NEXT** | collect friction/correctness evidence and prioritize quantitatively |

### Important feedback-design decision

`SemanticReviewCollector` and `OperationalValueCollector` are controlled research instruments. They will **not** be repurposed as casual thumbs-up/down feedback because that would contaminate experimental data. A separate minimal run-feedback channel is the next feedback task.

## 4. Provider state

Release 0 currently uses Cloudflare `@cf/zai-org/glm-4.7-flash` as a **provisional Release 0 provider**.

This does not change the frozen final provider decision:

```text
Provider Tournament v3 = 17 scenarios × 5 repetitions × 2 candidates = 170 attempts
final provider decision = NO_SELECTION
```

`DP-004` stays `NO_SELECTION` until the preregistered final campaign produces eligible evidence.

## 5. Product boundary available now

- managed authentication and server-owned tenant identity;
- 13 live TRACTIAN reads;
- 5 action operations represented as proposal-only capabilities;
- live provider decisions;
- evidence-aware terminal modes;
- safe tool/model/policy provenance;
- deterministic post-runtime evaluator;
- persisted history/reload;
- authenticated REST/SSE;
- four-level progressive UX;
- architecture/trace/capability/evaluation observability.

## 6. Deliberate non-claims / open final gates

Release 0 does **not** close:

- final Provider Tournament v3;
- full SECURITY-V1 hosted campaign;
- final remote load/capacity + evidence-derived SLO;
- real backup/restore drill + measured RTO/RPO;
- governed consequential external action execution;
- human semantic calibration;
- real MANUAL vs AGENT-ASSISTED operational-value study;
- adaptive-policy superiority;
- final evidence freeze/delivery bundle.

## 7. Current priority order

```text
P0 auth/tenant/provider/TRACTIAN/run regression
→ P1 wrong conclusion/tool/evidence/mode behavior
→ P1 first-user friction + casual run feedback
→ real-user UX iteration
→ Provider Tournament v3
→ SECURITY-V1
→ load/SLO + restore/recovery
→ governed actions
→ human calibration + operational value
→ adaptive challengers only after measured gaps
→ final evidence freeze
```

Do not add new architectural layers unless a measured blocker justifies them.

## 8. Evidence discipline

- promoted backend/runtime identity remains `082d6f...` until a later backend candidate independently clears promotion gates;
- hosted frontend/UX identity, hosted supplied-API identity, validated source identity and repository merge identity are tracked separately;
- a repository merge or docs-only commit is not a new backend release or automatic redeploy;
- CI evidence is not automatically production SLO/HA/security evidence;
- frozen history is never rewritten;
- user feedback may prioritize work but cannot bypass deterministic safety/authorization gates.