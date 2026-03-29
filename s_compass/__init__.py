"""
S Compass — runtime observability and control layer for AI systems.

Based on the URP S-functional  S = C + κI  (see Docs/S-Compass-System-Design.md).

Quick start::

    from s_compass import SCompassGateway, StepInput

    gw = SCompassGateway()
    gw.start_session("sess_001")

    result = gw.submit_step(StepInput(
        session_id="sess_001",
        prompt="Explain the S Compass.",
        output_text="S Compass is a telemetry and policy layer ...",
    ))
    print(result["scores"], result["regime"])
"""

from .gateway import SCompassGateway
from .schemas import (
    Claim,
    Event,
    Evidence,
    GrayBoxSignals,
    GraphEdge,
    PolicyAction,
    RetrievedChunk,
    ScoreSnapshot,
    StepInput,
    VALID_EVENT_TYPES,
)
from .estimators import (
    capacity_field,
    estimate_c,
    estimate_i,
    estimate_kappa,
    normalize,
)
from .estimators_graybox import (
    estimate_c_graybox,
    estimate_i_graybox,
    estimate_kappa_graybox,
)
from .scoring import classify_regime, score_step, score_step_dict
from .policy import evaluate as evaluate_policy
from .store import EvaluationStore
from .extraction import extract_claims, link_evidence, extract_and_link
from .graph import (
    analyse_coherence,
    build_coherence_graph,
    claim_grounding_ratio,
    graph_density,
    graph_to_dict,
)
from .api import create_app

__all__ = [
    # Gateway
    "SCompassGateway",
    # Schemas
    "Claim",
    "Event",
    "Evidence",
    "GrayBoxSignals",
    "GraphEdge",
    "PolicyAction",
    "RetrievedChunk",
    "ScoreSnapshot",
    "StepInput",
    "VALID_EVENT_TYPES",
    # Estimators (black-box)
    "capacity_field",
    "estimate_c",
    "estimate_i",
    "estimate_kappa",
    "normalize",
    # Estimators (gray-box)
    "estimate_c_graybox",
    "estimate_i_graybox",
    "estimate_kappa_graybox",
    # Scoring
    "classify_regime",
    "score_step",
    "score_step_dict",
    # Policy
    "evaluate_policy",
    # Store
    "EvaluationStore",
    # Extraction
    "extract_claims",
    "link_evidence",
    "extract_and_link",
    # Graph
    "analyse_coherence",
    "build_coherence_graph",
    "claim_grounding_ratio",
    "graph_density",
    "graph_to_dict",
    # API
    "create_app",
]
