"""
Generative Geometry — Pilot 4: higher-order relational accessibility.

Tests whether generic triangle-area features make held-out geometric properties
accessible to a fixed ridge learner beyond pairwise distances and matched
controls. This is a statistical-accessibility experiment, not evidence for new
information, new physical degrees of freedom, or recursive generation.

Protocol
--------
Six-point configurations from four families; leave-one-family-out evaluation.
Targets: convex-hull area (primary), perimeter (negative control), and
compactness (exploratory). Twenty replicates by default. Nested training
budgets: 25, 50, 100, 200, 500, and 1000.

Representations
---------------
raw                    Centered, RMS-normalized, randomly rotated coordinates.
raw_quadratic          Raw coordinates plus all quadratic monomials.
pairwise               All 15 pairwise distances.
higher_order           Pairwise distances plus all 20 unsigned triangle areas.
random_quadratic       Pairwise distances plus 20 label-independent random
                       quadratic projections of pairwise distances.
shuffled_higher_order  Pairwise distances plus independently permuted area
                       columns, breaking configuration correspondence.

Usage
-------
    python3 generative_geometry_pilot4.py --output-dir ./pilot4_output
    python3 generative_geometry_pilot4.py --replicates 2 --output-dir ./smoke

All random seeds are deterministic. See Pilot_4_Protocol.md for the analysis
rules fixed before the full run.
"""

from __future__ import annotations

import argparse
import itertools
import json
import platform
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.spatial import ConvexHull
from scipy.stats import t as student_t
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

DEFAULT_REPLICATES = 20
N_POINTS = 6
TRAIN_POOL_PER_FAMILY = 1200
TEST_PER_FAMILY = 800
BUDGETS = [25, 50, 100, 200, 500, 1000]
FAMILIES = ["convex_radial", "interior_points", "irregular_radial", "elongated"]
TASKS = ["hull_area", "hull_perimeter", "compactness"]
REPRESENTATIONS = [
    "raw",
    "raw_quadratic",
    "pairwise",
    "higher_order",
    "random_quadratic",
    "shuffled_higher_order",
]
RIDGE_ALPHA = 1e-3
PRIMARY_TASK = "hull_area"
PRIMARY_BUDGET = 200
FOCAL_REPRESENTATION = "higher_order"

PAIR_INDICES = list(itertools.combinations(range(N_POINTS), 2))
TRIPLE_INDICES = list(itertools.combinations(range(N_POINTS), 3))
RAW_QUADRATIC_INDICES = list(itertools.combinations_with_replacement(range(2 * N_POINTS), 2))


def radial_points(n, rng, sigma):
    """Generate points in sorted angular order with variable radii."""
    angles = np.sort(rng.uniform(0, 2 * np.pi, n))
    radii = np.exp(rng.normal(0, sigma, n))
    return np.column_stack((radii * np.cos(angles), radii * np.sin(angles)))


def convex_radial_points(n, rng):
    """Rejection-sample a radial configuration whose points are all hull vertices."""
    for _attempt in range(1000):
        points = radial_points(n, rng, sigma=0.10)
        if len(ConvexHull(points).vertices) == n:
            return points
    raise RuntimeError("Failed to generate a fully convex radial configuration")


def angular_order(points):
    center = points.mean(axis=0)
    angles = np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0])
    return points[np.argsort(angles)]


def make_configuration(family, rng):
    if family == "convex_radial":
        return convex_radial_points(N_POINTS, rng)
    if family == "interior_points":
        outer = convex_radial_points(4, rng)
        inner = []
        for _ in range(2):
            weights = rng.dirichlet(np.ones(4))
            inner.append(weights @ outer)
        return angular_order(np.vstack((outer, inner)))
    if family == "irregular_radial":
        return radial_points(N_POINTS, rng, sigma=0.50)
    if family == "elongated":
        points = radial_points(N_POINTS, rng, sigma=0.50)
        points[:, 1] *= 0.18
        return points
    raise ValueError(family)


def normalize_rotate_and_label(points, rotation):
    """Normalize pose/scale and compute invariant global geometric targets."""
    points = points - points.mean(axis=0)
    scale = np.sqrt(np.mean(np.sum(points**2, axis=1)))
    if not np.isfinite(scale) or scale <= 0:
        raise RuntimeError("Degenerate point configuration")
    points = points / scale

    hull_vertices = ConvexHull(points).vertices
    hull = points[hull_vertices]
    following = np.roll(hull, -1, axis=0)
    twice_area = np.sum(hull[:, 0] * following[:, 1] - hull[:, 1] * following[:, 0])
    area = 0.5 * abs(twice_area)
    perimeter = float(np.sum(np.linalg.norm(following - hull, axis=1)))
    compactness = float(4 * np.pi * area / perimeter**2)

    c, s = np.cos(rotation), np.sin(rotation)
    rotation_matrix = np.array([[c, -s], [s, c]])
    rotated = points @ rotation_matrix.T
    targets = np.array([area, perimeter, compactness], dtype=float)
    return rotated, targets


def make_family_dataset(family, replicate):
    """Generate independent training-pool and test configurations."""
    n_total = TRAIN_POOL_PER_FAMILY + TEST_PER_FAMILY
    rng = np.random.default_rng(
        10_000_000 + replicate * 1009 + FAMILIES.index(family) * 100_003
    )
    raw = np.zeros((n_total, 2 * N_POINTS))
    targets = np.zeros((n_total, len(TASKS)))
    for i in range(n_total):
        points = make_configuration(family, rng)
        rotated, target_values = normalize_rotate_and_label(
            points, rng.uniform(0, 2 * np.pi)
        )
        raw[i] = rotated.ravel()
        targets[i] = target_values
    return raw, targets


def pairwise_features(raw):
    points = raw.reshape(-1, N_POINTS, 2)
    i = np.array([pair[0] for pair in PAIR_INDICES])
    j = np.array([pair[1] for pair in PAIR_INDICES])
    return np.linalg.norm(points[:, i, :] - points[:, j, :], axis=2)


def triangle_area_features(raw):
    points = raw.reshape(-1, N_POINTS, 2)
    triples = np.asarray(TRIPLE_INDICES)
    a = points[:, triples[:, 0], :]
    b = points[:, triples[:, 1], :]
    c = points[:, triples[:, 2], :]
    cross = (b[..., 0] - a[..., 0]) * (c[..., 1] - a[..., 1]) - (
        b[..., 1] - a[..., 1]
    ) * (c[..., 0] - a[..., 0])
    return 0.5 * np.abs(cross)


def raw_quadratic_features(raw):
    i = np.array([pair[0] for pair in RAW_QUADRATIC_INDICES])
    j = np.array([pair[1] for pair in RAW_QUADRATIC_INDICES])
    return np.column_stack((raw, raw[:, i] * raw[:, j]))


def shuffled_areas(areas, rng):
    result = np.empty_like(areas)
    for column in range(areas.shape[1]):
        result[:, column] = areas[rng.permutation(len(areas)), column]
    return result


def build_datasets(replicate):
    """Build all representations from the same underlying observations."""
    feature_rng = np.random.default_rng(20_000_000 + replicate * 2017)
    n_random = len(TRIPLE_INDICES)
    n_pairwise = len(PAIR_INDICES)
    w1 = feature_rng.normal(0, 1 / np.sqrt(n_pairwise), (n_random, n_pairwise))
    w2 = feature_rng.normal(0, 1 / np.sqrt(n_pairwise), (n_random, n_pairwise))

    datasets = {}
    for family in FAMILIES:
        raw, targets = make_family_dataset(family, replicate)
        pairwise = pairwise_features(raw)
        areas = triangle_area_features(raw)
        random_quadratic = (pairwise @ w1.T) * (pairwise @ w2.T)
        shuffle_rng = np.random.default_rng(
            30_000_000 + replicate * 2027 + FAMILIES.index(family) * 100_003
        )
        representations = {
            "raw": raw,
            "raw_quadratic": raw_quadratic_features(raw),
            "pairwise": pairwise,
            "higher_order": np.column_stack((pairwise, areas)),
            "random_quadratic": np.column_stack((pairwise, random_quadratic)),
            "shuffled_higher_order": np.column_stack((
                pairwise,
                shuffled_areas(areas, shuffle_rng),
            )),
        }
        datasets[family] = {"targets": targets, "representations": representations}
    return datasets


def fit_and_evaluate(x_train, y_train, x_test, y_test):
    """Fixed ridge procedure; all standardization is fitted on training data."""
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)

    target_mean = float(y_train.mean())
    target_sd = float(y_train.std())
    if target_sd <= 0:
        raise RuntimeError("Training target has zero variance")
    model = Ridge(alpha=RIDGE_ALPHA)
    model.fit(x_train, (y_train - target_mean) / target_sd)
    prediction = model.predict(x_test) * target_sd + target_mean

    mse = float(mean_squared_error(y_test, prediction))
    test_sd = float(y_test.std())
    return {
        "mse": mse,
        "nrmse": float(np.sqrt(mse) / test_sd),
        "r2": float(r2_score(y_test, prediction)),
    }


def run_experiment(replicates):
    rows = []
    for replicate in range(replicates):
        datasets = build_datasets(replicate)
        for fold, test_family in enumerate(FAMILIES):
            train_families = [f for f in FAMILIES if f != test_family]
            order_seed = 40_000_000 + replicate * 2039 + fold * 100_003
            order_rng = np.random.default_rng(order_seed)

            for representation in REPRESENTATIONS:
                x_train_full = np.vstack([
                    datasets[f]["representations"][representation][:TRAIN_POOL_PER_FAMILY]
                    for f in train_families
                ])
                order = order_rng.permutation(len(x_train_full))
                x_test = datasets[test_family]["representations"][representation][
                    TRAIN_POOL_PER_FAMILY:
                ]

                for budget in BUDGETS:
                    selected = order[:budget]
                    x_train = x_train_full[selected]
                    for task_index, task in enumerate(TASKS):
                        y_train_full = np.concatenate([
                            datasets[f]["targets"][:TRAIN_POOL_PER_FAMILY, task_index]
                            for f in train_families
                        ])
                        y_train = y_train_full[selected]
                        y_test = datasets[test_family]["targets"][
                            TRAIN_POOL_PER_FAMILY:, task_index
                        ]
                        metrics = fit_and_evaluate(x_train, y_train, x_test, y_test)
                        rows.append({
                            "replicate": replicate,
                            "test_family": test_family,
                            "train_families": "|".join(train_families),
                            "task": task,
                            "representation": representation,
                            "budget": budget,
                            "n_features": x_train.shape[1],
                            "train_order_seed": order_seed,
                            **metrics,
                        })
        if (replicate + 1) % 5 == 0 or replicate + 1 == replicates:
            print(f"Completed {replicate + 1}/{replicates} replicates", flush=True)
    return pd.DataFrame(rows)


def make_summaries(raw):
    overall = (
        raw.groupby(["task", "budget", "representation"], sort=True)
        .agg(
            mean_r2=("r2", "mean"),
            sd_r2=("r2", "std"),
            median_r2=("r2", "median"),
            mean_nrmse=("nrmse", "mean"),
            observations=("r2", "size"),
        )
        .reset_index()
    )
    by_family = (
        raw.groupby(["task", "budget", "test_family", "representation"], sort=True)
        .agg(
            mean_r2=("r2", "mean"),
            sd_r2=("r2", "std"),
            median_r2=("r2", "median"),
            mean_nrmse=("nrmse", "mean"),
            replicates=("r2", "size"),
        )
        .reset_index()
    )
    return overall, by_family


def paired_comparisons(raw):
    """Compare mean held-out-family R2 within replicate; positive favors higher-order."""
    rows = []
    comparators = [r for r in REPRESENTATIONS if r != FOCAL_REPRESENTATION]
    for task in TASKS:
        for budget in BUDGETS:
            subset = raw[(raw["task"] == task) & (raw["budget"] == budget)]
            wide = subset.pivot(
                index=["replicate", "test_family"],
                columns="representation",
                values="r2",
            )
            for comparator in comparators:
                paired = wide[[FOCAL_REPRESENTATION, comparator]].dropna()
                fold_difference = paired[FOCAL_REPRESENTATION] - paired[comparator]
                replicate_difference = fold_difference.groupby("replicate").mean()
                n = len(replicate_difference)
                mean_difference = float(replicate_difference.mean())
                sd = float(replicate_difference.std(ddof=1))
                se = sd / np.sqrt(n)
                margin = float(student_t.ppf(0.975, n - 1)) * se
                rows.append({
                    "task": task,
                    "budget": budget,
                    "comparator": comparator,
                    "replicates": n,
                    "higher_order_mean_r2": float(paired[FOCAL_REPRESENTATION].mean()),
                    "comparator_mean_r2": float(paired[comparator].mean()),
                    "mean_r2_difference": mean_difference,
                    "ci95_low": mean_difference - margin,
                    "ci95_high": mean_difference + margin,
                    "ci_excludes_zero": bool(
                        (mean_difference - margin) * (mean_difference + margin) > 0
                    ),
                    "replicate_win_fraction": float(np.mean(replicate_difference > 0)),
                })
    return pd.DataFrame(rows)


def save_figures(overall, by_family, output_dir):
    area = overall[overall["task"] == "hull_area"].pivot(
        index="budget", columns="representation", values="mean_r2"
    ).reindex(columns=REPRESENTATIONS)
    ax = area.plot(marker="o", figsize=(12, 6))
    ax.set_xscale("log")
    ax.set_xticks(BUDGETS)
    ax.set_xticklabels(BUDGETS)
    ax.set_xlabel("Training configurations (log scale)")
    ax.set_ylabel("Mean held-out-family R²")
    ax.set_title("Pilot 4 — Hull-area sample efficiency")
    plt.tight_layout()
    plt.savefig(output_dir / "pilot4_hull_area_sample_efficiency.png", dpi=160)
    plt.close()

    at_primary = overall[overall["budget"] == PRIMARY_BUDGET].pivot(
        index="task", columns="representation", values="mean_r2"
    ).reindex(index=TASKS, columns=REPRESENTATIONS)
    ax = at_primary.plot(kind="bar", figsize=(14, 6))
    ax.set_xlabel("Downstream task")
    ax.set_ylabel("Mean held-out-family R²")
    ax.set_title(f"Pilot 4 — Task performance at budget {PRIMARY_BUDGET}")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_dir / "pilot4_task_performance.png", dpi=160)
    plt.close()

    family_area = by_family[
        (by_family["task"] == "hull_area")
        & (by_family["budget"] == PRIMARY_BUDGET)
    ].pivot(
        index="test_family", columns="representation", values="mean_r2"
    ).reindex(index=FAMILIES, columns=REPRESENTATIONS)
    ax = family_area.plot(kind="bar", figsize=(14, 6))
    ax.set_xlabel("Unseen test family")
    ax.set_ylabel("Mean R² across replicates")
    ax.set_title(f"Pilot 4 — Hull-area transfer at budget {PRIMARY_BUDGET}")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(output_dir / "pilot4_hull_area_by_family.png", dpi=160)
    plt.close()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--output-dir", type=Path, default=Path("pilot4_output"))
    return parser.parse_args()


def main():
    args = parse_args()
    if args.replicates < 2:
        raise ValueError("At least two replicates are required for paired intervals")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    raw = run_experiment(args.replicates)
    expected_rows = args.replicates * len(FAMILIES) * len(TASKS) * len(REPRESENTATIONS) * len(BUDGETS)
    if len(raw) != expected_rows:
        raise RuntimeError(f"Expected {expected_rows} result rows, found {len(raw)}")
    if not np.isfinite(raw[["mse", "nrmse", "r2"]].to_numpy()).all():
        raise RuntimeError("Non-finite model result detected")

    overall, by_family = make_summaries(raw)
    comparisons = paired_comparisons(raw)

    raw.to_csv(args.output_dir / "pilot4_raw_results.csv", index=False)
    overall.to_csv(args.output_dir / "pilot4_summary_overall.csv", index=False)
    by_family.to_csv(args.output_dir / "pilot4_summary_by_family.csv", index=False)
    comparisons.to_csv(args.output_dir / "pilot4_paired_comparisons.csv", index=False)
    save_figures(overall, by_family, args.output_dir)

    dimensions = {
        "raw": 2 * N_POINTS,
        "raw_quadratic": 2 * N_POINTS + len(RAW_QUADRATIC_INDICES),
        "pairwise": len(PAIR_INDICES),
        "higher_order": len(PAIR_INDICES) + len(TRIPLE_INDICES),
        "random_quadratic": len(PAIR_INDICES) + len(TRIPLE_INDICES),
        "shuffled_higher_order": len(PAIR_INDICES) + len(TRIPLE_INDICES),
    }
    metadata = {
        "experiment": "Generative Geometry Pilot 4",
        "replicates": args.replicates,
        "families": FAMILIES,
        "tasks": TASKS,
        "budgets_nested": BUDGETS,
        "representations": REPRESENTATIONS,
        "representation_dimensions": dimensions,
        "train_pool_per_family": TRAIN_POOL_PER_FAMILY,
        "test_per_family": TEST_PER_FAMILY,
        "ridge_alpha": RIDGE_ALPHA,
        "primary_task": PRIMARY_TASK,
        "primary_budget": PRIMARY_BUDGET,
        "primary_comparison": "higher_order minus pairwise held-out-family R2",
        "interval_method": "Paired t interval over 20 replicate means, each averaging four held-out-family folds",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
        "matplotlib": plt.matplotlib.__version__,
    }
    with open(args.output_dir / "pilot4_metadata.json", "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    primary = comparisons[
        (comparisons["task"] == PRIMARY_TASK)
        & (comparisons["budget"] == PRIMARY_BUDGET)
    ]
    print("\nPrimary-task paired comparisons at budget 200:")
    print(primary.to_string(index=False))
    print(f"\nSaved {len(raw)} model-evaluation rows to {args.output_dir}")


if __name__ == "__main__":
    main()
