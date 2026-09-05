from __future__ import annotations

import json

import pytest

from academy_tractian.realtime_wakeup import (
    PostgresListenNotifyWakeup,
    decode_wakeup_payload,
    encode_wakeup_payload,
)


def test_wakeup_payload_round_trip_contains_only_cursor_material() -> None:
    payload = encode_wakeup_payload(run_id="run_0123456789abcdef", sequence=17)

    assert decode_wakeup_payload(payload) == ("run_0123456789abcdef", 17)
    assert json.loads(payload) == {
        "run_id": "run_0123456789abcdef",
        "sequence": 17,
    }
    for forbidden in ("message", "arguments", "evidence", "user_id", "organization_id"):
        assert forbidden not in payload


@pytest.mark.parametrize(
    "payload",
    (
        "not-json",
        "[]",
        '{"run_id":"run_a"}',
        '{"run_id":"run_a","sequence":0,"message":"private"}',
        '{"run_id":"","sequence":0}',
        '{"run_id":"run_a","sequence":-1}',
        '{"run_id":"run_a","sequence":true}',
        '{"run_id":"run_a","sequence":"1"}',
    ),
)
def test_wakeup_payload_rejects_malformed_or_expanded_shapes(payload: str) -> None:
    with pytest.raises(ValueError):
        decode_wakeup_payload(payload)


def test_postgres_wakeup_configuration_fails_closed() -> None:
    with pytest.raises(ValueError, match="DSN"):
        PostgresListenNotifyWakeup(dsn="")
    with pytest.raises(ValueError, match="channel"):
        PostgresListenNotifyWakeup(dsn="postgresql://example", channel="bad-channel;DROP")
    with pytest.raises(ValueError, match="listen_timeout_seconds"):
        PostgresListenNotifyWakeup(
            dsn="postgresql://example",
            listen_timeout_seconds=0.001,
        )
