"""
Submission generator for the Feishu/Lark Quant Competition.

Converts signal scores to the competition CSV format:
  trade_day_id, asset_id, buy_percentage, sell_percentage

Usage:
    # Generate from in-sample data (testing only)
    python eval/generate_submission.py --sample

    # Generate from OOS data (when D485–D726 is released on May 28)
    python eval/generate_submission.py \\
        --daily data/daily_data_oos.parquet \\
        --sell-mode open \\
        --n-stocks 20 \\
        --output submissions/TEAMID_sell_open.csv

Strategy: trend_vol_v2 (vol_managed_v2 base + 35d positive-trend filter per stock).
Parameters: trend_window=35, overlay_window=30, sigma_threshold=2.0, base_window=60, excl_illiq=5%.
N=20 stocks, sell-at-open.

trend_vol_v2 adds a per-stock trend filter to vol_managed_v2: stocks whose adjusted
close is lower than 35 trading days ago are excluded. This removes 'quiet decliners'
(value traps) from the low-vol universe without introducing momentum bias.

In-sample result (D001–D484, N=20, sell-at-open):
  trend_vol_v2   (tw=35): CAGR=+12.29%, SR=+1.202, MDD=11.21%, Score=0.3877
  vol_managed_v2 (prior): CAGR=+9.64%,  SR=+1.032, MDD=9.38%,  Score=0.3296
  low_vol        (base):  CAGR=+8.81%,  SR=+0.961, MDD=9.38%,  Score=0.3045
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
# trend_vol_v2: vol_managed_v2 base + 35d trend filter — best signal (Score=0.3877)
from signals import trend_vol_v2 as signal_module


# ── Core generator ─────────────────────────────────────────────────────────────

def generate_orders(
    daily: pd.DataFrame,
    sell_mode: str = "open",
    n_stocks: int = 20,
    vol_window: int = 60,
    excl_illiq: float = 0.05,
) -> pd.DataFrame:
    """
    Generate buy/sell orders for each (day, asset) based on the vol_managed signal.

    Parameters
    ----------
    daily      : daily OHLCV DataFrame with at least: asset_id, trade_day_id,
                 close, adj_factor, vwap_0930_0935, open
    sell_mode  : "open" or "close" — must match your chosen submission mode
    n_stocks   : number of stocks to hold each day (default 100)
    vol_window : base rolling window for low_vol volatility estimate (default 60)
    excl_illiq : fraction of most illiquid stocks to exclude per day (default 0.05)

    Returns
    -------
    pd.DataFrame with columns: trade_day_id, asset_id, buy_percentage, sell_percentage
    Each day sums: buy_percentage ≈ 1.0 across selected stocks.
                   sell_percentage = 1.0 for stocks to exit, 0.0 for holds.
    """
    if sell_mode not in ("open", "close"):
        raise ValueError(f"sell_mode must be 'open' or 'close', got {sell_mode!r}")

    signal = signal_module.compute(daily, lob=None, trend_window=35)
    days = sorted(signal.index)

    # Filter: skip assets with missing buy price on a given day
    buy_col = "vwap_0930_0935"
    vwap = daily.pivot(index="trade_day_id", columns="asset_id", values=buy_col)
    open_p = daily.pivot(index="trade_day_id", columns="asset_id", values="open")

    records: list[dict] = []
    prev_holdings: set[str] = set()

    for i, day in enumerate(days):
        if i == 0:
            continue  # no signal available before day 1

        prev_day = days[i - 1]
        if prev_day not in signal.index:
            continue

        prev_sig = signal.loc[prev_day].dropna()

        # Filter to assets with valid buy price today
        if day not in vwap.index:
            continue
        valid_buy = vwap.loc[day].dropna()
        valid_buy = valid_buy[valid_buy > 0]
        prev_sig = prev_sig.loc[prev_sig.index.intersection(valid_buy.index)]

        if len(prev_sig) < n_stocks:
            # Not enough valid assets — hold existing portfolio, no orders
            continue

        top_n = set(prev_sig.nlargest(n_stocks).index)

        # Equal weight across selected assets
        buy_pct = 1.0 / n_stocks

        # Buys: selected assets not already held (or partial rebalance)
        for asset in top_n:
            records.append({
                "trade_day_id": day,
                "asset_id": asset,
                "buy_percentage": buy_pct,
                "sell_percentage": 0.0,
            })

        # Sells: held assets not in new target
        for asset in prev_holdings - top_n:
            records.append({
                "trade_day_id": day,
                "asset_id": asset,
                "buy_percentage": 0.0,
                "sell_percentage": 1.0,
            })

        prev_holdings = top_n

    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame(columns=["trade_day_id", "asset_id", "buy_percentage", "sell_percentage"])

    # Aggregate in case an asset appears multiple times
    df = df.groupby(["trade_day_id", "asset_id"], as_index=False).sum()
    return df.sort_values(["trade_day_id", "asset_id"]).reset_index(drop=True)


# ── Validation ─────────────────────────────────────────────────────────────────

def validate_orders(orders: pd.DataFrame, min_stocks: int = 10) -> list[str]:
    """
    Run basic sanity checks. Returns a list of warning strings (empty = ok).
    """
    warnings: list[str] = []
    for day, grp in orders.groupby("trade_day_id"):
        buys = grp[grp["buy_percentage"] > 0]
        if len(buys) < min_stocks:
            warnings.append(f"Day {day}: only {len(buys)} buys (min {min_stocks})")
        total_buy = buys["buy_percentage"].sum()
        if not np.isclose(total_buy, 1.0, atol=0.01) and len(buys) > 0:
            warnings.append(f"Day {day}: buy_percentage sums to {total_buy:.4f} (expected 1.0)")
        if (grp["buy_percentage"] < 0).any():
            warnings.append(f"Day {day}: negative buy_percentage found")
        if (grp["sell_percentage"] < 0).any():
            warnings.append(f"Day {day}: negative sell_percentage found")
        if (grp["sell_percentage"] > 1.0 + 1e-6).any():
            warnings.append(f"Day {day}: sell_percentage > 1.0 found")
    return warnings


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate competition submission CSV")
    parser.add_argument("--daily", default=None,
                        help="Path to daily parquet file (default: auto-detect IS or sample)")
    parser.add_argument("--sample", action="store_true", default=False,
                        help="Use sample data for a quick smoke test")
    parser.add_argument("--sell-mode", choices=["open", "close"], default="open",
                        help="Sell mode: open or close (default: open)")
    parser.add_argument("--n-stocks", type=int, default=20,
                        help="Number of stocks to hold (default: 20)")
    parser.add_argument("--vol-window", type=int, default=60,
                        help="Volatility rolling window in days (default: 60)")
    parser.add_argument("--excl-illiq", type=float, default=0.05,
                        help="Exclude bottom N%% of stocks by 20d avg amount (default: 0.05)")
    parser.add_argument("--output", default=None,
                        help="Output CSV path (default: submissions/submission_<sell_mode>.csv)")
    args = parser.parse_args()

    root = Path(__file__).parent.parent

    # Determine data path
    if args.daily:
        daily_path = Path(args.daily)
    elif args.sample:
        daily_path = root / "data" / "daily_sample.parquet"
    else:
        daily_path = root / "data" / "daily_data_in_sample.parquet"

    if not daily_path.exists():
        print(f"ERROR: data file not found: {daily_path}")
        sys.exit(1)

    print(f"Loading daily data from: {daily_path.name}")
    daily = pd.read_parquet(daily_path)
    days = sorted(daily["trade_day_id"].unique())
    print(f"  {len(days)} trading days ({days[0]}–{days[-1]}), {daily['asset_id'].nunique()} assets")

    print(f"\nGenerating orders: trend_vol_v2(trend_window=35), N={args.n_stocks}, sell={args.sell_mode}")
    orders = generate_orders(
        daily,
        sell_mode=args.sell_mode,
        n_stocks=args.n_stocks,
        vol_window=args.vol_window,
        excl_illiq=args.excl_illiq,
    )

    print(f"  Generated {len(orders)} rows across {orders['trade_day_id'].nunique()} trading days")

    # Validate
    warnings = validate_orders(orders)
    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings[:10]:
            print(f"  {w}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more")
    else:
        print("  Validation: OK")

    # Summary stats
    buy_rows = orders[orders["buy_percentage"] > 0]
    sell_rows = orders[orders["sell_percentage"] > 0]
    print(f"\n  Buy orders:  {len(buy_rows)} rows (avg {buy_rows['buy_percentage'].mean():.4f} per row)")
    print(f"  Sell orders: {len(sell_rows)} rows")

    # Output path
    if args.output:
        out_path = Path(args.output)
    else:
        out_dir = root / "submissions"
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / f"submission_N{args.n_stocks}_sell_{args.sell_mode}.csv"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    orders.to_csv(out_path, index=False)
    print(f"\nSubmission written to: {out_path}")
    print(f"  Shape: {orders.shape}")
    print(f"  Columns: {list(orders.columns)}")
    print()
    print("Next steps:")
    print("  1. When OOS data is released (May 28), re-run with --daily data/daily_data_oos.parquet")
    print("  2. Verify submission CSV matches format in competition brief (§4)")
    print("  3. Submit before June 1 deadline")


if __name__ == "__main__":
    main()
