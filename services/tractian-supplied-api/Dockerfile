FROM python:3.11.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/srv/tractian/api

WORKDIR /srv/tractian
COPY runtime.bundle.b64.part* /tmp/tractian-bundle/
RUN cat /tmp/tractian-bundle/runtime.bundle.b64.part* \
      | base64 -d > /tmp/tractian-runtime.tar.gz \
    && tar -xzf /tmp/tractian-runtime.tar.gz -C /srv/tractian \
    && python -m pip install --no-cache-dir -r /srv/tractian/requirements.lock \
    && rm -rf /tmp/tractian-bundle /tmp/tractian-runtime.tar.gz

EXPOSE 8080
CMD ["sh", "-c", "exec uvicorn app.hosting:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers --forwarded-allow-ips='*'"]
