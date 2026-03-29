"""
schemas.py

Canonical domain schemas for S Compass, based on Docs/S-Compass-System-Design.md
sections 9 and 10.

All data objects are plain dataclasses so they stay dependency-free and
serialisable.  Timestamps default to ISO-8601 UTC strings.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Canonical event envelope (Section 9)
# ---------------------------------------------------------------------------

VALID_EVENT_TYPES = frozenset(
    {
        "session.started",
        "prompt.received",
        "retrieval.completed",
        "model.started",
        "model.completed",
        "tool.called",
        "tool.completed",
        "claim.extracted",
        "policy.recommended",
        "policy.applied",
        "feedback.received",
        "gray_box.received",
        "white_box.received",
    }
)


@dataclass
class Event:
    """Canonical telemetry event (Design-doc §9)."""

    event_type: str
    timestamp: str
    session_id: str
    trace_id: str
    payload: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    step_id: Optional[str] = None
    actor_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Domain objects (Section 10)
# ---------------------------------------------------------------------------


@dataclass
class Claim:
    """An extracted claim from model output (Design-doc §10.1)."""

    text: str
    claim_type: str = "assertion"
    confidence: float = 1.0
    provenance: Optional[Dict[str, str]] = None
    claim_id: str = field(default_factory=lambda: f"claim_{uuid.uuid4().hex[:8]}")


@dataclass
class Evidence:
    """A piece of supporting/contradicting evidence (Design-doc §10.2)."""

    doc_id: str
    text: str
    support_type: str = "direct"
    weight: float = 1.0
    chunk_id: Optional[str] = None
    evidence_id: str = field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:8]}")


@dataclass
class GraphEdge:
    """An edge in the support/contradiction graph (Design-doc §10.3)."""

    source_id: str
    target_id: str
    edge_type: str = "supported_by"
    weight: float = 1.0
    edge_id: str = field(default_factory=lambda: f"edge_{uuid.uuid4().hex[:8]}")


@dataclass
class ScoreSnapshot:
    """A point-in-time score record (Design-doc §10.4)."""

    c: float
    i: float
    kappa: float
    s: float
    regime: str
    trace_id: Optional[str] = None
    confidence: float = 1.0
    mode: str = "black-box"


@dataclass
class PolicyAction:
    """A recommended or applied policy action (Design-doc §10.5)."""

    action: str
    reason: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    applied: bool = False
    policy_id: str = field(default_factory=lambda: f"pol_{uuid.uuid4().hex[:8]}")


# ---------------------------------------------------------------------------
# Step telemetry (high-level wrapper matching API §8.2)
# ---------------------------------------------------------------------------


@dataclass
class RetrievedChunk:
    """One chunk from a retrieval result."""

    doc_id: str
    text: str
    score: float = 0.0
    chunk_id: Optional[str] = None


@dataclass
class GrayBoxSignals:
    """Optional gray-box telemetry signals (Design-doc §6.2, §19.1).

    These signals are available when the model provider exposes richer
    introspection than pure black-box mode.  All fields are optional so
    that callers can supply whichever subset their provider supports.
    """

    logprobs: Optional[List[float]] = None
    """Per-token log-probabilities from the language model."""

    token_entropy: Optional[List[float]] = None
    """Per-token Shannon entropy (nats or bits, provider-dependent)."""

    relevance_scores: Optional[List[float]] = None
    """Per-chunk relevance scores from the retriever."""

    tool_confidence: Optional[Dict[str, float]] = None
    """Mapping of tool name → confidence score in [0, 1]."""

    decoding_instability: Optional[float] = None
    """Scalar instability signal (e.g. temperature/top-k adjustments)."""


@dataclass
class WhiteBoxSignals:
    """Optional white-box telemetry signals (Design-doc §6.3, v3 outline).

    These signals are available when running open/local models that expose
    internal architecture state.  All fields are optional so that callers
    can supply whichever subset their model runtime supports.
    """

    attention_entropy: Optional[List[float]] = None
    """Per-layer attention entropy (nats or bits)."""

    attention_variance: Optional[List[float]] = None
    """Per-layer attention variance across heads."""

    head_confidence: Optional[Dict[str, float]] = None
    """Mapping of head identifier → confidence score in [0, 1]."""

    kv_norm: Optional[List[float]] = None
    """Key-value cache norms per layer."""

    activation_sparsity: Optional[List[float]] = None
    """Per-layer activation sparsity ratio in [0, 1]."""

    gradient_norm: Optional[List[float]] = None
    """Gradient or Fisher-diagonal norms per layer."""

    residual_coherence: Optional[float] = None
    """Scalar residual-stream coherence vs. support signals in [0, 1]."""

    layer_count: Optional[int] = None
    """Number of model layers (for normalisation)."""


@dataclass
class StepInput:
    """All telemetry for a single inference step (Design-doc §8.2, §19.1)."""

    session_id: str
    prompt: str
    output_text: str
    step_id: str = field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    trace_id: str = field(default_factory=lambda: f"trace_{uuid.uuid4().hex[:8]}")
    retrieved_context: List[RetrievedChunk] = field(default_factory=list)
    citations: List[Dict[str, str]] = field(default_factory=list)
    claims: List[Claim] = field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    context_tokens_used: int = 0
    context_window: int = 4096
    latency_ms: float = 0.0
    latency_history: List[float] = field(default_factory=list)
    tool_failure_count: int = 0
    tool_total_count: int = 0
    history: List[str] = field(default_factory=list)
    gray_box: Optional[GrayBoxSignals] = None
    white_box: Optional[WhiteBoxSignals] = None
    mode: str = "black-box"
