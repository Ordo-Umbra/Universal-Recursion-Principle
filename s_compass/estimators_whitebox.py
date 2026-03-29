"""
estimators_whitebox.py

White-box C, I, and κ estimators for S Compass (Design-doc §6.3, v3 outline).

When attention maps, KV norms, activation sparsity, gradient norms, or
residual-stream coherence metrics are available the white-box estimators
provide the highest-fidelity measurements.  Each estimator gracefully falls
back to gray-box or black-box sub-components for any missing signal.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import numpy as np

from .schemas import Claim, GrayBoxSignals, RetrievedChunk, StepInput, WhiteBoxSignals
from .extraction import detect_contradictions
from .estimators import (
    _anti_repetition,
    _claim_novelty,
    _citation_coverage,
    _cross_turn_consistency,
    _retrieval_echo_novelty,
    _semantic_novelty,
    _sentence_structure_novelty,
    _support_graph_connectivity,
    _token_entropy,
    normalize,
)
from .estimators_graybox import (
    _contradiction_penalty,
    _logprob_entropy,
    _logprob_variance,
    _relevance_quality,
    _retrieval_overload,
    _token_uncertainty,
    _tool_confidence_aggregate,
    _tool_path_diversity,
)


# ---------------------------------------------------------------------------
# White-box helpers
# ---------------------------------------------------------------------------

def _attention_entropy_mean(attention_entropy: List[float]) -> float:
    """Mean per-layer attention entropy, normalised to [0, 1].

    Higher entropy across attention heads indicates more diverse,
    exploratory attention patterns — correlated with distinction (C).
    """
    if not attention_entropy:
        return 0.0
    mean_ent = sum(attention_entropy) / len(attention_entropy)
    # Sigmoid-normalise: moderate entropy ≈ 0.5, very high → 1.0
    return float(1.0 - math.exp(-mean_ent))


def _head_diversity(head_confidence: Optional[Dict[str, float]]) -> float:
    """Branch diversity across attention heads.

    Measures how uniformly confident different heads are.  High variance
    (some heads very confident, others not) indicates specialisation;
    uniform confidence indicates redundancy.  We want *moderate* diversity.
    """
    if not head_confidence:
        return 0.5  # neutral prior
    vals = list(head_confidence.values())
    if len(vals) < 2:
        return 0.5
    mean_c = sum(vals) / len(vals)
    std_c = math.sqrt(sum((v - mean_c) ** 2 for v in vals) / len(vals))
    # Normalise: std in [0, 0.5] roughly; scale to [0, 1]
    return float(np.clip(std_c * 2.0, 0.0, 1.0))


def _activation_sparsity_mean(activation_sparsity: List[float]) -> float:
    """Mean activation sparsity across layers, in [0, 1].

    Higher sparsity indicates more selective, focused computation —
    correlates with higher distinction when moderate and collapse when
    extreme.
    """
    if not activation_sparsity:
        return 0.5  # neutral prior
    return float(np.clip(sum(activation_sparsity) / len(activation_sparsity), 0.0, 1.0))


def _attention_concentration(attention_entropy: List[float]) -> float:
    """Attention concentration — inverse of entropy, normalised.

    High concentration (low entropy) means attention is focused on specific
    tokens, which correlates with coherent integration (I) when the model
    is attending to relevant context.
    """
    if not attention_entropy:
        return 0.5  # neutral
    mean_ent = sum(attention_entropy) / len(attention_entropy)
    # Invert: low entropy → high concentration
    concentration = math.exp(-mean_ent)
    return float(np.clip(concentration, 0.0, 1.0))


def _residual_stream_coherence(residual_coherence: Optional[float]) -> float:
    """Residual stream coherence vs. retrieved/support signals.

    Directly measures how well the model's internal representation aligns
    with grounding material — a direct I signal.
    """
    if residual_coherence is None:
        return 0.5  # neutral
    return float(np.clip(residual_coherence, 0.0, 1.0))


def _head_connectivity(head_confidence: Optional[Dict[str, float]]) -> float:
    """Head connectivity structure — fraction of heads above threshold.

    Measures what proportion of attention heads are operating with
    meaningful confidence, indicating coherent information flow.
    """
    if not head_confidence:
        return 0.5
    vals = list(head_confidence.values())
    if not vals:
        return 0.5
    active = sum(1 for v in vals if v >= 0.3)
    return float(np.clip(active / len(vals), 0.0, 1.0))


def _attention_variance_stress(attention_variance: List[float]) -> float:
    """Attention variance and saturation stress signal.

    High variance across layers indicates unstable attention patterns,
    reducing usable capacity (κ).
    """
    if not attention_variance:
        return 0.0
    mean_var = sum(attention_variance) / len(attention_variance)
    # Sigmoid squash: moderate variance ≈ 0.3, high → 1.0
    return float(2.0 / (1.0 + math.exp(-5.0 * mean_var)) - 1.0)


def _kv_norm_stress(kv_norm: List[float]) -> float:
    """KV cache norm stress — detects exploding norms.

    Large or diverging KV norms indicate memory pressure or instability.
    We compute the coefficient of variation and normalise.
    """
    if not kv_norm or len(kv_norm) < 2:
        return 0.0
    mean_n = sum(kv_norm) / len(kv_norm)
    if mean_n <= 0:
        return 0.0
    std_n = math.sqrt(sum((v - mean_n) ** 2 for v in kv_norm) / len(kv_norm))
    cv = std_n / mean_n
    # Also penalise large absolute norms
    norm_penalty = float(np.clip(mean_n / 100.0, 0.0, 0.5))
    return float(np.clip(cv + norm_penalty, 0.0, 1.0))


def _gradient_norm_stress(gradient_norm: List[float]) -> float:
    """Gradient/Fisher norm stress — detects gradient instability.

    Large or highly variable gradient norms indicate training instability
    or model uncertainty about its own outputs.
    """
    if not gradient_norm:
        return 0.0
    mean_g = sum(gradient_norm) / len(gradient_norm)
    # Sigmoid squash: large norms → high stress
    return float(2.0 / (1.0 + math.exp(-mean_g)) - 1.0)


def wb_signal_coverage(wb: Optional[WhiteBoxSignals]) -> float:
    """Fraction of white-box signal slots that are populated.

    Used by the scoring engine to compute dynamic confidence for
    white-box mode.  Returns a weighted coverage in [0, 1].
    """
    if wb is None:
        return 0.0
    _SIGNAL_WEIGHTS = {
        "attention_entropy": 0.20,
        "attention_variance": 0.15,
        "head_confidence": 0.15,
        "kv_norm": 0.10,
        "activation_sparsity": 0.15,
        "gradient_norm": 0.10,
        "residual_coherence": 0.15,
    }
    present = 0.0
    if wb.attention_entropy:
        present += _SIGNAL_WEIGHTS["attention_entropy"]
    if wb.attention_variance:
        present += _SIGNAL_WEIGHTS["attention_variance"]
    if wb.head_confidence:
        present += _SIGNAL_WEIGHTS["head_confidence"]
    if wb.kv_norm:
        present += _SIGNAL_WEIGHTS["kv_norm"]
    if wb.activation_sparsity:
        present += _SIGNAL_WEIGHTS["activation_sparsity"]
    if wb.gradient_norm:
        present += _SIGNAL_WEIGHTS["gradient_norm"]
    if wb.residual_coherence is not None:
        present += _SIGNAL_WEIGHTS["residual_coherence"]
    return present


# ---------------------------------------------------------------------------
# White-box C estimator (Design-doc §6.3: per-layer predictive entropy,
# branch diversity across heads, activation sparsity metrics)
# ---------------------------------------------------------------------------

def estimate_c_whitebox(step: StepInput) -> float:
    """Estimate Distinction / novelty (C) using white-box signals.

    Enriches gray-box / black-box C with:
    * per-layer attention entropy (predictive entropy proxy)
    * head diversity (branch diversity across heads)
    * activation sparsity metrics
    * tool-call path diversity
    * sentence-level structural novelty
    * retrieval-echo novelty

    When attention-based signals are available they receive the highest
    weights; gray-box logprobs are used when available as secondary
    signals; black-box text analysis fills remaining gaps.
    """
    wb: Optional[WhiteBoxSignals] = step.white_box
    gb: Optional[GrayBoxSignals] = step.gray_box

    # Primary entropy signal: prefer attention entropy → logprob entropy →
    # token_entropy → black-box proxy
    has_wb_entropy = False
    has_logprob = False
    if wb and wb.attention_entropy:
        entropy_signal = _attention_entropy_mean(wb.attention_entropy)
        has_wb_entropy = True
    elif gb and gb.logprobs:
        entropy_signal = _logprob_entropy(gb.logprobs)
        has_logprob = True
    elif gb and gb.token_entropy:
        entropy_signal = _token_uncertainty(gb.token_entropy)
        has_logprob = True
    else:
        entropy_signal = _token_entropy(step.output_text)

    # Head diversity (white-box only)
    h_diversity = _head_diversity(wb.head_confidence if wb else None)

    # Activation sparsity (white-box only)
    a_sparsity = _activation_sparsity_mean(
        wb.activation_sparsity if wb else None,
    )

    tool_diversity = _tool_path_diversity(step.tool_calls)

    components = [
        entropy_signal,
        h_diversity,
        a_sparsity,
        _semantic_novelty(step.output_text, step.retrieved_context),
        _claim_novelty(step.claims, step.citations),
        _anti_repetition(step.output_text),
        tool_diversity,
        _sentence_structure_novelty(step.output_text),
        _retrieval_echo_novelty(step.output_text, step.retrieved_context),
    ]

    # Weight profiles based on signal availability
    if has_wb_entropy:
        # Attention entropy is the premium signal
        weights = [0.20, 0.12, 0.10, 0.08, 0.08, 0.08, 0.06, 0.14, 0.14]
    elif has_logprob:
        # Logprob entropy is secondary; head diversity still from white-box
        weights = [0.16, 0.10, 0.08, 0.08, 0.08, 0.10, 0.08, 0.16, 0.16]
    else:
        # No entropy signal — lean on text analysis
        weights = [0.10, 0.08, 0.06, 0.10, 0.10, 0.12, 0.08, 0.18, 0.18]

    return normalize(components, weights=weights)


# ---------------------------------------------------------------------------
# White-box I estimator (Design-doc §6.3: attention concentration/entropy,
# head connectivity structure, residual stream coherence)
# ---------------------------------------------------------------------------

def estimate_i_whitebox(step: StepInput) -> float:
    """Estimate Integration / coherence (I) using white-box signals.

    Enriches gray-box / black-box I with:
    * attention concentration (inverse of entropy)
    * residual stream coherence
    * head connectivity structure
    * retriever relevance quality (from gray-box if available)
    * contradiction penalty

    When white-box attention signals are available they receive higher
    weights than the text-based sub-metrics.
    """
    wb: Optional[WhiteBoxSignals] = step.white_box
    gb: Optional[GrayBoxSignals] = step.gray_box

    # White-box I signals
    attn_conc = _attention_concentration(
        wb.attention_entropy if wb else None,
    )
    res_coh = _residual_stream_coherence(
        wb.residual_coherence if wb else None,
    )
    head_conn = _head_connectivity(wb.head_confidence if wb else None)

    # Gray-box relevance signal
    relevance = _relevance_quality(
        gb.relevance_scores if gb else None,
        step.retrieved_context,
    )

    # Contradiction penalty
    penalty = _contradiction_penalty(step.claims)

    has_wb_signals = (
        wb is not None
        and (wb.attention_entropy is not None or wb.residual_coherence is not None)
    )

    components = [
        attn_conc,
        res_coh,
        head_conn,
        _citation_coverage(step.claims, step.citations),
        _support_graph_connectivity(step.claims, step.citations),
        _cross_turn_consistency(step.output_text, step.history),
        relevance,
    ]

    if has_wb_signals:
        weights = [0.18, 0.16, 0.12, 0.14, 0.12, 0.10, 0.18]
    else:
        weights = [0.10, 0.10, 0.10, 0.18, 0.16, 0.16, 0.20]

    raw = normalize(components, weights=weights)
    return float(np.clip(raw - penalty, 0.0, 1.0))


# ---------------------------------------------------------------------------
# White-box κ estimator (Design-doc §6.3: attention variance and saturation,
# context pressure by layer, instability markers)
# ---------------------------------------------------------------------------

def estimate_kappa_whitebox(step: StepInput) -> float:
    """Estimate usable capacity (κ) using white-box signals.

    Extends gray-box κ with:
    * attention variance / saturation across layers
    * KV cache norm stress (exploding norms)
    * gradient norm instability
    * all gray-box signals when available (logprob variance, tool
      confidence, decoding instability, retrieval overload)
    """
    wb: Optional[WhiteBoxSignals] = step.white_box
    gb: Optional[GrayBoxSignals] = step.gray_box

    # --- black-box capacity terms ---
    context_load = (
        step.context_tokens_used / step.context_window
        if step.context_window > 0
        else 0.0
    )
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

    # --- gray-box stress terms ---
    lp_instability = _logprob_variance(gb.logprobs) if gb and gb.logprobs else 0.0
    tc = _tool_confidence_aggregate(gb.tool_confidence if gb else None)
    tool_uncertainty = 1.0 - tc
    decoding_stress = (
        gb.decoding_instability if gb and gb.decoding_instability else 0.0
    )
    ret_overload = _retrieval_overload(
        gb.relevance_scores if gb else None,
        step.retrieved_context,
    )

    # --- white-box stress terms ---
    attn_var_stress = _attention_variance_stress(
        wb.attention_variance if wb else None,
    )
    kv_stress = _kv_norm_stress(wb.kv_norm if wb else None)
    grad_stress = _gradient_norm_stress(wb.gradient_norm if wb else None)

    # Extended σ² with white-box terms (10 components)
    sigma_sq = (
        0.12 * context_load ** 2
        + 0.08 * latency_cv ** 2
        + 0.06 * tool_failure_rate ** 2
        + 0.10 * lp_instability ** 2
        + 0.06 * tool_uncertainty ** 2
        + 0.08 * decoding_stress ** 2
        + 0.10 * ret_overload ** 2
        + 0.16 * attn_var_stress ** 2
        + 0.12 * kv_stress ** 2
        + 0.12 * grad_stress ** 2
    )
    beta = 5.0
    return 1.0 / (1.0 + beta * sigma_sq)
