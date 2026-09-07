# Academy × TRACTIAN — Release 0 Acceptance

**Original acceptance status:** PASS / PROMOTED  
**Original accepted backend/runtime SHA:** `082d6f115c070fdc898df749b4b3018efd9ceeab`  
**Original workflow:** `hosted-production-release0-agent`  
**Original run:** `34069562818`  
**Current hardened backend/runtime:** `08866da60245f58f217981b7ae668b10be45cc67` (V13)  
**Current backend deployment:** `062c3cc4-4ac9-48ac-be06-2b4c490cea2a` — SUCCESS

This document preserves the original Release 0 acceptance evidence **and** explains the later prospective hardening. The original acceptance SHA/run are historical facts and are not rewritten to make later fixes look as if they existed in the first campaign.

## 1. Original acceptance ledger — immutable scope

| Gate | Original observed state |
|---|---|
| remote HTTPS frontend/API | **PASS** |
| Neon durable PostgreSQL | **PASS** |
| immutable backend release identity | **PASS — exact SHA** |
| managed browser auth | **PASS** |
| two-user/tenant negatives | **PASS — zero release-campaign disclosure** |
| real hosted provider | **PASS — provisional Cloudflare** |
| real typed TRACTIAN read | **PASS — remote 2xx observed** |
| provider → agent → TRACTIAN → evidence → terminal → evaluator | **PASS** |
| safe terminal behavior | **PASS** |
| evidence / lineage / persistence | **PASS** |
| authenticated REST/SSE | **PASS** |
| 18-operation capability contract | **PASS — 13 reads + 5 proposal-only actions** |
| external consequential action execution | **DISABLED / 0 calls** |
| USD0 / no paid spillover | **PASS Release 0 policy** |
| local/mock production dependency | **ZERO** |
| external two-user smoke | **PASS** |

## 2. Original proven hosted path

```text
real browser auth
→ server-owned tenant context
→ live Cloudflare model call
→ canonical typed TRACTIAN read
→ remote evidence
→ terminal mode
→ persisted output
→ deterministic post-runtime evaluation
→ safe lineage
→ Neon PostgreSQL
→ public authenticated REST/SSE
```

## 3. Why the current backend SHA is different

Real user-driven prompt testing after the original acceptance intentionally looked for semantic/trajectory failures. That produced a sequence of prospective fixes (#197, #198, #199, #200, #201, #207, #208, #210) and the current V13 backend.

The current runtime adds:

- stronger authorized asset/company discovery;
- nested structured resource-ID recovery;
- redundant metadata-loop suppression;
- mandatory condition evidence for relevant diagnostics;
- explicit `response_mode` semantics;
- managed-session read-burst resilience with correct 401/503 states;
- human asset-label grounding/comparison rules;
- data-quality evidence requirements;
- initial identity grounding before explicit-asset terminal;
- suppression of completed single-asset data-quality repetition.

See [`progress/2026-09-07-release0-live-hardening-v13.md`](progress/2026-09-07-release0-live-hardening-v13.md).

## 4. Current V13 live evidence — additive, not historical rewrite

### Data-quality trust

`run_21813cb7b4ad9adbdc5e`

`get_current_user → list_assets_by_company → get_data_quality → get_rms → point-specific get_rms → FINAL complete`

5 tools, 0 errors, 0 policy blocks; `get_data_quality` executed once.

### Missing comparison resource

`run_547b2a62d84ef56a3d3d`

`get_current_user → list_assets_by_company → FINAL unavailable`

R420 was absent from the authorized fleet; no internal-ID request, invented asset or cross-tenant scope expansion occurred. This validates fail-closed missing-resource behavior, not bilateral comparison quality.

### Probabilistic causal answer

`run_97b91f6e0feb91184283`

`get_current_user → list_assets_by_company → spectrum → point-specific spectrum drill-down → FINAL partial`

5 tools, 0 errors, 0 policy blocks. `partial` correctly communicates that the probable bearing mechanism remains causal inference rather than fully proven root cause.

All persisted blocking structural checks for these three runs passed.

## 5. Current response-mode contract

`response_mode` is customer-visible epistemic status:

- `complete` — material request fully supported;
- `partial` — useful supported answer with material uncertainty/incompleteness;
- `inconclusive` — no reliable directional core answer after evidence inspection;
- `conflict` — material contradiction;
- `unavailable` — required authorized evidence unavailable.

It is separate from the controller terminal decision and has no authorization power.

## 6. Current security boundary

Release 0 still does not authorize:

- browser-owned tenant/privilege authority;
- hidden model/route/paid fallback;
- raw provider/TRACTIAN/database/session secret projection;
- local/mock serving;
- hidden chain-of-thought exposure;
- consequential external action execution.

Managed-session resilience was hardened without stale auth: GET/HEAD may reuse a server-validated context for ≤2 seconds, while non-read operations always validate fresh and expired cache state is never served on error.

## 7. Current UX

The original minimum gate predates later UX work. The **current hosted frontend** is `1bc124a8d4dbd029178ff8129b25452129445de7` and uses task-driven Home / Analyses / Technical navigation with contextual result/evidence detail.

That UX evolution does not alter the original backend acceptance SHA.

## 8. Non-claims

Neither the original acceptance nor the V13 hardening proves final provider superiority, exhaustive semantic accuracy, complete live coverage of every read operation, full SECURITY-V1, final capacity/SLO/HA/RTO/RPO, consequential action readiness, human-calibrated semantic judge readiness, operational time savings or adaptive-policy superiority.