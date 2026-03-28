"""
estimators.py

C, I, and κ estimators for S Compass (Design-doc §4.3–4.5, §11, §19).

Each estimator accepts a :class:`StepInput` and returns a float in [0, 1].
Sub-metric helpers are exposed so that pipelines can swap estimators without
changing the scoring signature.
"""

from __future__ import annotations

import math
from typing import Dict, List, Sequence

import numpy as np

from .schemas import Claim, RetrievedChunk, StepInput


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _token_entropy(text: str) -> float:
    """Estimate Shannon entropy over whitespace tokens.

    This is a lightweight proxy for output entropy when logprobs are not
    available (black-box mode).  Returns a value in [0, 1] by normalising
    against the maximum possible entropy for the observed vocabulary size.
    """
    tokens = text.split()
    if not tokens:
        return 0.0
    counts: Dict[str, int] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    n = len(tokens)
    probs = [c / n for c in counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1.0
    return min(entropy / max_entropy, 1.0) if max_entropy > 0 else 0.0


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def _cosine_token_similarity(text_a: str, text_b: str) -> float:
    """Token-level cosine similarity (cheap embedding proxy)."""
    toks_a = text_a.lower().split()
    toks_b = text_b.lower().split()
    vocab = sorted(set(toks_a) | set(toks_b))
    if not vocab:
        return 0.0
    vec_a = np.array([toks_a.count(w) for w in vocab], dtype=float)
    vec_b = np.array([toks_b.count(w) for w in vocab], dtype=float)
    dot = float(np.dot(vec_a, vec_b))
    norm_a = float(np.linalg.norm(vec_a))
    norm_b = float(np.linalg.norm(vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# Normalize helper (Design-doc §19.3)
# ---------------------------------------------------------------------------

def normalize(values: Sequence[float], weights: Sequence[float] | None = None) -> float:
    """Weighted average → clip to [0, 1].

    Follows the z-score → weighted-average → clipping pipeline described
    in Design-doc §19.3.  When called with already-normalised sub-metrics
    the z-score step is a no-op and the function simply computes the
    weighted average.
    """
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return 0.0
    if weights is not None:
        w = np.asarray(weights, dtype=float)
        w = w / w.sum() if w.sum() > 0 else np.ones_like(w) / len(w)
    else:
        w = np.ones(len(arr)) / len(arr)
    result = float(np.dot(arr, w))
    return float(np.clip(result, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Capacity field helper (Design-doc §19.3)
# ---------------------------------------------------------------------------

def capacity_field(
    context_load: float = 0.0,
    latency_std: float = 0.0,
    tool_failure_rate: float = 0.0,
    beta: float = 5.0,
) -> float:
    r"""Compute κ from operational stress signals.

    Uses the sigmoid-form from Transformer-Dynamics.md §4:

    .. math::
        \kappa = \frac{1}{1 + \beta \sigma^2}

    where σ² is a weighted combination of context load, latency
    instability, and tool failure rate.
    """
    sigma_sq = (
        0.5 * context_load ** 2
        + 0.3 * latency_std ** 2
        + 0.2 * tool_failure_rate ** 2
    )
    return 1.0 / (1.0 + beta * sigma_sq)


# ---------------------------------------------------------------------------
# C Estimator (Design-doc §4.3, §19.2)
# ---------------------------------------------------------------------------

def _semantic_novelty(output: str, retrieval: List[RetrievedChunk]) -> float:
    """Embedding distance proxy: 1 − average cosine similarity to retrieved chunks."""
    if not retrieval:
        return 0.5  # neutral when no retrieval context
    sims = [_cosine_token_similarity(output, c.text) for c in retrieval]
    avg_sim = sum(sims) / len(sims)
    return 1.0 - avg_sim


def _claim_novelty(claims: List[Claim], citations: list) -> float:
    """Fraction of claims not directly covered by citations."""
    if not claims:
        return 0.0
    if not citations:
        return 1.0
    cited_texts = {str(c.get("text", c.get("doc_id", ""))) for c in citations}
    novel = sum(1 for cl in claims if cl.text not in cited_texts)
    return novel / len(claims)


def _anti_repetition(text: str) -> float:
    """1 − fraction of repeated token bigrams."""
    tokens = text.split()
    if len(tokens) < 2:
        return 1.0
    bigrams = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]
    unique = len(set(bigrams))
    return unique / len(bigrams)


def estimate_c(step: StepInput) -> float:
    """Estimate Distinction / novelty (C) for an inference step."""
    return normalize(
        [
            _token_entropy(step.output_text),
            _semantic_novelty(step.output_text, step.retrieved_context),
            _claim_novelty(step.claims, step.citations),
            _anti_repetition(step.output_text),
        ]
    )


# ---------------------------------------------------------------------------
# I Estimator (Design-doc §4.4, §19.2)
# ---------------------------------------------------------------------------

def _citation_coverage(claims: List[Claim], citations: list) -> float:
    """Fraction of claims that have at least one matching citation."""
    if not claims:
        return 1.0  # vacuously covered
    if not citations:
        return 0.0
    cited_ids = {str(c.get("doc_id", "")) for c in citations}
    covered = sum(
        1
        for cl in claims
        if cl.provenance and cl.provenance.get("source_type") in cited_ids
    )
    # Simpler heuristic: any claim whose text appears in citation text
    cited_texts = " ".join(str(c.get("text", "")) for c in citations)
    text_covered = sum(1 for cl in claims if cl.text.lower() in cited_texts.lower())
    return max(covered, text_covered) / len(claims)


def _cross_turn_consistency(output: str, history: List[str]) -> float:
    """Average cosine similarity with previous turns."""
    if not history:
        return 1.0  # first turn is trivially consistent
    sims = [_cosine_token_similarity(output, prev) for prev in history]
    return sum(sims) / len(sims)


def _support_graph_connectivity(claims: List[Claim], citations: list) -> float:
    """Proxy for support graph density: ratio of citations to claims."""
    if not claims:
        return 1.0
    if not citations:
        return 0.0
    return min(len(citations) / len(claims), 1.0)


def estimate_i(step: StepInput) -> float:
    """Estimate Integration / coherence (I) for an inference step."""
    return normalize(
        [
            _citation_coverage(step.claims, step.citations),
            _support_graph_connectivity(step.claims, step.citations),
            _cross_turn_consistency(step.output_text, step.history),
        ]
    )


# ---------------------------------------------------------------------------
# κ Estimator (Design-doc §4.5, §19.2)
# ---------------------------------------------------------------------------

def estimate_kappa(step: StepInput) -> float:
    """Estimate usable capacity (κ) for an inference step."""
    context_load = (
        step.context_tokens_used / step.context_window
        if step.context_window > 0
        else 0.0
    )
    # Latency dispersion from history
    if step.latency_history and len(step.latency_history) > 1:
        latency_std = float(np.std(step.latency_history))
        # Normalise against the mean so the scale is comparable
        mean_lat = float(np.mean(step.latency_history))
        latency_cv = latency_std / mean_lat if mean_lat > 0 else 0.0
    else:
        latency_cv = 0.0

    tool_failure_rate = (
        step.tool_failure_count / step.tool_total_count
        if step.tool_total_count > 0
        else 0.0
    )

    return capacity_field(
        context_load=context_load,
        latency_std=latency_cv,
        tool_failure_rate=tool_failure_rate,
    )
