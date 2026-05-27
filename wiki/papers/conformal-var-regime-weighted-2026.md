# Taming Tail Risk in Financial Markets: Conformal Risk Control for Nonstationary Portfolio VaR

**Authors:** Marc Schmitt  
**Venue/Source:** arXiv preprint  
**arXiv/DOI:** arXiv:2602.03903  
**Date:** February 3, 2026

---

## Core Claim
Standard rolling-window VaR calibration ignores the regime-dependence of forecast errors. Regime-weighted conformal risk control (RWC) wraps any quantile forecaster with a safety buffer calibrated from regime-similar past periods, providing finite-sample VaR coverage guarantees under weighted exchangeability even when returns are nonstationary.

---

## Method
**Conformal calibration**: given a quantile forecaster `q̂_t(α)`, the calibrated bound is `Q_t(α) = q̂_t(α) + λ_t` where `λ_t` is a safety buffer computed from recent forecast errors.

**RWC (Regime-Weighted Conformal)**:
- Assign weights `w_s ∝ exp(-κ(t-s)) × sim(regime_s, regime_t)` to past time steps, where `sim(·)` measures how similar past regime features are to the current regime (e.g. cosine similarity of vol, skew, market-return features).
- Calibrate `λ_t` as the weighted quantile of past coverage shortfalls.
- Theoretical guarantee: finite-sample coverage holds under weighted exchangeability; approximation bounds derived under smoothly drifting regimes.

**Practical simplification**: exponential time decay alone (`sim = 1`, `w_s ∝ exp(-κ(t-s))`) is shown to be a strong default under drift; regime weighting adds stability when regime detection is reliable.

Validated on the CRSP U.S. equity portfolio. Model-agnostic — works with GARCH, rolling-std, or any quantile forecaster as the base.

---

## Results
- On CRSP US equity: time-weighted conformal calibration outperforms fixed-window VaR on coverage accuracy.
- Regime weighting further improves regime-conditional stability in some configurations (with modest conservativeness cost).
- Finite-sample theoretical coverage guarantee provided (Theorem 1, weighted exchangeability assumption).
- No Sharpe/MDD portfolio results reported — the paper evaluates VaR forecasting accuracy, not trading strategy performance.

---

## Implementable Idea
Replace the binary vol-managed skip rule (`if market_var > 2× median: skip rebalance`) with a regime-weighted VaR bound on position sizes. When the regime-conditioned VaR exceeds a target drawdown budget, reduce position sizes proportionally:

```python
import numpy as np
import pandas as pd

def rwc_position_scale(market_ret_series, var_target=0.03, kappa=0.05, n_lookback=120):
    """
    Returns a [0, 1] position scale factor based on regime-weighted VaR.
    market_ret_series: daily cross-sectional mean returns (pandas Series)
    var_target: target 1-day 95% VaR threshold (e.g. 3% = "acceptable daily loss")
    kappa: exponential decay rate (higher = faster decay, shorter effective memory)
    """
    if len(market_ret_series) < n_lookback:
        return 1.0

    hist = market_ret_series.iloc[-n_lookback:].values
    # Exponential weights (most recent = highest weight)
    ages = np.arange(n_lookback, 0, -1)
    weights = np.exp(-kappa * ages)
    weights /= weights.sum()

    # Weighted quantile of losses (1st percentile = 95th loss percentile)
    losses = -hist  # positive = loss
    sorted_idx = np.argsort(losses)
    cum_w = np.cumsum(weights[sorted_idx])
    var_95_idx = np.searchsorted(cum_w, 0.95)
    var_95 = losses[sorted_idx[var_95_idx]]

    # Scale positions down if VaR exceeds target
    scale = np.clip(var_target / (var_95 + 1e-8), 0.2, 1.0)
    return float(scale)

# In trend_vol_v4 rebalancing step:
# scale = rwc_position_scale(market_ret[:t])
# buy_pct = target_pct * scale  # continuous reduction, not binary skip
```

This is a continuous analogue to our binary vol-managed overlay: instead of fully skipping the rebalance when market variance spikes, it continuously scales down position sizes in proportion to regime-conditional tail risk.

**Addresses priority:** Priority 2 — MDD reduction in long-only portfolios. Provides an alternative to the binary skip rule in `vol_managed_v2` / `trend_vol_v4`, with theoretical coverage guarantees. Signal #28 (new).

---

## Relevance to Feishu Competition
Our current MDD=7.98% is close to the minimum achievable with our portfolio size constraint (min 10 stocks) and IS market conditions. Two existing ideas target this (Signal #23 adaptive window, Signal #27 robust rebalancing). RWC adds a third angle: instead of shrinking the rebalancing step (Signal #27) or shortening the vol window (Signal #23), it directly targets position sizing via a regime-weighted VaR constraint.

In the D265–D367 drawdown episode (102-day sustained bear), our fixed binary threshold triggered intermittently. A regime-weighted exponential decay model would have smoothly increased the VaR estimate as the bear episode deepened, continuously reducing position sizes rather than binary on/off behaviour. Lower position sizes earlier in the drawdown → shallower peak-to-trough → lower MDD.

**Implementation note**: this is OOS-only. Do not test on IS data (parameter space exhausted). The only free parameter, `kappa`, can be set to 0.05 (half-life ≈ 14 days) without IS-fitting.

---

## Concepts
-> [[factor-models]] | [[chinese-ashore-market]]
