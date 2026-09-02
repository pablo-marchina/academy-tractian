# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-09-02 — D01 completed live; D02 governed path provider-free validated; frontend/demo visualization promoted to P0 delivery work  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Final sprint:** GitHub issue #115  
**Frontend/test track:** GitHub issues #114, #118, #119  
**D02 live execution:** GitHub issue #117

This document is the current human-readable state. Historical ADRs, frozen experiment inputs and prior result artifacts remain authoritative for their exact scopes and are not rewritten by this checkpoint.

## 1. Executive state

```text
external API / hosted-service project cost      USD 0 HARD CONSTRAINT
final delivery                                   2026-09-08

production runtime / evaluator                   IMPLEMENTED / REGRESSION-GREEN
provider-free integrated demo                    VALID / PRESERVED
structured escalation handoff                    PROVED
standalone wheel                                 PROVED

D01 live comparison                              COMPLETE
D01 attempts                                     32 / 32 COMPLETED
D01 actual cash cost                             USD 0.00
D01 observed Neurons                             2813.628464
D01 selection                                    NO_SELECTION
D01 raw provider material persisted              NO

D01 GLM CLIENT_FAILURE                           16 / 16 at exactly 512 output tokens
D01 Nemotron CLIENT_FAILURE                       8 / 8 at exactly 512 output tokens
D01 total CLIENT_FAILURE                         24 / 24 at exact 512-token ceiling
D01 Nemotron technically accepted outputs         7, range 297..495 tokens
D01 Nemotron RESPONSE_PAYLOAD_INVALID              1, 476 tokens

D02 completion cap                               1024
D02 full-packet worst-case                       9352.805376 Neurons
D02 start gate                                   >= 9352.805376 free Neurons
D02 provider-free implementation                 MERGED / VALIDATED
D02 governed custody/authorization               MERGED / VALIDATED
D02 live result                                  NOT YET EXECUTED

2026-09-02 UTC modeled remaining after D01        7186.371536 Neurons
full D02 in current UTC allocation               INELIGIBLE
next Workers AI reset                            2026-09-03 00:00 UTC
                                                   = 2026-09-02 21:00 BRT

frontend application in canonical main tree      NOT LOCATED
frontend/demo visualization                      P0 DELIVERY GAP
architecture expansion                           NO_CHANGE
```

## 2. What D01 changed

D01 resolved the original live-provider gate but did not support a production provider selection. Both candidates failed hard quality/stability gates, so the valid frozen result is `NO_SELECTION`.

Post-run sanitized accounting produced a strong censoring signal: every generic `CLIENT_FAILURE` occurred at exactly the frozen 512 completion-token ceiling. This supports a prospective completion-budget diagnostic, not an architecture rewrite.

D01 remains authoritative and is not rescored or retroactively repaired.

## 3. D02 state

ADR-026 / the D02 provider-free contract changes only the variables required to test the censoring hypothesis:

```text
max_completion_tokens        512 -> 1024
failure subtype visibility   generic CLIENT_FAILURE -> generic code + sanitized subtype
```

Held constant:

```text
Cloudflare Workers AI
GLM 4.7 Flash + Nemotron 3 120B A12B
8 public units × 2 repeats × 2 candidates = 32 attempts
prompt / JSON decision schema / temperature
typed ToolSpecs / evaluator / public rubric
single-agent controller
zero retries / zero fallbacks
direct Workers AI
USD 0 / no paid spillover
```

The D02 resource bound is derived from the frozen rates and ceilings:

```text
GLM, 16 attempts        1300.3776 Neurons
Nemotron, 16 attempts   8052.427776 Neurons
full packet             9352.805376 Neurons
Workers Free daily      10000 Neurons
max modeled headroom     647.194624 Neurons
```

The governed D02 executor, write-ahead custody, no-replay behavior, fresh-reset authorization, CLIs and provider-free regressions are merged. No D02 live provider call has been made by that implementation work.

## 4. Current D02 live boundary

The current UTC allocation cannot safely guarantee the full D02 packet under the hard USD 0 constraint:

```text
10000 - 2813.628464 = 7186.371536 remaining modeled Neurons
7186.371536 < 9352.805376 required D02 bound
```

Therefore the current window is blocked for the full governed D02 packet.

The earliest next eligible reset is:

```text
2026-09-03 00:00:00 UTC
2026-09-02 21:00:00 America/Sao_Paulo
```

The reset does not itself authorize inference. D02 still requires fresh truthful zero-use operator attestation, evidence no older than 600 seconds, receipt no older than 300 seconds, exact custody binding, direct Workers AI, Workers Paid disabled, no AI Gateway/prepaid route, and explicit launcher invocation.

No blind retry or replay is allowed after any attempt is durably claimed or becomes uncertain.

## 5. Frontend / visualization state

The previous plan treated rich UI as P2. That priority is superseded for final delivery.

The runtime, evaluation and delivery evidence are mature enough that interface quality, integration and demo usability now represent a material delivery risk. The canonical `main` tree does not currently expose an identifiable versioned frontend application (`package.json`, React/Vite/Next, Streamlit/dashboard source not found during the 2026-09-02 audit).

Current frontend actions:

```text
#118 locate/version the actual UI source or document exact external ownership
#119 freeze the required UI state matrix
#114 implement visual changes, integrate, test, freeze and regress
#115 preserve a dedicated frontend test day and hard visual/feature freeze
```

Required demo-visible states include at minimum:

```text
success / orient
clarify missing context
abstain / unavailable evidence
escalation + structured handoff
action or policy blocked
loading
empty
error / provider or tool failure
```

The UI must never expose credentials, account identifiers, evaluator-private truth, raw provider material or raw private observations prohibited by the runtime contracts.

## 6. Architecture decision

D01 provides no evidence that topology caused the dominant failures. D02 is intentionally a single-variable diagnostic. Until D02 or another controlled measurement proves a material P0/P1 gap:

```text
single-agent controller   PRESERVE
LangGraph                  DO NOT ADD
multi-agent                DO NOT ADD
RAG/vector/reranking       DO NOT ADD
persistent memory          DO NOT ADD
MCP migration              DO NOT ADD
adaptive routing           DO NOT ADD
```

Issue #92 remains a materiality gate, not an instruction to add architecture.

## 7. Delivery schedule

```text
2026-09-02  frontend visual changes + first test window; D02 after 21:00 reset if freshly authorized
2026-09-03  D02 analysis/provider-state integration + frontend regression
2026-09-04  dedicated frontend end-to-end test day
2026-09-05  HARD VISUAL + FEATURE FREEZE
2026-09-06  clean reproduction + full acceptance
2026-09-07  final rehearsal + contingency buffer; P0 fixes only
2026-09-08  delivery; no same-day feature development
```

After the hard freeze, every code/UI change requires a P0/P1 delivery justification and targeted regression.

## 8. Remaining blockers / bounded gaps

```text
D02 live result                         P0 / WAITING FOR ELIGIBLE RESET + FRESH AUTHORIZATION
frontend source ownership              P1 / #118
frontend visual integration/testing    P0 / #114
final sprint freeze/reproduction        P0 / #115
C4 exact evaluator artifact             EXTERNAL EXACT-BYTE BLOCKER / NO RECONSTRUCTION
production provider selection           MAY REMAIN NO_SELECTION
```

`NO_SELECTION` is a valid provider outcome and must not trigger a last-minute architecture rewrite.

## 9. Still forbidden

- paid Workers AI or paid spillover;
- fabricated quota/use evidence;
- credential/account probing as a readiness shortcut;
- provider inference without the applicable governed authorization path;
- replay of claimed/uncertain live attempts;
- rewriting frozen D01 evidence or ADRs post hoc;
- reconstructing the unavailable C4 artifact;
- exposing evaluator-private truth, credentials or raw provider material in UI/demo artifacts;
- speculative architecture expansion;
- cosmetic redesign after the hard visual freeze;
- claiming provider/model support beyond measured evidence.
