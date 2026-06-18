"""
test_visualize.py

Tests for the S Compass session-timeline visualization
(``s_compass/visualize.py``).  Uses the headless Agg backend so no display
is required.
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from s_compass import (
    EvaluationStore,
    ScoreSnapshot,
    plot_session,
    plot_session_from_store,
)
from s_compass.visualize import STATE_REGIME_COLORS, TRAJECTORY_COLORS


def _snap(c, i, kappa=0.9, regime="creative-grounded"):
    return ScoreSnapshot(c=c, i=i, kappa=kappa, s=round(c + kappa * i, 4), regime=regime)


_ARC = [
    _snap(0.50, 0.50, regime="creative-grounded"),
    _snap(0.70, 0.62, regime="creative-grounded"),
    _snap(0.86, 0.30, kappa=0.9, regime="hallucination-risk"),
    _snap(0.34, 0.18, kappa=0.2, regime="collapse"),
]


class TestPlotSession:
    def test_returns_figure_with_three_panels(self):
        fig = plot_session(_ARC)
        # Three stacked panels: lines, state band, trajectory band.
        assert len(fig.axes) == 3
        plt.close(fig)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            plot_session([])

    def test_single_step(self):
        fig = plot_session([_snap(0.6, 0.5)])
        assert fig is not None
        plt.close(fig)

    def test_saves_file(self, tmp_path):
        out = tmp_path / "session.png"
        fig = plot_session(_ARC, path=str(out))
        assert out.exists() and out.stat().st_size > 0
        plt.close(fig)

    def test_title_is_applied(self):
        fig = plot_session(_ARC, title="my session")
        assert fig.axes[0].get_title() == "my session"
        plt.close(fig)

    def test_colour_maps_cover_all_regimes(self):
        # Every state/trajectory label the system can emit must have a colour.
        assert set(STATE_REGIME_COLORS) == {
            "creative-grounded", "rigid", "hallucination-risk", "collapse",
        }
        assert set(TRAJECTORY_COLORS) == {
            "expanding", "consolidating", "diverging",
            "contracting", "steady", "initial",
        }


class TestPlotSessionFromStore:
    def test_from_store(self, tmp_path):
        store = EvaluationStore()
        store.start_session("s")
        for snap in _ARC:
            store.add_score("s", snap)
        out = tmp_path / "s.png"
        fig = plot_session_from_store(store, "s", path=str(out))
        assert out.exists()
        plt.close(fig)

    def test_missing_session_raises(self):
        store = EvaluationStore()
        store.start_session("empty")
        with pytest.raises(KeyError):
            plot_session_from_store(store, "empty")
