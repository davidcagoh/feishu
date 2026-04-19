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

## Factor Risk, Hedging, and the Fixed-Income Analogy

The fixed income lecture (Lec 02) provides a direct analogy for equity factor risk management.

**Yield curve PCA factors → Equity covariance PCA factors**

| Fixed income factor | Description | Historical casualty |
|---|---|---|
| v₁ — parallel shift | All rates move together; duration risk | Silicon Valley Bank 2023 |
| v₂ — steepening | Short end vs long end diverge | Orange County 1994 (v₁-neutral but v₂-exposed) |
| v₃ — convexity | Belly of the curve vs ends | Beacon Hill hedge fund 2002 |

**Equity analogue for our strategy:**

| Equity factor | Description | Our exposure |
|---|---|---|
| v₁ — market beta | All stocks move with the market | HIGH — low_vol has beta ~0.5–0.7; long-only means always net long |
| v₂ — sector/style tilt | Growth vs value, defensive vs cyclical | Moderate — low_vol concentrates in defensive sectors |
| v₃ — idiosyncratic | Stock-specific | Low — diversified N=20 |

**Key insight:** Our `low_vol` portfolio is "long duration" in equity terms. It earns the risk premium from being long equity, but has lower beta than the market. In bear regimes this is excellent; in bull regimes it structurally underperforms. This is *precisely* the Priority 1 OOS risk.

**Tradeoff of hedging directional risk:**

- In bonds: going duration-neutral (v₁-hedge) sacrifices yield carry — you give up the premium from being long rates
- In equity: reducing market beta sacrifices the equity risk premium in bull markets
- Full hedge requires shorts — **not available in our long-only competition setup**
- Partial mitigation: regime-conditional beta management (bull → hold more / less-defensive stocks; bear → hold fewer / more defensive). This is the equity analogue of dynamic duration management.

**Orange County lesson:** He was v₁-neutral but had massive v₂ exposure (steepening). Lesson for us: hedging one factor while inadvertently concentrating in another (e.g. adding "bull-market stocks" that create sector concentration) is dangerous. Any regime-adaptive tilt must also control sector/style concentration.

**PCA residual connection:** Our confirmed result (vol_rev IR 5.01→11.04 after PCA residuals) is exactly "removing v₁ exposure from the signal" — projecting out the market-factor direction. This is signal-level directional hedging, not portfolio-level. It does not fix bull/bear sensitivity of the portfolio; it only removes market-factor contamination from the alpha signal.

---

## Papers in This Wiki
- [[attention-factors-stat-arb]] — Attention Factors: conditional factor model for arbitrage
- [[ai-asset-pricing-models]] — AIPM: transformer-based SDF / factor model for pricing
- [[statistical-arbitrage]] — how factor residuals become the trading signal
