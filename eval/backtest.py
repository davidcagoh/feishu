"""
Portfolio backtester for the Feishu/Lark Quant Competition.

Replicates competition mechanics exactly:
  - Capital: RMB 50,000,000
  - Buy price: vwap_0930_0935 (skip asset if NaN)
  - Sell price: open (sell_mode="open") or close (sell_mode="close")
  - T+1 settlement: shares bought on day t cannot be sold until day t+1
  - Lot size: 100 shares (round DOWN)
  - Min 10 stocks held end-of-day; skip rebalance if not achievable
  - Transaction costs: buy max(turnover*0.0001, 5);
                       sell max(turnover*0.0001, 5) + turnover*0.0005
  - No leverage; no short selling

Scoring: 0.45 * CAGR + 0.30 * Sharpe + 0.25 * (-MDD)  [raw, not pct-ranked]
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd


# ── Cost helpers ──────────────────────────────────────────────────────────────

def _buy_cost(turnover: float) -> float:
    return max(turnover * 0.0001, 5.0)


def _sell_cost(turnover: float) -> float:
    return max(turnover * 0.0001, 5.0) + turnover * 0.0005


# ── Metrics ───────────────────────────────────────────────────────────────────

def _compute_cagr(portfolio_value: pd.Series, n_days: int, initial_capital: float) -> float:
    """Annualised return assuming 242 trading days per year."""
    if n_days <= 0:
        return float("nan")
    final = portfolio_value.iloc[-1]
    return (final / initial_capital) ** (242.0 / n_days) - 1.0


def _compute_sharpe(portfolio_value: pd.Series) -> float:
    """Annualised Sharpe ratio from daily portfolio values."""
    daily_returns = portfolio_value.pct_change().dropna()
    if len(daily_returns) < 2:
        return float("nan")
    std = daily_returns.std()
    if std == 0:
        return float("nan")
    return daily_returns.mean() / std * math.sqrt(242)


def _compute_mdd(portfolio_value: pd.Series) -> float:
    """Maximum drawdown as a positive fraction (e.g. 0.15 = 15%)."""
    cum_max = portfolio_value.cummax()
    drawdown = (cum_max - portfolio_value) / cum_max
    return float(drawdown.max())


# ── Main backtest ─────────────────────────────────────────────────────────────

def run_backtest(
    daily: pd.DataFrame,
    signal: pd.DataFrame,
    sell_mode: str = "open",
    n_stocks: int = 20,
    initial_capital: float = 50_000_000.0,
    weights: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """
    Full portfolio simulator matching competition mechanics.

    Parameters
    ----------
    daily : pd.DataFrame
        Raw daily OHLCV data with columns: asset_id, trade_day_id, open, high,
        low, close, volume, amount, adj_factor, vwap_0930_0935.
    signal : pd.DataFrame
        Pivot table of z-scored signals: index = trade_day_id, columns = asset_id.
        signal[t] is used to select stocks to BUY on day t+1.
    sell_mode : str
        "open"  — sell at today's open price.
        "close" — sell at today's close price.
    n_stocks : int
        Number of top-signal assets to hold each day.
    initial_capital : float
        Starting cash in RMB.
    weights : pd.DataFrame or None
        Optional allocation weight matrix (same shape as signal).
        When provided, new buy cash is allocated proportionally to weights
        instead of equally. Weights need not be normalised; they are
        normalised across the new-buy set each day.

    Returns
    -------
    dict with keys:
        portfolio_value : pd.Series  (trade_day_id → daily portfolio value at close)
        trades          : pd.DataFrame
        cagr            : float
        sharpe          : float
        mdd             : float
        n_days          : int
        score           : float  (raw 0.45*cagr + 0.30*sharpe + 0.25*(-mdd))
    """
    if sell_mode not in ("open", "close"):
        raise ValueError(f"sell_mode must be 'open' or 'close', got {sell_mode!r}")

    # ── Pre-index daily data for O(1) lookup ─────────────────────────────────
    daily_sorted = daily.sort_values(["trade_day_id", "asset_id"])
    all_days: list[str] = sorted(daily_sorted["trade_day_id"].unique().tolist())

    # Build per-day lookup: day -> {asset_id: {col: value}}
    # We only need: open, close, vwap_0930_0935
    price_cols = ["open", "close", "vwap_0930_0935"]
    day_prices: dict[str, dict[str, dict[str, float]]] = {}
    for day, grp in daily_sorted.groupby("trade_day_id"):
        day_prices[day] = {
            row["asset_id"]: {c: row[c] for c in price_cols}
            for _, row in grp.iterrows()
        }

    # ── State ─────────────────────────────────────────────────────────────────
    cash: float = initial_capital
    # holdings: asset_id -> shares (settled, available to sell)
    holdings: dict[str, int] = {}
    # bought_today: asset_id -> shares (T+1 locked, not yet available)
    bought_today: dict[str, int] = {}

    portfolio_value_list: list[tuple[str, float]] = []
    trade_records: list[dict[str, Any]] = []

    def _portfolio_close_value(day: str, local_holdings: dict[str, int], local_bought: dict[str, int]) -> float:
        total = cash
        prices = day_prices.get(day, {})
        for asset, shares in local_holdings.items():
            close = prices.get(asset, {}).get("close", float("nan"))
            if not math.isnan(close):
                total += shares * close
        for asset, shares in local_bought.items():
            close = prices.get(asset, {}).get("close", float("nan"))
            if not math.isnan(close):
                total += shares * close
        return total

    # Day 0 = initial capital (before any trades)
    # We prepend it after the loop with a synthetic label "D000" or just index 0
    # The spec says "Day 0 = initial_capital". We'll use the first real day's ID
    # with a note that it's the pre-trade value; portfolio_value starts at day[0].

    # ── Simulation loop ───────────────────────────────────────────────────────
    for i, day in enumerate(all_days):
        prices_today = day_prices.get(day, {})

        # Step 1: Determine target assets using PREVIOUS day's signal
        # signal[t-1] → buys on day t
        if i == 0:
            # No signal available before the first day — hold nothing, record value
            pv = _portfolio_close_value(day, holdings, bought_today)
            portfolio_value_list.append((day, pv))
            # Settle bought_today -> holdings (though holdings is empty day 0)
            for asset, shares in bought_today.items():
                holdings[asset] = holdings.get(asset, 0) + shares
            bought_today = {}
            continue

        prev_day = all_days[i - 1]

        # Signal from previous day
        if prev_day not in signal.index:
            target_set: set[str] = set()
        else:
            prev_signal = signal.loc[prev_day]
            prev_signal = prev_signal.dropna()
            # Filter to assets that have valid buy price today
            valid_assets = [
                a for a in prev_signal.index
                if a in prices_today
                and not math.isnan(prices_today[a].get("vwap_0930_0935", float("nan")))
                and prices_today[a]["vwap_0930_0935"] > 0
            ]
            prev_signal = prev_signal.loc[[a for a in valid_assets if a in prev_signal.index]]
            top_assets = prev_signal.nlargest(n_stocks).index.tolist()
            target_set = set(top_assets)

        # If fewer than 10 valid targets, skip rebalance — hold existing portfolio
        if len(target_set) < 10:
            # Settle T+1
            for asset, shares in bought_today.items():
                holdings[asset] = holdings.get(asset, 0) + shares
            bought_today = {}
            pv = _portfolio_close_value(day, holdings, bought_today)
            portfolio_value_list.append((day, pv))
            continue

        # Step 2: Sell phase
        # Sell settled holdings that are not in today's target
        sell_price_col = "open" if sell_mode == "open" else "close"
        assets_to_sell = [a for a in list(holdings.keys()) if a not in target_set]

        for asset in assets_to_sell:
            shares = holdings.pop(asset)
            if shares <= 0:
                continue
            sell_price = prices_today.get(asset, {}).get(sell_price_col, float("nan"))
            if math.isnan(sell_price) or sell_price <= 0:
                # Can't sell — put back in holdings
                holdings[asset] = shares
                continue
            turnover = shares * sell_price
            cost = _sell_cost(turnover)
            proceeds = turnover - cost
            cash += proceeds
            trade_records.append({
                "day": day,
                "asset_id": asset,
                "side": "sell",
                "shares": shares,
                "price": sell_price,
                "cost": cost,
                "turnover": turnover,
            })

        # Step 3: Buy phase (at vwap_0930_0935)
        # Only buy assets in target_set not already held (including locked)
        already_held = set(holdings.keys()) | set(bought_today.keys())
        to_buy = [a for a in target_set if a not in already_held]

        if to_buy:
            n_buys = len(to_buy)

            # Determine per-asset cash allocation
            if weights is not None and prev_day in weights.index:
                day_w = weights.loc[prev_day]
                buy_weights = {a: float(day_w.get(a, 0.0)) for a in to_buy}
                buy_weights = {a: w for a, w in buy_weights.items() if not math.isnan(w) and w > 0}
                w_total = sum(buy_weights.values())
                if w_total > 0:
                    per_asset_alloc = {a: cash * buy_weights.get(a, 0.0) / w_total for a in to_buy}
                else:
                    per_asset_alloc = {a: cash / n_buys for a in to_buy}
            else:
                per_asset_alloc = {a: cash / n_buys for a in to_buy}

            for asset in to_buy:
                buy_price = prices_today.get(asset, {}).get("vwap_0930_0935", float("nan"))
                if math.isnan(buy_price) or buy_price <= 0:
                    continue
                per_asset_allocation = per_asset_alloc[asset]
                raw_shares = per_asset_allocation / buy_price
                lots = int(raw_shares / 100)
                shares = lots * 100
                if shares <= 0:
                    continue
                turnover = shares * buy_price
                cost = _buy_cost(turnover)
                total_outlay = turnover + cost
                if total_outlay > cash:
                    # Re-compute with available cash
                    affordable = (cash - 5.0) / (buy_price * (1 + 0.0001))
                    lots = int(affordable / 100)
                    shares = lots * 100
                    if shares <= 0:
                        continue
                    turnover = shares * buy_price
                    cost = _buy_cost(turnover)
                    total_outlay = turnover + cost
                    if total_outlay > cash:
                        continue
                cash -= total_outlay
                bought_today[asset] = bought_today.get(asset, 0) + shares
                trade_records.append({
                    "day": day,
                    "asset_id": asset,
                    "side": "buy",
                    "shares": shares,
                    "price": buy_price,
                    "cost": cost,
                    "turnover": turnover,
                })

        # Step 4: End of day — record portfolio value at close
        pv = _portfolio_close_value(day, holdings, bought_today)
        portfolio_value_list.append((day, pv))

        # Settle T+1: move bought_today -> holdings for next day
        for asset, shares in bought_today.items():
            holdings[asset] = holdings.get(asset, 0) + shares
        bought_today = {}

    # ── Build outputs ─────────────────────────────────────────────────────────
    if not portfolio_value_list:
        portfolio_value = pd.Series(dtype=float)
    else:
        days_out, values_out = zip(*portfolio_value_list)
        # Prepend initial capital as day-0 entry (before first trading day)
        portfolio_value = pd.Series(
            [initial_capital] + list(values_out),
            index=["D000"] + list(days_out),
        )

    n_days = len(all_days)
    cagr = _compute_cagr(portfolio_value, n_days, initial_capital)
    sharpe = _compute_sharpe(portfolio_value)
    mdd = _compute_mdd(portfolio_value)
    score = 0.45 * cagr + 0.30 * sharpe + 0.25 * (-mdd)

    trades_df = pd.DataFrame(trade_records) if trade_records else pd.DataFrame(
        columns=["day", "asset_id", "side", "shares", "price", "cost", "turnover"]
    )

    return {
        "portfolio_value": portfolio_value,
        "trades": trades_df,
        "cagr": cagr,
        "sharpe": sharpe,
        "mdd": mdd,
        "n_days": n_days,
        "score": score,
    }


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from signals import REGISTRY

    parser = argparse.ArgumentParser(description="Run competition backtest")
    parser.add_argument("--sample", action="store_true", default=False,
                        help="Use sample data (fast, 20 days)")
    parser.add_argument("--signal", default="composite_full",
                        help="Signal name from REGISTRY (default: composite_full)")
    parser.add_argument("--sell-mode", choices=["open", "close"], default="open",
                        help="Sell price: open (default) or close")
    parser.add_argument("--n-stocks", type=int, default=20,
                        help="Number of stocks in portfolio (default: 20)")
    parser.add_argument("--lob", action="store_true", default=False,
                        help="Load LOB data (required for LOB signals)")
    args = parser.parse_args()

    root = Path(__file__).parent.parent / "data"
    if args.sample:
        daily_path = root / "daily_sample.parquet"
        lob_path = root / "lob_sample.parquet"
        print("Loading sample data...")
        daily = pd.read_parquet(daily_path)
        lob = pd.read_parquet(lob_path) if (args.lob and lob_path.exists()) else pd.DataFrame()
    else:
        daily_path = root / "daily_data_in_sample.parquet"
        print("Loading full daily data...")
        daily = pd.read_parquet(daily_path)
        if args.lob:
            lob_path = root / "lob_data_in_sample.parquet"
            if not lob_path.exists():
                print("  [warn] lob_data_in_sample.parquet not found — skipping LOB")
                lob = pd.DataFrame()
            else:
                all_days = sorted(daily["trade_day_id"].unique())
                print(f"  Loading LOB day-by-day ({len(all_days)} days)...", flush=True)
                chunks = []
                for i, day in enumerate(all_days, 1):
                    chunk = pd.read_parquet(lob_path, filters=[("trade_day_id", "==", day)])
                    chunks.append(chunk)
                    if i % 50 == 0:
                        print(f"    {i}/{len(all_days)} days loaded", flush=True)
                lob = pd.concat(chunks, ignore_index=True)
                print(f"  LOB loaded: {len(lob):,} rows", flush=True)
        else:
            lob = pd.DataFrame()

    sig_name = args.signal
    if sig_name not in REGISTRY:
        print(f"Unknown signal '{sig_name}'. Available: {list(REGISTRY)}")
        sys.exit(1)

    print(f"Computing signal: {sig_name}...")
    sig_module = REGISTRY[sig_name]
    signal = sig_module.compute(daily, lob if not lob.empty else None)

    wts = None
    if hasattr(sig_module, "compute_weights"):
        print(f"Computing weights: {sig_name}.compute_weights()...")
        wts = sig_module.compute_weights(daily, lob if not lob.empty else None)

    print(f"Running backtest (sell_mode={args.sell_mode}, n_stocks={args.n_stocks})...")
    result = run_backtest(
        daily=daily,
        signal=signal,
        sell_mode=args.sell_mode,
        n_stocks=args.n_stocks,
        weights=wts,
    )

    pv = result["portfolio_value"]
    print(f"\n{'='*50}")
    print(f"Signal:        {sig_name}")
    print(f"Sell mode:     {args.sell_mode}")
    print(f"N stocks:      {args.n_stocks}")
    print(f"Trading days:  {result['n_days']}")
    print(f"Start capital: RMB {50_000_000:,.0f}")
    print(f"Final value:   RMB {pv.iloc[-1]:,.0f}")
    print(f"CAGR:          {result['cagr']:.2%}")
    print(f"Sharpe:        {result['sharpe']:.3f}")
    print(f"Max drawdown:  {result['mdd']:.2%}")
    print(f"Raw score:     {result['score']:.4f}")
    print(f"{'='*50}")
    print(f"\nTrades: {len(result['trades'])} total "
          f"({(result['trades']['side'] == 'buy').sum()} buys, "
          f"{(result['trades']['side'] == 'sell').sum()} sells)")


if __name__ == "__main__":
    main()
