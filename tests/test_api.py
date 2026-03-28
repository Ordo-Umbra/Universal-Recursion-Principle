"""
test_api.py

Tests for the s_compass.api module (REST API per Design-doc §8).

Uses Flask's built-in test client so no real HTTP server is needed.
"""

import json

import pytest

from s_compass.api import create_app
from s_compass.gateway import SCompassGateway


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    """Create a Flask test client with a fresh gateway."""
    gw = SCompassGateway()
    app = create_app(gateway=gw)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture()
def seeded_client():
    """Client with a pre-started session and one submitted step."""
    gw = SCompassGateway()
    app = create_app(gateway=gw)
    app.config["TESTING"] = True
    with app.test_client() as c:
        c.post(
            "/v1/session/start",
            data=json.dumps({"session_id": "s1", "metadata": {"app": "test"}}),
            content_type="application/json",
        )
        c.post(
            "/v1/step",
            data=json.dumps({
                "session_id": "s1",
                "prompt": "Explain URP.",
                "output": {
                    "text": "URP is a framework proposing recursive S-maximization.",
                    "citations": [{"doc_id": "doc1", "text": "recursive S-maximization"}],
                },
                "retrieved_context": [
                    {"doc_id": "doc1", "text": "URP proposes recursive S-maximization.", "score": 0.9}
                ],
            }),
            content_type="application/json",
        )
        yield c


# ===========================================================================
# §8.1  POST /v1/session/start
# ===========================================================================

class TestSessionStart:
    def test_start_session(self, client):
        resp = client.post(
            "/v1/session/start",
            data=json.dumps({"session_id": "sess_001", "metadata": {"env": "test"}}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True
        assert data["session_id"] == "sess_001"

    def test_start_session_missing_id(self, client):
        resp = client.post(
            "/v1/session/start",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["ok"] is False

    def test_start_session_no_metadata(self, client):
        resp = client.post(
            "/v1/session/start",
            data=json.dumps({"session_id": "s2"}),
            content_type="application/json",
        )
        assert resp.status_code == 201


# ===========================================================================
# §8.2  POST /v1/step
# ===========================================================================

class TestStepSubmit:
    def test_submit_step(self, client):
        # Start a session first
        client.post(
            "/v1/session/start",
            data=json.dumps({"session_id": "s1"}),
            content_type="application/json",
        )
        resp = client.post(
            "/v1/step",
            data=json.dumps({
                "session_id": "s1",
                "prompt": "What is S Compass?",
                "output": {
                    "text": "S Compass is a telemetry and policy layer for AI systems.",
                    "citations": [],
                },
            }),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert "scores" in data
        assert "regime" in data
        assert "policy" in data
        assert set(data["scores"].keys()) == {"c", "i", "kappa", "s"}

    def test_submit_step_missing_session_id(self, client):
        resp = client.post(
            "/v1/step",
            data=json.dumps({"prompt": "test"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_submit_step_with_retrieval(self, client):
        client.post(
            "/v1/session/start",
            data=json.dumps({"session_id": "s1"}),
            content_type="application/json",
        )
        resp = client.post(
            "/v1/step",
            data=json.dumps({
                "session_id": "s1",
                "prompt": "Explain URP.",
                "output": {"text": "URP proposes recursive S-maximization."},
                "retrieved_context": [
                    {"doc_id": "doc1", "text": "URP recursive framework", "score": 0.85},
                ],
            }),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True

    def test_submit_step_with_model_info(self, client):
        client.post(
            "/v1/session/start",
            data=json.dumps({"session_id": "s1"}),
            content_type="application/json",
        )
        resp = client.post(
            "/v1/step",
            data=json.dumps({
                "session_id": "s1",
                "prompt": "Test",
                "output": {"text": "Response."},
                "model": {"provider": "openai", "name": "gpt-x", "temperature": 0.4},
            }),
            content_type="application/json",
        )
        assert resp.status_code == 200


# ===========================================================================
# §8.3  GET /v1/session/<session_id>
# ===========================================================================

class TestSessionSummary:
    def test_get_session_summary(self, seeded_client):
        resp = seeded_client.get("/v1/session/s1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["session_id"] == "s1"
        assert data["step_count"] >= 1
        assert "regime_counts" in data
        assert "avg_scores" in data

    def test_session_not_found(self, client):
        resp = client.get("/v1/session/nonexistent")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["ok"] is False


# ===========================================================================
# §8.4  GET /v1/trace/<trace_id>/graph
# ===========================================================================

class TestTraceGraph:
    def test_trace_not_found(self, client):
        resp = client.get("/v1/trace/missing/graph")
        assert resp.status_code == 404

    def test_trace_graph_after_step(self, client):
        """After submitting a step the trace graph should be available."""
        client.post(
            "/v1/session/start",
            data=json.dumps({"session_id": "s1"}),
            content_type="application/json",
        )
        # Submit a step with a known trace_id
        step_resp = client.post(
            "/v1/step",
            data=json.dumps({
                "session_id": "s1",
                "trace_id": "trace_known",
                "prompt": "Explain URP in detail.",
                "output": {
                    "text": "URP is a recursive framework. It maximizes S across scales.",
                },
                "retrieved_context": [
                    {"doc_id": "d1", "text": "URP recursive framework maximizes S"},
                ],
            }),
            content_type="application/json",
        )
        assert step_resp.status_code == 200

        resp = client.get("/v1/trace/trace_known/graph")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert "nodes" in data
        assert "claim_ids" in data


# ===========================================================================
# §8.5  POST /v1/policy/evaluate
# ===========================================================================

class TestPolicyEvaluate:
    def test_evaluate_healthy_scores(self, client):
        resp = client.post(
            "/v1/policy/evaluate",
            data=json.dumps({"scores": {"c": 0.7, "i": 0.6, "kappa": 0.8}}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["regime"] == "creative-grounded"
        assert data["policy"]["action"] == "none"

    def test_evaluate_hallucination_risk(self, client):
        resp = client.post(
            "/v1/policy/evaluate",
            data=json.dumps({"scores": {"c": 0.8, "i": 0.2, "kappa": 0.3}}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["regime"] == "hallucination-risk"
        assert data["policy"]["action"] == "require_grounded_regeneration"

    def test_evaluate_missing_scores(self, client):
        resp = client.post(
            "/v1/policy/evaluate",
            data=json.dumps({"scores": {"c": 0.5}}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_evaluate_collapse(self, client):
        resp = client.post(
            "/v1/policy/evaluate",
            data=json.dumps({"scores": {"c": 0.1, "i": 0.1, "kappa": 0.2}}),
            content_type="application/json",
        )
        data = resp.get_json()
        assert data["regime"] == "collapse"
        assert data["policy"]["action"] == "reduce_load_and_retry"

    def test_evaluate_rigid(self, client):
        resp = client.post(
            "/v1/policy/evaluate",
            data=json.dumps({"scores": {"c": 0.2, "i": 0.8, "kappa": 0.9}}),
            content_type="application/json",
        )
        data = resp.get_json()
        assert data["regime"] == "rigid"
        assert data["policy"]["action"] == "increase_temperature"
