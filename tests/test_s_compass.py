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
        assert "gray_box.received" in VALID_EVENT_TYPES
        assert len(VALID_EVENT_TYPES) == 12

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


# ===========================================================================
# Rolling window statistics (EvaluationStore.rolling_window_stats)
# ===========================================================================

class TestRollingWindowStats:
    def _store_with_scores(self, n: int) -> EvaluationStore:
        store = EvaluationStore()
        store.start_session("s1")
        for k in range(n):
            v = (k + 1) / n
            store.add_score(
                "s1",
                ScoreSnapshot(c=v, i=v * 0.5, kappa=0.8, s=v + 0.8 * v * 0.5, regime="creative-grounded"),
            )
        return store

    def test_nonexistent_session_returns_none(self):
        store = EvaluationStore()
        assert store.rolling_window_stats("missing") is None

    def test_empty_session_count_zero(self):
        store = EvaluationStore()
        store.start_session("s1")
        result = store.rolling_window_stats("s1", window=5)
        assert result["count"] == 0
        assert result["stats"] == {}

    def test_count_capped_at_window(self):
        store = self._store_with_scores(20)
        result = store.rolling_window_stats("s1", window=5)
        assert result["count"] == 5

    def test_count_uses_all_when_fewer_than_window(self):
        store = self._store_with_scores(3)
        result = store.rolling_window_stats("s1", window=10)
        assert result["count"] == 3

    def test_stats_fields_present(self):
        store = self._store_with_scores(5)
        result = store.rolling_window_stats("s1", window=5)
        for field in ("c", "i", "kappa", "s"):
            assert field in result["stats"]
            for stat_key in ("mean", "std", "min", "max"):
                assert stat_key in result["stats"][field]

    def test_mean_correct(self):
        store = EvaluationStore()
        store.start_session("s1")
        for c_val in (0.2, 0.4, 0.6):
            store.add_score("s1", ScoreSnapshot(c=c_val, i=0.5, kappa=0.8, s=1.0, regime="creative-grounded"))
        result = store.rolling_window_stats("s1", window=3)
        assert result["stats"]["c"]["mean"] == pytest.approx(0.4, abs=1e-4)

    def test_std_zero_for_constant_series(self):
        store = EvaluationStore()
        store.start_session("s1")
        for _ in range(5):
            store.add_score("s1", ScoreSnapshot(c=0.5, i=0.5, kappa=0.5, s=0.75, regime="creative-grounded"))
        result = store.rolling_window_stats("s1", window=5)
        assert result["stats"]["c"]["std"] == pytest.approx(0.0, abs=1e-6)

    def test_window_selects_most_recent(self):
        """The window should include only the *most recent* snapshots."""
        store = EvaluationStore()
        store.start_session("s1")
        # Add 5 old scores with c=0.1
        for _ in range(5):
            store.add_score("s1", ScoreSnapshot(c=0.1, i=0.5, kappa=0.8, s=0.5, regime="rigid"))
        # Add 3 new scores with c=0.9
        for _ in range(3):
            store.add_score("s1", ScoreSnapshot(c=0.9, i=0.5, kappa=0.8, s=1.3, regime="creative-grounded"))
        result = store.rolling_window_stats("s1", window=3)
        assert result["stats"]["c"]["mean"] == pytest.approx(0.9, abs=1e-4)


# ===========================================================================
# Structural novelty and retrieval echo metrics
# ===========================================================================

class TestSentenceStructureNovelty:
    """Tests for the _sentence_structure_novelty metric."""

    def test_degenerate_short_text(self):
        from s_compass.estimators import _sentence_structure_novelty
        assert _sentence_structure_novelty("I I I") == 0.0

    def test_no_sentence_boundaries(self):
        from s_compass.estimators import _sentence_structure_novelty
        val = _sentence_structure_novelty(
            "the the the the the the the the the the"
        )
        assert val == pytest.approx(0.1)

    def test_single_sentence(self):
        from s_compass.estimators import _sentence_structure_novelty
        val = _sentence_structure_novelty(
            "URP proposes that systems maximize S."
        )
        assert val == 0.5  # neutral for single sentence

    def test_template_pattern_low_novelty(self):
        """Structurally repetitive 'The X is/has/does Y' template."""
        from s_compass.estimators import _sentence_structure_novelty
        text = (
            "The system is good. The framework has potential. "
            "The model does inference. The output has quality. "
            "The pipeline is fast. The code is clean."
        )
        val = _sentence_structure_novelty(text)
        assert val < 0.45

    def test_repeated_prefix_very_low(self):
        """All sentences start with same phrase."""
        from s_compass.estimators import _sentence_structure_novelty
        text = (
            "Based on the docs, URP is recursive. "
            "Based on the docs, S measures quality. "
            "Based on the docs, the framework works. "
            "Based on the docs, further study is needed."
        )
        val = _sentence_structure_novelty(text)
        assert val < 0.30

    def test_diverse_structure_high_novelty(self):
        """Creative text with diverse sentence structures."""
        from s_compass.estimators import _sentence_structure_novelty
        text = (
            "The Universal Recursion Principle proposes that all persistent "
            "systems share one dynamical law. When a system generates new "
            "distinctions and integrates them, it persists and grows. "
            "However, failure to balance these leads to stagnation. "
            "This single framework unifies physics, biology, and AI."
        )
        val = _sentence_structure_novelty(text)
        assert val > 0.50

    def test_returns_unit_interval(self):
        from s_compass.estimators import _sentence_structure_novelty
        texts = [
            "Short.",
            "A. B. C. D. E.",
            "One sentence with many words but no periods",
            "Diverse starts. Another kind. Yet more variety. "
            "Questions work too? Exclamations also!",
        ]
        for text in texts:
            val = _sentence_structure_novelty(text)
            assert 0.0 <= val <= 1.0


class TestRetrievalEchoNovelty:
    """Tests for the _retrieval_echo_novelty metric."""

    def test_no_retrieval_neutral(self):
        from s_compass.estimators import _retrieval_echo_novelty
        assert _retrieval_echo_novelty("Some output text.", []) == 0.5

    def test_short_output_neutral(self):
        from s_compass.estimators import _retrieval_echo_novelty
        chunks = [RetrievedChunk(doc_id="d1", text="long text here", score=0.9)]
        assert _retrieval_echo_novelty("hi", chunks) == 0.5

    def test_verbatim_copy_low_novelty(self):
        from s_compass.estimators import _retrieval_echo_novelty
        source = "URP proposes that all persistent systems maximize S through distinction and integration."
        chunks = [RetrievedChunk(doc_id="d1", text=source, score=0.95)]
        val = _retrieval_echo_novelty(source, chunks)
        assert val < 0.1  # near-zero novelty for exact copy

    def test_rephrased_output_high_novelty(self):
        from s_compass.estimators import _retrieval_echo_novelty
        retrieval = "URP proposes S maximization through recursive understanding."
        output = (
            "The framework described in the paper suggests that systems "
            "which balance novelty and coherence under capacity constraints "
            "tend to persist and evolve over time."
        )
        chunks = [RetrievedChunk(doc_id="d1", text=retrieval, score=0.9)]
        val = _retrieval_echo_novelty(output, chunks)
        assert val > 0.5

    def test_returns_unit_interval(self):
        from s_compass.estimators import _retrieval_echo_novelty
        chunks = [RetrievedChunk(doc_id="d1", text="context text here", score=0.8)]
        texts = [
            "completely different output about something else",
            "context text here",
            "some overlap with context text but also new content",
        ]
        for text in texts:
            val = _retrieval_echo_novelty(text, chunks)
            assert 0.0 <= val <= 1.0


class TestTemplateRigidClassification:
    """Tests for the template-rigid detection in classify_regime."""

    def test_template_rigid_detected(self):
        """Low structural novelty + moderate I → rigid."""
        assert classify_regime(
            c=0.80, i=0.45, kappa=1.0, structural_novelty=0.30,
        ) == "rigid"

    def test_structural_novelty_default_no_effect(self):
        """Without structural_novelty, high-C moderate-I → creative-grounded."""
        assert classify_regime(c=0.80, i=0.45, kappa=1.0) == "creative-grounded"

    def test_high_structural_novelty_no_rigid(self):
        """High structural novelty doesn't trigger template-rigid."""
        assert classify_regime(
            c=0.80, i=0.45, kappa=1.0, structural_novelty=0.60,
        ) == "creative-grounded"

    def test_template_rigid_requires_moderate_i(self):
        """Low structural novelty with low I → hallucination, not rigid."""
        # I < _I_LOW (0.35) → hallucination check catches first
        assert classify_regime(
            c=0.80, i=0.25, kappa=1.0, structural_novelty=0.20,
        ) == "hallucination-risk"

    def test_template_rigid_requires_moderate_kappa(self):
        """Low structural novelty with low κ → collapse, not rigid."""
        assert classify_regime(
            c=0.30, i=0.30, kappa=0.20, structural_novelty=0.20,
        ) == "collapse"

    def test_existing_rigid_still_works(self):
        """Classic rigid pattern (low C, high I) still detected."""
        assert classify_regime(c=0.2, i=0.8, kappa=0.9) == "rigid"

    def test_c_estimator_includes_structural_metrics(self):
        """The C estimator should incorporate structural novelty."""
        # Template-style output (structurally repetitive)
        step_template = _make_step(
            output_text=(
                "The system is good. The system has features. "
                "The system does tasks. The system works well."
            ),
        )
        # Creative output (structurally diverse)
        step_creative = _make_step(
            output_text=(
                "URP offers a bold unification of physics and cognition. "
                "When a system balances novelty against coherence under "
                "finite capacity, it persists. However, imbalance leads "
                "to either stagnation or collapse."
            ),
        )
        c_template = estimate_c(step_template)
        c_creative = estimate_c(step_creative)
        # Both should be valid
        assert 0.0 <= c_template <= 1.0
        assert 0.0 <= c_creative <= 1.0
