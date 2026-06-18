"""
test_reach_care.py

Tests for the reach / care decomposition (Docs/The-Range.md) in
``s_compass/s_engine.py``.

reach = ΔC (capacity to act / model), care = ΔI (concern boundary).  Healthy
growth widens both together (balance → +1); the malignant verdict is reach
expanding while care collapses (the diverging geometry).
"""

import pytest

from s_compass import ReachCare, SEngine, reach_care, ScoreSnapshot


def _snap(c, i, kappa=0.9, regime="creative-grounded"):
    return ScoreSnapshot(c=c, i=i, kappa=kappa, s=round(c + kappa * i, 4), regime=regime)


class TestReachCare:
    def test_widening_together_is_balanced_and_benign(self):
        rc = reach_care(0.20, 0.20)
        assert rc.reach == 0.20 and rc.care == 0.20
        assert rc.balance == pytest.approx(1.0)
        assert rc.gap == 0.0
        assert rc.malignant is False

    def test_malignant_when_reach_outruns_collapsing_care(self):
        rc = reach_care(0.30, -0.30)
        assert rc.malignant is True
        # Pure divergence sits on the imbalance axis: balance ≈ 0.
        assert rc.balance == pytest.approx(0.0, abs=1e-9)
        assert rc.gap == pytest.approx(0.60)

    def test_withdrawing_is_not_malignant(self):
        # care grows while reach shrinks (consolidating) — not the verdict.
        rc = reach_care(-0.20, 0.20)
        assert rc.malignant is False

    def test_balanced_contraction_has_negative_balance(self):
        rc = reach_care(-0.20, -0.20)
        assert rc.balance == pytest.approx(-1.0)
        assert rc.malignant is False

    def test_malignant_requires_both_thresholds(self):
        # reach grows but care only dips inside the deadband → not malignant.
        assert reach_care(0.30, -0.01).malignant is False
        # care collapses but reach only inside the deadband → not malignant.
        assert reach_care(0.01, -0.30).malignant is False

    def test_zero_step_has_zero_balance(self):
        rc = reach_care(0.0, 0.0)
        assert rc.balance == 0.0
        assert rc.malignant is False

    def test_balance_is_bounded(self):
        for reach in (-0.4, -0.1, 0.0, 0.1, 0.4):
            for care in (-0.4, -0.1, 0.0, 0.1, 0.4):
                rc = reach_care(reach, care)
                assert -1.0 <= rc.balance <= 1.0

    def test_custom_deadband(self):
        # With a wider deadband, a small reach/care no longer counts.
        assert reach_care(0.08, -0.08, deadband=0.10).malignant is False
        assert reach_care(0.12, -0.12, deadband=0.10).malignant is True


class TestEngineReachCareTrajectory:
    def test_trajectory_skips_initial_and_flags_malignancy(self):
        eng = SEngine()
        # step 0: seed; step 1: reach up, care down → malignant.
        eng.assess_snapshot(_snap(0.50, 0.60))
        eng.assess_snapshot(_snap(0.75, 0.35))
        rc_series = eng.reach_care_trajectory()
        assert len(rc_series) == 1  # initial step omitted
        assert isinstance(rc_series[0], ReachCare)
        assert rc_series[0].malignant is True
        assert rc_series[0].reach > 0 and rc_series[0].care < 0

    def test_trajectory_matches_recursion_deltas(self):
        eng = SEngine()
        eng.assess_snapshot(_snap(0.40, 0.40))
        m = eng.assess_snapshot(_snap(0.60, 0.55))
        rc = eng.reach_care_trajectory()[0]
        assert rc.reach == m.delta_c
        assert rc.care == m.delta_i

    def test_empty_engine_has_empty_trajectory(self):
        assert SEngine().reach_care_trajectory() == []
