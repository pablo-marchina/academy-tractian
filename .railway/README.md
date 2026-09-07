# Railway Infrastructure as Code

The final production topology is described in [`railway.ts`](railway.ts).

This is intentionally a named `production` partial. It manages only `production-api` and `production-web`; historical `hosted-pilot` remains outside this partial.

All Railway-managed values and the two PostgreSQL DSNs use `preserve()`. Never commit PostgreSQL DSNs, provider keys, authentication secrets or partner credentials.

Repository-safe validation:

```bash
python scripts/validate_railway_iac_contract.py
```

The dedicated `railway-iac-contract` workflow also validates the TypeScript DSL.

Before the first IaC apply, use an authenticated Railway CLI session and review:

```bash
railway config plan
```

Accept only a plan with no `hosted-pilot` deletion, no unexpected destructive change, and exact production-api/production-web scope. Then apply the reviewed plan.

Current external blockers for `production-api`:

```text
ACADEMY_POSTGRES_INTERNAL_DSN
ACADEMY_POSTGRES_SCOPED_DSN
```

Their values must remain in Railway's native secret channel, never in source.
