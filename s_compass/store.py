"""
store.py

In-memory evaluation store for S Compass (Design-doc §4.8).

Persists sessions, steps, score snapshots, and policy interventions so that
both live monitoring and retrospective analysis are possible.  Includes
session-level drift detection and regime-transition tracking to surface
C / I / κ / S trends, regime stability, and early-warning alerts
(Design-doc §4.9).

For a production deployment this would be backed by Redis / Postgres /
a graph database; the in-memory implementation is the MVP default.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

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

    # -- drift detection & regime transitions (Design-doc §4.9) -------------

    @staticmethod
    def _linear_slope(values: List[float]) -> float:
        """Return the OLS slope of *values* treated as equally spaced points.

        Uses the standard formula for the slope of the best-fit line through
        ``(0, y_0), (1, y_1), …, (n-1, y_{n-1})``.  Returns ``0.0`` when
        fewer than two data points are available.
        """
        n = len(values)
        if n < 2:
            return 0.0
        sum_x = n * (n - 1) / 2.0
        sum_x2 = n * (n - 1) * (2 * n - 1) / 6.0
        sum_y = sum(values)
        sum_xy = sum(i * y for i, y in enumerate(values))
        denom = n * sum_x2 - sum_x * sum_x
        if denom == 0.0:
            return 0.0
        return (n * sum_xy - sum_x * sum_y) / denom

    def regime_transitions(
        self,
        session_id: str,
        window: int = 0,
    ) -> Optional[List[Dict[str, Any]]]:
        """Return a list of regime transitions within the session.

        Each transition records the step index where the regime changed,
        along with the previous and new regime labels.

        Parameters
        ----------
        session_id:
            The session to inspect.
        window:
            If positive, only the last *window* snapshots are considered.
            ``0`` means all snapshots.

        Returns
        -------
        list[dict] | None
            A list of ``{"step": int, "from": str, "to": str}`` dicts.
            Returns ``None`` if the session does not exist.
        """
        rec = self._sessions.get(session_id)
        if rec is None:
            return None
        snaps = rec.scores[-window:] if window > 0 else rec.scores
        transitions: List[Dict[str, Any]] = []
        for idx in range(1, len(snaps)):
            prev, curr = snaps[idx - 1].regime, snaps[idx].regime
            if prev != curr:
                transitions.append({"step": idx, "from": prev, "to": curr})
        return transitions

    # -- alert thresholds ---------------------------------------------------
    _SLOPE_DECLINING: float = -0.03
    _TRANSITION_RATE_UNSTABLE: float = 0.30

    def drift_summary(
        self,
        session_id: str,
        window: int = 10,
    ) -> Optional[Dict[str, Any]]:
        """Return a drift-detection summary for the session.

        Analyses score trends, regime stability, and generates early-warning
        alerts when the session trajectory is concerning.

        Parameters
        ----------
        session_id:
            The session to inspect.
        window:
            Number of most-recent snapshots to include (0 = all).

        Returns
        -------
        dict | None
            ``{"session_id", "window", "step_count", "s_trend", "c_trend",
            "i_trend", "kappa_trend", "regime_transitions", "transition_rate",
            "dominant_regime", "current_regime", "alerts"}``
            Returns ``None`` if the session does not exist.
        """
        rec = self._sessions.get(session_id)
        if rec is None:
            return None
        snaps = rec.scores[-window:] if window > 0 else rec.scores
        n = len(snaps)

        if n == 0:
            return {
                "session_id": session_id,
                "window": window,
                "step_count": 0,
                "s_trend": 0.0,
                "c_trend": 0.0,
                "i_trend": 0.0,
                "kappa_trend": 0.0,
                "regime_transitions": [],
                "transition_rate": 0.0,
                "dominant_regime": None,
                "current_regime": None,
                "alerts": [],
            }

        # Score trends (OLS slope per step)
        s_trend = round(self._linear_slope([s.s for s in snaps]), 4)
        c_trend = round(self._linear_slope([s.c for s in snaps]), 4)
        i_trend = round(self._linear_slope([s.i for s in snaps]), 4)
        kappa_trend = round(self._linear_slope([s.kappa for s in snaps]), 4)

        # Regime transitions
        transitions: List[Dict[str, Any]] = []
        for idx in range(1, n):
            prev, curr = snaps[idx - 1].regime, snaps[idx].regime
            if prev != curr:
                transitions.append({"step": idx, "from": prev, "to": curr})

        transition_rate = round(len(transitions) / max(n - 1, 1), 4)

        # Dominant and current regime
        regime_counts: Dict[str, int] = {}
        for snap in snaps:
            regime_counts[snap.regime] = regime_counts.get(snap.regime, 0) + 1
        dominant_regime = max(regime_counts, key=regime_counts.get) if regime_counts else None
        current_regime = snaps[-1].regime

        # Alerts
        alerts: List[str] = []
        if n >= 3 and s_trend <= self._SLOPE_DECLINING:
            alerts.append("declining_s")
        if n >= 3 and transition_rate >= self._TRANSITION_RATE_UNSTABLE:
            alerts.append("regime_instability")
        if "declining_s" in alerts and current_regime == "collapse":
            alerts.append("collapse_risk")
        if "declining_s" in alerts and current_regime == "hallucination-risk":
            alerts.append("hallucination_drift")

        return {
            "session_id": session_id,
            "window": window,
            "step_count": n,
            "s_trend": s_trend,
            "c_trend": c_trend,
            "i_trend": i_trend,
            "kappa_trend": kappa_trend,
            "regime_transitions": transitions,
            "transition_rate": transition_rate,
            "dominant_regime": dominant_regime,
            "current_regime": current_regime,
            "alerts": alerts,
        }
