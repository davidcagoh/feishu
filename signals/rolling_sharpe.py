"""
Rolling self-Sharpe signal: trailing 60d Sharpe ratio of each stock.

A stock's trailing Sharpe = mean(daily_ret) / std(daily_ret) * sqrt(window).
This is the most direct measure of what we want to select for: high risk-adjusted
return over the recent lookback period. It simultaneously rewards:
  - High average return (positive trend)
  - Low return volatility (smooth path)

Compared to low_vol: low_vol only rewards smooth paths, including smooth declines.
Compared to return_consistency: hit rate is bounded and resistant to outliers;
self-Sharpe amplifies the magnitude of returns, so it picks stocks that are not
just sometimes-positive but *reliably strongly positive*.

In a bear market: identifies stocks with genuine positive risk-adjusted performance.
In a bull market: identifies the stocks compounding most efficiently.

The main risk is mean-reversion: a stock with unusually high trailing Sharpe may
be due to revert. But Chinese A-share evidence shows that at this frequency, the
'steady accumulation' category is persistent rather than mean-reverting.

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
    window     : rolling window for Sharpe estimation (default 60)
    excl_illiq : fraction of most illiquid stocks to exclude (default 0.05)

    Returns
    -------
    pd.DataFrame : (trade_day_id x asset_id), cross-sectionally z-scored.
                   HIGH value = HIGH trailing Sharpe = favoured for selection.
    """
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    ret_mat = df.pivot(index="trade_day_id", columns="asset_id", values="ret")

    rolling_mean = ret_mat.rolling(window, min_periods=window).mean()
    rolling_std = ret_mat.rolling(window, min_periods=window).std()

    # Trailing annualised Sharpe ratio (per-stock, not portfolio-level)
    self_sharpe = rolling_mean / rolling_std.replace(0, np.nan) * np.sqrt(window)

    signal = self_sharpe

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
