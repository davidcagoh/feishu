# Factor Models

Factor models decompose asset returns into a systematic component (shared across assets) and an idiosyncratic component (asset-specific). They're the foundation of both risk management and statistical arbitrage.

---

## General Form

```
R_{i,t} = α_i + β'_{i,t-1} F_t + ε_{i,t}

where:
  R_{i,t}    = return of asset i at time t
  F_t        = K-vector of factor returns
  β_{i,t-1}  = K-vector of factor loadings (sensitivities), known at t-1
  ε_{i,t}    = idiosyncratic return (zero-mean, low cross-asset correlation)
  α_i        = asset-specific intercept (mispricing if factors span SDF)
```

---

## Types of Factors

| Type | Examples | How estimated |
|------|---------|--------------|
| Observable/fundamental | Fama-French (market, size, value, momentum, profitability, investment) | Constructed from observable characteristics |
| Statistical (PCA) | Top K PCs of return covariance matrix | Unsupervised; maximise explained variance |
| Conditional (IPCA) | Latent factors with loadings as functions of characteristics | Supervised; link loadings to observable attributes |
| Attention Factors | Latent factors optimised for arbitrage profitability | End-to-end; joint with trading objective |

---

## PCA Factor Models

Standard PCA extracts factors that maximise explained variation:
```
Cov(R) = Γ Λ Γ'   (eigendecomposition)
F_t = Γ'_K R_t    (top K eigenvectors as factor portfolios)
```

**Problem for arbitrage**: PCA factors have high turnover and large short positions because they're optimised for variance, not trading. From [[attention-factors-stat-arb]]: "PCA factors have high turnover and large short positions, which diminish net performance."

---

## IPCA (Instrumented PCA)

Links latent factor loadings to observable characteristics:
```
β_{i,t-1} = X_{i,t-1} B      (loadings are linear in characteristics)
F_t = (X_{t-1} B)' R_t / N   (characteristic-weighted returns)
```

Better factor conditioning than unconditional PCA because characteristics `X` carry information about time-varying risk exposures.

---

## Weak Factors

A key insight from [[attention-factors-stat-arb]]: factors that explain **little variance** may still be highly valuable for identifying mispricing. Standard PCA selects factors by explained variance, discarding weak factors. But weak factors often capture idiosyncratic co-movement relevant to arbitrage.

**Intuition:** If 100 assets all have a small systematic component driven by some obscure characteristic, PCA will miss this as noise. But if this component is mean-reverting, it's highly tradeable.

---

## Stochastic Discount Factor Connection

From [[ai-asset-pricing-models]]: any factor model implies an SDF:
```
M_{t+1} = 1 - w(X_t)' R_{t+1}
```
where `w(X_t)` is the max-SR portfolio. The SDF prices all assets by construction: `E[M_{t+1} R_{i,t+1}] = 0`.

Characteristic-managed factor portfolios `F_{t+1} = X'_t R_{t+1}` are a natural basis for the SDF.

---

## Feishu Competition Notes

**Without fundamental characteristics**, we must construct factor proxies from price/volume/LOB:

| Proxy factor | Construction | Economic meaning |
|-------------|-------------|-----------------|
| Market factor | Equal-weighted return | Systematic market exposure |
| Size proxy | Volume-weighted return (large stocks = high volume) | Liquidity / size |
| Momentum factor | Return-weighted portfolio (past winners long, losers short) | Trend |
| LOB factor | LOB-imbalance-weighted portfolio | Microstructure pressure |
| Volatility factor | Portfolio ranked by realised volatility | Vol risk |

**Minimal implementation:**
```python
# Compute daily cross-sectional PCA factors
from sklearn.decomposition import PCA

# returns matrix: (days x assets)
returns_matrix = daily.pivot(index='trade_day_id', columns='asset_id', values='ret')
returns_matrix = returns_matrix.fillna(0)

# Rolling PCA (or expanding window)
pca = PCA(n_components=10)
# ... fit on training window, extract factors F_t, compute residuals ε_{i,t}
```

---

## Papers in This Wiki
- [[attention-factors-stat-arb]] — Attention Factors: conditional factor model for arbitrage
- [[ai-asset-pricing-models]] — AIPM: transformer-based SDF / factor model for pricing
- [[statistical-arbitrage]] — how factor residuals become the trading signal
