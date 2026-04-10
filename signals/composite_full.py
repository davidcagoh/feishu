"""
Full composite signal: optimal combination of daily + LOB signals.

Key discovery (2026-04-10): LOB signals are NEGATIVELY correlated with daily signals
in their IC time series (rho = -0.24 to -0.57). They capture orthogonal market regimes:
  - Daily signals (vol_rev, ptv): work when price/volume overreaction dominates
  - LOB signals (lob_imb, ofi_ou): work when order-book microstructure dominates

This negative IC correlation creates massive diversification — optimal IR jumps from
5.08 (daily composite) to 7.87 (full composite).

Optimal weights via Sigma^{-1} mu on 463 aligned days (full eval 2026-04-10):
  ofi_ou:         0.3474  (highest IC among LOB signals; r=-0.574 with ptv)
  lob_imbalance:  0.2829  (low IC_std; high IR=2.40 individually)
  volume_reversal:0.2542  (anchor daily signal; IR=5.01 individually)
  price_to_vwap:  0.1155  (complement to vol_rev; low cross-correlation)

Data needed: LOB (required — falls back to composite_daily if LOB not provided).
"""

import numpy as np
import pandas as pd

from signals import composite_daily, lob_imbalance, ofi_ou, price_to_vwap, volume_reversal

WEIGHTS = {
    "volume_reversal": 0.2542,
    "price_to_vwap": 0.1155,
    "lob_imbalance": 0.2829,
    "ofi_ou": 0.3474,
}


def compute(daily: pd.DataFrame, lob: pd.DataFrame | None = None) -> pd.DataFrame:
    if lob is None or lob.empty:
        # Degrade gracefully to the daily-only composite
        return composite_daily.compute(daily, lob)

    components = {
        "volume_reversal": volume_reversal.compute(daily, lob),
        "price_to_vwap": price_to_vwap.compute(daily, lob),
        "lob_imbalance": lob_imbalance.compute(daily, lob),
        "ofi_ou": ofi_ou.compute(daily, lob),
    }

    # Align all to common index/columns
    days = components["volume_reversal"].index
    assets = components["volume_reversal"].columns
    for df in components.values():
        days = days.intersection(df.index)
        assets = assets.intersection(df.columns)

    composite = sum(
        WEIGHTS[name] * components[name].loc[days, assets]
        for name in components
    )

    # Re-z-score cross-sectionally
    composite = composite.sub(composite.mean(axis=1), axis=0).div(
        composite.std(axis=1).replace(0, np.nan), axis=0
    )

    return composite
