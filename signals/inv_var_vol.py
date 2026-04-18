"""
Inverse-variance weighted volatility-managed portfolio (Signal #14).

Wang & Li (2024) Vol-Managed Portfolios paper shows OOS Sharpe ~1.50 vs ~0.99
unmanaged when weighting positions by 1/σ² instead of equally.

Stock SELECTION is identical to vol_managed (low-vol ranking + high-vol day blanking).
ALLOCATION changes: weight_i ∝ 1/σ²_i so the lowest-variance stocks get the most
capital — the theoretically optimal allocation for uncorrelated assets.

The backtest engine calls compute() for selection and compute_weights() for allocation;
it detects compute_weights via hasattr().
"""

import numpy as np
import pandas as pd

from signals import low_vol, vol_managed


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    window: int = 20,
    sigma_threshold: float = 3.0,
    base_window: int = 60,
    excl_illiq: float = 0.05,
) -> pd.DataFrame:
    """Selection signal: identical to vol_managed (top-N by low-vol, high-vol days blanked)."""
    return vol_managed.compute(
        daily,
        lob=lob,
        window=window,
        sigma_threshold=sigma_threshold,
        base_window=base_window,
        excl_illiq=excl_illiq,
    )


def compute_weights(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    base_window: int = 60,
    excl_illiq: float = 0.05,
) -> pd.DataFrame:
    """
    Inverse-variance weight matrix (trade_day_id × asset_id).
    Higher weight = lower variance = more capital allocated.
    Illiquid stocks get NaN (backtest falls back to equal weight for them).
    """
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    ret_matrix = df.pivot(index="trade_day_id", columns="asset_id", values="ret")
    rolling_var = ret_matrix.rolling(base_window, min_periods=base_window).var()

    # 1/σ² — stocks with zero variance get NaN (excluded)
    inv_var = 1.0 / rolling_var.replace(0, np.nan)

    # Apply same liquidity filter as low_vol
    if excl_illiq > 0.0:
        amount_mat = df.pivot(index="trade_day_id", columns="asset_id", values="amount")
        liq_20d = amount_mat.rolling(20).mean()
        liq_threshold = liq_20d.quantile(excl_illiq, axis=1)
        illiquid_mask = liq_20d.lt(liq_threshold, axis=0)
        inv_var = inv_var.where(~illiquid_mask, np.nan)

    return inv_var
