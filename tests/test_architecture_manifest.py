from academy_tractian.architecture_manifest import architecture_manifest


def test_architecture_manifest_is_stable_connected_and_evidence_mappable() -> None:
    first = architecture_manifest(provider_selection_state="NO_SELECTION")
    second = architecture_manifest(provider_selection_state="NO_SELECTION")

    assert first == second
    assert len(first.manifest_sha256) == 64
    assert first.provider_selection_state == "NO_SELECTION"

    component_ids = {component.component_id for component in first.components}
    assert len(component_ids) == len(first.components)
    assert {edge.source for edge in first.edges} <= component_ids
    assert {edge.target for edge in first.edges} <= component_ids

    by_id = {component.component_id: component for component in first.components}
    assert by_id["harness_runner"].execution_role == "deterministic_boundary"
    assert "tool_call" in by_id["harness_runner"].activates_on_event_types
    assert by_id["production_evaluator"].execution_role == "post_runtime_only"
    assert by_id["production_evaluator"].activates_on_event_types == ()
    assert by_id["observability_projector"].trust_boundary == "raw-to-safe serialization boundary"
    assert by_id["operator_frontend"].layer == "browser"


def test_provider_state_is_part_of_manifest_identity() -> None:
    no_selection = architecture_manifest(provider_selection_state="NO_SELECTION")
    selected = architecture_manifest(provider_selection_state="SELECTED")

    assert no_selection.manifest_sha256 != selected.manifest_sha256
    assert selected.provider_selection_state == "SELECTED"
