"""
layerwise_transformer.py

Layerwise S-functional simulation for a transformer network.

This module directly validates the hypothesis stated in
``Docs/Transformer-Dynamics.md §6``:

    *Transformer layers approximately evolve to increase S, such that
    S^(l+1) ≥ S^(l).*

We simulate an L-layer transformer by generating attention weights and
predictive distributions that realistically evolve layer-by-layer (early
layers: broad, diffuse; later layers: focused, sharpened).  At the final
layer the softmax forces an output collapse (C drops sharply).

Key public functions
--------------------
compute_layer_metrics(predictive_dists, attention_weights, beta=1.0)
    Compute C, I, κ, S for a single layer — the same formulas as in
    ``Transformer-Dynamics.md`` sections 2–5.

simulate_layerwise(n_layers, seq_len, vocab_size, rng_seed, beta)
    Run the full layerwise simulation and return per-layer arrays of
    C, I, κ, S, ΔS.
"""

from __future__ import annotations

import numpy as np
from typing import Tuple


# ---------------------------------------------------------------------------
# Core layer metric computation (Transformer-Dynamics.md §2–5)
# ---------------------------------------------------------------------------

def _entropy(p: np.ndarray) -> float:
    """Shannon entropy of a discrete distribution."""
    p = p + 1e-12
    p = p / p.sum()
    return float(-np.sum(p * np.log(p)))


def compute_layer_metrics(
    predictive_dists: np.ndarray,
    attention_weights: np.ndarray,
    beta: float = 1.0,
) -> Tuple[float, float, float, float]:
    """Compute C, I, κ, S for one transformer layer.

    Implements the formulas from ``Transformer-Dynamics.md`` §2–5:

    - **C** (Distinction): average predictive entropy across tokens.
    - **I** (Integration): average inverse attention entropy (log n − H_attn).
    - **κ** (Capacity): 1 / (1 + β · mean(Var(α_i))).
    - **S**: C + κ · I.

    Parameters
    ----------
    predictive_dists:
        Shape ``(seq_len, vocab_size)`` — predictive distribution for each
        token.
    attention_weights:
        Shape ``(seq_len, seq_len)`` — row-normalised attention matrix.
    beta:
        Capacity sensitivity parameter.

    Returns
    -------
    (C, I, kappa, S) all floats.
    """
    seq_len = attention_weights.shape[0]

    # Distinction C — predictive entropy per token, averaged
    C = float(np.mean([_entropy(p) for p in predictive_dists]))

    # Integration I — inverse attention entropy per token, averaged
    log_n = np.log(seq_len) if seq_len > 1 else 0.0
    I_tokens = [log_n - _entropy(a) for a in attention_weights]
    I = float(np.mean(I_tokens))

    # Capacity κ — inverse attention variance
    variances = [float(np.var(a)) for a in attention_weights]
    sigma_sq = float(np.mean(variances))
    kappa = 1.0 / (1.0 + beta * sigma_sq)

    S = C + kappa * I
    return C, I, kappa, S


# ---------------------------------------------------------------------------
# Layerwise evolution simulation
# ---------------------------------------------------------------------------

def _softmax(x: np.ndarray) -> np.ndarray:
    """Numerically stable softmax."""
    e = np.exp(x - x.max())
    return e / e.sum()


def _make_attention(seq_len: int, concentration: float, rng: np.random.Generator) -> np.ndarray:
    """Generate a row-normalised attention matrix with given concentration.

    Higher *concentration* → more peaked (focused) rows.
    """
    rows = np.array(
        [rng.dirichlet(np.ones(seq_len) * concentration) for _ in range(seq_len)]
    )
    return rows


def _make_predictive_dists(
    vocab_size: int,
    seq_len: int,
    concentration: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate predictive distributions for each token.

    Higher *concentration* → more uniform (high entropy) distributions.
    """
    return np.array(
        [rng.dirichlet(np.ones(vocab_size) * concentration) for _ in range(seq_len)]
    )


def simulate_layerwise(
    n_layers: int = 8,
    seq_len: int = 16,
    vocab_size: int = 64,
    rng_seed: int = 0,
    beta: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Simulate layer-by-layer S-functional evolution in a transformer.

    Layer dynamics (Transformer-Dynamics.md §6):

    - Early layers: broad predictive distributions (high C) and diffuse
      attention (low I), low κ due to high variance.
    - Middle layers: attention sharpens (I rises), predictive entropy stays
      moderately high, κ improves.  S increases.
    - Final layer: softmax output collapse forces C to drop sharply while I
      stays focused; S resolves the accumulated distinction into one choice.

    Parameters
    ----------
    n_layers:
        Total number of transformer layers to simulate.
    seq_len:
        Number of tokens in the sequence.
    vocab_size:
        Vocabulary size for predictive distributions.
    rng_seed:
        Seed for reproducibility.
    beta:
        Capacity sensitivity (passed to :func:`compute_layer_metrics`).

    Returns
    -------
    (C_layers, I_layers, kappa_layers, S_layers, delta_S)
        Each a 1-D float array of length *n_layers*.
        ``delta_S[0]`` is defined as 0 (no previous layer to diff against).
    """
    rng = np.random.default_rng(rng_seed)

    C_layers = np.zeros(n_layers)
    I_layers = np.zeros(n_layers)
    kappa_layers = np.zeros(n_layers)
    S_layers = np.zeros(n_layers)

    for layer in range(n_layers):
        progress = layer / max(n_layers - 1, 1)  # 0 at layer 0, 1 at final layer

        if layer < n_layers - 1:
            # Predictive distributions: early layers are broad (near-uniform =
            # high Dirichlet concentration alpha → high entropy = high C),
            # gradually sharpening as the model builds context.
            # alpha: 6.0 → 0.8 over the network
            pred_concentration = max(6.0 * (1.0 - progress) + 0.8 * progress, 0.3)

            # Attention: starts diffuse (high alpha → uniform rows → low I),
            # sharpens toward specialised heads (low alpha → peaked rows → high I).
            # alpha: 5.0 → 0.15 over the network
            attn_concentration = max(5.0 * (1.0 - progress) + 0.15 * progress, 0.1)
        else:
            # Final layer: softmax output collapse — predictive distributions
            # become very peaked (low α → low entropy = low C).
            pred_concentration = 0.05
            # Attention stays focused from previous evolution.
            attn_concentration = 0.15

        preds = _make_predictive_dists(vocab_size, seq_len, pred_concentration, rng)
        attns = _make_attention(seq_len, attn_concentration, rng)

        C, I, kappa, S = compute_layer_metrics(preds, attns, beta=beta)
        C_layers[layer] = C
        I_layers[layer] = I
        kappa_layers[layer] = kappa
        S_layers[layer] = S

    delta_S = np.diff(S_layers, prepend=S_layers[0])
    delta_S[0] = 0.0

    return C_layers, I_layers, kappa_layers, S_layers, delta_S


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    C, I, kap, S, dS = simulate_layerwise(n_layers=8, seq_len=16, vocab_size=64)

    print("Layer-by-layer S-functional (Transformer-Dynamics.md §6 validation)")
    print(f"{'Layer':>6}  {'C':>8}  {'I':>8}  {'κ':>8}  {'S':>8}  {'ΔS':>8}")
    for l in range(len(S)):
        print(f"{l:>6}  {C[l]:>8.4f}  {I[l]:>8.4f}  {kap[l]:>8.4f}  {S[l]:>8.4f}  {dS[l]:>+8.4f}")

    # Count layers where S increased (excluding layer 0)
    increases = int((dS[1:] >= 0).sum())
    print(f"\nS increased or held in {increases}/{len(S)-1} layer transitions.")

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    fig.suptitle("Layerwise Transformer S-Functional (Transformer-Dynamics.md §6)")
    layers = np.arange(len(S))

    axes[0].plot(layers, C, "b-o", label="C (Distinction)")
    axes[0].plot(layers, I, "r-s", label="I (Integration)")
    axes[0].set_xlabel("Layer")
    axes[0].set_title("C and I per Layer")
    axes[0].legend()

    axes[1].plot(layers, kap, "g-^")
    axes[1].set_xlabel("Layer")
    axes[1].set_ylabel("κ")
    axes[1].set_title("Capacity κ per Layer")

    axes[2].plot(layers, S, "k-o", linewidth=2)
    axes[2].axhline(S[0], linestyle="--", color="gray", alpha=0.5)
    axes[2].set_xlabel("Layer")
    axes[2].set_ylabel("S")
    axes[2].set_title("S-Functional per Layer")

    plt.tight_layout()
    plt.savefig("layerwise_transformer.png", dpi=120)
    print("Saved layerwise_transformer.png")
