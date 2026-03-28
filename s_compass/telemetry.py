"""
telemetry.py

Telemetry normalizer for S Compass (Design-doc §4.2).

Converts heterogeneous application payloads into a sequence of canonical
Event objects so the rest of the pipeline stays vendor- and model-agnostic.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from .schemas import Event, VALID_EVENT_TYPES


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_event(
    event_type: str,
    session_id: str,
    trace_id: str,
    payload: Dict[str, Any] | None = None,
    **kwargs: Any,
) -> Event:
    """Build a canonical :class:`Event`, validating the event type.

    Parameters
    ----------
    event_type:
        Must be one of the types listed in :data:`VALID_EVENT_TYPES`.
    session_id, trace_id:
        Required identifiers for the telemetry stream.
    payload:
        Arbitrary data associated with the event.
    **kwargs:
        Forwarded to :class:`Event` (e.g. ``step_id``, ``source``).

    Returns
    -------
    Event
        A fully populated canonical event.

    Raises
    ------
    ValueError
        If *event_type* is not recognised.
    """
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(
            f"Unknown event_type {event_type!r}. "
            f"Valid types: {sorted(VALID_EVENT_TYPES)}"
        )
    return Event(
        event_type=event_type,
        timestamp=_utc_now(),
        session_id=session_id,
        trace_id=trace_id,
        payload=payload or {},
        **kwargs,
    )


def normalize_step_payload(raw: Dict[str, Any]) -> List[Event]:
    """Convert a raw step payload (roughly matching API §8.2) into events.

    This is a convenience helper that produces multiple canonical events
    from a single inference-step submission so that downstream processors
    can treat retrieval, generation, and tool calls uniformly.
    """
    session_id = raw.get("session_id", "unknown")
    trace_id = raw.get("trace_id", "unknown")
    step_id = raw.get("step_id")
    events: List[Event] = []

    # prompt received
    if "prompt" in raw:
        events.append(
            normalize_event(
                "prompt.received",
                session_id=session_id,
                trace_id=trace_id,
                payload={"prompt": raw["prompt"]},
                step_id=step_id,
            )
        )

    # retrieval completed
    if raw.get("retrieved_context"):
        events.append(
            normalize_event(
                "retrieval.completed",
                session_id=session_id,
                trace_id=trace_id,
                payload={"chunks": raw["retrieved_context"]},
                step_id=step_id,
            )
        )

    # model completed
    if "output" in raw or "output_text" in raw:
        events.append(
            normalize_event(
                "model.completed",
                session_id=session_id,
                trace_id=trace_id,
                payload={
                    "output": raw.get("output") or raw.get("output_text"),
                    "model": raw.get("model"),
                },
                step_id=step_id,
            )
        )

    # tool calls
    for tc in raw.get("tool_calls", []):
        events.append(
            normalize_event(
                "tool.called",
                session_id=session_id,
                trace_id=trace_id,
                payload=tc,
                step_id=step_id,
            )
        )

    return events
