# S-Functional Glossary

A single reference for the symbols of the S-functional and what each one means
in each layer of the framework. The same letters ($C$, $I$, $\kappa$, $S$)
appear in the logic, physics, information-theory, graph, transformer, and
S Compass treatments, but they are *operationalized* differently in each. This
page collects those meanings side by side so a symbol never has to be guessed
from context.

For why the functional appears in both a *level* form ($S = C + \kappa I$) and a
*delta* form ($S = \Delta C + \kappa\,\Delta I$), see
[Level-and-Delta-Forms.md](Level-and-Delta-Forms.md).

---

## 1. Core symbols at a glance

| Symbol | Name | One-line meaning |
|--------|------|------------------|
| $S$ | S-functional | The scalar a recursive system is conjectured to maximize. |
| $C$ | Distinction | How much meaningful, differentiated structure is present. |
| $I$ | Integration | How coherently that structure is woven into a whole. |
| $\kappa$ | Capacity | Usable capacity under load; scales $I$ toward zero under stress. |
| $\Delta C,\ \Delta I,\ \Delta S$ | Increments | Step-over-step *growth* in $C$, $I$, $S$ (the delta form). |
| $\beta$ | Complexity coupling | Universal constant $\approx 0.09$ (see §5). |
| $G$ | Coherence coupling | Universal constant $\approx 0.22$ (see §5). |

The two readings of the functional:

- **Level:** $S = C + \kappa I$ — the state *now*.
- **Delta:** $S = \Delta C + \kappa\,\Delta I$ — the *change* across a step.

---

## 2. Distinction $C$ across domains

> "How many distinguishable possibilities / how much new structure?"

| Domain | $C$ is operationalized as |
|--------|---------------------------|
| Logic / ordinal (URP §2) | Representational capacity $C(F)$: the ordinals a formal system can encode ($=\omega_1^{CK}$). |
| Field theory (URP §3) | Structural differentiation from the nonlinear term $\beta\lvert\nabla\phi\rvert^2$ — sharpening gradients, boundaries, domains. |
| Information theory (URP §4) | New predictive content: $I(Z_{new};O_{future}\mid O_{past})$ minus a redundancy penalty. |
| Graph (URP §5) | Effective complexity $EC(G)$: spectral entropy of degrees, motif/Betti counts, or embedding rank. |
| Transformer (Transformer-Dynamics §2) | Mean **predictive entropy** of hidden states over the vocabulary. |
| S Compass (`estimators.py`) | Weighted mix of token entropy, semantic novelty, claim novelty, anti-repetition, sentence-structure novelty, retrieval-echo novelty. |

---

## 3. Integration $I$ across domains

> "How coherently are the parts working together?"

| Domain | $I$ is operationalized as |
|--------|---------------------------|
| Logic / ordinal (URP §2) | Inferential capacity $I(F)$: the proof-theoretic ordinal — what the system can internally stabilize. |
| Field theory (URP §3) | Coherent integration from $G\,\nabla V\cdot\nabla\phi + \delta\mathcal{I}/\delta\phi$ — cross-region mutual information. |
| Information theory (URP §4) | Free-energy reduction $-\Delta F$ plus a synergy term. |
| Graph (URP §5) | Global efficiency $\mathrm{Eff}(G)$ and algebraic connectivity $\lambda_2(\mathcal{L})$; or reduction in description length. |
| Transformer (Transformer-Dynamics §3) | Inverse attention entropy: $\log n - H_{\text{attn}}$ (focused routing = high $I$). |
| S Compass (`estimators.py`) | Citation coverage, support-graph connectivity, cross-turn consistency (minus a contradiction penalty in gray-box). |

---

## 4. Capacity $\kappa$ across domains

> "Can the system actually use its integration right now, or is it under too much
> load?" In every domain $\kappa$ falls toward 0 under stress and rises toward 1
> when resources are ample.

| Domain | $\kappa$ is operationalized as |
|--------|--------------------------------|
| Logic / ordinal (URP §2) | $\kappa_t = \dfrac{1}{1+\lambda G_t}\,e^{-\rho_t}$, where $G_t$ is the incompleteness gap and $\rho_t$ a load factor. |
| Field theory (URP §3) | Suppressed by high gradient energy and extreme curvature. |
| Information theory (URP §4) | $\kappa_t = e^{-U_t}$, where $U_t$ = bits processed / capacity budget. |
| Graph (URP §5) | $\kappa_t = \dfrac{1}{1+\alpha\,\mathrm{dens}(G_t)+\beta\,\lvert V_t\rvert/C_{budget}}$. |
| Transformer (Transformer-Dynamics §4) | $\kappa = \dfrac{1}{1+\beta\sigma^2}$, where $\sigma^2$ is attention variance. |
| S Compass (`estimators.py :: capacity_field`) | $\kappa = \dfrac{1}{1+\beta\sigma^2}$, where $\sigma^2$ blends context load, latency CV, and tool-failure rate. |

---

## 5. Constants and parameters

| Symbol | Role | Value / source |
|--------|------|----------------|
| $\beta$ | Complexity coupling in the URP Lagrangian | $\approx 0.09$, from QCD scaling (not fitted to atomic data). |
| $G$ | Coherence-advection coupling in the URP Lagrangian | $\approx 0.22$, from instanton fractions in the QCD vacuum. |
| $\lambda$ | Gap-sensitivity in the ordinal $\kappa$ | Free parameter (URP §2.3). |
| $\rho_t$ | Dimensionless load factor in the ordinal $\kappa$ | Computational/energy/resource stress (URP §2.3). |
| $\lambda_{red},\ \lambda_{syn}$ | Redundancy / synergy weights | Information-theoretic layer (URP §4). |
| $G_t$ | Incompleteness gap $C(F_t)-I(F_t)$ | Regenerative; never closes (URP §2.1). |

---

## 6. Overloaded symbols — read with care

A few letters are reused for genuinely different things. The current docs do not
always flag this, so watch for:

- **$\beta$** is used three ways: (1) the universal **complexity coupling**
  $\beta\approx 0.09$ in the field Lagrangian; (2) a **sigmoid sharpness** in the
  capacity formula $\kappa = 1/(1+\beta\sigma^2)$ (Transformer-Dynamics §4); and
  (3) in code, `capacity_field(..., beta=5.0)` — the §4-style sharpness, *not*
  the 0.09 coupling. The capacity-$\beta$ and the Lagrangian-$\beta$ are
  unrelated despite sharing the letter.
- **$G$** is used three ways: the **coherence coupling** $G\approx 0.22$; the
  **incompleteness gap** $G_t = C(F_t)-I(F_t)$; and the **graph** $G_t=(V_t,E_t)$
  in the graph layer. Disambiguate by subscript and context.
- **$C$ and $I$** mean *capacities* (representational / inferential ordinals) in
  the logic layer, but *levels* (entropy / attention structure) everywhere else.
  The ordinal $C(F)$ is a ceiling; the transformer/S Compass $C$ is a measured
  quantity.
- **$S^{(l)}$ vs $S_t$**: superscript $(l)$ indexes transformer *layers*
  (Transformer-Dynamics §6); subscript $t$ indexes *time steps* (the rest of the
  framework and the S Compass).

---

## 7. Regime vocabularies

Two regime label sets exist; see
[Level-and-Delta-Forms.md §4](Level-and-Delta-Forms.md) for the full tables.

- **State regimes** (level form): `creative-grounded`, `rigid`,
  `hallucination-risk`, `collapse` — *where the system is*.
- **Trajectory regimes** (delta form): `expanding`, `diverging`,
  `consolidating`, `contracting`, `steady`, `initial` — *where it is heading*.
