"""
gateway.py

S Compass Gateway — the main entry point (Design-doc §4.1, §5).

Ties together telemetry normalisation, claim extraction, coherence graph
building, scoring, policy evaluation, and the evaluation store into a
single high-level API that application code can call per inference step.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .schemas import Event, PolicyAction, RetrievedChunk, ScoreSnapshot, StepInput
from .scoring import score_step
from .policy import evaluate as evaluate_policy
from .store import EvaluationStore
from .telemetry import normalize_event
from .extraction import extract_and_link
from .graph import analyse_coherence
from .particles import (
    ParticleDescription,
    PeriodicTable,
    compose_particle_description,
    parse_particle_properties,
    properties_to_retrieved_context,
)


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
        # trace_id → coherence analysis dict (Design-doc §8.4)
        self._trace_graphs: Dict[str, Dict[str, Any]] = {}
        self.periodic_table = PeriodicTable()

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
        2. Extracts claims and links evidence (§4.4).
        3. Builds the coherence graph (§4.4, §8.4).
        4. Computes C, I, κ, and S.
        5. Classifies the behavioural regime.
        6. Evaluates policy.
        7. Persists everything in the store.

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

        # 2. Extract claims and link evidence
        claims, evidences, edges = extract_and_link(step)

        # Emit claim.extracted events
        for claim in claims:
            claim_evt = normalize_event(
                "claim.extracted",
                session_id=session_id,
                trace_id=step.trace_id,
                payload={"claim_id": claim.claim_id, "text": claim.text},
                step_id=step.step_id,
            )
            self.store.add_event(session_id, claim_evt)

        # 2b. Feed extracted claims back into the step so the I estimator
        #     can use them for citation-coverage and support-graph metrics.
        if claims and not step.claims:
            step.claims = list(claims)

        # 3. Coherence graph
        coherence = analyse_coherence(claims, evidences, edges)
        self._trace_graphs[step.trace_id] = coherence

        # 4-5. Score
        # Auto-detect gray-box mode when signals are present.
        if step.gray_box is not None and step.mode == "black-box":
            step.mode = "gray-box"

        # Auto-detect white-box mode when signals are present.
        if step.white_box is not None and step.mode in ("black-box", "gray-box"):
            step.mode = "white-box"

        # Emit gray_box.received telemetry event when signals are present.
        if step.gray_box is not None:
            gb = step.gray_box
            signal_summary = {}
            for k in ("logprobs", "token_entropy", "relevance_scores",
                       "tool_confidence", "decoding_instability"):
                val = getattr(gb, k)
                if k == "decoding_instability":
                    signal_summary[k] = val is not None
                else:
                    signal_summary[k] = val is not None and bool(val)
            gb_evt = normalize_event(
                "gray_box.received",
                session_id=session_id,
                trace_id=step.trace_id,
                payload={"signals_present": signal_summary, "mode": step.mode},
                step_id=step.step_id,
            )
            self.store.add_event(session_id, gb_evt)

        # Emit white_box.received telemetry event when signals are present.
        if step.white_box is not None:
            wb = step.white_box
            wb_signal_summary = {}
            for k in ("attention_entropy", "attention_variance",
                       "head_confidence", "kv_norm", "activation_sparsity",
                       "gradient_norm", "residual_coherence"):
                val = getattr(wb, k)
                if k == "residual_coherence":
                    wb_signal_summary[k] = val is not None
                else:
                    wb_signal_summary[k] = val is not None and bool(val)
            wb_evt = normalize_event(
                "white_box.received",
                session_id=session_id,
                trace_id=step.trace_id,
                payload={"signals_present": wb_signal_summary, "mode": step.mode},
                step_id=step.step_id,
            )
            self.store.add_event(session_id, wb_evt)

        snapshot: ScoreSnapshot = score_step(step)
        self.store.add_score(session_id, snapshot)

        # 6. Policy
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

        # 7. Return
        return {
            "ok": True,
            "scores": {
                "c": snapshot.c,
                "i": snapshot.i,
                "kappa": snapshot.kappa,
                "s": snapshot.s,
            },
            "regime": snapshot.regime,
            "confidence": snapshot.confidence,
            "mode": step.mode,
            "policy": {"action": policy.action, "reason": policy.reason},
        }

    # -- read endpoints -----------------------------------------------------

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, object]]:
        """Return aggregate session summary (Design-doc §8.3)."""
        return self.store.session_summary(session_id)

    def get_session_scores(self, session_id: str) -> List[ScoreSnapshot]:
        """Return the full score timeline for a session."""
        return self.store.get_scores(session_id)

    def get_trace_graph(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Return the coherence graph analysis for a trace (Design-doc §8.4)."""
        return self._trace_graphs.get(trace_id)

    # -- particle describer ---------------------------------------------------

    def submit_particle_description(
        self,
        *,
        element_name: str,
        atomic_number: int,
        properties: Optional[List[Dict[str, Any]]] = None,
        description_text: str = "",
        retrieved_context: Optional[List[RetrievedChunk]] = None,
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        prompt: Optional[str] = None,
        mode: str = "black-box",
    ) -> Dict[str, object]:
        """Create and score a particle description, then store it in the table."""
        particle_properties = parse_particle_properties(
            atomic_number=atomic_number,
            description_text=description_text,
            retrieved_context=retrieved_context,
            raw_properties=properties,
        )

        context = list(retrieved_context or [])
        if not context:
            context = properties_to_retrieved_context(element_name, particle_properties)

        rendered_description = description_text.strip() or compose_particle_description(
            element_name,
            atomic_number,
            particle_properties,
        )

        step = StepInput(
            session_id=session_id or "particle_table",
            prompt=prompt or f"Describe element {element_name} through the S-functional framework.",
            output_text=rendered_description,
            retrieved_context=context,
            mode=mode,
        )
        if trace_id:
            step.trace_id = trace_id

        result = self.submit_step(step)
        particle = ParticleDescription(
            element_name=element_name,
            atomic_number=atomic_number,
            description_text=rendered_description,
            properties=particle_properties,
            scores=dict(result["scores"]),
            regime=str(result["regime"]),
            confidence=float(result["confidence"]),
            mode=str(result["mode"]),
            session_id=step.session_id,
            trace_id=step.trace_id,
        )
        self.periodic_table.add_description(particle)
        return {
            "ok": True,
            "particle": particle.to_dict(),
            "scores": result["scores"],
            "regime": result["regime"],
            "confidence": result["confidence"],
            "mode": result["mode"],
            "policy": result["policy"],
        }

    def get_particle_description(self, atomic_number: int) -> Optional[Dict[str, Any]]:
        """Return a stored particle description by atomic number."""
        particle = self.periodic_table.get_particle(atomic_number)
        return particle.to_dict() if particle is not None else None

    def get_periodic_table(self) -> Dict[str, Any]:
        """Return the current periodic-table view."""
        return self.periodic_table.to_dict()
