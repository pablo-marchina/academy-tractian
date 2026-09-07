# Academy × TRACTIAN — Active Project Status

**Status:** Release 0 **PROMOTED** / task-driven UX live / `release/production-final` integrated  
**Last verified:** 2026-09-07 BRT  
**Promoted backend/runtime SHA:** `082d6f115c070fdc898df749b4b3018efd9ceeab`  
**Current hosted frontend UX SHA:** `1bc124a8d4dbd029178ff8129b25452129445de7`  
**Current hosted supplied-API SHA:** `47561c1175181b508139e23e6e39b555c1347d57`  
**Validated PR #209 head:** `a707222f94fb92f9402409e84ba3de673637dfc9`  
**Production integration merge:** `1bc124a8d4dbd029178ff8129b25452129445de7`  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Branch:** `release/production-final`  
**PR:** `#209 (MERGED)`

This file is the mutable source of truth for **current execution state**. Frozen/history files remain immutable.

Repository integration identity and hosted component identities are intentionally tracked separately. PR #209 was merged into `release/production-final` and its exact merge commit was promoted to the Railway `production-web` service. This frontend promotion does not imply a new backend/runtime promotion.

## 1. Current objective

The infrastructure/read-only vertical slice is no longer the blocker. Release 0 is live and technically usable. The active objective is now:

> **make first-use quality excellent, collect uncontaminated real-user evidence, and close the remaining final-delivery hardening/research gates without weakening the promoted safety boundary.**

Current user path:

```text
authenticated remote user
→ Home
→ ask an equipment question in natural language
→ live provider + typed TRACTIAN reads
→ persisted evidence
→ FINAL | CLARIFY | ABSTAIN | ESCALATE
→ customer-first result + next step
→ evidence when needed
→ Analyses for prior runs or Technical for specialist depth
```

Consequential external action execution remains disabled in the promoted backend/runtime boundary.

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

## 3. Task-driven UX — implemented and hosted

The hosted frontend UX is `1bc124a8d4dbd029178ff8129b25452129445de7`. The supplied TRACTIAN API identity bridge remains hosted at `47561c1175181b508139e23e6e39b555c1347d57`.

PR #209 head `a707222f94fb92f9402409e84ba3de673637dfc9` passed the required regression surface and was merged into `release/production-final` as `1bc124a8d4dbd029178ff8129b25452129445de7`. Railway deployment `f78e88cd-82c2-4fcf-8f59-a51168f10fad` built that exact merge commit and passed the `/` healthcheck.

The validated PR #209 regression surface included:

- `frontend-provider-free`;
- `full-product-playwright`;
- `clean-clone-full-product-reproduction`;
- `eval-driven-development-provider-free`;
- `observability-api-provider-free`;
- `final-handoff-acceptance-audit`;
- `final-ci-required`.

### Completed UX work

| UX workstream | State | Current implementation |
|---|---|---|
| task-first global navigation | **DONE** | Home / Analyses / Technical only |
| focused first-run entry | **DONE** | one natural-language question + one primary `Analyse` action; examples optional |
| human-readable live progress | **DONE** | three understandable progress stages rather than internal runtime phases |
| customer-first terminal outcome | **DONE** | status → conclusion → next step → evidence |
| mode-specific recovery | **DONE** | distinct FINAL/CLARIFY/ABSTAIN/ESCALATE guidance without exposing internal reason codes in the primary UX |
| contextual evidence | **DONE** | evidence is entered from the result when needed rather than occupying a permanent global destination |
| recognition-first history | **DONE** | prior analyses use an accessible list instead of a dense table |
| task-grouped technical depth | **DONE** | Current analysis / Quality / Data / System / Actions / Studies; one family rendered at a time |
| keyboard and responsive access | **DONE** | focusable navigation/history, visible focus, large targets and 390px no-overflow browser acceptance |
| preserve full engineering observability | **DONE** | runtime/evals/architecture/capabilities/actions/studies remain available under Technical |
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
- task-driven Home / Analyses / Technical UX;
- contextual result/evidence flow;
- architecture/trace/capability/evaluation observability under specialist depth.

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