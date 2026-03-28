"""
policy.py

Policy engine for S Compass (Design-doc §4.7).

Translates score snapshots into actionable recommendations.
"""

from __future__ import annotations

from .schemas import PolicyAction, ScoreSnapshot


# ---------------------------------------------------------------------------
# Threshold-based policy rules (Design-doc §4.7)
# ---------------------------------------------------------------------------

_I_CITE_THRESHOLD = 0.35
_K_OVERLOAD_THRESHOLD = 0.40
_C_LOW_THRESHOLD = 0.30


def evaluate(snapshot: ScoreSnapshot) -> PolicyAction:
    """Return a policy recommendation given the current scores.

    Rules mirror the design-doc §4.7 interventions:

    * *hallucination-risk* → require grounded regeneration with citations
    * *collapse* with low κ → reduce retrieval breadth and retry
    * *rigid* → raise temperature to increase novelty
    * Otherwise → no action
    """
    regime = snapshot.regime

    if regime == "hallucination-risk":
        return PolicyAction(
            action="require_grounded_regeneration",
            reason="Integration below threshold; high hallucination risk.",
            parameters={
                "temperature": 0.2,
                "max_retrieval_chunks": 5,
                "citation_mode": "strict",
            },
            trace_id=snapshot.trace_id,
        )

    if regime == "collapse":
        if snapshot.kappa < _K_OVERLOAD_THRESHOLD:
            return PolicyAction(
                action="reduce_load_and_retry",
                reason="System capacity critically low; reduce retrieval breadth.",
                parameters={
                    "max_retrieval_chunks": 3,
                    "temperature": 0.3,
                },
                trace_id=snapshot.trace_id,
            )
        return PolicyAction(
            action="increase_novelty",
            reason="Both distinction and integration are low; try broader generation.",
            parameters={"temperature": 0.8},
            trace_id=snapshot.trace_id,
        )

    if regime == "rigid":
        return PolicyAction(
            action="increase_temperature",
            reason="Output is repetitive; raising temperature to encourage diversity.",
            parameters={"temperature": 0.7},
            trace_id=snapshot.trace_id,
        )

    # creative-grounded (or unclassified healthy) → no intervention
    return PolicyAction(
        action="none",
        reason="System is operating in a healthy regime.",
        trace_id=snapshot.trace_id,
    )
