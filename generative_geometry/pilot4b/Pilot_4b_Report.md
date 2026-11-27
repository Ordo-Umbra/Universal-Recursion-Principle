# Generative Geometry — Pilot 4b Report

## Constructor Discovery Within a Finite Grammar

### Executive result

Pilot 4b is a **partial positive result with an important stability failure**.

A usefulness-guided search over 80 generic constructor expressions repeatedly discovered cross-product-based structure without receiving hull-area labels during selection. Exact `abs(cross)` area rediscovery occurred in 39 of 80 independent discovery runs. Runs without direct area rediscovery still achieved mean held-out-family hull-area \(R^2=0.8185\) at the primary budget, principally through area-related alternatives such as signed and square-root cross products.

At budget 200, discovered constructors achieved mean \(R^2=0.8939\), compared with \(-0.6440\) for pairwise distances. The paired improvement was 1.5379 with a 95% interval of [1.4768, 1.5990]. Performance was positive in every unseen family.

However:

- The supplied area representation remained superior, achieving \(R^2=0.9684\).
- The pre-specified mean-based comparison against random constructors did **not** yield an interval excluding zero because random constructor performance was extremely heavy-tailed.
- Discovery was better than random retention in every replicate, and robust descriptive analyses strongly favored discovery, but this does not change the pre-specified interval result.
- A frequently selected self-ratio constructor caused catastrophic extrapolation at small final-training budgets.
- Only seven distinct expressions were retained across 160 selections, and almost all were cross-product-based. The experiment therefore shows concentrated rediscovery and variation around one relational family, not diverse conceptual invention.

The system demonstrated **usefulness-guided constructor discovery within a supplied grammar**, together with a clear failure of robust integration. It did not demonstrate recursion, open-ended discovery, or expansion beyond the grammar.

## Experimental design

### Constructor grammar

For each point triple, the system received five generic local invariants:

- `dot`;
- `cross`;
- squared edge lengths `u2`, `v2`, and `w2`.

Eighty candidates were generated systematically using generic unary and binary operations. The triangle-area constructor was not supplied directly, but was constructible as `abs(cross)` up to an irrelevant constant factor.

Each constructor produced a 20-component block, one value for each unordered point triple.

### Development guidance

Constructor selection used only:

- hull perimeter;
- compactness;
- hull vertex count.

Selection used 400 fitting configurations and 200 separate validation configurations from the three training families. Hull-area labels were excluded throughout constructor discovery.

Two constructors were retained greedily according to mean development-validation \(R^2\).

### Held-out evaluation

After constructor selection, the system was trained on hull area using configurations from the three training families and tested on the unseen fourth family.

Final representations were:

| Representation | Dimensionality |
|---|---:|
| pairwise | 15 |
| discovered | 55 |
| random_constructors | 55 |
| supplied_area | 35 |
| raw_quadratic | 90 |

Twenty replicates, four held-out-family folds, and six nested final-task budgets were used. The experiment contains 2,400 final model evaluations and 160 constructor-selection records.

## Primary results at budget 200

| Representation | Mean held-out-family \(R^2\) | Median \(R^2\) |
|---|---:|---:|
| discovered | 0.8939 | 0.9224 |
| supplied_area | 0.9684 | 0.9723 |
| raw_quadratic | 0.3034 | 0.3493 |
| pairwise | -0.6440 | 0.1148 |
| random_constructors | -1313.9468 | 0.1777 |

The random-constructor mean is dominated by rare, enormous negative outcomes. Its median is more representative of typical random performance, but neither statistic alone describes the full distribution.

### Paired comparisons

Positive differences favor discovered constructors.

| Comparator | Mean \(R^2\) difference | 95% interval | Replicate win fraction |
|---|---:|---:|---:|
| pairwise | 1.5379 | [1.4768, 1.5990] | 1.00 |
| raw_quadratic | 0.5905 | [0.5276, 0.6534] | 1.00 |
| supplied_area | -0.0745 | [-0.0967, -0.0523] | 0.10 |
| random_constructors | 1314.8407 | [-660.4891, 3290.1705] | 1.00 |

The primary discovered-versus-pairwise criterion passed. The pre-specified discovered-versus-random mean-interval criterion did not.

As an explicitly exploratory robustness analysis, discovery had a higher replicate-averaged \(R^2\) than random retention in 20 of 20 replicates. A two-sided exact sign test gives \(p\approx1.91\times10^{-6}\). This supports a robust direction of advantage, but it is a post hoc analysis and does not rescue the unmet pre-specified mean-interval criterion.

## Transfer to unseen families

Mean discovered-constructor hull-area \(R^2\) at budget 200:

| Unseen family | Discovered | Supplied area | Pairwise |
|---|---:|---:|---:|
| convex_radial | 0.9335 | 0.9836 | -0.5917 |
| interior_points | 0.9050 | 0.9767 | 0.3843 |
| irregular_radial | 0.8638 | 0.9479 | 0.4213 |
| elongated | 0.8734 | 0.9655 | -2.7899 |

The discovered representation transferred to all four families. Supplied area performed better in each family.

## What the system discovered

Across 80 discovery runs, two constructors were retained per run, producing 160 selection records.

| Expression | Retention count | Interpretation |
|---|---:|---|
| `divide(cross,cross)` | 77 | Cross-product sign, up to numerical stabilization |
| `abs(cross)` | 39 | Direct area rediscovery |
| `sqrt_abs(cross)` | 24 | Square root of local area magnitude |
| `cross` | 16 | Signed local area, up to a factor |
| `square(u2)` | 2 | Fourth-power edge-length scale |
| `add(cross,v2)` | 1 | Mixed signed-area/length expression |
| `add(cross,u2)` | 1 | Mixed signed-area/length expression |

Exact area appeared in 39 of 80 runs. Only seven unique expressions were retained, and only two selection records were entirely cross-free.

Under the pre-specified expression analysis, 121 selections were classified as non-area-linear. This should **not** be read as 121 independent conceptual discoveries. Most were signed, transformed, or self-ratio versions of the cross product.

## Direct rediscovery versus alternative pathways

At budget 200:

| Discovery runs | Mean hull-area \(R^2\) | Median \(R^2\) | Count |
|---|---:|---:|---:|
| Direct area selected | 0.9733 | 0.9726 | 39 |
| Direct area not selected | 0.8185 | 0.8359 | 41 |

Direct area rediscovery essentially recovered supplied-area performance. Runs without direct area still achieved useful transfer, but with lower and more variable performance.

The successful alternatives were mainly:

- `sqrt_abs(cross)`;
- signed `cross`;
- combinations of those with the cross-sign self-ratio.

This is evidence for **alternative area-related construction pathways**, not yet evidence for an entirely independent way of representing geometric extent.

## The integration failure: development usefulness is not robustness

The most frequently retained constructor was:

```text
divide(cross,cross)
```

This is approximately the sign of the cross product. It was useful for development tasks but created severe instability in final-task learning under small samples and distribution shift.

### Discovered-constructor performance across budgets

| Budget | Mean \(R^2\) | Median \(R^2\) | Supplied-area mean \(R^2\) |
|---:|---:|---:|---:|
| 25 | -2.25×10¹³ | -6.57×10¹¹ | 0.9018 |
| 50 | -1.00×10¹³ | -0.5137 | 0.9283 |
| 100 | -1.68×10¹⁰ | 0.8504 | 0.9588 |
| 200 | 0.8939 | 0.9224 | 0.9684 |
| 500 | 0.9188 | 0.9407 | 0.9730 |
| 1000 | 0.9233 | 0.9415 | 0.9747 |

All ten most catastrophic discovered-model results involved the self-ratio constructor. This pattern is consistent with near-constant or low-variance training features becoming dangerously rescaled when held-out configurations occupy values not represented in a small training subset. The experiment establishes the instability; the exact numerical mechanism warrants direct diagnosis in a follow-up.

At budget 100, the median discovered result is already good while the mean remains catastrophic. By budget 200, the mean has stabilized. This creates a clear distinction between:

- a constructor being useful on development tasks;
- a constructor being statistically safe to integrate;
- a constructor remaining useful under distribution shift;
- a constructor supporting continued development under finite capacity.

That distinction may be more valuable for the broader framework than the positive area result alone.

## What Pilot 4b supports

A defensible conclusion is:

> Within a supplied finite grammar, multi-task developmental guidance repeatedly identified cross-product-based constructors, including exact local area in nearly half of discovery runs. These constructors could transfer to held-out hull-area prediction in unseen geometric families, and area-related alternatives provided useful performance when exact area was not selected. However, supplied area remained superior, random-control comparisons were heavy-tailed, and a frequently retained self-ratio constructor caused severe small-sample instability. Constructor discovery therefore requires explicit robustness and integration criteria, not development-task usefulness alone.

The experiment does not establish:

- discovery outside the 80-candidate grammar;
- invention of the underlying geometric primitives;
- conceptual novelty of syntactically distinct expressions;
- recursive reuse of retained constructors;
- open-ended development;
- superiority under equalized total computation;
- operation beyond this synthetic geometric setting.

## Recommended next stage: stability-aware constructor discovery

Before Pilot 5, a focused Pilot 4c should address the failure directly.

### 1. Label-free constructor validity checks

Exclude or flag constructors that are constant, near-constant, numerically extreme, trivially self-referential, or poorly conditioned on reference configurations. These checks need not use task labels.

### 2. Robust development evaluation

Evaluate candidates across multiple training-family folds and use median or worst-case validation performance, rather than one pooled validation score.

### 3. Stability-aware retention

Penalize constructor blocks whose scaling or output distribution changes sharply across families. Measure the cost of retaining each block and its effect on existing useful constructors.

### 4. Pre-specified robust final statistics

Use median performance, log error, paired win rates, or a pre-specified robust estimator alongside mean \(R^2\). Random grammars containing pathological expressions require heavy-tailed analysis.

### 5. Alternative-constructor analysis

Distinguish direct rediscovery, algebraic equivalence, functional equivalence, and genuinely different task pathways. Syntax alone is not novelty.

Only after stable autonomous discovery should Pilot 5 allow retained constructors to become primitives for subsequent construction. Otherwise recursion may amplify instability rather than development.

## Reproduction

Run:

```bash
python3 generative_geometry_pilot4b.py --replicates 20 --output-dir ./pilot4b_output
```

The two-replicate smoke run can be reproduced with `--replicates 2`. All seeds are deterministic. Figures use medians for readability; the sample-efficiency figure begins at budget 100 because catastrophic low-budget values obscure the later curves. Unmodified means and all raw values are retained in the CSV files.

## Files

- [Pre-run protocol](Pilot_4b_Protocol.md)
- [Experiment script](generative_geometry_pilot4b.py)
- [Raw final evaluations](pilot4b_raw_results.csv)
- [Constructor selection history](pilot4b_selection_history.csv)
- [Constructor summary](pilot4b_constructor_summary.csv)
- [Candidate catalogue](pilot4b_candidate_catalogue.csv)
- [Overall summaries](pilot4b_summary_overall.csv)
- [Family summaries](pilot4b_summary_by_family.csv)
- [Paired comparisons](pilot4b_paired_comparisons.csv)
- [Sample-efficiency figure](pilot4b_sample_efficiency.png)
- [Constructor-frequency figure](pilot4b_constructor_counts.png)
- [Family-transfer figure](pilot4b_family_transfer.png)
- [Run metadata](pilot4b_metadata.json)
