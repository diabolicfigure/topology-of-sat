# A transient homology regime in growing random 3-SAT solution spaces

**Technical note** for the $n = 14$ snapshot in this repository.

Homology is used here as a **measuring instrument** for the geometry of satisfying assignments.  
This note does **not** claim a result about $\mathrm{P}$ vs $\mathrm{NP}$, and does **not** treat Betti numbers as a measure of computational hardness.

---

## 1. Setup

Let $\varphi$ be a 3-CNF formula on $n$ Boolean variables, and let

$$
S(\varphi) \subset \{0,1\}^n
$$

be its set of satisfying assignments. We equip $S(\varphi)$ with the structure of an **induced cubical complex** $K(\varphi)$ inside the Boolean hypercube: a $d$-dimensional face of the hypercube is included in $K(\varphi)$ if and only if all $2^d$ of its vertices lie in $S(\varphi)$.

We compute cubical homology with coefficients in $\mathbb{Z}/2\mathbb{Z}$:

$$
\beta_k(\varphi) \;=\; \dim H_k\bigl(K(\varphi);\,\mathbb{Z}/2\mathbb{Z}\bigr), \qquad k = 0,1,2.
$$

| Symbol | Meaning |
|--------|---------|
| $\beta_0$ | number of connected components (clusters) of the 1-skeleton |
| $\beta_1$ | number of independent unfilled 1-cycles |
| $\beta_2$ | number of independent 2-dimensional voids |

We do **not** draw an independent formula at each density. A single ordered **clause stream** is generated once; at target density $\alpha$ we retain only the first

$$
m \;=\; \mathrm{round}(\alpha \cdot n)
$$

clauses. Topology is therefore tracked along a monotonically growing family.

Two kinds of stream are used:

- **Uniform:** ordinary random 3-SAT clauses.
- **Planted:** every clause is satisfied by one fixed hidden assignment, so the formula remains satisfiable as density increases.

---

## 2. Hypothesis

High Betti numbers—especially cubical $\beta_1$—appear while the formula is still underconstrained. As clauses are added:

1. cycles die,
2. the space then shatters ($\beta_0$ rises),
3. for uniform families the space eventually collapses to unsatisfiability.

In this picture, topological complexity is a **transient regime on the way to hardness**, not hardness itself.

---

## 3. Protocol

| Parameter | Value |
|-----------|--------|
| $n$ | $14$ |
| $k$ | $3$ |
| Enumeration | full ($2^{14}$ assignments) |
| Uniform streams | seeds $1000$–$1011$ (12 families) |
| Planted streams | seeds $1012$–$1023$ (12 families) |
| $\alpha$-grid | $\{1.00, 1.25\} \cup \{1.5, 1.6, \ldots, 3.5\} \cup \{3.75, 4.00, \ldots, 5.00\}$ |
| Cubical 3-skeleton | computed when $\|S\| \le 2500$; otherwise 1-skeleton only (`truncated`) |

Additional logged quantities: skeleton $\beta_1$,  

$$
\mathrm{fill\_gap} \;=\; \text{skeleton }\beta_1 - \text{cubical }\beta_1,
$$

and the girth of the 1-skeleton (length of a shortest cycle).

Densities $\alpha < 1$ are omitted: $|S|$ is then several thousand, cubical $\beta_1$ is already observed to be $0$, and the cost of the 3-skeleton dominates.

```bash
python -m satlab.lifecycle \
  --n 14 --k 3 \
  --families 12 \
  --kind uniform,planted \
  --seed0 1000 \
  --max-vertices-dim3 2500 \
  --out results/path_c_n14.csv
```

---

## 4. Success and failure criteria

On a single growing family we record:

- **onset** — first $\alpha$ with cubical $\beta_1 > 0$
- **$\beta_1$ peak / death** — $\alpha$ of maximum cubical $\beta_1$; first later $\alpha$ after which cubical $\beta_1$ remains $0$
- **$\beta_0$ peak** — $\alpha$ of maximum $\beta_0$ among satisfiable prefixes
- **collapse** — first $\alpha$ with $|S| = 0$ (uniform streams only)

Verdicts:

| Verdict | Definition |
|---------|------------|
| **success** | onset occurs, $\beta_1$ dies, $\beta_1$-peak lies at or before $\beta_0$-peak, and cubical $\beta_1 = \beta_2 = 0$ on $\alpha \in [3.5, 4.5]$ |
| **no_signal** | cubical $\beta_1$ never exceeds $0$ (does not refute the hypothesis) |
| **fail_hard_peak** | $\beta_1$ (or $\beta_2$) peaks inside the hard window $[3.5, 4.5]$ |
| **fail_beta1_persists** | $\beta_1$ never returns to $0$ |

A vanishing $\beta_2$ does not refute the hypothesis; the claim concerns the life cycle of $\beta_1$.

---

## 5. Results

Total: **696** logged rows.  
Artefacts: `results/path_c_n14.csv`, `results/path_c_n14.summary.json`.

### 5.1 Aggregate verdicts

| Verdict | Count |
|---------|------:|
| success | 17 |
| no_signal | 7 |
| fail_hard_peak | 0 |
| fail_beta1_persists | 0 |

- Uniform: 8 success, 4 no_signal  
- Planted: 9 success, 3 no_signal  

Every family that grew a cubical hole matched the success order. Both failure classes are empty.

### 5.2 Mean curves

**Uniform (12 families).**  
The fraction of families with cubical $\beta_1 > 0$ peaks near $\alpha = 1.6$ (approximately $0.42$).  
Mean $\beta_0$ peaks near $\alpha = 3.1$ (approximately $3.50$).  
From $\alpha = 3.2$ onward the cubical-$\beta_1$ fraction is $0$. Uniform families then lose solutions toward $\alpha = 5$.

**Planted (12 families).**  
The cubical-$\beta_1$ fraction peaks at $\alpha = 2.0$ (approximately $0.67$) and is $0$ for all $\alpha \ge 3.0$, while the formulas remain satisfiable (mean $|S| \approx 7$ at $\alpha = 5$).  
Hole vanishing is therefore not an artefact of an empty solution set.

A rare planted $\beta_2$ flicker appears at $\alpha = 1.0$–$1.5$ (mean $0.08$–$0.17$). In the hard window, every family’s `hard_beta2_max` is $0$.

### 5.3 Walk-through (uniform seed 1001)

| $\alpha$ range | Behaviour |
|----------------|-----------|
| $1.0$–$2.1$ | $\beta_1 = 0$, $\beta_0 = 1$ |
| $2.2$ | $\beta_1$ appears |
| $2.2$–$3.1$ | $\beta_1 = 1$ while $\beta_0$ rises to $5$ |
| $3.2$ | $\beta_1$ dies |
| $4.25$ | unsatisfiable |

### 5.4 Cycle geometry

At low $\alpha$, $\mathrm{fill\_gap}$ is in the thousands: 2-faces kill most 1-skeleton cycles. Residual cubical $\beta_1$ is therefore not a 1-skeleton artefact.  
Wherever girth is computed it equals $4$: the shortest cycles are filled squares; leftover $\beta_1$ arises from longer cycles.

---

## 6. Related work

Solution-space geometry of random SAT—clustering, shattering, condensation—is a standard line of research (Achlioptas, Mézard–Zecchina, Coja-Oghlan, and others). Those works primarily track **how many clusters** exist ($\beta_0$-level information).

Homology asks a finer question: are there holes *inside* or *among* clusters?  
In the present snapshot the finer invariant ($\beta_1$) becomes active **before** the clustering peak and then dies.

---

## 7. Limits

- $n = 14$ only  
- no explicit homology generators beyond girth and fill-gap  
- no 2-SAT lifecycle comparison in this note  
- no claim that the same pattern persists at large $n$

## Reproduce

```bash
python -m unittest discover -s tests -v

python -m satlab.lifecycle \
  --n 14 --k 3 \
  --families 12 \
  --kind uniform,planted \
  --seed0 1000 \
  --max-vertices-dim3 2500 \
  --out results/path_c_n14.csv
```

Expected aggregate: 17 `success`, 7 `no_signal`, 0 hard-window failures.