# P12-C3 capacity-controlled activation / eligibility — PASS

Date: 2026-08-23  
Experiment: `P12-C3_EXPOSED_POOL_CAPACITY_CONTROLLED_FACTORIAL`

## Decision

The child activation gate is **`ACTIVATION_ELIGIBILITY_PASS`**. Exactly one P12-C3 live capacity-controlled EXPOSED_POOL experiment is authorized. This is authorization to execute the frozen collection protocol; it is not evidence that A00/A10/A01/A11 are qualified, preferred, final, or production-ready.

## Provider-free qualification

Pre-promotion workflow run `32666884507`, job `97261551174`, completed successfully with **79/79 checks PASS**. Artifact `9500275650`, digest `sha256:7512f800ab21d98c300fcfe4a40aa801981e1744dc4070d2d7d118a717ad170a`.

Post-promotion workflow run `32666992054`, job `97261833385`, also completed successfully and verified the final manifest with `execution_authorized=true`. Artifact `9500292605`, digest `sha256:f3ff884571a59bfb0c54a4c25daefc11b183db0da8c4ce28be8c351a9ff2d224`.

No provider/model call, private-oracle access, FRESH_BLIND access, or LEGACY_LOCKED_TEST access occurred during activation.

## Frozen scientific definition

Candidate definitions are unchanged from P12-C2:

```text
A00 = E0 + S0
A10 = E1 + S0
A01 = E0 + S1
A11 = E1 + S1
```

The parent configuration remains SHA-256 `9033a78a5bab46e4c48ebfc0ec70b6476570519fa62f0526625916d0cd3d3b89`. The deterministic factorial scorer remains SHA-256 `f3500751448c3b52bf361f4d565ba940c8e9e62e8ab197bb1206fdb7d89a7d22`.

## Frozen capacity mechanics

The activation froze and tested:

- 6 batches × 6 parents = 36 unique ticket-seed cells;
- seeds `2026082307`, `2026082308`, `2026082309`;
- strict batch order;
- minimum 30-second inter-request delay;
- Groq `retry-after`, `x-ratelimit-reset-requests`, `x-ratelimit-reset-tokens`, `x-ratelimit-remaining-requests`, and `x-ratelimit-remaining-tokens` handling;
- later reset wins when reset signals disagree, plus a 30-second safety margin;
- no reset metadata => abort batch rather than guessing a short retry;
- maximum 3 pre-output transport/rate-limit attempts per cell;
- any returned model output consumes that cell;
- accepted parent checkpoint is immutable;
- completed parent regeneration is forbidden;
- resume may execute only pending predeclared cells;
- public checkpoint record exposes only operational counts/reset metadata/checkpoint hash, never raw parents;
- collection horizon is exactly 72 hours from the first live provider call;
- no private scoring between batches;
- no partial/complete-case factorial analysis.

## Completeness gate before scoring

Private deterministic scoring is still blocked until all of the following are true:

```text
36 / 36 new common parents complete
144 / 144 A00/A10/A01/A11 outputs fixed
same parent shared by all four arms in every cell
candidate private-oracle accesses = 0
FRESH_BLIND accesses = 0
LEGACY_LOCKED_TEST accesses = 0
arm-specific provider calls = 0
```

If the 36-parent gate is not completed within the frozen 72-hour horizon, P12-C3 must close as an operational failure without deterministic arm scoring.

## Still not authorized

- semantic v4.2;
- FRESH_BLIND;
- LEGACY_LOCKED_TEST;
- architecture freeze;
- production-readiness claim.

## Next step

Freeze the P12-C3 live execution manifest and the checkpointed six-batch workflow **before the first P12-C3 provider call**. No live provider call was made by this activation gate.
