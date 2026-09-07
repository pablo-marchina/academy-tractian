from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any


_RUNTIME_ROOT = Path("/srv/tractian")
_MAX_USER_ID_BYTES = 256
_EXPECTED_CASE_FIELDS = frozenset(
    {"id", "ticket_id", "company_id", "user_id", "asset_id", "message"}
)
_EXPECTED_CASE_COUNT = 17


def _validate_user_id(value: str, *, label: str) -> str:
    normalized = value.strip()
    if not normalized or normalized != value:
        raise ValueError(f"invalid {label}")
    encoded = normalized.encode("ascii")
    if len(encoded) > _MAX_USER_ID_BYTES:
        raise ValueError(f"invalid {label}")
    if any(byte < 0x20 or byte == 0x7F for byte in encoded):
        raise ValueError(f"invalid {label}")
    return normalized


def _candidate_sources(path: Path | None = None) -> tuple[Path, ...]:
    if path is not None:
        return (path,)
    configured = os.environ.get("ACADEMY_TRACTIAN_CASE_SOURCE")
    if configured:
        return (Path(configured),)
    candidates = tuple(sorted(item for item in _RUNTIME_ROOT.rglob("cases.json") if item.is_file()))
    if not candidates:
        raise RuntimeError("tractian_domain_identity_case_source_unavailable")
    return candidates


def _sanitized_case_rows(source: Path) -> list[dict[str, object]] | None:
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or len(payload) != _EXPECTED_CASE_COUNT:
        return None
    if not all(isinstance(item, dict) and set(item) == _EXPECTED_CASE_FIELDS for item in payload):
        return None
    return payload


def load_domain_user_ids(path: Path | None = None) -> tuple[str, ...]:
    """Load ids only from the schema-verified, agent-visible sanitized case surface."""

    user_ids: set[str] = set()
    matched_source = False
    for source in _candidate_sources(path):
        rows = _sanitized_case_rows(source)
        if rows is None:
            continue
        matched_source = True
        for row in rows:
            raw = row.get("user_id")
            if not isinstance(raw, str):
                raise RuntimeError("tractian_domain_identity_case_source_invalid")
            user_ids.add(_validate_user_id(raw, label="TRACTIAN domain user id"))

    if not matched_source:
        raise RuntimeError("tractian_domain_identity_sanitized_case_source_unavailable")
    if not user_ids:
        raise RuntimeError("tractian_domain_identity_pool_unavailable")
    return tuple(sorted(user_ids))


def map_application_user_id(application_user_id: str, domain_user_ids: tuple[str, ...]) -> str:
    """Deterministically map one product identity to one valid synthetic TRACTIAN identity."""

    source_user = _validate_user_id(application_user_id, label="application user id")
    if not domain_user_ids:
        raise RuntimeError("tractian_domain_identity_pool_unavailable")
    if source_user in domain_user_ids:
        return source_user

    digest = sha256(f"academy-tractian-domain-user-v1:{source_user}".encode("utf-8")).digest()
    index = int.from_bytes(digest[:8], "big") % len(domain_user_ids)
    return domain_user_ids[index]


class SyntheticDomainIdentityBridge:
    """Translate product user ids only at the hosted synthetic TRACTIAN boundary.

    Neon remains authoritative for browser authentication, tenancy and run ownership. The supplied
    API has its own synthetic user universe, so its x-user-id cannot be the Neon primary key.
    This bridge derives a stable synthetic persona from the schema-verified agent-visible cases
    without exposing the mapped id to the browser or changing service authentication.
    """

    def __init__(self, app: Any, *, domain_user_ids: tuple[str, ...]) -> None:
        if not domain_user_ids:
            raise RuntimeError("tractian_domain_identity_pool_unavailable")
        self.app = app
        self.domain_user_ids = domain_user_ids

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        headers = list(scope.get("headers") or [])
        incoming: str | None = None
        rewritten: list[tuple[bytes, bytes]] = []
        for raw_name, raw_value in headers:
            if raw_name.lower() == b"x-user-id":
                if incoming is not None:
                    raise RuntimeError("tractian_domain_identity_duplicate_user_header")
                incoming = raw_value.decode("ascii")
                continue
            rewritten.append((raw_name, raw_value))

        if incoming is None:
            await self.app(scope, receive, send)
            return

        mapped = map_application_user_id(incoming, self.domain_user_ids)
        bridged_scope = dict(scope)
        bridged_scope["headers"] = [*rewritten, (b"x-user-id", mapped.encode("ascii"))]
        await self.app(bridged_scope, receive, send)


def _build_app() -> Any:
    from app.hosting import app as supplied_app

    return SyntheticDomainIdentityBridge(
        supplied_app,
        domain_user_ids=load_domain_user_ids(),
    )


if __name__ == "__main__":
    # Docker build-time fail-closed validation. Do not print or persist synthetic ids.
    load_domain_user_ids()
else:
    app = _build_app()
