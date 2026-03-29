"""
store.py

In-memory evaluation store for S Compass (Design-doc §4.8).

Persists sessions, steps, score snapshots, and policy interventions so that
both live monitoring and retrospective analysis are possible.

For a production deployment this would be backed by Redis / Postgres /
a graph database; the in-memory implementation is the MVP default.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .schemas import Event, PolicyAction, ScoreSnapshot


@dataclass
class SessionRecord:
    """All data associated with a single traced session."""

    session_id: str
    events: List[Event] = field(default_factory=list)
    scores: List[ScoreSnapshot] = field(default_factory=list)
    policies: List[PolicyAction] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


class EvaluationStore:
    """Simple in-memory store for S Compass data."""

    def __init__(self) -> None:
        self._sessions: Dict[str, SessionRecord] = {}

    # -- sessions -----------------------------------------------------------

    def start_session(
        self,
        session_id: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> SessionRecord:
        record = SessionRecord(session_id=session_id, metadata=metadata or {})
        self._sessions[session_id] = record
        return record

    def get_session(self, session_id: str) -> Optional[SessionRecord]:
        return self._sessions.get(session_id)

    def list_sessions(self) -> List[str]:
        return list(self._sessions.keys())

    # -- events -------------------------------------------------------------

    def add_event(self, session_id: str, event: Event) -> None:
        rec = self._sessions.get(session_id)
        if rec is None:
            rec = self.start_session(session_id)
        rec.events.append(event)

    # -- scores -------------------------------------------------------------

    def add_score(self, session_id: str, snapshot: ScoreSnapshot) -> None:
        rec = self._sessions.get(session_id)
        if rec is None:
            rec = self.start_session(session_id)
        rec.scores.append(snapshot)

    def get_scores(self, session_id: str) -> List[ScoreSnapshot]:
        rec = self._sessions.get(session_id)
        return list(rec.scores) if rec else []

    # -- policies -----------------------------------------------------------

    def add_policy(self, session_id: str, action: PolicyAction) -> None:
        rec = self._sessions.get(session_id)
        if rec is None:
            rec = self.start_session(session_id)
        rec.policies.append(action)

    # -- rolling window statistics ------------------------------------------

    def rolling_window_stats(
        self,
        session_id: str,
        window: int = 10,
    ) -> Dict[str, Any]:
        """Return rolling-window statistics over the last *window* score snapshots.

        Computes mean, standard deviation, minimum, and maximum for each of the
        four score fields (``c``, ``i``, ``kappa``, ``s``) across the most
        recent *window* snapshots.  If fewer than *window* snapshots are
        available all available snapshots are used.

        Parameters
        ----------
        session_id:
            The session to inspect.
        window:
            Number of most-recent snapshots to include.

        Returns
        -------
        dict
            ``{"session_id", "window", "count", "stats": {"c": {...}, ...}}``
            where each field dict has keys ``mean``, ``std``, ``min``, ``max``.
            Returns ``None`` if the session does not exist.
        """
        rec = self._sessions.get(session_id)
        if rec is None:
            return None
        snaps = rec.scores[-window:] if window > 0 else []
        n = len(snaps)
        if n == 0:
            return {
                "session_id": session_id,
                "window": window,
                "count": 0,
                "stats": {},
            }

        def _field_stats(vals: List[float]) -> Dict[str, float]:
            mean = sum(vals) / len(vals)
            variance = sum((v - mean) ** 2 for v in vals) / len(vals)
            return {
                "mean": round(mean, 4),
                "std": round(math.sqrt(variance), 4),
                "min": round(min(vals), 4),
                "max": round(max(vals), 4),
            }

        return {
            "session_id": session_id,
            "window": window,
            "count": n,
            "stats": {
                "c": _field_stats([s.c for s in snaps]),
                "i": _field_stats([s.i for s in snaps]),
                "kappa": _field_stats([s.kappa for s in snaps]),
                "s": _field_stats([s.s for s in snaps]),
            },
        }

    def session_summary(self, session_id: str) -> Optional[Dict[str, object]]:
        """Return an aggregate summary for a session (Design-doc §8.3)."""
        rec = self._sessions.get(session_id)
        if rec is None:
            return None
        if not rec.scores:
            return {
                "session_id": session_id,
                "step_count": 0,
                "regime_counts": {},
                "avg_scores": {},
                "mode_counts": {},
                "avg_confidence": None,
            }
        regime_counts: Dict[str, int] = {}
        mode_counts: Dict[str, int] = {}
        c_vals, i_vals, k_vals, s_vals, conf_vals = [], [], [], [], []
        for snap in rec.scores:
            regime_counts[snap.regime] = regime_counts.get(snap.regime, 0) + 1
            mode_counts[snap.mode] = mode_counts.get(snap.mode, 0) + 1
            c_vals.append(snap.c)
            i_vals.append(snap.i)
            k_vals.append(snap.kappa)
            s_vals.append(snap.s)
            conf_vals.append(snap.confidence)
        n = len(rec.scores)
        return {
            "session_id": session_id,
            "step_count": n,
            "regime_counts": regime_counts,
            "avg_scores": {
                "c": round(sum(c_vals) / n, 4),
                "i": round(sum(i_vals) / n, 4),
                "kappa": round(sum(k_vals) / n, 4),
                "s": round(sum(s_vals) / n, 4),
            },
            "mode_counts": mode_counts,
            "avg_confidence": round(sum(conf_vals) / n, 4),
        }
