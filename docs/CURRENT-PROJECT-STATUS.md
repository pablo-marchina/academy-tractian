# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-09-01 — Cloudflare live-execution authorization protocol frozen by ADR-021  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Evidence-first gate:** [`EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md`](EVIDENCE-AUDIT-BEFORE-EXPERIMENTS.md)  
**Frozen comparison:** [`adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md`](adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md)  
**Frozen client:** [`adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md`](adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md)  
**Frozen executor/custody:** [`adr/020-cloudflare-executor-custody-v2-provider-free-implementation-2026-09-01.md`](adr/020-cloudflare-executor-custody-v2-provider-free-implementation-2026-09-01.md)  
**Frozen authorization protocol:** [`adr/021-cloudflare-live-execution-authorization-protocol-2026-09-01.md`](adr/021-cloudflare-live-execution-authorization-protocol-2026-09-01.md)  
**Immediate plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)

This is the sole canonical human-readable current authorization state. Historical frozen ADRs/artifacts remain authoritative for their exact scopes.

## Executive state

```text
external API / hosted-service project cost      USD 0 HARD CONSTRAINT
evidence audit before new experiment             REQUIRED

historical evidence audit                        COMPLETE
provider factual refresh                         COMPLETE
Cloudflare comparison preregistration             FROZEN / ADR-018
Cloudflare provider client                        FROZEN / ADR-019
Cloudflare executor/custody v2                    FROZEN / ADR-020
Cloudflare live authorization protocol            FROZEN / ADR-021

provider/model inference calls                    0
credential/account probes                         0
live network validation                           0
comparison attempts consumed                      0 / 32
real Cloudflare dashboard evidence captured       NO
real authorization receipt issued                 NO
real Cloudflare credentials provisioned           NO
attempt 1 authorized                              NO
production provider/model selected                NO

candidate 1  @cf/zai-org/glm-4.7-flash
candidate 2  @cf/nvidia/nemotron-3-120b-a12b
plan SHA     092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb
population   8 public probes × 2 repeats × 2 candidates
max calls    32
packet max   7937.522688 neurons
Free daily   10000 neurons
start gate   >=9000 neurons remaining

Workers Paid                         FORBIDDEN
AI Gateway / prepaid unified billing FORBIDDEN
hidden retry/fallback/warm-up        FORBIDDEN
parallel live calls                  FORBIDDEN
provider-native tool execution       FORBIDDEN
claimed/uncertain replay             FORBIDDEN
```

## 1. Evidence-first D01 sequence

```text
historical evidence audit                         DONE
current USD-0 factual refresh                     DONE
minimum provider gap demonstrated                 DONE
comparison preregistration                        FROZEN / ADR-018
Cloudflare direct client                          FROZEN / ADR-019
ADR-010/011 reuse audit                           DONE
executor/custody v2 provider-free                 FROZEN / ADR-020
live authorization protocol provider-free         FROZEN / ADR-021
                                                    ↓
fresh real manual account/dashboard evidence      PENDING USER/ACCOUNT SIDE
                                                    ↓
short-lived authorization receipt                 NOT ISSUED
                                                    ↓
secure token/account-ID provisioning               NOT DONE
                                                    ↓
final receipt/root/evidence validation             NOT DONE
                                                    ↓
attempt 1                                          NOT AUTHORIZED
```

No step may be skipped merely because credentials become available.

## 2. ADR-018 scientific contract

Frozen and unchanged:

```text
models        GLM 4.7 Flash / Nemotron 3 120B A12B
population    SHA-256 561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251
geometry      8 × 2 × 2 = 32 max live attempts
input ceiling 8000 accounted tokens / attempt
output max    512 tokens / attempt
packet max    7937.522688 neurons
selection     Pareto / NO_SELECTION permitted
```

No candidate, metric, threshold, population or resource budget changed in ADR-021.

## 3. ADR-019 client

Frozen direct Workers AI client:

```text
src/academy_tractian/cloudflare_provider_client.py
a5c814b519584b6d4346e3b0567bbc3da8ba0bf4
```

Properties remain: exact two-model allowlist, direct route, explicit credentials, injected transport, zero retry/fallback/warm-up, strict JSON schema, no provider-native tool execution and no usage fabrication.

## 4. ADR-020 executor/custody

Frozen implementation identities remain unchanged:

```text
comparison v2  e12b1dfa03eb1c50bc97848821235ef422516092
live/custody   70d8e0ccc4d4eb003d78cdd152b1dffd30b43f29
provenance v2  e7f8bdc60910ef0acf7b14c71616448338eeefc2
```

ADR-020 preserves ADR-010/011 provider-neutral behavior: public P01-P08, B1, M1-M7/M10, one-shot calls, exact usage/neurons, H8-H10, durable 32-entry ledger, `CLAIMED` before network-capable invocation, uncertain/no-replay and sanitized immutable result.

## 5. ADR-021 authorization protocol

ADR-021 freezes **authorization capability, not a real authorization**.

Exact authorization gates:

```text
manual Workers AI dashboard observation          REQUIRED
source artifact retained outside repo            REQUIRED
source artifact SHA-256 in sanitized evidence    REQUIRED
Workers plan                                     Workers Free
Workers Paid                                     false
free neurons remaining                           >=9000
used + remaining                                 10000
same UTC day                                     REQUIRED
evidence maximum age                             600 seconds
receipt maximum lifetime                         300 seconds
receipt <= evidence validity                     REQUIRED
direct Workers AI route                          true
AI Gateway route                                 false
prepaid/unified billing route                    false
cf-aig-gateway-id                                absent
comparison attempts consumed                     0
exclusive Workers AI usage window                attested
provider inference used to obtain evidence       0
credential/account probe used for evidence       0
```

The receipt is cryptographically bound to:

- canonical evidence SHA-256;
- one canonical custody-root SHA-256;
- ADR-018/019/020 frozen blobs;
- plan SHA;
- direct Cloudflare route;
- exact two `@cf/...` model IDs;
- one UTC-day/freshness window.

It stores neither token, account ID nor raw local custody path.

## 6. Secret policy

Credentials are intentionally provisioned **after** a valid receipt exists.

Frozen policy:

```text
API token permission      Account > Workers AI > Read
resource scope            exact target account only
AI Gateway permissions    not required / should not be granted
Global API Key            forbidden
credential probing        forbidden
secret persistence        forbidden
```

Connected credentials alone never authorize execution.

## 7. Canonical future receipt command

Only after fresh real evidence exists:

```text
python scripts/research/issue_cloudflare_live_authorization_receipt_v1.py --evidence <evidence.json> --custody-root <canonical-root> --output <receipt.json>
```

The issuer is provider-free and refuses to run if provider credential environment variables are already present.

## 8. Freshness/concurrency rule

The evidence assumes exclusive Workers AI usage on the target account between observation and completion of the governed packet. Any unrelated Workers AI consumption invalidates the quota evidence and therefore the receipt.

Crossing 00:00 UTC also invalidates the authorization context; capture fresh evidence and issue a new receipt.

## 9. Provider-free validation

Validated candidate head before ADR-021 documentation:

```text
0d61e7908b5e9511e851bcd2c8e1e02e2299a682
```

Dedicated run `33512426906`:

```text
authorization tests                          8 passed
Cloudflare v2 regressions                   32 passed
ADR-010/011 regressions                     29 passed
provider credentials present                 false
provider calls                               0
```

All 14 workflows on that candidate were successful, including production runtime, final handoff audit and provider-free final reproduction.

## 10. Current non-claims

ADR-021 does **not** prove any of the following:

- the private account is currently Workers Free;
- >=9000 neurons are currently available;
- a Cloudflare token/account ID exists or works;
- either model is live-accessible from the target account;
- model quality/reliability/latency;
- attempt 1 authorization;
- production provider selection.

## 11. Next admissible task

The next step is **fresh real evidence acquisition and actual receipt issuance**. This is the first point in this provider path that requires account-side/user action because the project intentionally does not have access to the private Cloudflare dashboard or secrets.

Required order:

```text
1 manual dashboard evidence
2 choose one canonical custody root
3 create sanitized evidence JSON + retain source artifact privately
4 issue short-lived receipt with zero provider secrets present
5 only then provision CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID
6 validate exact receipt/evidence/root/time
7 explicit execution decision
8 only then attempt 1
```

## 12. Other decision areas

```text
single-agent controller      STRONG QUALIFIED BASELINE
multi-agent comparison       QUEUED AFTER PROVIDER BASIS
runtime comparison           QUEUED
native tools vs MCP          EVIDENCE SUFFICIENT CURRENT SCOPE
RAG/vector/reranking         NO MATERIAL CURRENT GAP
persistent memory            NO MATERIAL CURRENT GAP
adaptive routing             NOT CURRENTLY MATERIAL
```

## 13. C4 parallel track — unchanged

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
gate     REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

Only exact-byte recovery is authorized. No reconstruction, rescoring, substitution, semantic evaluation, FRESH_BLIND or LEGACY_LOCKED_TEST.

## 14. Still forbidden

- provider inference before a valid real receipt and explicit execution decision;
- credential/account probes merely to prove availability;
- Paid Workers, AI Gateway prepaid/unified billing or paid spillover;
- modifying ADR-018/019/020/021 frozen behavior after real evidence begins;
- hidden retries/fallbacks/warm-ups/provider state;
- changing the preregistered scientific packet post hoc;
- weakening HarnessRunner/safety/evaluator-private boundaries;
- C4 reconstruction/rescoring;
- premature topology/runtime experiments;
- final architecture or production-readiness claims before evidence supports them.
