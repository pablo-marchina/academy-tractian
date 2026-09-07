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

# Keep the supplied API/runtime immutable and add the product→synthetic-user translation only
# at the hosting boundary. The bridge validates its agent-visible user pool during image build.
COPY identity_bridge.py /srv/tractian/api/app/identity_bridge.py
RUN python /srv/tractian/api/app/identity_bridge.py

EXPOSE 8080
CMD ["sh", "-c", "exec uvicorn app.identity_bridge:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers --forwarded-allow-ips='*'"]
