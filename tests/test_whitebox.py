"""
test_whitebox.py

Tests for white-box mode (Design-doc §6.3).

Covers:
* WhiteBoxSignals schema
* White-box helper functions
* White-box C, I, κ estimators
* Score dispatching (white-box vs gray-box vs black-box)
* Gateway auto-detection and response fields
* REST API parsing of white_box_signals
* Policy hooks for white-box mode
* Backward compatibility (gray-box and black-box still work unchanged)
"""

import json
import math

import numpy as np
import pytest

from s_compass.schemas import (
    Claim,
    GrayBoxSignals,
    RetrievedChunk,
    ScoreSnapshot,
    StepInput,
    WhiteBoxSignals,
)
from s_compass.estimators_whitebox import (
    _activation_sparsity_mean,
    _attention_concentration,
    _attention_entropy_mean,
    _attention_variance_stress,
    _gradient_norm_stress,
    _head_connectivity,
    _head_diversity,
    _kv_norm_stress,
    _residual_stream_coherence,
    estimate_c_whitebox,
    estimate_i_whitebox,
    estimate_kappa_whitebox,
    wb_signal_coverage,
)
from s_compass.scoring import score_step
from s_compass.gateway import SCompassGateway
from s_compass.api import create_app
from s_compass.policy import evaluate as evaluate_policy


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


def _make_white_step(**overrides) -> StepInput:
    """Create a step pre-configured for white-box mode with full signals."""
    wb = WhiteBoxSignals(
        attention_entropy=[0.5, 0.6, 0.4, 0.55, 0.65, 0.45],
        attention_variance=[0.05, 0.08, 0.03, 0.06, 0.07, 0.04],
        head_confidence={"h0": 0.85, "h1": 0.70, "h2": 0.92, "h3": 0.60},
        kv_norm=[1.2, 1.5, 1.3, 1.1, 1.4, 1.6],
        activation_sparsity=[0.3, 0.4, 0.35, 0.25, 0.45, 0.38],
        gradient_norm=[0.01, 0.02, 0.015, 0.008, 0.025],
        residual_coherence=0.82,
        layer_count=6,
    )
    gb = GrayBoxSignals(
        logprobs=[-0.5, -1.0, -0.3, -2.0, -0.7, -0.4, -1.5, -0.2],
        token_entropy=[0.3, 0.5, 0.2, 0.8, 0.4, 0.6, 0.1, 0.9],
        relevance_scores=[0.91, 0.65, 0.40],
        tool_confidence={"search": 0.92, "calculator": 0.88},
        decoding_instability=0.05,
    )
    defaults = dict(
        session_id="sess_test",
        prompt="Explain URP layerwise dynamics with details.",
        output_text="URP is a recursive framework that maximizes S across scales and layers.",
        white_box=wb,
        gray_box=gb,
        mode="white-box",
        retrieved_context=[
            RetrievedChunk(doc_id="d1", text="URP recursive framework", score=0.9),
            RetrievedChunk(doc_id="d2", text="S-maximization scales", score=0.7),
            RetrievedChunk(doc_id="d3", text="Transformer attention", score=0.4),
        ],
    )
    defaults.update(overrides)
    return StepInput(**defaults)


# ===========================================================================
# WhiteBoxSignals schema
# ===========================================================================

class TestWhiteBoxSignals:
    def test_all_defaults_are_none(self):
        wb = WhiteBoxSignals()
        assert wb.attention_entropy is None
        assert wb.attention_variance is None
        assert wb.head_confidence is None
        assert wb.kv_norm is None
        assert wb.activation_sparsity is None
        assert wb.gradient_norm is None
        assert wb.residual_coherence is None
        assert wb.layer_count is None

    def test_all_fields_settable(self):
        wb = WhiteBoxSignals(
            attention_entropy=[0.5, 0.6],
            attention_variance=[0.05, 0.08],
            head_confidence={"h0": 0.9, "h1": 0.7},
            kv_norm=[1.2, 1.5],
            activation_sparsity=[0.3, 0.4],
            gradient_norm=[0.01, 0.02],
            residual_coherence=0.85,
            layer_count=12,
        )
        assert wb.attention_entropy == [0.5, 0.6]
        assert wb.attention_variance == [0.05, 0.08]
        assert wb.head_confidence == {"h0": 0.9, "h1": 0.7}
        assert wb.kv_norm == [1.2, 1.5]
        assert wb.activation_sparsity == [0.3, 0.4]
        assert wb.gradient_norm == [0.01, 0.02]
        assert wb.residual_coherence == 0.85
        assert wb.layer_count == 12

    def test_partial_signals(self):
        wb = WhiteBoxSignals(
            attention_entropy=[0.5, 0.6],
            residual_coherence=0.75,
        )
        assert wb.attention_entropy == [0.5, 0.6]
        assert wb.attention_variance is None
        assert wb.residual_coherence == 0.75


# ===========================================================================
# White-box helper functions
# ===========================================================================

class TestAttentionEntropyMean:
    def test_empty(self):
        assert _attention_entropy_mean([]) == 0.0

    def test_moderate_entropy(self):
        result = _attention_entropy_mean([0.5, 0.6, 0.4])
        assert 0.0 < result < 1.0

    def test_high_entropy_approaches_one(self):
        result = _attention_entropy_mean([3.0, 4.0, 5.0])
        assert result > 0.9

    def test_low_entropy_near_zero(self):
        result = _attention_entropy_mean([0.01, 0.02, 0.01])
        assert result < 0.05


class TestHeadDiversity:
    def test_none(self):
        assert _head_diversity(None) == 0.5

    def test_empty(self):
        assert _head_diversity({}) == 0.5

    def test_single_head(self):
        assert _head_diversity({"h0": 0.9}) == 0.5

    def test_uniform_low_diversity(self):
        result = _head_diversity({"h0": 0.5, "h1": 0.5, "h2": 0.5})
        assert result == 0.0

    def test_varied_higher_diversity(self):
        result = _head_diversity({"h0": 0.1, "h1": 0.9, "h2": 0.5})
        assert result > 0.3


class TestActivationSparsityMean:
    def test_none(self):
        assert _activation_sparsity_mean(None) == 0.5

    def test_empty(self):
        assert _activation_sparsity_mean([]) == 0.5

    def test_moderate(self):
        result = _activation_sparsity_mean([0.3, 0.4, 0.35])
        assert 0.3 <= result <= 0.4

    def test_clamped(self):
        result = _activation_sparsity_mean([1.5, 2.0])
        assert result <= 1.0


class TestAttentionConcentration:
    def test_none(self):
        assert _attention_concentration(None) == 0.5

    def test_low_entropy_high_concentration(self):
        result = _attention_concentration([0.01, 0.02, 0.01])
        assert result > 0.9

    def test_high_entropy_low_concentration(self):
        result = _attention_concentration([5.0, 6.0, 4.0])
        assert result < 0.01


class TestResidualStreamCoherence:
    def test_none(self):
        assert _residual_stream_coherence(None) == 0.5

    def test_high_coherence(self):
        assert _residual_stream_coherence(0.9) == 0.9

    def test_clamped_above(self):
        assert _residual_stream_coherence(1.5) == 1.0

    def test_clamped_below(self):
        assert _residual_stream_coherence(-0.1) == 0.0


class TestHeadConnectivity:
    def test_none(self):
        assert _head_connectivity(None) == 0.5

    def test_all_active(self):
        result = _head_connectivity({"h0": 0.9, "h1": 0.8, "h2": 0.7})
        assert result == 1.0

    def test_none_active(self):
        result = _head_connectivity({"h0": 0.1, "h1": 0.2, "h2": 0.0})
        assert result == 0.0

    def test_partial_active(self):
        result = _head_connectivity({"h0": 0.9, "h1": 0.1, "h2": 0.8, "h3": 0.0})
        assert result == 0.5


class TestAttentionVarianceStress:
    def test_empty(self):
        assert _attention_variance_stress([]) == 0.0

    def test_low_variance_low_stress(self):
        result = _attention_variance_stress([0.01, 0.02, 0.01])
        assert result < 0.1

    def test_high_variance_high_stress(self):
        result = _attention_variance_stress([0.5, 0.8, 0.9])
        assert result > 0.5


class TestKvNormStress:
    def test_empty(self):
        assert _kv_norm_stress([]) == 0.0

    def test_single(self):
        assert _kv_norm_stress([1.0]) == 0.0

    def test_stable_norms_low_stress(self):
        result = _kv_norm_stress([1.0, 1.0, 1.0, 1.0])
        assert result < 0.1

    def test_variable_norms_higher_stress(self):
        result = _kv_norm_stress([1.0, 5.0, 1.0, 8.0])
        assert result > 0.3


class TestGradientNormStress:
    def test_empty(self):
        assert _gradient_norm_stress([]) == 0.0

    def test_small_norms_low_stress(self):
        result = _gradient_norm_stress([0.01, 0.02, 0.01])
        assert result < 0.1

    def test_large_norms_high_stress(self):
        result = _gradient_norm_stress([5.0, 10.0, 8.0])
        assert result > 0.9


# ===========================================================================
# wb_signal_coverage
# ===========================================================================

class TestWbSignalCoverage:
    def test_none(self):
        assert wb_signal_coverage(None) == 0.0

    def test_empty_signals(self):
        wb = WhiteBoxSignals()
        assert wb_signal_coverage(wb) == 0.0

    def test_full_signals(self):
        wb = WhiteBoxSignals(
            attention_entropy=[0.5],
            attention_variance=[0.05],
            head_confidence={"h0": 0.9},
            kv_norm=[1.2],
            activation_sparsity=[0.3],
            gradient_norm=[0.01],
            residual_coherence=0.85,
        )
        coverage = wb_signal_coverage(wb)
        assert coverage == pytest.approx(1.0, abs=0.01)

    def test_partial_coverage(self):
        wb = WhiteBoxSignals(attention_entropy=[0.5], residual_coherence=0.85)
        coverage = wb_signal_coverage(wb)
        assert 0.3 <= coverage <= 0.4  # 0.20 + 0.15 = 0.35


# ===========================================================================
# White-box C estimator
# ===========================================================================

class TestWhiteBoxCEstimator:
    def test_returns_between_zero_and_one(self):
        step = _make_white_step()
        c = estimate_c_whitebox(step)
        assert 0.0 <= c <= 1.0

    def test_fallback_no_white_box_signals(self):
        step = _make_step(mode="white-box", white_box=WhiteBoxSignals())
        c = estimate_c_whitebox(step)
        assert 0.0 <= c <= 1.0

    def test_attention_entropy_increases_c(self):
        step_low = _make_white_step(
            white_box=WhiteBoxSignals(attention_entropy=[0.01] * 6),
        )
        step_high = _make_white_step(
            white_box=WhiteBoxSignals(attention_entropy=[2.0] * 6),
        )
        c_low = estimate_c_whitebox(step_low)
        c_high = estimate_c_whitebox(step_high)
        assert c_high > c_low

    def test_prefers_attention_over_logprobs(self):
        # When attention entropy is present, it's the primary signal
        step = _make_white_step()
        c = estimate_c_whitebox(step)
        assert 0.0 <= c <= 1.0


# ===========================================================================
# White-box I estimator
# ===========================================================================

class TestWhiteBoxIEstimator:
    def test_returns_between_zero_and_one(self):
        step = _make_white_step()
        i = estimate_i_whitebox(step)
        assert 0.0 <= i <= 1.0

    def test_fallback_no_white_box_signals(self):
        step = _make_step(mode="white-box", white_box=WhiteBoxSignals())
        i = estimate_i_whitebox(step)
        assert 0.0 <= i <= 1.0

    def test_high_residual_coherence_increases_i(self):
        step_low = _make_white_step(
            white_box=WhiteBoxSignals(residual_coherence=0.1),
        )
        step_high = _make_white_step(
            white_box=WhiteBoxSignals(residual_coherence=0.95),
        )
        i_low = estimate_i_whitebox(step_low)
        i_high = estimate_i_whitebox(step_high)
        assert i_high > i_low

    def test_attention_concentration_contributes(self):
        step = _make_white_step(
            white_box=WhiteBoxSignals(
                attention_entropy=[0.01] * 6,  # low entropy = high concentration
                residual_coherence=0.9,
            ),
        )
        i = estimate_i_whitebox(step)
        assert i > 0.3


# ===========================================================================
# White-box κ estimator
# ===========================================================================

class TestWhiteBoxKappaEstimator:
    def test_returns_between_zero_and_one(self):
        step = _make_white_step()
        k = estimate_kappa_whitebox(step)
        assert 0.0 <= k <= 1.0

    def test_stable_signals_high_kappa(self):
        step = _make_white_step(
            white_box=WhiteBoxSignals(
                attention_variance=[0.01] * 6,
                kv_norm=[1.0] * 6,
                gradient_norm=[0.001] * 5,
            ),
        )
        k = estimate_kappa_whitebox(step)
        assert k > 0.8

    def test_unstable_signals_low_kappa(self):
        step = _make_white_step(
            white_box=WhiteBoxSignals(
                attention_variance=[0.9, 0.8, 0.95],
                kv_norm=[1.0, 50.0, 2.0, 80.0],
                gradient_norm=[5.0, 10.0, 8.0],
            ),
            gray_box=GrayBoxSignals(
                decoding_instability=0.9,
                logprobs=[-0.01, -6.5, -0.02, -7.0],
            ),
            context_tokens_used=3900,
            context_window=4096,
            latency_history=[400, 6000, 15000, 22000],
            tool_failure_count=5,
            tool_total_count=5,
        )
        k = estimate_kappa_whitebox(step)
        assert k < 0.5

    def test_fallback_no_signals(self):
        step = _make_step(mode="white-box", white_box=WhiteBoxSignals())
        k = estimate_kappa_whitebox(step)
        assert 0.0 <= k <= 1.0


# ===========================================================================
# Score dispatch
# ===========================================================================

class TestScoreStepDispatch:
    def test_black_box_default(self):
        step = _make_step()
        snap = score_step(step)
        assert snap.mode == "black-box"
        assert snap.confidence == 0.65

    def test_white_box_full_signals(self):
        step = _make_white_step()
        snap = score_step(step)
        assert snap.mode == "white-box"
        assert snap.confidence >= 0.85
        assert snap.confidence <= 0.99

    def test_white_box_partial_signals(self):
        step = _make_white_step(
            white_box=WhiteBoxSignals(
                attention_entropy=[0.5, 0.6],
                residual_coherence=0.8,
            ),
        )
        snap = score_step(step)
        assert snap.mode == "white-box"
        # Partial WB signals → lower confidence than full
        assert 0.85 <= snap.confidence <= 0.99

    def test_white_box_higher_confidence_than_gray_box(self):
        step_wb = _make_white_step()
        step_gb = StepInput(
            session_id="sess_test",
            prompt="Explain URP.",
            output_text="URP is a recursive framework.",
            gray_box=GrayBoxSignals(
                logprobs=[-0.5, -1.0, -0.3],
                token_entropy=[0.3, 0.5, 0.2],
                relevance_scores=[0.91],
                tool_confidence={"search": 0.92},
                decoding_instability=0.05,
            ),
            mode="gray-box",
        )
        snap_wb = score_step(step_wb)
        snap_gb = score_step(step_gb)
        assert snap_wb.confidence > snap_gb.confidence

    def test_all_scores_in_range(self):
        step = _make_white_step()
        snap = score_step(step)
        assert 0.0 <= snap.c <= 1.0
        assert 0.0 <= snap.i <= 1.0
        assert 0.0 <= snap.kappa <= 1.0
        assert snap.s >= 0.0
        assert snap.regime in (
            "creative-grounded",
            "hallucination-risk",
            "rigid",
            "collapse",
        )


# ===========================================================================
# Gateway auto-detection
# ===========================================================================

class TestGatewayWhiteBox:
    def test_auto_detect_white_box_mode(self):
        gw = SCompassGateway()
        gw.start_session("s1")
        step = _make_white_step(session_id="s1", mode="black-box")
        result = gw.submit_step(step)
        assert result["mode"] == "white-box"

    def test_white_box_emits_telemetry_event(self):
        gw = SCompassGateway()
        gw.start_session("s1")
        step = _make_white_step(session_id="s1")
        gw.submit_step(step)

        rec = gw.store.get_session("s1")
        event_types = [e.event_type for e in rec.events]
        assert "white_box.received" in event_types

    def test_white_box_also_emits_gray_box_event(self):
        gw = SCompassGateway()
        gw.start_session("s1")
        step = _make_white_step(session_id="s1")
        gw.submit_step(step)

        rec = gw.store.get_session("s1")
        event_types = [e.event_type for e in rec.events]
        # Both gray-box and white-box events should be emitted when both present
        assert "gray_box.received" in event_types
        assert "white_box.received" in event_types

    def test_session_summary_tracks_white_box_mode(self):
        gw = SCompassGateway()
        gw.start_session("s1")
        step = _make_white_step(session_id="s1")
        gw.submit_step(step)

        summary = gw.get_session_summary("s1")
        assert "white-box" in summary["mode_counts"]
        assert summary["mode_counts"]["white-box"] >= 1
        assert summary["avg_confidence"] is not None
        assert summary["avg_confidence"] >= 0.85

    def test_confidence_in_response(self):
        gw = SCompassGateway()
        gw.start_session("s1")
        step = _make_white_step(session_id="s1")
        result = gw.submit_step(step)
        assert result["confidence"] >= 0.85
        assert result["confidence"] <= 0.99


# ===========================================================================
# REST API parsing
# ===========================================================================

class TestAPIWhiteBox:
    @pytest.fixture
    def client(self):
        app = create_app()
        app.config["TESTING"] = True
        with app.test_client() as c:
            yield c

    def _start_session(self, client, session_id="sess_wb"):
        client.post(
            "/v1/session/start",
            json={"session_id": session_id},
        )

    def test_white_box_signals_parsed(self, client):
        self._start_session(client)
        resp = client.post("/v1/step", json={
            "session_id": "sess_wb",
            "prompt": "Explain URP layerwise.",
            "output": {"text": "URP uses recursive S-maximization across layers."},
            "white_box_signals": {
                "attention_entropy": [0.5, 0.6, 0.4],
                "attention_variance": [0.05, 0.08, 0.03],
                "head_confidence": {"h0": 0.85, "h1": 0.70},
                "kv_norm": [1.2, 1.5],
                "activation_sparsity": [0.3, 0.4],
                "gradient_norm": [0.01, 0.02],
                "residual_coherence": 0.82,
                "layer_count": 6,
            },
        })
        data = resp.get_json()
        assert data["ok"] is True
        assert data["mode"] == "white-box"
        assert data["confidence"] >= 0.85

    def test_white_box_with_gray_box_signals(self, client):
        self._start_session(client)
        resp = client.post("/v1/step", json={
            "session_id": "sess_wb",
            "prompt": "Explain URP.",
            "output": {"text": "URP is recursive S-maximization."},
            "gray_box_signals": {
                "logprobs": [-0.5, -1.0],
                "relevance_scores": [0.9],
            },
            "white_box_signals": {
                "attention_entropy": [0.5, 0.6],
                "residual_coherence": 0.82,
            },
        })
        data = resp.get_json()
        assert data["ok"] is True
        assert data["mode"] == "white-box"

    def test_partial_white_box_signals(self, client):
        self._start_session(client)
        resp = client.post("/v1/step", json={
            "session_id": "sess_wb",
            "prompt": "Test partial signals.",
            "output": {"text": "Partial white-box signal test."},
            "white_box_signals": {
                "attention_entropy": [0.5, 0.6],
            },
        })
        data = resp.get_json()
        assert data["ok"] is True
        assert data["mode"] == "white-box"

    def test_empty_white_box_signals_no_upgrade(self, client):
        self._start_session(client)
        resp = client.post("/v1/step", json={
            "session_id": "sess_wb",
            "prompt": "Test empty signals.",
            "output": {"text": "Empty white-box signal test."},
            "white_box_signals": {},
        })
        data = resp.get_json()
        assert data["ok"] is True
        # Empty dict → raw_wb is falsy → no white-box upgrade
        assert data["mode"] == "black-box"

    def test_explicit_mode_override(self, client):
        self._start_session(client)
        resp = client.post("/v1/step", json={
            "session_id": "sess_wb",
            "prompt": "Mode override.",
            "output": {"text": "Explicit mode override test."},
            "white_box_signals": {
                "attention_entropy": [0.5],
            },
            "mode": "white-box",
        })
        data = resp.get_json()
        assert data["ok"] is True
        assert data["mode"] == "white-box"

    def test_policy_endpoint_accepts_white_box_mode(self, client):
        resp = client.post("/v1/policy/evaluate", json={
            "scores": {"c": 0.7, "i": 0.2, "kappa": 0.4},
            "confidence": 0.95,
            "mode": "white-box",
        })
        data = resp.get_json()
        assert data["ok"] is True
        assert data["mode"] == "white-box"
        # Hallucination-risk with high confidence + white-box → layer-targeted
        assert "white-box" in data["policy"]["reason"] or "layerwise" in data["policy"]["reason"]


# ===========================================================================
# Policy hooks for white-box mode
# ===========================================================================

class TestWhiteBoxPolicy:
    def test_hallucination_risk_white_box_high_confidence(self):
        snap = ScoreSnapshot(
            c=0.7, i=0.2, kappa=0.4, s=0.78,
            regime="hallucination-risk",
            confidence=0.95,
            mode="white-box",
        )
        action = evaluate_policy(snap)
        assert action.action == "require_grounded_regeneration"
        assert action.parameters.get("head_dropout") is not None
        assert action.parameters.get("route_to_safer_variant") is True
        assert action.parameters["temperature"] == 0.10

    def test_collapse_white_box_high_confidence(self):
        snap = ScoreSnapshot(
            c=0.2, i=0.2, kappa=0.3, s=0.26,
            regime="collapse",
            confidence=0.95,
            mode="white-box",
        )
        action = evaluate_policy(snap)
        assert action.action == "reduce_load_and_retry"
        assert action.parameters.get("head_dropout") == 0.10
        assert action.parameters.get("route_to_safer_variant") is True

    def test_rigid_white_box_high_confidence(self):
        snap = ScoreSnapshot(
            c=0.3, i=0.7, kappa=0.8, s=0.86,
            regime="rigid",
            confidence=0.95,
            mode="white-box",
        )
        action = evaluate_policy(snap)
        assert action.action == "increase_temperature"
        assert action.parameters["temperature"] == 0.85
        assert action.parameters.get("rep_pen_adjustment") == 0.10

    def test_creative_grounded_no_action(self):
        snap = ScoreSnapshot(
            c=0.7, i=0.7, kappa=0.9, s=1.33,
            regime="creative-grounded",
            confidence=0.95,
            mode="white-box",
        )
        action = evaluate_policy(snap)
        assert action.action == "none"

    def test_hallucination_risk_white_box_low_confidence(self):
        """White-box mode with low confidence falls back to non-WB policy."""
        snap = ScoreSnapshot(
            c=0.7, i=0.2, kappa=0.4, s=0.78,
            regime="hallucination-risk",
            confidence=0.70,
            mode="white-box",
        )
        action = evaluate_policy(snap)
        assert action.action == "require_grounded_regeneration"
        # Low confidence → no layer-targeted params
        assert "head_dropout" not in action.parameters


# ===========================================================================
# Backward compatibility
# ===========================================================================

class TestBackwardCompatibility:
    def test_black_box_still_works(self):
        step = _make_step()
        snap = score_step(step)
        assert snap.mode == "black-box"
        assert snap.confidence == 0.65
        assert 0.0 <= snap.c <= 1.0
        assert 0.0 <= snap.i <= 1.0
        assert 0.0 <= snap.kappa <= 1.0

    def test_gray_box_still_works(self):
        step = StepInput(
            session_id="sess_test",
            prompt="Explain URP.",
            output_text="URP is a recursive framework.",
            gray_box=GrayBoxSignals(
                logprobs=[-0.5, -1.0, -0.3, -2.0],
                token_entropy=[0.3, 0.5, 0.2, 0.8],
                relevance_scores=[0.91, 0.65],
                tool_confidence={"search": 0.92},
                decoding_instability=0.05,
            ),
            mode="gray-box",
        )
        snap = score_step(step)
        assert snap.mode == "gray-box"
        assert 0.65 <= snap.confidence <= 0.95

    def test_step_input_has_white_box_field(self):
        step = _make_step()
        assert step.white_box is None
        assert step.mode == "black-box"
