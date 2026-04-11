"""
Strategy visualisation — produces wiki/results/strategy_overview.png.

Four panels:
  1. Equity curves (vol_managed, low_vol, market baseline) + drawdown shading
  2. Rolling 60-day Sharpe ratio
  3. Portfolio turnover per day (bar + 20d rolling mean)
  4. Number of stocks held per day

Usage:
    python eval/visualize.py
    python eval/visualize.py --sample   # fast run on sample data
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Allow imports from repo root
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from eval.backtest import run_backtest
from signals import low_vol, vol_managed


# ── Colour constants ──────────────────────────────────────────────────────────

C_VM   = "#2563eb"   # vol_managed — primary blue
C_LV   = "#64748b"   # low_vol     — slate grey
C_MKT  = "#94a3b8"   # market baseline — light slate
C_FILL = "#dbeafe"   # vol_managed drawdown fill


# ── Portfolio helpers ─────────────────────────────────────────────────────────

def _market_baseline(daily: pd.DataFrame, initial_capital: float = 50_000_000.0) -> pd.Series:
    """Equal-weight all assets per day; compounded portfolio value."""
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    ret_matrix = df.pivot(index="trade_day_id", columns="asset_id", values="adj_close")
    # Daily equal-weight return
    daily_ret = ret_matrix.pct_change().mean(axis=1)  # cross-sectional mean return each day
    pv = pd.Series(
        initial_capital * (1 + daily_ret).cumprod(),
        index=daily_ret.index,
    )
    # Prepend day 0
    first_day = pv.index[0]
    # Use D000 as the pre-trade label to match backtest output
    pv = pd.concat([pd.Series([initial_capital], index=["D000"]), pv])
    return pv


def _days_held(trades_df: pd.DataFrame) -> pd.Series:
    """Number of distinct assets on the buy side per day (proxy for holdings count)."""
    buys = trades_df[trades_df["side"] == "buy"]
    return buys.groupby("day")["asset_id"].nunique()


def _turnover_per_day(trades_df: pd.DataFrame) -> pd.Series:
    """Total turnover (buys + sells) per day, as a fraction of 50M."""
    initial = 50_000_000.0
    tv = trades_df.groupby("day")["turnover"].sum() / initial
    return tv


def _rolling_sharpe(portfolio_value: pd.Series, window: int = 60) -> pd.Series:
    """Rolling annualised Sharpe ratio."""
    rets = portfolio_value.pct_change().dropna()
    roll_mean = rets.rolling(window).mean()
    roll_std  = rets.rolling(window).std()
    sharpe = roll_mean / roll_std.replace(0, np.nan) * math.sqrt(242)
    return sharpe


def _holdings_per_day(portfolio_value: pd.Series, trades_df: pd.DataFrame, all_days: list[str]) -> pd.Series:
    """
    Estimate number of stocks held at end of each day.

    We replay a simplified holdings tracker: buy adds assets, sell removes them.
    T+1 is ignored here — we count settled + locked as "held".
    """
    held: set[str] = set()
    counts: list[tuple[str, int]] = []

    # Build day -> (buys, sells) maps
    buy_map: dict[str, list[str]] = {}
    sell_map: dict[str, list[str]] = {}
    for _, row in trades_df.iterrows():
        day = row["day"]
        asset = row["asset_id"]
        if row["side"] == "buy":
            buy_map.setdefault(day, []).append(asset)
        else:
            sell_map.setdefault(day, []).append(asset)

    for day in all_days:
        for a in sell_map.get(day, []):
            held.discard(a)
        for a in buy_map.get(day, []):
            held.add(a)
        counts.append((day, len(held)))

    return pd.Series({d: c for d, c in counts})


# ── Annotation helpers ────────────────────────────────────────────────────────

def _stats_text(label: str, cagr: float, sharpe: float, mdd: float, final_val: float) -> str:
    return (
        f"{label}\n"
        f"  Final: {final_val / 50_000_000:.3f}×\n"
        f"  CAGR:  {cagr:+.2%}\n"
        f"  SR:    {sharpe:.3f}\n"
        f"  MDD:   {mdd:.2%}"
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main(sample: bool = False) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker
    except ImportError:
        print("ERROR: matplotlib is not installed. Install with: pip install matplotlib")
        sys.exit(1)

    # ── Load data ─────────────────────────────────────────────────────────────
    data_dir = ROOT / "data"
    if sample:
        daily_path = data_dir / "daily_sample.parquet"
        print("Loading sample data...")
    else:
        daily_path = data_dir / "daily_data_in_sample.parquet"
        print("Loading full daily data (this may take a moment)...")

    daily = pd.read_parquet(daily_path)
    all_days = sorted(daily["trade_day_id"].unique().tolist())
    print(f"  {len(all_days)} trading days, {daily['asset_id'].nunique()} assets")

    # ── Compute signals ───────────────────────────────────────────────────────
    print("Computing low_vol signal...")
    sig_lv = low_vol.compute(daily, lob=None, window=60, excl_illiq=0.05)

    print("Computing vol_managed signal...")
    sig_vm = vol_managed.compute(daily, lob=None, window=20, sigma_threshold=3.0,
                                  base_window=60, excl_illiq=0.05)

    # ── Run backtests ─────────────────────────────────────────────────────────
    N_STOCKS = 20
    SELL_MODE = "open"

    print(f"Running vol_managed backtest (N={N_STOCKS}, sell={SELL_MODE})...")
    res_vm = run_backtest(daily, sig_vm, sell_mode=SELL_MODE, n_stocks=N_STOCKS)

    print(f"Running low_vol backtest (N={N_STOCKS}, sell={SELL_MODE})...")
    res_lv = run_backtest(daily, sig_lv, sell_mode=SELL_MODE, n_stocks=N_STOCKS)

    print("Computing market baseline...")
    pv_mkt = _market_baseline(daily)

    pv_vm = res_vm["portfolio_value"]
    pv_lv = res_lv["portfolio_value"]

    # Normalise to 1.0 at start (D000)
    def _norm(pv: pd.Series) -> pd.Series:
        return pv / pv.iloc[0]

    norm_vm  = _norm(pv_vm)
    norm_lv  = _norm(pv_lv)
    norm_mkt = _norm(pv_mkt)

    # ── Derive panel data ─────────────────────────────────────────────────────
    rs_vm = _rolling_sharpe(pv_vm, window=60)
    rs_lv = _rolling_sharpe(pv_lv, window=60)

    tv_vm = _turnover_per_day(res_vm["trades"])
    tv_vm_roll = tv_vm.rolling(20, min_periods=1).mean()

    holdings_vm = _holdings_per_day(pv_vm, res_vm["trades"], all_days)

    # ── X-axis: integer positions, labelled every 50 days ────────────────────
    # We use day IDs directly (string index) but plot against integer positions
    # for neatness.  We build a shared integer index for each series.
    def _to_int_index(s: pd.Series, day_list: list[str]) -> pd.Series:
        """Map trade_day_id index -> integer position (excluding D000)."""
        pos = {d: i for i, d in enumerate(day_list)}
        return pd.Series(
            s.values,
            index=[pos.get(d, -1) for d in s.index],
        ).loc[lambda x: x.index >= 0]

    # For equity curves include D000 at position -1 prepended; we handle separately
    n_days = len(all_days)
    x_eq = np.arange(-1, n_days)   # -1 = D000, 0 = D001, ...

    def _equity_x(pv_norm: pd.Series) -> tuple[np.ndarray, np.ndarray]:
        """Extract x positions and y values for an equity curve including D000."""
        x = np.arange(-1, len(pv_norm) - 1)
        return x, pv_norm.values

    x_vm, y_vm = _equity_x(norm_vm)
    x_lv, y_lv = _equity_x(norm_lv)
    # Market baseline may have different length; align to pv_vm length
    norm_mkt_aligned = norm_mkt.reindex(pv_vm.index).ffill()
    x_mkt, y_mkt = _equity_x(norm_mkt_aligned)

    # Rolling sharpe: index = trade_day_id (no D000)
    rs_vm_int = _to_int_index(rs_vm, all_days)
    rs_lv_int = _to_int_index(rs_lv, all_days)

    # Turnover
    tv_vm_int      = _to_int_index(tv_vm, all_days)
    tv_vm_roll_int = _to_int_index(tv_vm_roll, all_days)

    # Holdings
    hold_int = _to_int_index(holdings_vm, all_days)

    # X-tick positions (every 50 days)
    tick_positions = list(range(0, n_days, 50))
    tick_labels    = [all_days[i] for i in tick_positions]

    # ── Figure setup ──────────────────────────────────────────────────────────
    try:
        plt.style.use("seaborn-v0_8-whitegrid")
    except OSError:
        plt.style.use("seaborn-whitegrid")

    fig = plt.figure(figsize=(16, 12))
    fig.suptitle(
        "vol_managed Strategy — In-Sample Performance (D001–D484)",
        fontsize=14, fontweight="bold", y=0.98,
    )

    # Grid: top row full width, bottom row 3 columns
    gs = fig.add_gridspec(2, 3, height_ratios=[1.6, 1], hspace=0.38, wspace=0.32)
    ax1 = fig.add_subplot(gs[0, :])    # Panel 1 — full width
    ax2 = fig.add_subplot(gs[1, 0])    # Panel 2
    ax3 = fig.add_subplot(gs[1, 1])    # Panel 3
    ax4 = fig.add_subplot(gs[1, 2])    # Panel 4

    # ── Panel 1: Equity curves ────────────────────────────────────────────────
    ax1.plot(x_mkt, y_mkt, color=C_MKT, lw=1.2, ls="--", label="Market (equal-weight)", zorder=2)
    ax1.plot(x_lv,  y_lv,  color=C_LV,  lw=1.5, label="low_vol (baseline)", zorder=3)
    ax1.plot(x_vm,  y_vm,  color=C_VM,  lw=2.0, label="vol_managed", zorder=4)

    # Drawdown shading for vol_managed
    running_max = np.maximum.accumulate(y_vm)
    ax1.fill_between(x_vm, y_vm, running_max, where=(y_vm < running_max),
                     color=C_FILL, alpha=0.6, label="vol_managed drawdown", zorder=1)

    # Stats annotation
    stats_vm = _stats_text(
        "vol_managed",
        res_vm["cagr"], res_vm["sharpe"], res_vm["mdd"],
        pv_vm.iloc[-1],
    )
    stats_lv = _stats_text(
        "low_vol",
        res_lv["cagr"], res_lv["sharpe"], res_lv["mdd"],
        pv_lv.iloc[-1],
    )
    annotation = stats_vm + "\n\n" + stats_lv
    ax1.text(
        0.015, 0.97, annotation,
        transform=ax1.transAxes, fontsize=8.5,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.85, edgecolor="#cbd5e1"),
        family="monospace",
    )

    ax1.axhline(1.0, color="#e2e8f0", lw=0.8, ls=":")
    ax1.set_xlim(x_vm[0], x_vm[-1])
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, fontsize=8, rotation=30, ha="right")
    ax1.set_xlabel("Trade Day", fontsize=9)
    ax1.set_ylabel("Portfolio Value (indexed to 1.0)", fontsize=9)
    ax1.set_title("Equity Curves", fontsize=11, fontweight="semibold")
    ax1.legend(loc="lower right", fontsize=8.5, framealpha=0.9)
    ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))

    # ── Panel 2: Rolling 60-day Sharpe ────────────────────────────────────────
    ax2.plot(rs_lv_int.index, rs_lv_int.values, color=C_LV, lw=1.2, label="low_vol")
    ax2.plot(rs_vm_int.index, rs_vm_int.values, color=C_VM, lw=1.8, label="vol_managed")
    ax2.axhline(0, color="#94a3b8", lw=0.8, ls="--")
    ax2.set_xlim(0, n_days - 1)
    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels(tick_labels, fontsize=7, rotation=30, ha="right")
    ax2.set_xlabel("Trade Day", fontsize=9)
    ax2.set_ylabel("Rolling 60-day Sharpe", fontsize=9)
    ax2.set_title("Rolling Sharpe (60d)", fontsize=11, fontweight="semibold")
    ax2.legend(fontsize=8, framealpha=0.9)

    # ── Panel 3: Portfolio turnover ───────────────────────────────────────────
    bar_color = "#bfdbfe"   # light blue bars
    ax3.bar(tv_vm_int.index, tv_vm_int.values * 100, color=bar_color,
            width=1.0, label="Daily turnover", alpha=0.85)
    ax3.plot(tv_vm_roll_int.index, tv_vm_roll_int.values * 100,
             color=C_VM, lw=1.8, label="20d rolling mean")
    ax3.set_xlim(0, n_days - 1)
    ax3.set_ylim(0, 20)
    ax3.set_xticks(tick_positions)
    ax3.set_xticklabels(tick_labels, fontsize=7, rotation=30, ha="right")
    ax3.set_xlabel("Trade Day", fontsize=9)
    ax3.set_ylabel("Turnover (% of portfolio)", fontsize=9)
    ax3.set_title("Portfolio Turnover (vol_managed)", fontsize=11, fontweight="semibold")
    ax3.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax3.legend(fontsize=8, framealpha=0.9)

    # ── Panel 4: Stocks held per day ──────────────────────────────────────────
    ax4.plot(hold_int.index, hold_int.values, color=C_VM, lw=1.5, label="Stocks held")
    ax4.axhline(N_STOCKS, color="#94a3b8", lw=0.8, ls="--", label=f"Target N={N_STOCKS}")
    ax4.set_xlim(0, n_days - 1)
    ax4.set_xticks(tick_positions)
    ax4.set_xticklabels(tick_labels, fontsize=7, rotation=30, ha="right")
    ax4.set_xlabel("Trade Day", fontsize=9)
    ax4.set_ylabel("Number of Stocks", fontsize=9)
    ax4.set_title("Stocks Held (vol_managed)", fontsize=11, fontweight="semibold")
    ax4.legend(fontsize=8, framealpha=0.9)

    # ── Save ──────────────────────────────────────────────────────────────────
    out_dir = ROOT / "wiki" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "strategy_overview.png"

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"\nFigure saved: {out_path}")
    print("\nPanel summary:")
    print("  Panel 1: Equity curves — vol_managed vs low_vol vs equal-weight market;")
    print("           drawdown regions shaded; stats box top-left.")
    print("  Panel 2: Rolling 60-day Sharpe ratio for both signals.")
    print("  Panel 3: Daily turnover (bars) + 20d rolling mean for vol_managed.")
    print("  Panel 4: Number of stocks held per day for vol_managed.")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate strategy overview figure")
    parser.add_argument("--sample", action="store_true",
                        help="Use sample data (fast, ~20 days)")
    args = parser.parse_args()
    main(sample=args.sample)
