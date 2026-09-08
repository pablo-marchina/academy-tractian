from __future__ import annotations

from .provider_budget_gate import PostgresProviderBudgetGate
from .provider_clients import ProviderHttpRequest, ProviderHttpResponse, ProviderJsonTransport


class BudgetGatedProviderJsonTransport:
    """Block production provider I/O while a governed USD0 campaign owns the budget lease."""

    def __init__(self, *, gate: PostgresProviderBudgetGate, inner: ProviderJsonTransport) -> None:
        self.gate = gate
        self.inner = inner

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        self.gate.assert_provider_available()
        return self.inner.post_json(request)
