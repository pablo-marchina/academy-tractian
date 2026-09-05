# Repository Cleanup Audit — 2026-09-05

## Purpose

This audit records the repository-wide reconciliation performed before the next development phase.

The governing invariant is:

> **Clean the active engineering surface without rewriting scientific history.**

Frozen results, exact-path/source-pinned evidence, accepted ADRs, consumed experiment records and historical workflow source are preserved. Branches and PRs are lifecycle/navigation surfaces; once their outcome is reconciled, deleting the branch ref does not authorize rewriting the underlying commit/PR/evidence history.

## Starting state

The repository audit began with:

- **129 branches** total (`main` + 128 non-main refs);
- multiple old squash/rebase branches whose commits appeared technically `ahead/diverged` even though their PR result was already incorporated into `main`;
- six open draft PR lines, including competing production/freeze branches and one scientifically blocked C4 branch;
- historical one-shot research workflows still able to trigger on ordinary product PRs;
- active canonical documentation mixed with names that had become hash-pinned historical evidence;
- no source family proven safe for cosmetic bulk deletion.

Because squash/rebase history creates ancestry false positives, branch reconciliation used the **PR outcome and surviving functionality** as the primary truth. Raw commit ancestry was used only for branches without a clear PR outcome.

## Pass 1 — canonical navigation and ownership

Merged through #192:

- replaced the root README with a concise canonical entrypoint;
- created `docs/CODEBASE-MAP.md`;
- created `tests/README.md` and `scripts/README.md`;
- updated `research/README.md`, `docs/README.md` and `.github/workflows/README.md` with lifecycle/ownership rules;
- expanded `.gitignore` for local/build/cache/report artifacts;
- rebaselined architecture, delivery plan, acceptance, runbook and TAPI coverage to the promoted PostgreSQL/distributed product and remote-production target;
- kept DuckDB as development/benchmark compatibility only, not production serving truth.

## Pass 2 — historical CI activation cleanup

A documentation-only PR revealed that old E-series, BIG-B, Cloudflare/D-series and provider experiment workflows were still subscribed to normal product pull requests.

The cleanup removed ordinary `pull_request` activation from historical/one-shot workflows while preserving:

- workflow source;
- prior Actions run provenance;
- manual `workflow_dispatch` where applicable;
- dedicated research-branch triggers where they already existed.

This changed **activation policy**, not historical experiment semantics.

## Pass 3 — frozen-document provenance repair

The first #192 head failed `clean-clone-full-product-reproduction` because the cleanup had treated `docs/CURRENT-PROJECT-STATUS.md` as mutable even though the 2026-09-04 final-freeze bundle hash-pins that exact path/blob.

The correction intentionally did **not** update the freeze hash to make CI pass.

Instead:

- restored `docs/CURRENT-PROJECT-STATUS.md` byte-for-byte to frozen git blob `36fc7db50457a787a9e026fc1518324f63a0d9cb`;
- retained the new mutable state as `docs/ACTIVE-PROJECT-STATUS.md`;
- kept `docs/RUBRIC-TO-EVIDENCE.md` frozen at git blob `2598f312106308484b35775f67cdb59b1fd7150f`;
- updated navigation so new state never needs to overwrite those historical paths.

The corrected #192 head passed the exact required CI and was squash-merged as:

`935357d2be714039bdadc81b05d40e4ef3676f7f`

## Pass 4 — branch and PR reconciliation

### Canonical merges

- **#192** `chore/repository-cleanup` — merged after exact-head required CI passed.
- **#194** `feat/remote-production-p0` — rebuilt from an 18-commit stacked branch into **one 12-file delta directly on cleaned `main`**, removing inherited stale docs/frozen-file drift. The normalized head passed all ten triggered workflows, including `production-runtime`, `clean-clone-full-product-reproduction` and `final-ci-required`, then squash-merged as:

`31b9de5f49ba2d784163a23a519ca762feff7a71`

The #194 merge adds only the fail-closed remote-production bootstrap: remote config validation, separate PostgreSQL migration, provider-closed server entrypoint, immutable container/build surface, production dependency lock, USD0 infrastructure eligibility evidence and focused regression tests. It does **not** select a provider or claim a deployed production environment.

### Explicitly superseded competing PRs

The following draft lines were closed **without merge** because merging them would restore obsolete or competing decisions:

- **#181** `feat/cloud-production-baseline` — 324-commit cloud baseline superseded by later PostgreSQL/distributed/runtime/rebaseline work and the narrower #194 bootstrap;
- **#190** `codex/final-canonical-docs-rehearsal` — obsolete freeze/documentation branch superseded by #192 and the corrected frozen-document lifecycle;
- **#191** `codex/live-demo-ready` — useful OIDC/JWKS/tenant/hosted ideas, but coupled to pre-rebaseline hosted/provider choices. The reusable requirements remain in the canonical production plan and must return through focused evidence-driven slices rather than by merging this branch wholesale.

### Scientific blocker archived without false completion

**#10** `eval/c4-required-reporting` was closed without merge because its own frozen contract forbids completion without the original evaluator-side artifact:

- SHA-256 `b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`;
- 177350 bytes;
- 144 rows / 36 parents × 4 arms.

Reconstruction, rescoring and substitution are forbidden. Closing the PR archives the blocked implementation; it does not convert the C4 gate to PASS. If the exact bytes are recovered later, the work must be reopened/rebased under the original frozen contract.

### Previously closed unmerged branches

The earlier unmerged diagnostic/rejected lines remain intentionally **not merged**:

- #150 `exp/p0-duckdb-concurrency-diagnostic`;
- #155 `feat/adaptive-soft-budget-experiment`;
- #171 `feat/restart-recovery-campaign`.

Their outcomes were superseded by later accepted work; branch deletion is cleanup, not retroactive promotion.

### Refs without a misleading PR signal

Three suspicious names were checked directly:

- `noop` — 0 commits ahead of `main`;
- `noop-audit-check` — 0 commits ahead of `main`;
- `tmp-do-not-use` — raw ancestry reported 17 commits ahead, but canonical semantic-review files already exist in `main` with identical git blobs (for example `frontend/src/components/SemanticReviewCollector.tsx`), confirming the apparent divergence is squash-history noise rather than unique surviving functionality.

## Physical branch cleanup

The exact 128 non-main branches observed at audit time are recorded in:

`docs/archive/legacy-branches-2026-09-05.txt`

`.github/workflows/repository-branch-hygiene.yml` performs the physical cleanup with two narrow rules:

1. on the merge that introduces the audited allowlist, delete **only exact branch names present in that file**;
2. prospectively, delete only same-repository head branches after GitHub reports their PR as actually merged.

Safety properties:

- no wildcard sweep of future development branches;
- `main` is rejected explicitly;
- a race between the initial sweep and merged-PR cleanup is handled by rechecking the remote ref;
- failure to remove an allowlisted branch leaves the maintenance workflow red rather than silently claiming success.

PR/commit/evidence history remains available after branch-ref deletion.

## Source reachability result

The noisy source families were audited before any package restructuring.

### `ACTIVE_CORE`

- `provider_clients.py` and the current runtime/API/PostgreSQL/action/observability/evaluation surfaces.

### `ACTIVE_SPECIALIZED`

- `provider_free_product.py` and provider-free acceptance helpers that exercise real runtime/controller/storage/SSE/evaluation behavior.

### `HISTORICAL_PINNED` / `RESEARCH_ONLY`

- Cloudflare/provider experiment modules tied to accepted ADRs and historical workflows;
- provider comparison/live-execution surfaces tied to earlier ADR/evidence chains.

No inspected source family passed the full `DEAD_SAFE_TO_REMOVE` predicate:

```text
not imported by promoted code/tests
AND not referenced by active workflows/scripts
AND not referenced by ADR/current docs
AND not exact-path/blob pinned by frozen evidence
AND not required for reproduction/handoff
```

Therefore **no cosmetic `src/` package move or historical-source bulk deletion was performed**. That restraint is part of the cleanup result, not unfinished guesswork.

## Current repository state after reconciliation

Canonical product `main` now contains:

- the cleaned documentation/navigation/governance surface from #192;
- the promoted PostgreSQL/distributed runtime already accepted before this audit;
- the fail-closed remote USD0 production bootstrap from #194;
- current product CI separated from historical one-shot research execution;
- explicit lifecycle protection for frozen status/rubric evidence;
- automated branch hygiene for merged work.

There are no remaining open PRs at the point the branch-hygiene cleanup is prepared.

## Claims that remain deliberately false/not proved

This cleanup does **not** prove or claim:

- a remotely deployed production URL;
- a selected production model/provider;
- standards-based OIDC/SSO in `main`;
- production HA/SLO/RTO/RPO;
- completed human semantic calibration;
- completed MANUAL vs ASSISTED operational-value evidence;
- branch protection enforcement;
- exactly-once external side effects;
- promotion of LangGraph, multi-agent, RAG, memory or MCP.

Those remain development/evidence tasks after the repository baseline is clean.

## Exit criterion

The repository is considered reconciled for the next development phase when:

- #192 and #194 are in `main` with exact-head CI green;
- competing/blocked PRs are explicitly closed rather than implicitly abandoned;
- the audited legacy branch sweep completes;
- normal product PRs do not execute historical one-shot research campaigns;
- frozen evidence remains byte/path-correct;
- no source file is removed without reachability/provenance proof;
- future merged PR heads are automatically cleaned.
