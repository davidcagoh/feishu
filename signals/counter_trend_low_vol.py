"""
Counter-trend within low-vol: selects quiet-pullback stocks from the vol_managed_v2 universe.

Mechanism: same low-vol + vol-blanking base as trend_vol_v3, but instead of requiring
positive 35d trend (trend > 0), requires a MILD NEGATIVE trend (-15% < trend < -3%).

Rationale:
- Avoids the execution-gap problem: we are NOT betting on overnight single-day reversal.
  We are betting that a stock quietly declining over 5–7 weeks will mean-revert over the
  following weeks.
- Complements trend_vol_v3: when trend_vol_v3 is fully invested in low-vol stocks that
  are holding up, this strategy is invested in low-vol stocks that have pulled back. The
  two universes are largely disjoint, so daily return correlation should be low.
- A 50/50 blend of the two could reduce MDD and improve Sharpe if the correlation is <0.3.

Parameters:
  pullback_lo = -0.15 : exclude stocks that have crashed (>15% drop — distress, not dip)
  pullback_hi = -0.03 : exclude stocks that are flat (less than 3% decline is noise)
  trend_window = 35   : same lookback as trend_vol_v3 for comparability

Backtest result: see wiki after running.
"""

import numpy as np
import pandas as pd

from signals import vol_managed_v2


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    trend_window: int = 35,
    pullback_lo: float = -0.15,
    pullback_hi: float = -0.03,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    daily        : raw daily OHLCV DataFrame
    lob          : ignored
    trend_window : lookback for trend measurement (default 35, matches trend_vol_v2)
    pullback_lo  : lower bound on 35d return (exclude crashes, default -0.15)
    pullback_hi  : upper bound on 35d return (exclude flat/up stocks, default -0.03)

    Returns
    -------
    pd.DataFrame : (trade_day_id x asset_id), same format as vol_managed_v2.
                   Only stocks in the pullback band are kept; all others NaN.
    """
    base_signal = vol_managed_v2.compute(daily, lob=None)

    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    adj_close_mat = df.pivot(
        index="trade_day_id", columns="asset_id", values="adj_close"
    )

    trend = adj_close_mat / adj_close_mat.shift(trend_window) - 1.0
    trend = trend.reindex(index=base_signal.index, columns=base_signal.columns)

    in_band = (trend > pullback_lo) & (trend < pullback_hi)
    return base_signal.where(in_band, np.nan)
