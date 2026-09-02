import json

from fastapi.testclient import TestClient

from academy_tractian.observability_api import create_observability_app


def test_architecture_endpoint_is_safe_versioned_and_provider_explicit(tmp_path) -> None:
    app = create_observability_app(
        db_path=tmp_path / "architecture.duckdb",
        provider_selection_state="NO_SELECTION",
    )
    client = TestClient(app)

    response = client.get("/api/architecture")
    assert response.status_code == 200
    payload = response.json()

    assert payload["schema_version"] == "architecture-manifest-v1"
    assert payload["architecture_version"] == "tractian-production-architecture-v1"
    assert payload["provider_selection_state"] == "NO_SELECTION"
    assert len(payload["manifest_sha256"]) == 64

    component_ids = {item["component_id"] for item in payload["components"]}
    assert "operator_frontend" in component_ids
    assert "production_evaluator" in component_ids
    assert "observability_api" in component_ids

    serialized = json.dumps(payload, sort_keys=True)
    for forbidden in (
        "identity_id",
        "user_id",
        "seed_ref",
        "authorization",
        "credential",
        "raw provider response",
        "chain-of-thought",
    ):
        assert forbidden not in serialized.lower()
