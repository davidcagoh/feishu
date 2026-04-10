#!/usr/bin/env python3
"""
PCA residual signal evaluation.

Hypothesis (from Attention Factors paper, Epstein et al. 2025): our mean-reversion signals
predict idiosyncratic returns better than raw returns, because removing systematic factor
returns (common market/sector moves) reduces noise in the prediction target.

Method:
  1. Build a rolling-window PCA of the cross-sectional return matrix.
     Each day t, use returns from t-LOOKBACK to t-1 to estimate K principal components.
  2. Project returns on day t onto those components → systematic return.
  3. Residual = raw return - systematic → idiosyncratic return.
  4. Evaluate each signal's IC against residual returns instead of raw returns.

Compares:
  - IC vs raw next-day returns (baseline)
  - IC vs residual next-day returns (PCA-adjusted)

Usage:
    python eval/pca_residual.py
    python eval/pca_residual.py --n-factors 10   # default=5
"""

import argparse
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.decomposition import PCA

sys.path.insert(0, str(Path(__file__).parent.parent))
from signals import lob_imbalance, ofi_ou, price_to_vwap, volume_reversal
from eval.run_eval import load_data, compute_returns

MODULES = {
    "volume_reversal": volume_reversal,
    "price_to_vwap": price_to_vwap,
    "lob_imbalance": lob_imbalance,
    "ofi_ou": ofi_ou,
}
WEIGHTS_FULL = np.array([0.2542, 0.1155, 0.2829, 0.3474])
LOOKBACK = 60
MIN_PERIODS = 20


def build_residual_returns(returns: pd.DataFrame, n_factors: int) -> pd.DataFrame:
    """
    Rolling PCA residual returns (vectorized, no O(n²) column lookup).

    For each day t:
      1. Restrict to assets present in both history AND today.
      2. Fill NaN in history with column mean.
      3. Fit PCA on the aligned (days × assets) matrix.
      4. Project today's returns onto factors → systematic; subtract → residual.
    """
    all_days = list(returns.index)
    ret_arr = returns.values        # (n_days × n_assets) numpy array for speed
    assets = list(returns.columns)
    n_assets = len(assets)
    residuals = {}

    for i, day in enumerate(all_days):
        if i < MIN_PERIODS:
            continue
        hist_slice = ret_arr[max(0, i - LOOKBACK): i]          # (win × n_assets)

        # Identify assets with sufficient history AND valid today
        today_row = ret_arr[i]                                  # (n_assets,)
        valid_today = ~np.isnan(today_row)
        col_obs = np.sum(~np.isnan(hist_slice), axis=0)        # per-asset obs count
        valid_hist = col_obs >= MIN_PERIODS // 2

        mask = valid_today & valid_hist
        if mask.sum() < max(n_factors + 1, 20):
            continue

        # Aligned slices
        h = hist_slice[:, mask].copy()                          # (win × k_assets)
        r_today = today_row[mask]                               # (k_assets,)

        # Fill NaN in history with column mean
        col_means = np.nanmean(h, axis=0)
        nan_mask = np.isnan(h)
        h[nan_mask] = np.take(col_means, np.where(nan_mask)[1])

        n_comp = min(n_factors, h.shape[0] - 1, h.shape[1] - 1)
        if n_comp < 1:
            continue

        pca = PCA(n_components=n_comp)
        pca.fit(h)

        mu = col_means
        loadings = pca.components_                              # (K × k_assets)
        scores = loadings @ (r_today - mu)                     # (K,)
        systematic = mu + loadings.T @ scores                  # (k_assets,)
        residual = r_today - systematic

        asset_subset = [assets[j] for j in np.where(mask)[0]]
        residuals[day] = pd.Series(residual, index=asset_subset)

    return pd.DataFrame(residuals).T  # (days × assets)


def ic_series_raw_vs_residual(signal: pd.DataFrame, returns_raw: pd.DataFrame,
                               returns_resid: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    sig_shifted = signal.shift(1)
    ics_raw, ics_resid = {}, {}

    for day in sig_shifted.index:
        if day not in returns_raw.index:
            continue
        s = sig_shifted.loc[day].dropna()
        r_raw = returns_raw.loc[day].dropna()
        c_raw = s.index.intersection(r_raw.index)
        if len(c_raw) >= 20:
            ic, _ = spearmanr(s[c_raw].values, r_raw[c_raw].values)
            if not np.isnan(ic):
                ics_raw[day] = ic

        if day not in returns_resid.index:
            continue
        r_res = returns_resid.loc[day].dropna()
        c_res = s.index.intersection(r_res.index)
        if len(c_res) >= 20:
            ic, _ = spearmanr(s[c_res].values, r_res[c_res].values)
            if not np.isnan(ic):
                ics_resid[day] = ic

    return pd.Series(ics_raw), pd.Series(ics_resid)


def fmt_stats(ic_s: pd.Series) -> str:
    n = len(ic_s)
    if n < 5:
        return f"n={n} (too few)"
    m = ic_s.mean(); s = ic_s.std()
    ir = m / s * np.sqrt(252) if s > 0 else float("nan")
    hit = (ic_s > 0).mean()
    return f"IC={m:.4f}  IR={ir:.2f}  hit={hit:.0%}  n={n}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-factors", type=int, default=5)
    args = parser.parse_args()

    print("Loading data...", flush=True)
    daily, lob = load_data(sample=False, with_lob=True)
    returns = compute_returns(daily)

    print(f"Building PCA residual returns (K={args.n_factors}, lookback={LOOKBACK})...", flush=True)
    residuals = build_residual_returns(returns, n_factors=args.n_factors)
    print(f"  Residual matrix: {residuals.shape[0]} days × {residuals.shape[1]} assets")

    results = []
    print("\nEvaluating signals (raw vs residual IC)...", flush=True)
    for name, module in MODULES.items():
        lob_arg = lob if name in ("lob_imbalance", "ofi_ou") else None
        sig = module.compute(daily, lob_arg)
        ic_raw, ic_res = ic_series_raw_vs_residual(sig, returns, residuals)
        print(f"  {name}:")
        print(f"    raw:      {fmt_stats(ic_raw)}")
        print(f"    residual: {fmt_stats(ic_res)}")
        results.append((name, ic_raw, ic_res))

    # Composite
    ic_dfs_raw  = pd.DataFrame({n: r for n, r, _ in results}).dropna()
    ic_dfs_res  = pd.DataFrame({n: r for n, _, r in results}).dropna()
    comp_raw  = pd.Series(ic_dfs_raw.values @ WEIGHTS_FULL,  index=ic_dfs_raw.index)
    comp_res  = pd.Series(ic_dfs_res.values @ WEIGHTS_FULL,  index=ic_dfs_res.index)
    print(f"  composite_full:")
    print(f"    raw:      {fmt_stats(comp_raw)}")
    print(f"    residual: {fmt_stats(comp_res)}")

    today = date.today().isoformat()
    lines = [
        f"# PCA Residual Signal Evaluation — {today}",
        "",
        f"**PCA factors K={args.n_factors}, lookback={LOOKBACK} days.**",
        "For each day, PCA fitted on prior {LOOKBACK} days of the full return matrix.",
        "Residual = raw return − systematic (projected onto K factors).",
        "",
        "## Results",
        "",
        "| Signal | Raw IC | Raw IR | Resid IC | Resid IR | ΔIR |",
        "|--------|--------|--------|----------|----------|-----|",
    ]
    for name, ic_raw, ic_res in results:
        def ir(s):
            n = len(s)
            if n < 5: return float("nan")
            m = s.mean(); sd = s.std()
            return m/sd*np.sqrt(252) if sd > 0 else float("nan")
        ir_r = ir(ic_raw); ir_res = ir(ic_res)
        delta = ir_res - ir_r if not (np.isnan(ir_r) or np.isnan(ir_res)) else float("nan")
        lines.append(f"| {name} | {ic_raw.mean():.4f} | {ir_r:.2f} | "
                     f"{ic_res.mean():.4f} | {ir_res:.2f} | {delta:+.2f} |")
    # composite
    ir_r = comp_raw.mean()/comp_raw.std()*np.sqrt(252)
    ir_res = comp_res.mean()/comp_res.std()*np.sqrt(252)
    delta = ir_res - ir_r
    lines.append(f"| composite_full | {comp_raw.mean():.4f} | {ir_r:.2f} | "
                 f"{comp_res.mean():.4f} | {ir_res:.2f} | {delta:+.2f} |")

    lines += [
        "",
        "## Interpretation",
        "",
        "- **ΔIR > 0**: signal predicts idiosyncratic returns better than raw returns — "
        "PCA denoising helps",
        "- **ΔIR < 0**: removing factors hurts — signal partially captures systematic moves",
        "- If composite_full ΔIR > 0, consider evaluating against PCA residuals as the "
        "primary IC target going forward",
        "",
        "---",
        f"_Generated by `eval/pca_residual.py` on {today}_",
    ]

    out = Path(__file__).parent.parent / "wiki" / "results" / "pca_residual.md"
    out.write_text("\n".join(lines))
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
