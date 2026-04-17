# Explainable Regime Aware Investing

**Authors:** Amine Boukardagha  
**Venue/Source:** arXiv preprint (q-fin.PM)  
**arXiv/DOI:** arXiv:2603.04441  
**Date:** February/March 2026  

---

## Core Claim
A strictly causal Wasserstein Hidden Markov Model (Wasserstein HMM) embeds dynamically inferred regime probabilities into a transaction-cost-aware mean-variance optimisation framework, achieving Sharpe 2.18 versus 1.59 for equal-weight and 1.18 for SPX buy-and-hold, with dramatically lower drawdown.

---

## Method
- **Wasserstein HMM**: Rolling Gaussian HMM fitted causally (no look-ahead). The number of hidden regimes is chosen adaptively via predictive model-order selection.
- **Template identity tracking**: Regime labels are kept stable across roll windows by matching each new Gaussian component to an existing template using the 2-Wasserstein distance between Gaussian distributions — prevents label swapping as the window rolls.
- **Portfolio layer**: Regime probabilities (e.g. probability of being in a "stress" regime) are fed as soft constraints into a transaction-cost-penalised MV optimiser. The optimiser tilts away from risky assets in proportion to stress-regime probability, rather than using a hard binary switch.
- **Universe**: Diversified daily cross-asset universe; rolling walk-forward evaluation.

---

## Results
| Strategy | Sharpe | Max Drawdown |
|---|---|---|
| Wasserstein HMM portfolio | 2.18 | −5.43% |
| Equal-weight diversification | 1.59 | n/a |
| SPX Buy & Hold | 1.18 | −14.62% |

Compared to a nonparametric KNN conditional-moment estimator, the parametric regime model produces lower turnover and smoother weight evolution. Regime inference stability is highlighted as the first-order determinant of portfolio drawdown and implementation robustness.

---

## Implementable Idea
Replace the current vol_managed binary threshold (`variance > 3× median → skip rebalance`) with a soft Wasserstein-HMM regime probability overlay:

```python
from hmmlearn.hmm import GaussianHMM
import numpy as np

# Compute daily market features (e.g. cross-sectional vol, market return)
# Fit rolling 2-regime Wasserstein HMM on market_features[-window:]
# Wasserstein identity tracking: match each newly estimated component to the
# stored "stress" template by computing ||μ_new - μ_stored||^2 + ||Σ_new - Σ_stored||_F^2

def compute_stress_prob(features, n_regimes=2, window=120):
    hmm = GaussianHMM(n_components=n_regimes, covariance_type='full', n_iter=100)
    hmm.fit(features[-window:])
    posteriors = hmm.predict_proba(features[-1:])   # shape (1, n_regimes)
    # identify the stress regime as the one with higher mean vol
    stress_idx = np.argmax([hmm.means_[i][0] for i in range(n_regimes)])
    return posteriors[0, stress_idx]

# In vol_managed.py:
# Instead of: if market_var > threshold: skip
# Use: weight = 1 - alpha * stress_prob (alpha tunable in 0.3–1.0)
# This gives a continuum: high-stress days get reduced position, not binary zero
```

The soft overlay avoids cliff-edge rebalancing decisions and captures partial-stress regimes that the current binary threshold misses.

**Addresses priority:** Regime-conditional alpha (hypothesis #6) — volatility regimes and signal IC stability.

---

## Relevance to Feishu Competition
Our current vol_managed (Score=0.3116) uses a hard threshold that skips rebalancing entirely when market variance > 3× its in-sample median. This is crude:
- It misses partial-stress days where reducing (not eliminating) rebalancing would help.
- The threshold is calibrated on in-sample data and may be wrong for OOS.

The Wasserstein HMM approach replaces the threshold with a probability that self-calibrates. Key adaptation steps:
1. Use as features: 20-day cross-sectional return std and market average return (both available).
2. Fit a 2-state HMM (calm / stress) on the rolling 120-day feature window.
3. Weight the low_vol rebalancing signal by `(1 − stress_prob)` rather than the binary on/off.
4. This is a drop-in replacement for the current `signals/vol_managed.py` filter.

Expected uplift: modest SR improvement on the OOS period where the current 3× threshold may be mis-calibrated.

---

## Concepts
-> [[reinforcement-learning]] | [[factor-models]] | [[chinese-ashore-market]]
