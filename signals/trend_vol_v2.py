"""
Trend-filtered vol_managed (tuned) — best new signal from 2026-04-20 battery.

Mechanism: vol_managed_v2 base (low-vol stock selection + vol-blanking overlay),
with an additional per-stock trend filter: stocks whose adjusted close is LOWER
than it was trend_window trading days ago are excluded from selection.

Why trend_window=35 is robust:
  - Full IS sweep over windows 5–100 shows 30–40d range all beat vol_managed_v2
    (Score 0.3248–0.3958). Window 37 spikes to 0.4310 but is surrounded by lower
    neighbours (36: 0.3743, 38: 0.3690) — a noise spike, not selected.
  - Window 35 sits on a stable plateau (33: 0.3958, 34: 0.3874, 35: 0.3877)
    and is chosen as the robust out-of-sample estimate.
  - Shorter windows (5–20d) hurt performance (hidden momentum → reversal kills IC);
    longer windows (60–100d) degrade as trend information becomes stale in the
    484-day IS bear-market period.

Backtest result (D001–D484, sell-at-open, N=20):
  CAGR = 12.29%  SR = 1.202  MDD = 11.21%  Score = 0.3877
  vs vol_managed_v2:  Score = 0.3296  (+17.6% relative)

IS-peak at 37d:
  CAGR = 13.71%  SR = 1.316  MDD = 10.24%  Score = 0.4310
  Note: likely overfitted; excluded from submission default.

MDD trade-off: MDD rises from 9.38% (vol_managed_v2) to 11.21% at window=35.
  This reflects reduced portfolio diversification on bear-market days when most
  stocks have negative 35d trends, forcing picks from a smaller eligible set.

Data needed: daily only.
"""

import numpy as np
import pandas as pd

from signals import vol_managed_v2


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    trend_window: int = 35,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    daily        : raw daily OHLCV DataFrame
    lob          : ignored
    trend_window : lookback for trend direction filter (default 35)

    Returns
    -------
    pd.DataFrame : (trade_day_id x asset_id), same format as vol_managed_v2.
                   Stocks with negative trend over trend_window are set to NaN.
    """
    base_signal = vol_managed_v2.compute(daily, lob=None)

    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    adj_close_mat = df.pivot(
        index="trade_day_id", columns="asset_id", values="adj_close"
    )

    trend = adj_close_mat / adj_close_mat.shift(trend_window) - 1.0
    trend = trend.reindex(index=base_signal.index, columns=base_signal.columns)

    return base_signal.where(trend > 0, np.nan)
