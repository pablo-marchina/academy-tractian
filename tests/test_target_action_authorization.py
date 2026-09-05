from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Mapping

import pytest

from research.e2.models import Permission, ToolSpec
from research.e2.policy import PolicyDecision
from research.e2.transport import TransportResponse

from academy_tractian.action_safety import ResourceCompanyBinding, action_fingerprint
from academy_tractian.production_actions_v2 import PendingActionSafe, ProductionActionPrincipal
from academy_tractian.runtime import canonical_tool_registry
from academy_tractian.target_action_authorization import (
    TargetAwarePendingActionCapturePolicy,
    TargetAwareProductionActionExecutor,
    target_resolver_from_legacy,
)


class FakeCustody:
    def __init__(self) -> None:
        self.created: list[dict[str, Any]] = []
        self.private: dict[str, Any] = {}
        self.transitions: list[tuple[str, str]] = []

    def create_or_get(self, *, origin_raw_run_id, requester_user_id, tool, arguments):
        fingerprint = action_fingerprint(tool, arguments)
        safe = PendingActionSafe(
            action_id="act_1",
            origin_run_id="run_1",
            tool_name=tool.name,
            action_fingerprint=fingerprint,
            impact=tool.impact.value,
            required_permissions=tuple(permission.value for permission in tool.required_permissions),
            state="PENDING_CONFIRMATION",
        )
        self.created.append(
            {
                "origin_raw_run_id": origin_raw_run_id,
                "requester_user_id": requester_user_id,
                "tool": tool.name,
                "arguments": arguments,
            }
        )
        self.private[safe.action_id] = SimpleNamespace(
            safe=safe,
            arguments=dict(arguments),
            idempotency_key="idem-server-owned",
        )
        return safe

    def get_private_for_requester(self, *, action_id, requester_user_id):
        del requester_user_id
        if action_id not in self.private:
            raise KeyError(action_id)
        return self.private[action_id]

    def transition(self, *, action_id, expected_states, new_state, execution_run_id=None):
        item = self.private[action_id]
        if item.safe.state not in expected_states:
            return False
        item.safe = item.safe.model_copy(
            update={"state": new_state, "execution_run_id": execution_run_id or item.safe.execution_run_id}
        )
        self.transitions.append((action_id, new_state))
        return True


class FakeLedger:
    def claim(self, **_kwargs):
        return True

    def mark(self, **_kwargs):
        return None


class NoopTransport:
    def request(self, _request):
        return TransportResponse(status_code=200, headers={}, body={"accepted": True})


class NoopSink:
    def publish(self, _event):
        return None


def _principal(*, company="comp_a", binding_company="comp_a", permissions=None):
    return ProductionActionPrincipal(
        user_id="usr_a",
        user_company_id=company,
        permissions=frozenset(permissions or {Permission.ACTION_HIGH}),
        resource_company_bindings=(
            ResourceCompanyBinding(resource_id="asset_a", company_id=binding_company),
        ),
    )


def _asset_args() -> dict[str, Any]:
    return {
        "asset_id": "asset_a",
        "body": {"justification": "Authorized maintenance configuration change"},
    }


def test_exact_target_resolver_is_lazy_and_only_called_for_action_proposal() -> None:
    calls: list[tuple[str, str]] = []
    custody = FakeCustody()

    def resolver(*, user_id: str, tool: ToolSpec, arguments: Mapping[str, Any]):
        calls.append((user_id, tool.name))
        assert arguments["asset_id"] == "asset_a"
        return _principal()

    policy = TargetAwarePendingActionCapturePolicy(
        user_id="usr_a",
        target_authorization_resolver=resolver,
        origin_raw_run_id="raw-run",
        custody=custody,
    )

    read = policy.check(canonical_tool_registry()["get_asset"], {"asset_id": "asset_a"})
    action = policy.check(canonical_tool_registry()["update_asset_config"], _asset_args())

    assert read == PolicyDecision(allowed=True, code="ALLOWED", reason="read tool outside action capture")
    assert calls == [("usr_a", "update_asset_config")]
    assert action.code == "CONFIRMATION_REQUIRED"
    assert len(custody.created) == 1


def test_cross_tenant_exact_target_is_blocked_before_pending_action_exists() -> None:
    custody = FakeCustody()

    def resolver(**_kwargs):
        return _principal(binding_company="comp_b")

    policy = TargetAwarePendingActionCapturePolicy(
        user_id="usr_a",
        target_authorization_resolver=resolver,
        origin_raw_run_id="raw-run",
        custody=custody,
    )
    decision = policy.check(canonical_tool_registry()["update_asset_config"], _asset_args())

    assert decision.code == "RESOURCE_SCOPE_DENIED"
    assert custody.created == []


def test_permission_revocation_blocks_proposal() -> None:
    custody = FakeCustody()

    def resolver(**_kwargs):
        return _principal(permissions={Permission.READ})

    policy = TargetAwarePendingActionCapturePolicy(
        user_id="usr_a",
        target_authorization_resolver=resolver,
        origin_raw_run_id="raw-run",
        custody=custody,
    )
    decision = policy.check(canonical_tool_registry()["update_asset_config"], _asset_args())

    assert decision.code == "PERMISSION_DENIED"
    assert custody.created == []


def test_confirmation_revalidates_exact_target_before_transitioning_to_executing() -> None:
    custody = FakeCustody()
    tool = canonical_tool_registry()["update_asset_config"]
    custody.create_or_get(
        origin_raw_run_id="raw-run",
        requester_user_id="usr_a",
        tool=tool,
        arguments=_asset_args(),
    )
    calls = 0

    def resolver(**_kwargs):
        nonlocal calls
        calls += 1
        return _principal()

    executor = TargetAwareProductionActionExecutor(
        custody=custody,
        ledger=FakeLedger(),
        target_authorization_resolver=resolver,
        transport_factory=NoopTransport,
        observability_sink=NoopSink(),
        actions_enabled=True,
    )

    execution_run_id, _prepared = executor.prepare_confirmed(
        action_id="act_1",
        identity_id="identity_a",
        requester_user_id="usr_a",
    )

    assert calls == 1
    assert execution_run_id
    assert custody.transitions[-1] == ("act_1", "EXECUTING")


def test_toctou_ownership_change_is_denied_before_confirmation_is_accepted() -> None:
    custody = FakeCustody()
    tool = canonical_tool_registry()["update_asset_config"]
    custody.create_or_get(
        origin_raw_run_id="raw-run",
        requester_user_id="usr_a",
        tool=tool,
        arguments=_asset_args(),
    )

    def resolver(**_kwargs):
        return _principal(binding_company="comp_b")

    executor = TargetAwareProductionActionExecutor(
        custody=custody,
        ledger=FakeLedger(),
        target_authorization_resolver=resolver,
        transport_factory=NoopTransport,
        observability_sink=NoopSink(),
        actions_enabled=True,
    )

    with pytest.raises(RuntimeError, match="action_authorization_denied:RESOURCE_SCOPE_DENIED"):
        executor.prepare_confirmed(
            action_id="act_1",
            identity_id="identity_a",
            requester_user_id="usr_a",
        )

    assert custody.private["act_1"].safe.state == "PENDING_CONFIRMATION"
    assert custody.transitions == []


def test_toctou_permission_revocation_is_denied_before_confirmation_is_accepted() -> None:
    custody = FakeCustody()
    tool = canonical_tool_registry()["update_asset_config"]
    custody.create_or_get(
        origin_raw_run_id="raw-run",
        requester_user_id="usr_a",
        tool=tool,
        arguments=_asset_args(),
    )

    def resolver(**_kwargs):
        return _principal(permissions={Permission.READ})

    executor = TargetAwareProductionActionExecutor(
        custody=custody,
        ledger=FakeLedger(),
        target_authorization_resolver=resolver,
        transport_factory=NoopTransport,
        observability_sink=NoopSink(),
        actions_enabled=True,
    )

    with pytest.raises(RuntimeError, match="action_authorization_denied:PERMISSION_DENIED"):
        executor.prepare_confirmed(
            action_id="act_1",
            identity_id="identity_a",
            requester_user_id="usr_a",
        )

    assert custody.private["act_1"].safe.state == "PENDING_CONFIRMATION"


def test_target_resolver_discovery_is_opt_in_and_backward_compatible() -> None:
    def legacy(*, user_id: str):
        return ProductionActionPrincipal(user_id=user_id, user_company_id="comp_a")

    class TargetCapable:
        def __call__(self, *, user_id: str):
            return ProductionActionPrincipal(user_id=user_id, user_company_id="comp_a")

        def resolve_target(self, **_kwargs):
            return _principal()

    assert target_resolver_from_legacy(legacy) is None
    assert callable(target_resolver_from_legacy(TargetCapable()))
