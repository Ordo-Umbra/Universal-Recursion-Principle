"""
scoring.py

S Scoring Engine and regime classifier (Design-doc §4.6, §11, §12).

Computes the top-level quantity  S = C + κI  and assigns a behavioural
regime label based on threshold rules.
"""

from __future__ import annotations

from typing import Dict

from .schemas import ScoreSnapshot, StepInput
from .estimators import (
    _sentence_structure_novelty,
    estimate_c,
    estimate_i,
    estimate_kappa,
)
from .estimators_graybox import (
    estimate_c_graybox,
    estimate_i_graybox,
    estimate_kappa_graybox,
    signal_coverage,
)


# ---------------------------------------------------------------------------
# Regime thresholds (Design-doc §12)
# ---------------------------------------------------------------------------

_C_HIGH = 0.55
_C_LOW = 0.35
_I_HIGH = 0.55
_I_LOW = 0.35
_K_LOW = 0.45
_K_CRITICAL = 0.25
_STRUCT_NOV_LOW = 0.40


def classify_regime(
    c: float,
    i: float,
    kappa: float,
    structural_novelty: float = 1.0,
) -> str:
    """Assign a behavioural regime label (Design-doc §12).

    Returns one of:

    * ``"rigid"`` — low C, high I, moderate-or-high κ
    * ``"creative-grounded"`` — high C, moderate-or-high I, moderate-or-high κ
    * ``"hallucination-risk"`` — high C, low I, low or unstable κ
    * ``"collapse"`` — low C, low I, low κ

    Parameters
    ----------
    structural_novelty:
        Optional sentence-level structural novelty score in [0, 1].
        When provided (by :func:`score_step`), enables detection of
        template-rigid outputs that have high lexical diversity but
        repetitive sentence structure.  Defaults to 1.0 (fully novel)
        when called without text analysis (e.g. from the policy
        evaluation endpoint with pre-computed scores).
    """
    if c <= _C_LOW and i <= _I_LOW and kappa < _K_LOW:
        return "collapse"
    if kappa < _K_CRITICAL and i <= _I_LOW:
        return "collapse"
    if c >= _C_HIGH and i < _I_LOW:
        return "hallucination-risk"
    # Rigid: integration dominates distinction — the output is well-grounded
    # (high I) but lacks creative transformation (C noticeably lower than I).
    # The i - c >= 0.10 heuristic captures outputs that echo retrieval
    # context closely, producing high citation coverage but little novelty.
    if (c < _C_HIGH or i - c >= 0.10) and i >= _I_HIGH and kappa >= _K_LOW:
        return "rigid"
    # Template-rigid: structurally repetitive text (e.g. "The X is Y.
    # The X has Z.") with at least moderate integration.  This catches
    # outputs with high lexical diversity but formulaic sentence patterns
    # that the score-only rigid check above misses.
    if structural_novelty < _STRUCT_NOV_LOW and i >= _I_LOW and kappa >= _K_LOW:
        return "rigid"
    if c >= _C_HIGH and i >= _I_LOW:
        return "creative-grounded"
    # Fallback: use S magnitude to pick the closest label
    s = c + kappa * i
    if s < 0.5:
        return "collapse"
    return "creative-grounded"


# ---------------------------------------------------------------------------
# Scoring engine
# ---------------------------------------------------------------------------

def score_step(step: StepInput) -> ScoreSnapshot:
    """Score a single inference step and classify its regime.

    Combines the C, I, and κ estimators into the S-functional
    ``S = C + κ I`` and returns a :class:`ScoreSnapshot`.

    When gray-box signals are present the higher-fidelity gray-box
    estimators are used and ``confidence`` is computed dynamically
    based on which signals are available.
    """
    use_gray = step.mode == "gray-box" and step.gray_box is not None

    if use_gray:
        c = estimate_c_graybox(step)
        i = estimate_i_graybox(step)
        kappa = estimate_kappa_graybox(step)
        # Dynamic confidence: black-box floor + weighted coverage of present signals
        coverage = signal_coverage(step.gray_box)
        confidence = 0.65 + 0.30 * coverage  # range [0.65, 0.95]
    else:
        c = estimate_c(step)
        i = estimate_i(step)
        kappa = estimate_kappa(step)
        confidence = 0.65

    # Compute structural novelty for template-rigid detection
    structural_novelty = _sentence_structure_novelty(step.output_text)

    s = c + kappa * i  # core URP formula
    regime = classify_regime(c, i, kappa, structural_novelty=structural_novelty)
    return ScoreSnapshot(
        c=round(c, 4),
        i=round(i, 4),
        kappa=round(kappa, 4),
        s=round(s, 4),
        regime=regime,
        trace_id=step.trace_id,
        confidence=round(confidence, 4),
        mode=step.mode,
    )


def score_step_dict(step: StepInput) -> Dict[str, object]:
    """Convenience wrapper returning a plain dict (matches API §8.2 response)."""
    snap = score_step(step)
    return {
        "ok": True,
        "scores": {
            "c": snap.c,
            "i": snap.i,
            "kappa": snap.kappa,
            "s": snap.s,
        },
        "regime": snap.regime,
    }
