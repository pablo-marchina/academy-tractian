# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-09-01 — ADR-021 live authorization protocol frozen; real account evidence pending  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Frozen preregistration:** ADR-018  
**Frozen client:** ADR-019  
**Frozen executor/custody:** ADR-020  
**Frozen authorization protocol:** ADR-021

This file is the short-horizon plan. It does not itself authorize provider inference or attempt 1.

## 1. Completed

```text
historical evidence audit                         DONE
current provider factual refresh                  DONE
four factual provider gates                       DONE
minimum Cloudflare comparison preregistration     FROZEN / ADR-018
provider-free Cloudflare client                   FROZEN / ADR-019
ADR-010/011 reuse audit                           DONE
Cloudflare executor/custody v2 provider-free      FROZEN / ADR-020
live authorization protocol provider-free         FROZEN / ADR-021

provider inference                                0
credential/account probes                         0
live network validation                           0
comparison attempts consumed                      0 / 32
real account evidence                             NONE
real authorization receipt                        NONE
attempt 1                                         NOT AUTHORIZED
```

## 2. NOW — acquire fresh real Cloudflare evidence

This is the first provider-path task requiring user/account-side access.

Before any credentials are provisioned, obtain a **manual Cloudflare Workers AI dashboard observation** proving the current state.

Required evidence:

```text
Workers plan                         Workers Free
Workers Paid enabled                 false
neurons used today                   explicit value
free neurons remaining               explicit value >=9000
used + remaining                     exactly 10000 within tolerance
UTC day                              current
observation age                      <=600 seconds when receipt is issued
comparison attempts already used     0
AI Gateway route                     false
prepaid/unified billing route        false
cf-aig-gateway-id                    absent
exclusive Workers AI usage window    attested
```

Do not use an inference call or credential/account API probe to obtain this evidence.

The source screenshot/export must be retained privately/outside the repo. The sanitized evidence JSON records only its SHA-256, not the screenshot, account ID or secret.

## 3. Select one canonical custody root

Before issuing the receipt, choose exactly one durable local custody root.

ADR-021 stores only:

```text
SHA-256(canonical resolved custody-root path)
```

The raw path is not persisted in the receipt.

Changing roots after receipt issuance invalidates authorization.

## 4. Create the sanitized evidence JSON

Use the frozen schema `cloudflare-live-authorization-evidence-v1`.

Required structure includes:

- observation timestamp in UTC;
- current UTC day;
- used/remaining neurons;
- Workers Free / no Paid;
- direct route / no Gateway or prepaid billing;
- zero comparison attempts consumed;
- exclusive usage-window attestation;
- zero inference/probe flags;
- source artifact SHA-256;
- no account identifier or secret.

The evidence must remain fresh; do not prepare it hours in advance.

## 5. Issue the receipt provider-free

With **no provider credential variables present**, run:

```text
python scripts/research/issue_cloudflare_live_authorization_receipt_v1.py --evidence <evidence.json> --custody-root <canonical-root> --output <receipt.json>
```

The receipt:

- lasts <=300 seconds;
- never outlives the 600-second evidence window;
- is bound to the evidence SHA;
- is bound to the custody-root SHA;
- is bound to ADR-018/019/020 and the exact plan/models/route;
- becomes invalid across UTC-day reset;
- contains no token/account ID/raw path.

If it expires, do not reuse it. Capture fresh evidence and issue another receipt.

## 6. Only after receipt — provision secrets

Then provide, securely at runtime:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

Token policy:

```text
permission       Account > Workers AI > Read
resource scope   exact target account only
AI Gateway perms not required / should not be granted
Global API Key   forbidden
```

Do not commit, log or serialize these values.

## 7. Final pre-attempt validation

Immediately before attempt 1, verify:

```text
receipt unexpired                          YES
evidence still <=600 seconds old           YES
same UTC day                               YES
custody-root SHA exact                     YES
evidence SHA exact                         YES
ADR-018/019/020 pins exact                 YES
plan SHA exact                             YES
model IDs exact                            YES
direct route exact                         YES
exclusive account usage window intact      YES
comparison attempts consumed               0
```

If unrelated Workers AI usage happened after evidence capture, invalidate the receipt and start again with fresh evidence.

## 8. THEN — explicit live execution decision

Only after all gates above are true may a separate execution action authorize:

```text
fixture_result = false
attempt 1 = admissible
```

The live path remains:

```text
GovernedCloudflareLiveTaskV2.prepare(...).execute_all()
```

ADR-020 then owns write-ahead `CLAIMED`, exact 32-entry ledger, uncertain/no-replay and resource stop guards.

## 9. Live packet if authorized

The scientific packet remains exactly:

```text
@cf/zai-org/glm-4.7-flash
VS
@cf/nvidia/nemotron-3-120b-a12b

8 public probes × 2 repeats × 2 candidates
max 32 attempts
```

No candidate, threshold, metric, prompt population or budget may change after results begin.

Valid terminal outcomes:

```text
cloudflare_glm_4_7_flash_workers_free
cloudflare_nemotron_3_120b_a12b_workers_free
NO_SELECTION
```

## 10. Parallel C4 track

Exact artifact still required:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 parents × 4 arms
```

Only exact-byte recovery is authorized.

## 11. Later queue

```text
AFTER PROVIDER RESULT  assess single-agent vs multi-agent only if still material
AFTER TOPOLOGY         runtime/orchestration comparison only if evidence gap remains
FINAL                  integrate best-supported configuration + full regression + architecture freeze
```

RAG, persistent memory and richer UI remain out of experiment scope unless a measured material gap appears.

## 12. Still forbidden

- issuing a real receipt from stale/synthetic/fabricated account evidence;
- provisioning secrets before receipt issuance;
- credential/account probing merely to prove account state;
- any inference before receipt + explicit execution authorization;
- Workers Paid, AI Gateway prepaid/unified billing or paid spillover;
- concurrent unrelated Workers AI use during the evidence/receipt/execution window;
- changing ADR-018 packet after execution begins;
- automatic retry/fallback/warm-up/resume;
- replaying claimed/uncertain attempts;
- C4 reconstruction or rescoring;
- premature final provider/architecture claims.
