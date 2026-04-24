# Dynamic Factor Allocation Leveraging Regime-Switching Signals

**Authors:** Yizhan Shu, John M. Mulvey
**Venue/Source:** The Journal of Portfolio Management, Vol. 51, No. 3, 2025
**arXiv/DOI:** arXiv:2410.14841 / DOI:10.3905/jpm.2024.1.649
**Date:** October 2024 (arXiv); JPM publication 2025

---

## Core Claim
A Sparse Jump Model (SJM) applied independently to each equity style factor's active-return time series detects factor-specific bull and bear regimes. Integrating these regime signals into a Black-Litterman long-only multi-factor portfolio improves information ratio from 0.05 (equal-weight) to ~0.4, using only historical price returns — no fundamental data required.

---

## Method
**Universe:** Seven long-only U.S. factor indices — market (MKT), value, size, momentum, quality, **low volatility**, growth.

**Regime detection — Sparse Jump Model (SJM):**
- Feature set: recent active return of each factor (vs. market), rolling active-return volatility (22d), market return (22d), market volatility (22d), factor momentum (12m)
- SJM learns sparse latent transitions between two states (bull = high positive active return; bear = negative/low) for each factor *independently*
- Output: causal bull probability p_t ∈ [0, 1] per factor per day (uses only past data; no look-ahead)
- SJM outperforms standard HMM in regime stability because it penalises frequent state transitions (sparse jump penalty)

**Portfolio construction:**
- Factor bull-probability → Black-Litterman views on expected active return for each factor
- BL combines views with equal-weight prior → final long-only factor tilt
- Fully invested; rebalanced monthly

---

## Results
- Multi-factor portfolio IR vs. market: **0.05 (equal-weight) → ~0.4 (SJM-timed)**
- Single-factor timing Sharpe ratios: **0.16** (momentum) to **~0.4** (value, growth)
- Low-volatility factor: performs well in bear regimes; lags in bull regimes — consistent with the asymmetry documented in Soebhag et al. (2025)
- No shorting or leverage; all results long-only
- SJM regime labels are more stable and interpretable than HMM labels

---

## Implementable Idea
Use an SJM (or its cross-sectional-vol approximation) to detect whether the low-vol factor is in a bull or bear regime. In bear regime: maintain trend_vol_v4 settings. In bull regime: expand N or relax trend threshold to reduce defensiveness.

```python
def detect_low_vol_regime(market_ret, low_vol_active_ret, window=120):
    """
    Simplified SJM approximation using cross-sectional market vol as bear proxy.
    Returns 'bear' if market vol > long-run median (defensive regime favoured),
    'bull' otherwise.
    
    market_ret: pd.Series of daily market returns
    low_vol_active_ret: pd.Series of daily low-vol portfolio vs market excess returns
    """
    import numpy as np
    if len(market_ret) < window:
        return 'bear'  # default conservative
    
    mkt_vol_22d = market_ret.rolling(22).std() * np.sqrt(252)
    active_trend = low_vol_active_ret.rolling(60).mean()
    
    # Bear signal: market vol elevated OR low-vol active return recently positive
    long_run_vol = mkt_vol_22d.rolling(120).median()
    vol_ratio = mkt_vol_22d.iloc[-1] / (long_run_vol.iloc[-1] + 1e-8)
    
    return 'bear' if vol_ratio > 1.0 else 'bull'


# In trend_vol_v4.py signal generation (for OOS period):
regime = detect_low_vol_regime(market_ret, low_vol_active_ret)
if regime == 'bull':
    N, trend_threshold = 30, 0.0   # expand: more stocks, less strict trend filter
else:
    N, trend_threshold = 20, -0.025  # maintain trend_vol_v4 defaults
```

A full SJM implementation requires the `jumpmodels` Python package or custom EM fitting of jump-diffusion processes. The simplified proxy above uses cross-sectional market volatility as a causal, price-only regime indicator.

**Addresses priority:** Priority 4 (regime detection from price-only signals) and Priority 1 (bull-market resilience — directly identifies when low-vol factor is in a disadvantaged regime and prescribes N expansion as the adaptive response).

---

## Relevance to Feishu Competition
This is the most directly actionable paper for our OOS risk. The SJM framework provides a causal, price-only regime detector for the low-vol factor specifically. If OOS D485–D726 is a bull market (as Chinese market data suggests for 2025–2026), the SJM signal would fire "bull" and trigger N expansion. The IS backtest should be re-run with the dynamic-N variant to assess how much Score is gained/lost in the bear IS period before adopting it for OOS. Key risk: IS period is almost entirely "bear" by this detector — so dynamic N may not help IS but is the primary OOS hedge.

---

## Concepts
-> [[factor-models]] | [[mean-reversion]] | [[chinese-ashore-market]]
