"""
Sanity-check the regime detector on IS data.

Prints per-label counts and a coarse timeline so we can eyeball whether
the detector flips at visually obvious regime changes. This validates
the classifier itself, not the strategy — no Score is computed here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from signals import regime  # noqa: E402


def main() -> None:
    daily = pd.read_parquet("data/daily_data_in_sample.parquet")
    labels = regime.regime_labels(daily)
    print(f"IS days: {len(labels)}")
    print("Label counts:")
    print(labels.value_counts())
    print()

    # Market cumulative return
    df = daily[["asset_id", "trade_day_id", "close", "adj_factor"]].copy()
    df["adj_close"] = df["close"] * df["adj_factor"]
    wide = df.pivot(index="trade_day_id", columns="asset_id", values="adj_close").sort_index()
    mret = wide.pct_change().mean(axis=1)
    cum = (1.0 + mret.fillna(0.0)).cumprod()

    # Segment the days by contiguous label runs so we can see timing
    df_seg = pd.DataFrame({"label": labels, "cum": cum}).reset_index()
    df_seg["group"] = (df_seg["label"] != df_seg["label"].shift()).cumsum()
    segs = (
        df_seg.groupby("group")
        .agg(
            label=("label", "first"),
            start=("trade_day_id", "first"),
            end=("trade_day_id", "last"),
            n=("trade_day_id", "count"),
            cum_start=("cum", "first"),
            cum_end=("cum", "last"),
        )
        .reset_index(drop=True)
    )
    segs["cum_delta_pct"] = (segs["cum_end"] / segs["cum_start"] - 1.0) * 100.0

    # Show all non-neutral segments (bull / stress) plus segment length >= 15
    interesting = segs[(segs["label"] != "neutral") | (segs["n"] >= 30)].copy()
    print("Notable regime segments:")
    print(interesting.to_string(index=False, float_format=lambda x: f"{x:7.2f}"))

    print()
    print(f"Bull  days: {(labels == 'bull').sum():4d}  ({(labels == 'bull').mean():.1%})")
    print(f"Neutral days: {(labels == 'neutral').sum():4d}  ({(labels == 'neutral').mean():.1%})")
    print(f"Stress days: {(labels == 'stress').sum():4d}  ({(labels == 'stress').mean():.1%})")


if __name__ == "__main__":
    main()
