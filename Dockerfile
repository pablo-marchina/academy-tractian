# syntax=docker/dockerfile:1.7
#
# Provider-neutral backend release artifact for the remote-production P0.
# The multi-platform Docker Official Image index is pinned so linux/amd64 and linux/arm64
# resolve from the same immutable Python 3.11.16 / Debian Bookworm image set.
ARG PYTHON_BASE_IMAGE="python:3.11.16-slim-bookworm@sha256:528257d48c1da0dcecc2e725d1ae34498d60c965f1241e39cd6a85a8859bdf84"

FROM ${PYTHON_BASE_IMAGE} AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /build

COPY pyproject.toml ./
COPY src ./src
COPY research/e2 ./research/e2

RUN python -m pip wheel . --no-deps --wheel-dir /wheelhouse


FROM ${PYTHON_BASE_IMAGE} AS runtime

# Railway injects this system variable for GitHub-backed builds. The build fails closed when the
# immutable source identity is absent or malformed; runtime configuration cannot manufacture it.
ARG RAILWAY_GIT_COMMIT_SHA=""
ARG ACADEMY_BUILD_ID="railway-build"

LABEL org.opencontainers.image.title="academy-tractian-remote-backend" \
      org.opencontainers.image.description="USD0-gated remote production backend artifact" \
      org.opencontainers.image.source="https://github.com/pablo-marchina/academy-tractian" \
      org.opencontainers.image.revision="${RAILWAY_GIT_COMMIT_SHA}" \
      academy.tractian.build-id="${ACADEMY_BUILD_ID}" \
      academy.tractian.cost-policy="usd0-hard-gate" \
      academy.tractian.provider-selection="NO_SELECTION"

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ACADEMY_BIND_HOST=0.0.0.0 \
    ACADEMY_PORT=8000

WORKDIR /app

COPY requirements-production.lock /tmp/requirements-production.lock
COPY --from=builder /wheelhouse /tmp/wheelhouse

RUN RAILWAY_GIT_COMMIT_SHA="${RAILWAY_GIT_COMMIT_SHA}" python - <<'PY'
import json
import os
import re
from pathlib import Path

sha = os.environ["RAILWAY_GIT_COMMIT_SHA"]
if re.fullmatch(r"[0-9a-f]{40}", sha) is None:
    raise SystemExit("RAILWAY_GIT_COMMIT_SHA must be an exact lowercase 40-character Git SHA")
Path("/app/.academy-release-identity.json").write_text(
    json.dumps(
        {"schema_version": "academy-release-artifact-v1", "git_sha": sha},
        separators=(",", ":"),
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)
PY

RUN python -m pip install --no-cache-dir -r /tmp/requirements-production.lock \
    && python -m pip install --no-cache-dir --no-deps /tmp/wheelhouse/academy_tractian-*.whl \
    && python -m pip check \
    && chmod 0444 /app/.academy-release-identity.json \
    && rm -rf /tmp/wheelhouse /tmp/requirements-production.lock \
    && groupadd --system --gid 10001 academy \
    && useradd --system --uid 10001 --gid 10001 --home-dir /nonexistent --shell /usr/sbin/nologin academy

USER 10001:10001

EXPOSE 8000

# Serving boot intentionally fails closed if the mandatory remote-production environment is absent,
# if the runtime release SHA disagrees with the baked artifact SHA, or if USD0/no-local constraints
# are violated. Schema migration is a separate command:
#   docker run --entrypoint python <image> -m academy_tractian.remote_migrate
ENTRYPOINT ["python", "-m", "academy_tractian.remote_server"]
