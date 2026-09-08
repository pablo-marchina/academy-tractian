from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from academy_tractian.provider_clients import UrllibProviderJsonTransport  # noqa: E402
from academy_tractian.provider_tournament_cross_provider_v2 import (  # noqa: E402
    NVIDIA_CANDIDATE,
    OPENROUTER_CANDIDATE,
    groq_candidate,
    run_synthetic_eligibility_probe,
)


GROQ_PROBE_ORDER = ("openai/gpt-oss-20b", "qwen/qwen3.8-27b")


def _required_secret(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"required hosted secret absent: {name}")
    return value


def _openrouter_capacity(api_key: str) -> dict[str, object]:
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        method="GET",
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20.0) as response:
            status = int(response.status)
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {
            "request_succeeded": False,
            "http_status": int(exc.code),
            "is_free_tier": None,
            "capacity_ge_85": False,
        }
    except Exception as exc:
        return {
            "request_succeeded": False,
            "http_status": None,
            "error_type": type(exc).__name__,
            "is_free_tier": None,
            "capacity_ge_85": False,
        }
    data = body.get("data") if isinstance(body, dict) else None
    is_free_tier = data.get("is_free_tier") if isinstance(data, dict) else None
    return {
        "request_succeeded": status == 200 and isinstance(is_free_tier, bool),
        "http_status": status,
        "is_free_tier": is_free_tier if isinstance(is_free_tier, bool) else None,
        "capacity_ge_85": is_free_tier is False,
    }


def main() -> int:
    groq_key = _required_secret("GROQ_API_KEY")
    nvidia_key = _required_secret("NVIDIA_API_KEY")
    openrouter_key = _required_secret("OPENROUTER_API_KEY")

    capacity = _openrouter_capacity(openrouter_key)
    evidence: dict[str, object] = {
        "schema_version": "provider-tournament-cross-provider-v2-eligibility",
        "decision_id": "DP-006",
        "openrouter_capacity": capacity,
        "groq_probe_order": list(GROQ_PROBE_ORDER),
        "groq_selected_model": None,
        "probes": [],
        "all_three_eligible": False,
        "raw_provider_material_recorded": False,
        "secret_material_recorded": False,
    }

    # The 85-observation OpenRouter geometry is impossible on the documented 50/day free tier.
    # Fail before any DP-006 inference so no partial provider probes influence a future design.
    if capacity.get("capacity_ge_85") is not True:
        evidence["closure_reason"] = "OPENROUTER_DAILY_CAPACITY_BELOW_PREREGISTERED_GEOMETRY_OR_UNPROVEN"
        print(json.dumps(evidence, sort_keys=True), flush=True)
        return 2

    transport = UrllibProviderJsonTransport()
    probes: list[dict[str, object]] = []

    groq_result: dict[str, object] | None = None
    selected_groq = None
    for model_id in GROQ_PROBE_ORDER:
        result = run_synthetic_eligibility_probe(
            candidate=groq_candidate(model_id),
            api_key=groq_key,
            transport=transport,
        )
        probes.append(result)
        if result.get("passed") is True:
            groq_result = result
            selected_groq = model_id
            break
    if groq_result is None and probes:
        groq_result = probes[-1]

    nvidia_result = run_synthetic_eligibility_probe(
        candidate=NVIDIA_CANDIDATE,
        api_key=nvidia_key,
        transport=transport,
    )
    probes.append(nvidia_result)

    openrouter_result = run_synthetic_eligibility_probe(
        candidate=OPENROUTER_CANDIDATE,
        api_key=openrouter_key,
        transport=transport,
    )
    probes.append(openrouter_result)

    all_three = bool(
        selected_groq
        and groq_result
        and groq_result.get("passed") is True
        and nvidia_result.get("passed") is True
        and openrouter_result.get("passed") is True
    )
    evidence["groq_selected_model"] = selected_groq
    evidence["probes"] = probes
    evidence["all_three_eligible"] = all_three
    evidence["closure_reason"] = None if all_three else "ONE_OR_MORE_PROVIDER_ROUTES_FAILED_ELIGIBILITY"
    print(json.dumps(evidence, sort_keys=True), flush=True)
    return 0 if all_three else 3


if __name__ == "__main__":
    raise SystemExit(main())
