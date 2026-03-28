"""
biology_urp.py

Biology simulation: life as a Universal Recursion Engine.

Implements a discrete-time model of a biological Maxwell's demon (minimal
cell or enzyme complex) maximising the S-functional

    S = ΔC + κ * ΔI

over a noisy thermodynamic environment, as described in
``Docs/Life as a Universal Recursion Engine.txt``.

Three biologically grounded components are simulated:

1. **Minimal-genome demon** – substrate discrimination under finite capacity κ.
   Each time-step the cell measures a noisy chemical gradient (producing ΔC),
   then uses that distinction to drive a directional flux (producing ΔI),
   capped by the current κ.

2. **Enzyme S-demon** – post-catalytic memory (Enhanced Enzyme Diffusion).
   After each catalytic event the enzyme carries a 1-bit memory of the
   reaction, biasing its next collision and creating a steady-state deviation
   from chemical equilibrium.

3. **Sagawa–Ito budget constraint** – entropy production is bounded by
   information inflow.  The simulation checks that ΔI ≤ κ * ΔC at every step,
   mirroring the bound σ̇_X ≤ İ_{Y→X}.

Key public functions
--------------------
simulate_cell_demon(n_steps, kappa_schedule)
    Run the minimal-genome demon and return per-step (delta_C, delta_I, kappa, S).

simulate_enzyme_demon(n_steps, memory_decay)
    Run the enzyme EED demon and return per-step (C, I, kappa, S, deviation).

sagawa_ito_check(delta_C_series, delta_I_series, kappa_series)
    Verify the Sagawa–Ito bound holds at every step.
"""

from __future__ import annotations

import numpy as np
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _shannon_entropy(p: np.ndarray) -> float:
    """Shannon entropy of a discrete probability distribution."""
    p = p + 1e-12
    p = p / p.sum()
    return float(-np.sum(p * np.log(p)))


# ---------------------------------------------------------------------------
# 1. Minimal-genome demon (substrate discrimination)
# ---------------------------------------------------------------------------

def simulate_cell_demon(
    n_steps: int = 60,
    rng_seed: int = 42,
    noise_std: float = 0.15,
    base_kappa: float = 0.8,
    kappa_schedule: List[float] | None = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Simulate a minimal-genome Maxwell's demon maximising S.

    At each step the demon:

    1. Observes a noisy binary chemical gradient to produce ΔC (distinction).
    2. Uses that distinction to drive a directional flux producing ΔI
       (integration), scaled by the current capacity κ.
    3. Accumulates S = ΔC + κ * ΔI.

    Capacity κ follows *kappa_schedule* if provided, otherwise a slow-decay
    schedule modelling resource depletion and recovery.

    Parameters
    ----------
    n_steps:
        Number of time-steps to simulate.
    rng_seed:
        Seed for reproducible random number generation.
    noise_std:
        Standard deviation of the observation noise on the gradient signal.
    base_kappa:
        Baseline capacity when no schedule is provided.
    kappa_schedule:
        Optional per-step κ values.  When shorter than *n_steps* the last
        value is repeated.

    Returns
    -------
    (delta_C, delta_I, kappa, S) each a 1-D array of length *n_steps*.
    """
    rng = np.random.default_rng(rng_seed)

    if kappa_schedule is not None:
        kappas = np.array(kappa_schedule, dtype=float)
        if len(kappas) < n_steps:
            kappas = np.pad(kappas, (0, n_steps - len(kappas)), mode="edge")
        kappas = kappas[:n_steps]
    else:
        # Slow oscillating resource availability
        t = np.linspace(0, 4 * np.pi, n_steps)
        kappas = base_kappa + 0.15 * np.sin(t)
        kappas = np.clip(kappas, 0.1, 1.0)

    delta_C = np.zeros(n_steps)
    delta_I = np.zeros(n_steps)
    S = np.zeros(n_steps)

    # Chemical gradient: true concentration difference between inside/outside
    true_gradient = rng.uniform(0.3, 0.9, size=n_steps)

    for t in range(n_steps):
        kappa_t = kappas[t]

        # ΔC — demon discriminates signal from noise
        noisy_obs = true_gradient[t] + rng.normal(0, noise_std)
        # Distinction = mutual information proxy: how well the observation
        # resolves the high/low gradient hypothesis
        p_high = float(np.clip(noisy_obs, 0.0, 1.0))
        p_low = 1.0 - p_high
        obs_entropy = _shannon_entropy(np.array([p_high, p_low]))
        # Maximum entropy = log(2); ΔC = reduction from maximum
        delta_C[t] = max(0.0, np.log(2) - obs_entropy)

        # ΔI — demon acts on the distinction to drive directed flux
        # Integration is the directed flux magnitude, capped by κ
        directed_flux = true_gradient[t] * delta_C[t]
        delta_I[t] = kappa_t * directed_flux

        S[t] = delta_C[t] + kappa_t * delta_I[t]

    return delta_C, delta_I, kappas, S


# ---------------------------------------------------------------------------
# 2. Enzyme S-demon (Enhanced Enzyme Diffusion / post-catalytic memory)
# ---------------------------------------------------------------------------

def simulate_enzyme_demon(
    n_steps: int = 80,
    rng_seed: int = 7,
    memory_decay: float = 0.3,
    base_rate: float = 1.0,
    kappa_env: float = 0.6,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Simulate an enzyme Maxwell's demon with post-catalytic memory (EED).

    After each catalytic event the enzyme holds a short-lived memory of which
    reaction just occurred.  This 1-bit memory biases its next collision,
    pushing the steady-state product distribution away from equilibrium.

    The deviation from chemical equilibrium at step *t* is used as a proxy
    for ΔI (the memory-driven integration gain).

    Parameters
    ----------
    n_steps:
        Number of catalytic cycles to simulate.
    rng_seed:
        Seed for reproducibility.
    memory_decay:
        Exponential decay constant for the EED memory (per step).
    base_rate:
        Baseline catalytic rate (arbitrary units).
    kappa_env:
        Environmental capacity (noise/crowding factor).

    Returns
    -------
    (C, I, kappa, S, deviation) each a 1-D array of length *n_steps*.
        ``deviation`` is the steady-state displacement from equilibrium
        produced by the demon memory at each step.
    """
    rng = np.random.default_rng(rng_seed)

    C = np.zeros(n_steps)
    I = np.zeros(n_steps)
    kappa = np.full(n_steps, kappa_env)
    S = np.zeros(n_steps)
    deviation = np.zeros(n_steps)

    memory = 0.0  # current memory strength (decays each step)

    for t in range(n_steps):
        # Catalytic event: product formed with Poisson fluctuation
        products_formed = rng.poisson(base_rate)

        # ΔC — 1-bit memory of last event (which reaction just happened)
        # Encode as entropy reduction: memory encodes one bit iff products>0
        if products_formed > 0:
            memory = min(memory + 1.0, 1.0)
        memory *= (1.0 - memory_decay)

        p_mem = np.clip(memory, 1e-9, 1.0 - 1e-9)
        bit_entropy = _shannon_entropy(np.array([p_mem, 1.0 - p_mem]))
        C[t] = max(0.0, np.log(2) - bit_entropy)

        # ΔI — memory biases next collision → deviation from equilibrium
        # Deviation is proportional to memory strength × rate
        eq_fraction = 0.5  # equilibrium product fraction
        biased_fraction = eq_fraction + memory * 0.3
        deviation[t] = abs(biased_fraction - eq_fraction)
        I[t] = deviation[t] * products_formed

        # κ — inversely proportional to local crowding (modelled as noise)
        noise = rng.uniform(0.0, 0.4)
        kappa[t] = kappa_env / (1.0 + noise)

        S[t] = C[t] + kappa[t] * I[t]

    return C, I, kappa, S, deviation


# ---------------------------------------------------------------------------
# 3. Sagawa–Ito budget check
# ---------------------------------------------------------------------------

def sagawa_ito_check(
    delta_C: np.ndarray,
    delta_I: np.ndarray,
    kappa: np.ndarray,
) -> Tuple[np.ndarray, bool]:
    """Verify the Sagawa–Ito bound: ΔI ≤ κ * ΔC at every step.

    In URP notation the entropy production in a subsystem is bounded by the
    information flowing in from connected systems (sigma_dot_X <= I_dot_{Y->X},
    where I_dot denotes the information inflow rate).
    Here the bound becomes ΔI ≤ κ * ΔC: you cannot build coherent structure
    faster than you receive information.

    Parameters
    ----------
    delta_C:
        Per-step distinction increments (information inflow).
    delta_I:
        Per-step integration increments (organisation gain).
    kappa:
        Per-step capacity values.

    Returns
    -------
    (violations_mask, all_satisfied)
        ``violations_mask`` is a boolean array marking steps where the bound
        is violated.  ``all_satisfied`` is True iff no violations occurred.
    """
    upper_bound = kappa * delta_C
    violations = delta_I > upper_bound + 1e-9
    return violations, bool(~violations.any())


# ---------------------------------------------------------------------------
# Entry point: print regime summary
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    print("=== Minimal-Genome Demon ===")
    dC, dI, kap, S_cell = simulate_cell_demon(n_steps=60)
    print(f"  Mean ΔC   : {dC.mean():.4f}")
    print(f"  Mean ΔI   : {dI.mean():.4f}")
    print(f"  Mean κ    : {kap.mean():.4f}")
    print(f"  Final S   : {S_cell[-1]:.4f}")
    print(f"  Total S   : {S_cell.sum():.4f}")

    violations, ok = sagawa_ito_check(dC, dI, kap)
    print(f"  Sagawa-Ito bound satisfied: {ok}")

    print("\n=== Enzyme EED Demon ===")
    C_enz, I_enz, kap_enz, S_enz, dev = simulate_enzyme_demon(n_steps=80)
    print(f"  Mean C    : {C_enz.mean():.4f}")
    print(f"  Mean I    : {I_enz.mean():.4f}")
    print(f"  Mean κ    : {kap_enz.mean():.4f}")
    print(f"  Mean dev  : {dev.mean():.4f}")
    print(f"  Final S   : {S_enz[-1]:.4f}")

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("Biology URP: Maxwell's Demon S-Functional", fontsize=14)

    axes[0, 0].plot(S_cell)
    axes[0, 0].set_title("Cell Demon: Cumulative S")
    axes[0, 0].set_xlabel("Step")
    axes[0, 0].set_ylabel("S")

    axes[0, 1].plot(dC, label="ΔC")
    axes[0, 1].plot(dI, label="ΔI")
    axes[0, 1].plot(kap, label="κ", linestyle="--")
    axes[0, 1].set_title("Cell Demon: ΔC, ΔI, κ")
    axes[0, 1].legend()

    axes[1, 0].plot(S_enz)
    axes[1, 0].set_title("Enzyme Demon: S per Step")
    axes[1, 0].set_xlabel("Catalytic cycle")

    axes[1, 1].plot(dev)
    axes[1, 1].set_title("Enzyme Demon: Equilibrium Deviation")
    axes[1, 1].set_xlabel("Catalytic cycle")
    axes[1, 1].set_ylabel("Deviation")

    plt.tight_layout()
    plt.savefig("biology_urp.png", dpi=120)
    print("\nSaved biology_urp.png")
