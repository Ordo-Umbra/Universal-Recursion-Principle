"""
Generative Geometry — Pilot 4f: frozen-constructor invariant integration.

No constructor search is performed. Supplied area and frozen Pilot 4e outputs
are evaluated with label-indexed, sorted, and full local-orbit feature blocks.

Usage
-----
    python3 generative_geometry_pilot4f.py --replicates 20 --output-dir ./pilot4f_output
    python3 generative_geometry_pilot4f.py --replicates 2 --output-dir ./smoke

See Pilot_4f_Protocol.md for the rules fixed before implementation and testing.
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
from scipy.stats import binomtest, t as student_t
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
FINAL_TARGET = "hull_area"
RIDGE_ALPHA = 1e-3
PRIMARY_BUDGET = 200
INVARIANCE_TOLERANCE = 1e-12
SEARCH_CONDITIONS = [
    "greedy", "neutral_drift", "diversity_archive", "sampled_lookahead",
    "independent_search", "unscaffolded",
]
CONSTRUCTOR_SOURCES = ["supplied_area", "initial"] + SEARCH_CONDITIONS
SUPPLIED_AGGREGATIONS = [
    "current", "pairwise_sorted", "constructor_sorted", "fully_sorted",
    "constructor_orbit_sorted", "fully_orbit_sorted",
]
FROZEN_AGGREGATIONS = [
    "current", "pairwise_sorted", "constructor_orbit_sorted", "fully_orbit_sorted",
]
LEAVES = ["dot", "cross", "u2", "v2", "w2"]
UNARY_OPERATIONS = ["abs", "square", "sqrt_abs"]
BINARY_OPERATIONS = ["multiply", "divide", "add", "abs_diff"]
PAIR_INDICES = list(itertools.combinations(range(N_POINTS), 2))
TRIPLE_INDICES = list(itertools.combinations(range(N_POINTS), 3))
ORBIT_INDICES = [
    ordering
    for triple in TRIPLE_INDICES
    for ordering in itertools.permutations(triple, 3)
]
INITIAL_TREE = ("leaf", "dot")
AREA_TREE = ("unary", "abs", ("leaf", "cross"))


def expression_name(tree):
    kind = tree[0]
    if kind == "leaf":
        return tree[1]
    if kind == "unary":
        return f"{tree[1]}({expression_name(tree[2])})"
    if kind == "binary":
        return f"{tree[1]}({expression_name(tree[2])},{expression_name(tree[3])})"
    raise ValueError(kind)


def expression_depth(tree):
    if tree[0] == "leaf":
        return 0
    if tree[0] == "unary":
        return 1 + expression_depth(tree[2])
    if tree[0] == "binary":
        return 1 + max(expression_depth(tree[2]), expression_depth(tree[3]))
    raise ValueError(tree[0])


def parse_expression(text):
    """Parse the frozen grammar without using eval."""
    position = 0

    def parse():
        nonlocal position
        start = position
        while position < len(text) and text[position] not in "(),":
            position += 1
        name = text[start:position]
        if not name:
            raise ValueError(f"Missing expression name in {text!r}")
        if position >= len(text) or text[position] != "(":
            if name not in LEAVES:
                raise ValueError(f"Unknown leaf {name!r}")
            return ("leaf", name)
        position += 1
        arguments = [parse()]
        while position < len(text) and text[position] == ",":
            position += 1
            arguments.append(parse())
        if position >= len(text) or text[position] != ")":
            raise ValueError(f"Unclosed operation in {text!r}")
        position += 1
        if name in UNARY_OPERATIONS and len(arguments) == 1:
            return ("unary", name, arguments[0])
        if name in BINARY_OPERATIONS and len(arguments) == 2:
            return ("binary", name, arguments[0], arguments[1])
        raise ValueError(f"Invalid operation {name!r} with {len(arguments)} arguments")

    tree = parse()
    if position != len(text):
        raise ValueError(f"Trailing expression content in {text!r}")
    if expression_name(tree) != text:
        raise ValueError(f"Expression round-trip failed for {text!r}")
    return tree


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
    return rotated, np.array([area, perimeter, compactness, hull_count], dtype=float)


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


def indexed_leaves(raw, indices):
    points = raw.reshape(-1, N_POINTS, 2)
    triples = np.asarray(indices)
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


def local_leaves(raw):
    return indexed_leaves(raw, TRIPLE_INDICES)


def orbit_leaves(raw):
    return indexed_leaves(raw, ORBIT_INDICES)


def evaluate_expression(leaves, tree):
    kind = tree[0]
    if kind == "leaf":
        return leaves[..., LEAVES.index(tree[1])].copy()
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        if kind == "unary":
            child = evaluate_expression(leaves, tree[2])
            operation = tree[1]
            if operation == "abs":
                return np.abs(child)
            if operation == "square":
                return child**2
            if operation == "sqrt_abs":
                return np.sqrt(np.abs(child))
            raise ValueError(operation)
        left = evaluate_expression(leaves, tree[2])
        right = evaluate_expression(leaves, tree[3])
        operation = tree[1]
        if operation == "multiply":
            return left * right
        if operation == "divide":
            return left / (np.abs(right) + 1e-8)
        if operation == "add":
            return left + right
        if operation == "abs_diff":
            return np.abs(left - right)
        raise ValueError(operation)


def dataset_dictionary(raw, targets):
    return {
        "raw": raw,
        "targets": targets,
        "pairwise": pairwise_features(raw),
        "leaves": local_leaves(raw),
        "orbit_leaves": orbit_leaves(raw),
    }


def build_ordered_datasets(replicate):
    datasets = {}
    for family in FAMILIES:
        raw, targets = make_family_dataset(family, replicate)
        datasets[family] = dataset_dictionary(raw, targets)
    return datasets


def permute_raw(raw, seed):
    points = raw.reshape(-1, N_POINTS, 2)
    rng = np.random.default_rng(seed)
    permutations = np.argsort(rng.random((len(raw), N_POINTS)), axis=1)
    permuted = np.take_along_axis(points, permutations[..., None], axis=1)
    return permuted.reshape(-1, 2 * N_POINTS)


def build_permuted_datasets(ordered_datasets, replicate):
    datasets = {}
    for family_index, family in enumerate(FAMILIES):
        source = ordered_datasets[family]
        seed = 93_000_000 + replicate * 3023 + family_index * 100_003
        raw = permute_raw(source["raw"], seed)
        datasets[family] = dataset_dictionary(raw, source["targets"])
        datasets[family]["permutation_seed"] = seed
    return datasets


def validate_invariance():
    """Check exact invariance under a fresh point relabeling before model fitting."""
    rows = []
    trees = {
        "supplied_area": AREA_TREE,
        "dot": INITIAL_TREE,
        "cross": ("leaf", "cross"),
        "asymmetric": parse_expression("abs_diff(u2,v2)"),
    }
    for family_index, family in enumerate(FAMILIES):
        raw, targets = make_family_dataset(family, 0)
        second_raw = permute_raw(raw, 97_000_000 + family_index * 100_003)

        def record(check, expression, first, second, required):
            difference = float(np.max(np.abs(first - second)))
            rows.append({
                "family": family,
                "check": check,
                "expression": expression,
                "required_invariant": required,
                "max_absolute_difference": difference,
                "tolerance": INVARIANCE_TOLERANCE,
                "passes": bool(difference <= INVARIANCE_TOLERANCE),
                "values_compared": int(first.size),
            })

        record(
            "sorted_pairwise", "", np.sort(pairwise_features(raw), axis=1),
            np.sort(pairwise_features(second_raw), axis=1), True,
        )
        first_leaves = local_leaves(raw)
        second_leaves = local_leaves(second_raw)
        first_orbit = orbit_leaves(raw)
        second_orbit = orbit_leaves(second_raw)
        for name, tree in trees.items():
            first_values = evaluate_expression(first_leaves, tree)
            second_values = evaluate_expression(second_leaves, tree)
            record(
                "simple_sorted_constructor", expression_name(tree),
                np.sort(first_values, axis=1), np.sort(second_values, axis=1),
                name == "supplied_area",
            )
            record(
                "orbit_sorted_constructor", expression_name(tree),
                np.sort(evaluate_expression(first_orbit, tree), axis=1),
                np.sort(evaluate_expression(second_orbit, tree), axis=1),
                True,
            )
        record("targets", "all", targets, targets, True)
    checks = pd.DataFrame(rows)
    failed = checks[checks.required_invariant & ~checks.passes]
    if not failed.empty:
        raise RuntimeError(f"Required invariance checks failed:\n{failed}")
    return checks


def load_constructor_manifest(search_path, replicates):
    search = pd.read_csv(search_path)
    rows = []
    for replicate in range(replicates):
        for test_family in FAMILIES:
            for source in CONSTRUCTOR_SOURCES:
                if source == "supplied_area":
                    expression = expression_name(AREA_TREE)
                elif source == "initial":
                    expression = expression_name(INITIAL_TREE)
                else:
                    selected = search[
                        (search.replicate == replicate)
                        & (search.test_family == test_family)
                        & (search.condition == source)
                    ]
                    if len(selected) != 1:
                        raise RuntimeError(
                            f"Expected one frozen row for {source}, replicate {replicate}, {test_family}"
                        )
                    expression = selected.iloc[0].output_expression
                tree = parse_expression(expression)
                rows.append({
                    "replicate": replicate,
                    "test_family": test_family,
                    "constructor_source": source,
                    "expression": expression,
                    "expression_depth": expression_depth(tree),
                })
    manifest = pd.DataFrame(rows)
    if len(manifest) != replicates * len(FAMILIES) * len(CONSTRUCTOR_SOURCES):
        raise RuntimeError("Unexpected constructor manifest size")
    return manifest


def constructor_block(dataset, tree, mode, train):
    values = dataset["orbit_leaves"] if mode == "orbit120" else dataset["leaves"]
    values = values[:TRAIN_POOL_PER_FAMILY] if train else values[TRAIN_POOL_PER_FAMILY:]
    result = evaluate_expression(values, tree)
    if mode in {"sorted20", "orbit120"}:
        result = np.sort(result, axis=1)
    return result


def representation_for_fold(datasets, train_families, test_family, tree, aggregation):
    pairwise_mode = "sorted15" if aggregation in {"pairwise_sorted", "fully_sorted", "fully_orbit_sorted"} else "label15"
    if aggregation in {"constructor_sorted", "fully_sorted"}:
        constructor_mode = "sorted20"
    elif aggregation in {"constructor_orbit_sorted", "fully_orbit_sorted"}:
        constructor_mode = "orbit120"
    else:
        constructor_mode = "label20"
    base_train = np.vstack([
        datasets[f]["pairwise"][:TRAIN_POOL_PER_FAMILY] for f in train_families
    ])
    base_test = datasets[test_family]["pairwise"][TRAIN_POOL_PER_FAMILY:]
    if pairwise_mode == "sorted15":
        base_train = np.sort(base_train, axis=1)
        base_test = np.sort(base_test, axis=1)
    train_constructor = np.concatenate([
        constructor_block(datasets[f], tree, constructor_mode, train=True)
        for f in train_families
    ], axis=0)
    test_constructor = constructor_block(
        datasets[test_family], tree, constructor_mode, train=False
    )
    return (
        np.column_stack((base_train, train_constructor)),
        np.column_stack((base_test, test_constructor)),
        pairwise_mode,
        constructor_mode,
    )


def fit_and_evaluate(x_train, y_train, x_test, y_test):
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
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
        nrmse = float(np.sqrt(mse) / y_test.std())
        r2 = float(r2_score(y_test, prediction))
    if not np.isfinite([mse, nrmse, r2]).all():
        raise RuntimeError("Non-finite final model result detected")
    return {
        "mse": mse,
        "nrmse": nrmse,
        "r2": r2,
        "log1p_nrmse": float(np.log1p(nrmse)),
    }


def run_experiment(replicates, search_path):
    invariance_checks = validate_invariance()
    manifest = load_constructor_manifest(search_path, replicates)
    result_rows = []
    final_index = TARGETS.index(FINAL_TARGET)
    for replicate in range(replicates):
        ordered = build_ordered_datasets(replicate)
        datasets = build_permuted_datasets(ordered, replicate)
        for fold, test_family in enumerate(FAMILIES):
            train_families = [f for f in FAMILIES if f != test_family]
            order_seed = 80_000_000 + replicate * 2069 + fold * 100_003
            for source in CONSTRUCTOR_SOURCES:
                selected = manifest[
                    (manifest.replicate == replicate)
                    & (manifest.test_family == test_family)
                    & (manifest.constructor_source == source)
                ]
                expression = selected.iloc[0].expression
                tree = parse_expression(expression)
                aggregations = SUPPLIED_AGGREGATIONS if source == "supplied_area" else FROZEN_AGGREGATIONS
                y_train_full = np.concatenate([
                    datasets[f]["targets"][:TRAIN_POOL_PER_FAMILY, final_index]
                    for f in train_families
                ])
                y_test = datasets[test_family]["targets"][TRAIN_POOL_PER_FAMILY:, final_index]
                order = np.random.default_rng(order_seed).permutation(len(y_train_full))
                for aggregation in aggregations:
                    x_train_full, x_test, pairwise_mode, constructor_mode = representation_for_fold(
                        datasets, train_families, test_family, tree, aggregation
                    )
                    for budget in BUDGETS:
                        chosen = order[:budget]
                        metrics = fit_and_evaluate(
                            x_train_full[chosen], y_train_full[chosen], x_test, y_test
                        )
                        result_rows.append({
                            "environment": "permuted",
                            "replicate": replicate,
                            "test_family": test_family,
                            "constructor_source": source,
                            "expression": expression,
                            "aggregation": aggregation,
                            "pairwise_mode": pairwise_mode,
                            "constructor_mode": constructor_mode,
                            "budget": budget,
                            "n_features": x_train_full.shape[1],
                            "train_order_seed": order_seed,
                            **metrics,
                        })
            tree = AREA_TREE
            x_train_full, x_test, pairwise_mode, constructor_mode = representation_for_fold(
                ordered, train_families, test_family, tree, "current"
            )
            y_train_full = np.concatenate([
                ordered[f]["targets"][:TRAIN_POOL_PER_FAMILY, final_index]
                for f in train_families
            ])
            y_test = ordered[test_family]["targets"][TRAIN_POOL_PER_FAMILY:, final_index]
            order = np.random.default_rng(order_seed).permutation(len(y_train_full))
            for budget in BUDGETS:
                chosen = order[:budget]
                metrics = fit_and_evaluate(
                    x_train_full[chosen], y_train_full[chosen], x_test, y_test
                )
                result_rows.append({
                    "environment": "ordered",
                    "replicate": replicate,
                    "test_family": test_family,
                    "constructor_source": "supplied_area",
                    "expression": expression_name(AREA_TREE),
                    "aggregation": "current",
                    "pairwise_mode": pairwise_mode,
                    "constructor_mode": constructor_mode,
                    "budget": budget,
                    "n_features": x_train_full.shape[1],
                    "train_order_seed": order_seed,
                    **metrics,
                })
        print(f"Completed {replicate + 1}/{replicates} replicates", flush=True)
    return pd.DataFrame(result_rows), manifest, invariance_checks


def make_summaries(raw):
    overall = (
        raw.groupby(["environment", "budget", "constructor_source", "aggregation"], sort=True)
        .agg(
            mean_r2=("r2", "mean"), sd_r2=("r2", "std"),
            median_r2=("r2", "median"), q10_r2=("r2", lambda x: x.quantile(0.10)),
            median_nrmse=("nrmse", "median"), mean_log1p_nrmse=("log1p_nrmse", "mean"),
            sd_log1p_nrmse=("log1p_nrmse", "std"), observations=("r2", "size"),
        ).reset_index()
    )
    by_family = (
        raw.groupby([
            "environment", "budget", "test_family", "constructor_source", "aggregation"
        ], sort=True)
        .agg(
            mean_r2=("r2", "mean"), sd_r2=("r2", "std"), median_r2=("r2", "median"),
            median_nrmse=("nrmse", "median"), mean_log1p_nrmse=("log1p_nrmse", "mean"),
            replicates=("r2", "size"),
        ).reset_index()
    )
    return overall, by_family


def interval_statistics(differences):
    differences = np.asarray(differences, dtype=float)
    n = len(differences)
    mean = float(differences.mean())
    sd = float(differences.std(ddof=1))
    half_width = float(student_t.ppf(0.975, n - 1) * sd / np.sqrt(n))
    nonzero = differences[differences != 0]
    positives = int(np.sum(nonzero > 0))
    p_value = float(binomtest(positives, len(nonzero), 0.5).pvalue) if len(nonzero) else 1.0
    return {
        "replicates": n,
        "mean_log_error_difference": mean,
        "ci95_low": mean - half_width,
        "ci95_high": mean + half_width,
        "ci_excludes_zero": bool(mean - half_width > 0 or mean + half_width < 0),
        "positive_favors_focus": True,
        "replicate_win_fraction": float(np.mean(differences > 0)),
        "exact_sign_p": p_value,
    }


def one_comparison(raw, source, focus, comparator, budget, primary=False):
    subset = raw[
        (raw.environment == "permuted")
        & (raw.constructor_source == source)
        & (raw.budget == budget)
        & (raw.aggregation.isin([focus, comparator]))
    ]
    wide = subset.pivot(
        index=["replicate", "test_family"], columns="aggregation", values="log1p_nrmse"
    )
    differences = (wide[comparator] - wide[focus]).groupby("replicate").mean()
    result = {
        "budget": budget,
        "constructor_source": source,
        "focus_aggregation": focus,
        "comparator_aggregation": comparator,
        "primary_comparison": primary,
        "focus_mean_log1p_nrmse": float(subset[subset.aggregation == focus].log1p_nrmse.mean()),
        "comparator_mean_log1p_nrmse": float(subset[subset.aggregation == comparator].log1p_nrmse.mean()),
        "focus_mean_r2": float(subset[subset.aggregation == focus].r2.mean()),
        "comparator_mean_r2": float(subset[subset.aggregation == comparator].r2.mean()),
        "focus_median_r2": float(subset[subset.aggregation == focus].r2.median()),
        "comparator_median_r2": float(subset[subset.aggregation == comparator].r2.median()),
    }
    result.update(interval_statistics(differences.to_numpy()))
    return result


def mechanism_comparisons(raw):
    rows = []
    for budget in BUDGETS:
        supplied = [
            ("fully_sorted", "current", budget == PRIMARY_BUDGET),
            ("pairwise_sorted", "current", False),
            ("constructor_sorted", "current", False),
            ("constructor_orbit_sorted", "current", False),
            ("fully_orbit_sorted", "current", False),
            ("fully_orbit_sorted", "fully_sorted", False),
        ]
        for focus, comparator, primary in supplied:
            rows.append(one_comparison(raw, "supplied_area", focus, comparator, budget, primary))
        for source in CONSTRUCTOR_SOURCES[1:]:
            for focus in ["pairwise_sorted", "constructor_orbit_sorted", "fully_orbit_sorted"]:
                rows.append(one_comparison(raw, source, focus, "current", budget))
    return pd.DataFrame(rows)


def one_interaction(raw, source, interaction_type, budget):
    if interaction_type == "simple_sorted":
        pair, full, constructor = "pairwise_sorted", "fully_sorted", "constructor_sorted"
    else:
        pair, full, constructor = "pairwise_sorted", "fully_orbit_sorted", "constructor_orbit_sorted"
    subset = raw[
        (raw.environment == "permuted")
        & (raw.constructor_source == source)
        & (raw.budget == budget)
        & (raw.aggregation.isin(["current", pair, full, constructor]))
    ]
    wide = subset.pivot(
        index=["replicate", "test_family"], columns="aggregation", values="log1p_nrmse"
    )
    interaction = (
        (wide[pair] - wide[full]) - (wide["current"] - wide[constructor])
    ).groupby("replicate").mean()
    result = {
        "budget": budget,
        "constructor_source": source,
        "interaction_type": interaction_type,
        "positive_means_constructor_aggregation_more_beneficial_with_sorted_pairwise": True,
    }
    result.update(interval_statistics(interaction.to_numpy()))
    return result


def aggregation_interactions(raw):
    rows = []
    for budget in BUDGETS:
        rows.append(one_interaction(raw, "supplied_area", "simple_sorted", budget))
        for source in CONSTRUCTOR_SOURCES:
            rows.append(one_interaction(raw, source, "orbit_sorted", budget))
    return pd.DataFrame(rows)


def validate_outputs(raw, manifest, invariance, replicates):
    expected_permuted = replicates * len(FAMILIES) * len(BUDGETS) * (
        len(SUPPLIED_AGGREGATIONS) + (len(CONSTRUCTOR_SOURCES) - 1) * len(FROZEN_AGGREGATIONS)
    )
    expected_ordered = replicates * len(FAMILIES) * len(BUDGETS)
    if len(raw[raw.environment == "permuted"]) != expected_permuted:
        raise RuntimeError("Unexpected permuted result count")
    if len(raw[raw.environment == "ordered"]) != expected_ordered:
        raise RuntimeError("Unexpected ordered result count")
    if len(manifest) != replicates * len(FAMILIES) * len(CONSTRUCTOR_SOURCES):
        raise RuntimeError("Unexpected manifest count")
    if not np.isfinite(raw[["mse", "nrmse", "r2", "log1p_nrmse"]].to_numpy()).all():
        raise RuntimeError("Non-finite final result")
    keys = ["environment", "replicate", "test_family", "constructor_source", "aggregation", "budget"]
    if raw.duplicated(keys).any():
        raise RuntimeError("Duplicate final result key")
    failed = invariance[invariance.required_invariant & ~invariance.passes]
    if not failed.empty:
        raise RuntimeError("Required invariance validation failed")


def validate_previous_reproduction(raw, pilot4e_dir, pilot4d_dir):
    metrics = ["mse", "nrmse", "r2", "log1p_nrmse"]

    def discrepancies(frame, first_suffix, second_suffix):
        absolute = {}
        scaled = {}
        for metric in metrics:
            first = frame[f"{metric}_{first_suffix}"].to_numpy()
            second = frame[f"{metric}_{second_suffix}"].to_numpy()
            difference = np.abs(first - second)
            absolute[metric] = float(difference.max())
            scaled[metric] = float((difference / np.maximum(1.0, np.abs(second))).max())
        return absolute, scaled

    current = raw[(raw.environment == "permuted") & (raw.aggregation == "current")].copy()
    previous4e = pd.read_csv(pilot4e_dir / "pilot4e_raw_results.csv")
    previous4e = previous4e.rename(columns={"representation": "constructor_source"})
    merged = current.merge(
        previous4e, on=["replicate", "test_family", "constructor_source", "budget"],
        suffixes=("_4f", "_4e"), validate="one_to_one",
    )
    if len(merged) != len(current):
        raise RuntimeError("Incomplete Pilot 4e reproduction join")
    for source, group in merged.groupby("constructor_source"):
        if not (group.expression_4f == group.expression_4e).all():
            raise RuntimeError(f"Frozen expression mismatch for {source}")
    absolute4e, scaled4e = discrepancies(merged, "4f", "4e")
    if max(scaled4e.values()) > 1e-10:
        raise RuntimeError(f"Pilot 4e reproduction failed: {scaled4e}")

    ordered = raw[(raw.environment == "ordered") & (raw.aggregation == "current")].copy()
    previous4d = pd.read_csv(pilot4d_dir / "pilot4d_raw_results.csv")
    previous4d = previous4d[
        (previous4d.arm == "ordered") & (previous4d.representation == "supplied_area")
    ]
    merged_ordered = ordered.merge(
        previous4d, on=["replicate", "test_family", "budget"],
        suffixes=("_4f", "_4d"), validate="one_to_one",
    )
    if len(merged_ordered) != len(ordered):
        raise RuntimeError("Incomplete Pilot 4d reproduction join")
    absolute4d, scaled4d = discrepancies(merged_ordered, "4f", "4d")
    if max(scaled4d.values()) > 1e-10:
        raise RuntimeError(f"Pilot 4d ordered reproduction failed: {scaled4d}")
    return {
        "comparison_rule": "absolute difference / max(1, absolute previous value) <= 1e-10",
        "pilot4e_current_rows_checked": int(len(merged)),
        "pilot4e_max_absolute_metric_difference": max(absolute4e.values()),
        "pilot4e_max_scaled_metric_difference": max(scaled4e.values()),
        "pilot4d_ordered_rows_checked": int(len(merged_ordered)),
        "pilot4d_max_absolute_metric_difference": max(absolute4d.values()),
        "pilot4d_max_scaled_metric_difference": max(scaled4d.values()),
    }


def save_figures(raw, overall, comparisons, output_dir):
    fig, ax = plt.subplots(figsize=(11, 7))
    supplied = overall[
        (overall.environment == "permuted") & (overall.constructor_source == "supplied_area")
    ]
    for aggregation in SUPPLIED_AGGREGATIONS:
        group = supplied[supplied.aggregation == aggregation].sort_values("budget")
        ax.plot(group.budget, group.median_r2, marker="o", label=aggregation)
    ordered = overall[
        (overall.environment == "ordered")
        & (overall.constructor_source == "supplied_area")
        & (overall.aggregation == "current")
    ].sort_values("budget")
    ax.plot(
        ordered.budget, ordered.median_r2, marker="o", color="black",
        linestyle="--", linewidth=2, label="ordered current reference",
    )
    ax.set_xscale("log")
    ax.set_xlabel("Final-task training configurations (log scale)")
    ax.set_ylabel("Median held-out-family hull-area R²")
    ax.set_title("Pilot 4f — Supplied-area integration across budgets")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(output_dir / "pilot4f_supplied_sample_efficiency.png", dpi=180)
    plt.close(fig)

    rows = []
    for source in CONSTRUCTOR_SOURCES:
        focus = "fully_sorted" if source == "supplied_area" else "fully_orbit_sorted"
        selected = comparisons[
            (comparisons.budget == PRIMARY_BUDGET)
            & (comparisons.constructor_source == source)
            & (comparisons.focus_aggregation == focus)
            & (comparisons.comparator_aggregation == "current")
        ].iloc[0]
        rows.append(selected)
    forest = pd.DataFrame(rows).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 7))
    y = np.arange(len(forest))
    means = forest.mean_log_error_difference.to_numpy()
    low = means - forest.ci95_low.to_numpy()
    high = forest.ci95_high.to_numpy() - means
    ax.errorbar(means, y, xerr=np.vstack((low, high)), fmt="o", capsize=4)
    ax.axvline(0, color="black", linewidth=1, linestyle="--")
    ax.set_yticks(y, forest.constructor_source)
    ax.set_xlabel("Current minus invariant mean log error (positive favors invariance)")
    ax.set_title("Pilot 4f — Fully invariant integration at budget 200")
    fig.tight_layout()
    fig.savefig(output_dir / "pilot4f_invariant_comparisons.png", dpi=180)
    plt.close(fig)

    sources = ["supplied_area", "greedy", "sampled_lookahead", "independent_search"]
    family_rows = []
    for source in sources:
        focus = "fully_sorted" if source == "supplied_area" else "fully_orbit_sorted"
        subset = raw[
            (raw.environment == "permuted")
            & (raw.budget == PRIMARY_BUDGET)
            & (raw.constructor_source == source)
            & (raw.aggregation.isin(["current", focus]))
        ]
        means = subset.groupby(["test_family", "aggregation"]).log1p_nrmse.mean().unstack()
        for family in FAMILIES:
            family_rows.append({
                "test_family": family,
                "constructor_source": source,
                "improvement": means.loc[family, "current"] - means.loc[family, focus],
            })
    family_improvement = pd.DataFrame(family_rows)
    fig, ax = plt.subplots(figsize=(12, 7))
    width = 0.19
    x = np.arange(len(FAMILIES))
    for index, source in enumerate(sources):
        group = family_improvement[family_improvement.constructor_source == source].set_index(
            "test_family"
        ).loc[FAMILIES]
        ax.bar(x + (index - 1.5) * width, group.improvement, width, label=source)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xticks(x, FAMILIES)
    ax.set_ylabel("Current minus invariant mean log error")
    ax.set_title("Pilot 4f — Family-level integration changes at budget 200")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "pilot4f_family_integration.png", dpi=180)
    plt.close(fig)


def parse_args():
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--output-dir", type=Path, default=Path("pilot4f_output"))
    parser.add_argument("--pilot4e-dir", type=Path, default=script_dir.parent / "generative_geometry_pilot4e")
    parser.add_argument("--pilot4d-dir", type=Path, default=script_dir.parent / "generative_geometry_pilot4d")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.replicates < 2:
        raise ValueError("At least two replicates are required for paired intervals")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw, manifest, invariance = run_experiment(
        args.replicates, args.pilot4e_dir / "pilot4e_search_summary.csv"
    )
    validate_outputs(raw, manifest, invariance, args.replicates)
    reproduction = validate_previous_reproduction(raw, args.pilot4e_dir, args.pilot4d_dir)
    overall, by_family = make_summaries(raw)
    comparisons = mechanism_comparisons(raw)
    interactions = aggregation_interactions(raw)
    raw.to_csv(args.output_dir / "pilot4f_raw_results.csv", index=False)
    manifest.to_csv(args.output_dir / "pilot4f_constructor_manifest.csv", index=False)
    invariance.to_csv(args.output_dir / "pilot4f_invariance_checks.csv", index=False)
    overall.to_csv(args.output_dir / "pilot4f_summary_overall.csv", index=False)
    by_family.to_csv(args.output_dir / "pilot4f_summary_by_family.csv", index=False)
    comparisons.to_csv(args.output_dir / "pilot4f_paired_comparisons.csv", index=False)
    interactions.to_csv(args.output_dir / "pilot4f_aggregation_interactions.csv", index=False)
    save_figures(raw, overall, comparisons, args.output_dir)
    metadata = {
        "experiment": "Generative Geometry Pilot 4f",
        "protocol_date": "2026-11-27",
        "replicates": args.replicates,
        "environment": "permuted with ordered supplied-area reference",
        "constructor_search": "none; frozen Pilot 4e outputs",
        "constructor_sources": CONSTRUCTOR_SOURCES,
        "supplied_aggregations": SUPPLIED_AGGREGATIONS,
        "frozen_aggregations": FROZEN_AGGREGATIONS,
        "families": FAMILIES,
        "held_out_final_target": FINAL_TARGET,
        "budgets_nested": BUDGETS,
        "ridge_alpha": RIDGE_ALPHA,
        "primary_budget": PRIMARY_BUDGET,
        "primary_comparison": "supplied_area fully_sorted versus current",
        "primary_metric": "Paired replicate means of log(1+NRMSE); current minus invariant",
        "interval_method": "Two-sided 95% Student-t interval over replicate means across four folds",
        "invariance_tolerance": INVARIANCE_TOLERANCE,
        "required_invariance_checks": int(invariance.required_invariant.sum()),
        "diagnostic_non_invariance_checks": int((~invariance.required_invariant).sum()),
        "permuted_final_evaluations": int(np.sum(raw.environment == "permuted")),
        "ordered_reference_evaluations": int(np.sum(raw.environment == "ordered")),
        "reproduction": reproduction,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
        "matplotlib": plt.matplotlib.__version__,
    }
    with open(args.output_dir / "pilot4f_metadata.json", "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
    primary = comparisons[comparisons.primary_comparison]
    print("\nPrimary comparison:")
    print(primary[[
        "constructor_source", "focus_aggregation", "comparator_aggregation",
        "mean_log_error_difference", "ci95_low", "ci95_high",
        "replicate_win_fraction", "exact_sign_p",
    ]].to_string(index=False))
    print("\nReproduction checks:", reproduction)
    print(f"\nSaved results to {args.output_dir}")


if __name__ == "__main__":
    main()
