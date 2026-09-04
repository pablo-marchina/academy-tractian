FROM python:3.11.16-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

WORKDIR /app

RUN groupadd --system academy \
    && useradd --system --gid academy --create-home academy

COPY pyproject.toml requirements.lock ./
COPY src ./src
COPY research/e2 ./research/e2
COPY scripts ./scripts

RUN python -m pip install --no-cache-dir "pip==26.2.1" \
    && PIP_CONSTRAINT=/app/requirements.lock python -m pip install --no-cache-dir . \
    && python scripts/validate_python_dependency_lock.py --allow-subset

USER academy

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/ready', timeout=3).read()"

CMD ["python", "-m", "academy_tractian.hosted_product"]
