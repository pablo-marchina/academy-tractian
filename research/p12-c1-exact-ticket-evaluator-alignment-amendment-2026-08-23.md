# P12-C1 exact-ticket evaluator alignment amendment — 2026-08-23

## Status

`FROZEN_EVALUATOR_ONLY_ALIGNMENT_AMENDMENT_BEFORE_METRICS`

This amendment was frozen **after the 36 common parents and 72 C0/C1 outputs were successfully fixed, but before any aggregate candidate metric was produced or observed**. It does not authorize provider reruns, candidate regeneration, C2, semantic v4.2, FRESH_BLIND, or LEGACY_LOCKED_TEST candidate access.

## Why the frozen scorer stopped

The first evaluator-only scoring attempt failed closed during oracle alignment and wrote no result artifact. Historical E9 v4.1 aligns a private row by two simultaneous conditions: the row must contain the group asset identifier and it must match the selected public `ticket_id`. That was valid for the historical one-visible-ticket-per-group runner, but P12-C1 preregistered **all 12 exposed tickets**.

The full P12-C1 corpus contains a ticket with exactly one private oracle row whose ticket identity is unambiguous but which does not satisfy the historical adapter's redundant embedded-asset condition. Therefore the original P12-C1 wrapper cannot score the complete preregistered corpus even though the underlying v4.1 normalization and scoring semantics are valid.

## Frozen correction

Private oracle selection changes from:

`embedded group asset match AND exact public ticket_id match`

to:

`exact public ticket_id match, requiring exactly one row`.

The group/ticket relationship is still independently checked against the already-frozen public P12-C1 activation mapping before private oracle lookup. Zero or multiple exact ticket matches fail closed. There is no group-union fallback, fuzzy matching, semantic search, or candidate-output-dependent alignment.

Everything that determines the score remains unchanged:

- E9 v4.1 blob `b33afab0b3bfc9b81037a5391f49d286ef0d7c35`;
- E9 v4 parent blob `63145e6fe14d7dd9b90d5567ffca6aa54ced933f`;
- v4.1 METHOD+path normalization;
- `score_call`;
- metric definitions and deterministic thresholds;
- group→scenario→ticket→repetition aggregation;
- 20,000-resample group-cluster bootstrap, seed `20260822`;
- candidate outputs, parent pairing, provider/model configuration, and seeds.

## Structural qualification before rescoring

Evaluator-only structural validation against the frozen oracle established, without emitting expected-path content:

- activated public tickets: **12**;
- tickets with exactly one oracle row: **12/12**;
- zero/multiple exact-ticket matches: **0**;
- tickets with complete v4.1 expected-step normalization: **12/12**.

Private oracle SHA-256: `d6fb6186e4c035effe7dafa44758eaf40948ac334f0a91f8634a5731b7e0cb38`. The oracle remains evaluator-only and is not committed.

## Reproducible scorer derivation

Frozen base scorer SHA-256:

`4ffc93ff73acad5c96cc099205390f544b6e6cff712f44c8431db83306bc7a73`

Derived exact-ticket scorer SHA-256:

`e12d603edd14b00edd76b65fdbe54b0f0534b3478a9c94c192a82b67080fd233`

The transformation is deterministic and fail-closed:

`scripts/research/p12_c1_exact_ticket_alignment_patch.py`

The amended scorer is authorized for **one evaluator-only scoring pass over the already frozen output artifact** with SHA-256 `94d975b022bec04c89f343748b59da643d2690d7e73c4fe07df28716fb9c1590`.

## Interpretation constraint

This is an evaluator-plumbing correction for the preregistered full-ticket design, not a candidate intervention. Any resulting evidence remains `EXPOSED_POOL` evidence. Passing the deterministic gates can at most qualify the relevant candidate state; it cannot freeze the architecture or establish blind generalization or production readiness.
