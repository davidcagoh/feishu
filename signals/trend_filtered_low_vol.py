"""
Trend-filtered low-vol signal: vol_managed_v2 base with declining-trend stocks removed.

The insight: low_vol selects quiet stocks, but 'quiet' includes stocks in a slow,
steady decline (value traps). Adding a trend filter removes stocks whose adjusted
close has been falling over the past N days, keeping only stocks that are at least
flat or gently rising within the low-vol universe.

In a bear market: the filter removes the worst 'dead weight' stocks from the
low-vol selection, potentially improving CAGR slightly.
In a bull market: the trend filter opens up the universe to include more
participating stocks when the low-vol universe is otherwise underperforming.

Trend criterion: 20d adjusted-close return > 0 (price is higher than 20 days ago).
This is a coarse but robust filter that avoids the noise of shorter windows and
the staleness of longer ones.

Data needed: daily only.
"""

import numpy as np
import pandas as pd

from signals import vol_managed_v2


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    trend_window: int = 20,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    daily        : raw daily OHLCV DataFrame
    lob          : ignored
    trend_window : lookback for trend direction filter (default 20)

    Returns
    -------
    pd.DataFrame : (trade_day_id x asset_id), same format as vol_managed_v2.
                   Stocks with negative trend over trend_window are set to NaN.
    """
    # Base signal: vol_managed_v2 (optimal tuned low-vol with vol-blanking)
    base_signal = vol_managed_v2.compute(daily, lob=None)

    # Compute adjusted-close matrix
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    adj_close_mat = df.pivot(index="trade_day_id", columns="asset_id", values="adj_close")

    # N-day price return as trend direction proxy
    trend = adj_close_mat / adj_close_mat.shift(trend_window) - 1.0

    # Align to base_signal index/columns
    trend = trend.reindex(index=base_signal.index, columns=base_signal.columns)

    # Zero out (NaN) stocks with negative trend — per stock per day
    # Stocks with NaN trend (insufficient history) are also excluded
    positive_trend = trend > 0
    filtered_signal = base_signal.where(positive_trend, np.nan)

    return filtered_signal
