"""
Return consistency signal: rolling fraction of positive-return days (hit rate).

A stock with a high hit rate earns positive returns on most days — this directly
translates to a higher Sharpe ratio and lower drawdown in any portfolio that holds
it. Unlike low_vol, which is agnostic to the direction of price movement, hit rate
filters for stocks that are genuinely grinding upward.

In a bear market: selects the few stocks that are consistently positive (defensive
SOEs, dividend payers, sector leaders that are accumulation targets).
In a bull market: selects stocks that are broadly participating in the uptrend.

Hit rate is also more robust than the 60d raw return because it is bounded [0, 1]
and resistant to single large-return outliers.

Data needed: daily only.
"""

import numpy as np
import pandas as pd


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    window: int = 60,
    excl_illiq: float = 0.05,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    daily      : raw daily OHLCV DataFrame
    lob        : ignored
    window     : rolling window for hit-rate computation (default 60)
    excl_illiq : fraction of most illiquid stocks to exclude (default 0.05)

    Returns
    -------
    pd.DataFrame : (trade_day_id x asset_id), cross-sectionally z-scored.
                   HIGH value = HIGH hit rate = favoured for selection.
    """
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    ret_mat = df.pivot(index="trade_day_id", columns="asset_id", values="ret")

    # Fraction of days with strictly positive return
    pos_indicator = (ret_mat > 0).astype(float)
    # Treat NaN returns as NaN (not zero)
    pos_indicator[ret_mat.isna()] = np.nan
    hit_rate = pos_indicator.rolling(window, min_periods=window).mean()

    signal = hit_rate

    # Liquidity filter
    if excl_illiq > 0.0:
        amount_mat = df.pivot(index="trade_day_id", columns="asset_id", values="amount")
        liq_20d = amount_mat.rolling(20).mean()
        liq_threshold = liq_20d.quantile(excl_illiq, axis=1)
        illiquid_mask = liq_20d.lt(liq_threshold, axis=0)
        signal = signal.where(~illiquid_mask, np.nan)

    # Cross-sectional z-score
    signal = signal.sub(signal.mean(axis=1), axis=0).div(
        signal.std(axis=1).replace(0, np.nan), axis=0
    )

    return signal
