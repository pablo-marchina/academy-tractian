from __future__ import annotations

from time import perf_counter

from .production_controller import ProductionAgentController
from .realtime_observability import FailIsolatedObservabilityPublisher


class ProductionObservableAgentController(ProductionAgentController):
    """Production controller hardening with the existing safe realtime publisher."""

    def __init__(
        self,
        *,
        observability_publisher: FailIsolatedObservabilityPublisher,
        **kwargs,
    ) -> None:
        self.observability_publisher = observability_publisher
        super().__init__(**kwargs)

    def _emit(self, event_type: str, **kwargs) -> None:
        super()._emit(event_type, **kwargs)
        canonical_append_perf = perf_counter()
        self.observability_publisher.publish_trace_state(
            self.runner.trace,
            canonical_append_perf=canonical_append_perf,
        )
