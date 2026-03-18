# The Universal Recursion Principle (URP)

Welcome to the foundational repository for the **Universal Recursion Principle** and the **S-Functional framework**.

This repository houses the theoretical papers, mathematical formalisms, and computational simulations that define URP—a unified framework proposing that physics, biology, and cognition are driven by a single dynamical law: the maximization of recursive understanding under capacity constraints.

## What is URP?

Contemporary science lacks a single dynamical quantity that distinguishes sustainable, open-ended growth from transient amplification followed by collapse. In physics, we track entropy or action; in AI, we track loss or reward. 

URP proposes that any sufficiently expressive recursive system evolves to maximize a scalar functional:

**S = ΔC + κΔI**

Where:
* **ΔC (Distinction):** The growth of meaningful new structure, boundaries, and resolution.
* **ΔI (Integration):** The coherent weaving of those distinctions into a predictive, globally unified whole.
* **κ (Capacity):** An effective field encoding resource limits (energy, compute, noise) that suppresses integration when the system is under stress.

When $S$ is maximized locally, we see the emergence of physical gauge symmetries, atomic orbital structures, and biological Maxwell's demons. When $S$ is used as a target for artificial intelligence and institutional design, it provides an objective that avoids specification gaming and self-termination.

## Repository Structure

* `/docs/` - Core technical foundations, including the primary URP mathematical formalization, the derivation of $G$ and $\beta$, and the translation of Gödelian incompleteness into physical dynamics.
* `/sims/` - Python and computational models testing the S-functional on graph networks, demonstrating how curvature maps to the capacity field $kappa$.
* `/references/` - Integrations mapping URP onto other emerging frameworks (e.g., Geometric Genesis, Information Thermodynamics, Biological Demons).

## Getting Started

If you are new to URP, we recommend reading the documents in this order:

1. **[Seeding a Civilization That Doesn't Self-Terminate](docs/Seeding_a_Civilization.md)** - A high-level manifesto on why current optimization metrics fail and why S is required.
2. **[The S-Functional as a Universal Dynamical Objective](docs/S_Functional_Formalization.md)** - The rigorous multi-layer formalization of URP across logic, physics, and graphs.
3. **[URP Technical Foundations](docs/URP_Technical_Foundations.pdf)** - The derivation of physical constants and gauge symmetries from S-maximization.

## 🎯 Sims Gallery (Fully Reproducible)

All simulations are pure URP, standalone, and match the results in the paper.  
Just run `pip install -r requirements.txt` once, then:

| Sim | File | What it shows | Command |
|-----|------|---------------|---------|
| **Helium 112-ppm** | `sims/helium_variational.py` | Flagship variational result (Z_eff ≈ 1.8366, IP = 24.590 eV) | `python sims/helium_variational.py` |
| **Squeezed-Light Negative Energy** | `sims/squeezed_light_negative_energy.py` | Local ΔS deficits + global S growth + Q_S bound | `python sims/squeezed_light_negative_energy.py` |
| **QCD Attractor Emergence** | `sims/qcd_attractor_emergence.py` | 0d points, 1d lines, 2d domains self-organize from noise | `python sims/qcd_attractor_emergence.py` |
| **Causality Protection** | `sims/causality_protection_theorem.py` | Finite propagation speed = effective c (no superluminal signaling) | `python sims/causality_protection_theorem.py` |
| **β & G Emergence** | `sims/beta_g_emergence.py` | Universal parameters β≈0.09 and G≈0.22 self-stabilize from S-max | `python sims/beta_g_emergence.py` |

Every sim saves its plot automatically and prints a clear summary. Clone, run, reproduce — no setup headaches.

---

**Next sims coming soon:**
- Multi-agent Graph-S cooperation (AI alignment demo)
- Full 3D field evolution
- Hybrid cavity + causality test

Contributions and issues welcome — this is the public seed of the Universal Recursion Principle.

## Contributing

This framework is actively expanding as new correspondences are found in information thermodynamics, quantum vacuum models, and AI alignment. If you are running simulations, testing the S-functional on neural network representations, or mapping URP to specific domains, pull requests are welcome.

## License
MIT License
