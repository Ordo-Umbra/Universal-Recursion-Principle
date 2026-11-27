"""Generative Geometry Pilot 4g: search aligned with invariant integration.

Pre-registered protocol: Pilot_4g_Protocol.md.
Three 500-proposal searches use the same sorted-pairwise/local-orbit feature
map during development and final held-out-family learning. No new stability
or ratio guard is introduced.
"""

import argparse
import itertools
import json
import platform
import time
import warnings
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
PROPOSAL_BUDGET = 500
LOOKAHEAD_CHILDREN = 5
LOOKAHEAD_GRANDCHILDREN = 4
SEARCH_CONDITIONS = ["greedy", "sampled_lookahead", "independent_search"]
REPRESENTATIONS = ["initial"] + SEARCH_CONDITIONS + ["supplied_area"]
RIDGE_ALPHA = 1e-3
PRIMARY_BUDGET = 200
MAX_EXPRESSION_DEPTH = 2
IMPROVEMENT_TOLERANCE = 1e-4
INVARIANCE_TOLERANCE = 1e-12
AREA_EXPRESSION = "abs(cross)"
INITIAL_EXPRESSION = "dot"
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


def near_constant_fraction(values):
    variance = np.var(values, axis=0)
    mean = np.mean(values, axis=0)
    threshold = 1e-10 * (mean**2 + 1e-12)
    return float(np.mean(variance <= threshold))


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


def make_search_context(datasets, train_families, context_seed):
    rng = np.random.default_rng(context_seed)
    orders = {family: rng.permutation(SEARCH_PER_FAMILY) for family in train_families}
    base = np.sort(np.vstack([
        datasets[f]["pairwise"][:SEARCH_PER_FAMILY] for f in train_families
    ]), axis=1)
    leaves = np.concatenate([
        datasets[f]["leaves"][:SEARCH_PER_FAMILY] for f in train_families
    ], axis=0)
    orbit = np.concatenate([
        datasets[f]["orbit_leaves"][:SEARCH_PER_FAMILY] for f in train_families
    ], axis=0)
    development_indices = [TARGETS.index(task) for task in DEVELOPMENT_TARGETS]
    targets = np.concatenate([
        datasets[f]["targets"][:SEARCH_PER_FAMILY, development_indices]
        for f in train_families
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
        "families": train_families, "base": base, "leaves": leaves,
        "orbit_leaves": orbit, "targets": targets, "offsets": offsets,
        "orders": orders, "folds": folds, "small_fit_sets": small_fit_sets,
    }


def development_score(tree, context):
    """Aligned score: exactly the downstream invariant integration map."""
    values = evaluate_expression(context["orbit_leaves"], tree)
    constructor = np.sort(values, axis=1)
    x = np.column_stack((context["base"], constructor))
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


def score_search_proposal(tree, context):
    valid, reasons = gate_expression(tree, context)
    if not valid:
        return {
            "valid": False, "reasons": reasons, "scores": None,
            "symmetry": "not_evaluated", "degree": np.nan, "dispersion": np.nan,
        }
    scores = development_score(tree, context)
    return {
        "valid": True, "reasons": [], "scores": scores,
        "symmetry": "orbit_integrated", "degree": np.nan, "dispersion": np.nan,
    }


def initialize_search(context):
    initial_result = score_search_proposal(INITIAL_TREE, context)
    if not initial_result["valid"]:
        raise RuntimeError("Initial constructor failed validity gates")
    return INITIAL_TREE, initial_result["scores"], initial_result


def summarize_search(condition, current, best_tree, best_scores, initial_result, records,
                     accepted_moves=0, non_improving_moves=0, negative_moves=0,
                     descendant_moves=0, archive_occupancy=1):
    output = expression_name(best_tree)
    encounters = [row for row in records if row["valid"] and row["expression"] == output]
    return {
        "condition": condition,
        "proposal_evaluations": len(records),
        "accepted_moves": accepted_moves,
        "non_improving_moves": non_improving_moves,
        "negative_moves": negative_moves,
        "descendant_value_moves": descendant_moves,
        "archive_occupancy": archive_occupancy,
        "current_expression": expression_name(current),
        "output_expression": output,
        "output_depth": expression_depth(best_tree),
        "output_robust_r2": best_scores["development_robust_r2"],
        "initial_robust_r2": initial_result["scores"]["development_robust_r2"],
        "output_symmetry_class": "orbit_integrated",
        "output_root_distance_capped": structural_root_distance(best_tree),
        "output_is_exact_area": best_tree == AREA_TREE,
        "area_encountered": any(row["expression"] == AREA_EXPRESSION and row["valid"] for row in records),
        "output_encounter_roles": "|".join(sorted({row["role"] for row in encounters})),
        "output_first_encounter_evaluation": min(
            [row["evaluation_number"] for row in encounters], default=0
        ),
        "valid_proposals": sum(row["valid"] for row in records),
        "invalid_proposals": sum(not row["valid"] for row in records),
        "initial_symmetry_class": initial_result["symmetry"],
    }



def search_record(condition, replicate, test_family, round_number, evaluation_number,
                  parent, tree, role, result=None, tabu=False, accepted=False,
                  acceptance_reason="", parent_score=np.nan, descendant_value=np.nan):
    scores = None if result is None else result["scores"]
    return {
        "condition": condition,
        "replicate": replicate,
        "test_family": test_family,
        "round": round_number,
        "evaluation_number": evaluation_number,
        "parent_expression": expression_name(parent),
        "expression": expression_name(tree),
        "role": role,
        "valid": bool(result is not None and result["valid"]),
        "tabu": bool(tabu),
        "gate_reasons": "" if result is None else "|".join(result["reasons"]),
        "development_robust_r2": np.nan if scores is None else scores["development_robust_r2"],
        "development_raw_mean_r2": np.nan if scores is None else scores["development_raw_mean_r2"],
        "development_raw_median_r2": np.nan if scores is None else scores["development_raw_median_r2"],
        "development_raw_min_r2": np.nan if scores is None else scores["development_raw_min_r2"],
        "symmetry_class": "asymmetric_other" if result is None else result["symmetry"],
        "homogeneity_degree": np.nan if result is None else result["degree"],
        "homogeneity_dispersion": np.nan if result is None else result["dispersion"],
        "parent_robust_r2": parent_score,
        "immediate_score_change": (
            np.nan if scores is None or not np.isfinite(parent_score)
            else scores["development_robust_r2"] - parent_score
        ),
        "descendant_value": descendant_value,
        "accepted": bool(accepted),
        "acceptance_reason": acceptance_reason,
    }


def update_best(best_tree, best_scores, tree, result):
    if not result["valid"]:
        return best_tree, best_scores, False
    score = result["scores"]["development_robust_r2"]
    best_score = best_scores["development_robust_r2"]
    if score > best_score or (score == best_score and expression_name(tree) < expression_name(best_tree)):
        return tree, result["scores"], True
    return best_tree, best_scores, False


def structural_root_distance(tree):
    if tree == INITIAL_TREE:
        return 0
    if tree in mutation_neighborhood(INITIAL_TREE):
        return 1
    return 2  # capped category: >=2


def greedy_search(context, replicate, test_family, seed):
    rng = np.random.default_rng(seed)
    current, current_scores, initial_result = initialize_search(context)
    best_tree, best_scores = current, current_scores
    records = []
    accepted_moves = 0
    for evaluation in range(1, PROPOSAL_BUDGET + 1):
        parent = current
        parent_score = current_scores["development_robust_r2"]
        proposals = mutation_neighborhood(parent)
        tree = proposals[int(rng.integers(len(proposals)))]
        result = score_search_proposal(tree, context)
        accepted = (
            result["valid"] and result["scores"]["development_robust_r2"]
            > parent_score + IMPROVEMENT_TOLERANCE
        )
        if accepted:
            current, current_scores = tree, result["scores"]
            accepted_moves += 1
        best_tree, best_scores, _ = update_best(best_tree, best_scores, tree, result)
        records.append(search_record(
            "greedy", replicate, test_family, 1, evaluation, parent, tree, "child",
            result, accepted=accepted, acceptance_reason="immediate_improvement" if accepted else "",
            parent_score=parent_score,
        ))
    summary = summarize_search(
        "greedy", current, best_tree, best_scores, initial_result, records,
        accepted_moves=accepted_moves,
    )
    summary["output_symmetry_class"] = "orbit_integrated"
    return best_tree, best_scores, records, summary


def sampled_lookahead_search(context, replicate, test_family, seed):
    rng = np.random.default_rng(seed)
    current, current_scores, initial_result = initialize_search(context)
    best_tree, best_scores = current, current_scores
    records = []
    evaluation = 0
    round_number = 0
    accepted_moves = non_improving = negative = descendant_moves = 0
    while evaluation < PROPOSAL_BUDGET:
        round_number += 1
        round_parent = current
        round_parent_score = current_scores["development_robust_r2"]
        neighborhood = mutation_neighborhood(round_parent)
        count = min(LOOKAHEAD_CHILDREN, len(neighborhood))
        indices = rng.choice(len(neighborhood), size=count, replace=False)
        child_candidates = []
        for index in indices:
            if evaluation >= PROPOSAL_BUDGET:
                break
            child = neighborhood[int(index)]
            evaluation += 1
            child_result = score_search_proposal(child, context)
            child_record = search_record(
                "sampled_lookahead", replicate, test_family, round_number, evaluation,
                round_parent, child, "child", child_result, parent_score=round_parent_score,
            )
            records.append(child_record)
            best_tree, best_scores, _ = update_best(best_tree, best_scores, child, child_result)
            descendant_value = -np.inf
            if child_result["valid"]:
                descendant_value = child_result["scores"]["development_robust_r2"]
                grandchild_neighborhood = mutation_neighborhood(child)
                for _ in range(LOOKAHEAD_GRANDCHILDREN):
                    if evaluation >= PROPOSAL_BUDGET:
                        break
                    grandchild = grandchild_neighborhood[int(rng.integers(len(grandchild_neighborhood)))]
                    evaluation += 1
                    grandchild_result = score_search_proposal(grandchild, context)
                    records.append(search_record(
                        "sampled_lookahead", replicate, test_family, round_number, evaluation,
                        child, grandchild, "grandchild", grandchild_result,
                        parent_score=child_result["scores"]["development_robust_r2"],
                    ))
                    best_tree, best_scores, _ = update_best(best_tree, best_scores, grandchild, grandchild_result)
                    if grandchild_result["valid"]:
                        descendant_value = max(
                            descendant_value, grandchild_result["scores"]["development_robust_r2"]
                        )
                child_record["descendant_value"] = descendant_value
                child_candidates.append((child, child_result, descendant_value, child_record))
        valid_candidates = [item for item in child_candidates if np.isfinite(item[2])]
        if valid_candidates:
            selected = min(valid_candidates, key=lambda item: (-item[2], expression_name(item[0])))
            child, child_result, descendant_value, child_record = selected
            if descendant_value > round_parent_score + IMPROVEMENT_TOLERANCE:
                immediate = child_result["scores"]["development_robust_r2"]
                current, current_scores = child, child_result["scores"]
                child_record["accepted"] = True
                child_record["acceptance_reason"] = "sampled_descendant_value"
                accepted_moves += 1
                if immediate <= round_parent_score + IMPROVEMENT_TOLERANCE:
                    non_improving += 1
                    descendant_moves += 1
                if immediate < round_parent_score - IMPROVEMENT_TOLERANCE:
                    negative += 1
    summary = summarize_search(
        "sampled_lookahead", current, best_tree, best_scores, initial_result, records,
        accepted_moves=accepted_moves, non_improving_moves=non_improving,
        negative_moves=negative, descendant_moves=descendant_moves,
    )
    summary["output_symmetry_class"] = "orbit_integrated"
    return best_tree, best_scores, records, summary


def independent_fixed_search(context, replicate, test_family, seed):
    rng = np.random.default_rng(seed)
    current, current_scores, initial_result = initialize_search(context)
    best_tree, best_scores = current, current_scores
    records = []
    accepted_moves = 0
    for evaluation in range(1, PROPOSAL_BUDGET + 1):
        tree = sample_expression(rng)
        result = score_search_proposal(tree, context)
        previous_best = best_scores["development_robust_r2"]
        best_tree, best_scores, improved = update_best(best_tree, best_scores, tree, result)
        if improved:
            accepted_moves += 1
        records.append(search_record(
            "independent_search", replicate, test_family, 1, evaluation,
            INITIAL_TREE, tree, "independent", result, accepted=improved,
            acceptance_reason="best_output_update" if improved else "", parent_score=previous_best,
        ))
    summary = summarize_search(
        "independent_search", best_tree, best_tree, best_scores, initial_result, records,
        accepted_moves=accepted_moves,
    )
    summary["output_symmetry_class"] = "orbit_integrated"
    return best_tree, best_scores, records, summary


def run_search_condition(condition, context, replicate, test_family, seed):
    functions = {
        "greedy": greedy_search,
        "sampled_lookahead": sampled_lookahead_search,
        "independent_search": independent_fixed_search,
    }
    return functions[condition](context, replicate, test_family, seed)


def invariant_representation_for_fold(datasets, train_families, test_family, tree, supplied=False):
    base_train = np.sort(np.vstack([
        datasets[f]["pairwise"][:TRAIN_POOL_PER_FAMILY] for f in train_families
    ]), axis=1)
    base_test = np.sort(datasets[test_family]["pairwise"][TRAIN_POOL_PER_FAMILY:], axis=1)
    key = "leaves" if supplied else "orbit_leaves"

    def block(family, train):
        values = datasets[family][key]
        values = values[:TRAIN_POOL_PER_FAMILY] if train else values[TRAIN_POOL_PER_FAMILY:]
        return np.sort(evaluate_expression(values, tree), axis=1)

    train_constructor = np.concatenate([block(f, True) for f in train_families], axis=0)
    test_constructor = block(test_family, False)
    return (
        np.column_stack((base_train, train_constructor)),
        np.column_stack((base_test, test_constructor)),
        "sorted15",
        "sorted20" if supplied else "orbit120",
    )


def run_experiment(replicates):
    invariance = validate_invariance()
    result_rows, proposal_rows, search_rows = [], [], []
    final_index = TARGETS.index(FINAL_TARGET)
    for replicate in range(replicates):
        ordered = build_ordered_datasets(replicate)
        datasets = build_permuted_datasets(ordered, replicate)
        for fold, test_family in enumerate(FAMILIES):
            train_families = [f for f in FAMILIES if f != test_family]
            context = make_search_context(
                datasets, train_families, 90_000_000 + replicate * 3001 + fold * 100_003
            )
            search_results = {
                "initial": {"expression": INITIAL_TREE, "scores": None},
                "supplied_area": {"expression": AREA_TREE, "scores": None},
            }
            for condition_index, condition in enumerate(SEARCH_CONDITIONS):
                tree, scores, records, summary = run_search_condition(
                    condition, context, replicate, test_family,
                    94_000_000 + replicate * 4001 + fold * 100_003 + condition_index * 1009,
                )
                if len(records) != PROPOSAL_BUDGET:
                    raise RuntimeError(f"Proposal budget mismatch: {condition}, {len(records)}")
                proposal_rows.extend(records)
                summary.update({"replicate": replicate, "test_family": test_family})
                search_rows.append(summary)
                search_results[condition] = {"expression": tree, "scores": scores}

            y_train_full = np.concatenate([
                datasets[f]["targets"][:TRAIN_POOL_PER_FAMILY, final_index]
                for f in train_families
            ])
            y_test = datasets[test_family]["targets"][TRAIN_POOL_PER_FAMILY:, final_index]
            order_seed = 80_000_000 + replicate * 2069 + fold * 100_003
            order = np.random.default_rng(order_seed).permutation(len(y_train_full))
            for representation in REPRESENTATIONS:
                tree = search_results[representation]["expression"]
                x_train_full, x_test, pairwise_mode, constructor_mode = invariant_representation_for_fold(
                    datasets, train_families, test_family, tree,
                    supplied=representation == "supplied_area",
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
                        "representation": representation,
                        "expression": expression_name(tree),
                        "aggregation": "fully_sorted" if representation == "supplied_area" else "fully_orbit_sorted",
                        "pairwise_mode": pairwise_mode,
                        "constructor_mode": constructor_mode,
                        "budget": budget,
                        "n_features": x_train_full.shape[1],
                        "candidate_evaluations": 0 if representation in {"initial", "supplied_area"} else PROPOSAL_BUDGET,
                        "train_order_seed": order_seed,
                        **metrics,
                    })
        print(f"Completed {replicate + 1}/{replicates} replicates", flush=True)
    return (
        pd.DataFrame(result_rows), pd.DataFrame(proposal_rows),
        pd.DataFrame(search_rows), invariance,
    )


def make_summaries(raw):
    overall = raw.groupby(["budget", "representation"], sort=True).agg(
        mean_r2=("r2", "mean"), sd_r2=("r2", "std"),
        median_r2=("r2", "median"), q10_r2=("r2", lambda x: float(np.quantile(x, 0.10))),
        min_r2=("r2", "min"), median_nrmse=("nrmse", "median"),
        mean_log1p_nrmse=("log1p_nrmse", "mean"),
        sd_log1p_nrmse=("log1p_nrmse", "std"), observations=("r2", "size"),
    ).reset_index()
    by_family = raw.groupby(["budget", "test_family", "representation"], sort=True).agg(
        mean_r2=("r2", "mean"), sd_r2=("r2", "std"),
        median_r2=("r2", "median"), q10_r2=("r2", lambda x: float(np.quantile(x, 0.10))),
        min_r2=("r2", "min"), median_nrmse=("nrmse", "median"),
        mean_log1p_nrmse=("log1p_nrmse", "mean"), replicates=("r2", "size"),
    ).reset_index()
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
        "replicates": n, "mean_log_error_difference": mean,
        "ci95_low": mean - half_width, "ci95_high": mean + half_width,
        "ci_excludes_zero": bool(mean - half_width > 0 or mean + half_width < 0),
        "positive_favors_focus": True,
        "replicate_win_fraction": float(np.mean(differences > 0)),
        "exact_sign_p": p_value,
    }


def one_comparison(raw, focus, comparator, budget, primary=False):
    subset = raw[
        (raw.budget == budget) & raw.representation.isin([focus, comparator])
    ]
    wide = subset.pivot(
        index=["replicate", "test_family"], columns="representation", values="log1p_nrmse"
    )
    differences = (wide[comparator] - wide[focus]).groupby("replicate").mean()
    result = {
        "budget": budget, "focus_representation": focus,
        "comparator_representation": comparator, "primary_comparison": primary,
        "focus_mean_log1p_nrmse": float(subset[subset.representation == focus].log1p_nrmse.mean()),
        "comparator_mean_log1p_nrmse": float(subset[subset.representation == comparator].log1p_nrmse.mean()),
        "focus_mean_r2": float(subset[subset.representation == focus].r2.mean()),
        "comparator_mean_r2": float(subset[subset.representation == comparator].r2.mean()),
        "focus_median_r2": float(subset[subset.representation == focus].r2.median()),
        "comparator_median_r2": float(subset[subset.representation == comparator].r2.median()),
    }
    result.update(interval_statistics(differences.to_numpy()))
    return result


def mechanism_comparisons(raw):
    specification = [
        ("sampled_lookahead", "initial", True),
        ("greedy", "initial", False),
        ("independent_search", "initial", False),
        ("sampled_lookahead", "greedy", False),
        ("independent_search", "sampled_lookahead", False),
        ("independent_search", "greedy", False),
        ("greedy", "supplied_area", False),
        ("sampled_lookahead", "supplied_area", False),
        ("independent_search", "supplied_area", False),
        ("supplied_area", "initial", False),
    ]
    return pd.DataFrame([
        one_comparison(raw, focus, comparator, budget, primary and budget == PRIMARY_BUDGET)
        for budget in BUDGETS
        for focus, comparator, primary in specification
    ])


def constructor_summary(search):
    return search.groupby(["condition", "output_expression"], sort=True).agg(
        runs=("condition", "size"),
        mean_output_robust_r2=("output_robust_r2", "mean"),
        min_output_robust_r2=("output_robust_r2", "min"),
        max_output_robust_r2=("output_robust_r2", "max"),
        exact_area_runs=("output_is_exact_area", "sum"),
        mean_accepted_moves=("accepted_moves", "mean"),
    ).reset_index()



def validate_parser_and_root():
    expressions = [
        "dot", "abs(cross)", "divide(dot,w2)", "abs_diff(u2,v2)",
        "multiply(add(dot,cross),sqrt_abs(w2))",
    ]
    for text in expressions:
        tree = parse_expression(text)
        if expression_name(tree) != text:
            raise RuntimeError(f"Expression round-trip failed: {text}")
    raw, targets = make_family_dataset("convex_radial", 0)
    first = dataset_dictionary(raw, targets)
    second = dataset_dictionary(permute_raw(raw, 1234567), targets)
    def root_features(data):
        base = np.sort(data["pairwise"], axis=1)
        values = np.sort(evaluate_expression(data["orbit_leaves"], INITIAL_TREE), axis=1)
        return np.column_stack((base, values))
    difference = float(np.max(np.abs(root_features(first) - root_features(second))))
    if difference > INVARIANCE_TOLERANCE:
        raise RuntimeError(f"Aligned root representation is not invariant: {difference}")
    return {"parser_round_trips": len(expressions), "aligned_root_max_difference": difference}


def validate_outputs(raw, proposals, search, invariance, replicates):
    expected_raw = replicates * len(FAMILIES) * len(REPRESENTATIONS) * len(BUDGETS)
    expected_proposals = replicates * len(FAMILIES) * len(SEARCH_CONDITIONS) * PROPOSAL_BUDGET
    expected_search = replicates * len(FAMILIES) * len(SEARCH_CONDITIONS)
    if len(raw) != expected_raw or len(proposals) != expected_proposals or len(search) != expected_search:
        raise RuntimeError(
            f"Unexpected output counts: raw={len(raw)}/{expected_raw}, "
            f"proposals={len(proposals)}/{expected_proposals}, search={len(search)}/{expected_search}"
        )
    if not np.isfinite(raw[["mse", "nrmse", "r2", "log1p_nrmse"]].to_numpy()).all():
        raise RuntimeError("Non-finite final result")
    keys = ["replicate", "test_family", "representation", "budget"]
    if raw.duplicated(keys).any():
        raise RuntimeError("Duplicate final result key")
    if proposals.duplicated(["condition", "replicate", "test_family", "evaluation_number"]).any():
        raise RuntimeError("Duplicate proposal evaluation key")
    counts = proposals.groupby(["condition", "replicate", "test_family"]).size()
    if not (counts == PROPOSAL_BUDGET).all():
        raise RuntimeError("A search did not consume exactly 500 proposals")
    valid_scores = proposals.loc[proposals.valid, "development_robust_r2"]
    if not np.isfinite(valid_scores).all():
        raise RuntimeError("Non-finite aligned development score")
    failed = invariance[invariance.required_invariant & ~invariance.passes]
    if not failed.empty:
        raise RuntimeError("Required invariance validation failed")


def validate_previous_reproduction(raw, pilot4f_dir):
    previous = pd.read_csv(pilot4f_dir / "pilot4f_raw_results.csv")
    previous = previous[
        (previous.environment == "permuted")
        & (
            ((previous.constructor_source == "initial") & (previous.aggregation == "fully_orbit_sorted"))
            | ((previous.constructor_source == "supplied_area") & (previous.aggregation == "fully_sorted"))
        )
    ].copy()
    previous["representation"] = previous.constructor_source
    current = raw[raw.representation.isin(["initial", "supplied_area"])].copy()
    merged = current.merge(
        previous, on=["replicate", "test_family", "representation", "budget"],
        suffixes=("_4g", "_4f"), validate="one_to_one",
    )
    if len(merged) != len(current):
        raise RuntimeError("Incomplete Pilot 4f reproduction join")
    if not (merged.expression_4g == merged.expression_4f).all():
        raise RuntimeError("Reference expression mismatch")
    metrics = ["mse", "nrmse", "r2", "log1p_nrmse"]
    maximum_absolute = 0.0
    maximum_scaled = 0.0
    for metric in metrics:
        difference = np.abs(merged[f"{metric}_4g"] - merged[f"{metric}_4f"])
        maximum_absolute = max(maximum_absolute, float(difference.max()))
        scaled = difference / np.maximum(1.0, np.abs(merged[f"{metric}_4f"]))
        maximum_scaled = max(maximum_scaled, float(scaled.max()))
    if maximum_scaled > 1e-10:
        raise RuntimeError(f"Pilot 4f reproduction failed: {maximum_scaled}")
    return {
        "comparison_rule": "absolute difference / max(1, absolute Pilot 4f value) <= 1e-10",
        "rows_checked": int(len(merged)),
        "max_absolute_metric_difference": maximum_absolute,
        "max_scaled_metric_difference": maximum_scaled,
    }



def save_figures(raw, overall, comparisons, search, output_dir):
    fig, ax = plt.subplots(figsize=(10, 6))
    for representation in REPRESENTATIONS:
        group = overall[overall.representation == representation].sort_values("budget")
        ax.plot(group.budget, group.mean_log1p_nrmse, marker="o", label=representation)
    ax.set_xscale("log")
    ax.set_xlabel("Final-task training configurations (log scale)")
    ax.set_ylabel("Mean log(1 + NRMSE); lower is better")
    ax.set_title("Pilot 4g — Aligned discovery and sample efficiency")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(output_dir / "pilot4g_sample_efficiency.png", dpi=180)
    plt.close(fig)

    selected = comparisons[
        (comparisons.budget == PRIMARY_BUDGET)
        & (comparisons.comparator_representation == "initial")
    ].copy().iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(selected))
    means = selected.mean_log_error_difference.to_numpy()
    errors = np.vstack((means - selected.ci95_low, selected.ci95_high - means))
    ax.errorbar(means, y, xerr=errors, fmt="o", capsize=4)
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.set_yticks(y, selected.focus_representation)
    ax.set_xlabel("Initial minus focus mean log error (positive favors focus)")
    ax.set_title("Pilot 4g — Discovery versus invariant initial dot at budget 200")
    fig.tight_layout()
    fig.savefig(output_dir / "pilot4g_primary_comparisons.png", dpi=180)
    plt.close(fig)

    subset = raw[raw.budget == PRIMARY_BUDGET]
    family = subset.groupby(["test_family", "representation"]).log1p_nrmse.mean().unstack()
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(FAMILIES))
    width = 0.16
    for index, representation in enumerate(REPRESENTATIONS):
        ax.bar(x + (index - 2) * width, family.loc[FAMILIES, representation], width, label=representation)
    ax.set_xticks(x, FAMILIES)
    ax.set_ylabel("Mean log(1 + NRMSE); lower is better")
    ax.set_title("Pilot 4g — Held-out-family performance at budget 200")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(output_dir / "pilot4g_family_transfer.png", dpi=180)
    plt.close(fig)

    activity = search.groupby("condition").agg(
        accepted_moves=("accepted_moves", "sum"),
        descendant_value_moves=("descendant_value_moves", "sum"),
        exact_area_selected=("output_is_exact_area", "sum"),
        exact_area_encountered=("area_encountered", "sum"),
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(activity))
    width = 0.20
    for index, column in enumerate(activity.columns):
        ax.bar(x + (index - 1.5) * width, activity[column], width, label=column)
    ax.set_xticks(x, activity.index)
    ax.set_ylabel("Count across search runs")
    ax.set_title("Pilot 4g — Search activity and exact-area encounter")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(output_dir / "pilot4g_search_activity.png", dpi=180)
    plt.close(fig)


def parse_args():
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--output-dir", type=Path, default=script_dir)
    parser.add_argument("--pilot4f-dir", type=Path, default=script_dir.parent / "generative_geometry_pilot4f")
    return parser.parse_args()


def main():
    started = time.time()
    args = parse_args()
    if args.replicates < 2:
        raise ValueError("At least two replicates are required for paired intervals")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    parser_checks = validate_parser_and_root()
    raw, proposals, search, invariance = run_experiment(args.replicates)
    validate_outputs(raw, proposals, search, invariance, args.replicates)
    reproduction = validate_previous_reproduction(raw, args.pilot4f_dir)
    overall, by_family = make_summaries(raw)
    comparisons = mechanism_comparisons(raw)
    constructors = constructor_summary(search)
    accepted = proposals[proposals.accepted].copy()

    raw.to_csv(args.output_dir / "pilot4g_raw_results.csv", index=False)
    proposals.to_csv(args.output_dir / "pilot4g_proposal_history.csv", index=False)
    accepted.to_csv(args.output_dir / "pilot4g_accepted_moves.csv", index=False)
    search.to_csv(args.output_dir / "pilot4g_search_summary.csv", index=False)
    constructors.to_csv(args.output_dir / "pilot4g_constructor_summary.csv", index=False)
    overall.to_csv(args.output_dir / "pilot4g_summary_overall.csv", index=False)
    by_family.to_csv(args.output_dir / "pilot4g_summary_by_family.csv", index=False)
    comparisons.to_csv(args.output_dir / "pilot4g_paired_comparisons.csv", index=False)
    invariance.to_csv(args.output_dir / "pilot4g_invariance_checks.csv", index=False)
    save_figures(raw, overall, comparisons, search, args.output_dir)

    metadata = {
        "pilot": "4g",
        "replicates": args.replicates,
        "families": FAMILIES,
        "search_conditions": SEARCH_CONDITIONS,
        "representations": REPRESENTATIONS,
        "proposal_budget_per_run": PROPOSAL_BUDGET,
        "search_runs": len(search),
        "proposal_evaluations": len(proposals),
        "final_evaluations": len(raw),
        "development_feature_count": 135,
        "searched_final_feature_count": 135,
        "supplied_final_feature_count": 35,
        "development_targets": DEVELOPMENT_TARGETS,
        "final_target": FINAL_TARGET,
        "development_budgets": DEVELOPMENT_BUDGETS,
        "final_budgets": BUDGETS,
        "primary_comparison": "sampled_lookahead versus initial at budget 200",
        "positive_difference": "comparator log error minus focus log error; positive favors focus",
        "new_stability_or_ratio_guard": False,
        "parser_checks": parser_checks,
        "required_invariance_checks": int(invariance.required_invariant.sum()),
        "maximum_required_invariance_discrepancy": float(
            invariance.loc[invariance.required_invariant, "max_absolute_difference"].max()
        ),
        "pilot4f_reproduction": reproduction,
        "runtime_seconds": time.time() - started,
        "software": {
            "python": platform.python_version(), "numpy": np.__version__,
            "pandas": pd.__version__, "scipy": scipy.__version__,
            "sklearn": sklearn.__version__, "platform": platform.platform(),
        },
    }
    with open(args.output_dir / "pilot4g_metadata.json", "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
