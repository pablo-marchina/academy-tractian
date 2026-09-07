from __future__ import annotations

import json
import os
from urllib.request import urlopen

from research.e2.models import ExecutionBinding
from research.e2.transport import build_b0_request

from .runtime import canonical_tool_registry
from .tractian_transport import ProductionTractianTransport


JUSTIFICATION = (
    "Operator explicitly approved this exact governed production write smoke against the supplied "
    "TRACTIAN test runtime after the production safety gates passed."
)


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required smoke variable: {name}")
    return value


def _load_action_targets() -> dict[str, str]:
    raw = _required("SMOKE_ACTION_TARGETS_JSON")
    decoded = json.loads(raw)
    required = {
        "update_asset_config",
        "reprocess_analysis",
        "request_specialist_analysis",
        "request_retraining",
        "escalate_case",
    }
    if not isinstance(decoded, dict) or set(decoded) != required:
        raise RuntimeError("smoke action target set must contain exactly the five canonical actions")
    if any(not isinstance(value, str) or not value.strip() for value in decoded.values()):
        raise RuntimeError("smoke action targets must be non-empty strings")
    return {key: value.strip() for key, value in decoded.items()}


def _arguments(tool_name: str, resource_id: str) -> dict[str, object]:
    if tool_name == "update_asset_config":
        return {
            "asset_id": resource_id,
            "body": {
                "justification": JUSTIFICATION,
                "changes": {"criticality": "high"},
            },
        }
    if tool_name in {"reprocess_analysis", "request_specialist_analysis"}:
        return {
            "analysis_id": resource_id,
            "body": {"justification": JUSTIFICATION},
        }
    if tool_name == "request_retraining":
        return {
            "model_id": resource_id,
            "body": {"justification": JUSTIFICATION},
        }
    if tool_name == "escalate_case":
        return {
            "case_id": resource_id,
            "body": {"justification": JUSTIFICATION},
        }
    raise RuntimeError(f"unexpected smoke action: {tool_name}")


def _check_capabilities() -> dict[str, object]:
    base = _required("SMOKE_PRODUCTION_API_URL").rstrip("/")
    with urlopen(f"{base}/api/release0/capabilities", timeout=15) as response:  # noqa: S310
        payload = json.loads(response.read().decode("utf-8"))
    summary = payload.get("tool_summary", {})
    execution = payload.get("action_execution", {})
    release = payload.get("release", {})
    if response.status != 200:
        raise RuntimeError(f"capability smoke failed: http_{response.status}")
    if summary.get("actions") != 5 or summary.get("executable_actions") != 5:
        raise RuntimeError("capability smoke failed: five executable actions not advertised")
    if execution.get("enabled") is not True or execution.get("mode") != "GOVERNED_CONFIRMATION":
        raise RuntimeError("capability smoke failed: governed confirmation not enabled")
    if release.get("governed_action_path_enabled") is not True:
        raise RuntimeError("capability smoke failed: governed action path disabled")
    return {
        "http_status": response.status,
        "actions": summary.get("actions"),
        "executable_actions": summary.get("executable_actions"),
        "mode": execution.get("mode"),
        "governed_action_path_enabled": release.get("governed_action_path_enabled"),
    }


def main() -> None:
    user_id = _required("SMOKE_USER_ID")
    targets = _load_action_targets()
    base_url = _required("ACADEMY_TRACTIAN_BASE_URL")
    server_headers_raw = _required("ACADEMY_TRACTIAN_SERVER_HEADERS_JSON")
    server_headers = json.loads(server_headers_raw)
    if not isinstance(server_headers, dict) or not server_headers:
        raise RuntimeError("TRACTIAN smoke headers must be a non-empty JSON object")

    capability = _check_capabilities()
    transport = ProductionTractianTransport(
        base_url=base_url,
        server_headers={str(k): str(v) for k, v in server_headers.items()},
    )
    registry = canonical_tool_registry()
    binding = ExecutionBinding(
        identity_id="governed-write-production-smoke",
        user_id=user_id,
        seed=None,
    )

    results: list[dict[str, object]] = []
    for tool_name in (
        "reprocess_analysis",
        "request_specialist_analysis",
        "update_asset_config",
        "request_retraining",
        "escalate_case",
    ):
        tool = registry[tool_name]
        request = build_b0_request(tool, _arguments(tool_name, targets[tool_name]), binding)
        response = transport.request(request)
        accepted = isinstance(response.body, dict) and response.body.get("accepted") is True
        results.append(
            {
                "tool_name": tool_name,
                "http_status": response.status_code,
                "accepted": accepted,
            }
        )
        if response.status_code not in {200, 201, 202} or not accepted:
            raise RuntimeError(
                f"governed write transport smoke failed for {tool_name}: "
                f"http_{response.status_code}:accepted_{str(accepted).lower()}"
            )

    print(
        json.dumps(
            {
                "schema_version": "governed-write-production-smoke-v1",
                "status": "PASS",
                "capability": capability,
                "actions": results,
                "credentials_recorded": False,
                "resource_ids_recorded": False,
                "response_bodies_recorded": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
