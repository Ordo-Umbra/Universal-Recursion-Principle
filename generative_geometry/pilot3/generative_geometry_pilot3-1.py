"""
Generative Geometry — Pilot 3: robustness and generalization check.

Tests whether a simple relational-curvature sampling heuristic remains useful
when the underlying angular landscape, initial ray count, noise, and budget vary.

Strategies:
- fixed: repeat measurements at the initial rays
- random: choose new angles uniformly
- relational_curvature: bisect the interval with the largest width-weighted
  change in neighboring slopes
- hybrid: use relational curvature most of the time, with 25% random exploration

This is a toy active-sampling benchmark. It tests reconstruction of a
pre-existing function, not creation of new ontological distinctions.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

N_REPLICATES = 60
NOISE_LEVELS = [0.0, 0.03, 0.10]
INITIAL_COUNTS = [6, 8, 12]
BUDGETS = [12, 24, 36]
FAMILIES = ["smooth_mixed", "narrow_features", "oscillatory"]
GRID_SIZE = 1200

def wrap(a):
    return np.mod(a, 2*np.pi)

def delta(a, b):
    return np.angle(np.exp(1j*(a-b)))

def make_landscape(family, rng):
    # Parameters are randomized independently for every replicate.
    phases = rng.uniform(0, 2*np.pi, 4)
    amps = rng.uniform(0.08, 0.32, 4)
    centers = rng.uniform(0, 2*np.pi, 3)
    signs = rng.choice([-1.0, 1.0], 3)
    widths = rng.uniform(0.07, 0.32, 3)
    bump_amps = rng.uniform(0.25, 0.9, 3)

    def f(theta):
        t = np.asarray(theta)
        base = sum(amps[k] * np.sin((k+1)*t + phases[k]) for k in range(4))
        if family == "smooth_mixed":
            bumps = sum(
                signs[k] * bump_amps[k] *
                np.exp(-0.5*(delta(t, centers[k])/widths[k])**2)
                for k in range(2)
            )
            return base + bumps
        if family == "narrow_features":
            # Narrow peaks/dips are deliberately difficult for coarse sampling.
            bumps = sum(
                signs[k] * bump_amps[k] *
                np.exp(-0.5*(delta(t, centers[k])/widths[k])**2)
                for k in range(3)
            )
            return 0.12*base + bumps
        if family == "oscillatory":
            # More rapid variation; local curvature can be ambiguous under sparse sampling.
            return 0.12*base + 0.22*np.sin(7*t + phases[0]) + 0.13*np.cos(11*t + phases[1])
        raise ValueError(family)
    return f

def observe(f, a, noise, rng):
    return float(f(a) + rng.normal(0, noise))

def interpolate(xs, ys, grid):
    order = np.argsort(wrap(xs))
    x = wrap(np.asarray(xs)[order])
    y = np.asarray(ys)[order]
    xp = np.r_[x[-1]-2*np.pi, x, x[0]+2*np.pi]
    yp = np.r_[y[-1], y, y[0]]
    return np.interp(wrap(grid), xp, yp)

def interval_data(xs, ys):
    order = np.argsort(wrap(xs))
    x = wrap(np.asarray(xs)[order])
    y = np.asarray(ys)[order]
    xe = np.r_[x, x[0]+2*np.pi]
    ye = np.r_[y, y[0]]
    widths = np.diff(xe)
    slopes = np.diff(ye)/widths
    return x, widths, slopes

def choose_curvature(xs, ys):
    x, widths, slopes = interval_data(xs, ys)
    n = len(slopes)
    scores = np.zeros(n)
    for j in range(n):
        change_left = abs(slopes[j] - slopes[(j-1) % n])
        change_right = abs(slopes[(j+1) % n] - slopes[j])
        # A heuristic score, not a theoretically derived optimality criterion.
        scores[j] = widths[j]**2 * (0.20 + max(change_left, change_right))
    j = int(np.argmax(scores))
    return wrap(x[j] + widths[j]/2)

def choose_new_angle(xs, ys, strategy, rng):
    if strategy == "random":
        return rng.uniform(0, 2*np.pi)
    if strategy == "relational_curvature":
        return choose_curvature(xs, ys)
    if strategy == "hybrid":
        if rng.random() < 0.25:
            return rng.uniform(0, 2*np.pi)
        return choose_curvature(xs, ys)
    raise ValueError(strategy)

def run_one(family, initial_n, budget, noise, replicate, strategy):
    # Same landscape and initial rays for every strategy within a condition.
    master = np.random.default_rng(
        1_000_000 + replicate*101 + initial_n*13 + budget*7 +
        int(noise*1000)*3 + FAMILIES.index(family)*997
    )
    f = make_landscape(family, master)
    initial = np.linspace(0, 2*np.pi, initial_n, endpoint=False)
    grid = np.linspace(0, 2*np.pi, GRID_SIZE, endpoint=False)
    truth = f(grid)

    # Strategy-specific RNGs; initial noisy observations are shared to make
    # the comparison paired and reduce irrelevant variation.
    initial_rng = np.random.default_rng(
        2_000_000 + replicate*103 + initial_n*17 + budget*11 +
        int(noise*1000)*5 + FAMILIES.index(family)*991
    )
    initial_y = [observe(f, a, noise, initial_rng) for a in initial]

    rng = np.random.default_rng(
        3_000_000 + replicate*107 + initial_n*19 + budget*13 +
        int(noise*1000)*7 + FAMILIES.index(family)*983 +
        ["fixed", "random", "relational_curvature", "hybrid"].index(strategy)*100003
    )
    xs = list(initial)
    ys = list(initial_y)

    if strategy == "fixed":
        sums = np.array(ys, dtype=float)
        counts = np.ones(initial_n, dtype=int)
        for k in range(budget):
            j = k % initial_n
            sums[j] += observe(f, xs[j], noise, rng)
            counts[j] += 1
        ys = list(sums/counts)
    else:
        for _ in range(budget):
            a = choose_new_angle(xs, ys, strategy, rng)
            if np.min(np.abs(delta(np.asarray(xs), a))) < 1e-7:
                # Prevent duplicate locations; use a random fallback.
                for _attempt in range(100):
                    a = rng.uniform(0, 2*np.pi)
                    if np.min(np.abs(delta(np.asarray(xs), a))) >= 1e-7:
                        break
            xs.append(a)
            ys.append(observe(f, a, noise, rng))

    pred = interpolate(xs, ys, grid)
    mse = float(np.mean((pred-truth)**2))
    return mse

def main():
    strategies = ["fixed", "random", "relational_curvature", "hybrid"]
    rows = []
    for family in FAMILIES:
        for initial_n in INITIAL_COUNTS:
            for budget in BUDGETS:
                for noise in NOISE_LEVELS:
                    scores = {s: [] for s in strategies}
                    for rep in range(N_REPLICATES):
                        for s in strategies:
                            scores[s].append(run_one(
                                family, initial_n, budget, noise, rep, s
                            ))
                    for s in strategies:
                        rows.append({
                            "family": family,
                            "initial_rays": initial_n,
                            "additional_budget": budget,
                            "noise_sd": noise,
                            "strategy": s,
                            "mean_mse": np.mean(scores[s]),
                            "sd_mse": np.std(scores[s], ddof=1),
                            "replicates": N_REPLICATES
                        })

    df = pd.DataFrame(rows)
    df.to_csv("generative_geometry_pilot3_results.csv", index=False)

    # Aggregate across all tested conditions, with equal weight per condition.
    aggregate = (
        df.groupby("strategy")
          .agg(mean_condition_mse=("mean_mse", "mean"),
               median_condition_mse=("mean_mse", "median"),
               conditions=("mean_mse", "count"))
          .reset_index()
          .sort_values("mean_condition_mse")
    )
    aggregate.to_csv("generative_geometry_pilot3_aggregate.csv", index=False)
    print("Aggregate across 81 conditions:")
    print(aggregate.to_string(index=False))

    # Relative performance by landscape family.
    family_table = df.groupby(["family", "strategy"])["mean_mse"].mean().unstack()
    print("\nMean error by landscape family:")
    print(family_table.to_string())

    ax = family_table.plot(kind="bar", figsize=(10, 5))
    ax.set_ylabel("Mean reconstruction error")
    ax.set_title("Pilot 3 — Average error by randomized landscape family")
    ax.set_xlabel("Landscape family")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("generative_geometry_pilot3_families.png", dpi=160)

    # Plot strategy performance as noise changes.
    noise_table = df.groupby(["noise_sd", "strategy"])["mean_mse"].mean().unstack()
    ax = noise_table.plot(marker="o", figsize=(9, 5))
    ax.set_ylabel("Mean reconstruction error")
    ax.set_title("Pilot 3 — Sensitivity to measurement noise")
    ax.set_xlabel("Measurement noise standard deviation")
    plt.tight_layout()
    plt.savefig("generative_geometry_pilot3_noise.png", dpi=160)

    # Per-condition wins, useful because an aggregate can conceal failures.
    winners = df.loc[df.groupby(
        ["family", "initial_rays", "additional_budget", "noise_sd"]
    )["mean_mse"].idxmin()]
    print("\nCondition wins:")
    print(winners["strategy"].value_counts().to_string())
    print("\nSaved detailed and aggregate CSVs and figures.")

if __name__ == "__main__":
    main()
