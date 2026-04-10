#!/usr/bin/env python3
"""
OU half-life of LOB imbalance per asset.

Fits AR(1): X_t = a + b * X_{t-1} + eps_t  per asset over the full sample.
  Mean reversion speed: kappa = -log(b)      (b = lag-1 autocorrelation)
  Half-life:            t_half = log(2)/kappa = -log(2)/log(b)  (in trading days)

Reports the cross-asset distribution and flags assets with very fast / very slow
mean reversion — potential use as a regime indicator or signal modifier.

Usage:
    python eval/ou_halflife.py
"""

import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from eval.run_eval import load_data

MIN_OBS = 60   # minimum days to fit OU


def compute_ofi_matrix(daily: pd.DataFrame, lob: pd.DataFrame) -> pd.DataFrame:
    """Daily level-1 signed flow / amount per (day, asset)."""
    flow = (
        lob[["trade_day_id", "asset_id", "bid_volume_1", "ask_volume_1"]]
        .assign(sf=lambda d: d["bid_volume_1"] - d["ask_volume_1"])
        .groupby(["trade_day_id", "asset_id"])["sf"].sum().reset_index()
    )
    merged = flow.merge(daily[["trade_day_id", "asset_id", "amount"]],
                        on=["trade_day_id", "asset_id"], how="left")
    merged["ofi"] = np.where(merged["amount"] > 0,
                             merged["sf"] / merged["amount"], np.nan)
    mat = merged.pivot(index="trade_day_id", columns="asset_id", values="ofi")
    all_days = sorted(daily["trade_day_id"].unique())
    all_assets = sorted(daily["asset_id"].unique())
    return mat.reindex(index=all_days, columns=all_assets)


def fit_ou_per_asset(ofi_mat: pd.DataFrame) -> pd.DataFrame:
    """Fit AR(1) per asset, return DataFrame with kappa, half_life, mu, sigma."""
    results = []
    for asset in ofi_mat.columns:
        x = ofi_mat[asset].dropna().values
        if len(x) < MIN_OBS:
            continue
        # OLS AR(1): regress x[1:] on x[:-1]
        x_lag = x[:-1]
        x_cur = x[1:]
        # b = cov(x_cur, x_lag) / var(x_lag)
        b = np.cov(x_cur, x_lag)[0, 1] / np.var(x_lag)
        b = np.clip(b, 1e-6, 1 - 1e-6)
        a = np.mean(x_cur) - b * np.mean(x_lag)
        mu = a / (1 - b)
        resid = x_cur - (a + b * x_lag)
        sigma = np.std(resid)
        kappa = -np.log(b)
        half_life = np.log(2) / kappa

        results.append({
            "asset_id": asset,
            "b": b,
            "kappa": kappa,
            "half_life_days": half_life,
            "mu": mu,
            "sigma_eps": sigma,
            "n_obs": len(x),
        })
    return pd.DataFrame(results).set_index("asset_id")


def main():
    print("Loading data...", flush=True)
    daily, lob = load_data(sample=False, with_lob=True)

    print("Computing daily OFI matrix...", flush=True)
    ofi_mat = compute_ofi_matrix(daily, lob)
    print(f"  OFI matrix: {ofi_mat.shape[0]} days × {ofi_mat.shape[1]} assets")

    print("Fitting OU per asset...", flush=True)
    ou_df = fit_ou_per_asset(ofi_mat)
    print(f"  Fitted for {len(ou_df)} assets (min {MIN_OBS} obs)")

    hl = ou_df["half_life_days"]
    print(f"\nHalf-life distribution (days):")
    for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
        print(f"  p{p:2d}: {np.percentile(hl, p):.2f}")

    fast = (hl <= 1).sum()
    mod  = ((hl > 1) & (hl <= 5)).sum()
    slow = (hl > 5).sum()
    print(f"\nFast mean-reversion (HL ≤ 1 day):  {fast} assets ({fast/len(hl):.0%})")
    print(f"Moderate (1 < HL ≤ 5 days):         {mod} assets ({mod/len(hl):.0%})")
    print(f"Slow (HL > 5 days):                  {slow} assets ({slow/len(hl):.0%})")

    # Top 10 fastest and slowest
    print("\nTop 10 fastest (most mean-reverting) assets:")
    print(ou_df.nsmallest(10, "half_life_days")[["half_life_days", "kappa", "sigma_eps"]].round(4).to_string())
    print("\nTop 10 slowest (most persistent) assets:")
    print(ou_df.nlargest(10, "half_life_days")[["half_life_days", "kappa", "sigma_eps"]].round(4).to_string())

    # Save
    out_csv = Path(__file__).parent.parent / "wiki" / "results" / "ou_halflife_per_asset.csv"
    ou_df.round(6).to_csv(out_csv)
    print(f"\nPer-asset results saved to {out_csv}")

    today = date.today().isoformat()
    lines = [
        f"# OU Half-Life of LOB Imbalance per Asset — {today}",
        "",
        f"Fitted AR(1) to daily OFI (level-1 signed flow / amount) for {len(ou_df)} assets "
        f"(min {MIN_OBS} observations).",
        "",
        "## Half-Life Distribution (trading days)",
        "",
        "| Percentile | Half-Life (days) |",
        "|------------|-----------------|",
    ]
    for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
        lines.append(f"| p{p} | {np.percentile(hl, p):.2f} |")

    lines += [
        "",
        f"- **Fast (HL ≤ 1 day):** {fast} assets ({fast/len(hl):.0%}) — "
        "OFI reverts within the same day; use day-of signal only",
        f"- **Moderate (1–5 days):** {mod} assets ({mod/len(hl):.0%}) — "
        "OFI persists a few days; multi-day rolling signal appropriate",
        f"- **Slow (HL > 5 days):** {slow} assets ({slow/len(hl):.0%}) — "
        "OFI is persistent/trending; OU assumption may be weak",
        "",
        "## Implications for ofi_ou Signal",
        "",
        "- The ofi_ou signal uses a 60-day rolling OU fit per asset, estimating kappa per window.",
        "- Median half-life determines whether the 60-day lookback is appropriate.",
        "- Assets with HL > 30 days effectively have b ≈ 1; the OU model degenerates.",
        "- Future refinement: skip OU signal for assets with HL > 20 days; "
        "fall back to raw imbalance inversion.",
        "",
        "## Per-Asset File",
        "",
        f"Full per-asset results: `wiki/results/ou_halflife_per_asset.csv`",
        "(columns: b, kappa, half_life_days, mu, sigma_eps, n_obs)",
        "",
        "---",
        f"_Generated by `eval/ou_halflife.py` on {today}_",
    ]

    out_md = Path(__file__).parent.parent / "wiki" / "results" / "ou_halflife.md"
    out_md.write_text("\n".join(lines))
    print(f"Report saved to {out_md}")


if __name__ == "__main__":
    main()
