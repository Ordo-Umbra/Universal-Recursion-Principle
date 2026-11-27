"""
Generative Geometry — Pilot 4d: stability-guided constructor refinement.

A fixed shallow `dot` constructor is revised through explicit parent-child
expression lineages in paired ordered and point-permuted arms. The geometry and
targets are identical across arms; only input point labels change. Matched
independent-search, unscaffolded-search, and random-lineage controls test whether
permutation increases the value of multi-step parent chaining on held-out area.

Usage
-----
    python3 generative_geometry_pilot4d.py --output-dir ./pilot4d_output
    python3 generative_geometry_pilot4d.py --replicates 2 --output-dir ./smoke

See Pilot_4d_Protocol.md for the rules fixed before implementation and testing.
"""

from __future__ import annotations

import argparse
import itertools
import json
import platform
from collections import Counter
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
SEARCH_PER_FAMILY = 160
DEVELOPMENT_FIT_ORDER = 80
DEVELOPMENT_VALIDATION = 80
DEVELOPMENT_BUDGETS = [40, 80]
BUDGETS = [25, 50, 100, 200, 500, 1000]
FAMILIES = ["convex_radial", "interior_points", "irregular_radial", "elongated"]
TARGETS = ["hull_area", "hull_perimeter", "compactness", "hull_count"]
DEVELOPMENT_TARGETS = ["hull_perimeter", "compactness", "hull_count"]
FINAL_TARGET = "hull_area"
ARMS = ["ordered", "permuted"]
REPRESENTATIONS = [
    "pairwise",
    "initial",
    "refined",
    "independent_search",
    "unscaffolded",
    "random_lineage",
    "supplied_area",
    "raw_quadratic",
]
SEARCH_CONDITIONS = ["refined", "independent_search", "unscaffolded", "random_lineage"]
RIDGE_ALPHA = 1e-3
PRIMARY_BUDGET = 200
MAX_REVISION_ROUNDS = 4
MAX_EXPRESSION_DEPTH = 2
IMPROVEMENT_TOLERANCE = 1e-4
AREA_EXPRESSION = "abs(cross)"
INITIAL_EXPRESSION = "dot"
LEAVES = ["dot", "cross", "u2", "v2", "w2"]
UNARY_OPERATIONS = ["abs", "square", "sqrt_abs"]
BINARY_OPERATIONS = ["multiply", "divide", "add", "abs_diff"]

PAIR_INDICES = list(itertools.combinations(range(N_POINTS), 2))
TRIPLE_INDICES = list(itertools.combinations(range(N_POINTS), 3))
RAW_QUADRATIC_INDICES = list(itertools.combinations_with_replacement(range(2 * N_POINTS), 2))

# Expression trees are tuples: ("leaf", name), ("unary", operation, child),
# or ("binary", operation, left, right).
INITIAL_TREE = ("leaf", INITIAL_EXPRESSION)
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
    return 1 + max(expression_depth(tree[2]), expression_depth(tree[3]))


def contains_subtree(tree, possible_child):
    if tree == possible_child:
        return True
    if tree[0] == "unary":
        return contains_subtree(tree[2], possible_child)
    if tree[0] == "binary":
        return contains_subtree(tree[2], possible_child) or contains_subtree(tree[3], possible_child)
    return False


def mutate_leaves(tree):
    if tree[0] == "leaf":
        for leaf in LEAVES:
            if leaf != tree[1]:
                yield ("leaf", leaf)
        return
    if tree[0] == "unary":
        for child in mutate_leaves(tree[2]):
            yield ("unary", tree[1], child)
        return
    for left in mutate_leaves(tree[2]):
        yield ("binary", tree[1], left, tree[3])
    for right in mutate_leaves(tree[3]):
        yield ("binary", tree[1], tree[2], right)


def mutate_operations(tree):
    if tree[0] == "unary":
        for operation in UNARY_OPERATIONS:
            if operation != tree[1]:
                yield ("unary", operation, tree[2])
        for child in mutate_operations(tree[2]):
            yield ("unary", tree[1], child)
        return
    if tree[0] == "binary":
        for operation in BINARY_OPERATIONS:
            if operation != tree[1]:
                yield ("binary", operation, tree[2], tree[3])
        for left in mutate_operations(tree[2]):
            yield ("binary", tree[1], left, tree[3])
        for right in mutate_operations(tree[3]):
            yield ("binary", tree[1], tree[2], right)


def mutation_neighborhood(tree):
    variants = set(mutate_leaves(tree)) | set(mutate_operations(tree))
    if expression_depth(tree) < MAX_EXPRESSION_DEPTH:
        for operation in UNARY_OPERATIONS:
            variants.add(("unary", operation, tree))
        for operation in BINARY_OPERATIONS:
            for leaf in LEAVES:
                leaf_tree = ("leaf", leaf)
                variants.add(("binary", operation, tree, leaf_tree))
                variants.add(("binary", operation, leaf_tree, tree))
    if tree[0] == "unary":
        variants.add(tree[2])
    elif tree[0] == "binary":
        variants.add(tree[2])
        variants.add(tree[3])
        variants.add(("binary", tree[1], tree[3], tree[2]))
    variants.discard(tree)
    return sorted(variants, key=expression_name)


def sample_expression(rng, depth=0):
    if depth >= MAX_EXPRESSION_DEPTH:
        return ("leaf", str(rng.choice(LEAVES)))
    kind = str(rng.choice(["leaf", "unary", "binary"], p=[0.40, 0.25, 0.35]))
    if kind == "leaf":
        return ("leaf", str(rng.choice(LEAVES)))
    if kind == "unary":
        return ("unary", str(rng.choice(UNARY_OPERATIONS)), sample_expression(rng, depth + 1))
    return (
        "binary",
        str(rng.choice(BINARY_OPERATIONS)),
        sample_expression(rng, depth + 1),
        sample_expression(rng, depth + 1),
    )


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


def raw_quadratic_features(raw):
    i = np.array([pair[0] for pair in RAW_QUADRATIC_INDICES])
    j = np.array([pair[1] for pair in RAW_QUADRATIC_INDICES])
    return np.column_stack((raw, raw[:, i] * raw[:, j]))


def local_leaves(raw):
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


def build_datasets(replicate):
    datasets = {}
    for family in FAMILIES:
        raw, targets = make_family_dataset(family, replicate)
        datasets[family] = {
            "raw": raw,
            "targets": targets,
            "pairwise": pairwise_features(raw),
            "raw_quadratic": raw_quadratic_features(raw),
            "leaves": local_leaves(raw),
        }
    return datasets


def build_permuted_datasets(ordered_datasets, replicate):
    """Independently relabel points within each configuration, preserving targets."""
    datasets = {}
    for family_index, family in enumerate(FAMILIES):
        source = ordered_datasets[family]
        raw = source["raw"]
        rng = np.random.default_rng(93_000_000 + replicate * 3023 + family_index * 100_003)
        points = raw.reshape(-1, N_POINTS, 2)
        permutations = np.argsort(rng.random((len(raw), N_POINTS)), axis=1)
        permuted = np.take_along_axis(points, permutations[..., None], axis=1)
        permuted_raw = permuted.reshape(-1, 2 * N_POINTS)
        datasets[family] = {
            "raw": permuted_raw,
            "targets": source["targets"],
            "pairwise": pairwise_features(permuted_raw),
            "raw_quadratic": raw_quadratic_features(permuted_raw),
            "leaves": local_leaves(permuted_raw),
            "permutation_seed": 93_000_000 + replicate * 3023 + family_index * 100_003,
        }
    return datasets


def near_constant_fraction(values):
    variance = np.var(values, axis=0)
    mean = np.mean(values, axis=0)
    threshold = 1e-10 * (mean**2 + 1e-12)
    return float(np.mean(variance <= threshold))


def make_search_context(datasets, train_families, context_seed):
    rng = np.random.default_rng(context_seed)
    orders = {}
    for family in train_families:
        orders[family] = rng.permutation(SEARCH_PER_FAMILY)

    base = np.vstack([datasets[f]["pairwise"][:SEARCH_PER_FAMILY] for f in train_families])
    leaves = np.concatenate([datasets[f]["leaves"][:SEARCH_PER_FAMILY] for f in train_families], axis=0)
    development_indices = [TARGETS.index(task) for task in DEVELOPMENT_TARGETS]
    targets = np.concatenate([
        datasets[f]["targets"][:SEARCH_PER_FAMILY, development_indices] for f in train_families
    ], axis=0)
    offsets = {family: i * SEARCH_PER_FAMILY for i, family in enumerate(train_families)}

    folds = []
    small_fit_sets = []
    for held_out in train_families:
        fitting = [f for f in train_families if f != held_out]
        validation_indices = offsets[held_out] + orders[held_out][DEVELOPMENT_FIT_ORDER:]
        if len(validation_indices) != DEVELOPMENT_VALIDATION:
            raise RuntimeError("Unexpected development validation size")
        budget_indices = {}
        for budget in DEVELOPMENT_BUDGETS:
            per_family = budget // 2
            chosen = np.concatenate([
                offsets[f] + orders[f][:per_family] for f in fitting
            ])
            budget_indices[budget] = chosen
            small_fit_sets.append(chosen)
        folds.append({
            "held_out": held_out,
            "validation_indices": validation_indices,
            "budget_indices": budget_indices,
        })
    return {
        "families": train_families,
        "base": base,
        "leaves": leaves,
        "targets": targets,
        "offsets": offsets,
        "orders": orders,
        "folds": folds,
        "small_fit_sets": small_fit_sets,
    }


def gate_values(values, context):
    reasons = []
    if not np.isfinite(values).all():
        reasons.append("non_finite")
        return False, reasons
    if np.max(np.abs(values)) > 1e6:
        reasons.append("extreme_output")
    for family in context["families"]:
        offset = context["offsets"][family]
        family_values = values[offset:offset + SEARCH_PER_FAMILY]
        if near_constant_fraction(family_values) > 0.20:
            reasons.append(f"family_near_constant:{family}")
    for indices in context["small_fit_sets"]:
        if near_constant_fraction(values[indices]) > 0.20:
            reasons.append("small_sample_near_constant")
            break
    family_rms = []
    for family in context["families"]:
        offset = context["offsets"][family]
        family_values = values[offset:offset + SEARCH_PER_FAMILY]
        family_rms.append(float(np.sqrt(np.mean(family_values**2))))
    maximum = max(family_rms)
    minimum = min(family_rms)
    if maximum > 0 and (minimum <= 1e-12 * maximum or maximum / minimum > 100):
        reasons.append("family_scale_collapse")
    return len(reasons) == 0, reasons


def gate_expression(tree, context):
    values = evaluate_expression(context["leaves"], tree)
    return gate_values(values, context)


def assemble_representation(base, constructor_values):
    return np.column_stack((base, constructor_values))


def development_score(tree, context):
    constructor_values = evaluate_expression(context["leaves"], tree)
    x = assemble_representation(context["base"], constructor_values)
    raw_scores = []
    for fold in context["folds"]:
        validation_indices = fold["validation_indices"]
        for budget in DEVELOPMENT_BUDGETS:
            fit_indices = fold["budget_indices"][budget]
            with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
                scaler = StandardScaler()
                x_fit = scaler.fit_transform(x[fit_indices])
                x_validation = scaler.transform(x[validation_indices])
                y_fit = context["targets"][fit_indices]
                y_validation = context["targets"][validation_indices]
                target_mean = y_fit.mean(axis=0)
                target_sd = y_fit.std(axis=0)
                if np.any(target_sd <= 0):
                    raise RuntimeError("Development target has zero variance")
                model = Ridge(alpha=RIDGE_ALPHA)
                model.fit(x_fit, (y_fit - target_mean) / target_sd)
                prediction = model.predict(x_validation) * target_sd + target_mean
                scores = r2_score(y_validation, prediction, multioutput="raw_values")
            scores = np.asarray(scores, dtype=float)
            scores = np.nan_to_num(scores, nan=-1e12, posinf=1.0, neginf=-1e12)
            raw_scores.extend(scores.tolist())
    raw_scores = np.asarray(raw_scores)
    clipped = np.clip(raw_scores, -1.0, 1.0)
    return {
        "development_robust_r2": float(np.median(clipped)),
        "development_raw_mean_r2": float(np.mean(raw_scores)),
        "development_raw_median_r2": float(np.median(raw_scores)),
        "development_raw_min_r2": float(np.min(raw_scores)),
    }


def proposal_row(condition, replicate, test_family, round_number, evaluation_number,
                 parent, tree, valid, reasons, scores=None, accepted=False):
    return {
        "condition": condition,
        "replicate": replicate,
        "test_family": test_family,
        "round": round_number,
        "evaluation_number": evaluation_number,
        "parent_expression": expression_name(parent),
        "expression": expression_name(tree),
        "expression_depth": expression_depth(tree),
        "valid": bool(valid),
        "gate_reasons": "|".join(reasons),
        "development_robust_r2": np.nan if scores is None else scores["development_robust_r2"],
        "development_raw_mean_r2": np.nan if scores is None else scores["development_raw_mean_r2"],
        "development_raw_median_r2": np.nan if scores is None else scores["development_raw_median_r2"],
        "development_raw_min_r2": np.nan if scores is None else scores["development_raw_min_r2"],
        "accepted": bool(accepted),
    }


def refined_search(context, replicate, test_family):
    current = INITIAL_TREE
    initial_valid, initial_reasons = gate_expression(current, context)
    if not initial_valid:
        raise RuntimeError(f"Initial constructor failed gates: {initial_reasons}")
    current_scores = development_score(current, context)
    initial_scores = current_scores
    current_score = current_scores["development_robust_r2"]
    rows = []
    accepted_rows = []
    round_counts = []
    evaluation_number = 0

    for round_number in range(1, MAX_REVISION_ROUNDS + 1):
        proposals = mutation_neighborhood(current)
        round_counts.append(len(proposals))
        scored = []
        for tree in proposals:
            evaluation_number += 1
            valid, reasons = gate_expression(tree, context)
            scores = development_score(tree, context) if valid else None
            scored.append((tree, valid, reasons, scores))
            rows.append(proposal_row(
                "refined", replicate, test_family, round_number, evaluation_number,
                current, tree, valid, reasons, scores, accepted=False,
            ))
        valid_scored = [item for item in scored if item[1]]
        if not valid_scored:
            break
        best = min(
            valid_scored,
            key=lambda item: (-item[3]["development_robust_r2"], expression_name(item[0])),
        )
        best_score = best[3]["development_robust_r2"]
        if best_score <= current_score + IMPROVEMENT_TOLERANCE:
            break
        parent = current
        parent_score = current_score
        current = best[0]
        current_scores = best[3]
        current_score = best_score
        accepted_evaluation = evaluation_number - len(proposals) + proposals.index(best[0]) + 1
        rows[accepted_evaluation - 1]["accepted"] = True
        accepted_rows.append({
            "replicate": replicate,
            "test_family": test_family,
            "round": round_number,
            "evaluation_number": accepted_evaluation,
            "parent_expression": expression_name(parent),
            "child_expression": expression_name(current),
            "parent_robust_r2": parent_score,
            "child_robust_r2": current_score,
            "robust_r2_improvement": current_score - parent_score,
            "parent_structurally_embedded": contains_subtree(current, parent),
            "child_depth": expression_depth(current),
        })
    return {
        "expression": current,
        "scores": current_scores,
        "initial_scores": initial_scores,
        "evaluations": evaluation_number,
        "round_counts": round_counts,
        "proposal_rows": rows,
        "accepted_rows": accepted_rows,
    }


def round_for_evaluation(evaluation_number, round_counts):
    cumulative = 0
    for round_number, count in enumerate(round_counts, start=1):
        cumulative += count
        if evaluation_number <= cumulative:
            return round_number
    raise ValueError("Evaluation exceeds matched round counts")


def independent_search(context, replicate, test_family, evaluations, round_counts, seed, initial_scores):
    rng = np.random.default_rng(seed)
    incumbent = INITIAL_TREE
    incumbent_scores = initial_scores
    incumbent_score = incumbent_scores["development_robust_r2"]
    rows = []
    for evaluation_number in range(1, evaluations + 1):
        round_number = round_for_evaluation(evaluation_number, round_counts)
        tree = sample_expression(rng)
        valid, reasons = gate_expression(tree, context)
        scores = development_score(tree, context) if valid else None
        accepted = False
        if valid and scores["development_robust_r2"] > incumbent_score + IMPROVEMENT_TOLERANCE:
            incumbent = tree
            incumbent_scores = scores
            incumbent_score = scores["development_robust_r2"]
            accepted = True
        elif valid and scores["development_robust_r2"] == incumbent_score:
            # Lexical tie-breaking applies only among exactly equal scores.
            if expression_name(tree) < expression_name(incumbent):
                incumbent = tree
                incumbent_scores = scores
                incumbent_score = scores["development_robust_r2"]
                accepted = True
        rows.append(proposal_row(
            "independent_search", replicate, test_family, round_number, evaluation_number,
            INITIAL_TREE, tree, valid, reasons, scores, accepted=accepted,
        ))
    return {"expression": incumbent, "scores": incumbent_scores, "proposal_rows": rows}


def unscaffolded_search(context, replicate, test_family, evaluations, round_counts, initial_scores):
    root_neighborhood = mutation_neighborhood(INITIAL_TREE)
    incumbent = INITIAL_TREE
    incumbent_scores = initial_scores
    incumbent_score = incumbent_scores["development_robust_r2"]
    rows = []
    for evaluation_number in range(1, evaluations + 1):
        round_number = round_for_evaluation(evaluation_number, round_counts)
        tree = root_neighborhood[(evaluation_number - 1) % len(root_neighborhood)]
        valid, reasons = gate_expression(tree, context)
        scores = development_score(tree, context) if valid else None
        accepted = False
        if valid and scores["development_robust_r2"] > incumbent_score + IMPROVEMENT_TOLERANCE:
            incumbent = tree
            incumbent_scores = scores
            incumbent_score = scores["development_robust_r2"]
            accepted = True
        elif valid and scores["development_robust_r2"] == incumbent_score:
            if expression_name(tree) < expression_name(incumbent):
                incumbent = tree
                incumbent_scores = scores
                incumbent_score = scores["development_robust_r2"]
                accepted = True
        rows.append(proposal_row(
            "unscaffolded", replicate, test_family, round_number, evaluation_number,
            INITIAL_TREE, tree, valid, reasons, scores, accepted=accepted,
        ))
    return {"expression": incumbent, "scores": incumbent_scores, "proposal_rows": rows}


def random_lineage_search(context, replicate, test_family, round_counts, seed):
    rng = np.random.default_rng(seed)
    current = INITIAL_TREE
    rows = []
    evaluation_number = 0
    for round_number, count in enumerate(round_counts, start=1):
        parent = current
        proposals = mutation_neighborhood(parent)
        next_current = parent
        accepted_evaluation = None
        for _ in range(count):
            evaluation_number += 1
            tree = proposals[int(rng.integers(len(proposals)))]
            valid, reasons = gate_expression(tree, context)
            if valid:
                next_current = tree
                accepted_evaluation = evaluation_number
            rows.append(proposal_row(
                "random_lineage", replicate, test_family, round_number, evaluation_number,
                parent, tree, valid, reasons, scores=None, accepted=False,
            ))
        if accepted_evaluation is not None:
            rows[accepted_evaluation - 1]["accepted"] = True
        current = next_current
    return {"expression": current, "scores": None, "proposal_rows": rows}


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
    return {"mse": mse, "nrmse": nrmse, "r2": r2, "log1p_nrmse": float(np.log1p(nrmse))}


def constructor_values_for_dataset(dataset, tree, train=True):
    leaves = dataset["leaves"][:TRAIN_POOL_PER_FAMILY] if train else dataset["leaves"][TRAIN_POOL_PER_FAMILY:]
    return evaluate_expression(leaves, tree)


def run_experiment(replicates):
    result_rows = []
    proposal_rows = []
    accepted_rows = []
    search_rows = []
    final_index = TARGETS.index(FINAL_TARGET)

    for replicate in range(replicates):
        ordered_datasets = build_datasets(replicate)
        arm_datasets = {
            "ordered": ordered_datasets,
            "permuted": build_permuted_datasets(ordered_datasets, replicate),
        }
        for arm in ARMS:
            datasets = arm_datasets[arm]
            for fold, test_family in enumerate(FAMILIES):
                train_families = [f for f in FAMILIES if f != test_family]
                context_seed = 90_000_000 + replicate * 3001 + fold * 100_003
                context = make_search_context(datasets, train_families, context_seed)

                refined = refined_search(context, replicate, test_family)
                evaluations = refined["evaluations"]
                round_counts = refined["round_counts"]
                independent = independent_search(
                    context, replicate, test_family, evaluations, round_counts,
                    91_000_000 + replicate * 3011 + fold * 100_003,
                    refined["initial_scores"],
                )
                unscaffolded = unscaffolded_search(
                    context, replicate, test_family, evaluations, round_counts,
                    refined["initial_scores"],
                )
                random_lineage = random_lineage_search(
                    context, replicate, test_family, round_counts,
                    92_000_000 + replicate * 3019 + fold * 100_003,
                )
                search_results = {
                    "initial": {"expression": INITIAL_TREE, "scores": refined["initial_scores"]},
                    "refined": refined,
                    "independent_search": independent,
                    "unscaffolded": unscaffolded,
                    "random_lineage": random_lineage,
                    "supplied_area": {"expression": AREA_TREE, "scores": None},
                }
                for condition in SEARCH_CONDITIONS:
                    rows = search_results[condition]["proposal_rows"]
                    for row in rows:
                        row["arm"] = arm
                    proposal_rows.extend(rows)
                for row in refined["accepted_rows"]:
                    row["arm"] = arm
                accepted_rows.extend(refined["accepted_rows"])

                search_row = {
                    "arm": arm,
                    "replicate": replicate,
                    "test_family": test_family,
                    "candidate_evaluations_per_guided_condition": evaluations,
                    "refined_rounds": len(round_counts),
                    "refined_accepted_revisions": len(refined["accepted_rows"]),
                    "refined_revision_path": " -> ".join(
                        [INITIAL_EXPRESSION] + [row["child_expression"] for row in refined["accepted_rows"]]
                    ),
                    "refined_initial_robust_r2": refined["initial_scores"]["development_robust_r2"],
                    "refined_final_robust_r2": refined["scores"]["development_robust_r2"],
                }
                for condition in ["initial", "refined", "independent_search", "unscaffolded", "random_lineage", "supplied_area"]:
                    tree = search_results[condition]["expression"]
                    search_row[f"{condition}_expression"] = expression_name(tree)
                    search_row[f"{condition}_depth"] = expression_depth(tree)
                    search_row[f"{condition}_is_exact_area"] = tree == AREA_TREE
                search_rows.append(search_row)

                base_train = np.vstack([
                    datasets[f]["pairwise"][:TRAIN_POOL_PER_FAMILY] for f in train_families
                ])
                base_test = datasets[test_family]["pairwise"][TRAIN_POOL_PER_FAMILY:]
                raw_train = np.vstack([
                    datasets[f]["raw_quadratic"][:TRAIN_POOL_PER_FAMILY] for f in train_families
                ])
                raw_test = datasets[test_family]["raw_quadratic"][TRAIN_POOL_PER_FAMILY:]
                representation_data = {
                    "pairwise": (base_train, base_test),
                    "raw_quadratic": (raw_train, raw_test),
                }
                for condition in ["initial", "refined", "independent_search", "unscaffolded", "random_lineage", "supplied_area"]:
                    tree = search_results[condition]["expression"]
                    train_constructor = np.concatenate([
                        constructor_values_for_dataset(datasets[f], tree, train=True) for f in train_families
                    ], axis=0)
                    test_constructor = constructor_values_for_dataset(datasets[test_family], tree, train=False)
                    representation_data[condition] = (
                        assemble_representation(base_train, train_constructor),
                        assemble_representation(base_test, test_constructor),
                    )

                y_train_full = np.concatenate([
                    datasets[f]["targets"][:TRAIN_POOL_PER_FAMILY, final_index] for f in train_families
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
                            "arm": arm,
                            "replicate": replicate,
                            "test_family": test_family,
                            "representation": representation,
                            "budget": budget,
                            "n_features": x_train_full.shape[1],
                            "expression": expression_name(search_results[representation]["expression"])
                            if representation in search_results else "",
                            "candidate_evaluations": evaluations,
                            "train_order_seed": order_seed,
                            **metrics,
                        })
        if (replicate + 1) % 2 == 0 or replicate + 1 == replicates:
            print(f"Completed {replicate + 1}/{replicates} replicates across both arms", flush=True)
    return (
        pd.DataFrame(result_rows),
        pd.DataFrame(proposal_rows),
        pd.DataFrame(accepted_rows),
        pd.DataFrame(search_rows),
    )


def make_summaries(raw):
    overall = (
        raw.groupby(["arm", "budget", "representation"], sort=True)
        .agg(
            mean_r2=("r2", "mean"),
            sd_r2=("r2", "std"),
            median_r2=("r2", "median"),
            q10_r2=("r2", lambda x: float(np.quantile(x, 0.10))),
            median_nrmse=("nrmse", "median"),
            mean_log1p_nrmse=("log1p_nrmse", "mean"),
            sd_log1p_nrmse=("log1p_nrmse", "std"),
            observations=("r2", "size"),
        )
        .reset_index()
    )
    by_family = (
        raw.groupby(["arm", "budget", "test_family", "representation"], sort=True)
        .agg(
            mean_r2=("r2", "mean"),
            sd_r2=("r2", "std"),
            median_r2=("r2", "median"),
            median_nrmse=("nrmse", "median"),
            mean_log1p_nrmse=("log1p_nrmse", "mean"),
            replicates=("r2", "size"),
        )
        .reset_index()
    )
    return overall, by_family


def paired_comparisons(raw):
    rows = []
    comparators = [
        "initial", "random_lineage", "unscaffolded", "independent_search",
        "supplied_area", "pairwise", "raw_quadratic",
    ]
    for arm in ARMS:
        for budget in BUDGETS:
            subset = raw[(raw["arm"] == arm) & (raw["budget"] == budget)]
            wide = subset.pivot(
                index=["replicate", "test_family"], columns="representation", values="log1p_nrmse"
            )
            r2_wide = subset.pivot(
                index=["replicate", "test_family"], columns="representation", values="r2"
            )
            for comparator in comparators:
                paired = wide[["refined", comparator]].dropna()
                # Positive difference favors refined: comparator error minus refined error.
                fold_difference = paired[comparator] - paired["refined"]
                replicate_difference = fold_difference.groupby("replicate").mean()
                n = len(replicate_difference)
                mean_difference = float(replicate_difference.mean())
                sd = float(replicate_difference.std(ddof=1))
                margin = float(student_t.ppf(0.975, n - 1)) * sd / np.sqrt(n)
                wins = int(np.sum(replicate_difference > 0))
                sign_p = float(binomtest(wins, n, 0.5, alternative="two-sided").pvalue)
                rows.append({
                    "arm": arm,
                    "budget": budget,
                    "comparator": comparator,
                    "replicates": n,
                    "refined_mean_log1p_nrmse": float(paired["refined"].mean()),
                    "comparator_mean_log1p_nrmse": float(paired[comparator].mean()),
                    "mean_log_error_difference": mean_difference,
                    "ci95_low": mean_difference - margin,
                    "ci95_high": mean_difference + margin,
                    "ci_excludes_zero": bool((mean_difference - margin) * (mean_difference + margin) > 0),
                    "positive_favors_refined": True,
                    "replicate_win_fraction": float(wins / n),
                    "exact_sign_p": sign_p,
                    "refined_mean_r2": float(r2_wide["refined"].mean()),
                    "comparator_mean_r2": float(r2_wide[comparator].mean()),
                    "refined_median_r2": float(r2_wide["refined"].median()),
                    "comparator_median_r2": float(r2_wide[comparator].median()),
                })
    return pd.DataFrame(rows)


def arm_interactions(raw):
    rows = []
    for budget in BUDGETS:
        subset = raw[raw["budget"] == budget]
        wide = subset.pivot(
            index=["arm", "replicate", "test_family"],
            columns="representation", values="log1p_nrmse",
        ).reset_index()
        wide["refinement_advantage"] = wide["unscaffolded"] - wide["refined"]
        replicate_arm = wide.groupby(["arm", "replicate"])["refinement_advantage"].mean().unstack("arm")
        difference = replicate_arm["permuted"] - replicate_arm["ordered"]
        n = len(difference)
        mean_difference = float(difference.mean())
        sd = float(difference.std(ddof=1))
        margin = float(student_t.ppf(0.975, n - 1)) * sd / np.sqrt(n)
        rows.append({
            "budget": budget,
            "replicates": n,
            "ordered_refinement_advantage": float(replicate_arm["ordered"].mean()),
            "permuted_refinement_advantage": float(replicate_arm["permuted"].mean()),
            "permuted_minus_ordered": mean_difference,
            "ci95_low": mean_difference - margin,
            "ci95_high": mean_difference + margin,
            "ci_excludes_zero": bool((mean_difference - margin) * (mean_difference + margin) > 0),
            "replicate_positive_fraction": float(np.mean(difference > 0)),
        })
    return pd.DataFrame(rows)


def lineage_arm_comparisons(search):
    """Pre-specified paired exact McNemar analyses for binary lineage outcomes."""
    rows = []
    index = ["replicate", "test_family"]
    ordered = search[search["arm"] == "ordered"].set_index(index)
    permuted = search[search["arm"] == "permuted"].set_index(index)
    outcomes = {
        "multi_step": (
            ordered["refined_accepted_revisions"] >= 2,
            permuted["refined_accepted_revisions"] >= 2,
        ),
        "terminal_exact_area": (
            ordered["refined_is_exact_area"],
            permuted["refined_is_exact_area"],
        ),
    }
    for outcome, (left, right) in outcomes.items():
        only_ordered = int(np.sum(left & ~right))
        only_permuted = int(np.sum(~left & right))
        discordant = only_ordered + only_permuted
        p_value = float(binomtest(only_permuted, discordant, 0.5).pvalue) if discordant else 1.0
        rows.append({
            "outcome": outcome,
            "ordered_count": int(left.sum()),
            "permuted_count": int(right.sum()),
            "both": int(np.sum(left & right)),
            "only_ordered": only_ordered,
            "only_permuted": only_permuted,
            "neither": int(np.sum(~left & ~right)),
            "exact_mcnemar_p": p_value,
        })
    return pd.DataFrame(rows)


def make_constructor_summary(search):
    rows = []
    for arm in ARMS:
        arm_search = search[search["arm"] == arm]
        for condition in ["refined", "independent_search", "unscaffolded", "random_lineage"]:
            counts = Counter(arm_search[f"{condition}_expression"])
            for expression, count in counts.items():
                subset = arm_search[arm_search[f"{condition}_expression"] == expression]
                rows.append({
                    "arm": arm,
                    "condition": condition,
                    "expression": expression,
                    "terminal_count": count,
                    "mean_candidate_evaluations": float(subset["candidate_evaluations_per_guided_condition"].mean()),
                    "exact_area": expression == AREA_EXPRESSION,
                })
    return pd.DataFrame(rows).sort_values(["arm", "condition", "terminal_count"], ascending=[True, True, False])


def save_figures(overall, by_family, search, accepted, output_dir):
    plot_representations = [
        "initial", "refined", "independent_search", "unscaffolded",
        "random_lineage", "supplied_area", "pairwise",
    ]
    for arm in ARMS:
        curves = overall[(overall["arm"] == arm) & (overall["budget"] >= 100)].pivot(
            index="budget", columns="representation", values="median_r2"
        ).reindex(columns=plot_representations)
        ax = curves.plot(marker="o", figsize=(12, 7))
        ax.set_xscale("log")
        ax.set_xticks([100, 200, 500, 1000])
        ax.set_xticklabels([100, 200, 500, 1000])
        ax.set_xlabel("Final-task training configurations (log scale)")
        ax.set_ylabel("Median held-out-family hull-area R²")
        ax.set_title(f"Pilot 4d — {arm.capitalize()} arm sample efficiency from budget 100")
        plt.tight_layout()
        plt.savefig(output_dir / f"pilot4d_sample_efficiency_{arm}.png", dpi=160)
        plt.close()

        family = by_family[(by_family["arm"] == arm) & (by_family["budget"] == PRIMARY_BUDGET)].pivot(
            index="test_family", columns="representation", values="median_r2"
        ).reindex(index=FAMILIES, columns=plot_representations)
        ax = family.plot(kind="bar", figsize=(14, 7))
        ax.set_xlabel("Unseen test family")
        ax.set_ylabel("Median hull-area R²")
        ax.set_title(f"Pilot 4d — {arm.capitalize()} arm family transfer at budget {PRIMARY_BUDGET}")
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(output_dir / f"pilot4d_family_transfer_{arm}.png", dpi=160)
        plt.close()

        paths = search[search["arm"] == arm]["refined_revision_path"].value_counts().head(12).sort_values()
        ax = paths.plot(kind="barh", figsize=(12, 7))
        ax.set_xlabel("Number of lineages")
        ax.set_ylabel("Revision path")
        ax.set_title(f"Pilot 4d — {arm.capitalize()} arm refinement paths")
        plt.tight_layout()
        plt.savefig(output_dir / f"pilot4d_revision_paths_{arm}.png", dpi=160)
        plt.close()

    revision_counts = (
        search.groupby(["refined_accepted_revisions", "arm"]).size().unstack("arm").fillna(0)
        .reindex(columns=ARMS)
    )
    ax = revision_counts.plot(kind="bar", figsize=(9, 5))
    ax.set_xlabel("Accepted syntactic revisions per refined lineage")
    ax.set_ylabel("Number of search runs")
    ax.set_title("Pilot 4d — Refinement depth by arm")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_dir / "pilot4d_revision_counts.png", dpi=160)
    plt.close()


def validate_outputs(raw, proposals, accepted, search, replicates):
    expected_results = replicates * len(ARMS) * len(FAMILIES) * len(REPRESENTATIONS) * len(BUDGETS)
    expected_runs = replicates * len(ARMS) * len(FAMILIES)
    if len(raw) != expected_results or len(search) != expected_runs:
        raise RuntimeError("Unexpected result or search row count")
    if not np.isfinite(raw[["mse", "nrmse", "r2", "log1p_nrmse"]].to_numpy()).all():
        raise RuntimeError("Non-finite final model result detected")
    for _, row in search.iterrows():
        arm = row["arm"]
        rep = int(row["replicate"])
        family = row["test_family"]
        conditions = proposals[
            (proposals["arm"] == arm) & (proposals["replicate"] == rep)
            & (proposals["test_family"] == family)
        ]
        expected = int(row["candidate_evaluations_per_guided_condition"])
        for condition in SEARCH_CONDITIONS:
            if len(conditions[conditions["condition"] == condition]) != expected:
                raise RuntimeError(f"Unmatched proposal budget for {condition}, {arm}, replicate {rep}, {family}")
    if len(accepted) != int(search["refined_accepted_revisions"].sum()):
        raise RuntimeError("Accepted-lineage count does not match search summary")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--output-dir", type=Path, default=Path("pilot4d_output"))
    return parser.parse_args()


def main():
    args = parse_args()
    if args.replicates < 2:
        raise ValueError("At least two replicates are required for paired intervals")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    raw, proposals, accepted, search = run_experiment(args.replicates)
    validate_outputs(raw, proposals, accepted, search, args.replicates)
    overall, by_family = make_summaries(raw)
    comparisons = paired_comparisons(raw)
    interactions = arm_interactions(raw)
    lineage_comparisons = lineage_arm_comparisons(search)
    constructor_summary = make_constructor_summary(search)

    raw.to_csv(args.output_dir / "pilot4d_raw_results.csv", index=False)
    proposals.to_csv(args.output_dir / "pilot4d_proposal_history.csv", index=False)
    accepted.to_csv(args.output_dir / "pilot4d_accepted_refinements.csv", index=False)
    search.to_csv(args.output_dir / "pilot4d_search_summary.csv", index=False)
    constructor_summary.to_csv(args.output_dir / "pilot4d_constructor_summary.csv", index=False)
    overall.to_csv(args.output_dir / "pilot4d_summary_overall.csv", index=False)
    by_family.to_csv(args.output_dir / "pilot4d_summary_by_family.csv", index=False)
    comparisons.to_csv(args.output_dir / "pilot4d_paired_comparisons.csv", index=False)
    interactions.to_csv(args.output_dir / "pilot4d_arm_interactions.csv", index=False)
    lineage_comparisons.to_csv(args.output_dir / "pilot4d_lineage_arm_comparisons.csv", index=False)
    save_figures(overall, by_family, search, accepted, args.output_dir)

    metadata = {
        "experiment": "Generative Geometry Pilot 4d",
        "protocol_date": "2026-11-23",
        "replicates": args.replicates,
        "arms": ARMS,
        "permutation_seed_base": 93_000_000,
        "permutation": "Independent deterministic point-label permutation per configuration in permuted arm",
        "families": FAMILIES,
        "development_targets": DEVELOPMENT_TARGETS,
        "held_out_final_target": FINAL_TARGET,
        "initial_expression": INITIAL_EXPRESSION,
        "area_reference_expression": AREA_EXPRESSION,
        "leaves": LEAVES,
        "unary_operations": UNARY_OPERATIONS,
        "binary_operations": BINARY_OPERATIONS,
        "maximum_expression_depth": MAX_EXPRESSION_DEPTH,
        "maximum_revision_rounds": MAX_REVISION_ROUNDS,
        "improvement_tolerance": IMPROVEMENT_TOLERANCE,
        "development_budgets": DEVELOPMENT_BUDGETS,
        "development_validation_per_fold": DEVELOPMENT_VALIDATION,
        "development_score": "Median of 18 task/fold/budget R2 values clipped to [-1,1]",
        "budgets_nested": BUDGETS,
        "representations": REPRESENTATIONS,
        "ridge_alpha": RIDGE_ALPHA,
        "primary_budget": PRIMARY_BUDGET,
        "primary_metric": "Paired replicate means of log(1+NRMSE); comparator minus refined",
        "interval_method": "Two-sided 95% Student-t interval over replicate means across four folds",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
        "matplotlib": plt.matplotlib.__version__,
    }
    with open(args.output_dir / "pilot4d_metadata.json", "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    primary = comparisons[comparisons["budget"] == PRIMARY_BUDGET]
    print("\nRefined-constructor paired comparisons at budget 200:")
    print(primary[[
        "arm", "comparator", "mean_log_error_difference", "ci95_low", "ci95_high",
        "replicate_win_fraction", "exact_sign_p",
    ]].to_string(index=False))
    print("\nArm interaction at budget 200:")
    print(interactions[interactions["budget"] == PRIMARY_BUDGET].to_string(index=False))
    print("\nRefined revision counts by arm:")
    print(search.groupby(["arm", "refined_accepted_revisions"]).size().to_string())
    print("\nMost frequent refined expressions by arm:")
    print(search.groupby(["arm", "refined_expression"]).size().groupby("arm", group_keys=False).nlargest(10).to_string())
    print(f"\nSaved results to {args.output_dir}")


if __name__ == "__main__":
    main()
