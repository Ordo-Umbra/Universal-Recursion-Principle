"""
real_transformer_layerwise.py

Real Transformer Layerwise S-Functional Validation
===================================================

Loads a pre-trained GPT-2 model via HuggingFace Transformers, runs prompts
through it, and extracts **actual** per-layer attention weights and
hidden-state logits to compute the layerwise S-functional decomposition:

    C^(l) = mean_{i} H(softmax(z_i^(l)))       — Distinction
    I^(l) = mean_{i,h} [log(n) − H(α_{i,h}^(l))] — Integration
    κ^(l) = 1 / (1 + β · σ²^(l))               — Capacity
    S^(l) = C^(l) + κ^(l) · I^(l)               — Total S

Validates the core hypothesis from ``Transformer-Dynamics.md §6``:

    S^(l+1) ≳ S^(l)

i.e., S approximately increases or holds across layers in a trained model.

The metric functions (compute_layer_c, compute_layer_i, etc.) are **pure
NumPy** and always importable.  The model extraction helpers require the
optional dependencies ``torch`` and ``transformers``.

Optional dependencies (for model extraction only)::

    pip install torch transformers

Key public functions
--------------------
compute_layer_c(logits)
    Distinction C from vocabulary logits — (seq_len, vocab_size).

compute_layer_i(attention)
    Integration I from multi-head attention — (n_heads, seq_len, seq_len).

compute_layer_kappa(attention, beta)
    Capacity κ from multi-head attention variance.

compute_layer_s(logits, attention, beta)
    Full S = C + κ · I for one layer.

per_head_metrics(attention)
    Per-head integration, variance, and concentration breakdown.

analyse_prompt(prompt, model_name, beta)
    Full layerwise analysis on a real HuggingFace causal-LM (requires torch).
"""

from __future__ import annotations

import numpy as np
from typing import Any, Dict, List, Tuple


# ---------------------------------------------------------------------------
# Pure-NumPy metric functions (always available)
# ---------------------------------------------------------------------------

def entropy(p: np.ndarray) -> float:
    """Shannon entropy  H(p) = −Σ p_k log p_k  (nats).

    Filters out near-zero entries for numerical stability.
    """
    p = np.asarray(p, dtype=np.float64).ravel()
    p = p[p > 1e-12]
    return -float(np.sum(p * np.log(p)))


def softmax(x: np.ndarray) -> np.ndarray:
    """Numerically stable softmax along the last axis."""
    x = np.asarray(x, dtype=np.float64)
    shifted = x - x.max(axis=-1, keepdims=True)
    e = np.exp(shifted)
    return e / e.sum(axis=-1, keepdims=True)


def compute_layer_c(logits: np.ndarray) -> float:
    """Per-layer Distinction  C^(l) = (1/n) Σ_i H(softmax(z_i)).

    Parameters
    ----------
    logits : ndarray, shape (seq_len, vocab_size)
        Raw logits (pre-softmax) for each token position at layer *l*.
        These are typically obtained by projecting the hidden state through
        the LM head: ``lm_head(ln_f(h_i^(l)))``.

    Returns
    -------
    float
        Average predictive entropy across all token positions.
    """
    probs = softmax(logits)  # (seq, vocab)
    return float(np.mean([entropy(p) for p in probs]))


def compute_layer_i(attention: np.ndarray) -> float:
    """Per-layer Integration  I^(l) = mean_{i,h}[log n − H(α_{i,h})].

    Parameters
    ----------
    attention : ndarray, shape (n_heads, seq_len, seq_len)
        Post-softmax attention weights for each head and query position.

    Returns
    -------
    float
        Average integration across all heads and positions.
    """
    n_heads, seq_len, _ = attention.shape
    log_n = np.log(seq_len) if seq_len > 1 else 0.0
    vals: List[float] = []
    for h in range(n_heads):
        for i in range(seq_len):
            vals.append(log_n - entropy(attention[h, i]))
    return float(np.mean(vals))


def compute_layer_kappa(attention: np.ndarray, beta: float = 1.0) -> float:
    """Per-layer Capacity  κ^(l) = 1 / (1 + β · σ²).

    σ² = mean_{i,h} Var_j(α_{i,h,j}).

    Parameters
    ----------
    attention : ndarray, shape (n_heads, seq_len, seq_len)
    beta : float
        Capacity sensitivity (default 1.0).

    Returns
    -------
    float
    """
    n_heads, seq_len, _ = attention.shape
    variances: List[float] = []
    for h in range(n_heads):
        for i in range(seq_len):
            variances.append(float(np.var(attention[h, i])))
    sigma_sq = float(np.mean(variances))
    return 1.0 / (1.0 + beta * sigma_sq)


def compute_layer_s(
    logits: np.ndarray,
    attention: np.ndarray,
    beta: float = 1.0,
) -> Tuple[float, float, float, float]:
    """Full per-layer S-functional:  S = C + κ · I.

    Parameters
    ----------
    logits : ndarray, shape (seq_len, vocab_size)
    attention : ndarray, shape (n_heads, seq_len, seq_len)
    beta : float

    Returns
    -------
    (C, I, kappa, S) : tuple of floats
    """
    c = compute_layer_c(logits)
    i = compute_layer_i(attention)
    kappa = compute_layer_kappa(attention, beta)
    s = c + kappa * i
    return c, i, kappa, s


def per_head_metrics(attention: np.ndarray) -> List[Dict[str, Any]]:
    """Per-head integration, variance, and concentration breakdown.

    Parameters
    ----------
    attention : ndarray, shape (n_heads, seq_len, seq_len)

    Returns
    -------
    list of dicts
        One dict per head with keys:
        ``head``, ``I_mean``, ``variance_mean``, ``max_attn_mean``.
    """
    n_heads, seq_len, _ = attention.shape
    log_n = np.log(seq_len) if seq_len > 1 else 0.0
    heads: List[Dict[str, Any]] = []
    for h in range(n_heads):
        i_vals: List[float] = []
        var_vals: List[float] = []
        max_vals: List[float] = []
        for i in range(seq_len):
            row = attention[h, i]
            i_vals.append(log_n - entropy(row))
            var_vals.append(float(np.var(row)))
            max_vals.append(float(np.max(row)))
        heads.append({
            "head": h,
            "I_mean": float(np.mean(i_vals)),
            "variance_mean": float(np.mean(var_vals)),
            "max_attn_mean": float(np.mean(max_vals)),
        })
    return heads


# ---------------------------------------------------------------------------
# Model extraction helpers (require torch + transformers)
# ---------------------------------------------------------------------------

def extract_layerwise_data(
    prompt: str,
    model_name: str = "gpt2",
) -> Dict[str, Any]:
    """Run *prompt* through a HuggingFace causal-LM and return per-layer data.

    Each layer entry contains the vocabulary logits (obtained by projecting
    the layer's hidden state through ``ln_f`` → ``lm_head``) and the
    post-softmax attention weights for every head.

    Parameters
    ----------
    prompt : str
        Input text to tokenize and run through the model.
    model_name : str
        Any HuggingFace causal-LM identifier (default ``"gpt2"``).

    Returns
    -------
    dict
        Keys: ``prompt``, ``model_name``, ``n_layers``, ``seq_len``,
        ``vocab_size``, ``n_heads``, ``layers`` (list of per-layer dicts
        with ``layer``, ``logits``, ``attention``).
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        output_attentions=True,
        output_hidden_states=True,
    )
    model.eval()

    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    # hidden_states: (n_layers+1,) including the embedding layer at index 0
    # attentions:    (n_layers,)
    hidden_states = outputs.hidden_states
    attentions = outputs.attentions

    n_layers = len(attentions)
    seq_len = inputs["input_ids"].shape[1]
    vocab_size = model.config.vocab_size
    n_heads = getattr(
        model.config, "n_head", model.config.num_attention_heads,
    )

    # In GPT-2 the logit projection is: lm_head(ln_f(hidden_state))
    ln_f = model.transformer.ln_f
    lm_head = model.lm_head

    layers_data: List[Dict[str, Any]] = []
    for layer_idx in range(n_layers):
        h = hidden_states[layer_idx + 1]  # (1, seq, hidden)
        with torch.no_grad():
            layer_logits = lm_head(ln_f(h))  # (1, seq, vocab)
        attn = attentions[layer_idx]  # (1, heads, seq, seq)
        layers_data.append({
            "layer": layer_idx,
            "logits": layer_logits[0].cpu().numpy(),   # (seq, vocab)
            "attention": attn[0].cpu().numpy(),         # (heads, seq, seq)
        })

    return {
        "prompt": prompt,
        "model_name": model_name,
        "n_layers": n_layers,
        "seq_len": seq_len,
        "vocab_size": vocab_size,
        "n_heads": n_heads,
        "layers": layers_data,
    }


def analyse_prompt(
    prompt: str,
    model_name: str = "gpt2",
    beta: float = 1.0,
) -> Dict[str, Any]:
    """Full layerwise S-functional analysis of *prompt* on a real model.

    Returns
    -------
    dict
        Arrays ``C``, ``I``, ``kappa``, ``S``, ``delta_S`` (each length
        *n_layers*), summary statistics ``n_increasing``,
        ``n_transitions``, ``s_increase_ratio``, and ``head_details``.
    """
    data = extract_layerwise_data(prompt, model_name)

    C_lst: List[float] = []
    I_lst: List[float] = []
    K_lst: List[float] = []
    S_lst: List[float] = []
    head_details: List[List[Dict[str, Any]]] = []

    for ld in data["layers"]:
        c, i, kappa, s = compute_layer_s(
            ld["logits"], ld["attention"], beta,
        )
        C_lst.append(c)
        I_lst.append(i)
        K_lst.append(kappa)
        S_lst.append(s)
        head_details.append(per_head_metrics(ld["attention"]))

    C = np.array(C_lst)
    I = np.array(I_lst)
    K = np.array(K_lst)
    S = np.array(S_lst)
    delta_S = np.diff(S, prepend=S[0])
    delta_S[0] = 0.0

    n_inc = int(np.sum(delta_S[1:] >= -1e-9))
    n_tr = len(delta_S) - 1

    return {
        "prompt": prompt,
        "model_name": model_name,
        "n_layers": data["n_layers"],
        "seq_len": data["seq_len"],
        "n_heads": data["n_heads"],
        "C": C,
        "I": I,
        "kappa": K,
        "S": S,
        "delta_S": delta_S,
        "n_increasing": n_inc,
        "n_transitions": n_tr,
        "s_increase_ratio": n_inc / max(n_tr, 1),
        "head_details": head_details,
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_results(
    results_list: List[Dict[str, Any]],
    save_path: str = "real_transformer_layerwise.png",
) -> None:
    """Plot layerwise C, I, κ, S for one or more prompts."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n_prompts = len(results_list)
    fig, axes = plt.subplots(
        n_prompts, 3, figsize=(14, 4 * n_prompts), squeeze=False,
    )

    for row, res in enumerate(results_list):
        layers = np.arange(res["n_layers"])

        # Panel 1: C and I
        ax = axes[row, 0]
        ax.plot(layers, res["C"], "b-o", label="C (distinction)", ms=5)
        ax.plot(layers, res["I"], "r-s", label="I (integration)", ms=5)
        ax.set_xlabel("Layer")
        ax.set_ylabel("Score")
        prompt_short = res["prompt"][:35]
        ax.set_title(f'C & I — "{prompt_short}…"')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        # Panel 2: κ
        ax = axes[row, 1]
        ax.plot(layers, res["kappa"], "g-^", label="κ (capacity)", ms=5)
        ax.set_xlabel("Layer")
        ax.set_ylabel("κ")
        ax.set_title("κ (capacity)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.05)

        # Panel 3: S
        ax = axes[row, 2]
        ax.plot(layers, res["S"], "k-o", label="S", linewidth=2, ms=5)
        ax.axhline(
            res["S"][0], color="gray", linestyle="--", alpha=0.5, label="S(0)",
        )
        ax.set_xlabel("Layer")
        ax.set_ylabel("S")
        ratio = res["s_increase_ratio"]
        ax.set_title(f"S — {ratio:.0%} transitions non-decreasing")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(save_path, dpi=120)
    plt.close(fig)
    print(f"\nSaved {save_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_TEST_PROMPTS = [
    "The Universal Recursion Principle proposes that all persistent systems "
    "maximize a single scalar functional",
    "Once upon a time in a kingdom far away, there lived a young girl who "
    "could speak to animals",
    "def fibonacci(n):\n    if n <= 1:\n        return n",
]


def main() -> None:
    """Run full real-transformer layerwise S-functional validation."""
    try:
        import torch            # noqa: F401
        from transformers import AutoTokenizer  # noqa: F401
    except ImportError:
        print("This simulation requires PyTorch and HuggingFace Transformers.")
        print("Install with:  pip install torch transformers")
        return

    print("Real Transformer Layerwise S-Functional Validation")
    print("=" * 60)
    print("Model: GPT-2  (12 layers, 12 heads, 768 hidden)")
    print("Hypothesis: S^(l+1) ≳ S^(l)  (Transformer-Dynamics.md §6)")
    print()

    results: List[Dict[str, Any]] = []
    for prompt in _TEST_PROMPTS:
        print(f'Prompt: "{prompt[:60]}…"')
        res = analyse_prompt(prompt)
        results.append(res)

        header = f"{'Layer':>5} {'C':>8} {'I':>8} {'κ':>8} {'S':>8} {'ΔS':>8}"
        print(header)
        for layer_idx in range(res["n_layers"]):
            sign = "+" if res["delta_S"][layer_idx] >= 0 else ""
            print(
                f"{layer_idx:5d} "
                f"{res['C'][layer_idx]:8.4f} "
                f"{res['I'][layer_idx]:8.4f} "
                f"{res['kappa'][layer_idx]:8.4f} "
                f"{res['S'][layer_idx]:8.4f} "
                f"{sign}{res['delta_S'][layer_idx]:.4f}"
            )

        print(
            f"\nS increased or held in "
            f"{res['n_increasing']}/{res['n_transitions']}"
            f" layer transitions  ({res['s_increase_ratio']:.0%})."
        )
        print()

    # Summary across prompts
    ratios = [r["s_increase_ratio"] for r in results]
    print("=" * 60)
    print(
        f"Mean S-increase ratio across {len(results)} prompts: "
        f"{np.mean(ratios):.0%}"
    )
    print(f"Min: {min(ratios):.0%}  Max: {max(ratios):.0%}")

    plot_results(results)


if __name__ == "__main__":
    main()
