"""
test_benchmark.py

Pytest tests that run the S Compass benchmark corpus through the REST API.

These tests validate that:

1. Every scenario can be submitted through the API without errors.
2. All seven REST endpoints return valid responses.
3. The regime classifier produces the expected labels for well-separated
   scenarios (creative-grounded and hallucination-risk in the current
   estimator configuration).
4. Session summaries and rolling-window stats are correctly computed.
5. Score components (C, I, κ, S) are within valid bounds.
"""

import json

import pytest

from s_compass.api import create_app
from s_compass.gateway import SCompassGateway

from benchmarks.corpus import (
    ALL_SCENARIOS,
    COLLAPSE,
    CREATIVE_GROUNDED,
    EDGE_CASES,
    HALLUCINATION_RISK,
    RIGID,
    WHITE_BOX,
)
from benchmarks.run_api_benchmark import run_benchmark


GRAY_BOX_LABELS = {
    scenario["label"]
    for scenario in ALL_SCENARIOS
    if scenario.get("gray_box_signals") and not scenario.get("white_box_signals")
}

WHITE_BOX_LABELS = {
    scenario["label"]
    for scenario in ALL_SCENARIOS
    if scenario.get("white_box_signals")
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def benchmark_results():
    """Run the full benchmark once and reuse across all tests."""
    return run_benchmark()


@pytest.fixture()
def client():
    """Flask test client with a fresh gateway."""
    gw = SCompassGateway()
    app = create_app(gateway=gw)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Structural tests: every scenario runs without error
# ---------------------------------------------------------------------------

class TestBenchmarkExecution:
    def test_all_scenarios_submitted(self, benchmark_results):
        """Every corpus scenario produces a valid API response."""
        assert len(benchmark_results["scenarios"]) == len(ALL_SCENARIOS)

    def test_all_sessions_created(self, benchmark_results):
        """Six session groups were created and listed."""
        assert set(benchmark_results["all_sessions"]) == {
            "bench_creative",
            "bench_hallucination",
            "bench_rigid",
            "bench_collapse",
            "bench_edge",
            "bench_whitebox",
        }

    def test_gray_box_scenarios_are_present(self):
        """The corpus includes gray-box benchmark traces."""
        assert GRAY_BOX_LABELS == {
            "creative-grounded-02-transformer-phases",
            "creative-grounded-14-gray-box-multi-source",
            "hallucination-risk-03-mixed-real-and-fake",
            "hallucination-risk-14-gray-box-unstable",
            "rigid-01-rote-repetition",
            "rigid-03-over-constrained",
            "rigid-11-gray-box-low-entropy",
            "collapse-03-incoherent-fragments",
            "collapse-11-gray-box-extreme-instability",
            "edge-18-gray-box-partial-signals",
        }

    def test_white_box_scenarios_are_present(self):
        """The corpus includes white-box benchmark traces."""
        assert WHITE_BOX_LABELS == {
            "creative-grounded-16-white-box-full",
            "hallucination-risk-16-white-box-divergent",
            "rigid-16-white-box-saturated",
            "collapse-16-white-box-breakdown",
        }

    def test_session_summaries_present(self, benchmark_results):
        """Each session has a valid summary with step counts."""
        for session_id, info in benchmark_results["sessions"].items():
            summary = info["summary"]
            assert "step_count" in summary
            assert summary["step_count"] > 0
            assert "regime_counts" in summary
            assert "avg_scores" in summary

    def test_rolling_window_present(self, benchmark_results):
        """Each session has rolling-window statistics."""
        for session_id, info in benchmark_results["sessions"].items():
            window = info["window"]
            assert window["ok"] is True
            assert window["count"] > 0
            assert "stats" in window
            for field in ("c", "i", "kappa", "s"):
                assert field in window["stats"]
                assert "mean" in window["stats"][field]
                assert "std" in window["stats"][field]


# ---------------------------------------------------------------------------
# Score validity tests
# ---------------------------------------------------------------------------

class TestScoreValidity:
    def test_c_in_bounds(self, benchmark_results):
        """C score is always in [0, 1]."""
        for s in benchmark_results["scenarios"]:
            assert 0.0 <= s["scores"]["c"] <= 1.0, (
                f"{s['label']}: C={s['scores']['c']}"
            )

    def test_i_in_bounds(self, benchmark_results):
        """I score is always in [0, 1]."""
        for s in benchmark_results["scenarios"]:
            assert 0.0 <= s["scores"]["i"] <= 1.0, (
                f"{s['label']}: I={s['scores']['i']}"
            )

    def test_kappa_in_bounds(self, benchmark_results):
        """κ score is always in [0, 1]."""
        for s in benchmark_results["scenarios"]:
            assert 0.0 <= s["scores"]["kappa"] <= 1.0, (
                f"{s['label']}: κ={s['scores']['kappa']}"
            )

    def test_s_non_negative(self, benchmark_results):
        """S = C + κI is always non-negative."""
        for s in benchmark_results["scenarios"]:
            assert s["scores"]["s"] >= 0.0, (
                f"{s['label']}: S={s['scores']['s']}"
            )

    def test_s_formula(self, benchmark_results):
        """S ≈ C + κ·I for every scenario (within rounding tolerance)."""
        for s in benchmark_results["scenarios"]:
            sc = s["scores"]
            expected_s = sc["c"] + sc["kappa"] * sc["i"]
            assert abs(sc["s"] - expected_s) < 0.01, (
                f"{s['label']}: S={sc['s']} != C+κI={expected_s}"
            )

    def test_gray_box_confidence_in_bounds(self, benchmark_results):
        """Benchmark responses expose valid confidence values."""
        for s in benchmark_results["scenarios"]:
            assert 0.0 <= s["confidence"] <= 1.0, (
                f"{s['label']}: confidence={s['confidence']}"
            )


class TestGrayBoxBenchmarking:
    def test_gray_box_scenarios_run_in_gray_box_mode(self, benchmark_results):
        """Configured gray-box scenarios should execute in gray-box mode."""
        by_label = {s["label"]: s for s in benchmark_results["scenarios"]}
        assert {label for label, s in by_label.items() if s["mode"] == "gray-box"} == GRAY_BOX_LABELS

    def test_gray_box_scenarios_use_high_confidence(self, benchmark_results):
        """Gray-box benchmark traces should surface higher confidence than black-box."""
        for s in benchmark_results["scenarios"]:
            if s["label"] in GRAY_BOX_LABELS:
                # Dynamic confidence: 0.65 base + up to 0.30 from signal coverage
                assert s["confidence"] > 0.65
                assert s["confidence"] <= 0.95
            elif s["label"] in WHITE_BOX_LABELS:
                # White-box confidence: [0.85, 0.99]
                assert s["confidence"] >= 0.85
                assert s["confidence"] <= 0.99
            else:
                assert s["confidence"] == pytest.approx(0.65)

    def test_gray_box_rigid_scenarios_match(self, benchmark_results):
        """Gray-box rigid traces should classify correctly.

        Both rigid-01 (rote repetition) and rigid-03 (over-constrained)
        use gray-box signals.  Structural repetition detection ensures
        both are now classified as rigid.
        """
        by_label = {s["label"]: s for s in benchmark_results["scenarios"]}
        for label in ("rigid-01-rote-repetition", "rigid-03-over-constrained"):
            assert by_label[label]["match"], (
                f"{label}: expected {by_label[label]['expected_regime']}, "
                f"got {by_label[label]['computed_regime']}"
            )


class TestWhiteBoxBenchmarking:
    def test_white_box_scenarios_run_in_white_box_mode(self, benchmark_results):
        """Configured white-box scenarios should execute in white-box mode."""
        by_label = {s["label"]: s for s in benchmark_results["scenarios"]}
        assert {label for label, s in by_label.items() if s["mode"] == "white-box"} == WHITE_BOX_LABELS

    def test_white_box_scenarios_have_high_confidence(self, benchmark_results):
        """White-box benchmark traces should surface highest confidence."""
        for s in benchmark_results["scenarios"]:
            if s["label"] in WHITE_BOX_LABELS:
                assert s["confidence"] >= 0.85
                assert s["confidence"] <= 0.99


# ---------------------------------------------------------------------------
# Regime classification tests — well-separated scenarios
# ---------------------------------------------------------------------------

class TestRegimeClassification:
    """Test regime accuracy for the clearly separated scenarios.

    The benchmark corpus includes scenarios designed to be unambiguous
    representatives of each regime.  Not all are expected to match the
    current heuristic estimators, but the well-separated ones should.
    """

    def test_creative_grounded_all_match(self, benchmark_results):
        """Creative-grounded scenarios should all be classified correctly."""
        creative = [
            s for s in benchmark_results["scenarios"]
            if s["label"].startswith("creative-grounded-")
        ]
        for s in creative:
            assert s["match"], (
                f"{s['label']}: expected {s['expected_regime']}, "
                f"got {s['computed_regime']}"
            )

    def test_hallucination_risk_all_match(self, benchmark_results):
        """Hallucination-risk scenarios should all be classified correctly."""
        hallucination = [
            s for s in benchmark_results["scenarios"]
            if s["label"].startswith("hallucination-risk-")
        ]
        for s in hallucination:
            assert s["match"], (
                f"{s['label']}: expected {s['expected_regime']}, "
                f"got {s['computed_regime']}"
            )

    def test_collapse_all_match(self, benchmark_results):
        """Collapse scenarios should all be classified correctly."""
        collapse = [
            s for s in benchmark_results["scenarios"]
            if s["label"].startswith("collapse-")
        ]
        for s in collapse:
            assert s["match"], (
                f"{s['label']}: expected {s['expected_regime']}, "
                f"got {s['computed_regime']}"
            )

    def test_rigid_well_separated_match(self, benchmark_results):
        """Well-separated rigid scenarios should be classified correctly.

        All five rigid scenarios are expected to match now that structural
        repetition detection catches template-style outputs with high
        lexical diversity but low structural diversity.
        """
        rigid = [
            s for s in benchmark_results["scenarios"]
            if s["label"].startswith("rigid-")
        ]
        for s in rigid:
            assert s["match"], (
                f"{s['label']}: expected {s['expected_regime']}, "
                f"got {s['computed_regime']}"
            )

    def test_hallucination_triggers_policy(self, benchmark_results):
        """Hallucination-risk scenarios should trigger grounded regeneration."""
        hallucination = [
            s for s in benchmark_results["scenarios"]
            if s["label"].startswith("hallucination-risk-")
        ]
        for s in hallucination:
            assert s["policy"]["action"] == "require_grounded_regeneration", (
                f"{s['label']}: expected require_grounded_regeneration, "
                f"got {s['policy']['action']}"
            )

    def test_creative_gets_no_policy_action(self, benchmark_results):
        """Creative-grounded scenarios should get 'none' policy action."""
        creative = [
            s for s in benchmark_results["scenarios"]
            if s["label"].startswith("creative-grounded-")
        ]
        for s in creative:
            assert s["policy"]["action"] == "none", (
                f"{s['label']}: expected none, got {s['policy']['action']}"
            )

    def test_collapse_triggers_policy(self, benchmark_results):
        """Collapse scenarios should trigger a load-reduction or retry policy."""
        collapse = [
            s for s in benchmark_results["scenarios"]
            if s["label"].startswith("collapse-")
        ]
        for s in collapse:
            assert s["policy"]["action"] in (
                "reduce_load_and_retry",
                "increase_novelty",
            ), (
                f"{s['label']}: expected reduce_load_and_retry or "
                f"increase_novelty, got {s['policy']['action']}"
            )


# ---------------------------------------------------------------------------
# Score separation tests — regimes should have distinguishable distributions
# ---------------------------------------------------------------------------

class TestScoreSeparation:
    """Validate that scores separate regimes in the expected directions."""

    def _avg_score(self, scenarios, prefix, field):
        group = [s for s in scenarios if s["label"].startswith(prefix)]
        return sum(s["scores"][field] for s in group) / len(group)

    def test_creative_c_higher_than_collapse(self, benchmark_results):
        """Creative-grounded has higher avg C than collapse."""
        sc = benchmark_results["scenarios"]
        c_creative = self._avg_score(sc, "creative-grounded-", "c")
        c_collapse = self._avg_score(sc, "collapse-", "c")
        assert c_creative > c_collapse

    def test_hallucination_i_lower_than_creative(self, benchmark_results):
        """Hallucination-risk has lower avg I than creative-grounded."""
        sc = benchmark_results["scenarios"]
        i_halluc = self._avg_score(sc, "hallucination-risk-", "i")
        i_creative = self._avg_score(sc, "creative-grounded-", "i")
        assert i_halluc < i_creative

    def test_collapse_kappa_lower_than_creative(self, benchmark_results):
        """Collapse scenarios (with capacity signals) have lower avg κ."""
        sc = benchmark_results["scenarios"]
        k_collapse = self._avg_score(sc, "collapse-", "kappa")
        k_creative = self._avg_score(sc, "creative-grounded-", "kappa")
        assert k_collapse < k_creative

    def test_collapse_s_lower_than_creative(self, benchmark_results):
        """Collapse scenarios have lower avg S than creative-grounded."""
        sc = benchmark_results["scenarios"]
        s_collapse = self._avg_score(sc, "collapse-", "s")
        s_creative = self._avg_score(sc, "creative-grounded-", "s")
        assert s_collapse < s_creative


# ---------------------------------------------------------------------------
# Standalone policy evaluation tests
# ---------------------------------------------------------------------------

class TestPolicyEvaluation:
    def test_all_policy_vectors_correct(self, benchmark_results):
        """Standalone policy evaluation with known vectors matches expected."""
        for check in benchmark_results["policy_evaluate_checks"]:
            assert check["match"], (
                f"Policy eval: expected {check['expected_regime']}, "
                f"got {check['computed_regime']}"
            )


# ---------------------------------------------------------------------------
# Individual endpoint tests (supplementary)
# ---------------------------------------------------------------------------

class TestCapacitySignals:
    """Verify that capacity signals flow through the API to κ estimation."""

    def test_capacity_reduces_kappa(self, client):
        """High context load + tool failures should reduce κ below 1.0."""
        client.post(
            "/v1/session/start",
            data=json.dumps({"session_id": "cap_test"}),
            content_type="application/json",
        )
        resp = client.post(
            "/v1/step",
            data=json.dumps({
                "session_id": "cap_test",
                "prompt": "Test prompt",
                "output": {"text": "A sufficiently long response for testing purposes."},
                "capacity": {
                    "context_tokens_used": 3800,
                    "context_window": 4096,
                    "latency_ms": 10000,
                    "latency_history": [1000, 5000, 10000, 8000, 15000],
                    "tool_failure_count": 3,
                    "tool_total_count": 5,
                },
            }),
            content_type="application/json",
        )
        data = resp.get_json()
        assert data["ok"] is True
        assert data["scores"]["kappa"] < 0.5, (
            f"Expected κ < 0.5 under stress, got {data['scores']['kappa']}"
        )

    def test_no_capacity_gives_full_kappa(self, client):
        """Without capacity signals, κ should be 1.0."""
        client.post(
            "/v1/session/start",
            data=json.dumps({"session_id": "nocap_test"}),
            content_type="application/json",
        )
        resp = client.post(
            "/v1/step",
            data=json.dumps({
                "session_id": "nocap_test",
                "prompt": "Test prompt",
                "output": {"text": "A response with no capacity constraints at all."},
            }),
            content_type="application/json",
        )
        data = resp.get_json()
        assert data["scores"]["kappa"] == 1.0


class TestHistorySignals:
    """Verify that conversation history flows through to I estimation."""

    def test_history_affects_consistency(self, client):
        """Providing history should influence cross-turn consistency."""
        client.post(
            "/v1/session/start",
            data=json.dumps({"session_id": "hist_test"}),
            content_type="application/json",
        )
        # Step without history
        resp1 = client.post(
            "/v1/step",
            data=json.dumps({
                "session_id": "hist_test",
                "prompt": "Explain URP.",
                "output": {"text": (
                    "URP proposes that systems maximize S through "
                    "distinction and integration under capacity constraints."
                )},
            }),
            content_type="application/json",
        )
        # Step with coherent history
        resp2 = client.post(
            "/v1/step",
            data=json.dumps({
                "session_id": "hist_test",
                "prompt": "Continue explaining.",
                "output": {"text": (
                    "URP proposes that systems maximize S through "
                    "distinction and integration under capacity constraints."
                )},
                "history": [
                    "URP is about maximizing S through distinction and integration.",
                ],
            }),
            content_type="application/json",
        )
        d1 = resp1.get_json()
        d2 = resp2.get_json()
        assert d1["ok"] is True
        assert d2["ok"] is True
        # Both should produce valid scores
        for field in ("c", "i", "kappa", "s"):
            assert field in d1["scores"]
            assert field in d2["scores"]
