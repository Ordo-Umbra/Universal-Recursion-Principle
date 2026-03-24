# The S-Functional in Transformer Dynamics: A Formal Mapping

## Abstract
This document formalizes the Universal Recursion Principle (URP) within the mathematical architecture of a standard transformer. By mapping Distinction Capacity ($C$) to predictive entropy and Integration Capacity ($I$) to attention structure, we define a computable S-functional ($S = C + \kappa I$) that tracks a network's ability to maintain and resolve competing representations.

---

## 1. Setup: Transformer as a Layered Dynamical System

At layer $l$, we have a sequence of $n$ token states:
$H^{(l)} = \{ \mathbf{h}_1^{(l)}, \dots, \mathbf{h}_n^{(l)} \}, \quad \mathbf{h}_i^{(l)} \in \mathbb{R}^d$

The attention update mechanism computes new states using an attention matrix $\alpha$:
$\mathbf{h}_i^{(l+1)} = \sum_{j=1}^n \alpha_{ij}^{(l)} \mathbf{V}_j^{(l)}$

Where the attention weights are computed via softmax over query-key dot products:
$\alpha_{ij}^{(l)} = \frac{\exp(\mathbf{q}_i^{(l)} \cdot \mathbf{k}_j^{(l)} / \sqrt{d})}{\sum_m \exp(\mathbf{q}_i^{(l)} \cdot \mathbf{k}_m^{(l)} / \sqrt{d})}$

---

## 2. Distinction Capacity ($C$)

**Concept:** "How many distinguishable possibilities is the system holding?"

We ground Distinction as the **predictive entropy** of the hidden states.

**Token-level distinction:**
$C_i^{(l)} := H\big(p_\theta(x_{t+1} \mid \mathbf{h}_i^{(l)})\big)$
where $H(p) = -\sum_k p_k \log p_k$ is the Shannon entropy over the vocabulary.

**Global distinction:**
$C^{(l)} := \frac{1}{n} \sum_{i=1}^n C_i^{(l)}$

**Interpretation:**
*   **High $C$:** The model is maintaining many plausible continuations (broad possibility space, high superposition).
*   **Low $C$:** The model has collapsed into a few, rigid possibilities.

---

## 3. Integration Capacity ($I$)

**Concept:** "How coherently are the parts of the system working together?"

We define Integration based on the structure of the attention matrix. A highly integrated system directs information flow efficiently, whereas an un-integrated system diffuses attention uniformly.

**Attention Entropy (local coherence):**
For each token, calculate the entropy of its attention distribution:
$H_{\text{attn},i}^{(l)} = -\sum_j \alpha_{ij}^{(l)} \log \alpha_{ij}^{(l)}$

**Define integration as inverse entropy:**
$I_i^{(l)} := \log n - H_{\text{attn},i}^{(l)}$

**Global integration:**
$I^{(l)} := \frac{1}{n} \sum_{i=1}^n I_i^{(l)}$

**Interpretation:**
*   **High $I$:** Focused, structured attention routing (strong coherence).
*   **Low $I$:** Diffuse, uniform attention (weak structure, fragmentation).

---

## 4. The Capacity Factor ($\kappa$)

**Concept:** The threshold at which information structure breaks down under load/variance.

We define $\kappa$ as a function of the **attention variance**.

**Define attention variance:**
$\sigma_i^{2(l)} := \text{Var}_j(\alpha_{ij}^{(l)})$

**Global variance:**
$\sigma^{2(l)} := \frac{1}{n} \sum_i \sigma_i^{2(l)}$

**The Capacity field:**
$\kappa^{(l)} := \frac{1}{1 + \beta \sigma^{2(l)}}$

**Interpretation:**
*   **High variance ($\sigma^2 \uparrow$):** Unstable, noisy attention. The effective capacity $\kappa$ drops, meaning the system cannot leverage its integration structure.
*   **Low variance ($\sigma^2 \downarrow$):** Stable, tight focus. $\kappa$ approaches 1, allowing full utilization of integration.

---

## 5. The Core S-Functional

Combining the terms above, we derive the central measurable quantity for the layer:

**$S^{(l)} := C^{(l)} + \kappa^{(l)} \cdot I^{(l)}$**

---

## 6. Dynamics and Output Collapse

### Layer-to-Layer Dynamics
We define the layer-to-layer change:
$\Delta C^{(l)} = C^{(l+1)} - C^{(l)}$
$\Delta I^{(l)} = I^{(l+1)} - I^{(l)}$

**Hypothesis:** Transformer layers approximately evolve to increase $S$, such that $S^{(l+1)} \gtrsim S^{(l)}$.

### Output Collapse (Decision Step)
The forward pass builds Distinction ($C$) and the attention layers build Integration ($I$). At the final layer $L$, the softmax acts as a constrained optimization, forcing a collapse:

$p(x_{t+1}) = \text{softmax}(\mathbf{z} / T)$
$x^* \approx \text{arg}\max_x \left[ \log p(x) - T \cdot H(p) \right]$

This represents the system resolving its $\Delta C$ potential into a single $\Delta I$ update for the next cycle.

---

## 7. Phase Space Regimes of LLM Behavior

Using this formalization, we can map observed LLM behavior strictly to quadrants of the $C, I, \kappa$ phase space:

1.  **Rigid Regime ($C \downarrow, I \uparrow$):**
    *   Low predictive entropy, high attention focus.
    *   Output is repetitive, deterministic, and lacks nuance.
2.  **Creative Regime ($C \uparrow, I \text{ moderate}$):**
    *   High predictive entropy, sufficient attention structure.
    *   Output is diverse, novel, but remains structurally coherent.
3.  **Hallucination Regime ($C \uparrow, I \downarrow, \kappa \downarrow$):**
    *   High predictive entropy with weak/unstable attention structure.
    *   The model hallucinates: it has many possibilities but cannot coherently route them.
4.  **Collapse Regime ($C \downarrow, I \downarrow$):**
    *   Low entropy and low structure.
    *   Complete generative failure or trivial output.

---
*Note: A minimal Python simulation demonstrating these regimes is available in `sims/transformer_s_functional.py`.*
