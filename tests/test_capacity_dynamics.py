"""Tests for the dynamical capacity layer (capacity_dynamics)."""

import math

import pytest

from s_compass import CapacityDynamics, CapacityParams, SCompassGateway, StepInput
from s_compass.schemas import ScoreSnapshot


def _snap(c=0.5, i=0.5, kappa=1.0):
    return ScoreSnapshot(c=c, i=i, kappa=kappa, s=c + kappa * i, regime="creative-grounded")


# ---------------------------------------------------------------------------
# The law itself
# ---------------------------------------------------------------------------

def test_exact_integration_matches_closed_form():
    p = CapacityParams(recovery=0.2, consumption=1.5, kappa0=1.0)
    dyn = CapacityDynamics(p)
    load = 0.6
    rate = p.recovery + p.consumption * load
    k_ss = p.recovery * p.kappa0 / rate
    expected = k_ss + (1.0 - k_ss) * math.exp(-rate * 2.5)
    dyn._integrate(load, 2.5)
    assert dyn.kappa == pytest.approx(expected, abs=1e-12)


def test_steady_state_is_engine_law():
    dyn = CapacityDynamics(CapacityParams(recovery=0.1, consumption=2.0))
    assert dyn.steady_state(0.0) == pytest.approx(1.0)
    assert dyn.steady_state(0.45) == pytest.approx(0.1 / (0.1 + 0.9))


def test_sustained_load_drains_capacity():
    dyn = CapacityDynamics(CapacityParams(recovery=0.05, consumption=2.0))
    heavy = _snap(c=0.9, kappa=0.4)          # high distinction + high stress
    readings = [dyn.update(heavy)["kappa_dynamic"] for _ in range(6)]
    assert all(b < a for a, b in zip(readings, readings[1:]))
    assert readings[-1] < 0.3


def test_idle_time_restores_capacity():
    dyn = CapacityDynamics(CapacityParams(recovery=0.2, consumption=2.0))
    for _ in range(5):
        dyn.update(_snap(c=0.9, kappa=0.4))
    drained = dyn.kappa
    recovered = dyn.recover(10.0)
    assert recovered > drained
    assert dyn.recover(1000.0) == pytest.approx(1.0, abs=1e-6)


def test_state_remembers_what_the_estimator_forgets():
    # identical instantaneous snapshots, different histories → different κ_dyn
    fresh = CapacityDynamics(CapacityParams(recovery=0.05, consumption=2.0))
    tired = CapacityDynamics(CapacityParams(recovery=0.05, consumption=2.0))
    for _ in range(8):
        tired.update(_snap(c=0.9, kappa=0.4))
    same_step = _snap(c=0.5, i=0.6, kappa=0.9)
    k_fresh = fresh.update(same_step)["kappa_dynamic"]
    k_tired = tired.update(same_step)["kappa_dynamic"]
    assert k_tired < k_fresh


def test_s_dynamic_uses_the_stateful_kappa():
    dyn = CapacityDynamics(CapacityParams(recovery=0.05, consumption=2.0))
    snap = _snap(c=0.4, i=0.8, kappa=0.5)
    out = dyn.update(snap)
    assert out["s_dynamic"] == pytest.approx(
        round(snap.c + out["kappa_dynamic"] * snap.i, 4), abs=2e-4)


def test_load_blend_weights():
    p = CapacityParams(distinction_weight=1.0, stress_weight=0.0)
    assert CapacityDynamics(p).step_load(_snap(c=0.7, kappa=0.2)) == pytest.approx(0.7)
    p = CapacityParams(distinction_weight=0.0, stress_weight=1.0)
    assert CapacityDynamics(p).step_load(_snap(c=0.7, kappa=0.2)) == pytest.approx(0.8)


# ---------------------------------------------------------------------------
# Gateway integration
# ---------------------------------------------------------------------------

def _step(session_id, text):
    return StepInput(session_id=session_id, prompt="p", output_text=text)


def test_gateway_off_by_default():
    gw = SCompassGateway()
    gw.start_session("s1")
    result = gw.submit_step(_step("s1", "Some output text about a topic."))
    assert "capacity" not in result
    snap = gw.get_session_scores("s1")[-1]
    assert snap.kappa_dynamic is None and snap.s_dynamic is None


def test_gateway_tracks_capacity_when_enabled():
    gw = SCompassGateway(track_capacity=True)
    gw.start_session("s2")
    result = gw.submit_step(_step("s2", "A novel and detailed explanation."))
    assert "capacity" in result
    cap = result["capacity"]
    for key in ("kappa_dynamic", "s_dynamic", "load", "steady_state", "depleted"):
        assert key in cap
    snap = gw.get_session_scores("s2")[-1]
    assert snap.kappa_dynamic == cap["kappa_dynamic"]
    assert snap.s_dynamic == cap["s_dynamic"]


def test_gateway_capacity_declines_across_steps_and_recovers():
    gw = SCompassGateway(track_capacity=True,
                         capacity_params=CapacityParams(recovery=0.05,
                                                        consumption=2.0))
    gw.start_session("s3")
    k = []
    for n in range(4):
        r = gw.submit_step(_step("s3", f"Fresh idea number {n} with new words."))
        k.append(r["capacity"]["kappa_dynamic"])
    assert k[-1] < k[0]
    recovered = gw.recover_capacity("s3", dt=50.0)
    assert recovered is not None and recovered > k[-1]


def test_gateway_depletion_escalates_policy():
    gw = SCompassGateway(track_capacity=True,
                         capacity_params=CapacityParams(recovery=0.01,
                                                        consumption=5.0,
                                                        depleted_threshold=0.25))
    gw.start_session("s4")
    last = None
    for n in range(10):
        last = gw.submit_step(_step(
            "s4", f"Entirely different creative topic {n} words vary a lot."))
        if last["capacity"]["depleted"]:
            break
    assert last is not None and last["capacity"]["depleted"]
    assert last["policy"]["action"] == "reduce_load_and_retry"


def test_restarting_session_resets_capacity():
    gw = SCompassGateway(track_capacity=True,
                         capacity_params=CapacityParams(recovery=0.05,
                                                        consumption=3.0))
    gw.start_session("s5")
    for n in range(5):
        gw.submit_step(_step("s5", f"Another new angle {n} on the question."))
    drained = gw._capacity["s5"].kappa
    gw.start_session("s5")
    assert gw._capacity["s5"].kappa == pytest.approx(1.0)
    assert drained < 1.0


def test_recover_capacity_unknown_session_is_none():
    gw = SCompassGateway(track_capacity=True)
    assert gw.recover_capacity("nope", dt=1.0) is None
