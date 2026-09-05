from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Literal, Mapping
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from research.e2.models import BoundRequest, Permission
from research.e2.transport import RequestTransport, TransportResponse

from .action_safety import ResourceCompanyBinding
from .decision_source import ProviderCallIdentity, ProviderDecisionSource
from .postgres_product_api import create_postgres_action_capable_product_app
from .product_api import AuthenticatedRuntimeContext, DEFAULT_RUNTIME_PERMISSIONS
from .production_actions_v2 import ProductionActionPrincipal
from .provider_clients import (
    GoogleInteractionsDecisionClient,
    OpenAIResponsesDecisionClient,
    UrllibProviderJsonTransport,
)
from .provider_free_product import ProviderFreeScenarioDecisionSource, ProviderFreeTransport
from .runtime import canonical_tool_registry


DemoMode = Literal["live", "fallback"]
DemoProvider = Literal["google", "openai"]
_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "0.0.0.0", "::1"})


class LiveDemoConfigurationError(ValueError):
    """Hosted demo configuration is incomplete or would silently depend on localhost."""


def _required(env: Mapping[str, str], name: str) -> str:
    value = env.get(name, "").strip()
    if not value:
        raise LiveDemoConfigurationError(f"missing_required_environment:{name}")
    return value


def _public_url(value: str, *, name: str) -> str:
    parsed = urllib_parse.urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise LiveDemoConfigurationError(f"invalid_public_url:{name}")
    if parsed.hostname.lower() in _LOCAL_HOSTS:
        raise LiveDemoConfigurationError(f"localhost_forbidden:{name}")
    return value.rstrip("/")


def _remote_postgres_dsn(value: str, *, name: str) -> str:
    parsed = urllib_parse.urlparse(value)
    if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname:
        raise LiveDemoConfigurationError(f"invalid_postgres_dsn:{name}")
    if parsed.hostname.lower() in _LOCAL_HOSTS:
        raise LiveDemoConfigurationError(f"localhost_forbidden:{name}")
    return value


def _boolean(env: Mapping[str, str], name: str, *, default: bool = False) -> bool:
    raw = env.get(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise LiveDemoConfigurationError(f"invalid_boolean:{name}")


def _port(env: Mapping[str, str]) -> int:
    raw = (env.get("PORT") or env.get("ACADEMY_PORT") or "8000").strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise LiveDemoConfigurationError("invalid_port") from exc
    if not 1 <= value <= 65535:
        raise LiveDemoConfigurationError("invalid_port")
    return value


@dataclass(frozen=True, repr=False)
class LiveDemoConfig:
    mode: DemoMode
    internal_dsn: str
    scoped_dsn: str
    schema: str
    host: str
    port: int
    frontend_origins: tuple[str, ...]
    initialize_schema: bool
    actions_enabled: bool
    provider: DemoProvider | None = None
    provider_api_key: str | None = None
    tractian_base_url: str | None = None
    tractian_bearer_token: str | None = None
    organization_id: str = "demo-tractian"
    user_id: str = "demo-operator"
    role: str = "demo-operator"
    seed: str | None = None
    company_id: str = "company-e2e"
    action_analysis_id: str = "analysis-e2e"
    action_asset_id: str = "asset-e2e"

    def __repr__(self) -> str:
        return (
            "LiveDemoConfig("
            f"mode={self.mode!r}, schema={self.schema!r}, host={self.host!r}, port={self.port!r}, "
            f"frontend_origins={self.frontend_origins!r}, initialize_schema={self.initialize_schema!r}, "
            f"actions_enabled={self.actions_enabled!r}, provider={self.provider!r}, "
            "internal_dsn=<redacted>, scoped_dsn=<redacted>, provider_api_key=<redacted>, "
            f"tractian_base_url={self.tractian_base_url!r}, tractian_bearer_token=<redacted>)"
        )

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "LiveDemoConfig":
        env = os.environ if environ is None else environ
        mode_raw = _required(env, "DEMO_MODE").lower()
        if mode_raw not in {"live", "fallback"}:
            raise LiveDemoConfigurationError("invalid_demo_mode")
        mode: DemoMode = mode_raw  # type: ignore[assignment]

        internal_dsn = _remote_postgres_dsn(
            _required(env, "ACADEMY_POSTGRES_INTERNAL_DSN"),
            name="ACADEMY_POSTGRES_INTERNAL_DSN",
        )
        scoped_dsn = _remote_postgres_dsn(
            _required(env, "ACADEMY_POSTGRES_SCOPED_DSN"),
            name="ACADEMY_POSTGRES_SCOPED_DSN",
        )

        origins: list[str] = []
        for item in env.get("ACADEMY_FRONTEND_ORIGINS", "").split(","):
            normalized = item.strip()
            if normalized:
                origins.append(_public_url(normalized, name="ACADEMY_FRONTEND_ORIGINS"))

        provider: DemoProvider | None = None
        provider_api_key: str | None = None
        tractian_base_url: str | None = None
        tractian_bearer_token: str | None = None
        if mode == "live":
            provider_raw = _required(env, "LIVE_DEMO_PROVIDER").lower()
            if provider_raw not in {"google", "openai"}:
                raise LiveDemoConfigurationError("unsupported_live_demo_provider")
            provider = provider_raw  # type: ignore[assignment]
            provider_api_key = _required(
                env,
                "GOOGLE_API_KEY" if provider == "google" else "OPENAI_API_KEY",
            )
            tractian_base_url = _public_url(
                _required(env, "TRACTIAN_API_BASE_URL"),
                name="TRACTIAN_API_BASE_URL",
            )
            token = env.get("TRACTIAN_API_TOKEN", "").strip()
            tractian_bearer_token = token or None

        schema = env.get("ACADEMY_POSTGRES_SCHEMA", "academy_live_demo").strip()
        if not schema:
            raise LiveDemoConfigurationError("invalid_postgres_schema")

        return cls(
            mode=mode,
            internal_dsn=internal_dsn,
            scoped_dsn=scoped_dsn,
            schema=schema,
            host=env.get("ACADEMY_HOST", "0.0.0.0").strip() or "0.0.0.0",
            port=_port(env),
            frontend_origins=tuple(dict.fromkeys(origins)),
            initialize_schema=_boolean(env, "ACADEMY_INITIALIZE_SCHEMA", default=False),
            actions_enabled=_boolean(env, "DEMO_ACTIONS_ENABLED", default=False),
            provider=provider,
            provider_api_key=provider_api_key,
            tractian_base_url=tractian_base_url,
            tractian_bearer_token=tractian_bearer_token,
            organization_id=env.get("DEMO_ORGANIZATION_ID", "demo-tractian").strip()
            or "demo-tractian",
            user_id=env.get("DEMO_USER_ID", "demo-operator").strip() or "demo-operator",
            role=env.get("DEMO_ROLE", "demo-operator").strip() or "demo-operator",
            seed=(env.get("DEMO_SEED", "").strip() or None),
            company_id=env.get("DEMO_COMPANY_ID", "company-e2e").strip() or "company-e2e",
            action_analysis_id=env.get("DEMO_ACTION_ANALYSIS_ID", "analysis-e2e").strip()
            or "analysis-e2e",
            action_asset_id=env.get("DEMO_ACTION_ASSET_ID", "asset-e2e").strip()
            or "asset-e2e",
        )


class LiveDemoHttpTransport(RequestTransport):
    """One-shot real HTTP tool transport for the hosted demo.

    The bearer token is application-owned and never added to a model-visible request. Non-2xx HTTP
    responses are returned to the existing HarnessRunner so normal tool-error policy remains the
    single interpretation boundary. Network/serialization failures fail closed.
    """

    def __init__(
        self,
        *,
        base_url: str,
        bearer_token: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.base_url = _public_url(base_url, name="TRACTIAN_API_BASE_URL")
        self._bearer_token = bearer_token
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.timeout_seconds = float(timeout_seconds)

    def __repr__(self) -> str:
        return (
            f"LiveDemoHttpTransport(base_url={self.base_url!r}, "
            "bearer_token=<redacted>)"
        )

    def request(self, request: BoundRequest) -> TransportResponse:
        path = request.path if request.path.startswith("/") else f"/{request.path}"
        url = f"{self.base_url}{path}"
        if request.query:
            query = urllib_parse.urlencode(request.query, doseq=True)
            url = f"{url}?{query}"

        headers = {**request.headers, "Accept": "application/json"}
        if request.body is not None:
            headers.setdefault("Content-Type", "application/json")
        if self._bearer_token:
            headers["Authorization"] = f"Bearer {self._bearer_token}"
        payload = (
            None
            if request.body is None
            else json.dumps(
                request.body,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        )
        raw_request = urllib_request.Request(
            url,
            data=payload,
            headers=headers,
            method=request.method,
        )
        try:
            with urllib_request.urlopen(raw_request, timeout=self.timeout_seconds) as response:
                status_code = int(response.status)
                response_headers = dict(response.headers)
                raw_body = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            status_code = int(exc.code)
            response_headers = dict(exc.headers)
            raw_body = exc.read().decode("utf-8", errors="replace")
        except Exception as exc:
            raise RuntimeError("tractian_transport_failure") from exc

        try:
            body = json.loads(raw_body) if raw_body else None
        except ValueError:
            body = raw_body
        return TransportResponse(
            status_code=status_code,
            headers=response_headers,
            body=body,
        )


def _runtime_context(config: LiveDemoConfig, request: Request) -> AuthenticatedRuntimeContext:
    user_id = request.headers.get("x-demo-user", config.user_id)
    organization_id = request.headers.get("x-demo-organization", config.organization_id)
    permissions = DEFAULT_RUNTIME_PERMISSIONS | frozenset({"analytics:read:global"})
    return AuthenticatedRuntimeContext(
        organization_id=organization_id,
        identity_id=f"identity:{organization_id}:{user_id}",
        user_id=user_id,
        role=config.role,
        permissions=permissions,
        seed=config.seed,
    )


def _action_principal(config: LiveDemoConfig, *, user_id: str) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id=config.company_id,
        permissions=frozenset({Permission.ACTION_LOW}),
        resource_company_bindings=(
            ResourceCompanyBinding(
                resource_id=config.action_analysis_id,
                company_id=config.company_id,
            ),
            ResourceCompanyBinding(
                resource_id=config.action_asset_id,
                company_id=config.company_id,
            ),
        ),
    )


def _decision_source_factory(config: LiveDemoConfig):
    if config.mode == "fallback":
        return ProviderFreeScenarioDecisionSource

    assert config.provider is not None
    assert config.provider_api_key is not None
    registry = canonical_tool_registry()

    def factory():
        transport = UrllibProviderJsonTransport()
        if config.provider == "google":
            client = GoogleInteractionsDecisionClient(
                api_key=config.provider_api_key or "",
                transport=transport,
                timeout_seconds=45.0,
            )
        else:
            client = OpenAIResponsesDecisionClient(
                api_key=config.provider_api_key or "",
                transport=transport,
                timeout_seconds=45.0,
            )
        return ProviderDecisionSource(
            client=client,
            registry=registry,
            call_identity=ProviderCallIdentity(
                provider_id=client.provider_id,
                model_id=client.model_id,
                route_id=client.route_id,
                live_call=True,
            ),
        )

    return factory


def _transport_factory(config: LiveDemoConfig):
    if config.mode == "fallback":
        return ProviderFreeTransport

    assert config.tractian_base_url is not None

    def factory() -> RequestTransport:
        return LiveDemoHttpTransport(
            base_url=config.tractian_base_url or "",
            bearer_token=config.tractian_bearer_token,
        )

    return factory


def build_live_demo_product(config: LiveDemoConfig | None = None):
    active = LiveDemoConfig.from_env() if config is None else config
    app = create_postgres_action_capable_product_app(
        internal_dsn=active.internal_dsn,
        scoped_dsn=active.scoped_dsn,
        schema=active.schema,
        initialize_schema=active.initialize_schema,
        decision_source_factory=_decision_source_factory(active),
        transport_factory=_transport_factory(active),
        context_provider=lambda request: _runtime_context(active, request),
        authorization_resolver=lambda *, user_id: _action_principal(active, user_id=user_id),
        actions_enabled=active.actions_enabled,
        provider_calls_enabled=True,
        max_workers=8,
        heartbeat_interval_ms=250,
    )
    if active.frontend_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(active.frontend_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )
    app.state.demo_mode = active.mode
    app.state.live_demo_provider = active.provider
    app.state.live_demo_external_http = active.mode == "live"
    app.state.demo_actions_enabled = active.actions_enabled
    return app


def main() -> None:
    import uvicorn

    config = LiveDemoConfig.from_env()
    uvicorn.run(
        build_live_demo_product(config),
        host=config.host,
        port=config.port,
        log_level=os.environ.get("ACADEMY_LOG_LEVEL", "warning"),
    )


if __name__ == "__main__":
    main()
