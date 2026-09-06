from __future__ import annotations

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = os.environ["ACADEMY_PRODUCTION_API_BASE_URL"].rstrip("/")
EXPECTED_SHA = os.environ["ACADEMY_EXPECTED_DEPLOYED_SHA"].strip().lower()


def fetch_json(path: str, *, attempts: int = 6) -> dict[str, object]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(
                f"{BASE_URL}{path}",
                headers={"User-Agent": "academy-tractian-hosted-g2-smoke/1"},
            )
            with urlopen(request, timeout=15) as response:  # noqa: S310 - fixed production HTTPS origin
                if response.status != 200:
                    raise RuntimeError(f"{path} returned HTTP {response.status}")
                payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, dict):
                    raise RuntimeError(f"{path} returned a non-object JSON payload")
                return payload
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, RuntimeError) as exc:
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(min(2**attempt, 8))
    raise RuntimeError(f"hosted G2 request failed for {path}: {type(last_error).__name__}") from last_error


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    health = fetch_json("/health")
    ready = fetch_json("/ready")
    release = fetch_json("/api/meta/release")

    require(health.get("status") == "ok", "hosted /health did not report ok")
    require(ready.get("status") == "ready", "hosted /ready did not report ready")

    require(release.get("schema_version") == "remote-production-release-v3", "release schema drift")
    require(release.get("environment") == "production", "release environment is not production")
    require(release.get("cost_policy") == "usd0-hard-gate", "USD0 hard gate metadata drift")
    require(release.get("browser_iam_mode") == "neon-auth", "hosted browser IAM mode drift")
    require(release.get("release_git_sha") == EXPECTED_SHA, "configured release SHA mismatch")
    require(release.get("artifact_git_sha") == EXPECTED_SHA, "baked artifact SHA mismatch")
    require(release.get("artifact_identity_verified") is True, "artifact identity is not verified")
    require(
        release.get("railway_runtime_identity_verified") is True,
        "Railway runtime SHA was not independently verified",
    )

    # Intentionally print only fields defined by the browser-safe release contract.
    sanitized = {
        "health_status": health.get("status"),
        "ready_status": ready.get("status"),
        "release_schema": release.get("schema_version"),
        "release_git_sha": release.get("release_git_sha"),
        "artifact_git_sha": release.get("artifact_git_sha"),
        "artifact_identity_verified": release.get("artifact_identity_verified"),
        "railway_runtime_identity_verified": release.get("railway_runtime_identity_verified"),
        "environment": release.get("environment"),
        "browser_iam_mode": release.get("browser_iam_mode"),
        "cost_policy": release.get("cost_policy"),
    }
    print(json.dumps(sanitized, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
