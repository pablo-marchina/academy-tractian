# Academy × TRACTIAN — Current Project Action Plan

**Status:** ACTIVE / reviewed canonical macro plan  
**Planning checkpoint:** 2026-08-25 22:50 BRT  
**Final delivery target:** 2026-09-08  
**Current status:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Progress ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Machine checkpoint:** [`research/results/project-progress-checkpoint-2026-08-25.json`](../research/results/project-progress-checkpoint-2026-08-25.json)

## 1. Planning objective

Finish the project with the strongest defensible evidence obtainable under the frozen P12 governance while preserving scientific validity, production-first requirements and the 2026-09-08 delivery deadline.

The project should be managed as seven macro phases, not as isolated experiments.

## 2. Macro phases

| Phase | Objective | Current state |
|---|---|---|
| 1. Benchmark and governance foundation | Freeze evidence roles, benchmark integrity, evaluator and access rules | COMPLETE |
| 2. Prospective exploration C1-C3 | Learn scientifically and operationally which candidate directions/provider paths fail or survive | COMPLETE / consumed history |
| 3. P12-C4 provider qualification and readiness | Establish a viable, isolated serving path before benchmark generation | **CURRENT / BLOCKED ON GENERATION ACCESS** |
| 4. Complete candidate qualification | Obtain 36/36 parents, 144/144 outputs and deterministic evidence | PENDING |
| 5. Semantic and independent validation | Semantic child gate for survivors plus FRESH_BLIND final evidence | PENDING |
| 6. Production-fit decision and architecture freeze | Select runtime/components/provider/deployment from evidence | PENDING |
| 7. Integration, regression and delivery | Production-path integration, safety regression, docs and demo | PENDING |

## 3. Current starting point

```text
P12-C1    complete; both arms failed deterministic gates
P12-C2    consumed operational failure; 31/36 parents; no scoring
P12-C3    consumed terminal operational failure; 3/36 parents; no scoring
P12-C4    provider qualification blocked; 0/36 parents; no scoring
QUALIFIED candidate            none
PREFERRED candidate            none
FRESH_BLIND source             none authorized
LEGACY_LOCKED_TEST             blocked
architecture                   unfrozen
production-readiness           not authorized
```

Cerebras numeric capacity passed, but the first synthetic Chat Completions request failed with HTTP 402 `payment_required`. The one-shot authorization was consumed with 0 model outputs and the second synthetic call was not attempted.

## 4. Phase 3 — P12-C4 provider qualification / readiness — CURRENT

### Completed

- provider-capacity ADR accepted with Cerebras + `gpt-oss-120b` as conditional qualification path;
- provider/model/SDK/request contract frozen for qualification;
- no automatic failover, warming or retries;
- 36 fresh C4 seeds frozen;
- no C1/C2/C3 partial-parent or live-seed reuse;
- prompt token sizing completed;
- 75-second pacing frozen;
- effective numeric organization/project limits passed;
- API-key authentication and model catalog accessibility confirmed;
- one-shot synthetic authorization generated provider-free;
- first one-shot live run executed and closed honestly on HTTP 402.

### Current hard blocker

The account/key currently lacks proven active Chat Completions generation access despite sufficient numeric quota.

### Direct remediation sequence

1. Obtain **first-party evidence** that Cerebras billing/trial/developer generation access is active. Do not commit API keys, payment details or account identifiers unnecessarily.
2. Freeze a **narrow pre-outcome infrastructure amendment** documenting that the prior synthetic attempt produced no model output and that the same authorization/run remains consumed.
3. Amend the access gate so numeric quota, catalog access and actual generation-access evidence are distinct claims.
4. Run provider-free self-checks only.
5. If all amended gates pass, create a **new versioned one-shot synthetic authorization**. Do not rerun/reuse the old authorization.
6. Execute exactly the preregistered two-call compatibility probe.
7. Require `2/2 PASS`; any auth, billing, transport, schema or tool-semantic failure stops progression.

No EXPOSED_POOL generation is authorized during this remediation.

## 5. Phase 4 — complete P12-C4 candidate qualification

Only after the synthetic gate passes and a full provider-free activation package passes:

```text
synthetic PASS
      ↓
full provider-free C4 activation PASS
      ↓
live manifest freeze
      ↓
36 common-parent provider calls
```

Frozen execution principles:

- exactly 36 common parents;
- 75 seconds minimum between provider requests unless prospectively amended from new verified capacity evidence;
- no retries, warming or failover hidden from the experiment;
- same provider/model/request contract for the whole packet;
- no arm-specific provider calls;
- private-oracle accesses = 0;
- FRESH_BLIND accesses = 0;
- LEGACY_LOCKED_TEST accesses = 0.

### 36/36 gate

If any parent is missing, the experiment stops without scoring.

If 36/36 completes:

```text
36 frozen parents
     ↓
local deterministic expansion
     ↓
A00 / A10 / A01 / A11
     ↓
144 / 144 fixed outputs
     ↓
immutable packet freeze
```

No partial or complete-case scoring is permitted.

## 6. Phase 4 scoring order

Only after `144/144` is frozen:

1. deterministic scorer and absolute gates;
2. preregistered factorial/paired contrasts;
3. 20,000-resample asset/story-group cluster bootstrap;
4. all applicable LOGO analyses;
5. per-group and modality slices;
6. safety/failure-family analysis;
7. operational denominator/missingness report.

Decision:

- no deterministic survivor → semantic evaluation stops and project scope is reassessed honestly;
- survivor(s) → only those exact arms may enter a separately preregistered semantic child gate.

## 7. Phase 5 — semantic and independent validation

### Semantic child gate

Before seeing semantic labels, freeze:

- exact survivor arms;
- claim-packet construction;
- judge/model/config;
- metrics/thresholds;
- missingness/failure treatment;
- one-shot semantics.

Semantic PASS is necessary for progression but does not alone make a candidate final or production-ready.

### FRESH_BLIND — parallel now, measurement later

Current state: `NO_SOURCE_AUTHORIZED`.

Before generation freeze, candidate development may receive only non-semantic source/custody metadata. Hidden cases, expected paths, outcomes, labels and candidate-specific feedback remain inaccessible.

Schedule:

- Tier A target: **2026-08-25 23:59 BRT**;
- if Tier A is not operational, transition planning to Tier B without weakening independence;
- Tier B fallback deadline: **2026-08-28 23:59 BRT**.

Final FRESH_BLIND measurement is authorized only after candidate/evaluator generation freeze and a separate one-shot access authorization.

## 8. Phase 6 — production-fit decision and architecture freeze

Architecture research may continue in parallel, but final choices remain unfrozen until candidate evidence exists.

Material choices include:

- provider/model serving strategy;
- orchestration/runtime;
- retrieval/RAG vs simpler evidence routing;
- reranking/vector database need;
- single-agent vs multi-agent decomposition;
- persistent memory;
- observability backend;
- retry/idempotency/authorization boundaries;
- deployment topology;
- UI/demo architecture.

For each material choice, compare a simple baseline against credible alternatives on reliability, latency, cost, maintainability, observability, security and evidence impact.

Architecture freeze occurs only after:

1. deterministic candidate qualification;
2. required semantic PASS;
3. production-fit comparison;
4. generation/evaluator freeze;
5. independent-evidence plan remains intact.

## 9. Phase 7 — integration, regression and final delivery

Protect **2026-09-03 onward** primarily for integration and delivery work.

Required before final delivery:

- end-to-end production-path regression;
- deterministic safety/security regression;
- provider failure/recovery behavior;
- reproducible environment/secrets setup;
- observability evidence;
- deployment/runbook documentation;
- final architecture and ADR documentation;
- evaluation methodology/results narrative;
- explicit limitations/non-claims;
- production-path demo/presentation, not a mock path.

Final target: **2026-09-08**.

## 10. Near-term execution board

### Immediate — current blocker

1. Resolve Cerebras billing/generation-access state with first-party evidence.
2. Freeze the narrow pre-outcome amendment.
3. Pass amended provider-free gates.
4. Execute one new versioned one-shot synthetic probe only if authorized.
5. Do not begin C4 benchmark generation until synthetic `2/2 PASS`.

### Parallel right now

1. Continue FRESH_BLIND Tier A custody/authorization preparation without outcome exposure.
2. If Tier A misses 2026-08-25 23:59 BRT, move planning to Tier B immediately.
3. Maintain canonical documentation/reproducibility.
4. Continue production-fit research without final architecture freeze.

### After synthetic PASS

1. freeze C4 activation and live manifest;
2. execute exactly one 36-parent prospective collection;
3. freeze 36/36;
4. expand locally to 144/144;
5. score only the complete packet;
6. advance only deterministic survivors.

## 11. Stop / pivot rules

- no rerun/reuse of C1/C2/C3 consumed experiments;
- no rerun/reuse of the failed synthetic authorization/run;
- no new provider attempt without materially new generation-access evidence and a prospectively frozen amendment;
- no partial scoring;
- if a complete C4 prospective packet cannot be obtained on schedule, preserve failed evidence and reassess scope rather than force a result;
- if no independent FRESH_BLIND source can be authorized by the fallback deadline, downgrade the generalization claim explicitly;
- if no candidate passes deterministic/semantic gates, do not claim a production-ready final candidate;
- do not sacrifice the September integration/regression buffer for repeated low-feasibility live attempts.

## 12. Definition of success

Strongest target:

1. one complete P12-C4 packet exists;
2. at least one candidate passes deterministic and required semantic gates;
3. candidate selection is supported by production-fit comparison;
4. candidate/evaluator generation is frozen;
5. independent FRESH_BLIND evidence supports the intended generalization claim;
6. final architecture is frozen from evidence;
7. end-to-end regression, operational documentation and production-path demonstration are complete.

If external constraints prevent the full target, success becomes an **evidence-honest delivery**: preserve failed attempts, quantify remaining uncertainty and make only claims actually supported by the frozen evidence.
