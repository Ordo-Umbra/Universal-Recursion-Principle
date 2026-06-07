# Level and Delta Forms of the S-Functional

The S-functional appears in this repository in two closely related forms, and
readers (and the code) move between them without it always being obvious that a
transition has happened. This short note names the two forms, shows that one is
the discrete derivative of the other, and explains why the theory is written in
one form while the practical S Compass pipeline is built mostly in the other.

This is the prose companion to the reconciliation already implemented in code:
`s_compass/scoring.py` (level form) and `s_compass/s_engine.py` (delta form).

---

## 1. The two forms

**Delta form** — *where is the system heading?*

$$\Delta S = \Delta C + \kappa\,\Delta I$$

Here $\Delta C$ and $\Delta I$ are *increments* — the growth in distinction and
integration across a step $t \rightarrow t+1$. This is the form used in the
[manifesto](manifesto.md) and the
[main framework](Universal-Recursion-Principle.md), where the fundamental object
is a *rate of recursive growth* and total understanding is the accumulation

$$S(T) = \sum_{t=0}^{T-1} \Delta S_t .$$

**Level form** — *where is the system now?*

$$S = C + \kappa I$$

Here $C$ and $I$ are *levels* — the absolute amount of distinction and
integration present at a single moment. This is the form used in
[Transformer-Dynamics.md](Transformer-Dynamics.md) (predictive entropy for $C$,
attention structure for $I$) and in the
[S Compass system design](S-Compass-System-Design.md).

---

## 2. Why both forms exist

They are not two different theories — the level form is the **state** and the
delta form is its **change over time**:

$$\Delta S_t = S_t - S_{t-1}, \qquad \Delta C_t = C_t - C_{t-1}, \qquad \Delta I_t = I_t - I_{t-1}.$$

The choice of form follows from what each part of the project can actually
*measure*:

- The **theory** reasons about open-ended growth, so it is naturally written in
  deltas: a system persists when $\langle dS/dt\rangle > 0$, i.e. it keeps
  generating distinction and integration. The interesting object is the
  trajectory, not any single snapshot.
- The **S Compass** has to score a *single inference step* from a trace, where
  the cheaply observable quantities (output entropy, citation coverage, context
  pressure) are **levels**, not increments. So the runtime pipeline estimates
  $C$, $I$, $\kappa$ as levels and reports $S = C + \kappa I$ per step.

The delta form is then recovered by differencing those levels across steps —
which is exactly what the `SEngine` does.

---

## 3. How the code keeps them consistent

A subtle failure mode is letting the two forms drift into *different*
definitions of $C$ and $I$. The implementation avoids this by computing the
level form once and differencing it:

- `s_compass/scoring.py :: score_step` computes the canonical $C$, $I$,
  $\kappa$, and $S = C + \kappa I$ for a step.
- `s_compass/s_engine.py :: SEngine` consumes that same snapshot and computes
  $\Delta C$, $\Delta I$, and $\Delta S = \Delta C + \kappa\,\Delta I$ relative
  to the previous step.

Because the delta form is built *from* the level snapshot, there is exactly one
definition of distinction and integration in the system. The only difference
between the forms is whether we report the value or its change.

---

## 4. Two regime vocabularies

The two forms answer different questions, so they carry different regime labels.

**State regimes** (level form — `classify_regime`) describe *where the system
is* and appear in Transformer-Dynamics §7 and the S Compass design doc:

| State regime | Signature |
|--------------|-----------|
| `creative-grounded` | high $C$, sufficient $I$ |
| `rigid` | low $C$, high $I$ |
| `hallucination-risk` | high $C$, low/unstable $I$, low $\kappa$ |
| `collapse` | low $C$, low $I$, low $\kappa$ |

**Trajectory regimes** (delta form — `classify_recursion`) describe *where the
system is heading*:

| Trajectory regime | Signature | Drifting toward |
|-------------------|-----------|-----------------|
| `expanding` | $\Delta C > 0,\ \Delta I > 0$ | creative-grounded |
| `diverging` | $\Delta C > 0,\ \Delta I < 0$ | hallucination-risk |
| `consolidating` | $\Delta C < 0,\ \Delta I > 0$ | rigid |
| `contracting` | $\Delta C < 0,\ \Delta I < 0$ | collapse |
| `steady` | both within a deadband | a fixed point |
| `initial` | first step (no predecessor) | — |

The two are complementary: the state regime classifies the current snapshot,
while the trajectory regime gives an early-warning signal that the state
regimes structurally cannot. A step can read as `creative-grounded` (a healthy
*state*) while its trajectory is already `contracting` (a degrading *motion*) —
the level form only notices once the decline has accumulated, but the delta
form flags the turn immediately.

---

## 5. Summary

- The theory is written in the **delta form** $S = \Delta C + \kappa\,\Delta I$
  because it is about sustained recursive *growth*.
- The S Compass runtime is built in the **level form** $S = C + \kappa I$
  because a single trace exposes levels, not increments.
- They are the same functional: **delta is the discrete derivative of level**,
  and the code enforces this by differencing one shared snapshot.
- **State regimes** say where you are; **trajectory regimes** say where you are
  going. Both are needed to steer an AI system before it fails, not after.
