"""
Generative Geometry — Pilot 3b: audit and strengthening pass.

Purpose
-------
Test which components of the Pilot 3 relational-curvature heuristic account for
its reconstruction performance. This remains a toy active-sampling benchmark
for reconstructing pre-existing periodic functions. It does not test the
creation of new ontological distinctions.

Strengthening changes relative to Pilot 3
----------------------------------------
1. Adds deterministic space-filling, gradient, curvature-only, and
   width-times-curvature ablations alongside the original strategies.
2. Uses the same landscape across initial counts, budgets, and noise levels
   for each family/replicate pair.
3. Generates one maximum-budget trajectory and evaluates nested budgets at
   checkpoints 12, 24, and 36.
4. Shares initial observation noise across strategies and uses matched
   standard-normal noise streams across noise levels where applicable.
5. Saves every replicate-level result, not only condition summaries.
6. Reports normalized MSE, relative performance, exact condition winners, and
   paired 95% confidence intervals for NMSE differences.

The original relational-curvature score is unchanged:
    width**2 * (0.20 + max(absolute neighboring slope changes)).

Usage
-------
    python3 generative_geometry_pilot3b.py --output-dir ./pilot3b_output
    python3 generative_geometry_pilot3b.py --replicates 5 --output-dir ./smoke

Default: 60 replicates. All random seeds are deterministic.
"""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from scipy.stats import t as student_t

DEFAULT_REPLICATES = 60
NOISE_LEVELS = [0.0, 0.03, 0.10]
INITIAL_COUNTS = [6, 8, 12]
BUDGETS = [12, 24, 36]
FAMILIES = ["smooth_mixed", "narrow_features", "oscillatory"]
GRID_SIZE = 1200

STRATEGIES = [
    "repeat_initial",
    "random",
    "widest_interval",
    "largest_gradient",
    "curvature_only",
    "weighted_curvature",
    "relational_curvature",
    "hybrid",
]

FOCAL_STRATEGY = "relational_curvature"
COMPARATORS = [s for s in STRATEGIES if s != FOCAL_STRATEGY]


def wrap(a):
    """Wrap angles to [0, 2*pi)."""
    return np.mod(a, 2 * np.pi)


def delta(a, b):
    """Shortest signed angular difference a-b."""
    return np.angle(np.exp(1j * (a - b)))


def landscape_seed(family, replicate):
    """Landscape depends only on family and replicate, enabling paired checks."""
    return 1_000_000 + replicate * 101 + FAMILIES.index(family) * 997


def initial_noise_seed(family, initial_n, replicate):
    return (
        2_000_000
        + replicate * 103
        + initial_n * 17
        + FAMILIES.index(family) * 991
    )


def strategy_seed(family, initial_n, replicate, strategy):
    """Noise and budget are deliberately absent: trajectories can be nested."""
    return (
        3_000_000
        + replicate * 107
        + initial_n * 19
        + FAMILIES.index(family) * 983
        + STRATEGIES.index(strategy) * 100003
    )


def make_landscape(family, rng):
    """Create a randomized periodic landscape; parameters match Pilot 3."""
    phases = rng.uniform(0, 2 * np.pi, 4)
    amps = rng.uniform(0.08, 0.32, 4)
    centers = rng.uniform(0, 2 * np.pi, 3)
    signs = rng.choice([-1.0, 1.0], 3)
    widths = rng.uniform(0.07, 0.32, 3)
    bump_amps = rng.uniform(0.25, 0.9, 3)

    def f(theta):
        t = np.asarray(theta)
        base = sum(
            amps[k] * np.sin((k + 1) * t + phases[k]) for k in range(4)
        )
        if family == "smooth_mixed":
            bumps = sum(
                signs[k]
                * bump_amps[k]
                * np.exp(-0.5 * (delta(t, centers[k]) / widths[k]) ** 2)
                for k in range(2)
            )
            return base + bumps
        if family == "narrow_features":
            bumps = sum(
                signs[k]
                * bump_amps[k]
                * np.exp(-0.5 * (delta(t, centers[k]) / widths[k]) ** 2)
                for k in range(3)
            )
            return 0.12 * base + bumps
        if family == "oscillatory":
            return (
                0.12 * base
                + 0.22 * np.sin(7 * t + phases[0])
                + 0.13 * np.cos(11 * t + phases[1])
            )
        raise ValueError(family)

    return f


def interpolate(xs, ys, grid):
    """Periodic piecewise-linear reconstruction used by every strategy."""
    order = np.argsort(wrap(xs))
    x = wrap(np.asarray(xs)[order])
    y = np.asarray(ys)[order]
    xp = np.r_[x[-1] - 2 * np.pi, x, x[0] + 2 * np.pi]
    yp = np.r_[y[-1], y, y[0]]
    return np.interp(wrap(grid), xp, yp)


def interval_data(xs, ys):
    """Return sorted starts, widths, and secant slopes on the periodic domain."""
    order = np.argsort(wrap(xs))
    x = wrap(np.asarray(xs)[order])
    y = np.asarray(ys)[order]
    xe = np.r_[x, x[0] + 2 * np.pi]
    ye = np.r_[y, y[0]]
    widths = np.diff(xe)
    slopes = np.diff(ye) / widths
    return x, widths, slopes


def neighboring_curvature(slopes):
    """Maximum absolute change between an interval's and its neighbor's slope."""
    n = len(slopes)
    changes = np.zeros(n)
    for j in range(n):
        change_left = abs(slopes[j] - slopes[(j - 1) % n])
        change_right = abs(slopes[(j + 1) % n] - slopes[j])
        changes[j] = max(change_left, change_right)
    return changes


def choose_scored_interval(scores, widths):
    """Maximize score; break exact ties by width, then by first occurrence."""
    scores = np.asarray(scores)
    best = np.max(scores)
    candidates = np.flatnonzero(np.isclose(scores, best, rtol=1e-12, atol=1e-15))
    if len(candidates) > 1:
        candidate_widths = widths[candidates]
        candidates = candidates[np.isclose(
            candidate_widths,
            np.max(candidate_widths),
            rtol=1e-12,
            atol=1e-15,
        )]
    return int(candidates[0])


def choose_curvature(xs, ys):
    """Original Pilot 3 selection rule, retained without changing its score."""
    x, widths, slopes = interval_data(xs, ys)
    changes = neighboring_curvature(slopes)
    scores = widths**2 * (0.20 + changes)
    j = int(np.argmax(scores))
    return wrap(x[j] + widths[j] / 2)


def choose_new_angle(xs, ys, strategy, rng):
    """Choose a new measurement location, or None for repeat_initial."""
    if strategy == "repeat_initial":
        return None
    if strategy == "random":
        return rng.uniform(0, 2 * np.pi)
    if strategy == "hybrid" and rng.random() < 0.25:
        return rng.uniform(0, 2 * np.pi)
    if strategy in ("relational_curvature", "hybrid"):
        return choose_curvature(xs, ys)

    x, widths, slopes = interval_data(xs, ys)
    changes = neighboring_curvature(slopes)
    if strategy == "widest_interval":
        scores = widths
    elif strategy == "largest_gradient":
        scores = np.abs(slopes)
    elif strategy == "curvature_only":
        scores = changes
    elif strategy == "weighted_curvature":
        scores = widths**2 * changes
    else:
        raise ValueError(strategy)

    j = choose_scored_interval(scores, widths)
    return wrap(x[j] + widths[j] / 2)


def nonduplicate_angle(xs, a, rng):
    """Retain Pilot 3's guard against numerically duplicate locations."""
    if np.min(np.abs(delta(np.asarray(xs), a))) >= 1e-7:
        return a
    for _attempt in range(100):
        a = rng.uniform(0, 2 * np.pi)
        if np.min(np.abs(delta(np.asarray(xs), a))) >= 1e-7:
            return a
    raise RuntimeError("Could not find a nonduplicate angle after 100 attempts")


def run_trajectory(
    family,
    initial_n,
    noise,
    replicate,
    strategy,
    f,
    grid,
    truth,
    truth_variance,
):
    """Run to the maximum budget and return nested-checkpoint measurements."""
    l_seed = landscape_seed(family, replicate)
    i_seed = initial_noise_seed(family, initial_n, replicate)
    s_seed = strategy_seed(family, initial_n, replicate, strategy)

    initial = np.linspace(0, 2 * np.pi, initial_n, endpoint=False)
    initial_rng = np.random.default_rng(i_seed)
    initial_z = initial_rng.normal(size=initial_n)
    initial_y = np.asarray(f(initial)) + noise * initial_z

    rng = np.random.default_rng(s_seed)
    xs = list(initial)
    ys = list(initial_y)
    rows = []

    def record(budget):
        pred = interpolate(xs, ys, grid)
        residual = pred - truth
        mse = float(np.mean(residual**2))
        nmse = mse / truth_variance
        rows.append({
            "family": family,
            "replicate": replicate,
            "initial_rays": initial_n,
            "additional_budget": budget,
            "noise_sd": noise,
            "strategy": strategy,
            "mse": mse,
            "nmse": nmse,
            "max_abs_error": float(np.max(np.abs(residual))),
            "truth_variance": truth_variance,
            "landscape_seed": l_seed,
            "initial_noise_seed": i_seed,
            "strategy_seed": s_seed,
        })

    if strategy == "repeat_initial":
        sums = np.asarray(ys, dtype=float).copy()
        counts = np.ones(initial_n, dtype=int)
        for step in range(max(BUDGETS)):
            j = step % initial_n
            z = rng.normal()
            sums[j] += float(f(xs[j])) + noise * z
            counts[j] += 1
            ys = list(sums / counts)
            if step + 1 in BUDGETS:
                record(step + 1)
        return rows

    for step in range(max(BUDGETS)):
        a = choose_new_angle(xs, ys, strategy, rng)
        a = nonduplicate_angle(xs, a, rng)
        z = rng.normal()
        xs.append(a)
        ys.append(float(f(a)) + noise * z)
        if step + 1 in BUDGETS:
            record(step + 1)
    return rows


def condition_summary(raw):
    keys = [
        "family",
        "initial_rays",
        "additional_budget",
        "noise_sd",
        "strategy",
    ]
    return (
        raw.groupby(keys, sort=True)
        .agg(
            mean_mse=("mse", "mean"),
            sd_mse=("mse", "std"),
            mean_nmse=("nmse", "mean"),
            sd_nmse=("nmse", "std"),
            mean_max_abs_error=("max_abs_error", "mean"),
            replicates=("mse", "size"),
        )
        .reset_index()
    )


def paired_comparisons(raw):
    """Paired NMSE differences: negative values favor relational curvature."""
    condition_keys = ["family", "initial_rays", "additional_budget", "noise_sd"]
    rows = []
    for condition, group in raw.groupby(condition_keys, sort=True):
        wide = group.pivot(index="replicate", columns="strategy", values="nmse")
        for comparator in COMPARATORS:
            paired = wide[[FOCAL_STRATEGY, comparator]].dropna()
            difference = paired[FOCAL_STRATEGY] - paired[comparator]
            n = len(difference)
            mean_difference = float(difference.mean())
            sd = float(difference.std(ddof=1))
            se = sd / np.sqrt(n)
            critical = float(student_t.ppf(0.975, n - 1))
            margin = critical * se
            rows.append({
                **dict(zip(condition_keys, condition)),
                "comparator": comparator,
                "replicates": n,
                "focal_mean_nmse": float(paired[FOCAL_STRATEGY].mean()),
                "comparator_mean_nmse": float(paired[comparator].mean()),
                "mean_nmse_difference": mean_difference,
                "ci95_low": mean_difference - margin,
                "ci95_high": mean_difference + margin,
                "paired_win_fraction": float(np.mean(difference < 0)),
                "mean_error_ratio": float(
                    paired[FOCAL_STRATEGY].mean()
                    / paired[comparator].mean()
                ),
                "ci_excludes_zero": bool(
                    (mean_difference - margin) * (mean_difference + margin) > 0
                ),
            })
    return pd.DataFrame(rows)


def exact_condition_winners(summary):
    condition_keys = ["family", "initial_rays", "additional_budget", "noise_sd"]
    indices = summary.groupby(condition_keys)["mean_nmse"].idxmin()
    return summary.loc[indices].sort_values(condition_keys).reset_index(drop=True)


def save_figures(summary, output_dir):
    family_table = (
        summary.groupby(["family", "strategy"])["mean_nmse"]
        .mean()
        .unstack()
        .reindex(columns=STRATEGIES)
    )
    ax = family_table.plot(kind="bar", figsize=(14, 6))
    ax.set_ylabel("Mean normalized reconstruction MSE")
    ax.set_title("Pilot 3b — Performance by landscape family")
    ax.set_xlabel("Landscape family")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_dir / "pilot3b_family_nmse.png", dpi=160)
    plt.close()

    curve_strategies = [
        "repeat_initial",
        "random",
        "widest_interval",
        "weighted_curvature",
        "relational_curvature",
        "hybrid",
    ]
    budget_table = (
        summary[summary["strategy"].isin(curve_strategies)]
        .groupby(["additional_budget", "strategy"])["mean_nmse"]
        .mean()
        .unstack()
        .reindex(columns=curve_strategies)
    )
    ax = budget_table.plot(marker="o", figsize=(11, 6))
    ax.set_ylabel("Mean normalized reconstruction MSE")
    ax.set_title("Pilot 3b — Nested budget performance")
    ax.set_xlabel("Additional measurement budget")
    ax.set_xticks(BUDGETS)
    plt.tight_layout()
    plt.savefig(output_dir / "pilot3b_budget_nmse.png", dpi=160)
    plt.close()

    noise_table = (
        summary[summary["strategy"].isin(curve_strategies)]
        .groupby(["noise_sd", "strategy"])["mean_nmse"]
        .mean()
        .unstack()
        .reindex(columns=curve_strategies)
    )
    ax = noise_table.plot(marker="o", figsize=(11, 6))
    ax.set_ylabel("Mean normalized reconstruction MSE")
    ax.set_title("Pilot 3b — Matched noise-level comparison")
    ax.set_xlabel("Measurement noise standard deviation")
    plt.tight_layout()
    plt.savefig(output_dir / "pilot3b_noise_nmse.png", dpi=160)
    plt.close()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--output-dir", type=Path, default=Path("pilot3b_output"))
    return parser.parse_args()


def main():
    args = parse_args()
    if args.replicates < 2:
        raise ValueError("At least two replicates are required for paired intervals")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    grid = np.linspace(0, 2 * np.pi, GRID_SIZE, endpoint=False)
    rows = []
    for family in FAMILIES:
        for replicate in range(args.replicates):
            f = make_landscape(
                family,
                np.random.default_rng(landscape_seed(family, replicate)),
            )
            truth = np.asarray(f(grid))
            truth_variance = float(np.var(truth))
            if not np.isfinite(truth_variance) or truth_variance <= 0:
                raise RuntimeError("Every landscape must have positive finite variance")
            for initial_n in INITIAL_COUNTS:
                for noise in NOISE_LEVELS:
                    for strategy in STRATEGIES:
                        rows.extend(run_trajectory(
                            family=family,
                            initial_n=initial_n,
                            noise=noise,
                            replicate=replicate,
                            strategy=strategy,
                            f=f,
                            grid=grid,
                            truth=truth,
                            truth_variance=truth_variance,
                        ))
        print(f"Completed landscape family: {family}", flush=True)

    raw = pd.DataFrame(rows)
    expected_rows = (
        len(FAMILIES)
        * len(INITIAL_COUNTS)
        * len(NOISE_LEVELS)
        * len(BUDGETS)
        * len(STRATEGIES)
        * args.replicates
    )
    if len(raw) != expected_rows:
        raise RuntimeError(f"Expected {expected_rows} raw rows, found {len(raw)}")
    if not np.isfinite(raw[["mse", "nmse", "max_abs_error"]].to_numpy()).all():
        raise RuntimeError("Non-finite evaluation result detected")

    summary = condition_summary(raw)
    comparisons = paired_comparisons(raw)
    winners = exact_condition_winners(summary)
    aggregate = (
        summary.groupby("strategy")
        .agg(
            mean_condition_mse=("mean_mse", "mean"),
            mean_condition_nmse=("mean_nmse", "mean"),
            median_condition_nmse=("mean_nmse", "median"),
            conditions=("mean_nmse", "count"),
        )
        .reindex(STRATEGIES)
        .reset_index()
        .sort_values("mean_condition_nmse")
    )

    raw.to_csv(args.output_dir / "pilot3b_raw_results.csv", index=False)
    summary.to_csv(args.output_dir / "pilot3b_condition_summary.csv", index=False)
    comparisons.to_csv(args.output_dir / "pilot3b_paired_comparisons.csv", index=False)
    winners.to_csv(args.output_dir / "pilot3b_condition_winners.csv", index=False)
    aggregate.to_csv(args.output_dir / "pilot3b_aggregate.csv", index=False)
    save_figures(summary, args.output_dir)

    metadata = {
        "experiment": "Generative Geometry Pilot 3b",
        "replicates": args.replicates,
        "families": FAMILIES,
        "initial_counts": INITIAL_COUNTS,
        "budgets_nested": BUDGETS,
        "noise_levels": NOISE_LEVELS,
        "grid_size": GRID_SIZE,
        "strategies": STRATEGIES,
        "focal_strategy": FOCAL_STRATEGY,
        "interval_confidence_method": "Two-sided paired t interval on replicate-level NMSE differences",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "matplotlib": plt.matplotlib.__version__,
    }
    with open(args.output_dir / "pilot3b_metadata.json", "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    print("\nAggregate, equally weighted by condition:")
    print(aggregate.to_string(index=False))
    print("\nExact condition winners by mean NMSE:")
    print(winners["strategy"].value_counts().to_string())
    print(f"\nSaved {len(raw)} raw rows and analysis files to {args.output_dir}")


if __name__ == "__main__":
    main()
