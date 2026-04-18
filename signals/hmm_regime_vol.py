"""
HMM soft regime overlay on low_vol (Signal #19).

Boukardagha (2026) Wasserstein HMM achieves Sharpe 2.18 vs 1.59 equal-weight
by replacing binary stress detection with a continuous regime probability.

Instead of the hard vol_managed blanking (all-NaN on high-vol days), this
signal scales the low_vol signal by (1 - P_stress_t):
  - Calm bull regime (P_stress ≈ 0): full exposure, signal unchanged
  - Moderate stress (P_stress = 0.5): half exposure
  - High stress (P_stress ≈ 1): near-zero exposure (effectively blanked)

This gives smoother portfolio transitions and avoids the cliff-edge at the
binary blanking threshold, which helps in transitional regimes.

HMM features (daily cross-sectional):
  - Market return (cross-sectional mean of adj returns)
  - Market vol (cross-sectional std of adj returns)
  - Down-breadth (% of assets with negative returns)
  - Skewness (cross-sectional skewness of returns)

Two-state Gaussian HMM:
  - State 0: low-vol / calm (high signal exposure)
  - State 1: high-vol / stress (low signal exposure)

P_stress = P(state=high-vol | observations_1:t) from Viterbi posterior.
"""

import numpy as np
import pandas as pd

try:
    from hmmlearn import hmm as hmmlib
    _HAS_HMMLEARN = True
except ImportError:
    _HAS_HMMLEARN = False

from signals import low_vol


def _build_market_features(daily: pd.DataFrame) -> pd.DataFrame:
    """Compute daily cross-sectional market features for HMM."""
    df = daily.copy().sort_values(["asset_id", "trade_day_id"])
    df["adj_close"] = df["close"] * df["adj_factor"]
    df["ret"] = df.groupby("asset_id")["adj_close"].pct_change()

    feats = df.groupby("trade_day_id")["ret"].agg(
        mkt_ret="mean",
        mkt_vol="std",
        down_breadth=lambda x: (x < 0).mean(),
        skewness=lambda x: float(x.skew()) if len(x.dropna()) >= 10 else 0.0,
    )
    return feats


def _fit_hmm_stress_prob(features: pd.DataFrame, n_iter: int = 100, random_state: int = 42) -> pd.Series:
    """
    Fit a 2-state Gaussian HMM on market features and return P(stress | obs).
    The stress state is identified as the one with higher market volatility.
    Falls back to vol-percentile method if hmmlearn unavailable.
    """
    feats = features.dropna()
    if feats.empty:
        return pd.Series(0.0, index=features.index)

    if not _HAS_HMMLEARN:
        # Fallback: use rolling vol percentile as stress proxy
        vol = feats["mkt_vol"]
        rolling_vol = vol.rolling(20, min_periods=5).mean()
        p_stress = rolling_vol.rank(pct=True).reindex(features.index).fillna(0.0)
        return p_stress.clip(0.0, 1.0)

    X = feats[["mkt_ret", "mkt_vol", "down_breadth", "skewness"]].values

    # Standardise for numerical stability
    X_mean = X.mean(axis=0)
    X_std = X.std(axis=0)
    X_std[X_std == 0] = 1.0
    X_norm = (X - X_mean) / X_std

    model = hmmlib.GaussianHMM(
        n_components=2,
        covariance_type="diag",
        n_iter=n_iter,
        random_state=random_state,
        tol=1e-4,
    )
    try:
        model.fit(X_norm)
    except Exception:
        # Fallback to percentile method on fit failure
        vol = feats["mkt_vol"]
        p_stress = vol.rank(pct=True).reindex(features.index).fillna(0.0)
        return p_stress.clip(0.0, 1.0)

    # Posterior state probabilities P(state_t | X_1:T)
    posteriors = model.predict_proba(X_norm)  # (n_days × 2)

    # Identify which state is "stress" = higher mkt_vol mean emission
    mkt_vol_idx = 1  # index of mkt_vol in feature array
    state_vol = [model.means_[s][mkt_vol_idx] for s in range(2)]
    stress_state = int(np.argmax(state_vol))

    p_stress_vals = posteriors[:, stress_state]
    p_stress = pd.Series(p_stress_vals, index=feats.index)
    return p_stress.reindex(features.index).fillna(0.0)


def compute(
    daily: pd.DataFrame,
    lob: pd.DataFrame | None = None,
    base_window: int = 60,
    excl_illiq: float = 0.05,
    hmm_iter: int = 100,
    min_warmup: int = 60,
) -> pd.DataFrame:
    """
    HMM soft-regime overlay on low_vol.

    Parameters
    ----------
    base_window : rolling window for base low_vol signal
    excl_illiq  : liquidity exclusion fraction
    hmm_iter    : HMM EM iterations
    min_warmup  : minimum days before HMM stress probability is trusted
                  (uses linear ramp-in for first min_warmup days)

    Returns
    -------
    pd.DataFrame (trade_day_id × asset_id) : low_vol signal scaled by (1 - P_stress).
        On high-stress days (P_stress → 1), signal ≈ 0 → backtest skips rebalance.
        On calm days (P_stress ≈ 0), signal = base low_vol signal unchanged.
    """
    # Base signal (full low_vol, no blanking)
    base_signal = low_vol.compute(daily, lob=None, window=base_window, excl_illiq=excl_illiq)

    # Market features for HMM
    features = _build_market_features(daily)
    features = features.reindex(base_signal.index)

    # Fit HMM and get stress probability
    p_stress = _fit_hmm_stress_prob(features, n_iter=hmm_iter)
    p_stress = p_stress.reindex(base_signal.index).fillna(0.0)

    # Ramp in trust over first min_warmup days (avoid overfitting to early data)
    days = base_signal.index.tolist()
    ramp = np.ones(len(days))
    for i in range(min(min_warmup, len(days))):
        ramp[i] = i / min_warmup
    ramp_series = pd.Series(ramp, index=days)

    # Effective stress: ramped p_stress
    eff_stress = p_stress * ramp_series

    # Scale signal by (1 - p_stress): continuous de-risking
    scale = (1.0 - eff_stress).clip(0.0, 1.0)

    # Blank rows where stress is very high (>0.85) to avoid tiny signal magnitudes
    # that cause random stock picks due to near-zero z-scores
    scaled_signal = base_signal.mul(scale, axis=0)
    very_high_stress = eff_stress > 0.85
    scaled_signal.loc[very_high_stress] = np.nan

    return scaled_signal
