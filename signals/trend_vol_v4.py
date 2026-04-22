"""
Trend-Vol v4: softened trend threshold (-0.025) + ERC weights.

Improvement over trend_vol_v3 (threshold=0.00):
  - Threshold -0.025 allows stocks flat-to-slightly-down over 35d into the eligible set.
    On bear-market days when most stocks decline, this gives more candidates → better
    portfolio diversification → lower drawdown.
  - Same ERC (1/σ) allocation weights as trend_vol_v3.

Why -0.025 and not -0.030:
  - -0.030 is the equal-weight IS peak but is a local spike (neighbours -0.027=0.3898,
    -0.033=0.3739 are notably lower), suggesting data-specific luck at exactly 3%.
  - -0.025 sits on a smoother plateau in ERC space (0.4024 vs 0.4050 at -0.027,
    0.4079 at -0.030) and is the most conservative improvement above current best.
  - MDD improvement is robust across the entire -0.020 to -0.040 range (~7.97-8.44%
    vs 11.04% for trend_vol_v3), so the mechanism holds regardless of exact threshold.

Backtest result (D001–D484, sell-at-open, N=20, ERC weights):
  CAGR = 11.75%  SR = 1.207  MDD = 7.98%  Score = 0.4024
  vs trend_vol_v3: Score = 0.3981  (+1.1% relative)
  vs trend_vol_v2: Score = 0.3877  (+3.8% relative)

Data needed: daily only.
"""

import numpy as np
import pandas as pd

from signals import vol_managed_v2, erc_vol_managed


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    trend_window: int = 35,
    trend_threshold: float = -0.025,
) -> pd.DataFrame:
    """Stock selection: low-vol + vol-blanking + softened trend filter."""
    base_signal = vol_managed_v2.compute(daily, lob=None)

    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    adj_close_mat = df.pivot(
        index="trade_day_id", columns="asset_id", values="adj_close"
    )

    trend = adj_close_mat / adj_close_mat.shift(trend_window) - 1.0
    trend = trend.reindex(index=base_signal.index, columns=base_signal.columns)

    return base_signal.where(trend > trend_threshold, np.nan)


def compute_weights(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    weight_window: int = 60,
) -> pd.DataFrame:
    """Capital allocation: inverse-volatility weights (1/σᵢ) per stock per day."""
    return erc_vol_managed.compute_weights(daily, lob=lob, weight_window=weight_window)
