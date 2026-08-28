from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.models import Permission, ToolKind, ToolSpec
from research.e2.policy import PolicyDecision, ResourcePolicy
from research.e2.validation import validate_arguments


ACTION_SAFETY_POLICY_VERSION = "prod-action-safety-v1"
PRODUCTION_RUNTIME_CONTROLLED_ACTION_FIELDS = frozenset(
    {
        "actions_enabled",
        "action_confirmation",
        "confirmed_action",
        "idempotency_key",
        "requester_confirmation",
        "resource_company_lookup",
        "user_company_id",
        "user_permissions",
    }
)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ResourceCompanyBinding(_FrozenModel):
    resource_id: str = Field(min_length=1)
    company_id: str = Field(min_length=1)


class ActionIdempotencyBinding(_FrozenModel):
    action_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    idempotency_key: str = Field(min_length=1)


class ProductionActionAuthorizationContext(_FrozenModel):
    """Runtime-owned action authorization state.

    None of these fields belongs in ControllerContext or model-supplied tool arguments.
    The production runtime currently constructs this context with execution disabled.
    """

    schema_version: Literal["prod-action-auth-context-v1"] = "prod-action-auth-context-v1"
    execution_enabled: bool = False
    user_permissions: frozenset[Permission] = frozenset()
    user_company_id: str = Field(min_length=1)
    resource_company_bindings: tuple[ResourceCompanyBinding, ...] = ()
    confirmed_action_fingerprints: frozenset[str] = frozenset()
    idempotency_bindings: tuple[ActionIdempotencyBinding, ...] = ()
    consumed_idempotency_keys: frozenset[str] = frozenset()

    @model_validator(mode="after")
    def validate_unique_runtime_bindings(self) -> "ProductionActionAuthorizationContext":
        resource_ids = [binding.resource_id for binding in self.resource_company_bindings]
        if len(resource_ids) != len(set(resource_ids)):
            raise ValueError("resource_company_bindings must contain unique resource ids")

        fingerprints = [binding.action_fingerprint for binding in self.idempotency_bindings]
        if len(fingerprints) != len(set(fingerprints)):
            raise ValueError("idempotency_bindings must contain unique action fingerprints")

        keys = [binding.idempotency_key for binding in self.idempotency_bindings]
        if len(keys) != len(set(keys)):
            raise ValueError("idempotency keys must not be shared across action fingerprints")
        return self


class ActionSafetyCheck(_FrozenModel):
    name: str = Field(min_length=1)
    passed: bool
    code: str = Field(min_length=1)


class ActionSafetyDecision(_FrozenModel):
    schema_version: Literal["prod-action-safety-decision-v1"] = "prod-action-safety-decision-v1"
    policy_version: Literal["prod-action-safety-v1"] = ACTION_SAFETY_POLICY_VERSION
    tool_name: str
    action_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    allowed: bool
    code: str
    failed_codes: tuple[str, ...]
    checks: tuple[ActionSafetyCheck, ...]
    idempotency_key_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    decision_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def _canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def action_fingerprint(tool: ToolSpec, arguments: dict[str, Any]) -> str:
    """Bind confirmation/idempotency to the exact proposed action without exposing its body."""

    return _canonical_sha256(
        {
            "operation_id": tool.operation_id,
            "method": tool.method,
            "path_template": tool.path_template,
            "tool_name": tool.name,
            "arguments": arguments,
        }
    )


def _target_resource_id(tool: ToolSpec, arguments: dict[str, Any]) -> str | None:
    path_ids = [
        parameter.name
        for parameter in tool.parameters
        if parameter.location == "path" and parameter.name.endswith("_id")
    ]
    if len(path_ids) != 1:
        return None
    value = arguments.get(path_ids[0])
    return value if isinstance(value, str) and value else None


def _check(name: str, passed: bool, code: str) -> ActionSafetyCheck:
    return ActionSafetyCheck(name=name, passed=passed, code=code)


_REASON = {
    "ALLOWED": "all production action-safety checks passed",
    "PERMISSION_DENIED": "required action permission is not runtime-authorized",
    "ACTIONS_DISABLED": "production action execution remains globally disabled",
    "RUNTIME_CONTEXT_FIELD_PROPOSED": "runtime-owned authorization state was supplied as model/tool arguments",
    "ARGUMENT_INVALID": "action arguments fail the canonical ToolSpec contract",
    "RESOURCE_SCOPE_UNKNOWN": "target resource has no runtime-owned company binding",
    "RESOURCE_SCOPE_DENIED": "target resource belongs to a different company",
    "INVALID_JUSTIFICATION": "action justification does not satisfy the canonical minimum",
    "CONFIRMATION_REQUIRED": "exact action fingerprint has no requester confirmation",
    "IDEMPOTENCY_KEY_REQUIRED": "exact action fingerprint has no runtime-owned idempotency key",
    "DUPLICATE_ACTION": "runtime-owned idempotency key has already been consumed",
}


class ProductionActionSafetyPolicy(ResourcePolicy):
    """Deterministic production B2 action gate.

    The policy can be dry-run with an explicitly enabled context, but ProductionRuntime keeps
    execution disabled. It never infers authorization from model text and never accepts
    confirmation/idempotency as tool arguments.
    """

    def __init__(self, *, context: ProductionActionAuthorizationContext) -> None:
        self.context = context
        self._resource_company_lookup = {
            binding.resource_id: binding.company_id
            for binding in context.resource_company_bindings
        }
        self._idempotency_lookup = {
            binding.action_fingerprint: binding.idempotency_key
            for binding in context.idempotency_bindings
        }

    def evaluate(self, tool: ToolSpec, arguments: dict[str, Any]) -> ActionSafetyDecision:
        if tool.kind is not ToolKind.ACTION:
            raise ValueError("ProductionActionSafetyPolicy only evaluates action ToolSpecs")

        fingerprint = action_fingerprint(tool, arguments)
        proposed_runtime_fields = sorted(
            set(arguments) & PRODUCTION_RUNTIME_CONTROLLED_ACTION_FIELDS
        )

        validation_issues = validate_arguments(tool, arguments)
        justification_issue_codes = {"INVALID_BODY", "INVALID_JUSTIFICATION"}
        non_justification_issues = [
            issue for issue in validation_issues if issue.code not in justification_issue_codes
        ]
        justification_issues = [
            issue for issue in validation_issues if issue.code in justification_issue_codes
        ]

        required_permissions_ok = all(
            permission in self.context.user_permissions
            for permission in tool.required_permissions
        )

        resource_id = _target_resource_id(tool, arguments)
        if tool.target_scope in {"resource", "company_resource"}:
            scope_known = (
                resource_id is not None
                and resource_id in self._resource_company_lookup
            )
            scope_same_company = (
                not scope_known
                or self._resource_company_lookup[resource_id] == self.context.user_company_id
            )
        else:
            scope_known = True
            scope_same_company = True

        confirmed = fingerprint in self.context.confirmed_action_fingerprints
        idempotency_key = self._idempotency_lookup.get(fingerprint)
        idempotency_present = bool(idempotency_key)
        idempotency_unused = (
            not idempotency_present
            or idempotency_key not in self.context.consumed_idempotency_keys
        )

        # Permission remains first to preserve the existing read-only production trace contract:
        # today ProductionRuntime grants zero permissions. The independent execution-switch
        # check still guarantees that granting a permission cannot enable execution by itself.
        checks = (
            _check("required_permissions", required_permissions_ok, "PERMISSION_DENIED"),
            _check("global_execution_switch", self.context.execution_enabled, "ACTIONS_DISABLED"),
            _check("runtime_context_isolation", not proposed_runtime_fields, "RUNTIME_CONTEXT_FIELD_PROPOSED"),
            _check("canonical_argument_contract", not non_justification_issues, "ARGUMENT_INVALID"),
            _check("resource_scope_known", scope_known, "RESOURCE_SCOPE_UNKNOWN"),
            _check("resource_scope_same_company", scope_same_company, "RESOURCE_SCOPE_DENIED"),
            _check("justification", not justification_issues, "INVALID_JUSTIFICATION"),
            _check("requester_confirmation", confirmed, "CONFIRMATION_REQUIRED"),
            _check("idempotency_key_present", idempotency_present, "IDEMPOTENCY_KEY_REQUIRED"),
            _check("idempotency_key_unused", idempotency_unused, "DUPLICATE_ACTION"),
        )
        failed_codes = tuple(check.code for check in checks if not check.passed)
        allowed = not failed_codes
        code = "ALLOWED" if allowed else failed_codes[0]
        idempotency_key_sha256 = (
            None if idempotency_key is None else sha256(idempotency_key.encode("utf-8")).hexdigest()
        )
        decision_payload = {
            "policy_version": ACTION_SAFETY_POLICY_VERSION,
            "tool_name": tool.name,
            "action_fingerprint": fingerprint,
            "allowed": allowed,
            "code": code,
            "failed_codes": failed_codes,
            "checks": [check.model_dump(mode="json") for check in checks],
            "idempotency_key_sha256": idempotency_key_sha256,
        }
        return ActionSafetyDecision(
            tool_name=tool.name,
            action_fingerprint=fingerprint,
            allowed=allowed,
            code=code,
            failed_codes=failed_codes,
            checks=checks,
            idempotency_key_sha256=idempotency_key_sha256,
            decision_sha256=_canonical_sha256(decision_payload),
        )

    def check(self, tool: ToolSpec, arguments: dict[str, object]) -> PolicyDecision:
        decision = self.evaluate(tool, dict(arguments))
        return PolicyDecision(
            allowed=decision.allowed,
            code=decision.code,
            reason=f"{ACTION_SAFETY_POLICY_VERSION}: {_REASON[decision.code]}",
        )
