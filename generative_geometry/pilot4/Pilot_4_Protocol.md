# Generative Geometry — Pilot 4 Protocol

## Status

Protocol fixed before the full experiment. Pilot 4 tests representation-dependent accessibility. It does not test the creation of information absent from the observations, new physical degrees of freedom, or recursive generation.

## Formal question

Given identical underlying geometric observations, a fixed linear learner, and a finite training-sample budget, can generic higher-order relational features improve held-out task performance relative to pairwise, raw, generic quadratic, random-feature, and shuffled-feature controls?

Let \(x\) denote a six-point geometric configuration. Representations include:

- \(\phi_{\mathrm{raw}}(x)\): centered, scale-normalized coordinates;
- \(\phi_{\mathrm{pair}}(x)\): all 15 pairwise distances;
- \(\phi_{\mathrm{higher}}(x)\): pairwise distances plus all 20 unsigned triangle areas;
- \(Q(\phi_{\mathrm{raw}}(x))\): raw coordinates plus all 90 linear and quadratic monomials;
- \(\phi_{\mathrm{random}}(x)\): pairwise distances plus 20 label-independent random quadratic features;
- \(\phi_{\mathrm{shuffled}}(x)\): pairwise distances plus triangle-area columns whose correspondence to configurations has been permuted.

The experiment asks whether a distinction is accessible to a specified model class under finite resources. It does not ask whether the distinction was mathematically absent from the original observations.

## Geometric environments

Each configuration contains six two-dimensional points. Configurations are centered, normalized by root-mean-square radius, and randomly rotated. Point order follows angular order before rotation.

Four environment families are used:

1. **convex_radial** — radial configurations accepted only when all six points are hull vertices;
2. **interior_points** — four convex outer points and two interior points;
3. **irregular_radial** — sorted angular samples with broadly varying radii;
4. **elongated** — irregular radial configurations subjected to strong vertical compression before normalization.

Evaluation uses leave-one-family-out transfer: train on three families and test on the unseen fourth.

## Downstream tasks

All targets are invariant to translation, rotation, and global scale after normalization.

### Primary task: convex-hull area

The primary comparison is higher-order versus pairwise representation at a training budget of 200 configurations, evaluated by held-out-family \(R^2\).

Hull area is not supplied as a feature. Local triangle areas are generic higher-order constructions. For convex angularly ordered polygons, subsets of these areas can express a triangle-fan decomposition. Pairwise distances contain the same underlying geometric information but do not make area linearly explicit.

### Negative-control task: convex-hull perimeter

Pairwise distances already provide local edge lengths. Higher-order area features are not expected to provide a general advantage. This task tests whether the method merely improves every target indiscriminately.

### Exploratory task: compactness

Compactness is \(4\pi A/P^2\), where \(A\) is hull area and \(P\) is hull perimeter. It requires a nonlinear global combination and was not used to design or select features.

## Learner and budgets

All representations are evaluated with the same fixed ridge-regression procedure. Features and targets are standardized using training data only. The regularization parameter is fixed at `1e-3`; test families are not used for tuning.

Nested training budgets:

- 25
- 50
- 100
- 200
- 500
- 1000 configurations

Each family/replicate dataset contains 1,200 training-pool and 800 test configurations. Twenty independent replicates are used. Training subsets are nested and shared across representations and tasks.

## Primary measures

- Held-out-family \(R^2\);
- normalized root mean squared error;
- sample-efficiency curves;
- paired \(R^2\) differences across replicates and folds;
- paired 95% t intervals for the primary comparison;
- representation dimensionality.

## Interpretation rules fixed before testing

### Support for higher-order representational usefulness

The primary result supports usefulness if higher-order features improve held-out hull-area performance over pairwise features, with a positive paired interval at budget 200, and show advantages over random and shuffled controls.

### No unique information or absolute capability expansion

If raw quadratic features match or exceed higher-order features, the result demonstrates that the raw observations already contain sufficient information and that a generic representation can expose it. Any higher-order advantage must then be interpreted in terms of accessibility, dimensionality, sample efficiency, or computational convenience—not unique information.

### No specific relational advantage

If random quadratic features match higher-order features, the result does not support a specific advantage for geometrically aligned relational construction.

### No higher-order benefit

If higher-order features do not improve hull-area performance over pairwise features, the primary hypothesis is unsupported in this model.

### No transfer

If advantages do not survive leave-one-family-out evaluation, they do not establish transfer to unseen structural families.

### Negative-control interpretation

A higher-order advantage on hull area without a corresponding advantage on perimeter would support task-specific representational usefulness. Improvement on every task, including perimeter, would require scrutiny for generic capacity or optimization effects.

## Limitations

- The experiment uses six-point synthetic configurations and one fixed linear learner.
- Feature-construction and training-computation costs are not yet equalized; this is a statistical-accessibility test, not a complete computational-cost comparison.
- Raw quadratic features have greater dimensionality than the higher-order representation.
- Secondary tasks and budgets are exploratory; no familywise multiple-comparison procedure is applied.
- Positive results would not establish open-ended learning, recursive generation, or emergence in physical, biological, or cognitive systems.
