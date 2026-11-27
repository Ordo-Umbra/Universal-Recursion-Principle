# Generative Geometry — Pilot 4 Report

## Higher-Order Relational Accessibility

### Executive result

Pilot 4 produced a strong positive result for the narrow hypothesis specified before testing:

> Generic higher-order relational features can make a downstream geometric property substantially more accessible to a fixed linear learner under finite training-sample budgets, including when evaluation occurs on an unseen geometric family.

At the primary budget of 200 training configurations, the higher-order representation achieved mean held-out-family \(R^2=0.9675\) for convex-hull area. Pairwise distances achieved \(R^2=-0.6586\). The paired difference was 1.6261, with a 95% interval of [1.5454, 1.7068].

Higher-order features also outperformed raw coordinates, raw quadratic features, random quadratic features, and shuffled triangle areas. The advantage was present at every tested budget from 25 to 1000 and in every held-out family.

The negative-control task behaved as expected: higher-order features did **not** improve hull-perimeter prediction over pairwise distances. This supports task-specific representational usefulness rather than indiscriminate improvement from additional features.

The result does **not** establish autonomous relational discovery, new information, new physical degrees of freedom, or recursive generation. Triangle-area constructors were supplied by the researcher. Pilot 4 demonstrates the usefulness of a supplied higher-order representation, not the system’s independent invention of that representation.

## Formal interpretation

The experiment concerns accessibility relative to a representation and model class.

Given configuration \(x\), representation \(\phi_j(x)\), learner \(L\), task \(q\), and sample budget \(B\), performance is evaluated on an unseen environment family. Effective representational expansion is indicated when \(\phi_{j+1}\) enables higher held-out performance or reaches a given performance level with fewer training observations than \(\phi_j\), under the specified controls.

This is weaker than information creation. Any deterministic geometric property is implicitly encoded in sufficiently complete observations. The experimental question is whether relational construction changes what the learner can efficiently extract and reuse.

## Experimental design

### Configurations

Each observation contains six two-dimensional points. Configurations are centered, normalized by root-mean-square radius, and randomly rotated. Point order follows angular order before rotation.

Four environment families were generated:

- **convex_radial:** all six points are hull vertices;
- **interior_points:** four convex outer points and two interior points;
- **irregular_radial:** angularly ordered points with broadly varying radii;
- **elongated:** irregular configurations subjected to strong vertical compression before normalization.

Evaluation used leave-one-family-out transfer. Models trained on three families were tested on the unseen fourth.

### Representations

| Representation | Features | Dimensionality |
|---|---|---:|
| raw | centered, normalized, rotated coordinates | 12 |
| raw_quadratic | raw coordinates and all quadratic monomials | 90 |
| pairwise | all pairwise distances | 15 |
| higher_order | pairwise distances and all unsigned triangle areas | 35 |
| random_quadratic | pairwise distances and 20 label-independent random quadratic projections | 35 |
| shuffled_higher_order | pairwise distances and area columns permuted across configurations | 35 |

The random and shuffled controls have the same dimensionality as the higher-order representation. Raw quadratic features provide a stronger generic baseline with greater dimensionality.

### Tasks

1. **Hull area — primary task.** The primary comparison was higher-order versus pairwise features at budget 200.
2. **Hull perimeter — negative control.** Pairwise distances already provide potentially relevant edge lengths.
3. **Compactness — exploratory.** Defined as \(4\pi A/P^2\), requiring a nonlinear global combination of area and perimeter.

Hull area, perimeter, and compactness were not supplied as input features.

### Learner and evaluation

All representations used the same ridge-regression procedure with fixed regularization `1e-3`. Feature and target standardization were fitted on training data only.

Twenty replicates were used. Each family/replicate dataset contained 1,200 training-pool and 800 test configurations. Nested training budgets were 25, 50, 100, 200, 500, and 1000.

The full experiment contains 8,640 model evaluations. Paired intervals were calculated over 20 replicate means, each averaging the four held-out-family folds, rather than treating correlated folds as independent replicates.

## Validation

The implementation passed checks for:

- expected feature dimensions;
- finite model results;
- correct hull structure in the convex and interior families;
- exact agreement between convex hull area and the relevant triangle-fan sum for convex angularly ordered configurations;
- expected result-row count;
- deterministic seeding.

The triangle-fan identity is important for interpretation: it verifies an explicit mechanism through which local higher-order areas can make global area linearly accessible in convex configurations. It does not by itself explain performance in configurations containing interior points or irregular hull membership.

## Primary results at budget 200

| Representation | Mean held-out-family \(R^2\) | Mean NRMSE |
|---|---:|---:|
| higher_order | 0.9675 | 0.1739 |
| raw_quadratic | 0.3449 | 0.7907 |
| random_quadratic | -0.2274 | 1.0286 |
| shuffled_higher_order | -0.3046 | 1.0582 |
| pairwise | -0.6586 | 1.1860 |
| raw | -3.1906 | 1.8799 |

Negative \(R^2\) indicates performance worse than predicting the test-target mean. Large positive paired differences are possible because several baselines have negative \(R^2\).

### Paired higher-order-minus-control differences

| Comparator | Mean \(R^2\) difference | 95% interval | Replicate win fraction |
|---|---:|---:|---:|
| raw | 4.1581 | [4.0171, 4.2990] | 1.00 |
| raw_quadratic | 0.6226 | [0.5914, 0.6538] | 1.00 |
| pairwise | 1.6261 | [1.5454, 1.7068] | 1.00 |
| random_quadratic | 1.1948 | [1.1149, 1.2747] | 1.00 |
| shuffled_higher_order | 1.2721 | [1.1793, 1.3649] | 1.00 |

All primary paired intervals exclude zero in the positive direction. Secondary comparisons are exploratory and unadjusted for multiple comparisons.

## Sample efficiency

Mean held-out-family \(R^2\) for hull area:

| Budget | Higher order | Raw quadratic | Pairwise | Random quadratic | Shuffled higher order |
|---:|---:|---:|---:|---:|---:|
| 25 | 0.8829 | -1.8499 | -2.4289 | -4.3004 | -6.6863 |
| 50 | 0.9251 | -1.1752 | -0.9601 | -2.1039 | -2.0134 |
| 100 | 0.9547 | -0.1779 | -0.7525 | -0.5300 | -0.5471 |
| 200 | 0.9675 | 0.3449 | -0.6586 | -0.2274 | -0.3046 |
| 500 | 0.9743 | 0.4455 | -0.5985 | -0.1363 | -0.1457 |
| 1000 | 0.9763 | 0.4762 | -0.5871 | -0.0773 | -0.1007 |

Higher-order features at budget 25 outperform every non-raw control even at budget 1000 in this fixed-learner setting. Every paired higher-order-minus-control interval for hull area excluded zero in the positive direction at every tested budget.

This is strong evidence of **sample-efficient accessibility for this learner and task distribution**. It is not evidence that more expressive nonlinear learners could not recover the same information from raw coordinates or pairwise distances.

## Transfer to unseen families

Hull-area \(R^2\) at budget 200:

| Unseen family | Higher order | Raw quadratic | Pairwise | Random quadratic | Shuffled higher order |
|---|---:|---:|---:|---:|---:|
| convex_radial | 0.9832 | 0.2962 | -0.4989 | 0.1522 | 0.2923 |
| interior_points | 0.9763 | 0.6505 | 0.3779 | 0.4399 | 0.3997 |
| irregular_radial | 0.9494 | 0.4616 | 0.4100 | 0.4317 | 0.2695 |
| elongated | 0.9610 | -0.0288 | -2.9235 | -1.9333 | -2.1801 |

The higher-order representation transferred to every held-out family. Its lowest family mean at the primary budget was 0.9494.

At budget 1000, its family means ranged from 0.9619 to 0.9818. The advantage is therefore not explained by success on only one geometric configuration type.

## Negative control: hull perimeter

At budget 200:

- higher-order \(R^2\): 0.3223;
- pairwise \(R^2\): 0.4585;
- random-quadratic \(R^2\): 0.4858.

The paired higher-order-minus-pairwise difference was -0.1362, with a 95% interval of [-0.1862, -0.0862]. At budget 1000, the corresponding values were 0.4590 for higher order and 0.5435 for pairwise.

Adding triangle areas therefore reduced perimeter performance relative to pairwise features. This is consistent with task-specific usefulness and shows that the extra features can impose a statistical cost when they are not aligned with the target.

## Exploratory compactness results

At budget 200:

- higher-order \(R^2\): 0.7930;
- raw-quadratic \(R^2\): 0.5633;
- pairwise \(R^2\): -1.3996;
- random-quadratic \(R^2\): -0.8259;
- shuffled-higher-order \(R^2\): -0.6126.

The higher-order advantage persisted in the aggregate at budget 1000. Raw quadratic features nevertheless outperformed higher-order features on the convex-family compactness fold at budget 200 (0.7099 versus 0.6337), so the exploratory result is not uniform across every family and representation.

## What the controls establish

### Pairwise control

The advantage over pairwise distances shows that adding higher-order area features changes linear accessibility. It does not show that area information was absent from pairwise distances: distances determine triangle areas through nonlinear relationships.

### Random quadratic control

The advantage over equally dimensioned random quadratic features supports a specific benefit of geometrically aligned higher-order construction, rather than an arbitrary benefit from adding nonlinear features.

### Shuffled-area control

The advantage over shuffled areas shows that preserving the marginal distribution of area values is insufficient. Their correspondence to the originating configuration matters.

### Raw quadratic control

Raw quadratic features did not match higher-order performance in the mixed-family, fixed-ridge setting. This shows that simply supplying generic quadratic monomials was insufficient for comparable transfer.

It does not prove that raw observations lack the necessary information. Raw quadratic features can express signed coordinate cross-products, but they do not directly provide unsigned local areas, hull selection, or the aligned relational decomposition. More expressive or nonlinear raw-data models remain necessary stronger baselines.

## Scope of the positive claim

The supported claim is:

> In this synthetic six-point setting, supplying aligned triangle-area relations made hull area and, exploratory, compactness substantially more accessible to a fixed ridge learner across unseen geometric families and severe sample constraints. The advantage was specific to geometrically aligned features and was not reproduced by random or shuffled controls. The benefit did not generalize indiscriminately to perimeter prediction.

The following claims remain untested:

- autonomous discovery of triangle-area constructors;
- endogenous selection of useful features without researcher-specified feature types;
- equivalence to an expansion of information-theoretic degrees of freedom;
- superiority to expressive nonlinear models given matched computation;
- recursive use of generated features to construct further features;
- operation in biological, cognitive, physical, or social systems.

## Recommended next steps

1. **Add expressive nonlinear raw and pairwise baselines.** These will bound what can be learned from the original observations when the learner is not restricted to ridge regression.
2. **Account for construction and computation costs.** Compare sample efficiency, feature dimensionality, construction cost, memory, training cost, and inference cost separately.
3. **Strengthen task separation.** Use development tasks for generic feature selection and reserve structurally different final tasks, avoiding final targets closely aligned with a supplied feature type.
4. **Test autonomous construction.** Allow the system to select and compose generic operators without being told that triangle area is the desired higher-order distinction.
5. **Only then test recursion.** Ablate earlier generated features to determine whether they causally enable later feature construction, rather than merely preceding it chronologically.

## Reproduction

Run:

```bash
python3 generative_geometry_pilot4.py --replicates 20 --output-dir ./pilot4_output
```

A two-replicate smoke run is available with `--replicates 2`. All random seeds are deterministic. The protocol was fixed before the full experiment and is included separately.

## Files

- [Pre-run protocol](Pilot_4_Protocol.md)
- [Experiment script](generative_geometry_pilot4.py)
- [Raw model evaluations](pilot4_raw_results.csv)
- [Overall summaries](pilot4_summary_overall.csv)
- [Family summaries](pilot4_summary_by_family.csv)
- [Paired comparisons](pilot4_paired_comparisons.csv)
- [Sample-efficiency figure](pilot4_hull_area_sample_efficiency.png)
- [Task-performance figure](pilot4_task_performance.png)
- [Family-transfer figure](pilot4_hull_area_by_family.png)
- [Run metadata](pilot4_metadata.json)
