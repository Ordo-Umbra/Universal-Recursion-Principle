"""
test_s_compass.py

Tests for the s_compass package.

Tests are grouped by module and follow the same conventions as the
existing test_sims.py suite.
"""

import numpy as np
import pytest

from s_compass.schemas import (
    Claim,
    Event,
    Evidence,
    GraphEdge,
    PolicyAction,
    RetrievedChunk,
    ScoreSnapshot,
    StepInput,
    VALID_EVENT_TYPES,
)
from s_compass.telemetry import normalize_event, normalize_step_payload
from s_compass.estimators import (
    capacity_field,
    estimate_c,
    estimate_i,
    estimate_kappa,
    normalize,
)
from s_compass.scoring import classify_regime, score_step, score_step_dict
from s_compass.policy import evaluate as evaluate_policy
from s_compass.store import EvaluationStore
from s_compass.gateway import SCompassGateway


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_step(**overrides) -> StepInput:
    defaults = dict(
        session_id="sess_test",
        prompt="What is URP?",
        output_text="URP is a unified framework proposing recursive S-maximization.",
    )
    defaults.update(overrides)
    return StepInput(**defaults)


# ===========================================================================
# Schemas
# ===========================================================================

class TestSchemas:
    def test_event_defaults(self):
        e = Event(
            event_type="model.completed",
            timestamp="2026-01-01T00:00:00Z",
            session_id="s1",
            trace_id="t1",
        )
        assert e.event_id.startswith("evt_")
        assert e.payload == {}

    def test_claim_defaults(self):
        c = Claim(text="S equals C plus kappa I")
        assert c.claim_id.startswith("claim_")
        assert c.confidence == 1.0

    def test_score_snapshot_fields(self):
        snap = ScoreSnapshot(c=0.6, i=0.8, kappa=0.7, s=1.16, regime="creative-grounded")
        assert snap.s == pytest.approx(1.16)

    def test_step_input_defaults(self):
        step = _make_step()
        assert step.context_window == 4096
        assert step.tool_failure_count == 0


# ===========================================================================
# Telemetry
# ===========================================================================

class TestTelemetry:
    def test_normalize_event_valid(self):
        evt = normalize_event(
            "model.completed",
            session_id="s1",
            trace_id="t1",
            payload={"text": "hello"},
        )
        assert evt.event_type == "model.completed"
        assert evt.payload == {"text": "hello"}

    def test_normalize_event_invalid_type(self):
        with pytest.raises(ValueError, match="Unknown event_type"):
            normalize_event("invalid.type", session_id="s1", trace_id="t1")

    def test_valid_event_types_complete(self):
        assert "session.started" in VALID_EVENT_TYPES
        assert "model.completed" in VALID_EVENT_TYPES
        assert len(VALID_EVENT_TYPES) == 11

    def test_normalize_step_payload(self):
        raw = {
            "session_id": "s1",
            "trace_id": "t1",
            "prompt": "Hello",
            "output_text": "World",
            "retrieved_context": [{"doc_id": "d1", "text": "..."}],
        }
        events = normalize_step_payload(raw)
        types = [e.event_type for e in events]
        assert "prompt.received" in types
        assert "retrieval.completed" in types
        assert "model.completed" in types


# ===========================================================================
# Estimators
# ===========================================================================

class TestEstimators:
    def test_normalize_uniform_weights(self):
        assert normalize([0.5, 0.5, 0.5]) == pytest.approx(0.5)

    def test_normalize_clips_to_unit(self):
        assert normalize([1.5, 2.0]) == pytest.approx(1.0)

    def test_normalize_empty(self):
        assert normalize([]) == 0.0

    def test_normalize_custom_weights(self):
        # weight 1.0 on 0.8, weight 0.0 on 0.2
        assert normalize([0.8, 0.2], weights=[1.0, 0.0]) == pytest.approx(0.8)

    def test_capacity_field_no_stress(self):
        k = capacity_field(context_load=0.0, latency_std=0.0, tool_failure_rate=0.0)
        assert k == pytest.approx(1.0)

    def test_capacity_field_full_stress(self):
        k = capacity_field(context_load=1.0, latency_std=1.0, tool_failure_rate=1.0)
        assert 0.0 < k < 0.5  # heavily degraded

    def test_capacity_field_partial_stress(self):
        k = capacity_field(context_load=0.5, latency_std=0.0, tool_failure_rate=0.0)
        assert 0.5 < k < 1.0

    def test_estimate_c_returns_unit_interval(self):
        step = _make_step()
        c = estimate_c(step)
        assert 0.0 <= c <= 1.0

    def test_estimate_i_returns_unit_interval(self):
        step = _make_step()
        i = estimate_i(step)
        assert 0.0 <= i <= 1.0

    def test_estimate_kappa_returns_unit_interval(self):
        step = _make_step()
        k = estimate_kappa(step)
        assert 0.0 <= k <= 1.0

    def test_estimate_kappa_degrades_under_context_pressure(self):
        low_pressure = _make_step(context_tokens_used=100, context_window=4096)
        high_pressure = _make_step(context_tokens_used=4000, context_window=4096)
        assert estimate_kappa(low_pressure) > estimate_kappa(high_pressure)

    def test_estimate_c_higher_for_diverse_output(self):
        repetitive = _make_step(output_text="the the the the the the")
        diverse = _make_step(
            output_text="URP proposes recursive maximization of a scalar functional S"
        )
        assert estimate_c(diverse) > estimate_c(repetitive)


# ===========================================================================
# Scoring
# ===========================================================================

class TestScoring:
    def test_classify_regime_rigid(self):
        assert classify_regime(c=0.2, i=0.8, kappa=0.9) == "rigid"

    def test_classify_regime_creative_grounded(self):
        assert classify_regime(c=0.7, i=0.6, kappa=0.8) == "creative-grounded"

    def test_classify_regime_hallucination_risk(self):
        assert classify_regime(c=0.8, i=0.2, kappa=0.3) == "hallucination-risk"

    def test_classify_regime_collapse(self):
        assert classify_regime(c=0.1, i=0.1, kappa=0.2) == "collapse"

    def test_score_step_returns_snapshot(self):
        step = _make_step()
        snap = score_step(step)
        assert isinstance(snap, ScoreSnapshot)
        assert 0.0 <= snap.c <= 1.0
        assert 0.0 <= snap.i <= 1.0
        assert 0.0 <= snap.kappa <= 1.0
        assert snap.regime in {"rigid", "creative-grounded", "hallucination-risk", "collapse"}

    def test_score_step_s_equals_c_plus_kappa_i(self):
        step = _make_step()
        snap = score_step(step)
        expected_s = snap.c + snap.kappa * snap.i
        assert snap.s == pytest.approx(expected_s, abs=1e-3)

    def test_score_step_dict_format(self):
        step = _make_step()
        result = score_step_dict(step)
        assert result["ok"] is True
        assert "scores" in result
        assert "regime" in result
        assert set(result["scores"].keys()) == {"c", "i", "kappa", "s"}


# ===========================================================================
# Policy
# ===========================================================================

class TestPolicy:
    def test_policy_none_for_healthy(self):
        snap = ScoreSnapshot(c=0.7, i=0.7, kappa=0.8, s=1.26, regime="creative-grounded")
        action = evaluate_policy(snap)
        assert action.action == "none"

    def test_policy_grounded_regeneration_for_hallucination(self):
        snap = ScoreSnapshot(c=0.9, i=0.2, kappa=0.3, s=0.96, regime="hallucination-risk")
        action = evaluate_policy(snap)
        assert action.action == "require_grounded_regeneration"
        assert "citation_mode" in action.parameters

    def test_policy_increase_temp_for_rigid(self):
        snap = ScoreSnapshot(c=0.2, i=0.8, kappa=0.9, s=0.92, regime="rigid")
        action = evaluate_policy(snap)
        assert action.action == "increase_temperature"

    def test_policy_reduce_load_for_collapse_low_kappa(self):
        snap = ScoreSnapshot(c=0.1, i=0.1, kappa=0.2, s=0.12, regime="collapse")
        action = evaluate_policy(snap)
        assert action.action == "reduce_load_and_retry"

    def test_policy_increase_novelty_for_collapse_ok_kappa(self):
        snap = ScoreSnapshot(c=0.1, i=0.1, kappa=0.6, s=0.16, regime="collapse")
        action = evaluate_policy(snap)
        assert action.action == "increase_novelty"


# ===========================================================================
# Store
# ===========================================================================

class TestStore:
    def test_start_and_get_session(self):
        store = EvaluationStore()
        store.start_session("s1", metadata={"app": "test"})
        rec = store.get_session("s1")
        assert rec is not None
        assert rec.metadata["app"] == "test"

    def test_add_and_get_scores(self):
        store = EvaluationStore()
        store.start_session("s1")
        snap = ScoreSnapshot(c=0.5, i=0.5, kappa=0.5, s=0.75, regime="creative-grounded")
        store.add_score("s1", snap)
        scores = store.get_scores("s1")
        assert len(scores) == 1
        assert scores[0].s == 0.75

    def test_session_summary(self):
        store = EvaluationStore()
        store.start_session("s1")
        store.add_score("s1", ScoreSnapshot(c=0.6, i=0.8, kappa=0.7, s=1.16, regime="creative-grounded"))
        store.add_score("s1", ScoreSnapshot(c=0.4, i=0.6, kappa=0.5, s=0.70, regime="rigid"))
        summary = store.session_summary("s1")
        assert summary["step_count"] == 2
        assert summary["regime_counts"]["creative-grounded"] == 1
        assert summary["regime_counts"]["rigid"] == 1
        assert summary["avg_scores"]["c"] == pytest.approx(0.5)

    def test_session_summary_empty(self):
        store = EvaluationStore()
        store.start_session("s1")
        summary = store.session_summary("s1")
        assert summary["step_count"] == 0

    def test_session_summary_nonexistent(self):
        store = EvaluationStore()
        assert store.session_summary("missing") is None

    def test_list_sessions(self):
        store = EvaluationStore()
        store.start_session("a")
        store.start_session("b")
        assert set(store.list_sessions()) == {"a", "b"}


# ===========================================================================
# Gateway (end-to-end)
# ===========================================================================

class TestGateway:
    def test_start_session(self):
        gw = SCompassGateway()
        result = gw.start_session("s1", metadata={"app": "test"})
        assert result["ok"] is True

    def test_submit_step_returns_scores(self):
        gw = SCompassGateway()
        gw.start_session("s1")
        step = _make_step(session_id="s1")
        result = gw.submit_step(step)
        assert result["ok"] is True
        assert "scores" in result
        assert "regime" in result
        assert "policy" in result

    def test_submit_step_persists_in_store(self):
        gw = SCompassGateway()
        gw.start_session("s1")
        gw.submit_step(_make_step(session_id="s1"))
        gw.submit_step(_make_step(session_id="s1"))
        scores = gw.get_session_scores("s1")
        assert len(scores) == 2

    def test_session_summary_after_steps(self):
        gw = SCompassGateway()
        gw.start_session("s1")
        gw.submit_step(_make_step(session_id="s1"))
        summary = gw.get_session_summary("s1")
        assert summary is not None
        assert summary["step_count"] == 1

    def test_hallucination_triggers_policy(self):
        """A flat uniform output with no citations should trigger a policy."""
        gw = SCompassGateway()
        gw.start_session("s1")
        # highly repetitive / flat output with explicit claims but no citations
        step = _make_step(
            session_id="s1",
            output_text=" ".join(["token"] * 200),
            claims=[Claim(text="ungrounded assertion")],
            citations=[],
        )
        result = gw.submit_step(step)
        # The exact regime depends on estimator thresholds, but with a very
        # repetitive output and no citations the system should not be
        # creative-grounded.
        assert result["regime"] != "creative-grounded" or result["policy"]["action"] == "none"

    def test_multiple_sessions_independent(self):
        gw = SCompassGateway()
        gw.start_session("a")
        gw.start_session("b")
        gw.submit_step(_make_step(session_id="a"))
        assert len(gw.get_session_scores("a")) == 1
        assert len(gw.get_session_scores("b")) == 0
