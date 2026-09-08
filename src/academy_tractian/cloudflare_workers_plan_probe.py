from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping
import urllib.error
import urllib.request


CLOUDFLARE_API_ROOT = "https://api.cloudflare.com/client/v4"


class CloudflarePlanProbeError(RuntimeError):
    pass


@dataclass(frozen=True)
class CloudflareWorkersPlanEvidence:
    state: str
    workers_paid_detected: bool
    default_usage_model: str | None
    account_subscription_count: int
    direct_api_probe: bool = True
    provider_inference_used: bool = False
    raw_response_recorded: bool = False


def _get_json(*, url: str, api_token: str, timeout_seconds: float = 20.0) -> Mapping[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            if int(response.status) != 200:
                raise CloudflarePlanProbeError("cloudflare_plan_probe_http_status")
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise CloudflarePlanProbeError(f"cloudflare_plan_probe_http_{int(exc.code)}") from None
    except CloudflarePlanProbeError:
        raise
    except Exception:
        raise CloudflarePlanProbeError("cloudflare_plan_probe_transport_failure") from None
    try:
        payload = json.loads(raw)
    except Exception:
        raise CloudflarePlanProbeError("cloudflare_plan_probe_json_invalid") from None
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise CloudflarePlanProbeError("cloudflare_plan_probe_api_failure")
    result = payload.get("result")
    if not isinstance(result, (dict, list)):
        raise CloudflarePlanProbeError("cloudflare_plan_probe_result_invalid")
    return payload


def _flatten_strings(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        found.append(value.casefold())
    elif isinstance(value, Mapping):
        for key, item in value.items():
            found.append(str(key).casefold())
            found.extend(_flatten_strings(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(_flatten_strings(item))
    return found


def probe_workers_plan(*, api_token: str, account_id: str) -> CloudflareWorkersPlanEvidence:
    """Read account settings + subscriptions; fail closed when Free cannot be proven.

    Cloudflare documents that accounts are Workers Free by default and Workers Paid is a paid
    account subscription. Standard is available to Workers Paid. A positive Workers/Standard paid
    signal is therefore disqualifying. Absence of a paid Workers subscription is accepted only when
    the subscription endpoint itself is readable; permission failure is not interpreted as Free.
    """

    if not api_token.strip() or not account_id.strip():
        raise CloudflarePlanProbeError("cloudflare_plan_probe_credentials_missing")
    settings_payload = _get_json(
        url=f"{CLOUDFLARE_API_ROOT}/accounts/{account_id}/workers/account-settings",
        api_token=api_token,
    )
    settings = settings_payload["result"]
    if not isinstance(settings, dict):
        raise CloudflarePlanProbeError("cloudflare_plan_probe_settings_invalid")
    usage_model_raw = settings.get("default_usage_model")
    usage_model = usage_model_raw.casefold() if isinstance(usage_model_raw, str) else None

    subscriptions_payload = _get_json(
        url=f"{CLOUDFLARE_API_ROOT}/accounts/{account_id}/subscriptions",
        api_token=api_token,
    )
    subscriptions = subscriptions_payload["result"]
    if not isinstance(subscriptions, list):
        raise CloudflarePlanProbeError("cloudflare_plan_probe_subscriptions_invalid")

    paid_workers_signal = usage_model == "standard"
    for subscription in subscriptions:
        strings = _flatten_strings(subscription)
        text = " ".join(strings)
        worker_related = "worker" in text
        paid_related = any(token in text for token in ("paid", "standard", "workers_standard"))
        if worker_related and paid_related:
            paid_workers_signal = True

    state = "WORKERS_PAID" if paid_workers_signal else "WORKERS_FREE"
    return CloudflareWorkersPlanEvidence(
        state=state,
        workers_paid_detected=paid_workers_signal,
        default_usage_model=usage_model,
        account_subscription_count=len(subscriptions),
    )
