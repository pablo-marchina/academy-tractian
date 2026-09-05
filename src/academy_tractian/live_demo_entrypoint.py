from __future__ import annotations

import os

from .live_demo_postgres_bootstrap import ensure_live_demo_scoped_role
from .live_demo_product import LiveDemoConfig, LiveDemoConfigurationError, build_live_demo_product


def _enabled(value: str | None, *, name: str) -> bool:
    if value is None:
        return False
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off", ""}:
        return False
    raise LiveDemoConfigurationError(f"invalid_boolean:{name}")


def main() -> None:
    import uvicorn

    config = LiveDemoConfig.from_env()
    if _enabled(
        os.environ.get("ACADEMY_BOOTSTRAP_SCOPED_ROLE"),
        name="ACADEMY_BOOTSTRAP_SCOPED_ROLE",
    ):
        ensure_live_demo_scoped_role(
            internal_dsn=config.internal_dsn,
            scoped_dsn=config.scoped_dsn,
        )

    uvicorn.run(
        build_live_demo_product(config),
        host=config.host,
        port=config.port,
        log_level=os.environ.get("ACADEMY_LOG_LEVEL", "warning"),
    )


if __name__ == "__main__":
    main()
