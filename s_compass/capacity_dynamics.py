"""
capacity_dynamics.py

Dynamical κ — a *stateful* capacity for S Compass sessions.

The κ estimator (``estimators.estimate_kappa`` and friends) is an
instantaneous stress readout: context pressure, latency dispersion, tool
failures, read fresh at every step and forgotten immediately.  But the URP
capacity is not a readout — it is a *field with dynamics*, consumed by
distinction load and regenerating with slack:

    dκ/dt = r·(κ₀ − κ) − c·load·κ

This is the same law the Project-Genesis engine integrates for its capacity
field, whose measured consequences (recall failing before coherence, the
persistence↔plasticity crossover in the recovery rate, capacity-bound
S-optima relocating to criticality — verified across two substrates by the
criticality-transplant experiment) all depend on κ carrying *state* between
steps.  With a stateful κ those results become testable predictions about
sessions: sustained heavy-load turns should deplete capacity faster than any
single-step stress reading shows, and idle time should genuinely restore it.

The ODE is linear in κ at fixed load, so each step is integrated **exactly**
(no stability constraints)::

    κ(t+Δt) = κ_ss + (κ(t) − κ_ss)·exp(−(r + c·load)·Δt),
    κ_ss    = r·κ₀ / (r + c·load)

Load is a blend of the two things a step demands of the capacity budget:
the *distinction* being produced (the C score — the URP semantics: capacity
is consumed by making distinctions) and the *stress* the static κ estimator
already measures (1 − κ_static).  Both weights are configurable and stated.

The level-form score ``S = C + κ_static·I`` is untouched — every existing
benchmark and threshold keeps its meaning.  The dynamical reading is
reported alongside as ``kappa_dynamic`` and ``s_dynamic = C + κ_dyn·I``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Optional

from .schemas import ScoreSnapshot

__all__ = ["CapacityParams", "CapacityDynamics"]


@dataclass
class CapacityParams:
    """Parameters of the capacity law and the load blend.

    ``recovery`` (r), ``consumption`` (c), and ``kappa0`` (κ₀) are the
    engine's constants; ``distinction_weight`` / ``stress_weight`` set the
    load blend ``load = w_d·C + w_s·(1 − κ_static)``.  Defaults are stated
    conventions, not measurements — fit ``r`` and ``c`` per deployment.
    """

    recovery: float = 0.15
    consumption: float = 1.0
    kappa0: float = 1.0
    distinction_weight: float = 0.5
    stress_weight: float = 0.5
    depleted_threshold: float = 0.25


class CapacityDynamics:
    """Per-session dynamical capacity: the URP κ law with state.

    One instance per session.  Call :meth:`update` with each step's score
    snapshot (Δt in *step units*, default 1.0 per step), and :meth:`recover`
    for idle periods between turns.  ``kappa`` is the current state.
    """

    def __init__(self, params: Optional[CapacityParams] = None) -> None:
        self.params = params or CapacityParams()
        self.kappa: float = self.params.kappa0
        self.steps: int = 0

    # -- the law -------------------------------------------------------------

    def step_load(self, snapshot: ScoreSnapshot) -> float:
        """The capacity load of a step: distinction produced + stress carried."""
        p = self.params
        return (p.distinction_weight * snapshot.c
                + p.stress_weight * (1.0 - snapshot.kappa))

    def steady_state(self, load: float) -> float:
        """κ_ss = r·κ₀ / (r + c·load) — the fixed point at constant load."""
        p = self.params
        return p.recovery * p.kappa0 / (p.recovery + p.consumption * load)

    def _integrate(self, load: float, dt: float) -> float:
        """Exact update of the linear ODE over ``dt`` at constant ``load``."""
        p = self.params
        rate = p.recovery + p.consumption * load
        k_ss = p.recovery * p.kappa0 / rate
        self.kappa = k_ss + (self.kappa - k_ss) * math.exp(-rate * dt)
        return self.kappa

    # -- public API ----------------------------------------------------------

    def update(self, snapshot: ScoreSnapshot, dt: float = 1.0) -> Dict[str, float]:
        """Consume/regenerate capacity for one scored step; return the reading.

        Returns ``kappa_dynamic`` (the post-step state), ``s_dynamic``
        (``C + κ_dyn·I``), the step's ``load``, the ``steady_state`` that
        load implies, and ``depleted`` (state below the stated threshold).
        """
        load = self.step_load(snapshot)
        kappa = self._integrate(load, dt)
        self.steps += 1
        return {
            "kappa_dynamic": round(kappa, 4),
            "s_dynamic": round(snapshot.c + kappa * snapshot.i, 4),
            "load": round(load, 4),
            "steady_state": round(self.steady_state(load), 4),
            "depleted": kappa < self.params.depleted_threshold,
        }

    def recover(self, dt: float) -> float:
        """Idle recovery: integrate the law with zero load for ``dt`` step-units.

        A session resumed after a break returns with genuinely restored
        capacity — the state the instantaneous estimator cannot carry.
        """
        return self._integrate(0.0, dt)
