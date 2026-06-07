"""
test_s_engine.py

Tests for the delta-form S-Engine (``s_compass/s_engine.py``).

The engine computes the recursion functional ΔS = ΔC + κ ΔI from the
step-over-step change in the canonical C and I estimators, and classifies
the trajectory (expanding / consolidating / diverging / contracting /
steady / initial).

The trajectory *math* is unit-tested with hand-built snapshots so the
delta logic is isolated from estimator noise; the gateway *integration*
is tested end-to-end with real steps.
"""

import pytest

from s_compass.schemas import Claim, RetrievedChunk, ScoreSnapshot, StepInput
from s_compass.s_engine import RecursionMetrics, SEngine, classify_recursion
from s_compass.gateway import SCompassGateway


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _snap(c, i, kappa=1.0, regime="creative-grounded", trace_id="t"):
    """Build a ScoreSnapshot with a consistent level-form S = C + κI."""
    return ScoreSnapshot(
        c=c, i=i, kappa=kappa, s=round(c + kappa * i, 4),
        regime=regime, trace_id=trace_id,
    )


def _step(output_text, **kw):
    return StepInput(session_id="sess", prompt="p", output_text=output_text, **kw)


# ---------------------------------------------------------------------------
# Regression: the module must import (it was broken dead code before)
# ---------------------------------------------------------------------------

def test_module_imports_and_exports():
    import s_compass

    assert s_compass.SEngine is SEngine
    assert s_compass.classify_recursion is classify_recursion
    assert s_compass.RecursionMetrics is RecursionMetrics


# ---------------------------------------------------------------------------
# classify_recursion — trajectory branches
# ---------------------------------------------------------------------------

class TestClassifyRecursion:
    def test_initial(self):
        assert classify_recursion(0.0, 0.0, is_initial=True) == "initial"
        # is_initial wins even when deltas are non-zero
        assert classify_recursion(0.9, -0.9, is_initial=True) == "initial"

    def test_steady_inside_deadband(self):
        assert classify_recursion(0.01, -0.02, deadband=0.05) == "steady"

    def test_expanding(self):
        assert classify_recursion(0.3, 0.3) == "expanding"

    def test_contracting(self):
        assert classify_recursion(-0.3, -0.3) == "contracting"

    def test_diverging_novelty_up_coherence_down(self):
        assert classify_recursion(0.3, -0.3) == "diverging"

    def test_consolidating_novelty_down_coherence_up(self):
        assert classify_recursion(-0.3, 0.3) == "consolidating"

    def test_one_component_in_deadband(self):
        # C active up, I neutral → expanding
        assert classify_recursion(0.3, 0.0) == "expanding"
        # C active down, I neutral → contracting
        assert classify_recursion(-0.3, 0.0) == "contracting"
        # I active up, C neutral → expanding
        assert classify_recursion(0.0, 0.3) == "expanding"
        # I active down, C neutral → contracting
        assert classify_recursion(0.0, -0.3) == "contracting"


# ---------------------------------------------------------------------------
# SEngine.assess_snapshot — delta math
# ---------------------------------------------------------------------------

class TestAssessSnapshot:
    def test_first_step_is_initial_with_zero_deltas(self):
        eng = SEngine()
        m = eng.assess_snapshot(_snap(0.5, 0.5))
        assert m.is_initial is True
        assert m.delta_c == 0.0
        assert m.delta_i == 0.0
        assert m.delta_s == 0.0
        assert m.regime == "initial"
        # Level-form values are passed through.
        assert m.c == 0.5 and m.i == 0.5 and m.s_level == 1.0

    def test_expanding_trajectory(self):
        eng = SEngine()
        eng.assess_snapshot(_snap(0.2, 0.2))
        m = eng.assess_snapshot(_snap(0.8, 0.8, kappa=1.0))
        assert m.is_initial is False
        assert m.delta_c == pytest.approx(0.6)
        assert m.delta_i == pytest.approx(0.6)
        assert m.delta_s == pytest.approx(1.2)  # 0.6 + 1.0 * 0.6
        assert m.regime == "expanding"

    def test_contracting_trajectory(self):
        eng = SEngine()
        eng.assess_snapshot(_snap(0.8, 0.8))
        m = eng.assess_snapshot(_snap(0.2, 0.2))
        assert m.delta_s == pytest.approx(-1.2)
        assert m.regime == "contracting"

    def test_diverging_trajectory(self):
        eng = SEngine()
        eng.assess_snapshot(_snap(0.3, 0.7))
        m = eng.assess_snapshot(_snap(0.8, 0.2))  # C up, I down
        assert m.delta_c == pytest.approx(0.5)
        assert m.delta_i == pytest.approx(-0.5)
        assert m.regime == "diverging"

    def test_consolidating_trajectory(self):
        eng = SEngine()
        eng.assess_snapshot(_snap(0.8, 0.2))
        m = eng.assess_snapshot(_snap(0.3, 0.7))  # C down, I up
        assert m.regime == "consolidating"

    def test_steady_trajectory(self):
        eng = SEngine()
        eng.assess_snapshot(_snap(0.5, 0.5))
        m = eng.assess_snapshot(_snap(0.51, 0.49))  # both within deadband
        assert m.regime == "steady"

    def test_delta_s_uses_per_step_kappa(self):
        eng = SEngine()
        eng.assess_snapshot(_snap(0.0, 0.0, kappa=0.5))
        m = eng.assess_snapshot(_snap(0.4, 0.4, kappa=0.5))
        # ΔS = ΔC + κ ΔI = 0.4 + 0.5 * 0.4 = 0.6
        assert m.delta_s == pytest.approx(0.6)
        assert m.kappa == 0.5

    def test_kappa_override(self):
        eng = SEngine(kappa=2.0)
        eng.assess_snapshot(_snap(0.0, 0.0, kappa=0.5))
        m = eng.assess_snapshot(_snap(0.4, 0.4, kappa=0.5))
        # Override forces κ = 2.0: ΔS = 0.4 + 2.0 * 0.4 = 1.2
        assert m.delta_s == pytest.approx(1.2)
        # The estimated κ is still reported on the metrics.
        assert m.kappa == 0.5

    def test_history_and_reset(self):
        eng = SEngine()
        eng.assess_snapshot(_snap(0.2, 0.2))
        eng.assess_snapshot(_snap(0.5, 0.5))
        assert len(eng.trajectory()) == 2
        eng.reset()
        assert eng.trajectory() == []
        # After reset the next step is initial again.
        m = eng.assess_snapshot(_snap(0.9, 0.9))
        assert m.is_initial is True


# ---------------------------------------------------------------------------
# SEngine.assess_step — real estimators
# ---------------------------------------------------------------------------

class TestAssessStep:
    def test_assess_step_matches_score_step(self):
        from s_compass.scoring import score_step

        eng = SEngine()
        step = _step("The recursion principle unifies distinction and integration.")
        snap = score_step(step)
        m = eng.assess_step(step)
        # First step: level-form values mirror score_step exactly.
        assert m.c == snap.c
        assert m.i == snap.i
        assert m.kappa == snap.kappa
        assert m.s_level == snap.s
        assert m.is_initial is True


# ---------------------------------------------------------------------------
# Gateway integration — opt-in recursion block
# ---------------------------------------------------------------------------

class TestGatewayIntegration:
    def test_recursion_absent_by_default(self):
        gw = SCompassGateway()
        gw.start_session("sess")
        result = gw.submit_step(_step("A first novel grounded answer."))
        assert "recursion" not in result

    def test_recursion_present_when_enabled(self):
        gw = SCompassGateway(track_recursion=True)
        gw.start_session("sess")
        r1 = gw.submit_step(_step("A first novel grounded answer about recursion."))
        assert "recursion" in r1
        assert r1["recursion"]["is_initial"] is True
        assert r1["recursion"]["delta_s"] == 0.0

        r2 = gw.submit_step(
            _step("An entirely different second response exploring new territory.")
        )
        assert r2["recursion"]["is_initial"] is False
        # s_level in the recursion block mirrors the level-form S.
        assert r2["recursion"]["s_level"] == r2["scores"]["s"]

    def test_existing_result_shape_unchanged_when_disabled(self):
        gw = SCompassGateway()
        gw.start_session("sess")
        result = gw.submit_step(_step("Some answer."))
        assert set(result["scores"].keys()) == {"c", "i", "kappa", "s"}
        assert "regime" in result and "policy" in result

    def test_restarting_session_resets_recursion(self):
        gw = SCompassGateway(track_recursion=True)
        gw.start_session("sess")
        gw.submit_step(_step("First answer."))
        # Restart the same session id → deltas start fresh.
        gw.start_session("sess")
        r = gw.submit_step(_step("Fresh start answer."))
        assert r["recursion"]["is_initial"] is True

    def test_per_session_isolation(self):
        gw = SCompassGateway(track_recursion=True)
        gw.start_session("a")
        gw.start_session("b")
        gw.submit_step(StepInput(session_id="a", prompt="p", output_text="Answer A one."))
        rb = gw.submit_step(
            StepInput(session_id="b", prompt="p", output_text="Answer B one.")
        )
        # Session b's first step is still initial despite a having a step.
        assert rb["recursion"]["is_initial"] is True
