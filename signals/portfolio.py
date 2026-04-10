"""
Signal-to-order converter for submission CSV generation.

Stateless mapping from z-scored signal pivot table to buy/sell percentages.
The actual portfolio simulation (T+1, costs, lot rounding) lives in eval/backtest.py.

Output format: trade_day_id, asset_id, buy_percentage, sell_percentage
  - Selected stocks: buy_percentage = 1/n_stocks, sell_percentage = 0
  - All other stocks: buy_percentage = 0,          sell_percentage = 1.0
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def signal_to_orders(
    signal: pd.DataFrame,
    n_stocks: int = 20,
) -> pd.DataFrame:
    """
    Convert z-scored signal pivot table to buy/sell percentage orders.

    Each day, the top-n_stocks assets by signal score receive equal-weight
    buy allocations. All other assets are flagged for full liquidation.

    Parameters
    ----------
    signal : pd.DataFrame
        Pivot table of z-scored signals: index = trade_day_id (strings like
        "D001"–"D484"), columns = asset_id (strings like "A000651").
        NaN entries are treated as missing and excluded from ranking.
    n_stocks : int
        Number of top-ranked stocks to buy each day. Equal-weight allocation.

    Returns
    -------
    pd.DataFrame with columns:
        trade_day_id    : str
        asset_id        : str
        buy_percentage  : float  (1/n_stocks for selected; 0 for others)
        sell_percentage : float  (0 for selected; 1.0 for others)
    """
    if n_stocks <= 0:
        raise ValueError(f"n_stocks must be positive, got {n_stocks}")

    buy_weight = 1.0 / n_stocks
    records: list[dict[str, object]] = []

    for day in signal.index:
        row = signal.loc[day].dropna()
        if row.empty:
            continue

        top_assets: set[str] = set(row.nlargest(n_stocks).index.tolist())

        for asset in signal.columns:
            in_top = asset in top_assets
            records.append({
                "trade_day_id": day,
                "asset_id": asset,
                "buy_percentage": buy_weight if in_top else 0.0,
                "sell_percentage": 0.0 if in_top else 1.0,
            })

    if not records:
        return pd.DataFrame(
            columns=["trade_day_id", "asset_id", "buy_percentage", "sell_percentage"]
        )

    return pd.DataFrame(records)


# ── CLI / smoke test ──────────────────────────────────────────────────────────

def main() -> None:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from signals import REGISTRY

    root = Path(__file__).parent.parent / "data"
    daily_path = root / "daily_sample.parquet"
    lob_path = root / "lob_sample.parquet"

    if not daily_path.exists():
        print(f"Sample file not found: {daily_path}")
        sys.exit(1)

    print("Loading sample data...")
    daily = pd.read_parquet(daily_path)
    lob = pd.read_parquet(lob_path) if lob_path.exists() else pd.DataFrame()

    # Use composite_daily for a quick smoke test (daily-only, always available)
    sig_name = "composite_daily"
    print(f"Computing signal: {sig_name}...")
    signal = REGISTRY[sig_name].compute(daily, None)

    print(f"Signal shape: {signal.shape}  (days × assets)")
    print(f"Sample signal values (first day, first 5 assets):")
    print(signal.iloc[0, :5].to_string())

    n_stocks = 20
    print(f"\nConverting to orders (n_stocks={n_stocks})...")
    orders = signal_to_orders(signal, n_stocks=n_stocks)

    print(f"Orders shape: {orders.shape}")
    print(f"Unique days: {orders['trade_day_id'].nunique()}")
    print(f"Unique assets: {orders['asset_id'].nunique()}")

    # Sanity checks
    buy_counts = orders[orders["buy_percentage"] > 0].groupby("trade_day_id").size()
    sell_counts = orders[orders["sell_percentage"] > 0].groupby("trade_day_id").size()
    print(f"\nBuy counts per day — min: {buy_counts.min()}, max: {buy_counts.max()}, "
          f"mean: {buy_counts.mean():.1f}")
    print(f"Sell counts per day — min: {sell_counts.min()}, max: {sell_counts.max()}, "
          f"mean: {sell_counts.mean():.1f}")

    # Check buy percentages sum to 1 per day (within float tolerance)
    buy_sums = orders.groupby("trade_day_id")["buy_percentage"].sum()
    assert np.allclose(buy_sums, 1.0, atol=1e-9), f"Buy percentages don't sum to 1: {buy_sums}"
    print("\nSanity check passed: buy_percentage sums to 1.0 per day.")

    # Preview first 5 rows of one day
    first_day = orders["trade_day_id"].iloc[0]
    sample_day = orders[orders["trade_day_id"] == first_day].head(5)
    print(f"\nSample orders for {first_day}:")
    print(sample_day.to_string(index=False))


if __name__ == "__main__":
    main()
