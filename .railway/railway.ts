import {
  defineRailway,
  github,
  preserve,
  project,
  service,
} from "railway/iac";

export const partial = "production";

export default defineRailway(() => {
  const productionApi = service("production-api", {
    source: github("pablo-marchina/academy-tractian", { branch: "release/production-final" }),
    build: {
      dockerfilePath: "Dockerfile",
      watchPatterns: ["src/**", "research/e2/**", "Dockerfile", "pyproject.toml", "requirements-production.lock"],
    },
    healthcheck: "/health",
    healthcheckTimeout: 60,
    replicas: { "us-east4-eqdc4a": 1 },
    restarts: "on_failure",
    restartLimit: 5,
    env: {
      ACADEMY_PORT: preserve(),
      ACADEMY_MAX_WORKERS: preserve(),
      ACADEMY_COST_POLICY: preserve(),
      ACADEMY_ENVIRONMENT: preserve(),
      ACADEMY_RUNTIME_IDENTITY_ISSUER: preserve(),
      ACADEMY_RUNTIME_IDENTITY_AUDIENCE: preserve(),
      ACADEMY_RELEASE_GIT_SHA: preserve(),
      ACADEMY_PAID_FALLBACK_ENABLED: preserve(),
      ACADEMY_LOCAL_SERVING_ENABLED: preserve(),
      ACADEMY_PROVIDER_CALLS_ENABLED: preserve(),
      ACADEMY_POSTGRES_SCHEMA: preserve(),
      ACADEMY_DEPLOYMENT_ID: preserve(),
      ACADEMY_BROWSER_IAM_MODE: preserve(),
      ACADEMY_PUBLIC_BASE_URL: preserve(),
      ACADEMY_NEON_AUTH_BASE_URL: preserve(),
      ACADEMY_POSTGRES_INTERNAL_DSN: preserve(),
      ACADEMY_POSTGRES_SCOPED_DSN: preserve(),
    },
  });

  const productionWeb = service("production-web", {
    source: github("pablo-marchina/academy-tractian", {
      branch: "release/production-final",
      rootDirectory: "frontend",
    }),
    build: { dockerfilePath: "Dockerfile.production", watchPatterns: ["frontend/**"] },
    healthcheck: "/",
    healthcheckTimeout: 120,
    replicas: { "us-east4-eqdc4a": 1 },
    restarts: "on_failure",
    restartLimit: 5,
    env: {
      NEON_AUTH_BASE_PATH: preserve(),
      NEON_AUTH_HOST: preserve(),
    },
  });

  return project("academy-tractian-hosted-pilot", { resources: [productionApi, productionWeb] });
});
