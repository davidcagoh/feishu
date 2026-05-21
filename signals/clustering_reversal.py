"""
Clustering-Augmented Reversal — Jiao & Zheng (Nov 2025).

See `wiki/papers/clustering-augmented-reversal-china-2025.md` for the
indexed paper. See `wiki/decisions/002-kill-criteria-clustering-reversal.md`
for the pre-registered evaluation protocol.

Mechanism (long-only adaptation)
--------------------------------
At each day t (after `lookback` warmup):

  1. Cluster the valid universe using a 60d return-series similarity
     metric (PCA whiten → K-means).
  2. Compute each stock's 5d cumulative log-return.
  3. Compute each cluster's mean 5d return.
  4. Signal = z-score(−(stock_5d_return − cluster_mean_5d_return)).

A stock that has *under-performed its cluster* over the past 5 days
gets a high signal — the long-only adaptation of the paper's
within-cluster reversal long leg.

Why 5d (not 1d)
---------------
Feishu's execution-gap problem (`wiki/_index.md` critical discovery):
1d reversal alpha is the overnight gap, which has happened before
`vwap_0930_0935` [t]. A 5d cluster-relative move is multi-bar and
takes multiple sessions to mean-revert — the alpha plays out over the
buy window, not before it.

Status
------
**SHELVED 2026-05-20** — pre-registered validation failed Gate 1 (standalone
viability) and Gate 3 (portfolio additivity). Standalone CAGR was
−44.29% on full IS (MDD 69.97%, kurt +17.59). Gate 2 (orthogonality)
*did* pass — pairwise correlation with trend_vol_v4 was 0.054 — but
that doesn't help when the signal is buying crashing stocks. See
`wiki/results/2026-05-20-clustering-reversal-validation.md`.

The 5d cluster-relative horizon does not rescue reversal from the
overnight-gap execution problem; if anything, multi-day underperformers
within their clusters keep crashing through the buy window.

Module retained for reproducibility; do not deploy.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


N_STOCKS = 20  # eval_layers driver picks this up


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    lookback: int = 60,
    n_clusters: int = 10,
    reversal_window: int = 5,
    excl_illiq: float = 0.05,
    vol_window: int = 20,
    sigma_threshold: float = 3.0,
    pca_components: int = 20,
    random_state: int = 42,
) -> pd.DataFrame:
    """Return a (trade_day_id × asset_id) z-scored signal DataFrame.

    Higher value → stock has under-performed its cluster over the past
    `reversal_window` days → expected reversal long.
    """
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    ret_matrix = df.pivot(index="trade_day_id", columns="asset_id", values="ret")
    log_ret_matrix = np.log1p(ret_matrix)
    cum_ret = log_ret_matrix.rolling(reversal_window, min_periods=reversal_window).sum()

    all_days: list[str] = ret_matrix.index.tolist()

    # Liquidity filter (5% most illiquid by 20d avg amount)
    if excl_illiq > 0.0:
        amount_mat = df.pivot(index="trade_day_id", columns="asset_id", values="amount")
        liq_20d = amount_mat.rolling(20).mean()
        liq_threshold = liq_20d.quantile(excl_illiq, axis=1)
        illiquid_mask = liq_20d.lt(liq_threshold, axis=0)
    else:
        illiquid_mask = pd.DataFrame(False, index=ret_matrix.index, columns=ret_matrix.columns)

    # Vol-managed blanking: skip high-variance days
    ret_sq = ret_matrix ** 2
    daily_var = ret_sq.mean(axis=1)
    rolling_var = daily_var.rolling(vol_window, min_periods=vol_window).mean()
    median_var = rolling_var.median()
    if median_var > 0 and not np.isnan(median_var):
        high_vol_mask = rolling_var > (sigma_threshold * median_var)
    else:
        high_vol_mask = pd.Series(False, index=ret_matrix.index)

    signal_rows: dict[str, pd.Series] = {}

    for i, day in enumerate(all_days):
        if i < lookback:
            continue
        if day not in cum_ret.index or cum_ret.loc[day].notna().sum() < n_clusters * 2:
            continue

        window_rets = ret_matrix.iloc[i - lookback: i]

        valid = window_rets.columns[window_rets.notna().sum() >= lookback // 2].tolist()

        if day in illiquid_mask.index:
            illiq_today = illiquid_mask.loc[day]
            valid = [a for a in valid if not illiq_today.get(a, False)]

        cum_today = cum_ret.loc[day, valid].dropna()
        valid = cum_today.index.tolist()

        if len(valid) < n_clusters * 2:
            continue

        # Cluster on 60d return series (standardised, PCA-whitened)
        X = window_rets[valid].fillna(0.0).values.T  # (n_assets × lookback)
        stds = X.std(axis=1, keepdims=True)
        stds[stds == 0] = 1.0
        X = X / stds

        n_comp = min(pca_components, X.shape[0] - 1, X.shape[1] - 1)
        if n_comp >= 2:
            X_in = PCA(n_components=n_comp, random_state=random_state).fit_transform(X)
        else:
            X_in = X

        k = min(n_clusters, len(valid) // 2)
        labels = KMeans(n_clusters=k, random_state=random_state, n_init=5).fit_predict(X_in)

        # Cluster mean 5d return + within-cluster demean
        cluster_mean = pd.Series(0.0, index=valid)
        for cid in range(k):
            members = [valid[j] for j, lbl in enumerate(labels) if lbl == cid]
            if not members:
                continue
            mu = cum_today[members].mean()
            cluster_mean.loc[members] = mu

        relative = cum_today - cluster_mean
        signal_today = -relative  # under-performers → high signal

        # Cross-sectional z-score (consistent with other signals)
        sd = signal_today.std()
        if sd > 0:
            signal_today = (signal_today - signal_today.mean()) / sd
        else:
            signal_today = signal_today * 0.0

        row = pd.Series(np.nan, index=ret_matrix.columns)
        row.loc[signal_today.index] = signal_today.values
        signal_rows[day] = row

    if not signal_rows:
        return pd.DataFrame()

    signal = pd.DataFrame(signal_rows).T
    signal.index.name = "trade_day_id"
    signal.loc[high_vol_mask.reindex(signal.index).fillna(False)] = np.nan
    return signal
