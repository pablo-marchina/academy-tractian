# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-23 23:50 BRT  
**Branch:** `research/systematic-foundation`  
**PR:** #2 — draft research-governance PR  
**Final delivery target:** 2026-09-08  
**Governance:** [`docs/PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This document is the canonical human-readable status of the project. Historical plans and experiments remain preserved as evidence, but they do not override this checkpoint.

## Executive summary

The Benchmark Integrity Gate is closed and the P12 evaluation protocol is `FROZEN`.

```text
P12-C1   CLOSED / DETERMINISTIC FAIL / NO ARM QUALIFIED
P12-C2   CONSUMED_OPERATIONAL_FAILURE / NO SCORING
P12-C3   CONSUMED_TERMINAL_OPERATIONAL_FAILURE / NO SCORING
current QUALIFIED implementation     NONE
current PREFERRED implementation     NONE
semantic v4.2                        NOT AUTHORIZED
FRESH_BLIND                          NO SOURCE AUTHORIZED
LEGACY_LOCKED_TEST                   ACCESS BLOCKED
final architecture                   UNFROZEN
production-readiness claim           NOT AUTHORIZED
```

P12-C1 completed a valid prospective deterministic comparison, but both arms failed the frozen gates. P12-C2 failed operationally after 31/36 common parents. P12-C3 prospectively introduced capacity control, passed provider-free activation and live-infrastructure qualification, reached live execution, accepted three common parents, and then entered a frozen terminal experiment state on the fourth cell. No 36-parent/144-output packet exists for C2 or C3, so no deterministic, semantic or arm-level conclusion may be inferred from their partial collections.

The largest schedule risks are now **provider-capacity reliability** and **absence of an authorized FRESH_BLIND source**.

## Governance milestones

| Milestone | State |
|---|---|
| BIG-B0 benchmark integrity audit | COMPLETE |
| BIG-B1 exposure/contamination ledger | COMPLETE |
| BIG-B2 benchmark-design alternatives | COMPLETE |
| BIG-B3 protocol selection | COMPLETE |
| BIG-B4 protocol freeze | COMPLETE / `FROZEN` |
| Historical candidate reinterpretation | COMPLETE |
| P12-C1 | CLOSED |
| P12-C2 | CONSUMED_OPERATIONAL_FAILURE |
| P12-C3 | CONSUMED_TERMINAL_OPERATIONAL_FAILURE |

## Evidence partitions under P12

### EXPOSED_POOL

Historical DEV + VALIDATION, seven independent asset/story groups. Allowed for adaptive development, ablation, evaluator qualification, failure analysis and candidate comparison. It cannot support an independent generalization claim.

### FRESH_BLIND

Primary independent real-domain evidence. Current state: `NO_BLIND_SOURCE_AUTHORIZED`.

This is now a critical-path dependency. Source preparation and access control should progress in parallel with EXPOSED_POOL development, while outcomes remain inaccessible to candidate development.

### LEGACY_LOCKED_TEST

Qualified supplementary held-out characterization only. Candidate execution remains blocked until separately authorized final access.

### SYNTHETIC_ADVERSARIAL

Evaluator/judge qualification, robustness and regression only.

## Historical implementation evidence

The only project-level `FROZEN` technical choice is the P12 evaluation protocol itself. Historical implementation components remain evidence-backed building blocks, not final architecture.

Retained/qualified foundations include ScenarioSchema, Canonical ToolSpec, TraceSchema, deterministic replay, HarnessRunner/HttpxTransport, LangGraph runtime candidate, native ToolSpec envelope, MCP-compatible adapter, E9 v4.1, E9 v4.2, E14c/d/e, E14n v1.1, E14p and E14q/E14q2.

No historical implementation is currently `PREFERRED` at project level.

## P12-C1

`P12-C1_EXPOSED_POOL_EVIDENCE_ROUTE_SELECTION` completed 36 common parents and 72 fixed outputs.

| Metric | C0 | C1 | C1 − C0 |
|---|---:|---:|---:|
| Evidence correctness | 0.2619 | 0.0833 | -0.1786 |
| Expected-read recall | 0.7322 | 0.6151 | -0.1171 |
| Extra public reads | 3.9643 | 3.5714 | -0.3929 |
| Decision correctness | 0.7857 | 0.7857 | 0 |
| Action correctness | 0.7143 | 0.7143 | 0 |
| Escalation correctness | 0.9286 | 0.9286 | 0 |
| Confirmed hard-safety violations | 3 | 3 | 0 |

Both arms failed deterministic gates. C1 reduced read count but worsened recall without improving decision/action/escalation quality.

Canonical evidence: `research/results/p12-c1-deterministic-paired-result-2026-08-23.json`.

## P12-C2

`P12-C2_EXPOSED_POOL_FACTORIAL_EVIDENCE_SAFETY` required 36 common parents and 144 fixed factorial outputs.

Live run `32663659575`:

```text
common parents attempted            36
common parents successful           31
common parents failed                5
failure family       rate_limit_long_window
36/36 freeze                       FAIL
144-output packet             NOT CREATED
private scoring                NOT EXECUTED
bootstrap / LOGO               NOT EXECUTED
```

Decision: `CONSUMED_OPERATIONAL_FAILURE`. Canonical closure: `research/results/p12-c2-live-cycle-closure-2026-08-23.json`.

## P12-C3

`P12-C3_EXPOSED_POOL_CAPACITY_CONTROLLED_FACTORIAL` preserved A00/A10/A01/A11 and changed only the prospective operational collection protocol.

Frozen collection contract:

```text
6 fixed batches × 6 parents
30 s minimum request spacing
30 s reset safety margin
max 3 pre-output attempts/cell
72 h horizon
completed parents immutable
resume = pending predeclared cells only
private scoring blocked until 36/36 + 144/144
partial/complete-case analysis forbidden
```

Provider-free activation and live-infrastructure qualification passed before live execution.

### Initial B1 pre-provider failure

Run `32671370930` made 0 provider requests and observed 0 candidate outcomes. It stopped on a retained E14l transport-invariant compatibility assertion. A narrow pre-outcome infrastructure amendment was frozen and provider-free qualified without changing candidate/model/prompt/evaluator/seeds/batch map/metrics/gates.

Effective runner SHA-256:

`07808b140d5f90211d5c3445988b46983754825303cbb66123255143094e08be`

Qualification runs: `32671829920` and `32672049576`.

### Continued B1 terminal failure

Trigger head: `d952113ef96f668b5e2e5692607f189404eae126`  
Run: `32672167702`

Sanitized checkpoint:

```text
completed cells                 3
pending cells                  33
transport failures              1
rate-limit events               1
batch complete              false
all 36 complete             false
terminal failure             true
horizon expired             false
first live call       2026-08-23T23:00:30.073807Z
horizon deadline      2026-08-26T23:00:30.073807Z
```

Artifacts:

- sanitized handoff `9501780930`, digest `sha256:e876709f13f36f0df3202a1ebd0c2feb1452e8483963915e1c56945316ad247c`;
- private checkpoint `9501780767`, digest `sha256:9189c8b840040b782b3e4ec8ef4dcc9450fa383d32804deb600b518c4df0d917` (raw checkpoint is not committed).

Decision:

```text
P12-C3 state                CONSUMED_TERMINAL_OPERATIONAL_FAILURE
36/36 freeze                NOT REACHED
144/144 packet              NOT CREATED
private scoring             NOT EXECUTED
semantic v4.2               NOT AUTHORIZED
qualified arms              NONE ESTABLISHED
preferred arm               NONE
same-experiment resume      FORBIDDEN
```

Canonical closure:

- `research/results/p12-c3-live-cycle-closure-2026-08-23.json`
- `research/p12-c3-live-cycle-closure-2026-08-23.md`

## Current blockers and risks

### CRITICAL — provider capacity

Two consecutive prospective experiments failed operationally during provider collection: C2 at 31/36 and C3 at 3/36. A new experiment must not simply repeat C3; provider capacity is now a material decision requiring alternative comparison before preregistration.

### CRITICAL — no authorized FRESH_BLIND source

P12 requires fresh independent real-domain evidence for the primary generalization claim. Preparation should progress in parallel while preserving strict outcome blindness.

### HIGH — no qualified current candidate

C1 failed scientifically. C2/C3 failed operationally before complete measurement.

### HIGH — architecture decision debt

Retrieval/RAG, reranking, multi-agent decomposition, persistent memory, observability backend and final deployment/UI choices remain unfrozen.

### HIGH — schedule

Final delivery is 2026-09-08. Time must remain for independent evidence, production-fit validation, integration/regression and documentation.

## Explicit non-claims

The project does not currently have a qualified/preferred final candidate, a successful C2/C3 factorial comparison, a current semantic v4.2 pass, an authorized FRESH_BLIND source, final LOCKED_TEST authorization, a frozen production architecture or production-readiness evidence.

Infrastructure gates and dry runs validate plumbing only.

## Canonical next step

See [`docs/PROJECT-PLAN.md`](PROJECT-PLAN.md).

The prior E14v-era plan is preserved at `docs/archive/PROJECT-PLAN-2026-08-20.md`.
