# Academy × TRACTIAN Frontend

Production React/TypeScript frontend for the hosted Academy × TRACTIAN Industrial Agent + Evaluation product.

**Current hosted frontend source:** `1bc124a8d4dbd029178ff8129b25452129445de7`  
**Production service:** Railway `production-web`  
**Primary navigation:** Home / Analyses / Technical

## Current product flow

The frontend consumes only the real browser-safe product API and managed auth boundary:

```text
managed sign-in
→ Home: one industrial question
→ POST /api/runs
→ authenticated SSE + durable catch-up
→ human-readable progress
→ Result: conclusion + next step
→ contextual Evidence when useful
→ Analyses for persisted history
→ Technical for specialist depth
```

There are no fake progress timers or browser-owned runtime identities in the production flow.

## Information architecture

### Home

Owns the first-user question entry. The user should not need internal company/asset identifiers when the backend can discover them through authorized fleet context.

### Result / Evidence

Result owns the selected run's customer-facing conclusion and next action. Evidence is contextual drill-down rather than a competing default navigation layer.

### Analyses

Owns persisted run history and selection.

### Technical

Specialist-only depth for current analysis/trace, quality/evaluation, data, system/capabilities, governed actions and controlled studies.

The earlier four-layer depth-tab UX remains historical implementation context, not the current primary product journey.

## Current UX quality target

The latest user review found the interface still too visually dense and difficult to navigate in places. The next structural simplification pass applies to the **entire frontend**, not just Home.

North star:

> **each screen should have one main question for the user to answer.**

Default rule:

> if an element does not help the user understand where they are, what happened or what they should do now, it should not appear by default.

Global direction:

- fewer simultaneous cards, panels, borders, shadows, badges and eyebrow labels;
- one principal heading/task per screen;
- one obvious primary CTA per screen;
- Evidence contextual from Result, not a global destination;
- Technical outside the normal user path;
- History list/recognition first, filters/table density only when justified by volume;
- summary first for Architecture/Trace/Evaluation/Capabilities;
- presets/questions before analytics dimension/filter builders;
- one action and its consequence at a time in Action Control;
- aggressive linearization on mobile;
- preserve ≥44 px interaction targets, keyboard navigation, visible focus, semantic accessibility and reduced motion.

Automated tests can prove browser behavior/accessibility-oriented invariants; they do **not** prove human usability. Representative-user evidence remains a separate final-quality gate.

## Managed authentication UX

The frontend distinguishes:

```text
checking
anonymous
authenticated
temporarily unavailable
```

Current behavior includes:

- invalid protected-session signal exits authenticated state;
- temporary `managed_session_unavailable` exposes retry rather than pretending the session is invalid;
- session revalidation on focus/visibility return;
- sign-in/create-account/password affordances without making browser state tenant authority.

The browser never chooses canonical organization, role, permissions, action grants or vendor actor identity.

## Governed action UX

`ActionControl` visualizes server-owned action state and exact confirmation. Human-facing states correspond to the canonical backend state machine:

```text
PENDING_CONFIRMATION  → waiting for confirmation
CONFIRMED             → confirmed
EXECUTING             → running
ACCEPTED              → accepted by external service
BLOCKED               → blocked for safety
NOT_ACCEPTED           → not accepted
UNCERTAIN              → outcome needs verification
```

Safety rules:

- show consequence/impact before confirmation;
- confirmation is for the exact existing action;
- browser does not send replacement action arguments, permissions, idempotency keys, grants or vendor actor identity;
- never render a successful action merely because a request was sent;
- only canonical backend `ACCEPTED` may appear as externally accepted;
- `UNCERTAIN` must remain visibly unresolved rather than encouraging blind retry.

Current production action limitation is backend/vendor-side: the five-action live smoke found `update_asset_config` HTTP 403 under the current upstream identity mapping. The frontend should present backend action truth accurately and must not hide that distinction.

## Safe observability

Browser-visible data may include safe run/action IDs, states, traces, evidence, capability summaries and evaluation projections. It must not expose:

- credentials/tokens/session material;
- raw server-owned grants;
- private action custody/arguments outside the approved safe projection;
- idempotency material;
- server-owned TRACTIAN vendor actor mapping;
- evaluator-private/gold material;
- hidden chain-of-thought/private model reasoning.

## Production source contract

The hosted `production-web` service builds from canonical branch `release/production-final`, Railway root `frontend`, `Dockerfile.production`.

A Railway **Redeploy** may reuse a previously captured source/config snapshot. It is not proof that current branch head or edited service configuration was fetched. Production evidence must record the actual deployed commit SHA.

The same-origin Caddy boundary proxies product API/SSE and managed Neon Auth endpoints. The proxy canonicalizes required upstream host forwarding while preserving the public browser origin so managed-auth base-URL/CSRF behavior stays meaningful.

## Local development

Start the API on `127.0.0.1:8000`, then:

```bash
cd frontend
npm ci
npm run dev
```

Vite proxies `/api`, `/health`, `/ready` and `/version` to the local API by default. Local proxy settings are development-only and must not become production topology.

## Quality gates

```bash
npm run typecheck
npm test
npm run build
npx playwright test
```

The required production matrix also exercises full-product browser acceptance with PostgreSQL, controller/tool/evaluation/SSE integration and action UI safety invariants.

PR #213 required-gate run `34164123263` passed Chromium full-product acceptance on the smoke-capable backend source. This is regression evidence, not proof of live vendor action acceptance.

## Frontend change checklist

Before adding UI:

1. What user question does this screen answer?
2. Is the information required now, or can it be contextual/technical drill-down?
3. Is the backend the authoritative source for this state?
4. Does the change accidentally expose tenant/action/vendor authority?
5. Does the control have one clear primary action and understandable failure state?
6. Does it preserve keyboard/focus/mobile/reduced-motion behavior?
7. Are tests proving behavior rather than a brittle screenshot layout?

See root [`README.md`](../README.md), [`../docs/ACTIVE-PROJECT-STATUS.md`](../docs/ACTIVE-PROJECT-STATUS.md) and [`../docs/PLAYWRIGHT-ACCEPTANCE.md`](../docs/PLAYWRIGHT-ACCEPTANCE.md).