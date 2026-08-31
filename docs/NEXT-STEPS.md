# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-31 — ADR-010/011 reuse audit complete; bounded Cloudflare execution adapter is the next justified task  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Frozen preregistration:** [`adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md`](adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md)  
**Frozen provider-free client:** [`adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md`](adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md)  
**Reuse audit:** [`ADR-010-011-REUSE-AUDIT-2026-08-31.md`](ADR-010-011-REUSE-AUDIT-2026-08-31.md)

This file is the short-horizon execution plan. It does not authorize provider inference, credential probing, customer mutation or C4 advancement.

## 1. Completed

```text
historical evidence audit                     DONE
current USD-0 provider fact refresh           DONE
four provider pre-benchmark factual gates     DONE
material D01 benchmark gap                    DEMONSTRATED
minimum Cloudflare comparison preregistration FROZEN / ADR-018
provider-free Cloudflare client               IMPLEMENTED + FROZEN / ADR-019
provider-free client/regression CI            PASS
ADR-010/011 execution/custody reuse audit     COMPLETE / ISSUE #73
provider/model inference calls                0
credential/account probes                     0
live network validation                       0
comparison attempts consumed                  0 / 32
```

Audit conclusion:

```text
ADR-010 historical live executor as-is        DO NOT EXECUTE
ADR-010 provider-neutral logic                 HIGH REUSE
ADR-011 historical live entrypoint as-is      DO NOT EXECUTE
ADR-011 custody/write-ahead invariants         HIGH REUSE
full executor redesign                        NOT JUSTIFIED
bounded Cloudflare v2 adapter                 JUSTIFIED
minimum demonstrated gaps                     7
```

## 2. NOW — separate provider-free Cloudflare executor/custody v2 implementation task

The next task may implement **only** the seven demonstrated gaps from the reuse audit. It must preserve ADR-010/011/018/019 frozen bytes and perform zero provider/model inference.

### Gap 1 — current-scope frozen bundle and plan

- pin ADR-018 design v2;
- reuse the unchanged public population SHA-256 `561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251`;
- pin ADR-019 Cloudflare client blob;
- include only:
  - `cloudflare_glm_4_7_flash_workers_free`;
  - `cloudflare_nemotron_3_120b_a12b_workers_free`;
- preserve 8 × 2 × 2 = 32 attempts and alternating candidate order;
- freeze a new v2 plan SHA rather than reusing historical ADR-010 plan identity.

### Gap 2 — result/summary v2 resource fields

Add only fields required by ADR-018:

- usage accounting completeness;
- observed input/output tokens;
- observed neurons per candidate and packet;
- actual cash-cost status, required USD 0;
- Cloudflare-specific M9 fields;
- explicit H8/H9/H10 outcomes/failure codes.

Do not persist raw provider request/response/exception material.

### Gap 3 — Cloudflare M8 + resource hard gates

Provider-free tests must prove:

```text
GLM input rate                5500 neurons / 1M input tokens
GLM output rate              36400 neurons / 1M output tokens
Nemotron input rate          45455 neurons / 1M input tokens
Nemotron output rate        136364 neurons / 1M output tokens
max prompt tokens / attempt   8000
max completion tokens          512
max packet neurons          7937.522688
```

Required behavior:

- missing exact usage → fail closed;
- observed prompt >8000 → stop before next attempt;
- observed completion >512 → stop before next attempt;
- cumulative observed neurons + frozen worst-case remaining-attempt neurons must fit available free allocation before next claim;
- paid spillover/nonfree route is disqualifying;
- incomplete accounting returns incomplete `NO_SELECTION`.

### Gap 4 — fixed provider-free Cloudflare M5 probes

Reuse the ADR-011 probe invariant, but run it against the exact ADR-019 client twice:

- GLM model configuration;
- Nemotron model configuration.

Each probe must prove one injected local failure, one invocation, zero retry/fallback, valid sanitized ADR-007 provenance and zero network calls.

### Gap 5 — exact Cloudflare live client factory

Provider-free construction only:

- explicit Cloudflare API token;
- explicit Cloudflare account ID;
- one generic `UrllibProviderJsonTransport` or byte-equivalent one-shot provider-neutral transport;
- exact ADR-019 client class;
- exact two model IDs;
- no environment lookup;
- no account/capability probe;
- no AI Gateway;
- no retry/fallback/warm-up.

### Gap 6 — current authorization/custody marker v2

Reuse ADR-011 custody properties:

- one canonical durable root;
- exclusive marker create;
- fixed internal `run/` directory;
- 32-entry sanitized ledger;
- `CLAIMED` fsync before network-capable invocation;
- claimed/uncertain attempt cannot replay;
- no automatic resume/reset;
- immutable sanitized result.

New marker must pin current Cloudflare execution identities rather than ADR-009/OpenAI/Gemini identities.

### Gap 7 — pre-live evidence gate interface

Implement provider-free validation of an **input evidence contract**, not a real Cloudflare probe.

Future execution must refuse attempt 1 unless separately frozen preflight evidence states/proves:

- Workers Free;
- Workers Paid not used;
- prepaid AI Gateway not used;
- >=9000 free neurons remain for the current UTC day;
- exact direct route/model/client identities;
- one canonical custody root.

The implementation task must not itself query the account or consume inference.

## 3. Reuse obligations — do not rewrite what is already proven

Reuse unchanged or preserve equivalent behavior for:

- public P01-P08 population/rubric;
- 32-attempt canonical sequential geometry;
- alternating order rule;
- provider-free null baseline;
- B1 validation;
- forbidden-key/private-key inspection;
- ADR-007 route/model/request/provenance validation;
- M1-M7 and M10 formulas;
- latency statistics and repeat stability;
- Pareto → quality margin → resource → latency → `NO_SELECTION` ordering;
- stdlib one-shot transport behavior;
- write-ahead custody/no-replay invariants;
- raw-material and secret non-persistence.

Do not edit historical ADR-010/011 implementation files merely to generalize them. Prefer new versioned adapter/executor/custody files that reuse safe provider-neutral primitives where practical.

## 4. Provider-free acceptance criteria for the next task

Before freezing the v2 execution adapter:

- zero provider/model inference;
- zero credential/account probe;
- zero live network validation;
- exact 32-entry plan generated with a new frozen SHA;
- deterministic tests for all seven gaps;
- both Cloudflare model configs pass fixed M5 injected-failure probes;
- missing usage and budget overflow paths fail closed;
- no secret/account ID appears in persisted evidence/repr/errors;
- historical ADR-010/011/018/019 blobs unchanged;
- current production/runtime/final-handoff regressions green.

## 5. AFTER IMPLEMENTATION — separate live-execution authorization

Even a fully validated v2 adapter still authorizes:

```text
provider/model inference      0
credential/account probes     0
comparison attempt 1          NO
production provider selection NO
```

A later separate task must freeze the operational preflight evidence and only then decide whether attempt 1 is admissible.

## 6. Historical/excluded roles remain unchanged

```text
Groq GPT-OSS                 HISTORICAL_CONTROL_ONLY
Gemini 3.7 Flash Free        PUBLIC/SYNTHETIC ONLY UNDER CURRENT DATA-USE BOUNDARY
Cloudflare Gemma 4 26B       EXCLUDED FROM MINIMUM FIRST PACKET
Ollama qwen3:4b              CONDITIONAL LOCAL BASELINE / OUTSIDE CORE PACKET
old ADR-008/#44 live packet  MUST NOT EXECUTE AS-IS
```

## 7. Agent topology — queued

The single-agent controller remains a strong qualified baseline. Do not implement planner→executor or critic/reviewer until the provider/model basis is selected or an honest provider `NO_SELECTION` is frozen.

## 8. Runtime/orchestration — queued

Do not restart generic runtime research. E6 already qualifies LangGraph and ADR-004 qualifies the explicit controller. Reopen only on a material reversal trigger after provider/topology evidence.

## 9. C4 — parallel unchanged track

Required exact artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
```

Only exact-byte recovery is authorized. No reconstruction, rescoring, substitution or downstream scientific gate advancement.

## 10. Ordered queue

```text
DONE      evidence audit
DONE      provider fact refresh
DONE      four factual gates
DONE      preregister/freeze minimum Cloudflare comparison
DONE      implement/validate/freeze provider-free Cloudflare client
DONE      audit ADR-010/011 reuse and isolate seven execution gaps
NOW       implement/validate/freeze bounded Cloudflare executor/custody v2 provider-free
THEN      separate live-execution authorization/preflight freeze
THEN      execute exact 32-attempt-max packet once
THEN      freeze candidate selection or honest NO_SELECTION
PARALLEL  exact C4 artifact recovery
LATER     topology comparison if still material
LATER     runtime/adaptive work only on reversal trigger/material gap
FINAL     integrate best-supported configuration + full regression + architecture freeze
```

## 11. Still forbidden

- any provider inference in the v2 implementation task;
- credential/account probing merely to prove availability/free quota;
- live network validation before separate live authorization;
- modifying frozen ADR-010/011/018/019 bytes to fit the new path;
- full executor rewrite when bounded reuse is sufficient;
- executing the old ADR-008/#44 OpenAI/Gemini packet;
- Paid Workers or prepaid AI Gateway;
- changing ADR-018 candidates/population/metrics/thresholds/budget without prospective amendment;
- Groq freshness reruns;
- hidden retries/fallbacks/warm-ups/provider state;
- weakening deterministic safety, `HarnessRunner` ownership or evaluator isolation;
- C4 reconstruction/rescoring;
- premature multi-agent/runtime implementation;
- final architecture or production-readiness claims before evidence supports them.
