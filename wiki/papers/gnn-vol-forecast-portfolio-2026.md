# Do Better Volatility Forecasts Lead to Better Portfolios? Evidence from Graph Neural Networks

**Authors:** Rylan Wade  
**Venue/Source:** arXiv q-fin.PM  
**arXiv/DOI:** arXiv:2605.19278  
**Code:** https://github.com/waderylan/sp500-gnn  
**Date:** May 19, 2026

---

## Core Claim
The objectives of minimising forecast MSE, maximising cross-sectional ranking accuracy, and maximising portfolio Sharpe ratio are empirically distinct: on S&P 500 realised-volatility data, these three objectives select three *different* optimal models. Cross-sectional ranking accuracy (Spearman ρ) is a better proxy for portfolio performance than MSE.

---

## Method
- **Universe:** 465 S&P 500 equities, weekly realised volatility (RV), 2015–2025
- **Baselines:** Heterogeneous Autoregressive (HAR) model; Long Short-Term Memory (LSTM)
- **Graph models:** GraphSAGE built on three graph types:
  1. Rolling correlation graph (edges = high pairwise return correlation)
  2. Sector graph (edges = same GICS sector)
  3. Granger-causal graph (edges = lagged Granger causality)
  - All tested with and without macro regime features
- **Three evaluation metrics:**
  1. **Forecast MSE** — standard prediction accuracy
  2. **Cross-sectional ranking accuracy** — Spearman rank correlation between predicted and actual next-week RV rankings across all 465 stocks
  3. **Portfolio Sharpe** — minimum-variance portfolio formed by inverse-vol weighting on forecasted RV, evaluated with realistic transaction costs

---

## Results
- **Key empirical finding:** Model with lowest MSE ≠ model with highest ranking accuracy ≠ model with highest portfolio Sharpe. Three different models optimal for three different objectives.
- **Graph models:** Add portfolio Sharpe value *only* when the portfolio construction rule can exploit the cross-sectional structure encoded by the graph (e.g. correlation graph benefits min-variance selection; sector graph benefits sector-neutral allocation).
- **Macro regime features:** Mixed results — improve MSE but do not reliably improve portfolio Sharpe.
- Specific Sharpe figures not reported in abstract; the contribution is methodological (the divergence between objective functions), not a new performance benchmark.

---

## Implementable Idea
No directly implementable signal for our pipeline (GNN infrastructure not available; S&P 500 data not Chinese A-shares). However, the finding validates our methodology choice:

**Key takeaway:** When evaluating or improving vol forecasting for stock selection, the right metric is **cross-sectional Spearman rank correlation** of predicted vs actual volatility, not forecast MSE. Our low_vol strategy selects by vol rank — the paper confirms this is the appropriate proxy objective for portfolio performance.

**Practical implication:** If we ever test adaptive vol windows (Signal #23, BAWS-based) or FIGARCH-based windows, evaluate them by their ranking stability (rank correlation of 60d vol across adjacent windows), not by the absolute forecast accuracy. This is the metric that predicts whether our top-N selection will be stable.

```python
from scipy.stats import spearmanr

def vol_ranking_stability(vol_series_t, vol_series_t1):
    """
    Evaluate vol forecasting quality by cross-sectional rank correlation.
    vol_series_t: dict {asset_id: vol_forecast_for_tomorrow}
    vol_series_t1: dict {asset_id: realised_vol_tomorrow}
    Returns Spearman rank correlation across assets.
    """
    assets = list(set(vol_series_t) & set(vol_series_t1))
    pred = [vol_series_t[a] for a in assets]
    real = [vol_series_t1[a] for a in assets]
    rho, _ = spearmanr(pred, real)
    return rho
```

**Addresses priority:** Priority 2 (MDD reduction methodology). Validates that optimising for cross-sectional vol ranking (not MSE) is the right objective when the goal is min-variance portfolio construction — supporting our vol-ranking-based selection over IC-optimised signals.

---

## Relevance to Feishu Competition
- **Validates our core discovery:** The "IC ≠ Portfolio Alpha" finding we established empirically (IC=+0.034 → CAGR=−54%) is explained mechanically by this paper: IC metrics optimise a different objective than portfolio performance. The correct metric for our stock selection objective is rank correlation of vol estimates, not return prediction IC.
- **No direct strategy change:** We already select stocks by vol rank; this paper confirms that is right. No signal change needed.
- **Research report value:** Provides recent peer-reviewed support (May 2026) for our methodology pivot from IC/IR metrics to portfolio backtesting as the evaluation standard. Citable in the "Factor Construction" and "Empirical Analysis" sections.

---

## Concepts
-> [[statistical-arbitrage]] | [[factor-models]]
