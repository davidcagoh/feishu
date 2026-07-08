# Machine Learning Enhanced Multi-Factor Quantitative Trading: A Cross-Sectional Portfolio Optimization Approach with Bias Correction

**Authors:** Yimin Du  
**Venue/Source:** arXiv q-fin.PM  
**arXiv/DOI:** arXiv:2507.07107  
**Date:** v1 June 2, 2025; v2 updated May 9, 2026

---

## Core Claim
Rolling-window factor pipelines for Chinese A-share markets contain a subtle but costly flaw: daily ±10% price limits (±20% for STAR/ChiNext) render a fraction of closing prices non-executable, yet standard implementations ingest these values before any row-filtering — a failure mode termed "upstream contamination" that inflates apparent IC by 18% and reduces realised Sharpe by 0.44 points.

---

## Method
A Boolean tradability mask is constructed at data load time and threaded through every operator in the factor pipeline: moving averages, rolling correlations, cross-sectional ranks, and return computations. Dates where `|close/prev_close − 1| ≥ 0.099` are masked out before any window operator consumes them; the window denominator shrinks accordingly (count of tradable days, not calendar days). The result is that the model only learns to predict returns it can actually trade. A 213-factor GPU-vectorised engine is validated on a 3,000-stock synthetic Chinese market panel and on proprietary real data from 2022–2024.

---

## Results
| Dataset | Sharpe | Annualised Return |
|---------|--------|-------------------|
| Synthetic 3,000-stock panel (2010–2024 calibration) | **2.05** | ~20% |
| Real A-share proprietary data (2022–2024) | **1.63** | ~20% |
| Bias-uncorrected baseline | ~1.2 | ~15% |

The mask alone (no other changes) accounts for the IC inflation and Sharpe improvement. The bias is most acute for factors using rolling mean/std of returns because a single limit-move day at the edge of the window inflates aggregate level and variance estimates.

---

## Implementable Idea
Apply a limit-move exclusion mask when computing the 60-day rolling standard deviation in `low_vol.py`. Currently, days where a stock hits its ±10% limit are masked at SELECTION time (the stock itself is excluded if its most recent day is a limit day), but the rolling window still includes historical limit-move days when computing vol.

**Fix for `low_vol.py`:**
```python
import numpy as np

def tradability_mask(ret_series, limit=0.099):
    """Boolean mask: False on days where |return| >= limit (non-tradable)."""
    return ret_series.abs() < limit

def masked_rolling_std(ret_series, window=60, limit=0.099):
    """Rolling std computed only over tradable (non-limit) days."""
    mask = tradability_mask(ret_series, limit)
    def _std(vals):
        tradable = vals[~np.isnan(vals)]  # already filtered by mask below
        return tradable.std() if len(tradable) >= 10 else np.nan
    masked = ret_series.where(mask)  # NaN on limit days
    return masked.rolling(window, min_periods=10).std()  # NaN treated as missing

# Replace in low_vol.py:
# daily['vol_60d'] = daily.groupby('asset_id')['ret'].transform(
#     lambda x: x.rolling(60).std()   # OLD
# )
daily['vol_60d'] = daily.groupby('asset_id')['ret'].transform(
    lambda x: masked_rolling_std(x, window=60)  # NEW
)
```

This is complementary to Signal #34 (MAD vol): the tradability mask excludes limit-move days entirely, while MAD is a robust estimator that downweights remaining outliers. Combining both gives a cleaner vol ranking.

**Addresses priority:** Priority 3 — Stock selection within the low-vol universe (cleaner, bias-corrected vol estimates improve the ranking quality of the core `low_vol.py` selection step).

---

## Relevance to Feishu Competition
Our `low_vol.py` computes rolling std over all available trading days including days where stocks hit ±10% limits. These are non-tradable closing prices (the price is the administrative limit, not a market-clearing price) and their inclusion inflates the vol estimate of stocks that have experienced occasional limit moves within the 60-day window. This could cause us to:
1. Incorrectly exclude a fundamentally quiet stock that had one limit-down day in the window
2. Incorrectly include a more volatile stock whose limit moves happened outside the window

The tradability mask fix (Signal #35) should improve the vol ranking precision at no cost. Since the competition is filed, this is a post-competition improvement. In a future version of the strategy, apply `masked_rolling_std` in `low_vol.py` and run a portfolio backtest to quantify the improvement.

---

## Concepts
-> [[chinese-ashore-market]] | [[statistical-arbitrage]] | [[factor-models]]
