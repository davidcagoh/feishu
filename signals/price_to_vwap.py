"""
Intraday drift reversal: close vs opening VWAP.

Hypothesis: stocks that rally hard from their opening VWAP tend to mean-revert
next day. Captures intraday momentum exhaustion, common in retail-driven A-shares.

Signal: negative of (close / vwap_0930_0935 - 1), cross-sectionally z-scored.
Data needed: daily only.
"""

import numpy as np
import pandas as pd


def compute(daily: pd.DataFrame, lob: pd.DataFrame | None = None) -> pd.DataFrame:
    df = daily.copy()

    mask = df["vwap_0930_0935"] > 0
    df["intraday_drift"] = np.nan
    df.loc[mask, "intraday_drift"] = (
        df.loc[mask, "close"] / df.loc[mask, "vwap_0930_0935"] - 1
    )

    drift = df.pivot(index="trade_day_id", columns="asset_id", values="intraday_drift")

    # Cross-sectional z-score, negate for reversal
    signal = drift.sub(drift.mean(axis=1), axis=0).div(drift.std(axis=1), axis=0)

    return -signal
