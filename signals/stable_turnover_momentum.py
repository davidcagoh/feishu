"""
Stable Turnover Momentum signal (Zhang, Chen & Xu, 2025).

Filters noisy momentum by requiring both price-path stability and turnover-rate
stability over the lookback window, then scales by idiosyncratic volatility.

Signal = momentum_return × price_stability × turnover_stability × IVOL

Where:
  momentum_return    = adj_close trailing 20-day return
  price_stability    = R² of linear fit of adj_close on time (monotone = high R²)
  turnover_stability = 1 / std(daily_turnover_ratio) — inverse of turnover noise
  IVOL               = std of market-residual daily returns (20-day trailing)

Data needed: daily only.
"""

import numpy as np
import pandas as pd
from scipy import stats


def _rolling_r2(price_matrix: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling R² of linear trend fit — measures how monotone the price path is."""
    r2 = pd.DataFrame(np.nan, index=price_matrix.index, columns=price_matrix.columns)
    days = list(price_matrix.index)
    x = np.arange(window, dtype=float)

    for i in range(window - 1, len(days)):
        day = days[i]
        window_prices = price_matrix.iloc[i - window + 1 : i + 1]
        r2_vals = {}
        for col in window_prices.columns:
            y = window_prices[col].values
            if np.isnan(y).sum() > window // 4:
                r2_vals[col] = np.nan
                continue
            mask = ~np.isnan(y)
            if mask.sum() < 5:
                r2_vals[col] = np.nan
                continue
            _, _, rval, _, _ = stats.linregress(x[mask], y[mask])
            r2_vals[col] = rval ** 2
        r2.loc[day] = r2_vals

    return r2


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    window: int = 20,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    daily  : raw daily OHLCV DataFrame
    lob    : ignored (daily-only signal)
    window : lookback window in trading days (default 20)

    Returns
    -------
    pd.DataFrame : (trade_day_id x asset_id), cross-sectionally z-scored.
                   HIGH value = strong stable upward trend with high IVOL.
    """
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    price_mat = df.pivot(index="trade_day_id", columns="asset_id", values="adj_close")
    ret_mat   = df.pivot(index="trade_day_id", columns="asset_id", values="ret")

    # Amount (turnover proxy)
    amount_mat = df.pivot(index="trade_day_id", columns="asset_id", values="amount")

    # ── Momentum return (20-day trailing) ────────────────────────────────────
    momentum = price_mat / price_mat.shift(window) - 1

    # ── Price stability: R² of linear fit (slow but correct) ─────────────────
    # Use rolling correlation as a faster proxy: |corr(t, price)| over window
    # This avoids the O(N*T) scipy loop for large matrices
    days = list(price_mat.index)
    t_arr = pd.DataFrame(
        {col: np.arange(len(days)) for col in price_mat.columns},
        index=days,
    )
    # Rolling correlation of time index with price = measure of trend linearity
    price_stability = t_arr.rolling(window).corr(price_mat) ** 2

    # ── Turnover stability: 1 / std(turnover ratio) ──────────────────────────
    turnover_mean = amount_mat.rolling(window).mean()
    turnover_ratio = amount_mat / turnover_mean.replace(0, np.nan)
    turnover_vol = turnover_ratio.rolling(window).std()
    turnover_stability = 1.0 / turnover_vol.replace(0, np.nan)

    # ── Idiosyncratic volatility: residual from market return ─────────────────
    market_ret = ret_mat.mean(axis=1)  # equal-weight market proxy
    market_aligned = pd.DataFrame(
        {col: market_ret for col in ret_mat.columns}, index=ret_mat.index
    )
    residuals = ret_mat - market_aligned
    ivol = residuals.rolling(window).std()

    # ── Composite signal ──────────────────────────────────────────────────────
    raw = momentum * price_stability * turnover_stability * ivol

    # Cross-sectional z-score
    signal = raw.sub(raw.mean(axis=1), axis=0).div(
        raw.std(axis=1).replace(0, np.nan), axis=0
    )

    return signal
