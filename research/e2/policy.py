from __future__ import annotations
from dataclasses import dataclass
from .models import Permission, ToolSpec

@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    code: str
    reason: str

class ResourcePolicy:
    """Deterministic policy layer. It never infers permissions from model text."""
    def __init__(self, *, user_permissions: set[Permission], user_company_id: str, resource_company_lookup: dict[str, str]):
        self.user_permissions = user_permissions
        self.user_company_id = user_company_id
        self.resource_company_lookup = resource_company_lookup

    def check(self, tool: ToolSpec, arguments: dict[str, object]) -> PolicyDecision:
        for permission in tool.required_permissions:
            if permission not in self.user_permissions:
                return PolicyDecision(False, "PERMISSION_DENIED", f"missing permission {permission.value}")
        if tool.target_scope in {"resource", "company_resource"}:
            resource_id = next((v for k, v in arguments.items() if k.endswith("_id") and k != "point_id"), None)
            if isinstance(resource_id, str) and resource_id in self.resource_company_lookup:
                if self.resource_company_lookup[resource_id] != self.user_company_id:
                    return PolicyDecision(False, "RESOURCE_SCOPE_DENIED", "target resource belongs to another company")
        return PolicyDecision(True, "ALLOWED", "policy checks passed")
