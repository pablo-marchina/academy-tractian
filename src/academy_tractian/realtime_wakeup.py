from __future__ import annotations

import asyncio
import json
import re
from threading import Event, Lock, Thread
from typing import Any, Protocol


DEFAULT_POSTGRES_WAKEUP_CHANNEL = "academy_observability_events"
_CHANNEL = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class RealtimeWakeup(Protocol):
    """Wake-up only coordination boundary for durable realtime streams.

    Implementations never own event truth. Callers must always read the durable observability
    store using their sequence cursor before and after waiting. A missed or duplicated wakeup is
    therefore an efficiency event, not a correctness event.
    """

    def start(self) -> None: ...

    def close(self) -> None: ...

    def generation(self, run_id: str) -> int: ...

    async def wait_for_change(
        self,
        run_id: str,
        *,
        after_generation: int,
        timeout_seconds: float,
    ) -> bool: ...

    def snapshot(self) -> dict[str, Any]: ...


def encode_wakeup_payload(*, run_id: str, sequence: int) -> str:
    if not run_id or len(run_id) > 128:
        raise ValueError("wakeup run_id must be within [1, 128] characters")
    if sequence < 0:
        raise ValueError("wakeup sequence must be >= 0")
    payload = json.dumps(
        {"run_id": run_id, "sequence": sequence},
        sort_keys=True,
        separators=(",", ":"),
    )
    if len(payload.encode("utf-8")) > 1024:
        raise ValueError("wakeup payload exceeds the bounded coordination contract")
    return payload


def decode_wakeup_payload(payload: str) -> tuple[str, int]:
    try:
        decoded = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid wakeup JSON") from exc
    if not isinstance(decoded, dict) or set(decoded) != {"run_id", "sequence"}:
        raise ValueError("invalid wakeup payload shape")
    run_id = decoded.get("run_id")
    sequence = decoded.get("sequence")
    if not isinstance(run_id, str) or not run_id or len(run_id) > 128:
        raise ValueError("invalid wakeup run_id")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
        raise ValueError("invalid wakeup sequence")
    return run_id, sequence


def _resolve_future(future: asyncio.Future[int], sequence: int) -> None:
    if not future.done():
        future.set_result(sequence)


def _cancel_future(future: asyncio.Future[int]) -> None:
    if not future.done():
        future.cancel()


class PostgresListenNotifyWakeup:
    """One dedicated LISTEN connection per application replica.

    PostgreSQL NOTIFY is used only to wake local SSE waiters. Event rows remain the durable
    source of truth, keyed by run_id/sequence. The listener reconnects independently from the
    request pools and malformed or duplicate notifications never enter the browser projection.
    """

    def __init__(
        self,
        *,
        dsn: str,
        channel: str = DEFAULT_POSTGRES_WAKEUP_CHANNEL,
        listen_timeout_seconds: float = 0.5,
        reconnect_delay_seconds: float = 0.25,
    ) -> None:
        if not dsn:
            raise ValueError("PostgreSQL wakeup DSN is required")
        if not _CHANNEL.fullmatch(channel):
            raise ValueError("invalid PostgreSQL wakeup channel")
        if not 0.05 <= listen_timeout_seconds <= 5.0:
            raise ValueError("listen_timeout_seconds must be within [0.05, 5.0]")
        if not 0.05 <= reconnect_delay_seconds <= 5.0:
            raise ValueError("reconnect_delay_seconds must be within [0.05, 5.0]")

        self._dsn = dsn
        self.channel = channel
        self.listen_timeout_seconds = listen_timeout_seconds
        self.reconnect_delay_seconds = reconnect_delay_seconds
        self._lock = Lock()
        self._stop = Event()
        self._thread: Thread | None = None
        self._latest_sequence: dict[str, int] = {}
        self._waiters: dict[str, set[asyncio.Future[int]]] = {}
        self._started = False
        self._connected = False
        self._notifications_received = 0
        self._valid_notifications = 0
        self._duplicate_notifications = 0
        self._payload_rejections = 0
        self._listener_reconnects = 0
        self._wait_calls = 0
        self._wait_wakeups = 0
        self._wait_timeouts = 0

    def start(self) -> None:
        with self._lock:
            if self._started:
                return
            self._started = True
            self._stop.clear()
            thread = Thread(
                target=self._listen_loop,
                name="academy-postgres-realtime-wakeup",
                daemon=True,
            )
            self._thread = thread
        thread.start()

    def close(self) -> None:
        with self._lock:
            if not self._started:
                return
            self._started = False
            self._stop.set()
            thread = self._thread
            self._thread = None
            waiters = [future for values in self._waiters.values() for future in values]
            self._waiters.clear()
        for future in waiters:
            future.get_loop().call_soon_threadsafe(_cancel_future, future)
        if thread is not None:
            thread.join(timeout=max(2.0, self.listen_timeout_seconds * 4))
        with self._lock:
            self._connected = False

    def generation(self, run_id: str) -> int:
        with self._lock:
            return self._latest_sequence.get(run_id, -1)

    async def wait_for_change(
        self,
        run_id: str,
        *,
        after_generation: int,
        timeout_seconds: float,
    ) -> bool:
        if not run_id:
            raise ValueError("run_id must be non-empty")
        if after_generation < -1:
            raise ValueError("after_generation must be >= -1")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be > 0")

        loop = asyncio.get_running_loop()
        future: asyncio.Future[int] = loop.create_future()
        with self._lock:
            if not self._started:
                raise RuntimeError("realtime wakeup listener is not started")
            self._wait_calls += 1
            current = self._latest_sequence.get(run_id, -1)
            if current > after_generation:
                self._wait_wakeups += 1
                return True
            self._waiters.setdefault(run_id, set()).add(future)

        try:
            await asyncio.wait_for(future, timeout=timeout_seconds)
        except asyncio.TimeoutError:
            with self._lock:
                self._wait_timeouts += 1
            return False
        finally:
            with self._lock:
                values = self._waiters.get(run_id)
                if values is not None:
                    values.discard(future)
                    if not values:
                        self._waiters.pop(run_id, None)

        with self._lock:
            self._wait_wakeups += 1
        return True

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "schema_version": "postgres-realtime-wakeup-v1",
                "backend": "postgresql_listen_notify",
                "started": self._started,
                "connected": self._connected,
                "notifications_received": self._notifications_received,
                "valid_notifications": self._valid_notifications,
                "duplicate_notifications": self._duplicate_notifications,
                "payload_rejections": self._payload_rejections,
                "listener_reconnects": self._listener_reconnects,
                "wait_calls": self._wait_calls,
                "wait_wakeups": self._wait_wakeups,
                "wait_timeouts": self._wait_timeouts,
                "active_waiters": sum(len(values) for values in self._waiters.values()),
                "tracked_runs": len(self._latest_sequence),
            }

    def _publish_local(self, *, run_id: str, sequence: int) -> None:
        with self._lock:
            previous = self._latest_sequence.get(run_id, -1)
            if sequence <= previous:
                self._duplicate_notifications += 1
                return
            self._latest_sequence[run_id] = sequence
            self._valid_notifications += 1
            waiters = tuple(self._waiters.get(run_id, ()))
        for future in waiters:
            future.get_loop().call_soon_threadsafe(_resolve_future, future, sequence)

    def _listen_loop(self) -> None:
        try:
            import psycopg
            from psycopg import sql
        except ImportError:
            with self._lock:
                self._connected = False
                self._listener_reconnects += 1
            return

        connected_once = False
        while not self._stop.is_set():
            try:
                with psycopg.connect(self._dsn, autocommit=True) as connection:
                    connection.execute(sql.SQL("LISTEN {}").format(sql.Identifier(self.channel)))
                    with self._lock:
                        self._connected = True
                        if connected_once:
                            self._listener_reconnects += 1
                    connected_once = True
                    while not self._stop.is_set():
                        for notification in connection.notifies(
                            timeout=self.listen_timeout_seconds,
                            stop_after=100,
                        ):
                            with self._lock:
                                self._notifications_received += 1
                            try:
                                run_id, sequence = decode_wakeup_payload(notification.payload)
                            except ValueError:
                                with self._lock:
                                    self._payload_rejections += 1
                                continue
                            self._publish_local(run_id=run_id, sequence=sequence)
            except Exception:
                with self._lock:
                    self._connected = False
                    if connected_once:
                        self._listener_reconnects += 1
                if self._stop.wait(self.reconnect_delay_seconds):
                    break
            finally:
                with self._lock:
                    self._connected = False
