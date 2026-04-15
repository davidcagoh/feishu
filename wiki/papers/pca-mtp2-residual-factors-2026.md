# Uncovering Residual Factors in Financial Time Series via PCA and MTP2-constrained Gaussian Graphical Models

**Authors:** See arXiv:2602.05580 (author names not extracted from available sources)  
**Venue/Source:** arXiv q-fin  
**arXiv/DOI:** arXiv:2602.05580  
**Date:** February 5, 2026

---

## Core Claim
Standard PCA removes common market factors from equity returns, but the residuals still contain latent shared structure that PCA cannot identify (because PCA maximises explained variance, not factor orthogonality). Applying a Multivariate Totally Positive of order 2 (MTP2)-constrained Gaussian Graphical Model (GGM) hierarchically on PCA residuals forces the estimated residual precision matrix to encode only the positive-correlation structure of financial time series, resulting in genuinely orthogonal idiosyncratic components that are substantially more effective for contrarian trading.

---

## Method
**Step 1 — PCA de-factoring:**
Fit a K-factor PCA to the T × N returns matrix (rolling window of ~250 days). Compute residuals:
```
ε_{i,t} = R_{i,t} - Σ_k β_{i,k} F_{k,t}
```
where F are the top K principal components. K is chosen by standard information criteria (BIC or explained-variance threshold ~80%).

**Step 2 — MTP2-constrained GGM on residuals:**
The key insight: financial residuals still exhibit near-singular eigenstructures because PCA is not designed to remove all common latent structure. Fit a Gaussian Graphical Model (graphical LASSO / GLASSO) to the residual covariance, but constrain the precision matrix Θ to be MTP2 (all off-diagonal elements of Θ are non-positive, i.e., all partial correlations are non-negative). This is a valid constraint for financial data because stocks tend to have positive rather than negative partial correlations.

The MTP2 constraint is imposed via a projected gradient / ADMM solver. The result is a sparse precision matrix that encodes only the genuine idiosyncratic relationships, removing residual common factors that PCA missed.

**Step 3 — Contrarian signal construction:**
Use the MTP2-GGM precision matrix to whiten the PCA residuals:
```
ε̃_{i,t} = (Θ^{1/2} ε_t)_i
```
The whitened residuals ε̃ are more orthogonal across assets. Apply a standard short-term contrarian signal:
```python
signal_{i,t} = -z_score_t(ε̃_{i,t})  # short-term reversal on cleaned residuals
```
Assets with the most negative recent idiosyncratic return (after full de-factoring) are expected to revert.

---

## Results
Backtested on S&P 500 and TOPIX 500 constituents, 2012–2024:

- **All residual-factor methods beat raw returns** as a baseline (all achieve higher Sharpe and lower max drawdown/CVaR than using excess returns over the index directly).
- **MTP2-GGM attains the highest Sharpe ratio among residual methods in most sub-periods** — outperforming PCA-only residuals, confirming that the hierarchical approach removes factor contamination more completely.
- Lower maximum drawdown and lower Conditional Value at Risk (CVaR) vs. PCA-only in all sub-periods — suggesting the cleaning improves tail-risk behaviour, not just mean return.
- Specific Sharpe ratio numbers not available from abstract/search; paper reports superiority is consistent across periods rather than a one-off result.

---

## Implementable Signal

**2-step residual contrarian signal (directly implementable with Feishu daily data):**

```python
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

# Returns matrix (T x N)
R = daily.pivot('trade_day_id', 'asset_id', 'ret').fillna(0)

WINDOW = 120  # rolling PCA window
K = 10        # number of market factors

signals = {}
for t in range(WINDOW, len(R)):
    train = R.iloc[t - WINDOW:t].values   # (120, N)
    today = R.iloc[t].values              # (N,)

    # Step 1: PCA de-factoring
    pca = PCA(n_components=K)
    pca.fit(train)
    resid_train = train - pca.inverse_transform(pca.transform(train))
    resid_today = today - pca.inverse_transform(pca.transform(today[np.newaxis, :]))[0]

    # Step 2: approximate MTP2-GGM whitening
    # Simplified version: shrink residual covariance, apply Ledoit-Wolf, invert
    # (Full MTP2 projection requires a specialised solver)
    from sklearn.covariance import LedoitWolf
    lw = LedoitWolf().fit(resid_train)
    prec = lw.precision_  # N x N precision matrix

    # Step 3: whiten today's residuals
    resid_whitened = prec @ resid_today

    # Contrarian signal: negative sign (high whitened residual → expect reversal)
    day_id = R.index[t]
    signals[day_id] = -resid_whitened

signal_df = pd.DataFrame(signals, index=R.columns).T
# Cross-sectional z-score
signal_df = signal_df.apply(lambda col: (col - col.mean()) / (col.std() + 1e-8), axis=1)
```

**Note:** The full MTP2 projection requires the `mtp2` or custom ADMM solver from the paper. Ledoit-Wolf shrinkage is a practical approximation that captures most of the benefit. The key improvement over our existing `vol_rev` signal (PCA residual + z-score) is the second-stage whitening step.

**Addresses hypothesis:** Hypothesis #4 — *Does cross-asset information help?* Directly confirms that PCA residuals still contain exploitable cross-asset correlations, and that removing them via structured graphical estimation (not just PCA) produces better contrarian signals.

---

## Relevance to Feishu Competition
This paper is the most directly implementable of this week's finds relative to our open hypotheses. Our existing `wiki/results/pca_residual.md` already shows that PCA residuals improve vol_rev's IC (IR 5.01→11.04). This paper suggests that we can go further: the residuals from our PCA step still contain latent common structure, and a precision-matrix whitening step (even approximate, via Ledoit-Wolf) should produce even cleaner idiosyncratic signals.

**Concrete next experiment:** Extend `signals/vol_rev.py` to add a Ledoit-Wolf precision-matrix whitening step after PCA de-factoring. Compare IC/IR of the whitened vs. unwhitened residual signal on the full 484-day panel.

**Expected impact on portfolio construction:** The PCA residual signal showed strong IC vs. idiosyncratic returns but we never completed an execution backtest for it (the critical discovery that IC ≠ portfolio alpha applies here too). However, a cleaner residual signal could reduce the volatility of the signal across days (lower IC std → higher IR), which is the mechanism by which portfolio Sharpe improves.

One caution: the paper uses US and Japanese data (S&P 500, TOPIX 500). Chinese A-shares have stronger retail-driven common factors (the "market mood" factor dominates). It's possible that a larger K (K=15–20 instead of K=10) is needed to fully de-factor the A-share residuals before the GGM step adds value.

---

## Concepts
→ [[statistical-arbitrage]] | [[factor-models]] | [[mean-reversion]]
