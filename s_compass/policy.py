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

    When ``snapshot.confidence`` is high (≥ 0.80, typically from gray-box
    or white-box signals) the policy produces more decisive interventions.
    Lower confidence yields softer nudges.

    In white-box mode (``snapshot.mode == "white-box"``), policy hooks can
    recommend layer-targeted interventions such as head dropout or routing
    to safer model variants (Design-doc §6.3 v3 outline).
    """
    regime = snapshot.regime
    high_confidence = snapshot.confidence >= 0.80
    is_white_box = snapshot.mode == "white-box"

    if regime == "hallucination-risk":
        if is_white_box and high_confidence:
            return PolicyAction(
                action="require_grounded_regeneration",
                reason="Integration below threshold; high hallucination risk (white-box layerwise detection).",
                parameters={
                    "temperature": 0.10,
                    "max_retrieval_chunks": 6,
                    "citation_mode": "strict",
                    "head_dropout": 0.05,
                    "route_to_safer_variant": True,
                },
                trace_id=snapshot.trace_id,
            )
        if high_confidence:
            return PolicyAction(
                action="require_grounded_regeneration",
                reason="Integration below threshold; high hallucination risk (high-confidence detection).",
                parameters={
                    "temperature": 0.15,
                    "max_retrieval_chunks": 6,
                    "citation_mode": "strict",
                },
                trace_id=snapshot.trace_id,
            )
        return PolicyAction(
            action="require_grounded_regeneration",
            reason="Integration below threshold; high hallucination risk.",
            parameters={
                "temperature": 0.3,
                "max_retrieval_chunks": 5,
                "citation_mode": "preferred",
            },
            trace_id=snapshot.trace_id,
        )

    if regime == "collapse":
        if snapshot.kappa < _K_OVERLOAD_THRESHOLD:
            if is_white_box and high_confidence:
                return PolicyAction(
                    action="reduce_load_and_retry",
                    reason="System capacity critically low; layerwise instability detected.",
                    parameters={
                        "max_retrieval_chunks": 2,
                        "temperature": 0.3,
                        "head_dropout": 0.10,
                        "route_to_safer_variant": True,
                    },
                    trace_id=snapshot.trace_id,
                )
            return PolicyAction(
                action="reduce_load_and_retry",
                reason="System capacity critically low; reduce retrieval breadth.",
                parameters={
                    "max_retrieval_chunks": 2 if high_confidence else 3,
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
        if is_white_box and high_confidence:
            return PolicyAction(
                action="increase_temperature",
                reason="Output is repetitive; applying layerwise diversity adjustments.",
                parameters={
                    "temperature": 0.85,
                    "rep_pen_adjustment": 0.10,
                },
                trace_id=snapshot.trace_id,
            )
        return PolicyAction(
            action="increase_temperature",
            reason="Output is repetitive; raising temperature to encourage diversity.",
            parameters={"temperature": 0.8 if high_confidence else 0.7},
            trace_id=snapshot.trace_id,
        )

    # creative-grounded (or unclassified healthy) → no intervention
    return PolicyAction(
        action="none",
        reason="System is operating in a healthy regime.",
        trace_id=snapshot.trace_id,
    )
