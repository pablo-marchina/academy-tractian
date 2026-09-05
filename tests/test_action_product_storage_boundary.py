from __future__ import annotations

import inspect

import pytest

from academy_tractian.action_product_api import create_action_capable_product_app
from academy_tractian.authenticated_postgres_product_api import (
    create_authenticated_postgres_action_capable_product_app,
)
from academy_tractian.postgres_product_api import create_postgres_action_capable_product_app


def test_action_product_local_storage_escape_hatch_is_fail_closed_by_default(tmp_path) -> None:
    with pytest.raises(ValueError, match="local file-backed fallbacks are test-only"):
        create_action_capable_product_app(
            db_path=tmp_path / "observability.duckdb",
            action_custody_path=tmp_path / "private-actions.duckdb",
            action_ledger_path=tmp_path / "action-ledger.duckdb",
            decision_source_factory=lambda: None,  # type: ignore[return-value]
            transport_factory=lambda: None,  # type: ignore[return-value]
            context_provider=lambda _request: None,  # type: ignore[return-value]
            authorization_resolver=lambda **_kwargs: None,  # type: ignore[return-value]
        )


def test_action_product_local_test_escape_hatch_cannot_become_default() -> None:
    parameter = inspect.signature(create_action_capable_product_app).parameters[
        "allow_local_test_storage"
    ]
    assert parameter.default is False


@pytest.mark.parametrize(
    "factory",
    (
        create_postgres_action_capable_product_app,
        create_authenticated_postgres_action_capable_product_app,
    ),
)
def test_promoted_postgres_product_entrypoints_expose_no_local_path(factory) -> None:
    parameters = inspect.signature(factory).parameters
    assert "db_path" not in parameters
    assert "action_custody_path" not in parameters
    assert "action_ledger_path" not in parameters
    assert "access_db_path" not in parameters
    assert "execution_db_path" not in parameters
    assert "allow_local_test_storage" not in parameters
