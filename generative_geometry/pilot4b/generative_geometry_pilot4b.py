"""
Generative Geometry — Pilot 4b: constructor discovery in a finite grammar.

A system retains two triple-level relational constructors using development
tasks only (hull perimeter, compactness, and hull vertex count). It is then
evaluated on held-out hull area in an unseen environment family. The previous
area constructor is not supplied directly, but is constructible as abs(cross).

This is usefulness-guided search and composition within an 80-candidate finite
grammar. It is not open-ended discovery, information creation, or recursion.

Usage
-------
    python3 generative_geometry_pilot4b.py --output-dir ./pilot4b_output
    python3 generative_geometry_pilot4b.py --replicates 2 --output-dir ./smoke

See Pilot_4b_Protocol.md for the interpretation rules fixed before the run.
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
TARGETS = ["hull_area", "hull_perimeter", "compactness", "hull_count"]
DEVELOPMENT_TARGETS = ["hull_perimeter", "compactness", "hull_count"]
FINAL_TARGET = "hull_area"
REPRESENTATIONS = [
    "pairwise",
    "discovered",
    "random_constructors",
    "supplied_area",
    "raw_quadratic",
]
RIDGE_ALPHA = 1e-3
N_RETAINED = 2
DEVELOPMENT_FIT = 400
DEVELOPMENT_VALIDATION = 200
PRIMARY_BUDGET = 200
AREA_EXPRESSION = "abs(cross)"

PAIR_INDICES = list(itertools.combinations(range(N_POINTS), 2))
TRIPLE_INDICES = list(itertools.combinations(range(N_POINTS), 3))
RAW_QUADRATIC_INDICES = list(itertools.combinations_with_replacement(range(2 * N_POINTS), 2))
LEAVES = ["dot", "cross", "u2", "v2", "w2"]
UNARY_OPERATIONS = ["identity", "abs", "square", "sqrt_abs"]
BINARY_OPERATIONS = ["multiply", "divide", "add", "abs_diff"]


def build_candidate_catalogue():
    catalogue = []
    for leaf in LEAVES:
        for operation in UNARY_OPERATIONS:
            name = leaf if operation == "identity" else f"{operation}({leaf})"
            catalogue.append({"kind": "unary", "operation": operation, "left": leaf, "right": None, "expression": name})
    for left, right in itertools.combinations_with_replacement(LEAVES, 2):
        for operation in BINARY_OPERATIONS:
            name = f"{operation}({left},{right})"
            catalogue.append({"kind": "binary", "operation": operation, "left": left, "right": right, "expression": name})
    assert len(catalogue) == 80
    assert AREA_EXPRESSION in [item["expression"] for item in catalogue]
    return catalogue


CATALOGUE = build_candidate_catalogue()
CATALOGUE_INDEX = {item["expression"]: i for i, item in enumerate(CATALOGUE)}
AREA_INDEX = CATALOGUE_INDEX[AREA_EXPRESSION]


def radial_points(n, rng, sigma):
    angles = np.sort(rng.uniform(0, 2 * np.pi, n))
    radii = np.exp(rng.normal(0, sigma, n))
    return np.column_stack((radii * np.cos(angles), radii * np.sin(angles)))


def convex_radial_points(n, rng):
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
        inner = [rng.dirichlet(np.ones(4)) @ outer for _ in range(2)]
        return angular_order(np.vstack((outer, inner)))
    if family == "irregular_radial":
        return radial_points(N_POINTS, rng, sigma=0.50)
    if family == "elongated":
        points = radial_points(N_POINTS, rng, sigma=0.50)
        points[:, 1] *= 0.18
        return points
    raise ValueError(family)


def normalize_rotate_and_label(points, rotation):
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
    hull_count = float(len(hull_vertices))

    c, s = np.cos(rotation), np.sin(rotation)
    rotation_matrix = np.array([[c, -s], [s, c]])
    rotated = points @ rotation_matrix.T
    targets = np.array([area, perimeter, compactness, hull_count], dtype=float)
    return rotated, targets


def make_family_dataset(family, replicate):
    n_total = TRAIN_POOL_PER_FAMILY + TEST_PER_FAMILY
    rng = np.random.default_rng(
        50_000_000 + replicate * 1009 + FAMILIES.index(family) * 100_003
    )
    raw = np.zeros((n_total, 2 * N_POINTS))
    targets = np.zeros((n_total, len(TARGETS)))
    for i in range(n_total):
        points = make_configuration(family, rng)
        rotated, target_values = normalize_rotate_and_label(points, rng.uniform(0, 2 * np.pi))
        raw[i] = rotated.ravel()
        targets[i] = target_values
    return raw, targets


def pairwise_features(raw):
    points = raw.reshape(-1, N_POINTS, 2)
    i = np.array([pair[0] for pair in PAIR_INDICES])
    j = np.array([pair[1] for pair in PAIR_INDICES])
    return np.linalg.norm(points[:, i, :] - points[:, j, :], axis=2)


def raw_quadratic_features(raw):
    i = np.array([pair[0] for pair in RAW_QUADRATIC_INDICES])
    j = np.array([pair[1] for pair in RAW_QUADRATIC_INDICES])
    return np.column_stack((raw, raw[:, i] * raw[:, j]))


def local_leaves(raw):
    """Return n x 20 x 5 generic invariant leaves for anchored point triples."""
    points = raw.reshape(-1, N_POINTS, 2)
    triples = np.asarray(TRIPLE_INDICES)
    p_i = points[:, triples[:, 0], :]
    p_j = points[:, triples[:, 1], :]
    p_k = points[:, triples[:, 2], :]
    u = p_j - p_i
    v = p_k - p_i
    w = p_k - p_j
    dot = np.sum(u * v, axis=2)
    cross = u[..., 0] * v[..., 1] - u[..., 1] * v[..., 0]
    u2 = np.sum(u * u, axis=2)
    v2 = np.sum(v * v, axis=2)
    w2 = np.sum(w * w, axis=2)
    return np.stack((dot, cross, u2, v2, w2), axis=2)


def evaluate_candidate(leaves, item):
    left = leaves[..., LEAVES.index(item["left"])]
    if item["kind"] == "unary":
        operation = item["operation"]
        if operation == "identity":
            return left
        if operation == "abs":
            return np.abs(left)
        if operation == "square":
            return left**2
        if operation == "sqrt_abs":
            return np.sqrt(np.abs(left))
        raise ValueError(operation)

    right = leaves[..., LEAVES.index(item["right"])]
    operation = item["operation"]
    if operation == "multiply":
        return left * right
    if operation == "divide":
        return left / (np.abs(right) + 1e-8)
    if operation == "add":
        return left + right
    if operation == "abs_diff":
        return np.abs(left - right)
    raise ValueError(operation)


def evaluate_all_candidates(leaves):
    """Return n x 20 x 80 candidate values without consulting task labels."""
    values = np.stack([evaluate_candidate(leaves, item) for item in CATALOGUE], axis=2)
    values = np.nan_to_num(values, nan=0.0, posinf=1e8, neginf=-1e8)
    return np.clip(values, -1e8, 1e8)


def area_alignment_values(datasets):
    """Squared correlation with abs(cross), equal to in-sample linear-fit R2."""
    area = np.concatenate([
        data["candidates"][..., AREA_INDEX].ravel() for data in datasets.values()
    ])
    area_centered = area - area.mean()
    area_ss = float(np.sum(area_centered**2))
    alignments = np.zeros(len(CATALOGUE))
    for index in range(len(CATALOGUE)):
        candidate = np.concatenate([
            data["candidates"][..., index].ravel() for data in datasets.values()
        ])
        candidate_centered = candidate - candidate.mean()
        denominator = area_ss * float(np.sum(candidate_centered**2))
        if denominator > 0:
            alignments[index] = float(np.sum(area_centered * candidate_centered)**2 / denominator)
    return np.clip(alignments, 0, 1)


def build_datasets(replicate):
    datasets = {}
    for family in FAMILIES:
        raw, targets = make_family_dataset(family, replicate)
        leaves = local_leaves(raw)
        datasets[family] = {
            "raw": raw,
            "targets": targets,
            "pairwise": pairwise_features(raw),
            "raw_quadratic": raw_quadratic_features(raw),
            "candidates": evaluate_all_candidates(leaves),
        }
    alignments = area_alignment_values(datasets)
    return datasets, alignments


def assemble_representation(base, candidates, indices):
    blocks = [base] + [candidates[..., index] for index in indices]
    return np.column_stack(blocks)


def development_score(base, candidates, indices, targets, fit_indices, validation_indices):
    """Multi-task validation score; hull area is absent from targets by construction."""
    x = assemble_representation(base, candidates, indices)
    x_fit = x[fit_indices]
    x_validation = x[validation_indices]
    y_fit = targets[fit_indices]
    y_validation = targets[validation_indices]

    scaler = StandardScaler()
    x_fit = scaler.fit_transform(x_fit)
    x_validation = scaler.transform(x_validation)
    target_mean = y_fit.mean(axis=0)
    target_sd = y_fit.std(axis=0)
    if np.any(target_sd <= 0):
        raise RuntimeError("Development target has zero variance")

    model = Ridge(alpha=RIDGE_ALPHA)
    model.fit(x_fit, (y_fit - target_mean) / target_sd)
    prediction = model.predict(x_validation) * target_sd + target_mean
    scores = r2_score(y_validation, prediction, multioutput="raw_values")
    return float(np.mean(scores)), scores


def discover_constructors(base, candidates, development_targets, selection_rng):
    development_indices = selection_rng.permutation(len(base))[:DEVELOPMENT_FIT + DEVELOPMENT_VALIDATION]
    fit_indices = development_indices[:DEVELOPMENT_FIT]
    validation_indices = development_indices[DEVELOPMENT_FIT:]

    selected = []
    history = []
    current_score, _ = development_score(
        base, candidates, selected, development_targets, fit_indices, validation_indices
    )
    for step in range(N_RETAINED):
        scores = np.full(len(CATALOGUE), -np.inf)
        for index in range(len(CATALOGUE)):
            if index in selected:
                continue
            score, _task_scores = development_score(
                base,
                candidates,
                selected + [index],
                development_targets,
                fit_indices,
                validation_indices,
            )
            scores[index] = score
        best_index = int(np.argmax(scores))
        best_score = float(scores[best_index])
        history.append({
            "step": step + 1,
            "candidate_index": best_index,
            "expression": CATALOGUE[best_index]["expression"],
            "development_validation_r2": best_score,
            "score_improvement": best_score - current_score,
        })
        selected.append(best_index)
        current_score = best_score
    return selected, history


def fit_and_evaluate(x_train, y_train, x_test, y_test):
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)
    target_mean = float(y_train.mean())
    target_sd = float(y_train.std())
    if target_sd <= 0:
        raise RuntimeError("Final training target has zero variance")
    model = Ridge(alpha=RIDGE_ALPHA)
    model.fit(x_train, (y_train - target_mean) / target_sd)
    prediction = model.predict(x_test) * target_sd + target_mean
    mse = float(mean_squared_error(y_test, prediction))
    return {
        "mse": mse,
        "nrmse": float(np.sqrt(mse) / y_test.std()),
        "r2": float(r2_score(y_test, prediction)),
    }


def constructor_category(index, alignment):
    expression = CATALOGUE[index]["expression"]
    if expression == AREA_EXPRESSION:
        return "direct_area_rediscovery"
    if alignment >= 0.999:
        return "linearly_area_aligned"
    return "non_area_linear"


def run_experiment(replicates):
    result_rows = []
    selection_rows = []
    development_indices = [TARGETS.index(task) for task in DEVELOPMENT_TARGETS]
    final_index = TARGETS.index(FINAL_TARGET)

    for replicate in range(replicates):
        datasets, alignments = build_datasets(replicate)
        for fold, test_family in enumerate(FAMILIES):
            train_families = [f for f in FAMILIES if f != test_family]
            base_train = np.vstack([
                datasets[f]["pairwise"][:TRAIN_POOL_PER_FAMILY] for f in train_families
            ])
            candidates_train = np.concatenate([
                datasets[f]["candidates"][:TRAIN_POOL_PER_FAMILY] for f in train_families
            ], axis=0)
            development_targets = np.concatenate([
                datasets[f]["targets"][:TRAIN_POOL_PER_FAMILY, development_indices]
                for f in train_families
            ], axis=0)

            selection_rng = np.random.default_rng(
                60_000_000 + replicate * 2053 + fold * 100_003
            )
            selected, history = discover_constructors(
                base_train, candidates_train, development_targets, selection_rng
            )
            random_rng = np.random.default_rng(
                70_000_000 + replicate * 2063 + fold * 100_003
            )
            random_selected = list(random_rng.choice(
                len(CATALOGUE), size=N_RETAINED, replace=False
            ))

            for step_index, item in enumerate(history):
                index = item["candidate_index"]
                selection_rows.append({
                    "replicate": replicate,
                    "test_family": test_family,
                    **item,
                    "random_expression": CATALOGUE[random_selected[step_index]]["expression"],
                    "area_linear_alignment_r2": alignments[index],
                    "constructor_category": constructor_category(index, alignments[index]),
                })

            base_test = datasets[test_family]["pairwise"][TRAIN_POOL_PER_FAMILY:]
            candidates_test = datasets[test_family]["candidates"][TRAIN_POOL_PER_FAMILY:]
            raw_train = np.vstack([
                datasets[f]["raw_quadratic"][:TRAIN_POOL_PER_FAMILY] for f in train_families
            ])
            representation_data = {
                "pairwise": (base_train, base_test),
                "discovered": (
                    assemble_representation(base_train, candidates_train, selected),
                    assemble_representation(base_test, candidates_test, selected),
                ),
                "random_constructors": (
                    assemble_representation(base_train, candidates_train, random_selected),
                    assemble_representation(base_test, candidates_test, random_selected),
                ),
                "supplied_area": (
                    assemble_representation(base_train, candidates_train, [AREA_INDEX]),
                    assemble_representation(base_test, candidates_test, [AREA_INDEX]),
                ),
                "raw_quadratic": (
                    raw_train,
                    datasets[test_family]["raw_quadratic"][TRAIN_POOL_PER_FAMILY:],
                ),
            }

            y_train_full = np.concatenate([
                datasets[f]["targets"][:TRAIN_POOL_PER_FAMILY, final_index]
                for f in train_families
            ])
            y_test = datasets[test_family]["targets"][TRAIN_POOL_PER_FAMILY:, final_index]
            order_seed = 80_000_000 + replicate * 2069 + fold * 100_003
            order = np.random.default_rng(order_seed).permutation(len(base_train))

            for representation, (x_train_full, x_test) in representation_data.items():
                for budget in BUDGETS:
                    chosen = order[:budget]
                    metrics = fit_and_evaluate(
                        x_train_full[chosen], y_train_full[chosen], x_test, y_test
                    )
                    result_rows.append({
                        "replicate": replicate,
                        "test_family": test_family,
                        "representation": representation,
                        "budget": budget,
                        "n_features": x_train_full.shape[1],
                        "selected_expressions": "|".join(
                            CATALOGUE[i]["expression"] for i in selected
                        ) if representation == "discovered" else "",
                        "train_order_seed": order_seed,
                        **metrics,
                    })
        if (replicate + 1) % 2 == 0 or replicate + 1 == replicates:
            print(f"Completed {replicate + 1}/{replicates} replicates", flush=True)
    return pd.DataFrame(result_rows), pd.DataFrame(selection_rows)


def make_summaries(raw):
    overall = (
        raw.groupby(["budget", "representation"], sort=True)
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
        raw.groupby(["budget", "test_family", "representation"], sort=True)
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
    rows = []
    for budget in BUDGETS:
        subset = raw[raw["budget"] == budget]
        wide = subset.pivot(
            index=["replicate", "test_family"], columns="representation", values="r2"
        )
        for comparator in [r for r in REPRESENTATIONS if r != "discovered"]:
            paired = wide[["discovered", comparator]].dropna()
            fold_difference = paired["discovered"] - paired[comparator]
            replicate_difference = fold_difference.groupby("replicate").mean()
            n = len(replicate_difference)
            mean_difference = float(replicate_difference.mean())
            sd = float(replicate_difference.std(ddof=1))
            margin = float(student_t.ppf(0.975, n - 1)) * sd / np.sqrt(n)
            rows.append({
                "budget": budget,
                "comparator": comparator,
                "replicates": n,
                "discovered_mean_r2": float(paired["discovered"].mean()),
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


def save_figures(overall, by_family, selections, output_dir):
    # Medians are used for visualization because rare pathological extrapolations
    # dominate mean R2. The unmodified means remain in the CSV outputs and report.
    curves = overall[overall["budget"] >= 100].pivot(
        index="budget", columns="representation", values="median_r2"
    ).reindex(columns=REPRESENTATIONS)
    ax = curves.plot(marker="o", figsize=(12, 6))
    ax.set_xscale("log")
    ax.set_xticks(BUDGETS)
    ax.set_xticklabels(BUDGETS)
    ax.set_xlabel("Final-task training configurations (log scale)")
    ax.set_ylabel("Median held-out-family hull-area R²")
    ax.set_title("Pilot 4b — Median sample efficiency after low-budget instability")
    plt.tight_layout()
    plt.savefig(output_dir / "pilot4b_sample_efficiency.png", dpi=160)
    plt.close()

    counts = selections["expression"].value_counts().head(15).sort_values()
    ax = counts.plot(kind="barh", figsize=(11, 7))
    ax.set_xlabel("Retention count across discovery runs")
    ax.set_title("Pilot 4b — Most frequently retained constructors")
    plt.tight_layout()
    plt.savefig(output_dir / "pilot4b_constructor_counts.png", dpi=160)
    plt.close()

    family = by_family[by_family["budget"] == PRIMARY_BUDGET].pivot(
        index="test_family", columns="representation", values="median_r2"
    ).reindex(index=FAMILIES, columns=REPRESENTATIONS)
    ax = family.plot(kind="bar", figsize=(13, 6))
    ax.set_xlabel("Unseen test family")
    ax.set_ylabel("Median hull-area R²")
    ax.set_title(f"Pilot 4b — Robust transfer view at budget {PRIMARY_BUDGET}")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(output_dir / "pilot4b_family_transfer.png", dpi=160)
    plt.close()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--output-dir", type=Path, default=Path("pilot4b_output"))
    return parser.parse_args()


def main():
    args = parse_args()
    if args.replicates < 2:
        raise ValueError("At least two replicates are required for paired intervals")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    raw, selections = run_experiment(args.replicates)
    expected_results = args.replicates * len(FAMILIES) * len(REPRESENTATIONS) * len(BUDGETS)
    expected_selections = args.replicates * len(FAMILIES) * N_RETAINED
    if len(raw) != expected_results or len(selections) != expected_selections:
        raise RuntimeError("Unexpected result or selection row count")
    if not np.isfinite(raw[["mse", "nrmse", "r2"]].to_numpy()).all():
        raise RuntimeError("Non-finite final model result detected")

    overall, by_family = make_summaries(raw)
    comparisons = paired_comparisons(raw)
    selection_summary = (
        selections.groupby(["expression", "constructor_category"], sort=True)
        .agg(
            retention_count=("expression", "size"),
            mean_development_r2=("development_validation_r2", "mean"),
            mean_area_alignment=("area_linear_alignment_r2", "mean"),
        )
        .reset_index()
        .sort_values("retention_count", ascending=False)
    )

    raw.to_csv(args.output_dir / "pilot4b_raw_results.csv", index=False)
    selections.to_csv(args.output_dir / "pilot4b_selection_history.csv", index=False)
    selection_summary.to_csv(args.output_dir / "pilot4b_constructor_summary.csv", index=False)
    pd.DataFrame(CATALOGUE).to_csv(args.output_dir / "pilot4b_candidate_catalogue.csv", index=False)
    overall.to_csv(args.output_dir / "pilot4b_summary_overall.csv", index=False)
    by_family.to_csv(args.output_dir / "pilot4b_summary_by_family.csv", index=False)
    comparisons.to_csv(args.output_dir / "pilot4b_paired_comparisons.csv", index=False)
    save_figures(overall, by_family, selections, args.output_dir)

    metadata = {
        "experiment": "Generative Geometry Pilot 4b",
        "replicates": args.replicates,
        "families": FAMILIES,
        "development_targets": DEVELOPMENT_TARGETS,
        "held_out_final_target": FINAL_TARGET,
        "candidate_count": len(CATALOGUE),
        "retained_constructors": N_RETAINED,
        "development_fit": DEVELOPMENT_FIT,
        "development_validation": DEVELOPMENT_VALIDATION,
        "budgets_nested": BUDGETS,
        "representations": REPRESENTATIONS,
        "ridge_alpha": RIDGE_ALPHA,
        "primary_budget": PRIMARY_BUDGET,
        "interval_method": "Paired t interval over replicate means across four held-out-family folds",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
        "matplotlib": plt.matplotlib.__version__,
    }
    with open(args.output_dir / "pilot4b_metadata.json", "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    primary = comparisons[comparisons["budget"] == PRIMARY_BUDGET]
    print("\nDiscovered-constructor comparisons at budget 200:")
    print(primary.to_string(index=False))
    print("\nConstructor categories across all selections:")
    print(selections["constructor_category"].value_counts().to_string())
    print("\nMost frequent selected constructors:")
    print(selection_summary.head(10).to_string(index=False))
    print(f"\nSaved results to {args.output_dir}")


if __name__ == "__main__":
    main()
