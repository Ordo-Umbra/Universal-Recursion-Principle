"""
api.py

REST API for S Compass (Design-doc §8).

Implements the five original endpoints plus two new ones:

* ``POST /v1/session/start``       — start a traced session (§8.1)
* ``POST /v1/step``                — submit + score an inference step (§8.2)
* ``GET  /v1/session/<id>``        — session summary (§8.3)
* ``GET  /v1/trace/<id>/graph``    — coherence graph for a trace (§8.4)
* ``POST /v1/policy/evaluate``     — standalone policy evaluation (§8.5)
* ``GET  /v1/sessions``            — list all active session IDs (new)
* ``GET  /v1/session/<id>/window`` — rolling-window score statistics (new)

The module exposes :func:`create_app` which returns a Flask application
wired to a shared :class:`SCompassGateway`.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from flask import Flask, jsonify, request

from .gateway import SCompassGateway
from .schemas import Claim, GrayBoxSignals, RetrievedChunk, ScoreSnapshot, StepInput
from .policy import evaluate as evaluate_policy
from .scoring import classify_regime


def create_app(gateway: Optional[SCompassGateway] = None) -> Flask:
    """Create and configure the Flask application.

    Parameters
    ----------
    gateway:
        An existing gateway instance to use.  When *None* a fresh
        :class:`SCompassGateway` is created.

    Returns
    -------
    Flask
        Configured application ready to serve.
    """
    app = Flask(__name__)
    gw = gateway or SCompassGateway()

    # Store the gateway on the app so tests can access it
    app.config["gateway"] = gw

    # -----------------------------------------------------------------
    # §8.1  POST /v1/session/start
    # -----------------------------------------------------------------
    @app.route("/v1/session/start", methods=["POST"])
    def start_session() -> tuple:
        body: Dict[str, Any] = request.get_json(silent=True) or {}
        session_id = body.get("session_id")
        if not session_id:
            return jsonify({"ok": False, "error": "session_id is required"}), 400
        metadata = body.get("metadata", {})
        result = gw.start_session(session_id, metadata=metadata)
        return jsonify(result), 201

    # -----------------------------------------------------------------
    # §8.2  POST /v1/step
    # -----------------------------------------------------------------
    @app.route("/v1/step", methods=["POST"])
    def submit_step() -> tuple:
        body: Dict[str, Any] = request.get_json(silent=True) or {}
        session_id = body.get("session_id")
        if not session_id:
            return jsonify({"ok": False, "error": "session_id is required"}), 400

        prompt = body.get("prompt", "")
        output = body.get("output", {})
        output_text = output.get("text", "") if isinstance(output, dict) else str(output)

        # Build retrieved context
        raw_chunks = body.get("retrieved_context", [])
        retrieved_context = [
            RetrievedChunk(
                doc_id=c.get("doc_id", ""),
                text=c.get("text", ""),
                score=c.get("score", 0.0),
                chunk_id=c.get("chunk_id"),
            )
            for c in raw_chunks
        ]

        # Build claims if provided
        raw_claims = body.get("claims", [])
        claims = [
            Claim(
                text=cl.get("text", ""),
                claim_type=cl.get("type", "assertion"),
                confidence=cl.get("confidence", 1.0),
            )
            for cl in raw_claims
        ]

        # Build citations
        citations = []
        if isinstance(output, dict):
            citations = output.get("citations", [])

        # Model metadata
        model_info = body.get("model", {})

        # Capacity / telemetry signals
        capacity = body.get("capacity", {})

        step = StepInput(
            session_id=session_id,
            prompt=prompt,
            output_text=output_text,
            retrieved_context=retrieved_context,
            claims=claims,
            citations=citations,
            model_name=model_info.get("name"),
            temperature=model_info.get("temperature"),
            context_tokens_used=capacity.get("context_tokens_used", 0),
            context_window=capacity.get("context_window", 4096),
            latency_ms=capacity.get("latency_ms", 0.0),
            latency_history=capacity.get("latency_history", []),
            tool_failure_count=capacity.get("tool_failure_count", 0),
            tool_total_count=capacity.get("tool_total_count", 0),
            history=body.get("history", []),
        )

        # Gray-box signals (Design-doc §6.2)
        raw_gb = body.get("gray_box_signals")
        if raw_gb and isinstance(raw_gb, dict):
            step.gray_box = GrayBoxSignals(
                logprobs=raw_gb.get("logprobs"),
                token_entropy=raw_gb.get("token_entropy"),
                relevance_scores=raw_gb.get("relevance_scores"),
                tool_confidence=raw_gb.get("tool_confidence"),
                decoding_instability=raw_gb.get("decoding_instability"),
            )
            step.mode = body.get("mode", "gray-box")

        if body.get("step_id"):
            step.step_id = body["step_id"]
        if body.get("trace_id"):
            step.trace_id = body["trace_id"]

        result = gw.submit_step(step)
        return jsonify(result), 200

    # -----------------------------------------------------------------
    # §8.3  GET /v1/session/<session_id>
    # -----------------------------------------------------------------
    @app.route("/v1/session/<session_id>", methods=["GET"])
    def get_session(session_id: str) -> tuple:
        summary = gw.get_session_summary(session_id)
        if summary is None:
            return jsonify({"ok": False, "error": "session not found"}), 404
        summary["ok"] = True
        return jsonify(summary), 200

    # -----------------------------------------------------------------
    # NEW  GET /v1/sessions  — list all session IDs
    # -----------------------------------------------------------------
    @app.route("/v1/sessions", methods=["GET"])
    def list_sessions() -> tuple:
        session_ids = gw.store.list_sessions()
        return jsonify({"ok": True, "sessions": session_ids}), 200

    # -----------------------------------------------------------------
    # NEW  GET /v1/session/<session_id>/window  — rolling window stats
    # -----------------------------------------------------------------
    @app.route("/v1/session/<session_id>/window", methods=["GET"])
    def session_window(session_id: str) -> tuple:
        try:
            window = int(request.args.get("window", 10))
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": "window must be an integer"}), 400
        result = gw.store.rolling_window_stats(session_id, window=window)
        if result is None:
            return jsonify({"ok": False, "error": "session not found"}), 404
        result["ok"] = True
        return jsonify(result), 200

    # -----------------------------------------------------------------
    # §8.4  GET /v1/trace/<trace_id>/graph
    # -----------------------------------------------------------------
    @app.route("/v1/trace/<trace_id>/graph", methods=["GET"])
    def get_trace_graph(trace_id: str) -> tuple:
        graph_data = gw.get_trace_graph(trace_id)
        if graph_data is None:
            return jsonify({"ok": False, "error": "trace not found"}), 404
        graph_data["ok"] = True
        return jsonify(graph_data), 200

    # -----------------------------------------------------------------
    # §8.5  POST /v1/policy/evaluate
    # -----------------------------------------------------------------
    @app.route("/v1/policy/evaluate", methods=["POST"])
    def policy_evaluate() -> tuple:
        body: Dict[str, Any] = request.get_json(silent=True) or {}
        scores = body.get("scores", {})

        c = scores.get("c")
        i = scores.get("i")
        kappa = scores.get("kappa")

        if c is None or i is None or kappa is None:
            return jsonify({
                "ok": False,
                "error": "scores.c, scores.i, and scores.kappa are required",
            }), 400

        s = c + kappa * i
        regime = classify_regime(c, i, kappa)

        # Accept optional confidence and mode for confidence-aware policy
        confidence = body.get("confidence", 0.65)
        mode = body.get("mode", "black-box")

        snapshot = ScoreSnapshot(
            c=c, i=i, kappa=kappa, s=s, regime=regime,
            trace_id=body.get("trace_id"),
            confidence=confidence,
            mode=mode,
        )
        action = evaluate_policy(snapshot)
        return jsonify({
            "ok": True,
            "scores": {"c": c, "i": i, "kappa": kappa, "s": round(s, 4)},
            "regime": regime,
            "confidence": round(confidence, 4),
            "mode": mode,
            "policy": {
                "action": action.action,
                "reason": action.reason,
                "parameters": action.parameters,
            },
        }), 200

    return app
