# Operational-value analysis decision — 2026-09-03

## Decision

Promote a trusted, offline analysis path for the blinded DEV operational-value pilot. The analysis is allowed to produce a **time signal only** after the collection packet is closed and the analysis protocol is frozen. It must not produce a business-value claim by itself.

## Current evidence state

The collection backend, participant flow, persistent timing custody, snapshot contract, paired analysis and CI gates are implemented. **No real human measurements have been collected in this repository and no engineer-time-saved claim is supported yet.** Test measurements are synthetic fixtures only.

## Freeze boundary

The trusted analysis path is intentionally not exposed through the participant FastAPI surface.

Before analysis:

1. Freeze an `operational-value-analysis-protocol-v1` document with `status=FROZEN`.
2. The protocol fixes the minimum complete-pair requirement, confidence level, paired-bootstrap iteration count and bootstrap seed before outcomes are inspected.
3. Close the packet through the trusted Postgres analysis store or `scripts/operational_value_analyze.py --close`.
4. Closing refuses any `ACTIVE` assignment and is irreversible through the analysis API.
5. Build a hash-bound snapshot from the complete registered task inventory plus persisted valid measurements and invalid-trial counts.

The current policy is deliberately conservative: **every registered MANUAL/ASSISTED pair must be complete** for the result to become analysis-ready. Missing or invalid arms are not imputed. A different missingness policy would require a separately frozen protocol change before inspecting outcomes.

## Measurement design

The promoted pilot uses the previously frozen `INDEPENDENT_MATCHED` design:

- each source case has one MANUAL task and one ASSISTED task;
- the same human operator may not supply both arms of a pair;
- invalid, interrupted, withdrawn and technical-failure trials are counted but never assigned fabricated elapsed time;
- the browser never owns authoritative elapsed time;
- persisted server-side monotonic time is the only human-effort duration used by analysis.

`LOCKED_TEST` remains outside this pilot and must not be used to tune sample size, thresholds, prompts, architecture, stopping policy or evaluator behavior.

## Estimands

For each complete pair:

`delta_seconds = manual_seconds - assisted_seconds`

The analysis reports:

- mean MANUAL human time;
- mean ASSISTED human time;
- mean and median paired time delta;
- `Engineer Minutes Saved per Ticket = mean(delta_seconds) / 60`;
- observed total engineer minutes saved across complete pairs;
- relative time reduction against mean MANUAL time;
- MANUAL and ASSISTED tickets per engineer hour;
- a paired non-parametric bootstrap confidence interval for the mean time delta.

Negative deltas are preserved. There is no zero-flooring and no imputation.

## Statistical rule

The paired bootstrap resamples complete pair deltas with replacement using the frozen deterministic seed. The percentile interval uses the frozen confidence level and iteration count.

The status is:

- `NOT_READY` if collection is open, an assignment is active, fewer than the frozen minimum complete pairs exist, any registered pair is incomplete, or no valid interval can be computed;
- `POSITIVE_TIME_SIGNAL` only if the entire confidence interval is above zero;
- `NEGATIVE_TIME_SIGNAL` only if the entire confidence interval is below zero;
- `INCONCLUSIVE_TIME_SIGNAL` otherwise.

The implementation does not choose a post-hoc minimum sample size, confidence level or stopping threshold. Synthetic tests use concrete values only to verify behavior.

## Business-claim gate

A positive time signal is **not** sufficient evidence that the agent saves useful engineer time. `business_claim_ready` is therefore hard-coded to `false`, and `requires_operational_quality_gate` remains `true`.

A later evidence-join slice must combine the frozen human-effort result with separately calibrated operational-quality evidence, including at minimum operational-conclusion correctness and useful-resolution correctness. Only that joined gate may support a business-value claim.

## Privacy and output boundary

The trusted Postgres snapshot may contain private evaluator material needed for pairing, including task IDs, pair IDs and hashed operator references. Those fields stay inside the trusted analysis boundary.

`scripts/operational_value_analyze.py` reads database credentials only from `ACADEMY_POSTGRES_INTERNAL_DSN` and `ACADEMY_POSTGRES_SCOPED_DSN`. Its persisted output excludes participant-level paired timing rows, task IDs, pair IDs, operator references, conclusion summaries and raw provider material. The exported evidence hash still binds the internal analysis result so the trusted host can reproduce it from the frozen database snapshot and protocol.

## Promotion criteria for this slice

This implementation can merge when:

- pure analysis contract tests pass;
- real Postgres freeze/snapshot integration tests pass;
- the trusted CLI compiles in CI;
- packet close refuses active trials;
- snapshot hashes are deterministic and tamper-evident;
- same-operator crossover fails closed;
- incomplete collections remain `NOT_READY`;
- no participant-facing API exposes the trusted analysis path;
- documentation explicitly states that there are no real human measurements or business claim yet.
