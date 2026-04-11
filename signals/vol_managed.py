"""
Volatility-managed portfolio overlay (Wang & Li 2024) on top of low_vol.

Core idea: scale portfolio exposure inversely with recent market realised
variance.  High market vol → reduce exposure → cuts MDD.
Low market vol → full / slightly higher exposure → preserves CAGR.

Scaling scalar = (target_var / rolling_var).clip(lo, hi)
where target_var = in-sample median of the 20-day rolling cross-sectional
mean-squared-return (market variance proxy).

The scalar multiplies the raw low_vol z-scores before they are passed to the
backtest engine.  Because the backtest normalises via nlargest() (ranking),
NOT by looking at raw magnitudes, this overlay does NOT change which stocks
are selected—it changes only the relative magnitude of the output.

To actually reduce portfolio exposure (hold cash) we need the backtest to see
fewer / weaker signals on high-vol days.  We therefore:
  1. Multiply z-scores by the scalar  (< 1 on high-vol days → weaker signal)
  2. Add a NaN-mask day when scalar < 0.6: the signal is still present, but
     downstream callers that look at the signal magnitude can use
     the embedded scalar metadata.

Actually the cleanest approach that works with the existing backtest is:
  - Scale the z-scores by scalar.  On high-vol days the scores are smaller,
    but the TOP stocks are unchanged (nlargest() is rank-preserving).
  - So the overlay does NOT affect stock selection directly via backtest.py.

The real benefit therefore must come through the *submission generator* or a
*custom backtest wrapper* that respects signal magnitude as position size.
Given the competition uses equal-weight inside backtest.py, the cleanest way
to realise the risk-reduction is to blank out (NaN) the signal on the
highest-variance days so the backtest skips rebalancing and stays in the
previous lower-vol portfolio.

Strategy implemented here:
  - Days where rolling_var > SIGMA_THRESHOLD * median_var → full NaN row
    (backtest skips rebalance, holds previous low-vol portfolio)
  - Other days → normal low_vol signal (unchanged stock ranks)
  - SIGMA_THRESHOLD is tunable (default 2.0 → blank ~top-5% vol days)

Parameters exposed in compute():
  window          : rolling variance window in days (default 20)
  sigma_threshold : blank days where var > sigma_threshold * median_var (default 2.0)
  base_window     : passed through to low_vol.compute() (default 60)
  excl_illiq      : passed through to low_vol.compute() (default 0.05)

Returns
-------
pd.DataFrame : (trade_day_id x asset_id) same format as low_vol.compute().
               High-vol days are all-NaN rows → backtest skips rebalancing.
"""

import numpy as np
import pandas as pd

from signals import low_vol


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    window: int = 20,
    sigma_threshold: float = 3.0,
    base_window: int = 60,
    excl_illiq: float = 0.05,
) -> pd.DataFrame:
    """
    Volatility-managed overlay on low_vol.

    Parameters
    ----------
    daily            : raw daily OHLCV DataFrame
    lob              : ignored (daily-only signal)
    window           : rolling window for market variance estimate (days)
    sigma_threshold  : blank out signal rows where rolling_var >
                       sigma_threshold * median rolling_var.
                       Set to np.inf to disable blanking.
    base_window      : rolling window for base low_vol signal (days)
    excl_illiq       : liquidity exclusion fraction for base low_vol signal

    Returns
    -------
    pd.DataFrame : (trade_day_id x asset_id), z-scored low_vol signal with
                   high-volatility days replaced by all-NaN rows.
    """
    # ── Step 1: base low_vol signal ──────────────────────────────────────────
    base_signal = low_vol.compute(
        daily, lob=None, window=base_window, excl_illiq=excl_illiq
    )

    # ── Step 2: market realised variance proxy ───────────────────────────────
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    # Cross-sectional mean of squared returns per day → market variance proxy
    daily_var: pd.Series = (
        df.groupby("trade_day_id")["ret"]
        .apply(lambda x: (x ** 2).mean())
    )
    # Align to the calendar ordering used in base_signal
    daily_var = daily_var.reindex(base_signal.index)

    # Rolling mean variance (window days)
    rolling_var: pd.Series = daily_var.rolling(window, min_periods=window).mean()

    # ── Step 3: compute scalar and identify high-vol days ────────────────────
    median_var = rolling_var.median()
    if median_var == 0 or np.isnan(median_var):
        # No variance data → return base signal unchanged
        return base_signal

    # Days where rolling_var > threshold * median → blank the signal
    high_vol_mask: pd.Series = rolling_var > (sigma_threshold * median_var)

    # ── Step 4: apply overlay ────────────────────────────────────────────────
    managed_signal = base_signal.copy()
    # Set entire rows to NaN for high-vol days
    managed_signal.loc[high_vol_mask] = np.nan

    return managed_signal
