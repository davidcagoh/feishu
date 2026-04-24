# Advancing Portfolio Optimization: Adaptive Minimum-Variance Portfolios and Minimum Risk Rate Frameworks

**Authors:** Ayush Jha, Abootaleb Shirvani, Ali M. Jaffri, Svetlozar T. Rachev, Frank J. Fabozzi
**Venue/Source:** SSRN Working Paper / arXiv
**arXiv/DOI:** arXiv:2501.15793 / SSRN:5112523
**Date:** January 2025

---

## Core Claim
An Adaptive Minimum-Variance Portfolio (AMVP) framework that replaces static rolling-window covariance with ARFIMA-FIGARCH time-varying covariance estimates achieves superior drawdown control and more stable portfolio weights during structural market breaks and regime transitions, compared to standard minimum-variance approaches.

---

## Method
**Covariance model — ARFIMA-FIGARCH:**
- ARFIMA (AutoRegressive Fractionally Integrated Moving Average): captures long-memory dynamics in return autocorrelation
- FIGARCH (Fractionally Integrated GARCH): models long-memory in conditional variance — volatility shocks decay hyperbolically (slowly) rather than exponentially, capturing the empirical "rough volatility" property
- Non-Gaussian innovations: Normal Inverse Gaussian (NIG) distribution captures fat tails and asymmetry observed in equity returns
- Covariance matrix updated iteratively in real time as new returns arrive

**Portfolio construction — AMVP:**
- At each rebalance, solve the standard minimum-variance problem using the ARFIMA-FIGARCH conditional covariance matrix
- "Minimum Risk Rate" (MRR) framework: defines a floor on the portfolio variance reduction achievable, ensuring the covariance estimate is not spuriously precise

**Test markets:** Cryptocurrency portfolios and global equity portfolios. Evaluated on both in-sample fit and out-of-sample drawdown/Sharpe.

---

## Results
- AMVP demonstrates **superior risk reduction during structural market breaks** (regime transitions, volatility spikes) versus static rolling-window minimum-variance
- **Reduced turnover** relative to models that react too fast or too slow to regime changes — FIGARCH's long-memory properties mean covariance adapts smoothly, not spasmodically
- **More stable portfolio weights** across regimes: less churn during transition periods
- Outperforms on volatility reduction and MDD metrics in periods of heightened market uncertainty
- Specific Sharpe/MDD numbers not publicly available in preprint; authors demonstrate superiority across multiple asset classes and time periods

---

## Implementable Idea
The core practical insight is that a **regime-adaptive volatility window** outperforms a fixed rolling window for minimum-variance stock selection. Our `signals/low_vol.py` uses a fixed 60d rolling std. The FIGARCH insight suggests using a shorter window (20–30d) during high-vol regimes and a longer window (60–90d) during calm regimes:

```python
import numpy as np
import pandas as pd

def adaptive_vol_window(returns_series, base_window=60, min_window=20, max_window=90):
    """
    Regime-adaptive volatility estimate inspired by ARFIMA-FIGARCH.
    Uses shorter window in high-vol regimes (faster adaptation),
    longer window in low-vol regimes (more stability).
    """
    # Current market vol regime: 22d vol vs 120d historical median
    vol_22d = returns_series.rolling(22).std().iloc[-1]
    vol_120d_median = returns_series.rolling(22).std().rolling(120).median().iloc[-1]
    
    if pd.isna(vol_22d) or pd.isna(vol_120d_median):
        return base_window
    
    vol_ratio = vol_22d / (vol_120d_median + 1e-8)
    
    if vol_ratio > 1.5:    # high-vol regime: shorten window for faster response
        return min_window
    elif vol_ratio < 0.75:  # low-vol regime: lengthen window for stability
        return max_window
    else:                  # normal regime: use base window
        return base_window

# In low_vol.py / trend_vol_v4.py, replace fixed 60d with adaptive window:
def compute_adaptive_vol(daily_returns, trade_day, base_window=60):
    market_ret = daily_returns.groupby('trade_day_id').mean()  # cross-sectional mean
    window = adaptive_vol_window(market_ret[:trade_day])
    return daily_returns.groupby('asset_id').apply(
        lambda x: x.rolling(window).std().iloc[-1]
    )
```

**Full ARFIMA-FIGARCH implementation** requires `arch` Python package for GARCH fitting per asset (expensive: 2270 assets × 484 days). The adaptive-window approximation above captures the core insight at negligible computational cost.

**Addresses priority:** Priority 2 (MDD reduction — adaptive covariance responds faster to regime transitions, reducing drawdowns from stale vol rankings) and Priority 1 (bull-market resilience — in calm bull regime, longer window produces more stable rankings, reducing turnover-drag during bull runs).

---

## Relevance to Feishu Competition
Our IS period has one major bear episode (D265–D367, 102-day drawdown in trend_vol_v3). The fixed 60d window was sub-optimal at the start of this episode — a FIGARCH-inspired window would have shortened to 20–30d as market vol spiked, updating vol rankings faster and potentially excluding the deteriorating stocks sooner. For OOS, if a bull-to-bear transition occurs in D485–D726, the adaptive window provides a faster response than the fixed 60d approach. The adaptive-window variant should be tested on IS as a robustness check — if it doesn't hurt IS (MDD ≤ 7.98%), it's a low-risk OOS improvement.

---

## Concepts
-> [[factor-models]] | [[mean-reversion]] | [[chinese-ashore-market]]
