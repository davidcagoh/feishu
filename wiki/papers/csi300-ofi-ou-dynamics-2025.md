# Stochastic Price Dynamics in Response to Order Flow Imbalance: Evidence from CSI 300 Index Futures

**Authors:** Chen Hu, Kouxiao Zhang  
**Venue/Source:** arXiv q-fin.TR  
**arXiv/DOI:** arXiv:2505.17388  
**Date:** May 23, 2025

---

## Core Claim

Order flow imbalance (OFI) in Chinese CSI 300 Index Futures is best modelled not as a Hawkes process (the standard approach) but as an **Ornstein-Uhlenbeck process with memory, driven by a Lévy jump process**. Replacing the drift of geometric Brownian motion with this OU-OFI dynamic yields a tractable model for price evolution that produces a "quasi-Sharpe ratio" (response ratio) — a principled trading trigger derived from OFI magnitude relative to the OU process's equilibrium.

---

## Method

**Signal model:**  
Let `X_t` be the order flow imbalance at time `t`. The model posits:

```
dX_t = κ(θ − X_t) dt + σ dL_t      [OU with Lévy jumps]
dS_t = X_t · S_t dt + S_t dW_t       [price driven by OFI drift]
```

Where:
- `κ` = mean-reversion speed of OFI
- `θ` = long-run OFI equilibrium (often near zero in liquid markets)
- `σ dL_t` = Lévy-driven shocks (fat-tailed order flow bursts)
- `X_t` replaces the constant drift `μ` in standard GBM

**Key derivation:** The paper derives a closed-form expression for the logarithmic return process `log(S_t/S_0)` including its mean and variance conditioned on the current OFI state `X_t`. From this, they define the **quasi-Sharpe ratio (response ratio)**:

```
ρ(X_t) = E[log return | X_t] / Std[log return | X_t]
```

This is the per-unit-risk expected return conditional on current OFI. Trading is triggered when `|ρ(X_t)|` exceeds a threshold.

**Empirical findings:**
- Horizon-dependent heterogeneity: OFI is a strong predictor at very short horizons but decays; the decay rate itself is regime-dependent.
- Regime-dependent memory: in high-volatility regimes, OFI shocks have longer memory (slower κ) — i.e., imbalances persist longer before reverting.

---

## Results

Applied to CSI 300 Index Futures LOB data:
- The OU-Lévy model provides better in-sample fit than Hawkes processes for order flow dynamics.
- The quasi-Sharpe ratio derived from the model provides a more principled entry/exit threshold than fixed OFI cutoffs.
- Regime-conditional analysis shows significantly different OFI predictability across market states, reinforcing the importance of regime detection (see [[reinforcement-learning]] for prob-DDPG approach).

---

## Relevance to Feishu Competition

This paper is directly set in the Chinese market and gives two actionable ideas for upgrading LOB signals:

**Idea A — OU parameter estimation as a daily signal:**  
Fit a rolling OU model to each asset's intraday OFI time series. The deviation of current OFI from its OU equilibrium (`X_t − θ̂`) is the signal. When OFI is far from equilibrium, expect reversion toward `θ̂`, and price will follow.

```python
import numpy as np
import pandas as pd

def fit_ou_moments(series):
    """Estimate OU parameters κ, θ, σ from observed time series via MLE/moments."""
    x = series.dropna().values
    if len(x) < 10:
        return np.nan, np.nan, np.nan
    dt = 1.0  # unit time steps (intraday snapshots)
    # Method of moments: use lag-1 autocorrelation
    ac = np.corrcoef(x[:-1], x[1:])[0, 1]
    ac = np.clip(ac, 1e-6, 1 - 1e-6)
    kappa = -np.log(ac) / dt
    theta = x.mean()
    sigma = x.std() * np.sqrt(2 * kappa)
    return kappa, theta, sigma

def compute_response_ratio(ofi_series, lookback=40):
    """
    Daily OU-based response ratio (quasi-Sharpe) for each asset.
    ofi_series: time-ordered daily OFI values for one asset.
    Returns series of response ratios.
    """
    results = []
    for i in range(lookback, len(ofi_series)):
        window = ofi_series.iloc[i - lookback:i]
        kappa, theta, sigma = fit_ou_moments(window)
        if np.isnan(kappa) or sigma < 1e-8:
            results.append(np.nan)
            continue
        x_t = ofi_series.iloc[i]
        # Expected log return proportional to (x_t - theta)
        # Variance = sigma^2 / (2*kappa)
        e_ret = (x_t - theta)          # direction and magnitude of expected price move
        var_ret = sigma**2 / (2 * kappa + 1e-8)
        rho = e_ret / (np.sqrt(var_ret) + 1e-8)  # quasi-Sharpe
        results.append(rho)
    return pd.Series(results, index=ofi_series.index[lookback:])


# Apply to Feishu LOB data
# Step 1: compute end-of-day OFI per asset
lob['ofi'] = (lob['bid_volume_1'] - lob['ask_volume_1']) / (
    lob['bid_volume_1'] + lob['ask_volume_1'] + 1e-8
)
eod_ofi = (
    lob.sort_values('time')
    .groupby(['asset_id', 'trade_day_id'])['ofi']
    .last()
    .reset_index()
)

# Step 2: for each asset, compute rolling response ratio
signal_list = []
for asset_id, grp in eod_ofi.groupby('asset_id'):
    grp = grp.set_index('trade_day_id').sort_index()
    rr = compute_response_ratio(grp['ofi'], lookback=40)
    rr.name = asset_id
    signal_list.append(rr)

response_ratio_df = pd.concat(signal_list, axis=1).T  # assets × days
```

**Idea B — Regime-conditional OFI predictability:**  
Estimate `κ` rolling. When `κ` is small (slow reversion, high OFI memory), OFI signals are more persistent and reliable. Weight OFI signals by `κ_t` as a confidence measure.

```python
# Low κ → OFI persists longer → OFI signal is more reliable this period
# Weight: confidence_weight = κ_t / max(κ_history)
```

This adds a self-calibrating quality filter to the existing LOB imbalance signal (#1) and connects to the regime-conditioning idea in Signal #5.

---

## Concepts
→ [[limit-order-book]] | [[mean-reversion]] | [[reinforcement-learning]] | [[chinese-ashore-market]]
