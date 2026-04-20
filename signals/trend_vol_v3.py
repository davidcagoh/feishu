"""
Trend-Vol v3: trend_vol_v2 selection + ERC (equal risk contribution) weights.

This is the current best strategy as of 2026-04-20.

Stock selection: identical to trend_vol_v2 (low-vol + 35d positive-trend filter
+ vol-blanking overlay from vol_managed_v2).

Capital allocation: 1/σᵢ weighting (inverse volatility), so each position
contributes approximately equal risk to the portfolio.

Why ERC helps on the trend-filtered universe but not on the unfiltered one:
- When tested on vol_managed_v2 alone, ERC gave Score=0.3268 vs equal-weight 0.3296
  (slight degradation: the unfiltered universe has enough vol diversity that ERC
  shifts too much weight to extreme-low-vol names)
- On trend_vol_v2's filtered universe (low vol AND positive trend), the remaining
  20 stocks are more homogeneous, and ERC's marginal reallocation toward the
  quietest names adds a small but consistent SR improvement

Backtest result (D001–D484, sell-at-open, N=20):
  CAGR = 12.55%  SR = 1.231  MDD = 11.04%  Score = 0.3981
  vs trend_vol_v2 equal-weight N=20: Score = 0.3877  (+2.7% relative)
  vs vol_managed_v2 (prior best):     Score = 0.3296  (+20.8% relative)

Data needed: daily only.
"""

import pandas as pd

from signals import trend_vol_v2, erc_vol_managed


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    trend_window: int = 35,
) -> pd.DataFrame:
    """Stock selection: identical to trend_vol_v2."""
    return trend_vol_v2.compute(daily, lob=lob, trend_window=trend_window)


def compute_weights(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    weight_window: int = 60,
) -> pd.DataFrame:
    """Capital allocation: inverse-volatility weights (1/σᵢ) per stock per day."""
    return erc_vol_managed.compute_weights(daily, lob=lob, weight_window=weight_window)
