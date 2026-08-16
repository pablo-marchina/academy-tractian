from __future__ import annotations

from .models import RunTrace, TraceEvent

TERMINAL_EVENTS = {"run_finished", "error"}


def validate_trace(trace: RunTrace) -> list[str]:
    errors: list[str] = []
    if not trace.events:
        return ["trace has no events"]
    sequences = [event.sequence for event in trace.events]
    if sequences != list(range(len(sequences))):
        errors.append("event sequence must be contiguous from zero")
    terminal_positions = [i for i, event in enumerate(trace.events) if event.event_type in TERMINAL_EVENTS]
    if len(terminal_positions) != 1:
        errors.append("trace must contain exactly one terminal event")
    elif terminal_positions[0] != len(trace.events) - 1:
        errors.append("terminal event must be last")
    if trace.events[0].event_type != "run_started":
        errors.append("trace must start with run_started")
    return errors


def append_event(trace: RunTrace, event: TraceEvent) -> RunTrace:
    expected = len(trace.events)
    if event.sequence != expected:
        raise ValueError(f"expected event sequence {expected}, got {event.sequence}")
    return trace.model_copy(update={"events": [*trace.events, event]})
