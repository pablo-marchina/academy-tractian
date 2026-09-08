from __future__ import annotations

from dataclasses import dataclass

import pytest

from research.e2.models import BoundRequest, Permission
from research.e2.transport import TransportResponse

from academy_tractian.action_safety import ResourceCompanyBinding
from academy_tractian.observability_store import ObservabilityStore
from academy_tractian.production_actions_v2 import (
    DuckDBActionIdempotencyLedger,
    PendingActionCustody,
    ProductionActionExecutor,
    ProductionActionPrincipal,
)
from academy_tractian.realtime_observability import DuckDBObservabilityEventSink
from academy_tractian.runtime import canonical_tool_registry


JUSTIFICATION = (
    "Operator reviewed the live evidence and explicitly approved this exact governed production action."
)


@dataclass(frozen=True)
class ActionCase:
    tool_name: str
    resource_argument: str
    resource_id: str
    permission: Permission
    method: str
    path: str
    body: dict[str, object]


ACTION_CASES = (
    ActionCase(
        tool_name="update_asset_config",
        resource_argument="asset_id",
        resource_id="asset-1",
        permission=Permission.ACTION_HIGH,
        method="PATCH",
        path="/assets/asset-1",
        body={"justification": JUSTIFICATION, "changes": {"criticality": "high"}},
    ),
    ActionCase(
        tool_name="reprocess_analysis",
        resource_argument="analysis_id",
        resource_id="analysis-1",
        permission=Permission.ACTION_LOW,
        method="POST",
        path="/analyses/analysis-1/reprocess",
        body={"justification": JUSTIFICATION},
    ),
    ActionCase(
        tool_name="request_specialist_analysis",
        resource_argument="analysis_id",
        resource_id="analysis-2",
        permission=Permission.ACTION_LOW,
        method="POST",
        path="/analyses/analysis-2/request-specialist",
        body={"justification": JUSTIFICATION},
    ),
    ActionCase(
        tool_name="request_retraining",
        resource_argument="model_id",
        resource_id="model-1",
        permission=Permission.ACTION_HIGH,
        method="POST",
        path="/models/model-1/request-retraining",
        body={"justification": JUSTIFICATION},
    ),
    ActionCase(
        tool_name="escalate_case",
        resource_argument="case_id",
        resource_id="case-1",
        permission=Permission.ESCALATE,
        method="POST",
        path="/cases/case-1/escalate",
        body={"justification": JUSTIFICATION},
    ),
)


class AcceptingTransport:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(
            status_code=202,
            headers={"content-type": "application/json"},
            body={"accepted": True},
        )


def _arguments(case: ActionCase) -> dict[str, object]:
    return {
        case.resource_argument: case.resource_id,
        "body": case.body,
    }


def _principal(case: ActionCase, *, company_id: str = "company-1") -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id="user-1",
        user_company_id="company-1",
        permissions=frozenset({case.permission}),
        resource_company_bindings=(
            ResourceCompanyBinding(resource_id=case.resource_id, company_id=company_id),
        ),
    )


def _resolver(principal: ProductionActionPrincipal):
    def resolve(*, user_id: str) -> ProductionActionPrincipal:
        if user_id != principal.user_id:
            raise PermissionError("unexpected_user")
        return principal

    return resolve


def _executor(tmp_path, case: ActionCase, *, principal: ProductionActionPrincipal, transport: AcceptingTransport, actions_enabled: bool = True):
    registry = canonical_tool_registry()
    custody = PendingActionCustody(tmp_path / f"{case.tool_name}-custody.duckdb")
    ledger = DuckDBActionIdempotencyLedger(tmp_path / f"{case.tool_name}-ledger.duckdb")
    observability = ObservabilityStore(tmp_path / f"{case.tool_name}-observability.duckdb")
    pending = custody.create_or_get(
        origin_raw_run_id=f"origin-{case.tool_name}",
        requester_user_id="user-1",
        tool=registry[case.tool_name],
        arguments=_arguments(case),
    )
    executor = ProductionActionExecutor(
        custody=custody,
        ledger=ledger,
        authorization_resolver=_resolver(principal),
        transport_factory=lambda: transport,
        observability_sink=DuckDBObservabilityEventSink(observability),
        actions_enabled=actions_enabled,
    )
    return custody, pending, executor


@pytest.mark.parametrize("case", ACTION_CASES, ids=lambda case: case.tool_name)
def test_every_canonical_action_reaches_transport_only_after_governed_confirmation(tmp_path, case: ActionCase) -> None:
    transport = AcceptingTransport()
    custody, pending, executor = _executor(
        tmp_path,
        case,
        principal=_principal(case),
        transport=transport,
    )

    execution_run_id, prepared = executor.prepare_confirmed(
        action_id=pending.action_id,
        identity_id="identity-1",
        requester_user_id="user-1",
    )
    trace = prepared.execute()

    assert len(transport.calls) == 1
    request = transport.calls[0]
    assert request.method == case.method
    assert request.path == case.path
    assert custody.get_safe(pending.action_id).state == "ACCEPTED"
    assert custody.get_safe(pending.action_id).execution_run_id == execution_run_id
    final = [event for event in trace.events if event.event_type == "final_response"][-1]
    assert final.result["reason_code"] == "ACTION_ACCEPTED"


@pytest.mark.parametrize("case", ACTION_CASES, ids=lambda case: case.tool_name)
def test_every_canonical_action_fails_closed_without_its_server_permission(tmp_path, case: ActionCase) -> None:
    transport = AcceptingTransport()
    principal = _principal(case).model_copy(update={"permissions": frozenset()})
    custody, pending, executor = _executor(
        tmp_path,
        case,
        principal=principal,
        transport=transport,
    )

    _, prepared = executor.prepare_confirmed(
        action_id=pending.action_id,
        identity_id="identity-1",
        requester_user_id="user-1",
    )
    trace = prepared.execute()

    assert transport.calls == []
    assert custody.get_safe(pending.action_id).state == "BLOCKED"
    check = [event for event in trace.events if event.event_type == "policy_check"][-1]
    assert check.metadata["violation"] == "PERMISSION_DENIED"


def test_high_impact_action_fails_closed_for_cross_company_resource(tmp_path) -> None:
    case = ACTION_CASES[0]
    transport = AcceptingTransport()
    custody, pending, executor = _executor(
        tmp_path,
        case,
        principal=_principal(case, company_id="company-2"),
        transport=transport,
    )

    _, prepared = executor.prepare_confirmed(
        action_id=pending.action_id,
        identity_id="identity-1",
        requester_user_id="user-1",
    )
    prepared.execute()

    assert transport.calls == []
    assert custody.get_safe(pending.action_id).state == "BLOCKED"


def test_global_kill_switch_blocks_before_execution_state_transition(tmp_path) -> None:
    case = ACTION_CASES[3]
    transport = AcceptingTransport()
    custody, pending, executor = _executor(
        tmp_path,
        case,
        principal=_principal(case),
        transport=transport,
        actions_enabled=False,
    )

    with pytest.raises(RuntimeError, match="action_kill_switch_engaged"):
        executor.prepare_confirmed(
            action_id=pending.action_id,
            identity_id="identity-1",
            requester_user_id="user-1",
        )

    assert transport.calls == []
    assert custody.get_safe(pending.action_id).state == "PENDING_CONFIRMATION"
