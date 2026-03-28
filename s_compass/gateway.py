"""
gateway.py

S Compass Gateway — the main entry point (Design-doc §4.1, §5).

Ties together telemetry normalisation, scoring, policy evaluation, and
the evaluation store into a single high-level API that application code
can call per inference step.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .schemas import Event, PolicyAction, ScoreSnapshot, StepInput
from .scoring import score_step
from .policy import evaluate as evaluate_policy
from .store import EvaluationStore
from .telemetry import normalize_event


class SCompassGateway:
    """High-level facade for the S Compass pipeline.

    Typical usage::

        gw = SCompassGateway()
        gw.start_session("sess_001", metadata={"app": "research-assistant"})
        result = gw.submit_step(step_input)
        print(result["scores"], result["regime"], result["policy"])
    """

    def __init__(self, store: Optional[EvaluationStore] = None) -> None:
        self.store = store or EvaluationStore()

    # -- session management -------------------------------------------------

    def start_session(
        self,
        session_id: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, object]:
        """Start a new traced session (Design-doc §8.1)."""
        self.store.start_session(session_id, metadata)
        evt = normalize_event(
            "session.started",
            session_id=session_id,
            trace_id=session_id,
            payload={"metadata": metadata or {}},
        )
        self.store.add_event(session_id, evt)
        return {"ok": True, "session_id": session_id}

    # -- step submission ----------------------------------------------------

    def submit_step(self, step: StepInput) -> Dict[str, object]:
        """Submit an inference step, score it, and return results.

        This is the primary runtime entry point (Design-doc §5 flow,
        API §8.2).  It:

        1. Records telemetry events.
        2. Computes C, I, κ, and S.
        3. Classifies the behavioural regime.
        4. Evaluates policy.
        5. Persists everything in the store.

        Returns a dict matching the API §8.2 response schema.
        """
        session_id = step.session_id

        # 1. Telemetry events
        prompt_evt = normalize_event(
            "prompt.received",
            session_id=session_id,
            trace_id=step.trace_id,
            payload={"prompt": step.prompt},
            step_id=step.step_id,
        )
        model_evt = normalize_event(
            "model.completed",
            session_id=session_id,
            trace_id=step.trace_id,
            payload={"output_text": step.output_text, "model": step.model_name},
            step_id=step.step_id,
        )
        self.store.add_event(session_id, prompt_evt)
        self.store.add_event(session_id, model_evt)

        # 2-3. Score
        snapshot: ScoreSnapshot = score_step(step)
        self.store.add_score(session_id, snapshot)

        # 4. Policy
        policy: PolicyAction = evaluate_policy(snapshot)
        self.store.add_policy(session_id, policy)

        if policy.action != "none":
            pol_evt = normalize_event(
                "policy.recommended",
                session_id=session_id,
                trace_id=step.trace_id,
                payload={
                    "action": policy.action,
                    "reason": policy.reason,
                    "parameters": policy.parameters,
                },
                step_id=step.step_id,
            )
            self.store.add_event(session_id, pol_evt)

        # 5. Return
        return {
            "ok": True,
            "scores": {
                "c": snapshot.c,
                "i": snapshot.i,
                "kappa": snapshot.kappa,
                "s": snapshot.s,
            },
            "regime": snapshot.regime,
            "policy": {"action": policy.action, "reason": policy.reason},
        }

    # -- read endpoints -----------------------------------------------------

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, object]]:
        """Return aggregate session summary (Design-doc §8.3)."""
        return self.store.session_summary(session_id)

    def get_session_scores(self, session_id: str) -> List[ScoreSnapshot]:
        """Return the full score timeline for a session."""
        return self.store.get_scores(session_id)
