#!/usr/bin/env python3
"""
Walk-forward validation for composite_full.

Splits at D240 (roughly half the 484-day sample):
  In-sample:  D001–D240 — fit optimal weights via Sigma^{-1} mu
  Out-of-sample: D241–D484 — apply frozen weights, measure IR

Also tests composite_daily (daily-only) for comparison.

Usage:
    python eval/walk_forward.py          # requires full data + LOB
    python eval/walk_forward.py --no-lob # daily composite only
"""

import argparse
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent.parent))
from signals import lob_imbalance, ofi_ou, price_to_vwap, volume_reversal
from eval.run_eval import load_data, compute_returns

SPLIT_DAY = "D240"
DAILY_COMPONENTS = ["volume_reversal", "price_to_vwap"]
FULL_COMPONENTS  = ["volume_reversal", "price_to_vwap", "lob_imbalance", "ofi_ou"]
MODULES = {
    "volume_reversal": volume_reversal,
    "price_to_vwap": price_to_vwap,
    "lob_imbalance": lob_imbalance,
    "ofi_ou": ofi_ou,
}


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


def fit_weights(ic_df: pd.DataFrame) -> np.ndarray:
    """Sigma^{-1} mu, normalised to sum=1, clipped to >= 0."""
    mu = ic_df.mean().values
    Sigma = ic_df.cov().values
    w = np.linalg.solve(Sigma, mu)
    w = np.maximum(w, 0)   # no short-selling of signals
    if w.sum() == 0:
        w = np.ones(len(w)) / len(w)
    else:
        w /= w.sum()
    return w


def composite_ic(ic_df: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    return pd.Series(ic_df.values @ weights, index=ic_df.index)


def summary(ic_s: pd.Series, label: str) -> dict:
    n = len(ic_s)
    mean_ic = ic_s.mean()
    std_ic = ic_s.std()
    ir = mean_ic / std_ic * np.sqrt(252) if std_ic > 0 else np.nan
    hit = (ic_s > 0).mean()
    print(f"  {label:35s}  IC={mean_ic:.4f}  IR={ir:.2f}  hit={hit:.0%}  n={n}")
    return {"label": label, "mean_ic": mean_ic, "ic_std": std_ic, "ir": ir, "hit": hit, "n": n}


def run(with_lob: bool):
    print("Loading data...", flush=True)
    daily, lob = load_data(sample=False, with_lob=with_lob)
    returns = compute_returns(daily)

    all_days = sorted(daily["trade_day_id"].unique())
    is_days  = [d for d in all_days if d <= SPLIT_DAY]
    oos_days = [d for d in all_days if d >  SPLIT_DAY]
    print(f"  In-sample: {is_days[0]}–{is_days[-1]} ({len(is_days)} days)")
    print(f"  Out-of-sample: {oos_days[0]}–{oos_days[-1]} ({len(oos_days)} days)")

    # Compute full IC series per component
    print("\nComputing IC series per component...", flush=True)
    ic_all = {}
    components = FULL_COMPONENTS if with_lob else DAILY_COMPONENTS
    for name in components:
        lob_arg = lob if (with_lob and name in ("lob_imbalance", "ofi_ou")) else None
        sig = MODULES[name].compute(daily, lob_arg)
        ic_all[name] = ic_series_for(sig, returns)
        print(f"  {name}: {len(ic_all[name])} days with IC")

    ic_df = pd.DataFrame(ic_all).dropna()
    ic_is  = ic_df[ic_df.index <= SPLIT_DAY]
    ic_oos = ic_df[ic_df.index >  SPLIT_DAY]
    print(f"\n  Aligned days: IS={len(ic_is)}, OOS={len(ic_oos)}")

    # --- Fit weights in-sample ---
    w_opt = fit_weights(ic_is)
    print(f"\nIn-sample fitted weights ({SPLIT_DAY} split):")
    for name, w in zip(components, w_opt):
        print(f"  {name}: {w:.4f}")

    # Fixed hardcoded weights (from full-sample optimization)
    if with_lob:
        w_fixed = np.array([0.2542, 0.1155, 0.2829, 0.3474])
    else:
        w_fixed = np.array([0.85, 0.15])

    print(f"\nFull-sample (hardcoded) weights:")
    for name, w in zip(components, w_fixed):
        print(f"  {name}: {w:.4f}")

    print("\n--- In-sample performance ---")
    summary(composite_ic(ic_is, w_opt),   "IS: IS-fitted weights")
    summary(composite_ic(ic_is, w_fixed), "IS: full-sample weights")

    print("\n--- Out-of-sample performance ---")
    r_oos_opt   = summary(composite_ic(ic_oos, w_opt),   "OOS: IS-fitted weights")
    r_oos_fixed = summary(composite_ic(ic_oos, w_fixed), "OOS: full-sample weights")

    # Equal-weight baseline
    w_eq = np.ones(len(components)) / len(components)
    summary(composite_ic(ic_oos, w_eq), "OOS: equal-weight baseline")

    # Individual signal baselines in OOS
    print("\n--- Individual signal OOS ---")
    for name in components:
        ic_s = ic_df[name][ic_df.index > SPLIT_DAY]
        summary(ic_s, f"OOS: {name}")

    # Build report
    today = date.today().isoformat()
    lines = [
        f"# Walk-Forward Validation — {today}",
        "",
        f"**Split:** {SPLIT_DAY} (IS: {is_days[0]}–{is_days[-1]}, OOS: {oos_days[0]}–{oos_days[-1]})",
        f"**Components:** {', '.join(components)}",
        "",
        "## In-Sample Fitted Weights",
        "",
    ]
    for name, w in zip(components, w_opt):
        lines.append(f"- {name}: {w:.4f}")
    lines += [
        "",
        "## Performance Summary",
        "",
        "| | Mean IC | IC Std | IR (ann.) | Hit Rate | Days |",
        "|---|---------|--------|-----------|----------|------|",
    ]
    for r in [
        ("IS — IS-fitted",        composite_ic(ic_is,  w_opt)),
        ("IS — full-sample fixed", composite_ic(ic_is,  w_fixed)),
        ("OOS — IS-fitted",        composite_ic(ic_oos, w_opt)),
        ("OOS — full-sample fixed",composite_ic(ic_oos, w_fixed)),
        ("OOS — equal-weight",     composite_ic(ic_oos, w_eq)),
    ]:
        label, ic_s = r
        n = len(ic_s)
        m = ic_s.mean(); s = ic_s.std()
        ir = m/s*np.sqrt(252) if s > 0 else float("nan")
        lines.append(f"| {label} | {m:.4f} | {s:.4f} | {ir:.2f} | {(ic_s>0).mean():.0%} | {n} |")

    lines += ["", "## Individual Signal OOS", "", "| Signal | Mean IC | IR (ann.) | Hit Rate |",
              "|--------|---------|-----------|----------|"]
    for name in components:
        ic_s = ic_df[name][ic_df.index > SPLIT_DAY]
        m = ic_s.mean(); s = ic_s.std()
        ir = m/s*np.sqrt(252) if s > 0 else float("nan")
        lines.append(f"| {name} | {m:.4f} | {ir:.2f} | {(ic_s>0).mean():.0%} |")

    lines += ["", "---", f"_Generated by `eval/walk_forward.py` on {today}_"]
    report = "\n".join(lines)

    out = Path(__file__).parent.parent / "wiki" / "results" / "walk_forward.md"
    out.write_text(report)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-lob", action="store_true")
    args = parser.parse_args()
    run(with_lob=not args.no_lob)
