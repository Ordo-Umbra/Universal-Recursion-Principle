# Generative Geometry — Pilot 4e Protocol

## Descendant Value, Neutral Drift, and Symmetry-Diverse Persistence

### Status

Protocol fixed on 2026-11-23 before implementation, smoke testing, or the full experiment. Numerical results must not be used to revise the hypotheses, search rules, descriptors, proposal accounting, primary comparison, or interpretation criteria in this document.

## Research question

Can parent-chained constructor search cross an unrewarded intermediate more effectively through symmetry-diverse persistence, bounded neutral drift, or sampled descendant lookahead than through fixed-budget greedy improvement?

The primary comparison is **diversity archive versus greedy search**. Sampled lookahead is a foresight reference condition, neutral drift tests tolerance without structural diversity, and independent and unscaffolded search test whether the same result can be obtained without developmental parent chaining.

The experiment concerns finite-grammar search under a common evaluation budget. It does not test open-ended invention or establish that biological or cognitive systems use explicit lookahead.

## Environment and data

Pilot 4e uses only the permuted environment from Pilot 4d. Six point labels are independently permuted within every configuration after normalization, rotation, and target computation. The underlying configurations and targets are identical to the ordered Pilot 4c/4d data, but features are computed after permutation.

The four environment families, targets, 1,200-configuration training pools, 800-configuration test sets, and leave-one-family-out evaluation are unchanged.

Development targets:

- hull perimeter;
- compactness;
- hull vertex count.

Held-out final target:

- convex-hull area.

Hull-area labels are excluded from search, gates, archive descriptors, and selection. Compactness remains acknowledged area-related development guidance.

## Grammar and initial constructor

The grammar is identical to Pilot 4c/4d:

- leaves `dot`, `cross`, `u2`, `v2`, `w2`;
- unary operations `abs`, `square`, `sqrt_abs`;
- binary operations `multiply`, `divide`, `add`, `abs_diff`;
- maximum expression depth 2;
- division \(a/(|b|+10^{-8})\).

Every search starts from `dot`. Expressions produce 20 triple-level values. The exact-area reference is `abs(cross)`, which is not a direct mutation of `dot`.

## Gates and robust development score

Numerical validity, family near-constancy, small-sample near-constancy, and family scale-collapse gates are identical to Pilot 4d.

For each final fold, three internal family-held-out development folds use fitting budgets 40 and 80 and 80 validation configurations. The learner is fixed ridge regression with training-only feature and target standardization. Development \(R^2\) values are clipped to \([-1,1]\), and the robust score \(U(E)\) is the median of 18 task/fold/budget values.

The common initial `dot` score is computed once per run and is not charged against the 500-proposal budget. Every subsequent proposed expression counts as one evaluation, including duplicates, tabu-rejected proposals, gate failures, children, and grandchildren. A duplicate or gate failure consumes its slot without receiving a free cached development score.

## Label-free symmetry descriptors

For anchored vectors \((u,v,w)\), endpoint exchange uses the exact transformation:

\[
(u,v,w)\mapsto(v,u,-w).
\]

Expressions are classified by numerical evaluation on development reference configurations using pre-specified tolerances:

1. **symmetric_nonnegative:** invariant under endpoint exchange and nonnegative within tolerance;
2. **symmetric_signed:** invariant under endpoint exchange and taking both signs;
3. **antisymmetric:** changes sign under endpoint exchange;
4. **asymmetric_other:** everything else.

Symmetry classification uses no target labels and does not name particular expressions. The archive has at most one incumbent per class.

Homogeneity is logged as a diagnostic only. Coordinate scaling by \(\alpha\) multiplies all five primitive leaves by \(\alpha^2\). Entrywise output ratios are used to estimate a median degree and its dispersion where values are numerically nonzero. Homogeneity does not affect archive membership or selection.

## Best-output rule

Every method retains the valid expression with the highest robust development score encountered during its search, including the initial root. This archived output is used for final held-out evaluation.

The output rule prevents a neutral random walker or exploratory parent from being evaluated solely by its final current expression. Lexicographic ordering resolves exact score ties. Output selection never uses hull-area labels or final test data.

## Fixed-budget search conditions

Every condition receives exactly 500 proposal evaluations per replicate/final-fold run. Search does not stop early. All conditions use deterministic condition-specific random seeds and the same development configurations within a run.

### 1. Greedy

At each proposal:

1. sample one mutation uniformly from the current parent's neighborhood;
2. apply gates and, if valid, compute \(U\);
3. replace the current parent only if
   \[
   U(E')>U(E_{\mathrm{current}})+10^{-4}.
   \]

This is a stochastic fixed-budget greedy baseline, not an exact replication of Pilot 4d's exhaustive, early-stopping search.

### 2. Neutral drift

The root is initially marked visited. At each proposal:

1. sample one mutation uniformly from the current parent's neighborhood;
2. if the expression was previously proposed in this run, reject it as tabu and consume the evaluation;
3. otherwise mark it visited, apply gates, and compute \(U\) if valid;
4. accept it as the next current parent only if both
   \[
   U(E')\geq U(E_{\mathrm{current}})-0.02
   \]
   and
   \[
   U(E')\geq U(E_{\mathrm{best}})-0.05.
   \]

The first rule bounds local loss; the second bounds cumulative decline relative to the best expression encountered. The best-output archive remains separate from the current parent.

### 3. Diversity archive

The archive contains at most four slots, one per symmetry class. Initially, `dot` occupies its class slot and the others are empty.

At each proposal:

1. select an active parent class round-robin in fixed class order;
2. sample one mutation uniformly from that parent's neighborhood;
3. gate and score the child and determine its symmetry class;
4. if the child's class slot is empty, install the first valid child;
5. otherwise replace the class incumbent only if
   \[
   U(E')>U(E_{\mathrm{class\ incumbent}})+10^{-4}.
   \]

Newly occupied classes join the round-robin schedule. Archive diversity concerns alternative parents during search; it does not add multiple constructor blocks to the final representation.

### 4. Sampled lookahead

The current parent begins at `dot`. Each round samples up to five distinct children without replacement from the current parent's neighborhood.

For each child:

1. evaluate the child, consuming one proposal;
2. if valid, sample four grandchildren uniformly with replacement from that child's neighborhood and evaluate each;
3. define the child's sampled descendant value as
   \[
   V(c)=\max\left(U(c),\max_{g\in G(c)}U(g)\right),
   \]
   with no additional descendant penalty (\(\lambda=0\));
4. record every child and grandchild evaluation and update the best-output archive when appropriate.

After the sampled children, select the valid child with the highest \(V(c)\), resolving ties lexicographically. Replace the current parent with that child only if:

\[
V(c)>U(E_{\mathrm{current}})+10^{-4}.
\]

The child becomes the next parent even when its immediate score is lower than the parent's, provided its sampled descendant value passes this rule. A high-scoring grandchild does not replace the child as parent.

Invalid children receive no grandchildren. Search continues until exactly 500 evaluations are logged; a final child or grandchild sequence may be truncated at the cap.

### 5. Independent search

Each proposal is sampled independently from the same stochastic depth-2 expression generator used in Pilot 4c/4d. There is no current parent. Valid expressions are scored, and the best-output archive is updated.

### 6. Unscaffolded search

Every proposal is a one-mutation variant of the original `dot` root. The deterministic root neighborhood is cycled as necessary until 500 evaluations have been consumed. Retained outputs never become parents.

## Lineage and activity measures

The proposal history records condition, round, evaluation number, parent, expression, child/grandchild role, gate reasons, development scores, symmetry class, homogeneity diagnostics, and acceptance decision.

Search summaries include:

- terminal output expression and score;
- accepted parent moves;
- non-improving and strictly negative immediate-score moves;
- lookahead moves accepted because of descendant value;
- exact terminal and intermediate area discovery;
- current-parent and output symmetry classes.

Structural dependency is measured by capped minimum root distance:

- 0: terminal expression is `dot`;
- 1: terminal expression belongs to the direct root neighborhood;
- \(\geq2\): terminal expression is outside the direct root neighborhood.

This distinguishes obligatory multi-step outputs from historically long paths ending in directly reachable expressions. Causal scaffolding still requires performance evidence against matched controls.

## Final representations

Ten representations are evaluated:

- `pairwise`;
- `initial` (`dot`);
- `greedy`;
- `neutral_drift`;
- `diversity_archive`;
- `sampled_lookahead`;
- `independent_search`;
- `unscaffolded`;
- `supplied_area`;
- `raw_quadratic`.

Each searched representation contains 15 pairwise distances plus one selected 20-component constructor block. Archive diversity therefore does not change final dimensionality.

## Final evaluation

- 20 replicates and four leave-one-family-out folds;
- 80 runs per search condition;
- exactly 500 proposals per condition/run;
- nested final-task budgets 25, 50, 100, 200, 500, and 1000;
- fixed `Ridge(alpha=1e-3)`;
- training-only feature and target standardization;
- common training order across all representations within replicate/fold;
- MSE, NRMSE, \(R^2\), and \(\log(1+\mathrm{NRMSE})\).

The primary endpoint is budget 200. The experiment contains 240,000 search proposals and 4,800 final model evaluations.

## Pre-specified statistical comparisons

For each representation, compute \(L=\log(1+\mathrm{NRMSE})\) and average four test-family folds within each replicate. Comparisons use two-sided 95% Student-\(t\) intervals over 20 replicate differences.

For a focus method \(M\) and comparator \(C\):

\[
D=L_C-L_M,
\]

so positive values favor the focus method.

### Primary

At budget 200:

- diversity archive versus greedy.

A positive interval whose lower bound exceeds zero supports persistence-based scaffolding under this search grammar.

### Secondary

At budget 200:

- sampled lookahead versus greedy;
- neutral drift versus greedy;
- diversity archive versus neutral drift;
- diversity archive versus sampled lookahead;
- independent search versus diversity archive;
- independent search versus sampled lookahead;
- unscaffolded versus diversity archive;
- diversity archive versus supplied area;
- sampled lookahead versus supplied area;
- greedy versus initial.

Other budgets, per-family results, medians, win fractions, exact sign tests, exact-area discovery, structural-depth categories, and valley-crossing counts are supporting analyses. Secondary comparisons are not adjusted for multiplicity.

## Interpretation rules fixed before testing

### Positive persistence-based scaffolding

Requires both:

- a positive primary archive-versus-greedy interval; and
- recorded archive lineages showing retention of expressions that greedy search would not retain immediately.

Exact-area discovery is not required if other constructors produce the advantage.

### Positive descendant-value result

Requires a positive lookahead-versus-greedy interval and documented accepted children whose immediate score did not improve but whose sampled descendant value passed the acceptance rule.

### Positive neutral-tolerance result

Requires a positive neutral-drift-versus-greedy interval. Tabu activity or revision count alone is insufficient.

### No general lineage advantage

If independent search matches or outperforms a lineage method, no general superiority over direct sampling is claimed. A positive archive-versus-greedy result would then concern the specified local search mechanisms only.

### Structural activity is not scaffolding

More accepted moves, more multi-step paths, or more \(\geq2\) outputs cannot establish a performance advantage. Post hoc subsets of successful valley crossings cannot rescue a failed primary interval.

### Incomplete recovery and instability

Supplied-area superiority, low-budget instability, family-specific failures, gate rejections, and heavy tails will be retained. The experiment does not test symmetric aggregation or multi-block representational integration; those remain separate questions.

## Limitations

- The environment, grammar, descriptors, thresholds, development tasks, and learner are researcher-supplied.
- Sampled lookahead evaluates only a small stochastic subset of descendants.
- The four-class archive is a minimal symmetry partition, not full MAP-Elites.
- Neutral-drift thresholds are fixed design choices and may affect whether valleys are crossed.
- Proposal count is matched, not runtime or memory.
- Independent and lineage methods have different proposal distributions by design.
- Compactness supplies area-related development guidance.
- Positive results would concern this synthetic finite-grammar setting and would not establish unrestricted open-endedness or metaphysical conclusions.
