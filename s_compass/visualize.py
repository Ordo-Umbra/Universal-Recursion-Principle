"""
visualize.py

Session-timeline visualization for S Compass.

Renders a session's C / I / κ / S trajectory together with two bands beneath
it — the **state regime** (level form: where each step *is*) and the
**trajectory regime** (delta form: where each step is *heading*) — so an
analyst can see at a glance where a session was healthy, where it diverged,
and where it collapsed.

matplotlib is imported lazily inside the plotting functions so that importing
``s_compass`` does not require a plotting backend.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from .schemas import ScoreSnapshot
from .s_engine import SEngine
from .store import EvaluationStore


# Colours shared by both bands: the trajectory regimes are deliberately given
# the same colour as the state regime they drift toward (see
# Docs/Level-and-Delta-Forms.md §4).
STATE_REGIME_COLORS = {
    "creative-grounded": "#2e7d32",   # green
    "rigid": "#1565c0",               # blue
    "hallucination-risk": "#ef6c00",  # orange
    "collapse": "#c62828",            # red
}

TRAJECTORY_COLORS = {
    "expanding": "#2e7d32",      # → creative-grounded
    "consolidating": "#1565c0",  # → rigid
    "diverging": "#ef6c00",      # → hallucination-risk
    "contracting": "#c62828",    # → collapse
    "steady": "#9e9e9e",         # fixed point
    "initial": "#e0e0e0",        # first step, no predecessor
}

_DEFAULT_COLOR = "#9e9e9e"


def _trajectory_regimes(snapshots: Sequence[ScoreSnapshot]) -> List[str]:
    """Per-step trajectory labels, computed via the shared :class:`SEngine`."""
    engine = SEngine()
    return [engine.assess_snapshot(s).regime for s in snapshots]


def _draw_band(ax, labels: Sequence[str], colors: dict, ylabel: str) -> None:
    """Draw a horizontal colour strip, one cell per step, with a side legend."""
    from matplotlib.patches import Patch

    for idx, label in enumerate(labels):
        ax.axvspan(idx - 0.5, idx + 0.5, color=colors.get(label, _DEFAULT_COLOR))
    ax.set_yticks([])
    ax.set_xlim(-0.5, len(labels) - 0.5)
    ax.set_ylabel(ylabel, rotation=0, ha="right", va="center", fontsize=8)

    # Legend lists only the labels actually present, in first-seen order.
    present = list(dict.fromkeys(labels))
    handles = [Patch(color=colors.get(l, _DEFAULT_COLOR), label=l) for l in present]
    ax.legend(
        handles=handles,
        loc="center left",
        bbox_to_anchor=(1.005, 0.5),
        fontsize=7,
        frameon=False,
    )


def plot_session(
    snapshots: Sequence[ScoreSnapshot],
    *,
    title: str = "S Compass session",
    path: Optional[str] = None,
):
    """Plot a session timeline and return the matplotlib ``Figure``.

    Parameters
    ----------
    snapshots:
        The session's score snapshots in step order (e.g. from
        :meth:`EvaluationStore.get_scores`).
    title:
        Figure title.
    path:
        When given, the figure is saved to this path at 120 dpi.

    The figure has three stacked panels sharing the step axis: the C / I / κ / S
    lines on top, the state-regime band, and the trajectory-regime band.
    """
    if not snapshots:
        raise ValueError("plot_session requires at least one snapshot")

    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec

    n = len(snapshots)
    steps = list(range(n))
    c = [s.c for s in snapshots]
    i = [s.i for s in snapshots]
    kappa = [s.kappa for s in snapshots]
    s_tot = [s.s for s in snapshots]
    states = [s.regime for s in snapshots]
    trajectory = _trajectory_regimes(snapshots)

    fig = plt.figure(figsize=(max(8.0, n * 0.7), 6.0))
    gs = GridSpec(3, 1, height_ratios=[6, 1, 1], hspace=0.18, figure=fig)
    ax = fig.add_subplot(gs[0])
    ax_state = fig.add_subplot(gs[1], sharex=ax)
    ax_traj = fig.add_subplot(gs[2], sharex=ax)

    ax.plot(steps, s_tot, marker="o", lw=2.0, color="#212121", label="S = C + κI")
    ax.plot(steps, c, marker=".", color=STATE_REGIME_COLORS["creative-grounded"], label="C (distinction)")
    ax.plot(steps, i, marker=".", color=STATE_REGIME_COLORS["rigid"], label="I (integration)")
    ax.plot(steps, kappa, marker=".", color="#9c27b0", label="κ (capacity)")
    ax.set_ylabel("score")
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelbottom=False)

    _draw_band(ax_state, states, STATE_REGIME_COLORS, "state")
    ax_state.tick_params(labelbottom=False)
    _draw_band(ax_traj, trajectory, TRAJECTORY_COLORS, "trajectory")
    ax_traj.set_xlabel("step")
    ax_traj.set_xticks(steps)

    if path:
        fig.savefig(path, dpi=120, bbox_inches="tight")
    return fig


def plot_session_from_store(
    store: EvaluationStore,
    session_id: str,
    *,
    title: Optional[str] = None,
    path: Optional[str] = None,
):
    """Plot a session held in *store* by ``session_id``.

    Raises ``KeyError`` if the session has no recorded scores.
    """
    snapshots = store.get_scores(session_id)
    if not snapshots:
        raise KeyError(f"no scores recorded for session {session_id!r}")
    return plot_session(
        snapshots,
        title=title or f"S Compass session: {session_id}",
        path=path,
    )
