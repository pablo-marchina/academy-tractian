# GitHub Actions — Workflow Lifecycle

This directory contains current product CI, intentional exact-SHA promotion gates, specialized hosted verification, provider experiments and historical research workflows. **Workflow presence is not execution authorization, and workflow success is not automatically a production claim.**

Current state: [`../../docs/ACTIVE-PROJECT-STATUS.md`](../../docs/ACTIVE-PROJECT-STATUS.md).  
Latest material episode: [`../../docs/progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`](../../docs/progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md).

## 1. Required product regression

Stable branch-protection target:

- `final-ci-required.yml` → `required-gate`

Use the stable aggregate status rather than making path-filtered/provider-live/research workflows individually required.

Required CI proves deterministic product/reproduction contracts for its exact SHA. It does **not** prove:

- OpenRouter availability or hosted functional success;
- all 13 TRACTIAN reads;
- governed action upstream transport availability;
- final action SECURITY-V1;
- production capacity/SLO/restore;
- semantic human correctness.

Latest GitHub metadata still reports `main.protected=false`; the required gate is ready for branch protection but enforcement is not active.

## 2. Production promotion

Production backend currently serves `5611687556b3d50c31f20fa85ede794f2500f05c` from `release/production-final`. Source/PR CI and Railway deployment/acceptance are separate:

```text
source tests
→ required CI
→ exact candidate identity
→ exact Railway deploy
→ /health + release identity
→ hosted managed-auth functional/security campaign
→ acceptance decision
```

A generic redeploy or a source merge must not be used as evidence that the latest commit is running.

Historical Release 0 workflows/runs remain historical; do not rewrite them to imply they tested current V14/governed-action production.

## 3. Current OpenRouter V14 / functional-closure workflows

Draft PR #222 adds/uses workflow surfaces including:

- `functional-provider-secret-presence.yml` — verifies required provider-secret configuration presence without exposing secret material;
- `hosted-provider-model-discovery-v1.yml` — controlled hosted free/provider model discovery;
- `provider-tournament-cross-provider-v1-live.yml` — prospective cross-provider live comparison;
- `provider-tournament-cross-provider-v2-eligibility.yml` — eligibility/filtering before scientific comparison;
- hosted/QA jobs that invoke safe provider probes and the authenticated functional campaign.

Associated scripts distinguish separate questions:

```text
provider secret/config exists?
provider/model eligible/free?
initial V14 request reproducible?
response shape valid?
completion truncates?
quota/rate-limit permits comparison?
B204 authenticated functional requirements pass?
```

Do not collapse them into one `provider PASS` flag.

## 4. Current hosted functional acceptance rule

The live production path requires the real managed browser session. Current B204 suite:

```text
F01 explicit asset condition
F02 causal investigation
F03 data quality
```

Current result is 0/3 because the first OpenRouter decision fails before a TRACTIAN tool call. A sanitized probe observed HTTP 200 + exact model + assistant content but `finish_reason=length`. A bounded follow-up experiment hit HTTP 429 for every variant and remains `INCONCLUSIVE`.

A final workflow/job may mark the migration functionally green only when the **exact deployed candidate SHA** gets 3/3 with:

- real managed authentication;
- exact OpenRouter provider/model/route provenance;
- valid typed model decisions;
- real TRACTIAN tool calls;
- grounded terminal/response mode;
- persisted evaluation/verification;
- no tenant/action/cost/provenance hard-gate regression.

Never add a production-auth bypass merely to automate this gate.

## 5. Governed action workflows / smokes

The controlled production pre-deploy governed-write smoke has exercised all five canonical action transports with HTTP 200 acceptance and no sensitive-material recording.

Treat that as a **specialized/promotion evidence class**, not as full action security acceptance. Final action SECURITY-V1 still needs independent adversarial scenarios for cross-user/tenant authorization, altered confirmation, duplicate confirmation, lease loss, ambiguity/`UNCERTAIN`, kill switch, prompt/tool injection and leakage.

## 6. Frontend regression/deployment

Current hosted frontend is `4364364266c6a88d4affd85cb3a734c774cd42c8`. Frontend may advance independently from backend/supplied API if contracts remain compatible and browser gates pass.

Provider-free Playwright is a deterministic CI dependency replacement. It cannot override a failing hosted OpenRouter functional campaign.

## 7. Specialized validation

Examples include:

- production runtime/build/release checks;
- PostgreSQL operational/RLS/recovery/distributed correctness;
- observability/realtime/verification;
- action custody/idempotency/lease regressions;
- provider-free EDD/evaluator campaigns;
- Railway/IaC contracts;
- full-product Playwright;
- targeted hosted provider/TRACTIAN/action smoke gates.

Each workflow proves only its declared scope.

## 8. Experimental workflow discipline

Provider/model/framework/adaptive challengers follow:

```text
measured gap
→ eligibility hard gates
→ preregistered manifest/protocol
→ controlled run
→ machine-readable results
→ failure/uncertainty analysis
→ PROMOTE | REJECT | INCONCLUSIVE | NO_CHANGE | NO_SELECTION
```

Historical/consumed experiment YAML remains for provenance. Do not rerun consumed packets merely to seek a preferred answer.

## 9. Workflow lifecycle labels

Every new workflow should be one of:

- `required` — ordinary merge regression;
- `promotion` — intentional exact-SHA hosted release gate;
- `specialized` — targeted engineering/security/production validation;
- `repository-maintenance` — narrow repo operation;
- `experimental` — preregistered research execution;
- `historical-one-shot` — retained only for provenance.

Prefer reusable scripts/modules + a small number of stable orchestration workflows over one YAML per tiny check.

## 10. Safety rules

- never print provider/database/auth/TRACTIAN/grant/actor/evaluator/blind secrets;
- never record raw provider material unless a separate explicitly sanitized protocol authorizes a safe subset;
- keep provider-free regression distinct from live-provider consumption;
- preserve exact SHA/protocol identity;
- do not silently relax expected SHA, model/route, quota, cost or gold-isolation gates;
- no paid/model fallback to make a workflow green;
- no acceptance of truncated `finish_reason=length` output;
- no unbounded provider retry loops;
- never treat skipped/not-triggered jobs as pass;
- preserve scientifically material failed/inconclusive attempts;
- do not add managed-auth/tenant bypasses for hosted prompt tests;
- do not delete historical workflows until unreferenced provenance is proven.

## 11. Cleanup / branch governance

When unsafe to rerun but provenance-sensitive, disable future triggers rather than falsifying history. Physical deletion/rename requires proof that no frozen evidence, ADR, active workflow, reproduction contract or Actions provenance references the file.

Branch protection remains external configuration: after applying it, verify `main.protected=true` and the stable `required-gate` context before documenting enforcement as closed.