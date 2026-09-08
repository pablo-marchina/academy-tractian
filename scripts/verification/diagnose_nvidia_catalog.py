from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Mapping

ENDPOINT = "https://integrate.api.nvidia.com/v1/models"
SCHEMA_VERSION = "nvidia-hosted-catalog-diagnostic-v1"
TARGETS = (
    "nvidia/llama-3.3-nemotron-super-49b-v1",
    "nvidia/llama-3.3-nemotron-super-49b-v1.5",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def main() -> int:
    token = os.environ.get("NVIDIA_API_KEY", "").strip()
    if not token:
        raise RuntimeError("missing:NVIDIA_API_KEY")

    request = urllib.request.Request(
        ENDPOINT,
        method="GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "academy-tractian-nvidia-catalog-diagnostic/1.0",
        },
    )

    started = time.perf_counter_ns()
    raw = ""
    status: int | None = None
    transport_error: str | None = None
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status = int(response.status)
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        raw = exc.read().decode("utf-8", errors="replace")
    except Exception as exc:
        transport_error = type(exc).__name__
    latency_ms = max(0, time.perf_counter_ns() - started) // 1_000_000

    try:
        payload: Any = json.loads(raw) if raw else {}
    except Exception:
        payload = {}

    data = payload.get("data") if isinstance(payload, Mapping) else None
    model_ids: list[str] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, Mapping) and isinstance(item.get("id"), str):
                model_ids.append(item["id"])

    normalized = sorted(set(model_ids))
    nemotron_ids = [model_id for model_id in normalized if "nemotron" in model_id.casefold()]
    super_ids = [
        model_id
        for model_id in nemotron_ids
        if "super" in model_id.casefold() and ("49b" in model_id.casefold() or "120b" in model_id.casefold())
    ]
    target_presence = {target: target in normalized for target in TARGETS}

    error_code = None
    error_type = None
    if isinstance(payload, Mapping) and isinstance(payload.get("error"), Mapping):
        error = payload["error"]
        if error.get("code") is not None:
            error_code = str(error["code"])[:128]
        if error.get("type") is not None:
            error_type = str(error["type"])[:128]

    report = {
        "schema_version": SCHEMA_VERSION,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "provider_id": "nvidia",
        "route": "integrate.api.nvidia.com/v1/models",
        "http_status": status,
        "latency_ms": latency_ms,
        "catalog_shape_ok": isinstance(data, list),
        "model_count": len(normalized),
        "catalog_sha256": digest(normalized) if normalized else None,
        "target_presence": target_presence,
        "nemotron_model_ids": nemotron_ids[:50],
        "candidate_super_model_ids": super_ids[:20],
        "provider_error_code": error_code,
        "provider_error_type": error_type,
        "transport_error_type": transport_error,
        "credentials_recorded": False,
        "raw_provider_material_recorded": False,
    }
    report["result"] = "PASS" if status == 200 and isinstance(data, list) else "FAIL"
    print("NVIDIA_CATALOG_DIAGNOSTIC=" + canonical_json(report), flush=True)
    return 0 if report["result"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
