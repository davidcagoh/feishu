"""
Order Flow Imbalance with matched-filter normalization (Kang 2025, arXiv:2512.18648).

The canonical LOB imbalance normalizes by total level-1 volume (bid_vol_1 + ask_vol_1).
Kang (2025) shows that for detecting institutional order flow, the correct matched filter
is to normalize by a market-cap proxy rather than by the contemporaneous LOB volume.
In the Feishu dataset, daily `amount` (RMB turnover) serves as the market-cap proxy.

Two variants are implemented:

  ofi_mc         — level-1 only, normalized by amount (exposed as compute())
  ofi_multi_mc   — depth-weighted multi-level, normalized by amount

Both are cross-sectionally z-scored per day.
"""

import numpy as np
import pandas as pd


def compute(daily: pd.DataFrame, lob: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Level-1 OFI normalized by daily amount (market-cap proxy).

    Signal:
        raw_ofi(asset, day) = sum_t [ bid_volume_1(t) - ask_volume_1(t) ]
        ofi_mc(asset, day)  = raw_ofi / amount

    Returns a (trade_day_id × asset_id) DataFrame of cross-sectional z-scores.
    """
    all_days = sorted(daily["trade_day_id"].unique())
    all_assets = sorted(daily["asset_id"].unique())

    if lob is None or lob.empty:
        return pd.DataFrame(np.nan, index=all_days, columns=all_assets)

    # 1. Signed flow per snapshot
    df = lob[["asset_id", "trade_day_id", "bid_volume_1", "ask_volume_1"]].copy()
    df["signed_flow"] = df["bid_volume_1"] - df["ask_volume_1"]

    # 2. Sum across all snapshots per (asset_id, trade_day_id)
    daily_ofi = (
        df.groupby(["trade_day_id", "asset_id"])["signed_flow"]
        .sum()
        .reset_index()
        .rename(columns={"signed_flow": "daily_ofi_raw"})
    )

    # 3. Merge with daily amount
    amount_df = daily[["trade_day_id", "asset_id", "amount"]].copy()
    merged = daily_ofi.merge(amount_df, on=["trade_day_id", "asset_id"], how="left")

    # 4. Normalize by amount; mask where amount is zero or missing
    merged["ofi_mc"] = np.where(
        merged["amount"] > 0,
        merged["daily_ofi_raw"] / merged["amount"],
        np.nan,
    )

    # 5. Pivot to (day × asset)
    signal = merged.pivot(index="trade_day_id", columns="asset_id", values="ofi_mc")
    signal = signal.reindex(index=all_days, columns=all_assets)

    # 6. Invert: full-sample eval shows IC=-0.006, IR=-1.05 as-is.
    # Same Chinese retail FOMO dynamic as standard imbalance.
    signal = -signal

    # 7. Cross-sectional z-score per day
    signal = signal.sub(signal.mean(axis=1), axis=0).div(
        signal.std(axis=1), axis=0
    )

    return signal


def compute_multilevel(
    daily: pd.DataFrame, lob: pd.DataFrame | None = None
) -> pd.DataFrame:
    """
    Multi-level depth-weighted OFI normalized by daily amount.

    For levels k = 1..10:
        weighted_flow(t) = sum_k [ (1/k) * (bid_volume_k(t) - ask_volume_k(t)) ]

    Aggregated to daily, divided by amount, cross-sectionally z-scored.
    """
    all_days = sorted(daily["trade_day_id"].unique())
    all_assets = sorted(daily["asset_id"].unique())

    if lob is None or lob.empty:
        return pd.DataFrame(np.nan, index=all_days, columns=all_assets)

    levels = range(1, 11)
    bid_cols = [f"bid_volume_{k}" for k in levels]
    ask_cols = [f"ask_volume_{k}" for k in levels]

    # Check which level columns are actually present
    available_bid = [c for c in bid_cols if c in lob.columns]
    available_ask = [c for c in ask_cols if c in lob.columns]

    if not available_bid:
        # Fall back to level-1 only
        return compute(daily, lob)

    df = lob[["asset_id", "trade_day_id"] + available_bid + available_ask].copy()

    # Weighted signed flow per snapshot
    weighted = pd.Series(0.0, index=df.index)
    for k in range(1, len(available_bid) + 1):
        b_col = f"bid_volume_{k}"
        a_col = f"ask_volume_{k}"
        if b_col in df.columns and a_col in df.columns:
            weighted = weighted + (1.0 / k) * (df[b_col] - df[a_col])

    df["weighted_flow"] = weighted

    daily_ofi = (
        df.groupby(["trade_day_id", "asset_id"])["weighted_flow"]
        .sum()
        .reset_index()
        .rename(columns={"weighted_flow": "daily_ofi_raw"})
    )

    amount_df = daily[["trade_day_id", "asset_id", "amount"]].copy()
    merged = daily_ofi.merge(amount_df, on=["trade_day_id", "asset_id"], how="left")

    merged["ofi_multi_mc"] = np.where(
        merged["amount"] > 0,
        merged["daily_ofi_raw"] / merged["amount"],
        np.nan,
    )

    signal = merged.pivot(
        index="trade_day_id", columns="asset_id", values="ofi_multi_mc"
    )
    signal = signal.reindex(index=all_days, columns=all_assets)

    signal = signal.sub(signal.mean(axis=1), axis=0).div(
        signal.std(axis=1), axis=0
    )

    return signal
