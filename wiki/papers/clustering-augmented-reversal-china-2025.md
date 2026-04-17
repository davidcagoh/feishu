# Clustering-Augmented Reversal Strategy: Evidence from Chinese Stock Market

**Authors:** Weilin Jiao, Xu Zheng  
**Venue/Source:** Pacific-Basin Finance Journal (Elsevier)  
**arXiv/DOI:** doi:10.1016/j.pacfin.2025 (pii: S0927538X25003336)  
**Date:** November 2025 (online publication)  

---

## Core Claim
Applying K-means clustering to group stocks before constructing reversal portfolios generates significantly higher risk-adjusted returns than standard reversal strategies in Chinese A-shares. Clustering contributes 20–45% of total portfolio returns independently of the reversal component.

---

## Method
1. **Cluster stocks** using K-means on price/volume features (e.g. past-return, volatility, turnover) at each rebalance date. Number of clusters chosen via gap statistic or elbow method.
2. **Within-cluster reversal**: long the bottom-return quintile within each cluster, short the top-return quintile. Standard reversal is cross-cluster (all stocks together).
3. **Why clustering helps**: within a cluster, stocks share a common latent factor (e.g. sector, risk regime, style). Reversal after a shared shock mean-reverts faster and more reliably than reversal across unrelated stocks that may have moved for different reasons.
4. **Transition matrices**: show that mean reversion is more pronounced for past winners than losers, and is concentrated within clusters rather than between clusters.

---

## Results
| Strategy | Monthly alpha | Factor loadings |
|---|---|---|
| Standard reversal (A-shares) | baseline | positive MKT, SMB |
| **Clustering-augmented reversal** | **2.281–2.505%/month** | **None significant** |

Clustering independently contributes 20–45% of the total return gain. Technical factors (price, volume, volatility) are more effective cluster features than fundamental factors, consistent with retail dominance. Results are robust across different numbers of clusters (K = 5–15).

---

## Implementable Idea
The direct reversal strategy fails in our competition due to execution timing (signal captures overnight gap, we buy after it). However, the K-means clustering insight has a direct application to the **low_vol portfolio diversification problem**:

Our current low_vol portfolio has been shown to concentrate into ~12 core holdings with only 7 effective independent bets (see `wiki/results/sector_concentration.md`). Clustering can fix this:

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

def cluster_constrained_low_vol(daily, trade_day, N=20, n_clusters=10, lookback=60):
    """
    Select N lowest-volatility stocks ensuring representation across clusters.
    """
    # Build feature matrix for clustering
    recent = daily[daily['trade_day_id'] <= trade_day].groupby('asset_id').tail(lookback)
    features = recent.groupby('asset_id').agg(
        vol=('ret', 'std'),
        mean_ret=('ret', 'mean'),
        mean_vol_turnover=('amount', lambda x: np.log(x.mean() + 1))
    ).dropna()

    # K-means clustering
    scaler = StandardScaler()
    X = scaler.fit_transform(features)
    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    features['cluster'] = km.fit_predict(X)

    # Select floor(N/n_clusters) lowest-vol stocks per cluster, fill remainder globally
    stocks_per_cluster = max(1, N // n_clusters)
    selected = []
    for c in range(n_clusters):
        cluster_stocks = features[features['cluster'] == c].nsmallest(stocks_per_cluster, 'vol')
        selected.extend(cluster_stocks.index.tolist())

    # Fill remaining slots with globally lowest-vol stocks not yet selected
    remaining = features[~features.index.isin(selected)].nsmallest(N - len(selected), 'vol')
    selected.extend(remaining.index.tolist())

    return selected[:N]
```

This ensures the portfolio spans distinct volatility/return regimes rather than concentrating in a single correlated cluster (e.g. all utilities or all financials).

**Addresses priority:** Signal combination under correlated factors (hypothesis #1) — specifically the diversification gap in our low_vol portfolio. Also partially addresses sector concentration issue noted in `wiki/results/sector_concentration.md`.

---

## Relevance to Feishu Competition
Our current best (vol_managed, Score=0.3116) selects the N=20 lowest-volatility stocks, which tend to be highly correlated (mean pairwise r=0.33, 7 effective bets). If a single sector event hits the concentrated cluster:
- MDD spike that disproportionately hurts our score (Score weighs MDD at 25%).
- Our OOS period (D485–D726) may have different sector dynamics than in-sample.

Using clustering-constrained selection should:
1. Reduce pairwise correlation among selected stocks.
2. Increase effective number of independent bets from ~7 toward the full N=20.
3. Reduce MDD without sacrificing CAGR (lower concentration = lower idiosyncratic blow-up risk).

Try as Signal #20 in place of or alongside the current `signals/low_vol.py`.

---

## Concepts
-> [[chinese-ashore-market]] | [[mean-reversion]] | [[statistical-arbitrage]] | [[factor-models]]
