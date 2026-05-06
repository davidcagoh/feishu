# Hedging Market Risk and Uncertainty via a Robust Portfolio Approach

**Authors:** Adele Ravagnani, Mattia Chiappari, Andrea Flori, Piero Mazzarisi, Marco Patacca
**Venue/Source:** arXiv q-fin.PM
**arXiv/DOI:** arXiv:2604.02126
**Date:** April 2, 2026

---

## Core Claim
Standard dynamic minimum-variance hedging ignores forecast uncertainty in volatility estimates and over-reacts to volatile periods by updating positions too aggressively. The authors derive a closed-form robust hedge ratio using a box-uncertainty robust optimisation framework: the robust hedge is the standard minimum-variance hedge multiplied by a shrinkage factor proportional to forecast certainty, and it achieves lower turnover and better downside protection.

---

## Method
**Three-component framework:**

1. **Volatility forecasting:** Autoregressive models (HAR-RV family) for multi-step-ahead realised variance and covariance, fit on high-frequency intraday data.

2. **Box-uncertainty robust optimisation:** The true variance `σ²_t` is unknown; it lies in a box `[σ²_forecast − δ, σ²_forecast + δ]` where δ is the forecast uncertainty. The robust hedge minimises the worst-case portfolio variance over this box.

3. **Closed-form robust hedge ratio:**
```
h*_robust = h*_standard × (1 − δ / σ²_forecast)
```
where `h*_standard = Cov(r_port, r_hedge) / Var(r_hedge)` is the standard OLS hedge ratio, and `δ` is estimated from historical forecast errors (e.g., rolling RMSE of σ² forecasts).

**Key insight:** When the volatility forecast is highly uncertain (large δ), the robust hedge ratio automatically shrinks toward zero — the framework recommends *not* rebalancing aggressively when estimates are unreliable.

**Data:** Equity, bond, and commodity ETFs (diversified basket), 2016–2024.

---

## Results
- Robust hedge ratios are more stable (lower time-series variation) than standard dynamic minimum-variance hedges.
- Turnover reduced substantially vs. standard dynamic hedging.
- With transaction costs factored in, the robust approach achieves better risk-adjusted performance (Sharpe, MDD) because stable hedge ratios avoid excessive rebalancing costs during volatile periods.
- Downside protection improves: the robust hedge avoids the "chasing volatility" problem where the standard hedge oscillates into and out of positions during rapid regime transitions.

---

## Implementable Idea
The key insight is directly applicable to our portfolio without derivatives. Our current `vol_managed` overlay is binary (skip rebalancing entirely if market variance > threshold). The robust portfolio framework suggests a softer version: **shrink rebalancing magnitude when volatility forecast uncertainty is high**.

```python
import numpy as np

def robust_rebalance_weights(current_weights, target_weights,
                              sigma_forecast, sigma_rmse, max_shrink=0.8):
    """
    Shrink the rebalance step toward current holdings when vol forecast is uncertain.
    sigma_forecast: current rolling vol estimate (e.g., 22d std)
    sigma_rmse: recent forecast error of sigma (rolling RMSE of sigma over 22d trailing)
    Returns blended weights between current and target.
    """
    # Uncertainty ratio: high = uncertain forecast → shrink more
    delta = sigma_rmse / (sigma_forecast + 1e-8)
    # Shrinkage factor (clipped): 0 = don't rebalance, 1 = full rebalance
    alpha = np.clip(1.0 - delta, 1.0 - max_shrink, 1.0)
    return alpha * target_weights + (1.0 - alpha) * current_weights

# In vol_managed.py or trend_vol_v4.py:
# 1. Compute 22d rolling sigma estimate
# 2. Compute rolling RMSE of the sigma estimate (how wrong it was on past 10d)
# 3. Use robust_rebalance_weights() to blend old and new weights

# Estimate sigma_rmse (rolling error of vol forecast)
def sigma_forecast_rmse(returns_series, vol_window=22, error_window=10):
    """Approximate forecast uncertainty as RMSE of rolling vol vs next-day realised vol."""
    sigma = returns_series.rolling(vol_window).std()
    realised_next = returns_series.shift(-1).abs()  # approximate 1-step realised vol
    error = (sigma - realised_next).rolling(error_window).std()
    return error
```

**Practical effect:** On days when the vol estimate is stable (low σ_RMSE), the portfolio rebalances fully to the target (α ≈ 1). On days of regime transition (high σ_RMSE), it partially sticks to current holdings (α < 1). This reduces turnover and prevents "chasing" a rapidly-changing vol estimate into a drawdown.

**Comparison to current approach:** Our `vol_managed_v2` uses a hard threshold: if variance > 2σ_median, skip entirely. The robust approach provides a continuous spectrum: instead of skip/full, it scales the rebalancing step size by (1 − δ). This is less sensitive to the threshold calibration, which was a known IS-overfitting risk.

**Addresses priority:** Priority 2 — MDD reduction in long-only portfolios. The core mechanism (shrink rebalancing when vol estimate is uncertain) directly addresses the "dynamic vol windows" sub-priority: in high-vol periods when estimates are noisy, the robust approach effectively shortens the "window of trust" and reduces position turnover.

---

## Relevance to Feishu Competition
The robust hedge ratio formula provides a principled, IS-data-free way to tune the aggressiveness of our rebalancing step. Rather than searching for an optimal sigma threshold on IS data (which risks overfitting), we can compute the empirical forecast RMSE of our 60d rolling vol estimate and use it as a signal of how much to trust the current covariance estimate. On days D1–D484 where vol spiked (our MDD episode D265–D367), the vol estimate RMSE was likely high — the robust approach would have held positions more steady during this 102-day drawdown rather than chasing the next-day vol signal. This could be worth 0.5–1.5% MDD improvement. Implementation time: ~1 day. Risk: the δ parameter (uncertainty level) needs one calibration choice; using rolling RMSE of vol forecast is a clean, IS-robust proxy.

---

## Concepts
-> [[mean-reversion]] | [[kelly-betting]]
