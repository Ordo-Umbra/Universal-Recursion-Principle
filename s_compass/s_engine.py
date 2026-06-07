"""
s_engine.py

Delta-form S-Engine for S Compass — the recursion-faithful counterpart to
the level-form scoring engine (``scoring.py``).

Two complementary readings of the URP S-functional live in this codebase:

* **Level form** (``scoring.py``): ``S = C + κI`` answers *"where is the
  system now?"*  — the absolute state of distinction, integration, and
  capacity at a single step.
* **Delta form** (this module): ``ΔS = ΔC + κ ΔI`` answers *"where is the
  system heading?"* — the step-over-step *recursion*, i.e. the rate at
  which distinction and integration are growing or decaying.

The delta form is the discrete derivative of the level form.  Crucially,
both forms share the **same** canonical C and I estimators: this engine
calls :func:`s_compass.scoring.score_step` (or reuses an already-computed
:class:`~s_compass.schemas.ScoreSnapshot`) so there is exactly one
definition of distinction and integration across the whole system.  The
only difference is whether we report the value or its change.

Where the level-form regimes describe a *state*
(``rigid / creative-grounded / hallucination-risk / collapse``), the
delta-form regimes describe a *trajectory*:

* ``expanding``      — ΔC > 0 and ΔI > 0: distinction and integration both
  growing (healthy recursion)
* ``consolidating``  — ΔC < 0 and ΔI > 0: shedding novelty while gaining
  coherence (converging / rigidifying trajectory)
* ``diverging``      — ΔC > 0 and ΔI < 0: novelty rising while coherence
  falls (runaway / hallucination trajectory)
* ``contracting``    — ΔC < 0 and ΔI < 0: both shrinking (collapse
  trajectory)
* ``steady``         — both changes inside the deadband (a fixed point of
  the recursion)
* ``initial``        — the first step of a session, which has no predecessor
  to difference against
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .schemas import ScoreSnapshot, StepInput
from .scoring import score_step


# ---------------------------------------------------------------------------
# Recursion metrics
# ---------------------------------------------------------------------------

@dataclass
class RecursionMetrics:
    """Delta-form metrics for a single inference step.

    Combines the level-form snapshot (``c``, ``i``, ``kappa``, ``s_level``)
    with the recursion quantities (``delta_c``, ``delta_i``, ``delta_s``)
    and a trajectory ``regime`` label.
    """

    c: float           # level-form distinction at this step
    i: float           # level-form integration at this step
    kappa: float       # usable capacity at this step
    s_level: float     # level-form S = C + κI (for cross-reference)
    delta_c: float     # ΔC = Cₜ − Cₜ₋₁
    delta_i: float     # ΔI = Iₜ − Iₜ₋₁
    delta_s: float     # ΔS = ΔC + κ ΔI
    regime: str        # trajectory regime (see module docstring)
    is_initial: bool   # True for the first step (no predecessor)
    trace_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Trajectory regime classifier
# ---------------------------------------------------------------------------

def classify_recursion(
    delta_c: float,
    delta_i: float,
    is_initial: bool = False,
    deadband: float = 0.05,
) -> str:
    """Classify the recursion *trajectory* from ΔC and ΔI.

    The ``deadband`` defines a neutral zone around zero: changes smaller in
    magnitude than ``deadband`` are treated as "no change", which prevents
    estimator noise from being read as a real trend.

    Returns one of ``"initial"``, ``"steady"``, ``"expanding"``,
    ``"consolidating"``, ``"diverging"``, or ``"contracting"``.
    """
    if is_initial:
        return "initial"

    eps = deadband
    c_up, c_dn = delta_c > eps, delta_c < -eps
    i_up, i_dn = delta_i > eps, delta_i < -eps

    # Both components inside the deadband → a fixed point of the recursion.
    if not (c_up or c_dn) and not (i_up or i_dn):
        return "steady"

    # Both components clearly active.
    if c_up and i_up:
        return "expanding"
    if c_dn and i_dn:
        return "contracting"
    if c_up and i_dn:
        return "diverging"
    if c_dn and i_up:
        return "consolidating"

    # Exactly one component is inside the deadband: classify by the active one.
    if i_up or c_up:
        return "expanding"
    return "contracting"


# ---------------------------------------------------------------------------
# S-Engine
# ---------------------------------------------------------------------------

class SEngine:
    """Stateful delta-form engine that tracks recursion across a session.

    Feed it steps (or pre-computed snapshots) in order; each call returns
    the :class:`RecursionMetrics` for that step relative to the previous
    one.  Use one engine per session (or call :meth:`reset` between
    sessions).

    Parameters
    ----------
    kappa:
        Optional fixed capacity override for the ΔS combination.  When
        ``None`` (the default) the per-step estimated κ from the score
        snapshot is used, so capacity stress modulates the recursion just
        as it does in the level form.
    deadband:
        Neutral zone for the trajectory classifier (see
        :func:`classify_recursion`).
    """

    def __init__(self, kappa: Optional[float] = None, deadband: float = 0.05) -> None:
        self.kappa_override = kappa
        self.deadband = deadband
        self._prev_c: Optional[float] = None
        self._prev_i: Optional[float] = None
        self.history: List[RecursionMetrics] = []

    def reset(self) -> None:
        """Clear all accumulated state so the engine can be reused."""
        self._prev_c = None
        self._prev_i = None
        self.history = []

    def assess_step(self, step: StepInput) -> RecursionMetrics:
        """Score ``step`` with the canonical engine, then compute deltas.

        Use this for standalone analysis.  When the caller already has a
        :class:`ScoreSnapshot` (e.g. the gateway), prefer
        :meth:`assess_snapshot` to avoid scoring twice.
        """
        return self.assess_snapshot(score_step(step))

    def assess_snapshot(self, snap: ScoreSnapshot) -> RecursionMetrics:
        """Compute delta-form metrics from an already-computed snapshot."""
        c, i, kappa, s_level = snap.c, snap.i, snap.kappa, snap.s

        is_initial = self._prev_c is None
        if is_initial:
            delta_c = 0.0
            delta_i = 0.0
        else:
            delta_c = c - self._prev_c
            delta_i = i - self._prev_i

        k = self.kappa_override if self.kappa_override is not None else kappa
        delta_s = delta_c + k * delta_i
        regime = classify_recursion(
            delta_c, delta_i, is_initial=is_initial, deadband=self.deadband
        )

        metrics = RecursionMetrics(
            c=c,
            i=i,
            kappa=kappa,
            s_level=s_level,
            delta_c=round(delta_c, 4),
            delta_i=round(delta_i, 4),
            delta_s=round(delta_s, 4),
            regime=regime,
            is_initial=is_initial,
            trace_id=snap.trace_id,
        )

        self._prev_c = c
        self._prev_i = i
        self.history.append(metrics)
        return metrics

    def trajectory(self) -> List[RecursionMetrics]:
        """Return the full per-step recursion history."""
        return list(self.history)
