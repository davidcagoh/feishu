"""
ERC-weighted vol_managed signal (Equal Risk Contribution).

Stock selection is identical to vol_managed_v2 (low-vol stocks, vol-blanking
overlay). The improvement is in how capital is allocated among selected stocks:
instead of equal weighting, each stock receives a weight inversely proportional
to its recent volatility (1/σᵢ), so every position contributes roughly equal
risk to the portfolio.

Why this should help vs equal weight:
  - Equal weighting on a low-vol universe still over-allocates risk to the
    higher-vol stocks within that universe (even though all are 'low-vol' vs
    the full cross-section, they vary materially amongst themselves).
  - 1/σ weighting shifts more capital to the most stable names, smoothing
    out daily portfolio variance → higher Sharpe ratio.
  - MDD should also decrease slightly because the largest losers on any
    given drawdown day are the higher-vol stocks, which now have smaller weights.

The backtest engine uses `compute_weights()` to allocate capital on new buys.

Data needed: daily only.
"""

import numpy as np
import pandas as pd

from signals import vol_managed_v2


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Stock selection: identical to vol_managed_v2."""
    return vol_managed_v2.compute(daily, lob=lob)


def compute_weights(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    weight_window: int = 60,
) -> pd.DataFrame:
    """
    Inverse-volatility weights for capital allocation among selected stocks.

    Returns a (trade_day_id x asset_id) DataFrame of unnormalised weights.
    The backtest normalises these across the new-buy set each day.

    Parameters
    ----------
    daily         : raw daily OHLCV DataFrame
    lob           : ignored
    weight_window : rolling window for per-stock vol estimate (default 60)
    """
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    ret_mat = df.pivot(index="trade_day_id", columns="asset_id", values="ret")
    rolling_std = ret_mat.rolling(weight_window, min_periods=weight_window).std()

    # Weight = 1/σ; replace 0-vol stocks with NaN (can't compute weight)
    inv_vol_weights = 1.0 / rolling_std.replace(0, np.nan)

    return inv_vol_weights
