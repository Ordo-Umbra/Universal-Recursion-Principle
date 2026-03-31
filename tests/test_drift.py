"""
test_drift.py

Tests for session-level drift detection, regime-transition tracking,
drift-aware policy escalation, and the /v1/session/{id}/drift REST
endpoint (Design-doc §4.9).
"""

from __future__ import annotations

import json

import pytest

from s_compass import (
    EvaluationStore,
    SCompassGateway,
    ScoreSnapshot,
    StepInput,
    evaluate_policy,
    evaluate_with_drift,
    create_app,
)


# ── helpers ────────────────────────────────────────────────────────────────

def _snap(
    c: float = 0.6,
    i: float = 0.5,
    kappa: float = 0.9,
    regime: str = "creative-grounded",
    *,
    confidence: float = 0.65,
    mode: str = "black-box",
    trace_id: str | None = None,
) -> ScoreSnapshot:
    """Create a ScoreSnapshot with sensible defaults."""
    return ScoreSnapshot(
        c=c, i=i, kappa=kappa,
        s=round(c + kappa * i, 4),
        regime=regime,
        confidence=confidence,
        mode=mode,
        trace_id=trace_id,
    )


def _store_with_scores(scores: list[ScoreSnapshot]) -> EvaluationStore:
    """Return a store with a single session containing *scores*."""
    store = EvaluationStore()
    store.start_session("sess")
    for snap in scores:
        store.add_score("sess", snap)
    return store


# ═══════════════════════════════════════════════════════════════════════════
#  1. Linear slope helper
# ═══════════════════════════════════════════════════════════════════════════

class TestLinearSlope:
    """Unit tests for the OLS slope helper."""

    def test_empty_list(self):
        assert EvaluationStore._linear_slope([]) == 0.0

    def test_single_value(self):
        assert EvaluationStore._linear_slope([1.0]) == 0.0

    def test_constant_values(self):
        assert EvaluationStore._linear_slope([3.0, 3.0, 3.0, 3.0]) == 0.0

    def test_perfect_upward(self):
        slope = EvaluationStore._linear_slope([0.0, 1.0, 2.0, 3.0])
        assert abs(slope - 1.0) < 1e-9

    def test_perfect_downward(self):
        slope = EvaluationStore._linear_slope([3.0, 2.0, 1.0, 0.0])
        assert abs(slope - (-1.0)) < 1e-9

    def test_noisy_upward(self):
        slope = EvaluationStore._linear_slope([0.0, 0.5, 0.3, 0.8, 1.0])
        assert slope > 0.0

    def test_two_points(self):
        slope = EvaluationStore._linear_slope([1.0, 3.0])
        assert abs(slope - 2.0) < 1e-9


# ═══════════════════════════════════════════════════════════════════════════
#  2. Regime transitions
# ═══════════════════════════════════════════════════════════════════════════

class TestRegimeTransitions:
    """Tests for regime_transitions() on the store."""

    def test_nonexistent_session(self):
        store = EvaluationStore()
        assert store.regime_transitions("nope") is None

    def test_empty_session(self):
        store = _store_with_scores([])
        assert store.regime_transitions("sess") == []

    def test_single_score(self):
        store = _store_with_scores([_snap()])
        assert store.regime_transitions("sess") == []

    def test_no_transitions(self):
        store = _store_with_scores([
            _snap(regime="creative-grounded"),
            _snap(regime="creative-grounded"),
            _snap(regime="creative-grounded"),
        ])
        assert store.regime_transitions("sess") == []

    def test_single_transition(self):
        store = _store_with_scores([
            _snap(regime="creative-grounded"),
            _snap(regime="hallucination-risk"),
        ])
        transitions = store.regime_transitions("sess")
        assert len(transitions) == 1
        assert transitions[0] == {
            "step": 1, "from": "creative-grounded", "to": "hallucination-risk",
        }

    def test_multiple_transitions(self):
        store = _store_with_scores([
            _snap(regime="creative-grounded"),
            _snap(regime="hallucination-risk"),
            _snap(regime="hallucination-risk"),
            _snap(regime="collapse"),
        ])
        transitions = store.regime_transitions("sess")
        assert len(transitions) == 2
        assert transitions[0]["to"] == "hallucination-risk"
        assert transitions[1]["to"] == "collapse"

    def test_windowed_transitions(self):
        store = _store_with_scores([
            _snap(regime="creative-grounded"),
            _snap(regime="hallucination-risk"),
            _snap(regime="rigid"),
            _snap(regime="rigid"),
        ])
        # Only last 2 scores → no transition (both rigid)
        transitions = store.regime_transitions("sess", window=2)
        assert len(transitions) == 0

        # Last 3 scores → one transition (hallucination → rigid)
        transitions = store.regime_transitions("sess", window=3)
        assert len(transitions) == 1


# ═══════════════════════════════════════════════════════════════════════════
#  3. Drift summary
# ═══════════════════════════════════════════════════════════════════════════

class TestDriftSummary:
    """Tests for the drift_summary() method."""

    def test_nonexistent_session(self):
        store = EvaluationStore()
        assert store.drift_summary("nope") is None

    def test_empty_session(self):
        store = _store_with_scores([])
        result = store.drift_summary("sess")
        assert result["step_count"] == 0
        assert result["alerts"] == []
        assert result["current_regime"] is None
        assert result["dominant_regime"] is None

    def test_single_step(self):
        store = _store_with_scores([_snap()])
        result = store.drift_summary("sess")
        assert result["step_count"] == 1
        assert result["current_regime"] == "creative-grounded"
        assert result["dominant_regime"] == "creative-grounded"
        assert result["s_trend"] == 0.0  # not enough points

    def test_stable_session_no_alerts(self):
        """A stable creative-grounded session should produce no alerts."""
        store = _store_with_scores([
            _snap(c=0.60, i=0.55, kappa=0.95, regime="creative-grounded"),
            _snap(c=0.62, i=0.57, kappa=0.94, regime="creative-grounded"),
            _snap(c=0.64, i=0.56, kappa=0.93, regime="creative-grounded"),
            _snap(c=0.63, i=0.58, kappa=0.94, regime="creative-grounded"),
        ])
        result = store.drift_summary("sess")
        assert result["step_count"] == 4
        assert result["alerts"] == []
        assert result["transition_rate"] == 0.0
        assert result["dominant_regime"] == "creative-grounded"
        assert result["current_regime"] == "creative-grounded"
        assert result["s_trend"] >= 0.0  # S is stable/rising

    def test_declining_s_alert(self):
        """Monotonically declining S triggers 'declining_s' alert."""
        store = _store_with_scores([
            _snap(c=0.70, i=0.60, kappa=0.95, regime="creative-grounded"),
            _snap(c=0.55, i=0.50, kappa=0.80, regime="creative-grounded"),
            _snap(c=0.40, i=0.40, kappa=0.60, regime="creative-grounded"),
            _snap(c=0.30, i=0.30, kappa=0.40, regime="creative-grounded"),
        ])
        result = store.drift_summary("sess")
        assert result["s_trend"] < 0.0
        assert "declining_s" in result["alerts"]

    def test_regime_instability_alert(self):
        """Frequent regime transitions trigger 'regime_instability' alert."""
        store = _store_with_scores([
            _snap(regime="creative-grounded"),
            _snap(regime="hallucination-risk"),
            _snap(regime="rigid"),
            _snap(regime="collapse"),
        ])
        result = store.drift_summary("sess")
        assert result["transition_rate"] == 1.0  # every step transitions
        assert "regime_instability" in result["alerts"]

    def test_collapse_risk_alert(self):
        """Declining S with current regime=collapse triggers 'collapse_risk'."""
        store = _store_with_scores([
            _snap(c=0.60, i=0.50, kappa=0.90, regime="creative-grounded"),
            _snap(c=0.40, i=0.30, kappa=0.50, regime="rigid"),
            _snap(c=0.20, i=0.15, kappa=0.20, regime="collapse"),
            _snap(c=0.10, i=0.10, kappa=0.10, regime="collapse"),
        ])
        result = store.drift_summary("sess")
        assert "declining_s" in result["alerts"]
        assert "collapse_risk" in result["alerts"]
        assert result["current_regime"] == "collapse"

    def test_hallucination_drift_alert(self):
        """Declining S with current regime=hallucination triggers 'hallucination_drift'."""
        store = _store_with_scores([
            _snap(c=0.80, i=0.60, kappa=0.90, regime="creative-grounded"),
            _snap(c=0.75, i=0.40, kappa=0.70, regime="creative-grounded"),
            _snap(c=0.70, i=0.20, kappa=0.50, regime="hallucination-risk"),
            _snap(c=0.65, i=0.10, kappa=0.30, regime="hallucination-risk"),
        ])
        result = store.drift_summary("sess")
        assert "declining_s" in result["alerts"]
        assert "hallucination_drift" in result["alerts"]

    def test_window_limits_scope(self):
        """Drift summary should only consider the last *window* scores."""
        # First 5 steps: declining.  Last 3 steps: stable/rising.
        store = _store_with_scores([
            _snap(c=0.80, i=0.70, kappa=0.95, regime="creative-grounded"),
            _snap(c=0.60, i=0.50, kappa=0.80, regime="creative-grounded"),
            _snap(c=0.40, i=0.30, kappa=0.60, regime="rigid"),
            _snap(c=0.20, i=0.15, kappa=0.30, regime="collapse"),
            _snap(c=0.10, i=0.10, kappa=0.10, regime="collapse"),
            # recovery begins
            _snap(c=0.30, i=0.30, kappa=0.50, regime="creative-grounded"),
            _snap(c=0.50, i=0.45, kappa=0.70, regime="creative-grounded"),
            _snap(c=0.65, i=0.55, kappa=0.85, regime="creative-grounded"),
        ])
        # Full window sees recovery — no alerts expected
        result = store.drift_summary("sess", window=3)
        assert result["step_count"] == 3
        assert result["s_trend"] > 0.0
        assert "declining_s" not in result["alerts"]
        assert result["current_regime"] == "creative-grounded"

    def test_trends_are_rounded(self):
        """All trend values should be rounded to 4 decimal places."""
        store = _store_with_scores([
            _snap(c=0.60, i=0.50, kappa=0.90, regime="creative-grounded"),
            _snap(c=0.61, i=0.51, kappa=0.91, regime="creative-grounded"),
            _snap(c=0.62, i=0.52, kappa=0.92, regime="creative-grounded"),
        ])
        result = store.drift_summary("sess")
        for key in ("s_trend", "c_trend", "i_trend", "kappa_trend"):
            val_str = str(result[key])
            if "." in val_str:
                decimals = len(val_str.split(".")[1])
                assert decimals <= 4, f"{key}={result[key]} has too many decimals"

    def test_transition_rate_calculation(self):
        """Transition rate = transitions / (steps - 1)."""
        store = _store_with_scores([
            _snap(regime="creative-grounded"),
            _snap(regime="hallucination-risk"),
            _snap(regime="hallucination-risk"),
            _snap(regime="rigid"),
            _snap(regime="rigid"),
        ])
        result = store.drift_summary("sess")
        # 2 transitions / 4 gaps = 0.5
        assert result["transition_rate"] == 0.5

    def test_dominant_regime(self):
        """Dominant regime is the most common regime in the window."""
        store = _store_with_scores([
            _snap(regime="creative-grounded"),
            _snap(regime="rigid"),
            _snap(regime="rigid"),
            _snap(regime="rigid"),
            _snap(regime="creative-grounded"),
        ])
        result = store.drift_summary("sess")
        assert result["dominant_regime"] == "rigid"

    def test_all_window_zero(self):
        """window=0 should use all scores."""
        store = _store_with_scores([
            _snap(regime="creative-grounded"),
            _snap(regime="creative-grounded"),
        ])
        result = store.drift_summary("sess", window=0)
        assert result["step_count"] == 2


# ═══════════════════════════════════════════════════════════════════════════
#  4. Drift-aware policy
# ═══════════════════════════════════════════════════════════════════════════

class TestDriftAwarePolicy:
    """Tests for the drift-aware policy escalation function."""

    def test_no_drift_matches_base(self):
        """When drift is None, behaviour matches evaluate()."""
        snap = _snap(regime="creative-grounded")
        base = evaluate_policy(snap)
        drift_result = evaluate_with_drift(snap, drift=None)
        assert base.action == drift_result.action
        assert base.reason == drift_result.reason

    def test_empty_alerts_matches_base(self):
        """When drift contains no alerts, behaviour matches evaluate()."""
        snap = _snap(regime="creative-grounded")
        base = evaluate_policy(snap)
        drift_info = {"alerts": []}
        drift_result = evaluate_with_drift(snap, drift=drift_info)
        assert base.action == drift_result.action

    def test_declining_s_lowers_temperature(self):
        """declining_s should reduce temperature in the policy parameters."""
        snap = _snap(regime="hallucination-risk", c=0.7, i=0.2, kappa=0.5)
        base = evaluate_policy(snap)
        drift_result = evaluate_with_drift(snap, drift={"alerts": ["declining_s"]})
        base_temp = base.parameters.get("temperature", 1.0)
        drift_temp = drift_result.parameters.get("temperature", 1.0)
        assert drift_temp < base_temp

    def test_regime_instability_adds_stabilise(self):
        """regime_instability should add stabilise=True to parameters."""
        snap = _snap(regime="rigid", c=0.3, i=0.6, kappa=0.9)
        drift_result = evaluate_with_drift(
            snap, drift={"alerts": ["regime_instability"]},
        )
        assert drift_result.parameters.get("stabilise") is True

    def test_collapse_risk_overrides_action(self):
        """collapse_risk should force reduce_load_and_retry regardless of base."""
        snap = _snap(regime="collapse", c=0.1, i=0.1, kappa=0.1)
        drift_result = evaluate_with_drift(
            snap,
            drift={"alerts": ["declining_s", "collapse_risk"]},
        )
        assert drift_result.action == "reduce_load_and_retry"
        assert "Collapse risk" in drift_result.reason
        assert drift_result.parameters.get("stabilise") is True

    def test_hallucination_drift_tightens_citations(self):
        """hallucination_drift should enforce strict citations."""
        snap = _snap(regime="hallucination-risk", c=0.7, i=0.2, kappa=0.5)
        drift_result = evaluate_with_drift(
            snap,
            drift={"alerts": ["declining_s", "hallucination_drift"]},
        )
        assert drift_result.parameters.get("citation_mode") == "strict"

    def test_drift_reason_includes_alert_text(self):
        """The reason field should mention drift alerts."""
        snap = _snap(regime="rigid", c=0.3, i=0.6, kappa=0.9)
        drift_result = evaluate_with_drift(
            snap, drift={"alerts": ["declining_s"]},
        )
        assert "[drift:" in drift_result.reason
        assert "declining_s" in drift_result.reason


# ═══════════════════════════════════════════════════════════════════════════
#  5. Gateway drift endpoint
# ═══════════════════════════════════════════════════════════════════════════

class TestGatewayDrift:
    """Tests for SCompassGateway drift methods."""

    def test_get_drift_summary(self):
        gw = SCompassGateway()
        gw.start_session("s1")

        # Submit a few steps
        for c, i, k, regime in [
            (0.7, 0.6, 0.9, "creative-grounded"),
            (0.5, 0.4, 0.7, "creative-grounded"),
            (0.3, 0.2, 0.5, "rigid"),
        ]:
            snap = _snap(c=c, i=i, kappa=k, regime=regime)
            gw.store.add_score("s1", snap)

        drift = gw.get_drift_summary("s1")
        assert drift is not None
        assert drift["step_count"] == 3
        assert drift["current_regime"] == "rigid"

    def test_get_drift_summary_missing_session(self):
        gw = SCompassGateway()
        assert gw.get_drift_summary("nonexistent") is None

    def test_get_regime_transitions(self):
        gw = SCompassGateway()
        gw.start_session("s1")
        gw.store.add_score("s1", _snap(regime="creative-grounded"))
        gw.store.add_score("s1", _snap(regime="hallucination-risk"))
        transitions = gw.get_regime_transitions("s1")
        assert len(transitions) == 1
        assert transitions[0]["to"] == "hallucination-risk"


# ═══════════════════════════════════════════════════════════════════════════
#  6. REST API drift endpoint
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def client():
    """Create a test client for the REST API."""
    gw = SCompassGateway()
    app = create_app(gateway=gw)
    app.config["TESTING"] = True
    return app.test_client(), gw


class TestDriftAPI:
    """Tests for GET /v1/session/{id}/drift."""

    def test_drift_endpoint_missing_session(self, client):
        c, _ = client
        resp = c.get("/v1/session/nonexistent/drift")
        assert resp.status_code == 404

    def test_drift_endpoint_empty_session(self, client):
        c, gw = client
        gw.start_session("s1")
        resp = c.get("/v1/session/s1/drift")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["ok"] is True
        assert data["step_count"] == 0
        assert data["alerts"] == []

    def test_drift_endpoint_with_scores(self, client):
        c, gw = client
        gw.start_session("s1")
        for regime in ["creative-grounded", "hallucination-risk", "collapse"]:
            gw.store.add_score("s1", _snap(regime=regime))
        resp = c.get("/v1/session/s1/drift")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["ok"] is True
        assert data["step_count"] == 3
        assert data["current_regime"] == "collapse"
        assert len(data["regime_transitions"]) == 2

    def test_drift_endpoint_window_param(self, client):
        c, gw = client
        gw.start_session("s1")
        for _ in range(5):
            gw.store.add_score("s1", _snap(regime="creative-grounded"))
        resp = c.get("/v1/session/s1/drift?window=3")
        data = json.loads(resp.data)
        assert data["step_count"] == 3

    def test_drift_endpoint_invalid_window(self, client):
        c, gw = client
        gw.start_session("s1")
        resp = c.get("/v1/session/s1/drift?window=abc")
        assert resp.status_code == 400

    def test_drift_endpoint_alerts(self, client):
        """Verify that declining S is detected through the API."""
        c, gw = client
        gw.start_session("s1")
        for s_val in [1.5, 1.2, 0.9, 0.5]:
            snap = _snap(
                c=s_val * 0.4, i=s_val * 0.3, kappa=0.8,
                regime="creative-grounded",
            )
            gw.store.add_score("s1", snap)
        resp = c.get("/v1/session/s1/drift")
        data = json.loads(resp.data)
        assert data["s_trend"] < 0.0
        assert "declining_s" in data["alerts"]


# ═══════════════════════════════════════════════════════════════════════════
#  7. Integration: submit_step + drift
# ═══════════════════════════════════════════════════════════════════════════

class TestDriftIntegration:
    """End-to-end tests submitting steps and checking drift."""

    def test_submit_steps_then_check_drift(self):
        gw = SCompassGateway()
        gw.start_session("sess_drift")

        # Submit several steps with varying quality
        steps = [
            ("Explain URP.", "The S-functional S = C + κI captures novelty weighted by capacity."),
            ("What is C?", "C measures distinction — meaningful new structure and creative differentiation."),
            ("Repeat that.", "C. C. C."),
        ]

        for prompt, output in steps:
            gw.submit_step(StepInput(
                session_id="sess_drift",
                prompt=prompt,
                output_text=output,
            ))

        drift = gw.get_drift_summary("sess_drift")
        assert drift is not None
        assert drift["step_count"] == 3
        assert drift["current_regime"] is not None

    def test_full_pipeline_drift_after_collapse(self):
        """Submit healthy steps followed by collapse, then check drift."""
        gw = SCompassGateway()
        gw.start_session("sess_collapse")

        # Healthy steps
        for _ in range(3):
            gw.submit_step(StepInput(
                session_id="sess_collapse",
                prompt="Explain URP in detail with examples from physics.",
                output_text=(
                    "The Universal Recursion Principle proposes S = ΔC + κΔI. "
                    "In physics, C captures the growth of distinguishable states. "
                    "I measures coherent integration of those states into unified predictions. "
                    "κ encodes capacity constraints like energy or compute budgets."
                ),
                retrieved_context=[],
            ))

        # Degenerate steps (collapse-like)
        for _ in range(3):
            gw.submit_step(StepInput(
                session_id="sess_collapse",
                prompt="Explain.",
                output_text="I.",
                context_tokens_used=3900,
                context_window=4096,
                latency_ms=5000.0,
            ))

        drift = gw.get_drift_summary("sess_collapse", window=6)
        assert drift is not None
        assert drift["step_count"] == 6
        assert drift["s_trend"] < 0.0  # S should be declining
        assert len(drift["regime_transitions"]) >= 1  # at least one transition
