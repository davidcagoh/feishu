# Portfolio Optimization under Fast and Slow Latent Mean-Reverting and Momentum Drift

**Authors:** Dannin J. Eccles, Roger Lee  
**Venue/Source:** arXiv q-fin.MF (Mathematical Finance)  
**arXiv/DOI:** arXiv:2607.01705  
**Date:** July 2, 2026

---

## Core Claim
When a risky asset's drift is driven by two unobserved stochastic factors — one fast-mean-reverting (short-term noise), one slow-mean-reverting (persistent trend) — the optimal partial-information portfolio strategy under power/log/exponential utility has a **closed-form** expression whose signal is exactly a MACD-type (Moving Average Convergence Divergence) indicator: the difference between a fast and a slow Exponential Moving Average (EMA) of past prices, plus a deterministic Volterra correction.

---

## Method
The latent drift model: asset return `dS/S = (μ_fast + μ_slow) dt + σ dW`, where `μ_fast` and `μ_slow` each satisfy OU processes with different reversion speeds (κ_fast >> κ_slow). The investor observes only prices, not the latent drifts. The Kalman filter is applied to estimate the posterior distribution of (μ_fast, μ_slow). The optimal filtered estimate of the combined drift takes the form:

`μ̂_t = α × EMA_fast(t) + β × EMA_slow(t) + Volterra_correction(t)`

where EMA_k(t) = ∫₀ᵗ κ_k e^{-κ_k(t-s)} log S_s ds. The difference `EMA_fast − EMA_slow` is exactly the classical MACD signal. Admissibility and verification results (i.e., the strategy actually solves the HJB equation) are established rigorously.

---

## Results
Theoretical paper — no empirical backtest. Results are mathematical proofs establishing:
1. The Kalman filter for two-scale OU drift yields MACD as the sufficient statistic for optimal allocation
2. Under log utility: optimal position is `w* ∝ μ̂_t / σ²` (same structure as Merton)
3. The Volterra term accounts for the information uncertainty (smaller when prices are more informative)
4. In the two-scale model, a single-EMA investor leaves significant value on the table vs. the dual-EMA investor

---

## Implementable Idea
Replace the current 35-day return threshold in `trend_vol_v4.py` with a MACD-style dual-EMA trend signal. Current filter: `trend_35d = close[-1]/close[-35] - 1 > -0.025`. Proposed filter: `EMA(5) > EMA(35)` (fast EMA above slow EMA), with a tolerance band.

```python
import pandas as pd
import numpy as np

def macd_trend_filter(adj_close_series, fast_span=5, slow_span=35, tolerance=-0.001):
    """
    MACD-style dual-EMA trend filter.
    Returns True if fast EMA > slow EMA - tolerance (uptrend or flat).
    Replaces current 35d return threshold in trend_vol_v4.

    fast_span=5: captures recent short-term momentum
    slow_span=35: matches current 35d trend window horizon
    tolerance=-0.001: allows slight downward tilt (mirrors -0.025 return threshold)
    """
    ema_fast = adj_close_series.ewm(span=fast_span, adjust=False).mean()
    ema_slow = adj_close_series.ewm(span=slow_span, adjust=False).mean()
    macd = ema_fast - ema_slow
    normalised_macd = macd / (ema_slow + 1e-8)
    return normalised_macd > tolerance

# In trend_vol_v4.py selection loop, replace:
# trend_35d = adj_close / adj_close.shift(35) - 1
# eligible = candidates[trend_35d > threshold]
# With:
def select_with_macd_filter(daily, trade_day, fast_span=5, slow_span=35, tolerance=-0.001):
    history = daily[daily['trade_day_id'] <= trade_day].copy()
    history['adj_close'] = history['close'] * history['adj_factor']
    ema_fast = history.groupby('asset_id')['adj_close'].transform(
        lambda x: x.ewm(span=fast_span, adjust=False).mean()
    )
    ema_slow = history.groupby('asset_id')['adj_close'].transform(
        lambda x: x.ewm(span=slow_span, adjust=False).mean()
    )
    latest = history[history['trade_day_id'] == trade_day].copy()
    latest['macd_norm'] = (ema_fast - ema_slow) / (ema_slow + 1e-8)
    latest = latest[latest['macd_norm'].notnull()]
    eligible = latest[latest['macd_norm'] > tolerance]
    return eligible
```

**Advantage over single 35d return:**
- EMA is exponentially weighted (recent days count more) → less sensitive to a single large-move day at the 35d boundary
- Dual-EMA separates short-term fluctuation (fast) from sustained trend (slow) — closer to what the theory derives as optimal
- More robust on bear-market days: EMA(5) > EMA(35) is smoother than comparing close[-1]/close[-35], which can jump discontinuously when a limit-move day exits the window

**Addresses priority:** Priority 3 — Stock selection within the low-vol universe (improves the trend filter's robustness and provides a theoretically grounded dual-timescale signal). New signal idea #36.

---

## Relevance to Feishu Competition
Our 35-day return threshold (`trend_vol_v4`) uses `close[-1]/close[-35] - 1` as the trend indicator. This has a known discontinuity problem: when a limit-move day rolls out of the 35-day window, the 35d return jumps suddenly, causing spurious inclusion/exclusion of stocks. The MACD-style EMA filter is smoother and, according to this paper, is the theoretically optimal estimator of the persistent-trend component of drift. Testing `EMA(5) > EMA(35)` (or variants) as a post-competition improvement to the trend filter is warranted. The tolerance band calibration (-0.001 → roughly −0.1% in EMA ratio) maps approximately to the current −0.025 return threshold.

---

## Concepts
-> [[mean-reversion]] | [[kelly-betting]] | [[factor-models]]
