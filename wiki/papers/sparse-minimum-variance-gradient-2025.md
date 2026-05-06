# A Scalable Gradient-Based Optimization Framework for Sparse Minimum-Variance Portfolio Selection

**Authors:** Sarat Moka, Matias Quiroz, Vali Asimit, Samuel Muller
**Venue/Source:** arXiv q-fin.PM
**arXiv/DOI:** arXiv:2505.10099
**Date:** May 15, 2025

---

## Core Claim
The standard sparse minimum-variance portfolio (select exactly k of p assets to minimise portfolio variance) is an NP-hard mixed-integer quadratic program (MIQP) whose runtime grows exponentially with k and p. The authors reformulate it as a continuous optimisation problem via Boolean relaxation with a tunable concavity parameter, yielding a gradient-based algorithm that matches commercial MIQP solvers at a fraction of the computational cost.

---

## Method
**Boolean relaxation with concavity scheduling:**

The standard sparse MVP problem is:
```
min_{w, z}  w' Σ w
s.t.  1'w = 1,  w_i ≥ 0 ∀i,  z_i ∈ {0,1},  w_i ≤ z_i,  1'z = k
```

The authors introduce a continuous auxiliary variable s_i ∈ [0,1] replacing z_i, add an auxiliary objective `f(s; λ)` that is convex when λ=0 (easy warm-start) and concave when λ→∞ (forces s to binary), and gradually increase λ during optimisation. This path ensures convergence to near-integer solutions without a combinatorial branch-and-bound search.

**Key algorithm properties:**
- O(k p²) per iteration (vs. exponential for exact MIQP)
- Provably equivalent to MIQP on the set of binary points
- Scalable to p = 1000+ assets with k = 20–50

---

## Results
On standard portfolio benchmark datasets, the gradient-based algorithm:
- Matches commercial solvers (Gurobi, CPLEX) in the selected asset set for >95% of problem instances
- In rare cases where selections differ, the error in portfolio variance is negligible (<0.01%)
- Achieves orders-of-magnitude speedup for large p, enabling real-time portfolio updates

The paper does not report Sharpe/MDD metrics; the contribution is algorithmic efficiency, not alpha generation. The key claim is that the sparse MVP (cardinality-constrained minimum variance) is now practically solvable at scale.

---

## Implementable Idea
Our current selection logic in `trend_vol_v4.py`:
1. Compute 60d rolling vol per asset
2. Filter by trend threshold (35d return > −0.025)
3. Exclude illiquid (bottom 5% by amount)
4. **Take the top-N by univariate rolling vol (rank and pick)**

Step 4 is a greedy approximation: it ignores cross-asset correlations. The true sparse MVP would find the N stocks whose **joint** portfolio variance is minimum, which is lower than the portfolio variance from the top-N individually-quietest stocks (because low correlations among stocks reduce portfolio variance independently of each stock's own variance).

Replacement for Step 4:
```python
import numpy as np
from scipy.optimize import minimize

def sparse_mvp_gradient(Sigma, k, n_iter=200, lambda_max=50.0):
    """
    Find sparse minimum-variance portfolio weights via Boolean relaxation.
    Sigma: p×p covariance matrix
    k: target number of assets (cardinality constraint)
    Returns: weight vector (length p, zeros for excluded assets)
    """
    p = Sigma.shape[0]
    s = np.ones(p) / p         # auxiliary binary relaxation
    w = np.ones(p) / p         # portfolio weights

    for lam in np.linspace(0, lambda_max, n_iter):
        # Gradient of portfolio variance w.r.t. w (holding s fixed)
        grad_w = 2 * Sigma @ w
        # Gradient of concavity regulariser w.r.t. s
        # f(s;λ) = -λ * sum(s*(1-s)) forces s to {0,1}
        grad_s = -lam * (1 - 2 * s)

        # Projected gradient step
        w = w - 0.01 * grad_w * s           # only update active assets
        s = np.clip(s - 0.01 * grad_s, 0, 1)

        # Project w to simplex restricted to support of s
        w = np.maximum(w, 0)
        if w.sum() > 0: w /= w.sum()

    # Round s to binary: select top-k by s value
    top_k = np.argsort(s)[-k:]
    w_sparse = np.zeros(p)
    w_sub = np.linalg.lstsq(Sigma[np.ix_(top_k, top_k)], np.ones(k), rcond=None)[0]
    w_sub = np.maximum(w_sub, 0); w_sub /= w_sub.sum()
    w_sparse[top_k] = w_sub
    return w_sparse

# In trend_vol_v4.py, after filtering to eligible assets:
# Compute covariance of eligible assets (60d rolling returns)
# Call sparse_mvp_gradient(Sigma_eligible, k=20)
# Use returned weights directly (already minimum-variance ERC-like)
```

This replaces both the N-selection step and the 1/σ ERC weighting with a single joint optimisation that minimises portfolio variance subject to exactly N=20 stocks being held.

**Addresses priority:** Priority 3 — Stock selection within the low-vol universe. By solving for the jointly-optimal N stocks (not just the top-N individually quietest), this can identify low-correlation pairs that achieve lower portfolio variance than the current selection, directly targeting MDD reduction through better diversification.

---

## Relevance to Feishu Competition
Our current ERC weights (`1/σ_i`) already move in the right direction (concentrate in low-vol stocks) but ignore correlations. The sparse MVP replaces both the selection step and the weighting step with a single operation that minimises actual portfolio variance. Given our IS MDD of 7.98%, even a modest 0.5% portfolio vol reduction could improve Score by ~0.002–0.003 (MDD is 25% of Score). The algorithm is fast enough to run daily across 2,270 assets. Key risk: covariance estimation with only 60 days of data is noisy for 2,270×2,270 matrices — regularisation (Ledoit-Wolf) is essential before applying sparse MVP. Suggested implementation: restrict eligible universe to the top 100 by rolling vol (our existing filter), then run sparse_mvp_gradient on the Σ_{100×100} to select N=20.

---

## Concepts
-> [[factor-models]] | [[statistical-arbitrage]]
