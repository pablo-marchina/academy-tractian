from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
import os
from pathlib import Path
from threading import Event, Thread
from time import perf_counter, sleep, time
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from psycopg import connect, sql

from research.e2.controller import ControllerContext, ControllerDecision, ControllerDecisionKind
from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse

from academy_tractian.authenticated_postgres_product_api import (
    create_authenticated_postgres_action_capable_product_app,
)
from academy_tractian.load_concurrency_benchmark import (
    LoadBenchmarkProtocol,
    LoadPressureObservation,
    LoadRequestObservation,
    analyze_load_benchmark,
)
from academy_tractian.product_api import DEFAULT_RUNTIME_PERMISSIONS
from academy_tractian.production_actions_v2 import ProductionActionPrincipal
from academy_tractian.runtime_identity import SignedRuntimeIdentityClaims, issue_signed_runtime_token


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)

SECRET = "load-benchmark-runtime-secret-that-is-at-least-32-bytes"
ISSUER = "academy-load-benchmark"
AUDIENCE = "academy-product"


class DelayedFinalSource:
    def decide(self, _context: ControllerContext) -> ControllerDecision:
        sleep(0.05)
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Provider-free load benchmark completed.",
            },
        )


class NoopTransport:
    def request(self, _request: BoundRequest) -> TransportResponse:
        raise AssertionError("final-only load benchmark must not call transport")


def _resolver(*, user_id: str) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="company-a",
        permissions=frozenset(),
        resource_company_bindings=(),
    )


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_load_{suffix}"
        self.role = f"academy_load_scoped_{suffix}"
        self.password = "scoped-test-password"
        with connect(admin_dsn, autocommit=True) as connection:
            connection.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOBYPASSRLS").format(
                    sql.Identifier(self.role),
                    sql.Literal(self.password),
                )
            )
        parsed = urlsplit(admin_dsn)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 5432
        database = parsed.path or "/postgres"
        self.scoped_dsn = urlunsplit(
            (
                parsed.scheme or "postgresql",
                f"{self.role}:{self.password}@{host}:{port}",
                database,
                "",
                "",
            )
        )

    def cleanup(self) -> None:
        with connect(self.admin_dsn, autocommit=True) as connection:
            connection.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(self.schema))
            )
            connection.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(self.role)))


@pytest.fixture
def postgres_fixture():
    fixture = _PgFixture(os.environ["POSTGRES_OPERATIONAL_TEST_DSN"])
    try:
        yield fixture
    finally:
        fixture.cleanup()


def _headers(*, user_id: str, organization_id: str) -> dict[str, str]:
    now = int(time())
    token = issue_signed_runtime_token(
        secret=SECRET,
        claims=SignedRuntimeIdentityClaims(
            issuer=ISSUER,
            audience=AUDIENCE,
            token_id=f"load-{organization_id}-{user_id}-{uuid4().hex[:12]}",
            identity_id=f"identity-{organization_id}-{user_id}",
            user_id=user_id,
            organization_id=organization_id,
            permissions=tuple(sorted(DEFAULT_RUNTIME_PERMISSIONS)),
            issued_at=now - 5,
            expires_at=now + 300,
        ),
    )
    return {"Authorization": f"Bearer {token}"}


def _pressure_sample(app, *, level: int, started: float) -> LoadPressureObservation:
    execution = app.state.run_execution_registry.snapshot()
    telemetry = app.state.production_telemetry.snapshot()
    resources = telemetry["resources"]
    persistence = telemetry["observability"]["persistence_duration"]
    return LoadPressureObservation(
        concurrency_level=level,
        elapsed_ms=(perf_counter() - started) * 1000.0,
        active_runs=int(execution["active_runs"]),
        queued_runs=int(execution["queued_runs"]),
        inflight_runs=int(execution["inflight_runs"]),
        max_workers=int(execution["max_workers"]),
        executor_utilization=float(execution["executor_utilization"]),
        process_cpu_time_ms=float(resources["process_cpu_time_ms"]),
        rss_current_bytes=None
        if resources["rss_current_bytes"] is None
        else int(resources["rss_current_bytes"]),
        rss_max_bytes=None
        if resources["rss_max_bytes"] is None
        else int(resources["rss_max_bytes"]),
        persistence_p95_ms=None
        if persistence["p95_ms"] is None
        else float(persistence["p95_ms"]),
    )


def test_authenticated_postgres_load_campaign_measures_saturation_without_capacity_claim(
    postgres_fixture,
) -> None:
    protocol = LoadBenchmarkProtocol(
        protocol_id="postgres-load-ci-v1",
        concurrency_levels=(1, 4),
        requests_per_level=6,
        warmup_requests=1,
        completion_timeout_seconds=10,
        pressure_poll_interval_ms=5,
    )
    app = create_authenticated_postgres_action_capable_product_app(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        decision_source_factory=DelayedFinalSource,
        transport_factory=NoopTransport,
        authorization_resolver=_resolver,
        runtime_identity_secret=SECRET,
        runtime_identity_issuer=ISSUER,
        runtime_identity_audience=AUDIENCE,
        schema=postgres_fixture.schema,
        initialize_schema=True,
        max_workers=2,
        provider_calls_enabled=True,
        actions_enabled=False,
        heartbeat_interval_ms=250,
    )
    assert app.state.local_test_storage_enabled is False

    request_observations: list[LoadRequestObservation] = []
    pressure_observations: list[LoadPressureObservation] = []
    wall_durations: dict[int, float] = {}
    run_scope: dict[str, tuple[str, str]] = {}

    with TestClient(app) as client:
        warm_headers = _headers(user_id="warm-user", organization_id="warm-org")
        warm = client.post(
            "/api/runs",
            headers=warm_headers,
            json={"user_request": "Warm provider-free benchmark path."},
        )
        assert warm.status_code == 202
        warm_future = app.state.run_execution_registry.future(warm.json()["run_id"])
        assert warm_future is not None
        warm_future.result(timeout=10)

        for level in protocol.concurrency_levels:
            level_started = perf_counter()
            stop_monitor = Event()

            def monitor() -> None:
                while not stop_monitor.is_set():
                    pressure_observations.append(
                        _pressure_sample(app, level=level, started=level_started)
                    )
                    stop_monitor.wait(protocol.pressure_poll_interval_ms / 1000.0)

            monitor_thread = Thread(target=monitor, name=f"load-pressure-{level}", daemon=True)
            monitor_thread.start()

            def one_request(index: int) -> LoadRequestObservation:
                organization_id = "org-a" if index % 2 == 0 else "org-b"
                user_id = "user-a" if index % 2 == 0 else "user-b"
                headers = _headers(user_id=user_id, organization_id=organization_id)
                started = perf_counter()
                response = client.post(
                    "/api/runs",
                    headers=headers,
                    json={"user_request": f"Synthetic load request {level}-{index}."},
                )
                submit_ms = (perf_counter() - started) * 1000.0
                if response.status_code != 202:
                    return LoadRequestObservation(
                        concurrency_level=level,
                        request_index=index,
                        submit_status_code=response.status_code,
                        submit_latency_ms=submit_ms,
                        terminal_state="submit_rejected",
                    )

                run_id = response.json()["run_id"]
                run_scope[run_id] = (organization_id, user_id)
                future = app.state.run_execution_registry.future(run_id)
                assert future is not None
                try:
                    future.result(timeout=protocol.completion_timeout_seconds)
                except FutureTimeout:
                    return LoadRequestObservation(
                        concurrency_level=level,
                        request_index=index,
                        submit_status_code=202,
                        submit_latency_ms=submit_ms,
                        end_to_end_latency_ms=(perf_counter() - started) * 1000.0,
                        terminal_state="timeout",
                    )
                terminal = app.state.run_execution_registry.status(run_id)
                assert terminal in {"completed", "failed", "interrupted", "uncertain"}
                return LoadRequestObservation(
                    concurrency_level=level,
                    request_index=index,
                    submit_status_code=202,
                    submit_latency_ms=submit_ms,
                    end_to_end_latency_ms=(perf_counter() - started) * 1000.0,
                    terminal_state=terminal,
                )

            with ThreadPoolExecutor(max_workers=level) as executor:
                observations = tuple(
                    executor.map(one_request, range(protocol.requests_per_level))
                )
            wall_durations[level] = perf_counter() - level_started
            request_observations.extend(observations)
            stop_monitor.set()
            monitor_thread.join(timeout=2)
            pressure_observations.append(
                _pressure_sample(app, level=level, started=level_started)
            )

        report = analyze_load_benchmark(
            protocol,
            requests=tuple(request_observations),
            pressure=tuple(pressure_observations),
            wall_duration_seconds=wall_durations,
        )

        assert report.total_requests == 12
        assert report.production_capacity_claim_ready is False
        assert report.thresholds_preregistered is False
        assert all(item.accepted_count == 6 for item in report.levels)
        assert all(item.completed_count == 6 for item in report.levels)
        assert all(item.error_rate == 0 for item in report.levels)
        assert all(item.submit_latency.p99_ms is not None for item in report.levels)
        assert all(item.end_to_end_latency.p99_ms is not None for item in report.levels)
        assert report.levels[1].peak_executor_utilization == 1.0
        assert report.levels[1].peak_queued_runs >= 1
        assert report.levels[1].peak_inflight_runs >= 3
        assert report.levels[1].persistence_p95_ms_max_observed is not None

        assert len(run_scope) == 12
        assert len(set(run_scope)) == 12
        org_a_run = next(run_id for run_id, scope in run_scope.items() if scope[0] == "org-a")
        wrong_tenant = client.get(
            f"/api/runs/{org_a_run}",
            headers=_headers(user_id="user-b", organization_id="org-b"),
        )
        assert wrong_tenant.status_code == 404
        assert wrong_tenant.json()["detail"] == "run_not_found"

        serialized = report.model_dump_json()
        for private_fragment in (
            "org-a",
            "org-b",
            "user-a",
            "user-b",
            "identity-",
            org_a_run,
            "Synthetic load request",
        ):
            assert private_fragment not in serialized

        output_path = os.environ.get("LOAD_BENCHMARK_OUTPUT")
        if output_path:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
