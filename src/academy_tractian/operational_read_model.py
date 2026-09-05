from __future__ import annotations

from collections import Counter, defaultdict
from math import ceil
from statistics import mean
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .observability_contract import OBSERVABILITY_SCHEMA_VERSION, ObservabilityStoreContract
from .provider_experiments import provider_experiment_registry


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AnalyticsFilter(_FrozenModel):
    field: str = Field(min_length=1, max_length=64)
    operator: Literal["eq", "ne", "in"]
    value: str | int | bool | list[str] | list[int] | list[bool]


class AnalyticsQuery(_FrozenModel):
    dataset: Literal["runs", "events", "evaluations"]
    run_id: str | None = Field(default=None, min_length=1, max_length=128)
    dimensions: tuple[str, ...] = Field(default=(), max_length=2)
    measure: str
    filters: tuple[AnalyticsFilter, ...] = Field(default=(), max_length=8)
    chart_type: Literal["table", "bar", "line", "heatmap", "histogram"] = "table"
    limit: int = Field(default=100, ge=1, le=500)

    @model_validator(mode="after")
    def validate_shape(self) -> "AnalyticsQuery":
        if self.chart_type == "heatmap" and len(self.dimensions) != 2:
            raise ValueError("heatmap requires exactly two dimensions")
        if self.chart_type in {"bar", "line"} and len(self.dimensions) != 1:
            raise ValueError(f"{self.chart_type} requires exactly one dimension")
        if self.chart_type == "histogram" and self.dimensions:
            raise ValueError("histogram does not accept dimensions")
        return self


_RUN_DIMENSIONS = {
    "scenario_id",
    "config_hash",
    "terminal_decision",
    "terminal_response_mode",
    "completed",
}
_EVENT_DIMENSIONS = {
    "event_type",
    "origin",
    "tool_name",
    "decision_kind",
    "provider_id",
    "model_id",
    "outcome",
    "failure_code",
    "policy_stage",
    "policy_allowed",
    "policy_contained",
    "policy_violation",
    "response_mode",
}
_EVALUATION_DIMENSIONS = {"check_name", "passed", "blocking", "blocking_pass"}

_MEASURES: dict[str, set[str]] = {
    "runs": {
        "count",
        "completed_rate",
        "avg_model_calls",
        "avg_tool_calls",
        "avg_policy_blocks",
        "avg_errors",
    },
    "events": {
        "count",
        "avg_latency_ms",
        "p50_latency_ms",
        "p95_latency_ms",
        "error_rate",
        "policy_block_rate",
        "latency_ms_distribution",
    },
    "evaluations": {"count", "pass_rate", "blocking_pass_rate"},
}

_DIMENSIONS = {
    "runs": _RUN_DIMENSIONS,
    "events": _EVENT_DIMENSIONS,
    "evaluations": _EVALUATION_DIMENSIONS,
}

_HISTOGRAM_MEASURES = {"latency_ms_distribution"}


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = percentile * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    fraction = rank - low
    return ordered[low] + (ordered[high] - ordered[low]) * fraction


def _rate(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def _scalar_key(value: Any) -> str | int | bool | None:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    return str(value)


def _filter_matches(row: dict[str, Any], item: AnalyticsFilter) -> bool:
    current = row.get(item.field)
    if item.operator == "eq":
        return current == item.value
    if item.operator == "ne":
        return current != item.value
    values = item.value if isinstance(item.value, list) else [item.value]
    return current in values


def _aggregate_measure(dataset: str, rows: list[dict[str, Any]], measure: str) -> float | int | None:
    if measure == "count":
        return len(rows)
    if dataset == "runs":
        if measure == "completed_rate":
            return _rate(sum(bool(row["completed"]) for row in rows), len(rows))
        column = {
            "avg_model_calls": "model_calls",
            "avg_tool_calls": "tool_calls",
            "avg_policy_blocks": "policy_blocks",
            "avg_errors": "errors",
        }.get(measure)
        if column:
            return 0.0 if not rows else mean(float(row[column]) for row in rows)
    if dataset == "events":
        latencies = [float(row["latency_ms"]) for row in rows if row.get("latency_ms") is not None]
        if measure == "avg_latency_ms":
            return None if not latencies else mean(latencies)
        if measure == "p50_latency_ms":
            return _percentile(latencies, 0.5)
        if measure == "p95_latency_ms":
            return _percentile(latencies, 0.95)
        if measure == "error_rate":
            return _rate(sum(bool(row.get("failure_code")) or row.get("event_type") == "error" for row in rows), len(rows))
        if measure == "policy_block_rate":
            policy_rows = [row for row in rows if row.get("event_type") == "policy_check"]
            return _rate(sum(row.get("policy_allowed") is False for row in policy_rows), len(policy_rows))
    if dataset == "evaluations":
        if measure == "pass_rate":
            return _rate(sum(bool(row["passed"]) for row in rows), len(rows))
        if measure == "blocking_pass_rate":
            blocking = [row for row in rows if bool(row["blocking"])]
            return _rate(sum(bool(row["passed"]) for row in blocking), len(blocking))
    raise ValueError("unsupported analytics measure")


def _latency_summary(values: list[float]) -> dict[str, int | float | None]:
    return {
        "count": len(values),
        "avg_ms": None if not values else mean(values),
        "p50_ms": _percentile(values, 0.50),
        "p95_ms": _percentile(values, 0.95),
        "max_ms": None if not values else max(values),
    }


class OperationalReadModel:
    """Provider-free analytics over the persisted sanitized observability projection only."""

    def __init__(self, store: ObservabilityStoreContract) -> None:
        self.store = store

    def _runs(self, run_id: str | None = None) -> list[dict[str, Any]]:
        if run_id is not None:
            item = self.store.get_run(run_id)
            return [] if item is None else [item]
        return self.store.list_runs(limit=1000)

    def _events(self, run_id: str | None = None) -> list[dict[str, Any]]:
        if run_id is not None:
            return self.store.get_events(run_id) if self.store.get_run(run_id) is not None else []
        rows: list[dict[str, Any]] = []
        for run in self._runs():
            rows.extend(self.store.get_events(str(run["run_id"])))
        return rows

    def _evaluations(self, run_id: str | None = None) -> list[dict[str, Any]]:
        if run_id is not None:
            return self.store.get_evaluation(run_id) if self.store.get_run(run_id) is not None else []
        rows: list[dict[str, Any]] = []
        for run in self._runs():
            rows.extend(self.store.get_evaluation(str(run["run_id"])))
        return rows

    def _passive_provider_operability(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        rows = [row for row in events if row.get("event_type") == "model_call"]
        latencies = [float(row["latency_ms"]) for row in rows if row.get("latency_ms") is not None]
        failures = [row for row in rows if row.get("failure_code")]
        last = max(rows, key=lambda row: str(row.get("timestamp") or ""), default=None)
        return {
            "source": "persisted_safe_model_call_events",
            "observations": len(rows),
            "live_calls": sum(row.get("live_call") is True for row in rows),
            "failures": len(failures),
            "failure_rate": _rate(len(failures), len(rows)),
            "latency": _latency_summary(latencies),
            "last": None if last is None else {
                "provider_id": last.get("provider_id"),
                "model_id": last.get("model_id"),
                "outcome": last.get("outcome"),
                "failure_code": last.get("failure_code"),
                "latency_ms": last.get("latency_ms"),
            },
            "external_probe_performed": False,
        }

    def _passive_adapter_operability(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        rows = [row for row in events if row.get("event_type") == "tool_result"]
        statuses = [int(row["status_code"]) for row in rows if row.get("status_code") is not None]
        success = sum(200 <= value < 300 for value in statuses)
        last = max(rows, key=lambda row: str(row.get("timestamp") or ""), default=None)
        return {
            "source": "persisted_safe_tool_result_events",
            "observations": len(rows),
            "status_observations": len(statuses),
            "http_2xx": success,
            "http_non_2xx": len(statuses) - success,
            "http_2xx_rate": _rate(success, len(statuses)),
            "status_codes": dict(sorted(Counter(str(value) for value in statuses).items())),
            "last": None if last is None else {
                "tool_name": last.get("tool_name"),
                "status_code": last.get("status_code"),
            },
            "external_probe_performed": False,
        }

    def production_health(
        self,
        *,
        provider_selection_state: str,
        live_operability: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        overview = self.store.overview()
        runs = self._runs()
        events = self._events()
        incomplete_runs = sum(not bool(row["completed"]) for row in runs)
        provider = self._passive_provider_operability(events)
        adapter = self._passive_adapter_operability(events)

        telemetry = None if live_operability is None else live_operability.get("telemetry")
        execution = None if live_operability is None else live_operability.get("execution")
        controls = None if live_operability is None else live_operability.get("controls")
        telemetry = telemetry if isinstance(telemetry, dict) else None
        execution = execution if isinstance(execution, dict) else None
        controls = controls if isinstance(controls, dict) else None

        heartbeat = None if telemetry is None else telemetry.get("runtime_heartbeat")
        heartbeat = heartbeat if isinstance(heartbeat, dict) else None
        sse = None if telemetry is None else telemetry.get("sse")
        sse = sse if isinstance(sse, dict) else None
        observability = None if telemetry is None else telemetry.get("observability")
        observability = observability if isinstance(observability, dict) else None
        provider_switch = None if controls is None else controls.get("provider_kill_switch")
        provider_switch = provider_switch if isinstance(provider_switch, dict) else None
        action_switch = None if controls is None else controls.get("action_kill_switch")
        action_switch = action_switch if isinstance(action_switch, dict) else None

        runtime_status = "not_instrumented" if heartbeat is None else str(heartbeat.get("status", "unknown"))
        adapter_status = "observed" if adapter["observations"] else "no_observations"
        provider_operability_status = "observed" if provider["observations"] else "no_observations"
        sse_status = "not_instrumented" if sse is None else "instrumented"
        provider_switch_status = "not_instrumented"
        if provider_switch is not None:
            provider_switch_status = "engaged" if provider_switch.get("engaged") else "disengaged"
        action_switch_status = "not_instrumented"
        if action_switch is not None:
            action_switch_status = "engaged" if action_switch.get("engaged") else "disengaged"

        overall_ready = self.store.ready()
        if heartbeat is not None:
            overall_ready = overall_ready and runtime_status == "ready"

        measured: dict[str, Any] = {
            "forbidden_field_leakage": 0,
            "provider_operability": provider,
            "tractian_adapter_operability": adapter,
        }
        if telemetry is not None:
            measured.update(
                {
                    "uptime_ms": telemetry.get("uptime_ms"),
                    "startup_readiness_ms": telemetry.get("startup_readiness_ms"),
                    "runtime_heartbeat": heartbeat,
                    "observability": observability,
                    "sse": sse,
                }
            )
        if execution is not None:
            measured["executor_pressure"] = execution
        if controls is not None:
            measured["controls"] = controls

        not_measured_yet = [
            "runtime_request_latency_by_outcome_ms",
            "api_read_query_latency_ms",
            "cpu_memory_pressure",
            "external_provider_probe",
            "external_tractian_probe",
            "reconnect_event_loss_rate",
            "logical_duplicate_delivery_rate",
        ]
        if live_operability is None:
            not_measured_yet.extend(
                [
                    "startup_readiness_ms",
                    "observability_overhead_ms",
                    "runtime_event_to_persistence_ms",
                    "persistence_to_browser_ms",
                    "sse_reconnect_recovery_ms",
                    "active_sse_clients",
                    "executor_pressure",
                    "provider_kill_switch",
                    "action_kill_switch",
                ]
            )

        return {
            "schema_version": "production-health-v2",
            "store_schema_version": OBSERVABILITY_SCHEMA_VERSION,
            "overall_status": "ready" if overall_ready else "degraded",
            "components": [
                {"component": "observability_store", "status": "ready" if self.store.ready() else "unavailable", "detail": "persistent sanitized observability read model"},
                {"component": "observability_api", "status": "ready", "detail": "REST/SSE control plane process is serving this response"},
                {"component": "evaluator_path", "status": "available", "detail": "post-runtime safe evaluation persistence path is configured"},
                {"component": "provider_selection", "status": provider_selection_state, "detail": "governed provider experiment selection state"},
                {"component": "runtime", "status": runtime_status, "detail": "independent process heartbeat plus executor execution state when product telemetry is attached"},
                {"component": "tractian_api_adapter", "status": adapter_status, "detail": "passive operability from real persisted tool_result status codes; no external probe"},
                {"component": "provider_operability", "status": provider_operability_status, "detail": "passive operability from real persisted model_call outcomes/latency; no provider probe"},
                {"component": "sse_clients", "status": sse_status, "detail": "active clients, reconnects and delivery lag measured in the live stream path"},
                {"component": "provider_kill_switch", "status": provider_switch_status, "detail": "host-owned gate blocks runtime_factory before provider-owned client construction"},
                {"component": "action_kill_switch", "status": action_switch_status, "detail": "ProductionRuntimeConfig v1 keeps consequential actions disabled"},
                {"component": "executor_pressure", "status": "measured" if execution is not None else "not_instrumented", "detail": "active/queued/inflight runs against configured max_workers"},
            ],
            "totals": {
                **overview,
                "incomplete_runs": incomplete_runs,
            },
            "measured": measured,
            "not_measured_yet": sorted(set(not_measured_yet)),
        }

    def tools_metrics(self, *, run_id: str | None = None) -> dict[str, Any]:
        events = self._events(run_id)
        tool_events = [row for row in events if row.get("tool_name")]
        by_tool: dict[str, dict[str, Any]] = {}
        for tool_name in sorted({str(row["tool_name"]) for row in tool_events}):
            rows = [row for row in tool_events if row.get("tool_name") == tool_name]
            calls = [row for row in rows if row.get("event_type") == "tool_call"]
            results = [row for row in rows if row.get("event_type") == "tool_result"]
            status_counts = Counter(str(row["status_code"]) for row in results if row.get("status_code") is not None)
            by_tool[tool_name] = {
                "tool_name": tool_name,
                "proposals": sum(row.get("event_type") == "tool_proposal" for row in rows),
                "calls": len(calls),
                "results": len(results),
                "observations": sum(row.get("event_type") == "observation" for row in rows),
                "status_codes": dict(sorted(status_counts.items())),
            }
        return {
            "schema_version": "tools-metrics-v2",
            "scope": {"run_id": run_id},
            "items": list(by_tool.values()),
            "count": len(by_tool),
        }

    def policies_metrics(self, *, run_id: str | None = None) -> dict[str, Any]:
        rows = [row for row in self._events(run_id) if row.get("event_type") == "policy_check"]
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[str(row.get("policy_stage") or "unknown")].append(row)
        items = []
        for stage, stage_rows in sorted(grouped.items()):
            blocked = sum(row.get("policy_allowed") is False for row in stage_rows)
            items.append(
                {
                    "policy_stage": stage,
                    "checks": len(stage_rows),
                    "allowed": sum(row.get("policy_allowed") is True for row in stage_rows),
                    "blocked": blocked,
                    "contained": sum(row.get("policy_contained") is True for row in stage_rows),
                    "block_rate": _rate(blocked, len(stage_rows)),
                    "violations": dict(sorted(Counter(str(row["policy_violation"]) for row in stage_rows if row.get("policy_violation")).items())),
                }
            )
        return {
            "schema_version": "policies-metrics-v2",
            "scope": {"run_id": run_id},
            "items": items,
            "count": len(items),
        }

    def evaluation_metrics(self, *, run_id: str | None = None) -> dict[str, Any]:
        rows = self._evaluations(run_id)
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[str(row["check_name"])].append(row)
        items = []
        for check_name, check_rows in sorted(grouped.items()):
            items.append(
                {
                    "check_name": check_name,
                    "evaluations": len(check_rows),
                    "passed": sum(bool(row["passed"]) for row in check_rows),
                    "pass_rate": _rate(sum(bool(row["passed"]) for row in check_rows), len(check_rows)),
                    "blocking": any(bool(row["blocking"]) for row in check_rows),
                }
            )
        blocking_rows = [row for row in rows if bool(row["blocking"])]
        return {
            "schema_version": "evaluation-metrics-v2",
            "scope": {"run_id": run_id},
            "checks": items,
            "check_count": len(items),
            "rows": len(rows),
            "overall_pass_rate": _rate(sum(bool(row["passed"]) for row in rows), len(rows)),
            "blocking_pass_rate": _rate(sum(bool(row["passed"]) for row in blocking_rows), len(blocking_rows)),
        }

    def lineage(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        if run is None:
            raise KeyError(run_id)
        events = self.store.get_events(run_id)
        evidence = {item["evidence_id"]: item for item in self.store.get_evidence(run_id)}
        cards: list[dict[str, Any]] = []
        for event in events:
            card = {
                "lineage_id": event["event_id"],
                "sequence": event["sequence"],
                "origin": event["origin"],
                "event_type": event["event_type"],
                "tool_name": event.get("tool_name"),
                "decision_kind": event.get("decision_kind"),
                "policy_stage": event.get("policy_stage"),
                "policy_allowed": event.get("policy_allowed"),
                "status_code": event.get("status_code"),
                "evidence_id": event.get("evidence_id"),
                "reason_code": event.get("reason_code"),
                "response_mode": event.get("response_mode"),
                "message": event.get("message"),
            }
            if event.get("evidence_id") in evidence:
                card["evidence_ref"] = evidence[event["evidence_id"]]
            cards.append(card)
        evaluation = self.store.get_evaluation(run_id)
        if evaluation:
            cards.append(
                {
                    "lineage_id": f"{run_id}:evaluation",
                    "sequence": len(events),
                    "origin": "EVALUATOR",
                    "event_type": "post_runtime_evaluation",
                    "evaluation": evaluation,
                }
            )
        return {
            "schema_version": "safe-output-lineage-v1",
            "run_id": run_id,
            "runtime_card_count": len(events),
            "evaluation_card_count": 1 if evaluation else 0,
            "cards": cards,
        }

    def query_schema(self) -> dict[str, Any]:
        return {
            "schema_version": "dynamic-analytics-schema-v2",
            "global_scope_fields": ["run_id"],
            "datasets": {
                dataset: {
                    "dimensions": sorted(_DIMENSIONS[dataset]),
                    "measures": sorted(_MEASURES[dataset]),
                }
                for dataset in ("runs", "events", "evaluations")
            },
            "filter_operators": ["eq", "ne", "in"],
            "chart_types": {
                "table": {"dimension_count": [0, 1, 2]},
                "bar": {"dimension_count": [1]},
                "line": {"dimension_count": [1]},
                "heatmap": {"dimension_count": [2]},
                "histogram": {"dimension_count": [0], "measures": ["latency_ms_distribution"]},
            },
            "limits": {"max_dimensions": 2, "max_filters": 8, "max_rows": 500, "max_source_runs": 1000},
        }

    def query(self, spec: AnalyticsQuery) -> dict[str, Any]:
        allowed_dimensions = _DIMENSIONS[spec.dataset]
        allowed_measures = _MEASURES[spec.dataset]
        for dimension in spec.dimensions:
            if dimension not in allowed_dimensions:
                raise ValueError(f"dimension_not_allowed:{dimension}")
        if spec.measure not in allowed_measures:
            raise ValueError(f"measure_not_allowed:{spec.measure}")
        for item in spec.filters:
            if item.field not in allowed_dimensions:
                raise ValueError(f"filter_field_not_allowed:{item.field}")
        if spec.chart_type == "histogram" and spec.measure not in _HISTOGRAM_MEASURES:
            raise ValueError("histogram_measure_not_allowed")
        if spec.measure in _HISTOGRAM_MEASURES and spec.chart_type != "histogram":
            raise ValueError("distribution_measure_requires_histogram")

        source = {
            "runs": lambda: self._runs(spec.run_id),
            "events": lambda: self._events(spec.run_id),
            "evaluations": lambda: self._evaluations(spec.run_id),
        }[spec.dataset]()
        filtered = [row for row in source if all(_filter_matches(row, item) for item in spec.filters)]

        if spec.chart_type == "histogram":
            values = [float(row["latency_ms"]) for row in filtered if row.get("latency_ms") is not None]
            if not values:
                rows: list[dict[str, Any]] = []
            else:
                bin_count = min(20, max(1, ceil(len(values) ** 0.5)))
                minimum, maximum = min(values), max(values)
                width = max(1.0, (maximum - minimum) / bin_count)
                buckets = [0 for _ in range(bin_count)]
                for value in values:
                    index = min(bin_count - 1, int((value - minimum) / width))
                    buckets[index] += 1
                rows = [
                    {
                        "bin_start": minimum + index * width,
                        "bin_end": minimum + (index + 1) * width,
                        "value": count,
                    }
                    for index, count in enumerate(buckets)
                ]
        elif spec.dimensions:
            grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
            for row in filtered:
                key = tuple(_scalar_key(row.get(dimension)) for dimension in spec.dimensions)
                grouped[key].append(row)
            rows = []
            for key, group_rows in sorted(grouped.items(), key=lambda item: tuple(str(value) for value in item[0])):
                result = {dimension: value for dimension, value in zip(spec.dimensions, key, strict=True)}
                result["value"] = _aggregate_measure(spec.dataset, group_rows, spec.measure)
                rows.append(result)
        else:
            rows = [{"value": _aggregate_measure(spec.dataset, filtered, spec.measure)}]

        return {
            "schema_version": "dynamic-analytics-result-v2",
            "dataset": spec.dataset,
            "run_id": spec.run_id,
            "dimensions": list(spec.dimensions),
            "measure": spec.measure,
            "chart_type": spec.chart_type,
            "source_row_count": len(filtered),
            "rows": rows[: spec.limit],
            "truncated": len(rows) > spec.limit,
        }

    def provider_experiments(self) -> dict[str, Any]:
        return provider_experiment_registry().model_dump(mode="json")
