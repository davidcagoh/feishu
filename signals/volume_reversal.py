"""
Volume surprise reversal.

Hypothesis: unusually high volume relative to recent history signals retail
overreaction and predicts next-day reversal. Well-documented in Chinese A-shares
where retail traders chase volume spikes.

Signal: negative of today's volume / rolling-20-day-mean-volume, cross-sectionally z-scored.
Data needed: daily only (requires at least 21 days of history; NaN for early rows).
"""

import numpy as np
import pandas as pd


LOOKBACK = 20


def compute(daily: pd.DataFrame, lob: pd.DataFrame | None = None) -> pd.DataFrame:
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])

    rolling_mean = df.groupby("asset_id")["volume"].transform(
        lambda x: x.shift(1).rolling(LOOKBACK, min_periods=5).mean()
    )

    df["vol_ratio"] = df["volume"] / rolling_mean.replace(0, np.nan)

    vol_matrix = df.pivot(index="trade_day_id", columns="asset_id", values="vol_ratio")

    # Log-transform to reduce skew from spikes
    vol_matrix = np.log1p(vol_matrix)

    # Cross-sectional z-score, negate for reversal
    signal = vol_matrix.sub(vol_matrix.mean(axis=1), axis=0).div(
        vol_matrix.std(axis=1), axis=0
    )

    return -signal
