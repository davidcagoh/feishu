"""
Alpha191 Factor 071 — 24-Day Percentage Deviation from Mean.

Price above its 24-day simple moving average is overextended and expected to
revert. Validated cross-market by double-selection LASSO (arXiv:2601.06499):
one of 17 Chinese factors that survive in the informationally-efficient US market.

Signal: -(adj_close - SMA_24) / SMA_24
  → positive = price below 24d average (cheap, expect bounce)
  → negative = price above 24d average (extended, expect reversion)

Data needed: daily only (close, adj_factor).
"""

import numpy as np
import pandas as pd


def compute(daily: pd.DataFrame, lob: pd.DataFrame | None = None) -> pd.DataFrame:
    all_days = sorted(daily["trade_day_id"].unique())
    all_assets = sorted(daily["asset_id"].unique())

    df = daily[["trade_day_id", "asset_id", "close", "adj_factor"]].copy()
    df["adj_close"] = df["close"] * df["adj_factor"]
    df = df.sort_values(["asset_id", "trade_day_id"])

    df["sma_24"] = df.groupby("asset_id")["adj_close"].transform(
        lambda x: x.rolling(24, min_periods=12).mean()
    )

    df["f071"] = np.where(
        df["sma_24"] > 0,
        (df["adj_close"] - df["sma_24"]) / df["sma_24"],
        np.nan,
    )

    # Negate: above SMA → extended → expect reversion (negative return)
    df["signal"] = -df["f071"]

    signal = df.pivot(index="trade_day_id", columns="asset_id", values="signal")
    signal = signal.reindex(index=all_days, columns=all_assets)

    # Cross-sectional z-score per day
    signal = signal.sub(signal.mean(axis=1), axis=0).div(
        signal.std(axis=1), axis=0
    )

    return signal
