# Topology of SAT Solution Spaces

**Lifecycle of cubical Betti numbers in random and planted 3-SAT**

This repository is a reproducible snapshot of one experiment at $n = 14$.  
Homology is used as a measuring instrument for the geometry of satisfying assignments.

---

## 1. Mathematical setup

### 1.1 Solution space as a cubical complex

Let $\varphi$ be a CNF formula on $n$ Boolean variables. Write

$$
S(\varphi) = \{ x \in \{0,1\}^n \mid \varphi(x) = 1 \}
$$

for its set of satisfying assignments.

We view $S(\varphi)$ as a **cubical subcomplex** $K(\varphi)$ of the $n$-dimensional Boolean hypercube:

- **0-faces (vertices):** the points of $S(\varphi)$
- **1-faces (edges):** pairs of solutions at Hamming distance 1
- **$k$-faces:** $k$-dimensional subcubes of the hypercube whose entire vertex set lies in $S(\varphi)$

Equivalently: a set of $k$ free coordinates spans a $k$-cube in $K(\varphi)$ if and only if all $2^k$ assignments obtained by varying those bits (and fixing the rest) satisfy $\varphi$.

### 1.2 Homology

We compute cubical homology of $K(\varphi)$ with coefficients in $\mathrm{GF}(2) = \mathbb{Z}/2\mathbb{Z}$:

$$
\beta_k(\varphi) = \dim_{\mathrm{GF}(2)} H_k\big(K(\varphi);\,\mathrm{GF}(2)\big)
$$

| Symbol | Meaning |
|--------|---------|
| $\beta_0$ | number of connected components (clusters) in the 1-skeleton |
| $\beta_1$ | number of independent 1-dimensional holes (cycles that do not bound a 2-chain) |
| $\beta_2$ | number of independent 2-dimensional voids |

Additional logged quantities:

- **skeleton $\beta_1$**: first Betti number of the pure 1-skeleton (higher faces ignored)
- **fill gap**: skeleton $\beta_1$ minus cubical $\beta_1$ (how many 1-cycles are killed by 2-faces)
- **girth**: length of a shortest non-bounding cycle when cubical $\beta_1 > 0$

When $|S(\varphi)|$ is large, higher-dimensional faces may be truncated. In this experiment, full cubical homology up to dimension 3 is computed whenever $|S| \le 2500$.

---

## 2. Experimental protocol: clause-density lifecycle

Rather than drawing an independent formula at each density, we fix a **clause stream** and grow the formula monotonically.

### 2.1 Design

- $n = 14$, $k = 3$ (3-SAT)
- Full enumeration of $\{0,1\}^n$
- 12 **uniform** streams and 12 **planted** streams (seeds $1000$–$1023$)
- A stream is an ordered list of random 3-clauses
- At density $\alpha$ the instance consists of the first

$$
m = \mathrm{round}(\alpha \cdot n)
$$

  clauses of that stream
- **Planted** streams are generated so that one fixed hidden assignment remains satisfying for every $\alpha$ (the formula stays SAT while density increases)
- $\alpha$-grid:
  - $1.00$, $1.25$
  - $1.5$ to $3.5$ in steps of $0.1$
  - $3.75$ to $5.0$ in steps of $0.25$

For every pair $(\text{family},\alpha)$ we record $|S|$, $\beta_0$, cubical $\beta_1$, $\beta_2$, skeleton $\beta_1$, fill gap, girth, and runtime.

### 2.2 Success criterion

For a single stream we declare a **success** if there exist densities

$$
\alpha_{\mathrm{onset}} < \alpha_{\mathrm{death}} \le \alpha_{\beta_0\text{-peak}}
$$

such that:

1. cubical $\beta_1$ becomes positive at $\alpha_{\mathrm{onset}}$
2. cubical $\beta_1$ returns to zero by $\alpha_{\mathrm{death}}$
3. $\beta_0$ attains a peak at or after $\alpha_{\mathrm{death}}$
4. in the window $\alpha \in [3.5, 4.5]$, neither cubical $\beta_1$ nor $\beta_2$ peaks above earlier values

Streams that never grow cubical $\beta_1$ are labelled **no_signal**.

---

## 3. Results ($n = 14$)

**Aggregate:** 17 success · 7 no_signal · 0 hard-window peaks  
(24 families total).

### 3.1 Observed order (when signal is present)

On the 17 successful streams the same qualitative lifecycle appears:

1. **Underconstrained regime** ($\alpha \approx 1.5$–$2.2$): cubical $\beta_1$ is born  
2. **Before the clustering peak** ($\alpha \approx 2.0$–$3.2$): cubical $\beta_1$ dies  
3. **Around $\alpha \approx 2.8$–$3.5$**: $\beta_0$ peaks (clustering)  
4. **Uniform streams only:** still higher $\alpha$ eventually yields unsatisfiability

In the interval $\alpha \in [3.5, 4.5]$ **no** family exhibits a peak of cubical $\beta_1$ or $\beta_2$.

Planted streams remain satisfiable at high density, yet $\beta_1$ still vanishes.  
Therefore the disappearance of holes is not an artefact of an empty solution set.

### 3.2 Geometry of the cycles

- Fill gap is large at low $\alpha$: most 1-skeleton cycles are boundaries of 2-faces  
- Residual cubical $\beta_1$ is consequently a genuine feature of the cubical complex, not a 1-skeleton artefact  
- Observed girth is $4$: the shortest cycles are filled squares; surviving $\beta_1$ comes from longer cycles

### 3.3 Summary

On this ensemble, cubical $\beta_1$ behaves as a **transient** of the underconstrained regime.  
$\beta_0$ tracks the familiar clustering picture.  
$\beta_2$ does not appear as a late-density phenomenon at $n = 14$.

---

## 4. Limits

- $n = 14$ only  
- no explicit homology generators beyond girth and fill-gap  
- no 2-SAT lifecycle comparison in this snapshot  
- no claim that the same pattern persists at large $n$

This note reports an empirical topological transition at $n = 14$.

---

## 5. Reproduce

Python 3.11+. Core pipeline uses only the standard library.

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

Expected aggregate verdict: 17 `success`, 7 `no_signal`, 0 hard-window peaks.

Checked-in artefacts:

- `results/path_c_n14.csv` — full lifecycle log  
- `docs/lifecycle-note.md` — extended technical note  
- `tests/` — unit tests for the homology engine  

---

## 6. Related work

Solution-space geometry of random SAT (clustering / shattering) is a standard line: Achlioptas, Mézard–Zecchina, Coja-Oghlan and others. Those works primarily track how many clusters exist. Homology asks a finer question about holes inside or among clusters. In this snapshot the finer invariant becomes active before the clustering peak and then dies.

---

## License

MIT

---

## Citation

If you use this snapshot, please cite the repository together with the experimental protocol  
($n$, seeds, $\alpha$-grid, cubical homology over $\mathrm{GF}(2)$).
```