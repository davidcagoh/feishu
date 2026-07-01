# The Decision Geometry of Covariance Estimation for the Global Minimum-Variance Portfolio under Heavy Tails

**Authors:** Xavier Fonseca (Academy for AI, Games and Media, Breda University of Applied Sciences)
**Venue/Source:** arXiv
**arXiv/DOI:** arXiv:2606.27462
**Date:** June 25, 2026

---

## Core Claim
Standard covariance estimators are evaluated by matrix-norm loss (Frobenius or operator norm), but the GMVP objective is a portfolio weight vector, not the covariance matrix itself. The paper proves an **exact regret identity**: GMVP portfolio loss depends on the covariance estimation error only through its *projection onto the portfolio weight direction*, scaled by portfolio concentration and conditioning number — not through the full matrix error. Under heavy-tailed returns (tail index κ ∈ (2, 4)), this gives precise guidance on which estimators are decision-optimal rather than matrix-optimal.

---

## Method
1. **Regret decomposition:** Derives a closed-form expression for GMVP decision regret as a function of the projection of the estimation error matrix onto the true minimum-variance portfolio direction.
2. **Decision geometry:** Shows GMVP regret is invariant to a (p−1)-dimensional subspace of the p²-dimensional error matrix — specifically, invariant to the covariance-scale direction (isotropic scaling doesn't change portfolio weights).
3. **Heavy-tail extension:** Applies the framework to returns with power-law tails (κ ∈ (2, 4), where κ = 2 is infinite variance), establishing regret convergence rates for estimators in this regime.
4. **Numerical validation:** Monte Carlo simulations confirm that estimators minimising decision-regret (e.g., Tyler's M-estimator) outperform matrix-norm-minimisers on out-of-sample portfolio variance under heavy tails.

---

## Results
| Setting | Finding |
|---------|---------|
| Gaussian returns | Matrix-norm and decision-optimal estimators coincide (no benefit to decision-geometry approach) |
| Heavy tails κ ∈ (2, 4) | Decision-optimal estimator achieves lower out-of-sample portfolio variance than standard shrinkage estimators of comparable complexity |
| Portfolio concentration | High-concentration portfolios (few effective bets) are more sensitive to estimation error in the portfolio weight direction |
| Conditioning of Σ | Ill-conditioned covariance → regret bound larger; regularisation (shrinkage, factor structure) helps independently of heavy tails |

No specific Sharpe or CAGR benchmarks — primarily a theoretical paper with numerical validation.

---

## Implementable Idea
**Replace rolling sample standard deviation with a robust scale estimator (MAD or Qn) in `low_vol.py` stock ranking.** The paper's core insight is that for min-var decisions, heavy-tailed estimation errors in the direction of portfolio weights matter most. Since Chinese A-share returns exhibit heavy tails (daily returns with ± 10% limits produce a thick-tailed empirical distribution), sample standard deviation (which squares errors and is sensitive to outliers) is a suboptimal estimator for the purpose of ranking stocks by volatility.

**Drop-in replacement:**
```python
import numpy as np

def mad_vol(series, window=60):
    """
    Median Absolute Deviation as a robust vol estimate.
    MAD × 1.4826 is a consistent estimator of std under normality,
    but resists outliers under heavy tails.
    """
    def rolling_mad(x):
        x = x.dropna()
        if len(x) < 10:
            return np.nan
        return np.median(np.abs(x - np.median(x))) * 1.4826
    return series.rolling(window).apply(rolling_mad, raw=False)

# In low_vol.py, replace:
#   daily['vol_60d'] = daily.groupby('asset_id')['ret'].transform(
#       lambda x: x.rolling(60).std()
#   )
# With:
#   daily['vol_60d'] = daily.groupby('asset_id')['ret'].transform(
#       lambda x: mad_vol(x)
#   )
```

The effect is that temporary spikes (e.g., stock hits ±10% limit, which would inflate sample std but is excluded from the MAD centre) do not inflate the vol ranking, giving a more stable cross-sectional ranking of truly-quiet stocks.

**Addresses priority:** Priority 2 — MDD reduction. A more robust vol ranking should reduce the incidence of selecting stocks that appear low-vol by sample std but actually carry tail risk (e.g., single ±10% limit day followed by a quiet period), potentially reducing MDD during adverse episodes.

---

## Relevance to Feishu Competition
Our `low_vol.py` uses 60-day rolling standard deviation for stock ranking. The Fonseca (2026) decision-geometry framework formally justifies replacing it with a robust estimator under heavy tails. Since Chinese A-share daily returns have fat tails — especially from the ±10% price limits which create a bimodal distribution — MAD-based ranking should produce a more stable low-vol portfolio. Expected benefit: fewer misclassified stocks (stocks that hit a limit-day and then go quiet, appearing low-vol); potential MDD reduction. This is a low-complexity, high-robustness drop-in change. Signal #34.

Note: the paper covers GMVP joint optimisation, but the decision-geometry insight (prioritise estimators that are accurate in the portfolio weight direction) applies equally to our greedy "rank by individual vol" step, which implicitly targets the lowest-vol stocks as the GMVP active set.

---

## Concepts
-> [[factor-models]] | [[mean-reversion]] | [[chinese-ashore-market]]
