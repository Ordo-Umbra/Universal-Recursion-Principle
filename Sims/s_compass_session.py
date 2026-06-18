"""
s_compass_session.py

Visualize an S Compass session timeline: the C / I / κ / S trajectory with the
state-regime and delta-form trajectory bands beneath it.

This demo builds an illustrative session that walks through a healthy phase, a
*diverging* turn (novelty rising while grounding falls — the level-S line stays
high while the trajectory band already flags the danger), and finally a
*contracting* slide into collapse.  The state regimes are assigned by the real
classifier and the trajectory band by the real SEngine, so only the raw
C / I / κ numbers are illustrative.

Run::

    python Sims/s_compass_session.py

Saves ``s_compass_session.png`` and prints the drift summary.
"""

import os
import sys

# Make the repo root importable when run as ``python Sims/s_compass_session.py``.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from s_compass import EvaluationStore, plot_session_from_store
from s_compass.scoring import classify_regime
from s_compass.schemas import ScoreSnapshot


# (C, I, κ) for each step of the illustrative arc.
ARC = [
    (0.60, 0.55, 0.98),  # healthy
    (0.70, 0.62, 0.99),  # expanding — both rising
    (0.80, 0.66, 0.98),  # still expanding
    (0.86, 0.45, 0.95),  # diverging — C up, I drops (grounding slips)
    (0.88, 0.30, 0.90),  # diverging continues toward hallucination
    (0.62, 0.24, 0.55),  # contracting — capacity buckling
    (0.34, 0.18, 0.22),  # collapse
]


def build_session(store: EvaluationStore, session_id: str = "demo") -> None:
    store.start_session(session_id)
    for c, i, kappa in ARC:
        regime = classify_regime(c, i, kappa)
        store.add_score(
            session_id,
            ScoreSnapshot(c=c, i=i, kappa=kappa, s=round(c + kappa * i, 4), regime=regime),
        )


def main() -> None:
    store = EvaluationStore()
    build_session(store, "demo")

    drift = store.drift_summary("demo", window=0)
    print("S Compass session drift summary")
    print(f"  steps              : {drift['step_count']}")
    print(f"  s_trend (level)    : {drift['s_trend']:+.4f}")
    print(f"  delta_s_mean       : {drift['delta_s_mean']:+.4f}")
    print(f"  cumulative_delta_s : {drift['cumulative_delta_s']:+.4f}")
    print(f"  current_trajectory : {drift['current_trajectory']}")
    print(f"  alerts             : {drift['alerts']}")

    plot_session_from_store(store, "demo", path="s_compass_session.png")
    print("\nSaved s_compass_session.png")


if __name__ == "__main__":
    main()
