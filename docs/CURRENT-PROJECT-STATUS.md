# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-26 11:10 BRT  
**Branch:** `research/systematic-foundation`  
**PR:** #2 — draft research-governance PR  
**Final delivery target:** 2026-09-08  
**Governance:** [`docs/PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Progress ledger:** [`docs/PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Machine-readable checkpoint:** [`research/results/project-progress-checkpoint-2026-08-26.json`](../research/results/project-progress-checkpoint-2026-08-26.json)

This document is the canonical human-readable project status. Historical plans, failed serving routes and consumed one-shot attempts remain preserved as evidence but do not authorize later gates.

## Executive summary

The Benchmark Integrity Gate is closed and the P12 protocol remains `FROZEN`.

```text
P12-C1   CLOSED / DETERMINISTIC FAIL / NO ARM QUALIFIED
P12-C2   CONSUMED_OPERATIONAL_FAILURE / 31 OF 36 / NO SCORING
P12-C3   CONSUMED_TERMINAL_OPERATIONAL_FAILURE / 3 OF 36 / NO SCORING
P12-C4   PROVIDER QUALIFICATION BLOCKED / 0 OF 36 / 0 OF 144 / NO SCORING

Cerebras synthetic route     CONSUMED_OPERATIONAL_FAILURE_NO_MODEL_OUTPUT / HTTP 402
OpenRouter synthetic route   CONSUMED_OPERATIONAL_FAILURE_NO_MODEL_OUTPUT / HTTP 404 FREE VARIANT UNAVAILABLE

current QUALIFIED implementation     NONE
current PREFERRED implementation     NONE
semantic v4.2                        NOT AUTHORIZED
FRESH_BLIND                          NO SOURCE AUTHORIZED
LEGACY_LOCKED_TEST                   ACCESS BLOCKED
final architecture                   UNFROZEN
production-readiness claim           NOT AUTHORIZED
```

The project is still in **Phase 3 — P12-C4 provider qualification and readiness**. Benchmark generation has not started. The current blocking question is now narrower: **qualify a new no-card serving route prospectively before any EXPOSED_POOL call**.

## Completed foundations

The benchmark-integrity work, P12 protocol freeze, evidence partitions, deterministic evaluator infrastructure, fresh C4 seed map, complete-packet-only scoring rules and statistical contract remain valid.

P12-C1/C2/C3 remain consumed and may not be rerun or repackaged. No C2/C3 partial parent or live seed may be reused to form a confirmatory C4 packet.

## C4 serving-route history

### Cerebras — consumed before model output

The Cerebras path passed provider-free checks and numeric-capacity attestation, but the one-shot live synthetic run `32901958789` received HTTP 402 `payment_required` on its first request. There were zero model outputs and the second synthetic request was not attempted.

Canonical closure:

- `research/results/p12-c4-cerebras-synthetic-live-probe-closure-2026-08-25.json`

The Cerebras authorization and workflow run are consumed and may not be rerun/reused.

### OpenRouter + OpenInference — consumed before model output

ADR-002 prospectively selected the no-card route:

```text
gateway             OpenRouter
model               openai/gpt-oss-120b:free
upstream provider   OpenInference only
provider fallback   false
model fallback      none
application retries 0
transport            httpx==0.28.1
minimum pacing       75 seconds
```

The provider-free qualification completed successfully in run `32977533642`. It generated a distinct one-shot authorization that was committed at head `2e73bb22a391a8a5180047a1b4e4d57f74012546`.

The resulting live synthetic run was:

```text
workflow        research-p12-c4-openrouter-synthetic-live-probe
run             32977791243
run attempt     1
job             98206680887
preflight       PASS
httpx pin       PASS
first request   HTTP 404
model outputs   0
second request  NOT ATTEMPTED
```

The provider returned:

```text
This model is unavailable for free. The paid version is available now - use this slug instead: openai/gpt-oss-120b
```

Consequences:

```text
provider request attempts      1
successful HTTP responses      0
model outputs observed         0
automatic retries              0
provider fallbacks             0
model fallbacks                0
benchmark inputs loaded        0
private-oracle accesses        0
FRESH_BLIND accesses           0
LEGACY_LOCKED_TEST accesses    0
```

The one-shot OpenRouter authorization is now **consumed**. The same authorization/workflow run must not be rerun or reinterpreted.

Canonical closure:

- `research/results/p12-c4-openrouter-synthetic-live-probe-closure-2026-08-26.json`

The raw Actions artifact is intentionally not committed because it contains a provider-assigned user identifier. The canonical closure preserves hashes/provenance without that identifier.

## Current critical path

```text
new no-card provider route identified
        ↓
prospective ADR amendment
        ↓
provider/model/transport/request contract frozen
        ↓
provider-free compatibility gate PASS
        ↓
NEW one-shot synthetic authorization
        ↓
exactly 2 preregistered synthetic calls
        ↓
2 / 2 PASS ?
   ┌────────────┐
   │ no         │ yes
   ▼            ▼
 STOP      full provider-free C4 activation
                 ↓
           live manifest freeze
                 ↓
            36 / 36 parents
                 ↓
        local A00/A10/A01/A11 expansion
                 ↓
           144 / 144 outputs
                 ↓
             packet freeze
                 ↓
 deterministic gates → 20k bootstrap → LOGO → slices/failure analysis
```

No shortcut around this sequence is authorized.

## Parallel work

FRESH_BLIND source/custody preparation may continue without outcome exposure. Canonical documentation, reproducibility work and production-fit research may also continue, but final architecture must remain unfrozen until candidate evidence supports a decision.

## Hard rules

- no reuse or rerun of the consumed Cerebras or OpenRouter synthetic authorizations;
- no EXPOSED_POOL provider call before a new synthetic 2/2 PASS, full activation PASS and live-manifest freeze;
- C4 must reach exactly 36/36 common parents and 144/144 fixed arm outputs before scoring;
- no partial/complete-case scoring;
- semantic evaluation only for deterministic survivors;
- no FRESH_BLIND outcome access before candidate/evaluator generation freeze and separate authorization;
- no production-readiness or final-architecture claim before supporting evidence exists.

## Explicit non-claims

The project currently has no qualified/preferred candidate, no successful C4 packet, no semantic-v4.2 pass, no authorized FRESH_BLIND source, no final LOCKED_TEST authorization, no frozen production architecture and no production-readiness evidence.
