# Market State Transitions and Crash Early Warning in the Chinese Stock Market

**Authors:** Wu-Yue Pang, Li Lin
**Venue/Source:** Frontiers in Physics (2025); SSRN working paper
**arXiv/DOI:** SSRN:5296493 / https://doi.org/10.3389/fphy.2025.1647667
**Date:** August 2025

---

## Core Claim
The Chinese stock market exhibits five distinct structural states detectable from rolling pairwise return correlation matrices via K-means clustering. Transitions between these states — especially sequences moving toward high-correlation "fragile" states — provide early warning of market crashes, achievable with high precision and recall from price-only data.

---

## Method
1. **State identification:** Compute rolling pairwise return correlation matrix across Chinese stocks over a 60-day window. Apply multidimensional scaling (MDS) to project to 2D. K-means clustering (K=5) identifies 5 structural market states reflecting varying degrees of systemic co-movement.
2. **Temporal features:** Engineer three feature classes capturing: (a) medium-term state proportions (which states the market occupied over past ~3 months), (b) directional change ratios (how frequently the market is moving toward fragile vs stable states), (c) short-term transition motifs (specific 3-state sequences in recent history).
3. **Crash classifier:** Decision tree trained on the temporal features in a walk-forward design; projection-based state labeling enables real-time application without refitting.

---

## Results
- 5 states show strong temporal persistence; markets tend to remain in one state for weeks before transitioning
- State transitions are directional: certain sequences (e.g., stable→moderate→fragile) reliably precede crash conditions
- Decision tree achieves high precision and recall across historical Chinese crash episodes
- Framework is real-time applicable: new days can be assigned to states via nearest-centroid projection without retraining

---

## Implementable Idea
Apply the rolling correlation → MDS → K-means pipeline to our IS data (D001–D484) to identify which of the 5 states the market is in at D484. This gives price-only OOS regime evidence independent of our vol-ratio detector:

```python
from sklearn.manifold import MDS
from sklearn.cluster import KMeans
import numpy as np, pandas as pd

returns = daily.pivot('trade_day_id', 'asset_id', 'ret').fillna(0)
WINDOW = 60

state_coords = []
for t in range(WINDOW, len(returns)):
    window_rets = returns.iloc[t-WINDOW:t]
    corr = window_rets.corr().values
    # Convert correlation to distance
    dist = np.sqrt(np.clip(2 * (1 - corr), 0, None))
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42, n_init=4)
    coords = mds.fit_transform(dist)
    state_coords.append(coords.mean(axis=0))  # market-level 2D coordinate

state_df = pd.DataFrame(state_coords, columns=['x', 'y'],
                        index=returns.index[WINDOW:])
km = KMeans(n_clusters=5, random_state=42, n_init=20)
state_df['state'] = km.fit_predict(state_df[['x', 'y']])

# Inspect state at end of IS (D484) and trend over D460–D484
print(state_df.tail(25)['state'].value_counts())
```

**Interpretation:** Low average correlation = stocks are diverging = market is idiosyncratic → typically a bull or recovery state (consistent with "slow bull" 2025 narrative). High average correlation = stocks crash together = fragile state → bear risk.

**What state D484 maps to confirms or challenges the v5 submission decision.**

**Addresses priority:** Priority 4 — OOS regime confirmation (HIGHEST URGENCY). Provides a price-only, Chinese-specific method to characterise D484's structural market state and assess the probability of continuing into OOS as a bull/slow-bull vs transitioning to a crash.

---

## Relevance to Feishu Competition
Our regime.py detector classifies D484 based on 22d vol vs 120d-median vol ratio. Known weakness: slow-bleed capitulation also shows low vol → false bull. This paper's 5-state correlation approach is ORTHOGONAL to vol level — it uses the STRUCTURE of cross-sectional co-movement (how correlated stocks are), not just the level of market volatility. Applying both detectors to D484 and checking agreement strengthens OOS regime confidence.

**If both agree on bull (low vol + low cross-sectional correlation): submit v5 (N=30, threshold=0.00 on bull days).**  
**If they disagree: conservative default is v4 (N=20, threshold=-0.025).**

The paper also provides temporal feature engineering ideas (medium-term state proportions, directional change ratios) that could improve our regime.py beyond the current binary vol-ratio threshold — but this is optional given our pre-committed decision rule.

---

## Concepts
-> [[chinese-ashore-market]] | [[mean-reversion]] | [[factor-models]]
