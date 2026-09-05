from __future__ import annotations

import inspect

import pytest

from academy_tractian.action_product_api import create_action_capable_product_app
from academy_tractian.authenticated_postgres_product_api import (
    create_authenticated_postgres_action_capable_product_app,
)
from academy_tractian.observability_api import create_observability_app
from academy_tractian.postgres_product_api import create_postgres_action_capable_product_app
from academy_tractian.product_api import create_product_app


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


def test_generic_product_factory_requires_explicit_durable_stores() -> None:
    parameters = inspect.signature(create_product_app).parameters
    for required_store in ("observability_store", "run_access_store", "execution_store"):
        assert parameters[required_store].default is inspect.Parameter.empty
    for forbidden_path in ("db_path", "access_db_path", "execution_db_path"):
        assert forbidden_path not in parameters


def test_observability_api_has_no_implicit_local_default() -> None:
    parameters = inspect.signature(create_observability_app).parameters
    assert parameters["db_path"].default is None
    assert parameters["observability_store"].default is None
    with pytest.raises(ValueError, match="observability_store is required"):
        create_observability_app()


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
