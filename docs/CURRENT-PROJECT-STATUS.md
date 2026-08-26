# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-25 22:50 BRT  
**Branch:** `research/systematic-foundation`  
**PR:** #2 — draft research-governance PR  
**Final delivery target:** 2026-09-08  
**Governance:** [`docs/PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Progress ledger:** [`docs/PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Machine-readable checkpoint:** [`research/results/project-progress-checkpoint-2026-08-25.json`](../research/results/project-progress-checkpoint-2026-08-25.json)

This document is the canonical human-readable status of the project. Historical plans, attempts and intermediate states remain preserved as evidence but do not override this checkpoint.

## Executive summary

The Benchmark Integrity Gate is closed and the P12 evaluation protocol is `FROZEN`.

```text
P12-C1   CLOSED / DETERMINISTIC FAIL / NO ARM QUALIFIED
P12-C2   CONSUMED_OPERATIONAL_FAILURE / 31 OF 36 / NO SCORING
P12-C3   CONSUMED_TERMINAL_OPERATIONAL_FAILURE / 3 OF 36 / NO SCORING
P12-C4   PROVIDER QUALIFICATION BLOCKED / SYNTHETIC OPERATIONAL FAIL / 0 OF 36
Cerebras numeric capacity            PASS
Cerebras generation access           FAIL / HTTP 402 PAYMENT_REQUIRED
current QUALIFIED implementation     NONE
current PREFERRED implementation     NONE
semantic v4.2                        NOT AUTHORIZED
FRESH_BLIND                          NO SOURCE AUTHORIZED
LEGACY_LOCKED_TEST                   ACCESS BLOCKED
final architecture                   UNFROZEN
production-readiness claim           NOT AUTHORIZED
```

The project is currently in **Phase 3: P12-C4 provider qualification / experiment readiness**. It has not yet entered C4 benchmark collection or candidate qualification.

## Completed foundations

### Governance and benchmark integrity

| Milestone | State |
|---|---|
| BIG-B0 benchmark integrity audit | COMPLETE |
| BIG-B1 exposure/contamination ledger | COMPLETE |
| BIG-B2 benchmark-design alternatives | COMPLETE |
| BIG-B3 protocol selection | COMPLETE |
| BIG-B4 protocol freeze | COMPLETE / `FROZEN` |
| Historical candidate/component reinterpretation | COMPLETE |

### Prospective P12 history

| Experiment | State | Complete packet | Scoring | Scientific conclusion |
|---|---|---:|---|---|
| P12-C1 | CLOSED / deterministic fail | 36 parents / 72 outputs | COMPLETE | no arm qualified |
| P12-C2 | CONSUMED_OPERATIONAL_FAILURE | 31/36 parents | BLOCKED | none |
| P12-C3 | CONSUMED_TERMINAL_OPERATIONAL_FAILURE | 3/36 parents | BLOCKED | none |
| P12-C4 | PROVIDER QUALIFICATION BLOCKED | 0/36 parents | BLOCKED | none |

C1/C2/C3 remain consumed. Their partial outputs, scores and live seeds may not be reused to form a confirmatory C4 packet.

## P12-C4 preparation completed

The provider-capacity ADR is `ACCEPTED` with `CONDITIONAL_GO_TO_P12_C4_PREREGISTRATION`. Cerebras + `gpt-oss-120b` is a temporary experimental serving path, not a frozen production provider.

Completed provider-free / account-level work includes:

- fresh C4 seed map frozen with no C1/C2/C3 live-seed reuse;
- serving contract frozen: `cerebras_cloud_sdk==1.91.0`, no warming, retries or failover;
- `temperature=0`, `reasoning_effort=medium`, hidden reasoning, strict JSON schema and 4096 completion budget frozen;
- prompt sizing completed for all 36 parents;
- maximum conservative prompt bound = 3,284 tokens;
- maximum reserved admission/request = 7,380 tokens;
- full 36-parent reserved upper bound = 265,002 tokens;
- minimum pacing = 75 seconds between provider requests;
- effective numeric account/project limits attested: 5 RPM, 30k uncached TPM, 90k total TPM, 1M TPH, 1M TPD;
- authenticated model-catalog access to `gpt-oss-120b` confirmed;
- one-shot synthetic authorization frozen.

## P12-C4 synthetic live probe — operational failure

The one-shot live workflow was:

```text
workflow        research-p12-c4-cerebras-synthetic-live-probe
run             32901958789
run attempt     1
job             97977601612
head            9e0a89e1959dcc4ffd659baef1a4f07e137a7245
preflight       PASS
SDK pin         PASS
live execution  FAIL
```

The first preregistered synthetic provider request reached Cerebras and failed with:

```text
HTTP 402
error type: payment_required_error
code:       payment_required
param:      quota
message:    Payment required to access this resource. Visit your billing tab.
```

Consequences:

```text
provider request attempts observed   1
successful generation calls          0
model outputs observed                0
first synthetic probe complete       false
second synthetic request attempted   false
benchmark inputs loaded               0
private-oracle accesses               0
FRESH_BLIND accesses                  0
LEGACY_LOCKED_TEST accesses           0
```

The authorization attempt is **consumed**. The same workflow run or authorization must not be rerun/reused.

Canonical closure:

- `research/results/p12-c4-cerebras-synthetic-live-probe-closure-2026-08-25.json`

## Correct interpretation of the account attestation

The previous account attestation remains valid historical evidence for:

- first-party organization/project numeric limits;
- API-key authentication;
- model catalog accessibility.

It is **not sufficient evidence of active generation access** after the live endpoint returned HTTP 402.

Before any new synthetic attempt or benchmark generation, new first-party evidence must establish that billing/trial/developer generation access is active. No secret or payment credential may be committed.

## Current blockers

### CRITICAL — Cerebras generation/billing access

Numeric quota is sufficient, but live Chat Completions generation is not currently available to this account/key context. This blocks the synthetic compatibility gate and therefore all P12-C4 activation and EXPOSED_POOL generation.

### CRITICAL — FRESH_BLIND source not authorized

Current state: `NO_SOURCE_AUTHORIZED`. Tier A target remains 2026-08-25 23:59 BRT. If not operational by the frozen cutoff, planning transitions to the Tier B independently authored fallback, with 2026-08-28 23:59 BRT as the fallback deadline.

### HIGH — no qualified current candidate

C1 failed scientifically. C2/C3 failed operationally before complete measurement. C4 has not begun benchmark generation.

### HIGH — architecture remains unfrozen

Retrieval/RAG, reranking, multi-agent decomposition, persistent memory, observability, final provider, deployment and UI remain open. This is intentional until candidate evidence supports a freeze.

## Immediate critical path

The next valid sequence is:

```text
1. first-party generation/billing activation evidence
2. narrow pre-outcome infrastructure amendment
3. provider-free validation of the amended one-shot path
4. new one-shot synthetic authorization only if all gates PASS
5. exactly 2 preregistered synthetic calls → PASS required
6. full provider-free C4 activation
7. C4 live manifest freeze
8. exactly 36/36 common parents
9. local A00/A10/A01/A11 expansion → exactly 144/144 outputs
10. packet freeze
11. deterministic gates → 20k bootstrap → LOGO → slices/failure analysis
12. semantic child gate for deterministic survivors only
13. production-fit decision + generation freeze
14. separately authorized FRESH_BLIND measurement
15. architecture freeze → regression → documentation → delivery
```

Hard rules:

- same failed synthetic authorization/run: **no rerun**;
- no EXPOSED_POOL call before synthetic PASS + activation PASS + live manifest freeze;
- no partial scoring;
- no semantic evaluation before deterministic survival;
- no FRESH_BLIND outcome access before candidate/evaluator generation freeze and separate authorization;
- no production-readiness or final-architecture claim before evidence supports it.

## Parallel work allowed now

Only work that cannot contaminate or bypass the experimental path should proceed in parallel:

1. FRESH_BLIND source/custody/authorization preparation without outcome exposure;
2. canonical documentation and reproducibility maintenance;
3. provider-free preparation for a narrow access-remediation amendment;
4. production-fit research that does not freeze final architecture prematurely.

## Explicit non-claims

The project currently has **no** qualified/preferred candidate, successful C2/C3/C4 factorial comparison, semantic-v4.2 pass, authorized FRESH_BLIND source, final LOCKED_TEST authorization, frozen production architecture or production-readiness evidence.

Infrastructure and access checks validate only what they explicitly test.
