"""
estimators_graybox.py

Gray-box C, I, and κ estimators for S Compass (Design-doc §6.2).

When logprobs, relevance scores, token-level uncertainty, or tool
confidence metrics are available the gray-box estimators provide
higher-fidelity measurements than the black-box defaults.  Each
estimator gracefully falls back to its black-box counterpart for any
missing signal.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import numpy as np

from .schemas import Claim, GrayBoxSignals, RetrievedChunk, StepInput
from .extraction import detect_contradictions
from .estimators import (
    _anti_repetition,
    _claim_novelty,
    _citation_coverage,
    _cosine_token_similarity,
    _cross_turn_consistency,
    _retrieval_echo_novelty,
    _semantic_novelty,
    _sentence_structure_novelty,
    _support_graph_connectivity,
    _token_entropy,
    capacity_field,
    normalize,
)


# ---------------------------------------------------------------------------
# Gray-box helpers
# ---------------------------------------------------------------------------

def _logprob_entropy(logprobs: List[float]) -> float:
    """Compute normalised entropy from per-token log-probabilities.

    Each log-probability represents the model's confidence in the chosen
    token.  We convert to probabilities, compute the mean pointwise
    entropy, and normalise to [0, 1].

    Higher values indicate more *uniform* (uncertain) token selections,
    which correlates with higher novelty / distinction (C).
    """
    if not logprobs:
        return 0.0
    # Convert log-probs to probabilities and compute pointwise entropy.
    # log-probs are typically negative; clamp to avoid math errors.
    probs = [min(math.exp(lp), 1.0) for lp in logprobs]
    # Pointwise self-information scaled by probability
    entropies = [-p * math.log2(p) if 0 < p < 1 else 0.0 for p in probs]
    mean_ent = sum(entropies) / len(entropies)
    # Normalise: max possible pointwise entropy is 1 bit (at p=0.5)
    return float(np.clip(mean_ent, 0.0, 1.0))


def _token_uncertainty(token_entropy: List[float]) -> float:
    """Mean of provider-supplied per-token entropy values, normalised."""
    if not token_entropy:
        return 0.0
    mean_ent = sum(token_entropy) / len(token_entropy)
    # Assume values are already in [0, ∞); softmax-normalise
    return float(1.0 - math.exp(-mean_ent))


def _logprob_variance(logprobs: List[float]) -> float:
    """Variance of log-probabilities as an instability signal.

    Higher variance ⇒ the model oscillated between confident and
    uncertain tokens, signalling decoding instability (lowers κ).
    Returns a value in [0, 1] via sigmoid squashing.
    """
    if not logprobs or len(logprobs) < 2:
        return 0.0
    var = float(np.var(logprobs))
    # Sigmoid squash so result sits in [0, 1]
    return float(2.0 / (1.0 + math.exp(-var)) - 1.0)


def _relevance_quality(
    relevance_scores: Optional[List[float]],
    retrieval: List[RetrievedChunk],
) -> float:
    """Aggregate retriever relevance quality.

    Prefers explicit ``relevance_scores`` from gray-box signals.  Falls
    back to the ``.score`` field on each :class:`RetrievedChunk` when
    gray-box scores are absent.
    """
    scores: List[float] = []
    if relevance_scores:
        scores = list(relevance_scores)
    elif retrieval:
        scores = [c.score for c in retrieval]
    if not scores:
        return 0.5  # neutral prior
    return float(np.clip(sum(scores) / len(scores), 0.0, 1.0))


def _tool_confidence_aggregate(tool_confidence: Optional[Dict[str, float]]) -> float:
    """Mean tool confidence, defaulting to 1.0 when absent."""
    if not tool_confidence:
        return 1.0
    vals = list(tool_confidence.values())
    if not vals:
        return 1.0
    return float(np.clip(sum(vals) / len(vals), 0.0, 1.0))


def _contradiction_penalty(claims: List[Claim]) -> float:
    """Compute a contradiction penalty in [0, 1] from extracted claims.

    Uses :func:`detect_contradictions` to find claim pairs that have high
    topic overlap but opposite negation polarity.  The penalty is the
    weighted fraction of claims involved in at least one contradiction,
    capped at 0.30 to avoid dominating the I score from false positives
    in the heuristic negation detector.

    Implements the ``- contradiction_penalty`` term from Design-doc §11.
    """
    if len(claims) < 2:
        return 0.0
    edges = detect_contradictions(claims)
    if not edges:
        return 0.0
    involved = {e.source_id for e in edges} | {e.target_id for e in edges}
    # Average edge weight captures how strong the overlaps are
    avg_weight = sum(e.weight for e in edges) / len(edges)
    raw = (len(involved) / len(claims)) * avg_weight
    # Cap at 0.30 to prevent false positives from dominating I
    return min(raw, 0.30)


def _tool_path_diversity(tool_calls: List[Dict[str, Any]]) -> float:
    """Measure diversity of tool-call paths (Design-doc §19.2).

    Higher diversity (more distinct tools used) indicates more creative,
    multi-source synthesis.  Returns a value in [0, 1].
    """
    if not tool_calls:
        return 0.5  # neutral prior when no tools used
    names = [tc.get("name", tc.get("tool", "unknown")) for tc in tool_calls]
    unique = len(set(names))
    total = len(names)
    if total <= 1:
        return 0.5
    # Normalised diversity: unique/total, but single unique tool = low diversity
    return float(np.clip(unique / total, 0.0, 1.0))


def _retrieval_overload(
    relevance_scores: Optional[List[float]],
    retrieval: List[RetrievedChunk],
) -> float:
    """Retrieval overload stress signal (Design-doc §19.2).

    High breadth (many chunks) with low mean relevance signals retrieval
    saturation, adding capacity pressure.  Returns a stress value in [0, 1]
    where 0 = no overload and 1 = maximal overload.
    """
    scores: List[float] = []
    if relevance_scores:
        scores = list(relevance_scores)
    elif retrieval:
        scores = [c.score for c in retrieval]
    if not scores:
        return 0.0  # no retrieval = no overload
    mean_relevance = sum(scores) / len(scores)
    low_hit_rate = 1.0 - mean_relevance
    # Scale by breadth: more chunks with low relevance = more overload
    breadth_factor = min(len(scores) / 10.0, 1.0)
    return float(np.clip(low_hit_rate * breadth_factor, 0.0, 1.0))


def signal_coverage(gb: Optional[GrayBoxSignals]) -> float:
    """Fraction of gray-box signal slots that are populated.

    Used by the scoring engine to compute dynamic confidence.  Returns
    a value in [0, 1] representing the weighted coverage of available
    gray-box signals.
    """
    if gb is None:
        return 0.0
    _SIGNAL_WEIGHTS = {
        "logprobs": 0.30,
        "token_entropy": 0.20,
        "relevance_scores": 0.20,
        "tool_confidence": 0.15,
        "decoding_instability": 0.15,
    }
    present = 0.0
    if gb.logprobs:
        present += _SIGNAL_WEIGHTS["logprobs"]
    if gb.token_entropy:
        present += _SIGNAL_WEIGHTS["token_entropy"]
    if gb.relevance_scores:
        present += _SIGNAL_WEIGHTS["relevance_scores"]
    if gb.tool_confidence:
        present += _SIGNAL_WEIGHTS["tool_confidence"]
    if gb.decoding_instability is not None:
        present += _SIGNAL_WEIGHTS["decoding_instability"]
    return present


# ---------------------------------------------------------------------------
# Gray-box C estimator (Design-doc §4.3, §6.2)
# ---------------------------------------------------------------------------

def estimate_c_graybox(step: StepInput) -> float:
    """Estimate Distinction / novelty (C) using gray-box signals.

    Enriches the black-box C estimate with:
    * logprob-derived entropy (replaces token-frequency entropy)
    * token-level uncertainty from provider-supplied entropy
    * tool-call path diversity (Design-doc §19.2)
    * sentence-level structural novelty
    * retrieval-echo novelty

    When logprob-based entropy is available it receives higher weight
    than the black-box fallback components.
    """
    gb: Optional[GrayBoxSignals] = step.gray_box

    # Entropy component: prefer logprobs → token_entropy → black-box proxy
    has_logprob_signal = False
    if gb and gb.logprobs:
        entropy_signal = _logprob_entropy(gb.logprobs)
        has_logprob_signal = True
    elif gb and gb.token_entropy:
        entropy_signal = _token_uncertainty(gb.token_entropy)
        has_logprob_signal = True
    else:
        entropy_signal = _token_entropy(step.output_text)

    tool_diversity = _tool_path_diversity(step.tool_calls)

    components = [
        entropy_signal,
        _semantic_novelty(step.output_text, step.retrieved_context),
        _claim_novelty(step.claims, step.citations),
        _anti_repetition(step.output_text),
        tool_diversity,
        _sentence_structure_novelty(step.output_text),
        _retrieval_echo_novelty(step.output_text, step.retrieved_context),
    ]

    # Give logprob entropy higher weight when available (Design-doc §6.2)
    if has_logprob_signal:
        weights = [0.22, 0.10, 0.10, 0.10, 0.10, 0.19, 0.19]
    else:
        weights = [0.14, 0.10, 0.10, 0.14, 0.10, 0.21, 0.21]

    return normalize(components, weights=weights)


# ---------------------------------------------------------------------------
# Gray-box I estimator (Design-doc §4.4, §6.2)
# ---------------------------------------------------------------------------

def estimate_i_graybox(step: StepInput) -> float:
    """Estimate Integration / coherence (I) using gray-box signals.

    Enriches the black-box I estimate with:
    * retriever relevance quality
    * contradiction penalty (Design-doc §11)

    When explicit relevance scores are available they receive higher weight.
    """
    gb: Optional[GrayBoxSignals] = step.gray_box

    relevance = _relevance_quality(
        gb.relevance_scores if gb else None,
        step.retrieved_context,
    )

    has_explicit_relevance = gb is not None and gb.relevance_scores is not None

    # Contradiction penalty (Design-doc §11: I = ... - contradiction_penalty)
    penalty = _contradiction_penalty(step.claims)

    components = [
        _citation_coverage(step.claims, step.citations),
        _support_graph_connectivity(step.claims, step.citations),
        _cross_turn_consistency(step.output_text, step.history),
        relevance,
    ]

    # Give relevance higher weight when explicit scores are available
    if has_explicit_relevance:
        weights = [0.25, 0.20, 0.20, 0.35]
    else:
        weights = [0.25, 0.25, 0.25, 0.25]

    raw = normalize(components, weights=weights)
    return float(np.clip(raw - penalty, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Gray-box κ estimator (Design-doc §4.5, §6.2)
# ---------------------------------------------------------------------------

def estimate_kappa_graybox(step: StepInput) -> float:
    """Estimate usable capacity (κ) using gray-box signals.

    Extends the black-box κ with:
    * logprob variance as a token-level instability signal
    * tool confidence metrics
    * decoding instability
    * retrieval overload (Design-doc §19.2)
    """
    gb: Optional[GrayBoxSignals] = step.gray_box

    context_load = (
        step.context_tokens_used / step.context_window
        if step.context_window > 0
        else 0.0
    )

    # Latency dispersion
    if step.latency_history and len(step.latency_history) > 1:
        latency_std = float(np.std(step.latency_history))
        mean_lat = float(np.mean(step.latency_history))
        latency_cv = latency_std / mean_lat if mean_lat > 0 else 0.0
    else:
        latency_cv = 0.0

    tool_failure_rate = (
        step.tool_failure_count / step.tool_total_count
        if step.tool_total_count > 0
        else 0.0
    )

    # Gray-box stress terms (default to 0 / benign when absent)
    lp_instability = _logprob_variance(gb.logprobs) if gb and gb.logprobs else 0.0
    tc = _tool_confidence_aggregate(gb.tool_confidence if gb else None)
    tool_uncertainty = 1.0 - tc  # invert: higher uncertainty = more stress
    decoding_stress = gb.decoding_instability if gb and gb.decoding_instability else 0.0

    # Retrieval overload (Design-doc §19.2)
    ret_overload = _retrieval_overload(
        gb.relevance_scores if gb else None,
        step.retrieved_context,
    )

    # Extended σ² with gray-box terms
    sigma_sq = (
        0.25 * context_load ** 2
        + 0.15 * latency_cv ** 2
        + 0.10 * tool_failure_rate ** 2
        + 0.15 * lp_instability ** 2
        + 0.10 * tool_uncertainty ** 2
        + 0.10 * decoding_stress ** 2
        + 0.15 * ret_overload ** 2
    )
    beta = 5.0
    return 1.0 / (1.0 + beta * sigma_sq)
