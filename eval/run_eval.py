#!/usr/bin/env python3
"""
Signal evaluation script.

Usage:
    python eval/run_eval.py                  # full data (slow, requires large files)
    python eval/run_eval.py --sample         # sample data only (fast, 20 days)
    python eval/run_eval.py --signal reversal  # single signal

Outputs:
    wiki/results/latest.md        (overwritten every run)
    wiki/results/YYYY-MM-DD.md    (archived snapshot)
    stdout                        (same content)
"""

import argparse
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))
from signals import REGISTRY


# ── Data loading ─────────────────────────────────────────────────────────────

def load_data(sample: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    root = Path(__file__).parent.parent / "data"
    if sample:
        daily_path = root / "daily_sample.parquet"
        lob_path = root / "lob_sample.parquet"
    else:
        daily_path = root / "daily_data_in_sample.parquet"
        lob_path = None  # never load LOB unfiltered

    daily = pd.read_parquet(daily_path)
    lob = pd.read_parquet(lob_path) if lob_path and lob_path.exists() else pd.DataFrame()

    return daily, lob


# ── Returns computation ───────────────────────────────────────────────────────

def compute_returns(daily: pd.DataFrame) -> pd.DataFrame:
    """Adjusted next-day returns, limit-hits masked to NaN."""
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    # Mask limit-hit days — stock is uninvestable
    df.loc[df["ret"].abs() > 0.095, "ret"] = np.nan

    ret_matrix = df.pivot(index="trade_day_id", columns="asset_id", values="ret")

    # Shift back 1: ret_matrix[t] = return earned on day t
    # To use signal[t] → ret[t+1], we shift returns back so they align with signal
    return ret_matrix


# ── Evaluation ────────────────────────────────────────────────────────────────

def evaluate_signal(
    signal: pd.DataFrame,
    returns: pd.DataFrame,
    name: str,
) -> dict:
    """
    Compute IC series and summary stats.

    signal[t] predicts returns[t+1], so we shift signal forward by 1.
    """
    # Signal on day t aligns with next-day return: shift signal by +1
    sig_shifted = signal.shift(1)

    common_days = sig_shifted.index.intersection(returns.index)
    common_assets = sig_shifted.columns.intersection(returns.columns)

    sig = sig_shifted.loc[common_days, common_assets]
    ret = returns.loc[common_days, common_assets]

    ic_series = []
    for day in common_days:
        s = sig.loc[day].dropna()
        r = ret.loc[day].dropna()
        common = s.index.intersection(r.index)
        if len(common) < 20:
            continue
        ic, _ = spearmanr(s[common].values, r[common].values)
        if not np.isnan(ic):
            ic_series.append(ic)

    ic_s = pd.Series(ic_series)
    n = len(ic_s)
    mean_ic = ic_s.mean() if n > 0 else np.nan
    std_ic = ic_s.std() if n > 1 else np.nan
    ir = mean_ic / std_ic * np.sqrt(252) if (n > 1 and std_ic > 0) else np.nan
    hit_rate = (ic_s > 0).mean() if n > 0 else np.nan

    return {
        "name": name,
        "mean_ic": mean_ic,
        "ic_std": std_ic,
        "ir_annualised": ir,
        "hit_rate": hit_rate,
        "n_days": n,
    }


# ── Report formatting ─────────────────────────────────────────────────────────

def fmt(val, fmt_str=".4f"):
    return f"{val:{fmt_str}}" if not (val is None or np.isnan(val)) else "N/A"


def build_report(results: list[dict], sample: bool, daily: pd.DataFrame) -> str:
    today = date.today().isoformat()
    days = daily["trade_day_id"].nunique()
    assets = daily["asset_id"].nunique()
    day_range = f"{daily['trade_day_id'].min()}–{daily['trade_day_id'].max()}"

    lines = [
        f"# Signal Evaluation Results — {today}",
        "",
        f"**Data:** {'sample' if sample else 'full'} — {days} days ({day_range}), {assets} assets",
    ]
    if sample:
        lines.append(
            "_Note: IC estimates on sample data (≤20 days) are noisy. "
            "Use for smoke-testing only. Run without --sample for reliable estimates._"
        )
    lines += [
        "",
        "## Results",
        "",
        "| Signal | Mean IC | IC Std | IR (ann.) | Hit Rate | Days |",
        "|--------|---------|--------|-----------|----------|------|",
    ]

    for r in results:
        lines.append(
            f"| {r['name']} "
            f"| {fmt(r['mean_ic'])} "
            f"| {fmt(r['ic_std'])} "
            f"| {fmt(r['ir_annualised'], '.2f')} "
            f"| {fmt(r['hit_rate'], '.0%') if not np.isnan(r['hit_rate']) else 'N/A'} "
            f"| {r['n_days']} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "- **IC > 0.02**: signal has meaningful predictive power at daily frequency",
        "- **IR > 0.5**: annualised information ratio worth pursuing",
        "- **Hit rate > 55%**: signal is directionally consistent",
        "",
        "## Next Steps",
        "",
    ]

    # Auto-generate next steps based on results
    strong = [r for r in results if not np.isnan(r["mean_ic"]) and r["mean_ic"] > 0.02]
    weak = [r for r in results if not np.isnan(r["mean_ic"]) and r["mean_ic"] <= 0]

    if strong:
        names = ", ".join(r["name"] for r in strong)
        lines.append(f"- Promising signals to develop further: **{names}**")
        lines.append("  - Test on full dataset for reliable IC estimates")
        lines.append("  - Try combining signals (IC correlation < 0.3 → good diversification)")

    if weak:
        names = ", ".join(r["name"] for r in weak)
        lines.append(f"- Weak/negative signals: **{names}** — consider inverting or discarding")

    lines += [
        "- See `wiki/ideas/feishu-competition-signals.md` for more signal ideas",
        "",
        "---",
        f"_Generated by `eval/run_eval.py` on {today}_",
    ]

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", default=False,
                        help="Use sample data (fast, 20 days)")
    parser.add_argument("--signal", default=None,
                        help="Evaluate a single signal by name")
    args = parser.parse_args()

    print("Loading data...", flush=True)
    daily, lob = load_data(sample=args.sample)
    returns = compute_returns(daily)

    signals_to_run = (
        {args.signal: REGISTRY[args.signal]}
        if args.signal and args.signal in REGISTRY
        else REGISTRY
    )

    results = []
    for name, module in signals_to_run.items():
        print(f"  Computing {name}...", flush=True)
        try:
            signal = module.compute(daily, lob if not lob.empty else None)
            result = evaluate_signal(signal, returns, name)
            results.append(result)
            print(f"    IC={fmt(result['mean_ic'])}  IR={fmt(result['ir_annualised'], '.2f')}  "
                  f"hit={fmt(result['hit_rate'], '.0%') if not np.isnan(result['hit_rate']) else 'N/A'}  "
                  f"n={result['n_days']}")
        except Exception as e:
            print(f"    ERROR: {e}")
            results.append({"name": name, "mean_ic": np.nan, "ic_std": np.nan,
                            "ir_annualised": np.nan, "hit_rate": np.nan, "n_days": 0})

    report = build_report(results, args.sample, daily)
    print("\n" + report)

    # Write to wiki/results/
    results_dir = Path(__file__).parent.parent / "wiki" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    (results_dir / "latest.md").write_text(report)
    (results_dir / f"{today}.md").write_text(report)
    print(f"\nResults written to wiki/results/latest.md and wiki/results/{today}.md")


if __name__ == "__main__":
    main()
