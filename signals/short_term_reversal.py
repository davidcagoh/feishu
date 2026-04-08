"""
Short-term cross-sectional reversal.

Hypothesis: assets with the highest relative return today tend to underperform tomorrow.
Driven by retail overreaction — well-documented in Chinese A-shares (stronger than in US).

Signal: negative cross-sectional z-score of today's adjusted return.
Data needed: daily only.
"""

import numpy as np
import pandas as pd


def compute(daily: pd.DataFrame, lob: pd.DataFrame | None = None) -> pd.DataFrame:
    df = daily.copy()
    df["adj_close"] = df["close"] * df["adj_factor"]
    df = df.sort_values(["asset_id", "trade_day_id"])

    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    # Filter limit-hit days — stock can't be traded, exclude from signal
    df.loc[df["ret"] > 0.095, "ret"] = np.nan
    df.loc[df["ret"] < -0.095, "ret"] = np.nan

    ret_matrix = df.pivot(index="trade_day_id", columns="asset_id", values="ret")

    # Cross-sectional z-score per day
    signal = ret_matrix.sub(ret_matrix.mean(axis=1), axis=0).div(
        ret_matrix.std(axis=1), axis=0
    )

    # Negate: high return today → short signal (expect reversal)
    return -signal
