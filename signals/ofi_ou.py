"""
OU quasi-Sharpe OFI signal (Hu & Zhang, 2025, arXiv:2505.XXXXX).

Idea: fit a rolling Ornstein-Uhlenbeck process to per-asset daily OFI.
The trading signal is the quasi-Sharpe ratio:

    signal = (μ - X_t) * κ / σ_ε

where:
    X_t = today's daily OFI (raw level-1 signed flow, normalized by amount)
    μ   = rolling mean of OFI (long-run equilibrium, estimated per asset)
    κ   = mean-reversion speed = -log(b), b = rolling lag-1 autocorrelation of OFI
    σ_ε = innovation noise ≈ rolling_std * sqrt(1 - b²)  (AR(1) residual std)

Compared to plain lob_imbalance:
  - Accounts for how fast OFI reverts (κ): faster-reverting assets get more weight
  - Accounts for noise level (σ_ε): normalizes by signal quality
  - Uses longer history (60-day rolling) rather than a single EOD snapshot

Interpretation (inverted — Chinese retail FOMO dynamic):
  - High positive OFI → above mean → contrarian short signal → positive signal here
  - The OU distance tells us "this OFI anomaly is large AND reverts fast"

Data needed: LOB (falls back to NaN if not provided).
"""

import numpy as np
import pandas as pd

LOOKBACK = 60    # days to fit rolling OU
MIN_PERIODS = 20  # minimum observations for OU parameter estimates


def _build_ofi_matrix(daily: pd.DataFrame, lob: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-(asset, day) daily OFI = sum of signed level-1 flow / amount.
    Returns a (trade_day_id × asset_id) matrix.
    """
    all_days = sorted(daily["trade_day_id"].unique())
    all_assets = sorted(daily["asset_id"].unique())

    # Sum bid - ask across all snapshots per day
    flow = (
        lob[["trade_day_id", "asset_id", "bid_volume_1", "ask_volume_1"]]
        .assign(signed_flow=lambda d: d["bid_volume_1"] - d["ask_volume_1"])
        .groupby(["trade_day_id", "asset_id"])["signed_flow"]
        .sum()
        .reset_index()
    )

    # Normalize by daily amount (market-cap proxy, Kang 2025)
    merged = flow.merge(
        daily[["trade_day_id", "asset_id", "amount"]], on=["trade_day_id", "asset_id"], how="left"
    )
    merged["ofi"] = np.where(merged["amount"] > 0, merged["signed_flow"] / merged["amount"], np.nan)

    mat = merged.pivot(index="trade_day_id", columns="asset_id", values="ofi")
    return mat.reindex(index=all_days, columns=all_assets)


def compute(daily: pd.DataFrame, lob: pd.DataFrame | None = None) -> pd.DataFrame:
    all_days = sorted(daily["trade_day_id"].unique())
    all_assets = sorted(daily["asset_id"].unique())

    if lob is None or lob.empty:
        return pd.DataFrame(np.nan, index=all_days, columns=all_assets)

    ofi = _build_ofi_matrix(daily, lob)

    # Rolling OU parameter estimation (vectorized across assets)
    roll = ofi.rolling(LOOKBACK, min_periods=MIN_PERIODS)

    mu = roll.mean()                                    # long-run mean
    sigma = roll.std()                                  # total std

    # Lag-1 autocorrelation as AR(1) coefficient
    b = ofi.rolling(LOOKBACK, min_periods=MIN_PERIODS).corr(ofi.shift(1))
    b = b.clip(0.001, 0.999)   # keep b in (0, 1) for log and sqrt

    kappa = -np.log(b)                                  # mean-reversion speed
    sigma_eps = sigma * np.sqrt(1.0 - b ** 2)           # innovation noise

    # Quasi-Sharpe signal: distance from mean, weighted by reversion speed, per noise unit.
    # (mu - X_t) is already negative when bid OFI is high → correctly contrarian for
    # Chinese A-shares (retail FOMO drives bid pressure → mean-reversion in price).
    # No inversion needed: unlike raw lob_imbalance which needed flipping, this signal's
    # direction is set by (mu - X_t) rather than X_t itself.
    signal = (mu - ofi) * kappa / sigma_eps.replace(0, np.nan)

    # Cross-sectional z-score per day
    signal = signal.sub(signal.mean(axis=1), axis=0).div(
        signal.std(axis=1).replace(0, np.nan), axis=0
    )

    return signal
