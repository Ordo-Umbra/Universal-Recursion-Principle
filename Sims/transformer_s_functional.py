"""
transformer_s_functional.py

A minimal simulation demonstrating the S-functional (S = C + κ * I) 
applied to transformer dynamics, as formalized in URP.

We simulate a single attention layer and compute:
- C (Distinction): Predictive entropy of the hidden states.
- I (Integration): Inverse entropy of the attention weights.
- κ (Capacity): Inverse variance of the attention weights.

We test four theoretical regimes:
1. Rigid: Low C, High I
2. Creative: High C, Moderate I
3. Hallucination: High C, Low I, Low κ
4. Collapse: Low C, Low I
"""

import numpy as np
import scipy.stats

def compute_entropy(p_dist):
    """Compute Shannon entropy of a probability distribution."""
    # Add small epsilon to avoid log(0)
    p = p_dist + 1e-9
    p = p / np.sum(p)
    return -np.sum(p * np.log(p))

def compute_layer_S_functional(predictive_dists, attention_weights, beta=1.0):
    """
    Given simulated predictive distributions and attention weights for 'n' tokens,
    computes C, I, kappa, and S.
    """
    n = len(predictive_dists)
    
    # 1. Distinction (C) -> Average predictive entropy
    C_tokens = [compute_entropy(p) for p in predictive_dists]
    C = np.mean(C_tokens)
    
    # 2. Integration (I) -> Inverse attention entropy
    H_attn = [compute_entropy(a) for a in attention_weights]
    I_tokens = [np.log(len(a)) - h for a, h in zip(attention_weights, H_attn)]
    I = np.mean(I_tokens)
    
    # 3. Capacity (kappa) -> Inverse variance of attention
    variances = [np.var(a) for a in attention_weights]
    sigma_sq = np.mean(variances)
    kappa = 1.0 / (1.0 + beta * sigma_sq)
    
    # 4. Total S
    S = C + (kappa * I)
    
    return S, C, I, kappa

def simulate_regime(regime_name, vocab_size=100, seq_len=10):
    """Generates mock distributions corresponding to different LLM regimes."""
    
    if regime_name == "Rigid":
        # Low C (predictable tokens), High I (focused attention)
        preds = [np.eye(vocab_size)[0] for _ in range(seq_len)]
        attns = [np.eye(seq_len)[0] for _ in range(seq_len)]
        
    elif regime_name == "Creative":
        # High C (many options), Moderate I (structured but distributed attention)
        preds = [np.random.dirichlet(np.ones(vocab_size) * 0.5) for _ in range(seq_len)]
        attns = [np.random.dirichlet(np.ones(seq_len) * 0.1) for _ in range(seq_len)]
        
    elif regime_name == "Hallucination":
        # High C (flat/random predictions), Low I (flat/random attention)
        preds = [np.ones(vocab_size) / vocab_size for _ in range(seq_len)]
        attns = [np.ones(seq_len) / seq_len for _ in range(seq_len)]
        
    elif regime_name == "Collapse":
        # Low C (stuck on one token), Low I (diffuse attention)
        preds = [np.eye(vocab_size)[0] for _ in range(seq_len)]
        attns = [np.ones(seq_len) / seq_len for _ in range(seq_len)]
        
    S, C, I, kappa = compute_layer_S_functional(preds, attns)
    
    print(f"--- {regime_name} Regime ---")
    print(f"S (Total)   : {S:.3f}")
    print(f"C (Distinc) : {C:.3f}")
    print(f"I (Integ)   : {I:.3f}")
    print(f"κ (Capacity): {kappa:.3f}
")

if __name__ == "__main__":
    print("Testing URP Transformer Functional Regimes
")
    simulate_regime("Rigid")
    simulate_regime("Creative")
    simulate_regime("Hallucination")
    simulate_regime("Collapse")
