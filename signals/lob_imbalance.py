"""
End-of-day LOB level-1 order imbalance.

Hypothesis: excess bid volume relative to ask volume signals buying pressure
and predicts positive next-day return.

Signal: (bid_vol_1 - ask_vol_1) / (bid_vol_1 + ask_vol_1), end-of-day snapshot,
cross-sectionally z-scored.
Data needed: LOB (falls back to NaN if not provided).

Variants to consider:
  - Mean imbalance over all snapshots (vs end-of-day)
  - Multi-level weighted imbalance: sum_k (1/k) * imbalance_k
  - Imbalance trend: end-of-day minus start-of-day imbalance
"""

import numpy as np
import pandas as pd


def compute(daily: pd.DataFrame, lob: pd.DataFrame | None = None) -> pd.DataFrame:
    all_days = sorted(daily["trade_day_id"].unique())
    all_assets = sorted(daily["asset_id"].unique())

    if lob is None or lob.empty:
        return pd.DataFrame(np.nan, index=all_days, columns=all_assets)

    df = lob.copy()
    total = df["bid_volume_1"] + df["ask_volume_1"]
    df["imbalance"] = np.where(
        total > 0,
        (df["bid_volume_1"] - df["ask_volume_1"]) / total,
        np.nan,
    )

    # End-of-day: last snapshot per (day, asset)
    eod = (
        df.sort_values("time")
        .groupby(["trade_day_id", "asset_id"])["imbalance"]
        .last()
        .reset_index()
    )

    signal = eod.pivot(index="trade_day_id", columns="asset_id", values="imbalance")

    # Reindex to full universe (NaN for days without LOB data)
    signal = signal.reindex(index=all_days, columns=all_assets)

    # Cross-sectional z-score per day (only where data exists)
    signal = signal.sub(signal.mean(axis=1), axis=0).div(
        signal.std(axis=1), axis=0
    )

    return signal
