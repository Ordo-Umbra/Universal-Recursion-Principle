# Generative Geometry — Pilot 4c Report

## Stability-Guided Constructor Refinement and Developmental Scaffolding

### Executive result

Pilot 4c is a **positive result for actual constructor refinement and development guidance, but a negative result for developmental scaffolding**.

The system began every search with the imperfect shallow constructor `dot` and revised its expression through recorded parent–child mutations. All 80 refined lineages accepted at least one syntactic revision, producing 93 accepted revisions in total. At the primary held-out budget of 200, refinement significantly improved hull-area prediction over the initial constructor and over a random lineage under the pre-specified paired log-error analysis.

However:

- Most refinement was shallow: 70 of 80 runs accepted only one revision, seven accepted two, and three accepted three.
- Refined search did **not** outperform the matched unscaffolded control. The primary scaffolding interval included zero.
- Exact `abs(cross)` was the terminal refined constructor in only 3 of 80 runs, although it appeared as an accepted intermediate in one additional run.
- Supplied area remained far superior to the typical refined constructor.
- A secondary paired interval favored refined search over independent search, but the two methods selected the same terminal expression in 49 of 80 runs and refined search won only half of replicate-level comparisons. This is not evidence of a broad or consistent lineage advantage.
- Label-free gates rejected the previously pathological self-ratio, but low-budget instability remained.

The defensible conclusion is therefore narrow: **robust development guidance can support genuine expression revision and improve a fixed imperfect constructor, but this experiment does not show that intermediate constructors causally scaffold better later development.**

## Experimental design

### Refinement mechanism

Every search began with:

```text
dot
```

Mutations could replace leaves, change node operations, wrap an expression in a unary operation, compose it with a leaf, remove a root operation, shrink a binary expression, or swap binary children. Expressions were limited to depth 2.

A child replaced its parent only when it:

1. passed numerical, near-constancy, small-sample, and cross-family scale gates; and
2. improved the robust development score by more than \(10^{-4}\).

At most four revision rounds were permitted. Parents remained in the lineage archive but were not added as extra feature blocks. Consequently, the initial and refined representations both had 35 dimensions: 15 pairwise distances plus one 20-component triple-constructor block.

### Robust development guidance

Search used hull perimeter, compactness, and hull vertex count, never hull-area labels. For each final fold, three internal family-held-out development folds were evaluated at fitting budgets 40 and 80. The development score was the median of 18 task/fold/budget \(R^2\) values after clipping each to \([-1,1]\).

### Matched controls

- **Initial:** fixed `dot` without revision.
- **Independent search:** development-guided random expression proposals without parent chaining.
- **Unscaffolded:** development-guided variants of the original root; retained variants never became parents.
- **Random lineage:** lineage-like random expression changes without development-label guidance.

Every control received exactly the refined run's candidate-evaluation count. Across 80 runs, this was 7,523 proposals per search condition, or 30,092 logged proposals overall.

### Final evaluation

The final task was hull area in an unseen environment family. Twenty replicates, four leave-one-family-out folds, and six nested training budgets were used, yielding 3,840 final model evaluations.

The primary robust error measure was:

\[
L=\log(1+\mathrm{NRMSE}).
\]

Paired intervals were computed over 20 replicate means across four test families. Differences are comparator minus refined, so positive values favor refinement.

## Primary results at budget 200

| Representation | Mean held-out \(R^2\) | Median \(R^2\) | 10th-percentile \(R^2\) | Median NRMSE |
|---|---:|---:|---:|---:|
| initial | -0.5118 | 0.1532 | -2.5738 | 0.9202 |
| refined | 0.6320 | 0.7728 | 0.2910 | 0.4767 |
| independent search | 0.4058 | 0.7676 | -0.5161 | 0.4821 |
| unscaffolded | 0.6578 | 0.7690 | 0.3338 | 0.4806 |
| random lineage | -799.9730 | -0.3355 | -70.5737 | 1.1555 |
| supplied area | 0.9684 | 0.9723 | 0.9474 | 0.1664 |
| pairwise | -0.6440 | 0.1148 | -2.9630 | 0.9408 |
| raw quadratic | 0.3034 | 0.3493 | -0.0577 | 0.8066 |

The random-lineage mean is dominated by extreme failures. The median, log-error analysis, and unmodified raw results are all retained because no single summary describes this heavy-tailed distribution.

### Pre-specified paired comparisons

| Comparator | Log-error difference | 95% interval | Replicate win fraction | Exact sign \(p\) |
|---|---:|---:|---:|---:|
| initial | 0.3132 | [0.2826, 0.3438] | 1.00 | \(1.91\times10^{-6}\) |
| random lineage | 0.7489 | [0.5630, 0.9348] | 1.00 | \(1.91\times10^{-6}\) |
| unscaffolded | 0.0015 | [-0.0195, 0.0226] | 0.30 | 0.1153 |
| independent search | 0.0381 | [0.0087, 0.0676] | 0.50 | 1.0000 |
| supplied area | -0.2695 | [-0.2995, -0.2396] | 0.00 | \(1.91\times10^{-6}\) |
| pairwise | 0.3299 | [0.2993, 0.3605] | 1.00 | \(1.91\times10^{-6}\) |
| raw quadratic | 0.1631 | [0.1345, 0.1917] | 1.00 | \(1.91\times10^{-6}\) |

The primary refinement and guidance criteria passed. The primary scaffolding criterion failed. Supplied area was significantly better than refined search. The independent-search interval favored refinement, but its low win fraction and frequent terminal-expression agreement require a qualified interpretation.

## What refinement actually did

### Revision counts

| Accepted revisions | Search runs |
|---:|---:|
| 1 | 70 |
| 2 | 7 |
| 3 | 3 |

Every run accepted at least one revision, but the mean was only 1.1625 revisions. Search evaluated a mean of 94.04 proposals per guided condition, with a range of 86–186.

### Revision paths

| Path | Runs |
|---|---:|
| `dot → cross` | 64 |
| `dot → add(cross,dot)` | 6 |
| `dot → cross → abs(cross)` | 3 |
| `dot → v2 → sqrt_abs(v2)` | 1 |
| `dot → cross → add(cross,u2)` | 1 |
| `dot → cross → abs(cross) → add(abs(cross),cross)` | 1 |
| `dot → cross → sqrt_abs(cross) → add(cross,sqrt_abs(cross))` | 1 |
| `dot → cross → sqrt_abs(cross) → sqrt_abs(u2)` | 1 |
| `dot → add(cross,dot) → add(add(cross,dot),cross)` | 1 |
| `dot → add(cross,dot) → add(add(cross,dot),w2)` | 1 |

The dominant result was replacement of the dot product by a signed cross product. This is genuine expression revision, but it is usually a single mutation rather than an extended developmental trajectory.

### Terminal constructors and held-out performance

| Terminal refined expression | Runs | Mean \(R^2\) | Median \(R^2\) |
|---|---:|---:|---:|
| `cross` | 64 | 0.6782 | 0.7690 |
| `add(cross,dot)` | 6 | 0.4573 | 0.6574 |
| `abs(cross)` | 3 | 0.9737 | 0.9698 |
| `add(abs(cross),cross)` | 1 | 0.8339 | 0.8339 |
| `add(add(cross,dot),w2)` | 1 | 0.8049 | 0.8049 |
| `add(add(cross,dot),cross)` | 1 | 0.8534 | 0.8534 |
| `add(cross,sqrt_abs(cross))` | 1 | 0.9258 | 0.9258 |
| `add(cross,u2)` | 1 | 0.8172 | 0.8172 |
| `sqrt_abs(u2)` | 1 | -1.6707 | -1.6707 |
| `sqrt_abs(v2)` | 1 | -1.0782 | -1.0782 |

The three runs terminating in exact area achieved mean \(R^2=0.9737\), essentially recovering supplied-area performance. The other 77 runs averaged 0.6187. This shows that refinement can reach the known constructor through a two-step path, but the development objectives usually did not select it.

Exact area was accepted as an intermediate in four runs. In one of these, a later development-improving revision replaced it with `add(abs(cross),cross)`, which performed worse than supplied area on the final task. Development improvement therefore does not guarantee movement toward the held-out optimum.

## Why the scaffolding claim failed

The unscaffolded control evaluates one-mutation variants of `dot` and retains the best, but never allows a retained variant to become a parent. For a one-revision refined run, this is effectively the same search outcome: both can select the best direct variant of `dot`.

Accordingly, refined and unscaffolded search produced exactly the same terminal expression in 70 of 80 runs—the same 70 runs with only one accepted refined revision. Their overall performance was consequently almost identical:

- refined mean \(R^2=0.6320\);
- unscaffolded mean \(R^2=0.6578\);
- paired log-error difference 0.0015, with 95% interval [-0.0195, 0.0226].

Among the ten multi-revision runs, an exploratory subset analysis favored refined search in seven and gave a mean unscaffolded-minus-refined log-error difference of 0.0121. This is mechanistically compatible with a benefit from intermediate parents, but it is a small, post hoc, lineage-selected subset. It does **not** satisfy or rescue the pre-specified scaffolding criterion.

Pilot 4c therefore identifies an important design limitation: a test of scaffolding must require problems for which useful multi-step revision is common, rather than infer scaffolding from lineages that usually terminate after one direct mutation.

## Independent-search comparison

Independent search discovered exact terminal area in 4 of 80 runs, compared with 3 for refined search. Refined and independent search selected the same terminal expression in 49 runs.

The pre-specified paired log-error interval favored refined search by 0.0381, with 95% interval [0.0087, 0.0676]. However:

- the refined replicate win fraction was only 0.50;
- the exact sign test gave \(p=1.0\);
- independent search had lower mean \(R^2\) but almost identical median \(R^2\);
- the mean log-error advantage was influenced by worse independent-search tails rather than consistent per-replicate superiority.

The formal secondary interval therefore supports an advantage under its specified estimand, but the broader evidence does not justify claiming a general or robust superiority of lineage-based refinement over independent search.

## Transfer to unseen families

Mean hull-area \(R^2\) at budget 200:

| Unseen family | Initial | Refined | Independent | Unscaffolded | Supplied area |
|---|---:|---:|---:|---:|---:|
| convex radial | -0.2723 | 0.5973 | 0.4735 | 0.7286 | 0.9836 |
| interior points | 0.3703 | 0.8604 | 0.8597 | 0.8521 | 0.9767 |
| irregular radial | 0.3851 | 0.7358 | 0.7329 | 0.7338 | 0.9479 |
| elongated | -2.5304 | 0.3343 | -0.4430 | 0.3165 | 0.9655 |

Refinement improved mean performance over the initial constructor in every family. Transfer remained weakest for elongated configurations, where signed or mixed constructors were much less effective than exact area.

## Stability gates and remaining instability

Across all four search conditions, 922 of 30,092 proposals were rejected by at least one gate. In the refined condition, 249 of 7,523 proposals were invalid.

Frequently rejected expressions included:

- `abs_diff(dot,dot)` — 356 proposals;
- `abs_diff(cross,cross)` — 82;
- `divide(cross,cross)` — 56;
- `divide(dot,dot)` — 53.

Every observed `divide(cross,cross)` proposal was rejected. The gates therefore directly prevented retention of the self-ratio constructor associated with Pilot 4b's catastrophic failures.

Nevertheless, gated refinement was not uniformly stable:

| Budget | Refined mean \(R^2\) | Refined median \(R^2\) | Supplied-area mean \(R^2\) |
|---:|---:|---:|---:|
| 25 | -2.2401 | -0.7756 | 0.9018 |
| 50 | 0.3900 | 0.5979 | 0.9283 |
| 100 | 0.5764 | 0.7279 | 0.9588 |
| 200 | 0.6320 | 0.7728 | 0.9684 |
| 500 | 0.6683 | 0.7847 | 0.9730 |
| 1000 | 0.6835 | 0.7988 | 0.9747 |

The gates removed a specific pathological mechanism and prevented the extreme random-lineage failures from dominating refined performance, but they did not guarantee safe integration at budget 25. This is consistent with the development budgets beginning at 40 and with constructor usefulness remaining learner- and sample-dependent.

## What Pilot 4c supports

A defensible summary is:

> Starting from a supplied imperfect constructor, a system can revise relational expressions through explicit parent–child lineages using label-free stability gates and robust multi-task development feedback. These revisions improved held-out hull-area prediction relative to both the initial constructor and random expression lineages. Exact area was occasionally reached through a two-step refinement path and then recovered supplied-area performance. However, most lineages accepted only one revision, refined search did not outperform the matched unscaffolded control, exact area was rarely retained, supplied area remained superior, and low-budget instability persisted. The experiment demonstrates useful constructor refinement but not a general developmental-scaffolding advantage.

It does not establish:

- open-ended discovery beyond the supplied grammar;
- autonomous choice of the initial constructor;
- reliable multi-step refinement;
- causal benefits of developmental scaffolding;
- consistent superiority over independent search;
- robustness at every sample budget;
- mathematical novelty from syntactic difference alone;
- operation beyond this synthetic geometry and fixed ridge learner.

## Implications for the next experiment

A stronger follow-up should be designed around the failure rather than around collecting more one-step successes:

1. Use starting constructors and development tasks for which direct one-mutation solutions are insufficient.
2. Pre-specify a multi-step scaffolding test rather than selecting multi-revision lineages afterward.
3. Include the lowest final budget of interest inside development evaluation if small-sample stability is a requirement.
4. Retain matched independent and unscaffolded controls, but ensure that their search trajectories can differ meaningfully from refined search.
5. Analyze when development feedback rejects or moves away from exact area without using final-task labels to repair the search retrospectively.
6. Test several fixed initial constructors in separate pre-specified strata before claiming a general refinement mechanism.

## Reproduction

Run:

```bash
python3 generative_geometry_pilot4c.py --replicates 20 --output-dir ./pilot4c_output
```

A two-replicate smoke run is available with `--replicates 2`. All seeds are deterministic. Validation confirmed the intended mutation path and gate behavior; the script applies identical proposal budgets across controls, validates output counts, and retains all raw final metrics and proposal histories.

## Files

- [Pre-run protocol](Pilot_4c_Protocol.md)
- [Experiment script](generative_geometry_pilot4c.py)
- [Raw final evaluations](pilot4c_raw_results.csv)
- [Complete proposal history](pilot4c_proposal_history.csv)
- [Accepted refinements](pilot4c_accepted_refinements.csv)
- [Search summaries and terminal expressions](pilot4c_search_summary.csv)
- [Terminal-constructor summary](pilot4c_constructor_summary.csv)
- [Overall summaries](pilot4c_summary_overall.csv)
- [Family summaries](pilot4c_summary_by_family.csv)
- [Paired comparisons](pilot4c_paired_comparisons.csv)
- [Sample-efficiency figure](pilot4c_sample_efficiency.png)
- [Family-transfer figure](pilot4c_family_transfer.png)
- [Revision-count figure](pilot4c_revision_counts.png)
- [Revision-path figure](pilot4c_revision_paths.png)
- [Run metadata](pilot4c_metadata.json)
