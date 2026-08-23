# P12-C2 live cycle closure — 2026-08-23

## Status

`CONSUMED_OPERATIONAL_FAILURE`

The single authorized live P12-C2 `EXPOSED_POOL` cycle was executed in workflow run `32663659575`. The provider/model cycle was consumed and may not be rerun.

## What completed

- live preflight: PASS;
- exact P12-C2 activation and protocol guards: PASS;
- exact runner and scorer pins: PASS;
- agent-visible corpus isolation: PASS;
- candidate private-oracle access: 0;
- FRESH_BLIND access: 0;
- LEGACY_LOCKED_TEST access: 0;
- arm-specific provider calls: 0;
- common-parent generations attempted: 36;
- common-parent generations completed: 31.

## Operational failure

Five of the 36 common-parent generations failed under the provider failure family `rate_limit_long_window` after the frozen retry policy had been exercised. The generation summary reported:

```text
expected common parents      36
attempted common parents     36
successful common parents    31
failed common parents         5
internal retries             10
failure family               rate_limit_long_window
provider cycle consumed      yes
rerun allowed                no
```

This is an external-provider operational failure, not an arm-quality or hard-safety result.

## Freeze and scoring consequence

The preregistered measurement required all 36 common parents to exist before deriving and freezing all 144 paired factorial outputs (`A00/A10/A01/A11`). Because only 31 parents completed:

- the 36-parent/144-output freeze gate was not satisfied;
- immutable live freeze geometry validation was skipped;
- the private-scoring intermediate was not uploaded;
- the private deterministic scorer was not executed;
- the private oracle was not loaded;
- factorial contrasts were not computed;
- the 20,000-resample group bootstrap was not computed;
- LOGO was not computed.

The private-scoring handoff job was correctly skipped rather than scoring an incomplete packet.

## Scientific interpretation

No P12-C2 arm-level scientific conclusion exists from this run. In particular, this run does **not** establish that A00, A10, A01, or A11 passes or fails the deterministic gates, and it does not support selecting a `QUALIFIED` or `PREFERRED` arm.

The completed 31 parents must not be silently treated as a smaller confirmatory sample because the preregistration fixed three repetitions per visible ticket and the scorer/aggregation contract requires the complete frozen packet. Treating the incomplete set as the planned factorial result would change the estimand and missingness handling after outcomes were exposed.

## Governance decision

```text
P12-C2 live cycle                  CONSUMED
P12-C2 operational result         FAILURE: provider long-window rate limit
complete common parents           31 / 36
complete fixed factorial outputs  NOT PRODUCED
private deterministic scoring     NOT RUN
factorial analysis                NOT RUN
bootstrap                         NOT RUN
LOGO                              NOT RUN
qualified arms                    NONE ESTABLISHED
preferred arm                     NONE
same-cycle rerun                  FORBIDDEN
semantic v4.2                     NOT AUTHORIZED
FRESH_BLIND                       NOT AUTHORIZED
LEGACY_LOCKED_TEST                NOT AUTHORIZED
architecture freeze               NOT AUTHORIZED
production-readiness claim        NOT AUTHORIZED
```

If more `EXPOSED_POOL` evidence is desired, the next valid path is a **new preregistered experiment/generation** with provider-capacity controls chosen before any new outcomes. It must not be represented as a rerun or continuation of this consumed P12-C2 cycle.

## Evidence

- workflow run: `32663659575`;
- preflight job: `97253541865` — success;
- generate/freeze job: `97253566866` — failure;
- private-scoring handoff job: `97256434951` — skipped;
- sanitized generation artifact: `p12-c2-generation-summary`, artifact `9499705496`;
- artifact digest: `sha256:da4a3f05a388e7306091d47960e4c2238d488d7cac98f8c1403aa175cca934cb`;
- machine-readable closure: `research/results/p12-c2-live-cycle-closure-2026-08-23.json`.
