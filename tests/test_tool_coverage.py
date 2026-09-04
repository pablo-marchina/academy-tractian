from academy_tractian.tool_coverage import build_tractian_tool_coverage


def test_tool_coverage_preserves_truthful_18_operation_claim_boundary() -> None:
    payload = build_tractian_tool_coverage()
    summary = payload["summary"]

    assert payload["schema_version"] == "tractian-tool-coverage-v1"
    assert payload["status"] == "PARTIAL_INTEGRATED_ROUTE_EVIDENCE"
    assert summary == {
        "normalized_operations": 18,
        "contract_registered": 18,
        "implementation_routes_present": 18,
        "integrated_route_execution_evidenced": 1,
        "integrated_route_execution_not_yet_evidenced": 17,
        "actions": 5,
        "reads": 13,
    }

    operations = payload["operations"]
    assert len(operations) == 18
    assert {item["tool_name"] for item in operations if item["integrated_route_execution_evidenced"]} == {
        "get_asset"
    }
    assert all(item["contract_registered"] for item in operations)
    assert all(item["implementation_route_present"] for item in operations)
