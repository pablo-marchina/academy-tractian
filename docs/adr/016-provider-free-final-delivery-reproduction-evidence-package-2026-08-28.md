# ADR-016 — Provider-free final-delivery reproduction and evidence package

**Date:** 2026-08-28  
**Status:** FROZEN FOR PROVIDER-FREE FINAL-DELIVERY REPRODUCTION SCOPE  
**Tracks:** #57 / PR #58  
**Supersedes:** nothing

## Decision

Freeze a clean-checkout, provider-free final-delivery reproduction package that proves the already accepted production/runtime safety evidence can be reproduced together and traced to one machine-readable evidence index without widening authorization.

This ADR does not freeze the global production architecture and does not claim production readiness. It freezes only the provider-free reproduction/evidence package defined prospectively in issue #57.

## Preregistered integrated demo

Issue #57 fixed the exact five-scenario order before the final result was interpreted:

1. `DEMO-01` — canonical `get_asset` read/investigate followed by `ORIENT`;
2. `DEMO-02` — `ASK_CLARIFICATION / MISSING_CONTEXT`;
3. `DEMO-03` — `ABSTAIN / NO_SAFE_PATH`;
4. `DEMO-04` — `ESCALATE_HUMAN / HUMAN_REVIEW_REQUIRED`;
5. `DEMO-05` — controlled supplied/test `reprocess_analysis`, deterministic local `202 {"accepted": true}`, exactly one local transport and one fresh durable claim, followed by `ACT_REPROCESS`.

The exact campaign version is `provider-free-final-delivery-reproduction-v1`.

The campaign uses the accepted runtime/controller/evaluator and controlled-action boundaries. It does not create another execution path.

## Exact integrated result

The clean-checkout validator reproduced:

```text
DELIVERY_REPRODUCTION_VALIDATION      PASS
report SHA-256                        43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445
integrated demo scenarios             5 / 5
exact traces evaluated                5 / 5
contract expectations                 5 / 5
provider calls                        0
credential/account probes             0
real customer mutations               0
semantic/private/blind access         0
automatic retries                     0
replays                               0
```

The exact scenario identities are:

| Scenario | Spec SHA-256 | Result SHA-256 | Trace SHA-256 | Behavioral trace SHA-256 |
|---|---|---|---|---|
| `DEMO-01` | `a730392bef5c6ab9063015100a2afc10742cae4e92268d3394424d34723638a4` | `55a81f09d52fcb91caf22dcd452ac23dee143f405e4e3b90b1971d040b592cff` | `b715b29790af3f7cd92bf839beec6d08e2b77e3e79e8101db81c419d454e7143` | `0fc767340450e6c7be388ba15b48616e39a25a566162a33eb30d54e8b18f7d99` |
| `DEMO-02` | `926d91a234d5d8a331b17218fa15e57f1f61f453b9edbd0bf08638cf5c309944` | `a30033aed27b89a52602a0c794c15134ceec39c6a7935b39709698943e4854eb` | `0c593d21777ed3ac62f31042caa1c1f75e6c20f62269d58a824c174e5f500dad` | `b3cde3c561bc43df97bae3ecca7a7050294375a872fd288d89eb01506641b95c` |
| `DEMO-03` | `8bbd629de8da5de3fe5db994b56dc36732336f61cf34ea343f26bb4e578b7e10` | `2e4dc13ef6edbae797299974e3031d893f11bd0fa4ddd7451a8a06525c6609cb` | `5d57ef1e7da115cddd34bcab98c3294b10c2c56f28d6ab6c56cd7a58e0123e11` | `f4cb91487ff5ec88ad9398cfae9c25b4e43a48467bb1f264a39dca44d6058869` |
| `DEMO-04` | `f74dbc1466659ef432d9e4718da50ee81c31d93bcd866ccf8cb4a6a1c642c809` | `1d72f3f40bf78bc63232c0dcc45496bd4ea5977cbdc6368565f654d313f37720` | `363fe4ccef4d402a27b5a22c90f8da00605de8de8c5b8c455a9296feea67db84` | `a224f926f3ba823b80e919c7fabc97cfbed2351f5dbfd11c38973db03c851378` |
| `DEMO-05` | `16217eb15bda21c8c6e956b89d9d9740c260af7c90dfc57385630a96e8f9049e` | `80f11833ecfb1b425ea66f65d1fd709475ff856a240e747c37607fec74ce65ca` | `71e4d37da6f88033e4bd5ec25c5ac15e6d7c52eef4532eb3ba60aa5cd227f04d` | `e8cc10fb55062f7a06eeccf51dc7be1fab243ee8796e56c63dd4be78e6e26565` |

The immutable compact result manifest is:

`research/results/provider-free-final-delivery-demo-result-2026-08-28.json`.

## Clean-checkout reproduction contract

The dedicated workflow executes the preregistered order:

1. install the production package and `research/e2` editable dependencies;
2. run the complete production test suite;
3. regress the accepted ADR-004 controller boundary;
4. reproduce frozen EV-007;
5. reproduce frozen EV-008;
6. reproduce frozen EV-011;
7. validate the final-delivery demo, its static manifest and the evidence index.

No live provider credential is required or consumed by this workflow.

At validated pre-freeze head `9ac8296726f356d146cd3a0c549074a29548cfcb`:

- `final-delivery-provider-free-reproduction #7` / run `33158593240` — PASS;
- production suite inside the clean-checkout workflow — `232 passed`;
- ADR-004 controller regression — `12 passed`;
- EV-007 — PASS with frozen report SHA unchanged;
- EV-008 — PASS with frozen report SHA unchanged;
- EV-011 — PASS with frozen report SHA unchanged;
- integrated demo — PASS with report SHA `43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445`;
- all 12 workflows triggered for the head — success.

## Evidence index

The machine-readable index is:

`research/results/final-delivery-evidence-index-2026-08-28.json`.

The validated index contains:

```text
entries                              31
repository-resident entries          30
exact Git blobs resolved             30 / 30
external blocker entries              1
index violations                      0
```

It covers the preregistered minimum evidence set:

- ADR-004 through ADR-015;
- EV-007 freeze, result and validator;
- EV-008 freeze, result and validator;
- EV-011 freeze, result and validator;
- provider-comparison plan identity;
- exact C4 external blocker identity;
- final-delivery workflow and validator;
- campaign-level demo identity plus DEMO-01 through DEMO-05 result identities.

Each repository-resident entry is checked against the exact Git blob at its canonical path. Canonical report/result SHA-256 values are also checked against the content of the corresponding result/freeze manifests instead of trusting the index declaration alone.

The index intentionally does not index itself, avoiding a circular Git-blob dependency.

## Preserved falsifications

Two failures were preserved rather than hidden or reclassified.

### Falsification 1 — inferred ADR filenames

The initial evidence tests assumed ADR filenames from their titles. The integrated five-scenario demo passed, but eight evidence-index tests failed before the index could be considered valid.

The correction replaced inferred paths with the repository's actual canonical ADR paths. Scenario geometry, result hashes, runtime behavior and acceptance criteria were unchanged.

### Falsification 2 — historical freeze representation mismatch

After static-index validation was enabled, dedicated clean-checkout run `33158501340` failed with `1 failed, 231 passed` because the checker assumed all EV freezes represented result identity with `result.path`.

That assumption was false:

- EV-007 carries `result.path` directly;
- EV-008 and EV-011 carry the canonical report SHA under `result` and the result file/path/blob identity under `direct_blobs`.

The checker was corrected to validate the representation each immutable historical freeze actually uses. Historical freeze files and their scientific/production results were not modified.

The corrected head produced 30/30 repository-resident blob resolutions and zero index violations.

## Frozen upstream identities

This package preserves, without reinterpretation:

```text
EV-007 report SHA-256
7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9

EV-008 report SHA-256
1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8

EV-011 report SHA-256
cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e

provider-comparison plan SHA-256
69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f

missing C4 artifact SHA-256
b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
```

`COMM-07` remains evaluator-invalid by design in frozen EV-011. This package does not turn safe communication around an uncertain action into a valid completed action.

## Explicit boundaries

ADR-016 does not authorize or imply:

- any of the 32 bounded ADR-009 live provider calls;
- credential or account probing;
- provider/model selection;
- provider-side conversation state;
- real customer mutation;
- default `ProductionRuntime` action enablement;
- reconstruction, rescoring or substitution of the missing C4 artifact;
- semantic/private/blind evaluation;
- `FRESH_BLIND` or `LEGACY_LOCKED_TEST` access;
- scientific-gate advancement;
- a global architecture freeze;
- a production-readiness claim.

The provider comparison remains `UNEXECUTED_GATED` at 0/32 calls. C4 remains `EXTERNALLY_BLOCKED` on the exact 177350-byte / 144-row artifact.

## Interpretation

ADR-016 establishes a reproducible, auditable provider-free delivery baseline: a clean checkout can reproduce the accepted deterministic runtime/evaluator campaigns and the five-scenario integrated demo, while the evidence index distinguishes reproducible evidence from immutable historical evidence, external blockers and unexecuted gated work.

This is delivery evidence, not evidence that unavailable external prerequisites were completed.

## Change rule

Any change to the five-scenario population/order, frozen result identities, evidence-status semantics, canonical provider/C4 boundaries, clean-checkout command sequence, or evidence-resolution rules after this freeze requires a prospective amendment/new evidence identity. Historical ADR-016 evidence remains immutable.