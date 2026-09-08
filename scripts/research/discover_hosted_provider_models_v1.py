from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


PROVIDERS = (
    ("groq", "https://api.groq.com/openai/v1/models", "GROQ_API_KEY"),
    ("nvidia", "https://integrate.api.nvidia.com/v1/models", "NVIDIA_API_KEY"),
    ("openrouter", "https://openrouter.ai/api/v1/models", "OPENROUTER_API_KEY"),
)

KEYWORDS = (
    "gpt-oss",
    "nemotron",
    "qwen",
    "glm",
    "deepseek",
    "kimi",
    "llama",
    "mistral",
    "gemma",
    "inkling",
)


def _is_zero_price(value: object) -> bool:
    try:
        return float(str(value)) == 0.0
    except (TypeError, ValueError):
        return False


def _summarize(provider: str, body: object) -> dict[str, object]:
    if not isinstance(body, dict) or not isinstance(body.get("data"), list):
        return {"provider": provider, "schema_valid": False, "model_count": 0, "candidate_ids": []}
    rows = [item for item in body["data"] if isinstance(item, dict) and isinstance(item.get("id"), str)]
    ids = sorted({str(item["id"]) for item in rows})
    keyword_ids = [model_id for model_id in ids if any(keyword in model_id.lower() for keyword in KEYWORDS)]
    result: dict[str, object] = {
        "provider": provider,
        "schema_valid": True,
        "model_count": len(ids),
        "candidate_ids": keyword_ids,
    }
    if provider == "openrouter":
        free_ids: list[str] = []
        for item in rows:
            pricing = item.get("pricing")
            if not isinstance(pricing, dict):
                continue
            if _is_zero_price(pricing.get("prompt")) and _is_zero_price(pricing.get("completion")):
                free_ids.append(str(item["id"]))
        result["zero_price_candidate_ids"] = sorted(
            model_id for model_id in set(free_ids) if any(keyword in model_id.lower() for keyword in KEYWORDS)
        )
    return result


def main() -> int:
    results: list[dict[str, object]] = []
    for provider, url, secret_name in PROVIDERS:
        key = os.environ.get(secret_name, "").strip()
        if not key:
            results.append({"provider": provider, "status": "SECRET_ABSENT"})
            continue
        request = urllib.request.Request(
            url,
            method="GET",
            headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=20.0) as response:
                status = int(response.status)
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            results.append({"provider": provider, "status": "HTTP_ERROR", "http_status": int(exc.code)})
            continue
        except Exception as exc:
            results.append({"provider": provider, "status": "CLIENT_ERROR", "error_type": type(exc).__name__})
            continue
        summary = _summarize(provider, body)
        summary["status"] = "OK"
        summary["http_status"] = status
        results.append(summary)
    print(json.dumps({"schema_version": "hosted-provider-model-discovery-v1", "results": results}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
