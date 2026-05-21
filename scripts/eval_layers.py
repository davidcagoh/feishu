#!/usr/bin/env python3
"""
Layered evaluation driver — runs a list of signals through the competition
backtester, then computes the L1–L6 stack across the resulting wallet curves.

Outputs (per run):
  wiki/results/layered_leaderboard.md   — markdown leaderboard
  wiki/results/_layered_table.json      — structured row data for downstream use

Cross-project frame: see root `wiki/learnings.md`. Feishu can lag on L4 (DSR)
and L6 (MDB) until N grows; L2/L3/L5 are immediately applicable.

Usage
-----
    python scripts/eval_layers.py --sample
    python scripts/eval_layers.py --signals trend_vol_v4 trend_vol_v5 low_vol
    python scripts/eval_layers.py                   # full data, default suite
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

# Allow running from repo root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from eval.backtest import run_backtest  # noqa: E402
from eval.layers import LayeredMetrics, compute, format_markdown_table  # noqa: E402
from eval.dsr import compute_dsr_table, format_dsr_table  # noqa: E402
from eval.correlation_mdb import (  # noqa: E402
    correlation_matrix,
    mdb_table,
    returns_matrix,
)
from signals import REGISTRY  # noqa: E402


# Default suite — the production submission set + nearest baselines, per
# wiki/_index.md leaderboard. Override with --signals on the CLI.
DEFAULT_SIGNALS = [
    "trend_vol_v3",
    "vol_managed_v2",
    "low_vol",
]

WIKI_RESULTS = ROOT / "wiki" / "results"


# ─── Data + run ───────────────────────────────────────────────────────────────


def load_daily(sample: bool) -> pd.DataFrame:
    if sample:
        path = ROOT / "data" / "daily_sample.parquet"
    else:
        path = ROOT / "data" / "daily_data_in_sample.parquet"
    if not path.exists():
        raise FileNotFoundError(f"missing data file: {path}")
    return pd.read_parquet(path)


def _resolve_n_stocks(module, cli_default: int) -> int:
    """Per-signal N override.

    Some signals (trend_vol_v5) need a specific breadth to operate as designed
    — e.g. v5's regime overlay caps daily breadth at `BULL_PARAMS.n_stocks=30`
    on bull days and 20 elsewhere. Capping such a signal at the CLI default
    silently turns it into a different strategy.

    Resolution order: `module.N_STOCKS` → `module.BULL_PARAMS.n_stocks` → CLI default.
    """
    if hasattr(module, "N_STOCKS"):
        return int(module.N_STOCKS)
    bull = getattr(module, "BULL_PARAMS", None)
    if bull is not None and hasattr(bull, "n_stocks"):
        return int(bull.n_stocks)
    return cli_default


def run_one(daily: pd.DataFrame, sig_name: str, n_stocks: int, sell_mode: str) -> tuple[dict, int]:
    if sig_name not in REGISTRY:
        raise KeyError(f"unknown signal {sig_name!r}; available: {list(REGISTRY)}")
    module = REGISTRY[sig_name]
    signal = module.compute(daily, None)
    weights = module.compute_weights(daily, None) if hasattr(module, "compute_weights") else None
    effective_n = _resolve_n_stocks(module, n_stocks)
    result = run_backtest(
        daily=daily,
        signal=signal,
        sell_mode=sell_mode,
        n_stocks=effective_n,
        weights=weights,
    )
    return result, effective_n


# ─── Aggregation ──────────────────────────────────────────────────────────────


def metrics_row(label: str, m: LayeredMetrics) -> dict:
    return {
        "signal": label,
        "CAGR_pct": m.cagr_pct,
        "Sharpe": m.sharpe,
        "Calmar": m.calmar,
        "MDD_pct": m.mdd_pct,
        "SQN": m.sqn,
        "skew": m.skew,
        "kurt_excess": m.kurt_excess,
        "tail_ratio": m.tail_ratio,
        "cvar_5_pct": m.cvar_5_pct,
        "ulcer": m.ulcer_index,
        "martin": m.martin_ratio,
        "pain": m.pain_index,
        "n_obs": m.n_obs,
        "score": m.competition_score,
    }


def leaderboard_markdown(rows: list[dict]) -> str:
    # Sort by competition score descending for a familiar leaderboard view.
    rows = sorted(rows, key=lambda r: -r["score"])
    head = (
        "| Signal | Score | CAGR | Sharpe | Calmar | MDD | SQN | Skew | Kurt | "
        "Ulcer | Martin |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    )
    body = "\n".join(
        f"| {r['signal']} | {r['score']:.4f} | {r['CAGR_pct']:+.2f}% | "
        f"{r['Sharpe']:.3f} | {r['Calmar']:.2f} | {r['MDD_pct']:.2f}% | "
        f"{r['SQN']:.2f} | {r['skew']:+.2f} | {r['kurt_excess']:+.2f} | "
        f"{r['ulcer']:.2f} | {r['martin']:.2f} |"
        for r in rows
    )
    return f"{head}\n{body}"


# ─── CLI ──────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Layered evaluation across signals")
    parser.add_argument("--sample", action="store_true", help="use 20-day sample data")
    parser.add_argument("--signals", nargs="+", default=None,
                        help=f"signal names (default: {DEFAULT_SIGNALS})")
    parser.add_argument("--sell-mode", choices=["open", "close"], default="close")
    parser.add_argument("--n-stocks", type=int, default=20)
    parser.add_argument("--write", action="store_true",
                        help="write outputs to wiki/results/")
    args = parser.parse_args()

    signals = args.signals or DEFAULT_SIGNALS
    daily = load_daily(args.sample)
    print(f"Loaded daily data: {len(daily):,} rows, "
          f"{daily['trade_day_id'].nunique()} days", flush=True)

    wallets: dict[str, pd.Series] = {}
    trade_returns: dict[str, pd.Series] = {}
    rows: list[dict] = []

    for name in signals:
        print(f"\n=== {name} ===", flush=True)
        result, effective_n = run_one(daily, name, args.n_stocks, args.sell_mode)
        if effective_n != args.n_stocks:
            print(f"  [n_stocks override] {name}: {effective_n} "
                  f"(CLI default {args.n_stocks})", flush=True)
        wallet = result["portfolio_value"]
        trades = result["trades"]

        # Per-trade returns for SQN, when available. The competition backtester
        # records buy/sell legs; we proxy a per-day return series instead.
        tr = wallet.pct_change().dropna()
        wallets[name] = wallet
        trade_returns[name] = tr

        m = compute(wallet, trade_returns=tr)
        rows.append(metrics_row(name, m))
        print(format_markdown_table(m, title=name))

    # Layer-4: DSR across the candidate set
    dsr_rows = compute_dsr_table(wallets)
    print("\n=== Layer 4 — Deflated Sharpe (humility check) ===")
    print(format_dsr_table(dsr_rows))

    # Layer-6: correlation + MDB (only meaningful with ≥ 2 strategies)
    corr_md = ""
    mdb_md = ""
    if len(wallets) >= 2:
        rmat = returns_matrix(wallets)
        corr = correlation_matrix(rmat)
        print("\n=== Layer 6 — Pairwise daily-return correlation ===")
        print(corr.round(3).to_markdown())
        corr_md = corr.round(3).to_markdown()

        # MDB of each strategy vs the rest of the book
        all_names = list(wallets.keys())
        mdb_rows: list[dict] = []
        for cand in all_names:
            book = [s for s in all_names if s != cand]
            tbl = mdb_table(rmat, book, [cand])
            mdb_rows.append({"candidate": cand, **tbl.loc[cand].to_dict()})
        mdb_df = pd.DataFrame(mdb_rows).set_index("candidate")
        print("\n=== Layer 6 — MDB (leave-one-out) ===")
        print(mdb_df.round(3).to_markdown())
        mdb_md = mdb_df.round(3).to_markdown()

    print("\n=== Layered leaderboard ===")
    leaderboard = leaderboard_markdown(rows)
    print(leaderboard)

    if args.write:
        WIKI_RESULTS.mkdir(parents=True, exist_ok=True)
        out_md = WIKI_RESULTS / "layered_leaderboard.md"
        out_md.write_text(
            "# Layered Leaderboard\n\n"
            f"_Generated by `scripts/eval_layers.py` "
            f"(sell_mode={args.sell_mode}, n_stocks={args.n_stocks}, "
            f"sample={args.sample})_\n\n"
            "## L1–L5 per strategy\n\n"
            f"{leaderboard}\n\n"
            "## L4 — DSR (humility check)\n\n"
            f"{format_dsr_table(dsr_rows)}\n\n"
            + (f"## L6 — Correlation\n\n{corr_md}\n\n## L6 — MDB (leave-one-out)\n\n{mdb_md}\n"
               if corr_md else "")
        )
        out_json = WIKI_RESULTS / "_layered_table.json"
        out_json.write_text(json.dumps({
            "rows": rows,
            "dsr": [r.__dict__ for r in dsr_rows],
        }, indent=2))
        print(f"\nwrote {out_md}")
        print(f"wrote {out_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
