#!/usr/bin/env python3
"""
Regime-conditional IC analysis for composite_full.

Two regime classifiers:
  1. Vol-based: rolling 20-day cross-sectional return std (high vs low)
  2. Dispersion-based: rolling cross-sectional IC std of best signal (high IC-variance
     days vs low IC-variance days)

For each regime, reports per-signal and composite IC/IR/hit.

Usage:
    python eval/regime_analysis.py
"""

import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent.parent))
from signals import lob_imbalance, ofi_ou, price_to_vwap, volume_reversal
from eval.run_eval import load_data, compute_returns

COMPONENTS = ["volume_reversal", "price_to_vwap", "lob_imbalance", "ofi_ou"]
MODULES = {
    "volume_reversal": volume_reversal,
    "price_to_vwap": price_to_vwap,
    "lob_imbalance": lob_imbalance,
    "ofi_ou": ofi_ou,
}
WEIGHTS_FULL = np.array([0.2542, 0.1155, 0.2829, 0.3474])


def ic_series_for(signal: pd.DataFrame, returns: pd.DataFrame) -> pd.Series:
    sig_shifted = signal.shift(1)
    common_days = sig_shifted.index.intersection(returns.index)
    common_assets = sig_shifted.columns.intersection(returns.columns)
    ics = {}
    for day in common_days:
        s = sig_shifted.loc[day, common_assets].dropna()
        r = returns.loc[day, common_assets].dropna()
        c = s.index.intersection(r.index)
        if len(c) < 20:
            continue
        ic, _ = spearmanr(s[c].values, r[c].values)
        if not np.isnan(ic):
            ics[day] = ic
    return pd.Series(ics)


def regime_stats(ic_s: pd.Series, label: str):
    n = len(ic_s)
    if n < 5:
        print(f"    {label:30s}  n={n} (too few)")
        return None
    m = ic_s.mean(); s = ic_s.std()
    ir = m / s * np.sqrt(252) if s > 0 else float("nan")
    hit = (ic_s > 0).mean()
    print(f"    {label:30s}  IC={m:.4f}  IR={ir:.2f}  hit={hit:.0%}  n={n}")
    return {"label": label, "mean_ic": m, "ic_std": s, "ir": ir, "hit": hit, "n": n}


def main():
    print("Loading data...", flush=True)
    daily, lob = load_data(sample=False, with_lob=True)
    returns = compute_returns(daily)

    # --- Volatility regime ---
    # Cross-sectional std of daily returns, rolling 20-day mean
    cs_vol = returns.std(axis=1)  # per-day cross-sectional return dispersion
    vol_smooth = cs_vol.rolling(20, min_periods=5).mean()
    vol_median = vol_smooth.median()
    high_vol_days = set(vol_smooth[vol_smooth > vol_median].index)
    low_vol_days  = set(vol_smooth[vol_smooth <= vol_median].index)
    print(f"\nVol regimes: high={len(high_vol_days)} days, low={len(low_vol_days)} days "
          f"(median CS vol={vol_median:.4f})")

    # Compute IC series per component
    print("\nComputing IC series per component...", flush=True)
    ic_all = {}
    for name in COMPONENTS:
        lob_arg = lob if name in ("lob_imbalance", "ofi_ou") else None
        sig = MODULES[name].compute(daily, lob_arg)
        ic_all[name] = ic_series_for(sig, returns)

    ic_df = pd.DataFrame(ic_all).dropna()

    # Composite IC series
    ic_composite = pd.Series(ic_df.values @ WEIGHTS_FULL, index=ic_df.index, name="composite_full")

    print(f"\nTotal aligned days: {len(ic_df)}")

    # --- Vol regime breakdown ---
    print("\n=== Volatility Regime ===")
    aligned_high = ic_df.index[ic_df.index.isin(high_vol_days)]
    aligned_low  = ic_df.index[ic_df.index.isin(low_vol_days)]
    print(f"  High-vol ({len(aligned_high)} days):")
    for name in COMPONENTS:
        regime_stats(ic_df.loc[aligned_high, name], name)
    regime_stats(ic_composite[aligned_high], "composite_full")
    print(f"  Low-vol ({len(aligned_low)} days):")
    for name in COMPONENTS:
        regime_stats(ic_df.loc[aligned_low, name], name)
    regime_stats(ic_composite[aligned_low], "composite_full")

    # --- Trend regime (momentum vs reversal environment) ---
    # Use cross-sectional mean return as trend indicator: positive = up day, negative = down day
    mean_ret = returns.mean(axis=1)
    mean_ret_smooth = mean_ret.rolling(5, min_periods=2).mean()
    up_days   = set(mean_ret_smooth[mean_ret_smooth > 0].index)
    down_days = set(mean_ret_smooth[mean_ret_smooth <= 0].index)
    aligned_up   = ic_df.index[ic_df.index.isin(up_days)]
    aligned_down = ic_df.index[ic_df.index.isin(down_days)]
    print(f"\n=== Market Direction Regime (5d smooth mean return) ===")
    print(f"  Up market ({len(aligned_up)} days):")
    for name in COMPONENTS:
        regime_stats(ic_df.loc[aligned_up, name], name)
    regime_stats(ic_composite[aligned_up], "composite_full")
    print(f"  Down market ({len(aligned_down)} days):")
    for name in COMPONENTS:
        regime_stats(ic_df.loc[aligned_down, name], name)
    regime_stats(ic_composite[aligned_down], "composite_full")

    # Build markdown report
    today = date.today().isoformat()
    lines = [
        f"# Regime Analysis — {today}",
        "",
        "## Volatility Regime (rolling 20-day cross-sectional return std)",
        "",
        f"Median CS vol = {vol_median:.4f}. "
        f"High-vol days (>{vol_median:.4f}): {len(aligned_high)}, "
        f"Low-vol days: {len(aligned_low)}.",
        "",
        "| Signal | IC (high-vol) | IR (high-vol) | IC (low-vol) | IR (low-vol) |",
        "|--------|--------------|--------------|-------------|-------------|",
    ]
    for name in COMPONENTS + ["composite_full"]:
        if name == "composite_full":
            s_h = ic_composite[aligned_high]
            s_l = ic_composite[aligned_low]
        else:
            s_h = ic_df.loc[aligned_high, name]
            s_l = ic_df.loc[aligned_low, name]
        def fmt(ic_s):
            if len(ic_s) < 5:
                return "N/A", "N/A"
            m = ic_s.mean(); s = ic_s.std()
            ir = m/s*np.sqrt(252) if s > 0 else float("nan")
            return f"{m:.4f}", f"{ir:.2f}"
        ih, irh = fmt(s_h)
        il, irl = fmt(s_l)
        lines.append(f"| {name} | {ih} | {irh} | {il} | {irl} |")

    lines += [
        "",
        "## Market Direction Regime (5-day smoothed mean cross-sectional return)",
        "",
        f"Up days: {len(aligned_up)}, Down days: {len(aligned_down)}.",
        "",
        "| Signal | IC (up) | IR (up) | IC (down) | IR (down) |",
        "|--------|---------|---------|-----------|-----------|",
    ]
    for name in COMPONENTS + ["composite_full"]:
        if name == "composite_full":
            s_u = ic_composite[aligned_up]
            s_d = ic_composite[aligned_down]
        else:
            s_u = ic_df.loc[aligned_up, name]
            s_d = ic_df.loc[aligned_down, name]
        iu, iru = fmt(s_u)
        id_, ird = fmt(s_d)
        lines.append(f"| {name} | {iu} | {iru} | {id_} | {ird} |")

    lines += ["", "---", f"_Generated by `eval/regime_analysis.py` on {today}_"]

    out = Path(__file__).parent.parent / "wiki" / "results" / "regime_analysis.md"
    out.write_text("\n".join(lines))
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
