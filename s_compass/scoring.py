"""
scoring.py

S Scoring Engine and regime classifier (Design-doc §4.6, §11, §12).

Computes the top-level quantity  S = C + κI  and assigns a behavioural
regime label based on threshold rules.
"""

from __future__ import annotations

from typing import Dict

from .schemas import ScoreSnapshot, StepInput
from .estimators import estimate_c, estimate_i, estimate_kappa


# ---------------------------------------------------------------------------
# Regime thresholds (Design-doc §12)
# ---------------------------------------------------------------------------

_C_HIGH = 0.55
_C_LOW = 0.35
_I_HIGH = 0.55
_I_LOW = 0.35
_K_LOW = 0.45
_K_CRITICAL = 0.25


def classify_regime(c: float, i: float, kappa: float) -> str:
    """Assign a behavioural regime label (Design-doc §12).

    Returns one of:

    * ``"rigid"`` — low C, high I, moderate-or-high κ
    * ``"creative-grounded"`` — high C, moderate-or-high I, moderate-or-high κ
    * ``"hallucination-risk"`` — high C, low I, low or unstable κ
    * ``"collapse"`` — low C, low I, low κ
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
    """
    c = estimate_c(step)
    i = estimate_i(step)
    kappa = estimate_kappa(step)
    s = c + kappa * i  # core URP formula
    regime = classify_regime(c, i, kappa)
    return ScoreSnapshot(
        c=round(c, 4),
        i=round(i, 4),
        kappa=round(kappa, 4),
        s=round(s, 4),
        regime=regime,
        trace_id=step.trace_id,
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
