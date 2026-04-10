"""
Alpha191 Factor 046 — Multi-Period Mean Reversion Ratio.

Price position within the trailing 20-day high/low range. A stock near its
rolling high is overbought and expected to revert. Validated cross-market by
double-selection LASSO (arXiv:2601.06499): one of 17 Chinese factors that
survive in the informationally-efficient US market.

Signal: -(adj_close - roll_min_20) / (roll_max_20 - roll_min_20)
  → positive = near rolling low (cheap, expect bounce)
  → negative = near rolling high (expensive, expect reversion)

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

    df["roll_max"] = df.groupby("asset_id")["adj_close"].transform(
        lambda x: x.rolling(20, min_periods=10).max()
    )
    df["roll_min"] = df.groupby("asset_id")["adj_close"].transform(
        lambda x: x.rolling(20, min_periods=10).min()
    )

    range_ = df["roll_max"] - df["roll_min"]
    df["f046"] = np.where(
        range_ > 0,
        (df["adj_close"] - df["roll_min"]) / range_,
        np.nan,
    )

    # Negate: high position in range → near high → expect reversion (negative return)
    df["signal"] = -df["f046"]

    signal = df.pivot(index="trade_day_id", columns="asset_id", values="signal")
    signal = signal.reindex(index=all_days, columns=all_assets)

    # Cross-sectional z-score per day
    signal = signal.sub(signal.mean(axis=1), axis=0).div(
        signal.std(axis=1), axis=0
    )

    return signal
