"""
K-means cluster-constrained low-vol selection (Signal #20).

Jiao & Zheng (Nov 2025) show that K-means cluster-constrained selection
yields 2.28–2.50%/month alpha and addresses portfolio concentration.

Problem with plain low_vol: sector-concentrated picks (~7 effective bets,
r̄=0.43 within-cluster). Fix: cluster assets by return correlation, then
pick the best low-vol stock(s) from EACH cluster.

Algorithm per day:
  1. Build (window × n_assets) return matrix for past `lookback` days.
  2. Standardise each asset's return series (zero mean, unit std).
  3. K-means cluster asset return series into K clusters.
  4. Within each cluster, rank by low-vol signal (low variance = high rank).
  5. Select top `n_per_cluster` stocks per cluster → K × n_per_cluster stocks.
  6. Apply vol_managed high-vol day blanking overlay.

The signal output is a binary indicator: selected stocks get signal=1,
rest get NaN — the backtest selects top-N by signal which maps to this.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from signals import vol_managed


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    lookback: int = 60,
    n_clusters: int = 10,
    n_per_cluster: int = 2,
    vol_window: int = 20,
    sigma_threshold: float = 3.0,
    excl_illiq: float = 0.05,
    pca_components: int = 20,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    lookback       : days of return history for clustering (default 60)
    n_clusters     : number of K-means clusters (default 10)
    n_per_cluster  : stocks to select per cluster (default 2 → 20 total)
    vol_window     : rolling volatility window for within-cluster ranking (days)
    sigma_threshold: blank days where market var > threshold × median var
    excl_illiq     : fraction of illiquid stocks to exclude (bottom percentile by amount)
    pca_components : PCA dims before KMeans (speeds up clustering, reduces noise)
    random_state   : KMeans random seed for reproducibility
    """
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    ret_matrix = df.pivot(index="trade_day_id", columns="asset_id", values="ret")
    all_days = ret_matrix.index.tolist()

    # Liquidity filter: assets to exclude per day
    if excl_illiq > 0.0:
        amount_mat = df.pivot(index="trade_day_id", columns="asset_id", values="amount")
        liq_20d = amount_mat.rolling(20).mean()
        liq_threshold = liq_20d.quantile(excl_illiq, axis=1)
        illiquid_mask = liq_20d.lt(liq_threshold, axis=0)
    else:
        illiquid_mask = pd.DataFrame(False, index=ret_matrix.index, columns=ret_matrix.columns)

    # Vol-managed market variance proxy for blanking
    ret_sq = ret_matrix ** 2
    daily_var = ret_sq.mean(axis=1)
    rolling_var = daily_var.rolling(vol_window, min_periods=vol_window).mean()
    median_var = rolling_var.median()
    if median_var > 0 and not np.isnan(median_var):
        high_vol_mask = rolling_var > (sigma_threshold * median_var)
    else:
        high_vol_mask = pd.Series(False, index=ret_matrix.index)

    # Rolling vol for within-cluster ranking (60d std; low vol = high rank)
    rolling_std = ret_matrix.rolling(lookback, min_periods=lookback).std()

    # Build signal day-by-day
    signal_rows = {}

    for i, day in enumerate(all_days):
        if i < lookback:
            continue

        # Past `lookback` days of returns for clustering
        window_rets = ret_matrix.iloc[i - lookback: i]  # (lookback × n_assets)

        # Drop assets with too many NaNs in this window
        valid_assets = window_rets.columns[window_rets.notna().sum() >= lookback // 2].tolist()

        # Exclude illiquid assets
        if day in illiquid_mask.index:
            illiq_today = illiquid_mask.loc[day]
            valid_assets = [a for a in valid_assets if not illiq_today.get(a, False)]

        if len(valid_assets) < n_clusters * n_per_cluster:
            continue

        X = window_rets[valid_assets].fillna(0).values.T  # (n_assets × lookback)

        # Standardise each asset's return series
        stds = X.std(axis=1, keepdims=True)
        stds[stds == 0] = 1.0
        X = X / stds

        # PCA for noise reduction before clustering
        n_comp = min(pca_components, X.shape[0] - 1, X.shape[1] - 1)
        if n_comp >= 2:
            pca = PCA(n_components=n_comp, random_state=random_state)
            X_pca = pca.fit_transform(X)
        else:
            X_pca = X

        # K-means clustering
        k = min(n_clusters, len(valid_assets) // n_per_cluster)
        km = KMeans(n_clusters=k, random_state=random_state, n_init=5)
        labels = km.fit_predict(X_pca)

        # Get today's vol for ranking within clusters
        if day in rolling_std.index:
            vol_today = rolling_std.loc[day, valid_assets]
        else:
            continue

        # Select top n_per_cluster (lowest vol) from each cluster
        selected = []
        for cluster_id in range(k):
            members = [valid_assets[j] for j, lbl in enumerate(labels) if lbl == cluster_id]
            if not members:
                continue
            cluster_vols = vol_today[members].dropna()
            if cluster_vols.empty:
                continue
            # Lowest vol = best pick (ascending sort)
            top = cluster_vols.nsmallest(n_per_cluster).index.tolist()
            selected.extend(top)

        if not selected:
            continue

        # Build signal row: selected assets get 1.0, rest get NaN
        row = pd.Series(np.nan, index=ret_matrix.columns)
        row[selected] = 1.0
        signal_rows[day] = row

    if not signal_rows:
        return pd.DataFrame()

    signal = pd.DataFrame(signal_rows).T
    signal.index.name = "trade_day_id"

    # Blank high-vol days (same as vol_managed overlay)
    signal.loc[high_vol_mask] = np.nan

    return signal
