"""
Composite daily signal: optimally weighted combination of independent signal clusters.

Derivation (full 484-day eval, 2026-04-10):
  Five daily signals collapse to three independent clusters (IC correlation matrix):
    - Cluster A: short_term_reversal ↔ price_to_vwap  (r=0.930)
    - Cluster B: alpha191_046 ↔ alpha191_071          (r=0.939)
    - Cluster C: volume_reversal                       (standalone)

  Best per cluster by IR: price_to_vwap (Cluster A), alpha191_071 (Cluster B), volume_reversal (C).

  Optimal weights via Sigma^{-1} mu (maximum-IR portfolio over IC time series):
    volume_reversal: 0.85   (low IC std = 0.108; most efficient signal)
    price_to_vwap:   0.15   (low cross-correlation with vol_rev = 0.244)
    alpha191_071:    ~0      (IC std = 0.197; high noise cancels diversification benefit
                              despite raw IC matching volume_reversal)

  Grid-search confirms: [0.85, 0.00, 0.15] achieves IR=5.17 vs IR=5.00 for vol_rev alone.

Components used: volume_reversal + price_to_vwap only.
Data needed: daily only.
"""

import numpy as np
import pandas as pd

from signals import price_to_vwap, volume_reversal

WEIGHTS = {
    "volume_reversal": 0.85,
    "price_to_vwap": 0.15,
}


def compute(daily: pd.DataFrame, lob: pd.DataFrame | None = None) -> pd.DataFrame:
    components = {
        "volume_reversal": volume_reversal.compute(daily, lob),
        "price_to_vwap": price_to_vwap.compute(daily, lob),
    }

    # Align to common index/columns
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
