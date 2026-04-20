"""
Quality composite signal: equal-weight average of three quality dimensions.

Three components, each cross-sectionally z-scored:
  1. Low volatility    (-rolling_std_60d)   — stable price path
  2. Return consistency (hit_rate_60d)       — positive returns most days
  3. Low beta          (-rolling_beta_60d)   — low systematic risk

The composite score rewards stocks that are simultaneously defensive on all three
dimensions. A stock that is excellent on one but poor on others scores less than
a stock that is consistently good on all three.

This differs from just using low_vol because:
  - Hit rate explicitly rewards positive direction (not just quietness)
  - Low beta is orthogonal to idiosyncratic vol (which drives low_vol)
  - The combination is more robust and less likely to select 'quiet decliners'

Liquidity filter is applied once at the end after combining z-scores.

Data needed: daily only.
"""

import numpy as np
import pandas as pd

from signals import low_beta, return_consistency, low_vol


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
    window     : rolling window for all three components (default 60)
    excl_illiq : liquidity exclusion fraction (default 0.05)

    Returns
    -------
    pd.DataFrame : (trade_day_id x asset_id), cross-sectionally z-scored.
                   HIGH value = HIGH quality composite = favoured for selection.
    """
    # Each component is already cross-sectionally z-scored and has the liquidity
    # filter applied. We re-apply the liquidity filter at the end on the composite.
    vol_sig = low_vol.compute(daily, lob=None, window=window, excl_illiq=0.0)
    hit_sig = return_consistency.compute(daily, lob=None, window=window, excl_illiq=0.0)
    beta_sig = low_beta.compute(daily, lob=None, window=window, excl_illiq=0.0)

    # Equal-weight average (NaN propagates if any component is NaN)
    composite = (vol_sig + hit_sig + beta_sig) / 3.0

    # Liquidity filter on composite
    if excl_illiq > 0.0:
        df = daily.copy().sort_values(["asset_id", "trade_day_id"])
        amount_mat = df.pivot(index="trade_day_id", columns="asset_id", values="amount")
        liq_20d = amount_mat.rolling(20).mean()
        liq_threshold = liq_20d.quantile(excl_illiq, axis=1)
        illiquid_mask = liq_20d.lt(liq_threshold, axis=0)
        illiquid_mask = illiquid_mask.reindex(
            index=composite.index, columns=composite.columns, fill_value=False
        )
        composite = composite.where(~illiquid_mask, np.nan)

    # Re-z-score the composite
    composite = composite.sub(composite.mean(axis=1), axis=0).div(
        composite.std(axis=1).replace(0, np.nan), axis=0
    )

    return composite
