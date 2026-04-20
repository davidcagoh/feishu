"""
Low-beta stock selection signal.

Conceptually distinct from low_vol: low-vol captures both idiosyncratic and
systematic risk, while low-beta captures only systematic (market co-movement)
risk. In a bear market, low-beta stocks fall less because they're not correlated
with market declines. In a bull market, they also rise less — which is the key
OOS risk vs low_vol.

Mechanism: rolling 60d OLS beta of each stock's return vs equal-weighted
cross-sectional market return. Negate so high signal = low beta = preferred.

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
    window     : rolling window for beta estimation (default 60)
    excl_illiq : fraction of most illiquid stocks to exclude (default 0.05)

    Returns
    -------
    pd.DataFrame : (trade_day_id x asset_id), cross-sectionally z-scored.
                   HIGH value = LOW beta = favoured for selection.
    """
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    ret_mat = df.pivot(index="trade_day_id", columns="asset_id", values="ret")

    # Equal-weighted market return per day
    mkt_ret = ret_mat.mean(axis=1)

    # Rolling covariance of each stock with market, and market variance
    rolling_cov = ret_mat.rolling(window).cov(mkt_ret)
    rolling_mkt_var = mkt_ret.rolling(window).var()

    # Beta = Cov(stock, mkt) / Var(mkt)
    beta_mat = rolling_cov.div(rolling_mkt_var, axis=0)

    # Negate: high score = low beta
    signal = -beta_mat

    # Liquidity filter: same as low_vol
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
