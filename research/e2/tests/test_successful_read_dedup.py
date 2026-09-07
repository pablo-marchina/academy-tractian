from __future__ import annotations

from research.e2.models import ExecutionBinding, ToolKind, ToolParameter, ToolSpec
from research.e2.runner import HarnessRunner
from research.e2.transport import TransportResponse

from academy_tractian.realtime_observability import ObservableHarnessRunner


class RecordingTransport:
    def __init__(self, status_code: int = 200) -> None:
        self.status_code = status_code
        self.calls = []

    def request(self, request):
        self.calls.append(request)
        return TransportResponse(
            status_code=self.status_code,
            headers={"content-type": "application/json"},
            body={"ok": self.status_code < 300},
        )


class NullPublisher:
    def publish_trace_state(self, trace, *, canonical_append_perf=None) -> None:
        del trace, canonical_append_perf


def _registry() -> dict[str, ToolSpec]:
    parameter = ToolParameter(
        name="asset_id",
        location="path",
        required=True,
        parameter_schema={"type": "string", "minLength": 1},
    )
    return {
        "read_asset": ToolSpec(
            name="read_asset",
            operation_id="readAsset",
            method="GET",
            path_template="/assets/{asset_id}",
            kind=ToolKind.READ,
            parameters=(parameter,),
        ),
        "touch_asset": ToolSpec(
            name="touch_asset",
            operation_id="touchAsset",
            method="POST",
            path_template="/assets/{asset_id}/touch",
            kind=ToolKind.ACTION,
            parameters=(parameter,),
        ),
    }


def _historical_runner(transport):
    return HarnessRunner(
        run_id="historical",
        scenario_id="historical",
        config_hash="a" * 64,
        registry=_registry(),
        binding=ExecutionBinding(identity_id="identity", user_id="user"),
        transport=transport,
        strict_arguments=True,
    )


def _production_runner(transport):
    return ObservableHarnessRunner(
        observability_publisher=NullPublisher(),
        run_id="observable-dedupe",
        scenario_id="observable-dedupe",
        config_hash="b" * 64,
        registry=_registry(),
        binding=ExecutionBinding(identity_id="identity", user_id="user"),
        transport=transport,
        strict_arguments=True,
    )


def test_frozen_historical_harness_still_allows_duplicate_reads() -> None:
    transport = RecordingTransport()
    runner = _historical_runner(transport)
    assert runner.execute_tool("read_asset", {"asset_id": "asset-a"}).executed
    assert runner.execute_tool("read_asset", {"asset_id": "asset-a"}).executed
    assert len(transport.calls) == 2


def test_production_wrapper_blocks_duplicate_successful_read_before_transport() -> None:
    transport = RecordingTransport()
    runner = _production_runner(transport)
    first = runner.execute_tool("read_asset", {"asset_id": "asset-a"})
    second = runner.execute_tool("read_asset", {"asset_id": "asset-a"})
    assert first.executed
    assert not second.executed
    assert second.blocked_code == "DUPLICATE_SUCCESSFUL_READ"
    assert len(transport.calls) == 1


def test_production_wrapper_allows_same_read_tool_with_different_arguments() -> None:
    transport = RecordingTransport()
    runner = _production_runner(transport)
    assert runner.execute_tool("read_asset", {"asset_id": "asset-a"}).executed
    assert runner.execute_tool("read_asset", {"asset_id": "asset-b"}).executed
    assert len(transport.calls) == 2


def test_failed_read_is_not_recorded_as_successful_duplicate() -> None:
    transport = RecordingTransport(status_code=503)
    runner = _production_runner(transport)
    assert runner.execute_tool("read_asset", {"asset_id": "asset-a"}).executed
    assert runner.execute_tool("read_asset", {"asset_id": "asset-a"}).executed
    assert len(transport.calls) == 2


def test_action_calls_are_never_intercepted_by_read_deduplication() -> None:
    transport = RecordingTransport()
    runner = _production_runner(transport)
    assert runner.execute_tool("touch_asset", {"asset_id": "asset-a"}).executed
    assert runner.execute_tool("touch_asset", {"asset_id": "asset-a"}).executed
    assert len(transport.calls) == 2


def test_duplicate_read_trace_records_proposal_and_contained_policy_check_only() -> None:
    transport = RecordingTransport()
    runner = _production_runner(transport)
    assert runner.execute_tool("read_asset", {"asset_id": "asset-a"}).executed
    before = len(runner.trace.events)
    duplicate = runner.execute_tool("read_asset", {"asset_id": "asset-a"})
    assert not duplicate.executed
    new_events = runner.trace.events[before:]
    assert [event.event_type for event in new_events] == ["tool_proposal", "policy_check"]
    assert new_events[-1].metadata["violation"] == "DUPLICATE_SUCCESSFUL_READ"
    assert new_events[-1].metadata["contained"] is True
    assert len(transport.calls) == 1
