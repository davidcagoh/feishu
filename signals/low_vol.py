"""
Minimum volatility signal: select stocks with the lowest rolling return volatility.

Key discovery (2026-04-10 backtest analysis): All reversal/IC-based signals have
NEGATIVE execution IC (vwap→next_open). The only reliable positive execution IC
signal is low volatility — defensive stocks that don't swing wildly.

Mechanism: In a bear market, low-vol stocks (SOEs, utilities, banks) maintain their
value and avoid the catastrophic limit-down spirals that destroy reversal strategies.
The 60-day window is optimal — captures genuine structural low-vol, not noise.

Backtest result (D001–D484, sell-at-close, N=100, excl_illiq=0.05):
  CAGR = +9.32%,  SR = +0.85,  MDD = 13.28%  ← with 5% liquidity filter
  CAGR = +8.63%,  SR = +0.79,  MDD = 12.80%  ← without filter

Liquidity filter: null out signal for stocks whose 20-day rolling `amount` falls
below the 5th cross-sectional percentile, preventing selection of micro-cap stocks
that face catastrophic limit-down spirals.

vs market: CAGR ≈ –20%,  vs reversal signals: CAGR ≈ –54%

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
    lob        : ignored (daily-only signal)
    window     : rolling window for volatility estimate in trading days (default 60)
    excl_illiq : fraction of most illiquid stocks to exclude (default 0.05 = bottom 5%)
                 Measured by 20-day rolling mean of `amount`. Set to 0.0 to disable.

    Returns
    -------
    pd.DataFrame : (trade_day_id x asset_id), cross-sectionally z-scored.
                   HIGH value = LOW volatility = favoured for selection.
                   Illiquid stocks receive NaN and are excluded from selection.
    """
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    ret_matrix = df.pivot(index="trade_day_id", columns="asset_id", values="ret")

    # Rolling volatility; negate so HIGH signal = LOW vol
    rolling_std = ret_matrix.rolling(window).std()  # min_periods=window (pandas default)
    signal = -rolling_std

    # Liquidity filter: null out illiquid stocks (bottom excl_illiq of cross-section)
    if excl_illiq > 0.0:
        amount_mat = df.pivot(index="trade_day_id", columns="asset_id", values="amount")
        liq_20d = amount_mat.rolling(20).mean()
        # Cross-sectional percentile threshold per day
        liq_threshold = liq_20d.quantile(excl_illiq, axis=1)  # Series indexed by day
        illiquid_mask = liq_20d.lt(liq_threshold, axis=0)
        signal = signal.where(~illiquid_mask, np.nan)

    # Cross-sectional z-score each day
    signal = signal.sub(signal.mean(axis=1), axis=0).div(
        signal.std(axis=1).replace(0, np.nan), axis=0
    )

    return signal
