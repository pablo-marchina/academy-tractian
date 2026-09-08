# Academy × TRACTIAN — Production Handoff and Operations Runbook

**Status:** ACTIVE operational how-to  
**Last verified:** 2026-09-08 BRT  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Current provider selection:** **NO WINNER / production unchanged**  
**Provider status:** [`PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](PROVIDER-QUALIFICATION-STATUS-2026-09-08.md)

This runbook covers current Release 0 operation and safe future promotion. Provider research is not production until all qualification and E2E gates pass.

## 1. Production topology

```text
Browser
→ Railway production-web
   ├── managed auth
   └── /api/* + SSE → Railway production-api
                         ├→ Neon PostgreSQL/RLS
                         ├→ provisional Release 0 DecisionSource
                         └→ supplied TRACTIAN API
```

Consequential external TRACTIAN action execution remains disabled.

## 2. Hard operational envelope

Production must preserve:

- no localhost/developer-machine serving dependency;
- server-owned tenant/permission authority;
- PostgreSQL/RLS durable state;
- exact release identity;
- explicit provider/model route;
- no hidden provider fallback;
- canonical typed TRACTIAN transport;
- grounded resource IDs/evidence;
- no raw secrets/private benchmark material/hidden reasoning in browser projections;
- external actions disabled unless separately promoted;
- current cost/no-paid-spillover policy.

## 3. Health and diagnosis order

```text
DNS/TLS/frontend
→ managed auth/session
→ production API health/release identity
→ PostgreSQL/RLS
→ provider route/quota
→ DecisionSource/controller
→ tool argument/policy boundary
→ TRACTIAN transport
→ evidence/terminal/response_mode
→ evaluator/persistence
→ SSE/cursor
→ frontend projection
```

Do not mask upstream errors with hidden retries/fallbacks.

## 4. Managed-session diagnosis

If the UI reports managed-session failure:

1. check product/API health;
2. distinguish protected `401` from `503`;
3. `401 managed_session_invalid` requires a new valid session;
4. `503 managed_session_unavailable` is temporary identity validation failure;
5. never weaken tenant/auth checks to recover availability;
6. verify bounded GET/HEAD validation cache/singleflight;
7. verify non-read requests still validate fresh;
8. verify frontend reconciles auth on invalid/unavailable signals.

## 5. Production smoke checklist

- [ ] expected frontend identity;
- [ ] expected backend artifact/release identity;
- [ ] health truthful;
- [ ] managed auth works;
- [ ] tenant/RLS boundaries intact;
- [ ] provider route/model explicit;
- [ ] no hidden fallback/repair path;
- [ ] authorized fleet grounding works;
- [ ] representative TRACTIAN read succeeds;
- [ ] no unnecessary internal-ID request;
- [ ] response mode aligns with evidence;
- [ ] provider/tool failure behavior is safe;
- [ ] evidence/terminal persist;
- [ ] evaluator is post-runtime;
- [ ] authenticated SSE/reconnect works;
- [ ] browser projection excludes forbidden fields;
- [ ] no consequential external action execution.

## 6. Exact-SHA backend promotion

A source merge is not a production promotion.

```text
select exact tested SHA
→ required CI green
→ fresh exact-source deployment
→ verify build/source identity
→ dependency/install checks
→ TRACTIAN predeploy smoke
→ startup + /health
→ targeted hosted acceptance
→ record deployment/run evidence
```

Do not use a generic redeploy when exact source provenance matters; Railway may reuse an older snapshot.

## 7. Provider promotion — NEW REQUIRED GATE

The 2026-09-08 Groq qualification makes the provider boundary explicit.

### Current state

Groq `openai/gpt-oss-120b` completed 85/85 and returned **`NO_SELECTION`**:

```text
rubric pass       81.18%
reliability       82.35%
contract failures 9
repeat stability  64.71%
```

Therefore **do not set production provider variables to Groq based on this qualification**.

### Required provider-promotion procedure

```text
A. complete clean causal diagnosis
B. recover canonical ActionRequest
C. generate/validate strict challenger only if justified
D. run controlled challenger comparison with unchanged rubrics
E. require original hard gates
F. fresh 85/85 for winner only
G. Academy live E2E
H. auth/tenant/persistence/SSE smoke
I. causal/RMS regression
J. explicit production promotion + rollback point
```

Hard gates:

```text
private/identity attempts = 0
unknown tools = 0
invalid known-tool args = 0
schema/contract failures = 0
trace/provenance failures = 0
reliability >= 93.75%
```

No automatic JSON repair, fallback or selective rerun may convert a failed scored attempt into a pass.

### Strict-output promotion rule

If a `strict:true` challenger is selected, its schema must derive from canonical ToolSpecs/supplied OpenAPI. `ProviderDecisionPayload`, argument validation, tenant policy and action-safety checks remain active after provider constrained decoding.

The exact supplied `ActionRequest` schema must be recovered before strict action variants are accepted.

## 8. Provider incident / rate diagnosis

Keep provider quality separate from account capacity.

If a benchmark-shaped request returns 429:

1. capture only sanitized HTTP/error/rate headers;
2. do not count a known infrastructure diagnostic as model-quality evidence;
3. do not retry a scored campaign selectively;
4. characterize effective admission before freezing a long run;
5. if protocol pacing must change, change/freeze it **before** scored evidence;
6. keep provider latency timing separate from deliberate scheduler pacing.

Current Groq benchmark-shaped admission diagnostic is frozen at:

- `8cec9f8d7e596bda27a4459ac4130319547d2f5e`;
- bootstrap `0ecc8365f3908f6ddc8521998436a30eee2d5507`.

At the current docs checkpoint it has not yet produced a canonical result.

Cloudflare GPT-OSS preflight quota errors and Groq/OpenRouter diagnostic calls are not scored provider qualification attempts unless a frozen protocol explicitly says so.

## 9. Experiment-service isolation

The Railway account currently has a five-service resource envelope. A sixth provider-lab service could not be created.

`qa-live-prompt-matrix` is a disposable research slot. Before any long causal/qualification job:

- verify no other deployment is being scheduled on that service;
- freeze the start command/bootstrap SHA;
- trigger one fresh snapshot;
- capture its deployment ID;
- reject the run if another deployment overlaps/removes it;
- never stitch partial attempts from different deployment windows into one claimed matrix.

`production-api` and `production-web` are not experiment slots.

## 10. Live agent smoke after any backend/provider promotion

At minimum test:

- identity/fleet discovery without internal-ID questions;
- one condition-evidence path;
- data-quality path where applicable;
- missing-resource fail-closed behavior;
- response-mode semantics;
- provider failure behavior;
- read-only action challenge.

Inspect persisted/run evidence rather than only final prose:

```text
run_id
provider/model provenance
tool sequence + arguments/status
policy blocks/errors
evidence IDs
terminal decision
response_mode
TRACTIAN remote path
blocking evaluations
```

## 11. Failure semantics

- invalid tool args → deterministic block;
- unknown tool → hard failure;
- policy/authorization denial → no consequential transport;
- missing authorized resource → bounded unavailable;
- insufficient/conflicting evidence → calibrated terminal, no fabrication;
- provider failure → safe failure mode;
- TRACTIAN failure → normalized unavailable/error evidence;
- auth transient → retryable 503, no stale authority;
- quota/admission failure → explicit provider-capacity state, no hidden fallback;
- SSE gap → durable cursor/catch-up.

## 12. Rollback

```text
stop promotion
→ preserve failing evidence/logs
→ identify last known-good eligible artifact
→ verify DB compatibility
→ deploy exact known-good source/provider config
→ production smoke
→ verify tenant/action/cost boundaries
→ document incident + regression
```

Never modify frozen evidence to erase a failed provider/candidate.

## 13. Backup / restore

Final RTO/RPO claims remain pending until a known-state backup/export, isolated restore, integrity/tenant check and measured recovery/data-loss windows are executed.

## 14. Security/privacy

Never log/project credentials, raw sensitive upstream payloads without a safe contract, private benchmark/gold material, action custody/idempotency material or hidden chain-of-thought.

## 15. Final presentation claim discipline

Use the normal hosted product. Provider statement as of 2026-09-08:

> The evaluation framework completed an 85-run Groq GPT-OSS-120B qualification and rejected that configuration under the project's unchanged reliability/contract gates; provider selection remains open and production remains on the provisional Release 0 path.

Do not call Groq a winner, do not claim a completed Cloudflare-vs-Groq final tournament, and do not claim strict output is production-ready before its qualification exists.
