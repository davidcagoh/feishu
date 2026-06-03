# Continuous Timing Signals for Growth-Defensive Style Allocation: Factor Attribution, Risk Matching, and Out-of-Sample Evidence

**Authors:** Zheli Xiong  
**Venue/Source:** arXiv q-fin.PM  
**arXiv/DOI:** arXiv:2605.20636  
**Date:** May 20, 2026

---

## Core Claim
Conditional allocation between a growth/technology ETF basket and a defensive income/value ETF basket can be improved over binary threshold switching by using continuous tanh-mapped timing signals with EWMA smoothing; a 50% max-active-tilt policy achieves Sharpe 1.01 with OOS walk-forward and post-2022 validation.

---

## Method
- Two baskets: growth/tech ETF basket (G) and defensive income/value ETF basket (D)
- Macro-market timing signals combined via interaction terms smoothed with **softplus** activation
- Total score mapped to G/D allocation weights through **hyperbolic tangent (tanh)** — providing a continuous, bounded transition rather than a cliff-edge binary switch
- Realized weights smoothed with **EWMA** (span ≈ 5 days) to reduce turnover from whipsawing
- 50% maximum active tilt constraint; 10bp round-trip transaction costs
- Evaluation window: June 28, 2017 to May 15, 2026
- Validation: walk-forward out-of-sample and post-2022 holdout

**Fama-French 5-factor + momentum attribution of the G-D relative portfolio:**
- Market β = 0.273 (slight positive market exposure → defensive is closer to market-neutral)
- HML β = −0.552 (growth = growth tilt, defensive = value tilt; large and expected)
- Momentum β = 0.117 (mild momentum tilt in growth relative to defensive)
- α = 1.95% annualised (Newey-West t = 0.81; not statistically significant at 5%)

---

## Results
| Config | CAGR | Sharpe | MDD |
|--------|------|--------|-----|
| Smooth-score policy (50% tilt, 10bp costs) | 19.24% | 1.01 | −31.63% |

- Walk-forward validation confirms Sharpe > 1.0 holds OOS
- Post-2022 analysis shows the primary value-add is drawdown reduction relative to static growth-tilt benchmark

---

## Implementable Idea
Replace the binary vol-ratio regime detector in `signals/regime.py` with a continuous tanh-score signal for N interpolation between v4 (N=20) and v5 (N=30). The tanh mapping prevents the cliff-edge transitions in our current binary switch; EWMA smoothing reduces portfolio churn.

```python
import numpy as np
import pandas as pd

def continuous_regime_n(market_ret, n_base=20, n_bull=30,
                        vol_window=22, median_window=120, ewma_span=5):
    """
    Returns a continuous N between n_base (bear) and n_bull (bull).
    Uses tanh(vol_signal + trend_signal) → EWMA → N interpolation.
    """
    # Vol-ratio signal: negative = current vol above median (bearish)
    vol_22d = market_ret.rolling(vol_window).std()
    vol_median = vol_22d.rolling(median_window).median()
    vol_signal = -(vol_22d / (vol_median + 1e-8) - 1.0)

    # 35d market trend signal (Sharpe ratio of recent market returns)
    trend_signal = market_ret.rolling(35).mean() / (market_ret.rolling(35).std() + 1e-8)

    # Combine, compress to [-1, 1], EWMA smooth
    raw_score = 0.6 * vol_signal + 0.4 * trend_signal
    smooth_score = pd.Series(np.tanh(raw_score)).ewm(span=ewma_span).mean()

    # Map score ∈ [-1, 1] → N ∈ [n_base, n_bull]
    alpha = (smooth_score + 1.0) / 2.0          # remap to [0, 1]
    n_cont = n_base + (n_bull - n_base) * alpha
    return n_cont.round().clip(n_base, n_bull).astype(int)
```

**Compared to current binary switch (`signals/regime.py`):** current switch has a cliff at vol_ratio=0.75 → v5; this replaces it with a smooth interpolation. EWMA span=5 ≈ 1 trading week lag, matching our daily rebalancing.

**Addresses priority:** Priority 1 — Bull-market resilience. Provides a concrete continuous signal for the v4↔v5 switching problem, with OOS evidence that continuous (tanh + EWMA) outperforms binary threshold in style-allocation tasks.

---

## Relevance to Feishu Competition
- **Direct application:** The binary vol-ratio switch in `signals/regime.py` (used by `trend_vol_v5`) is equivalent to a sign function. Replacing it with tanh-score + EWMA would smooth the N=20↔30 transition, potentially reducing the turnover spike on switch days.
- **Known limitation:** Paper uses US ETF baskets over 2017–2026; direct performance (CAGR 19.24%, MDD −31.63%) is not transferable to Chinese A-shares. The **methodology** (continuous score + EWMA) is what is implementable.
- **Competition context:** Since submission is filed (T016_sell_open.csv), this is a post-competition refinement idea. The current binary switch in regime.py has a known weakness (D458–D481 bull-labelled during market decline); a continuous score would have assigned partial weight rather than full v5 mode in that episode.
- **Research report use:** Provides a recent methodological citation for the growth-defensive style timing decision and validates the continuous-signal approach.

---

## Concepts
-> [[chinese-ashore-market]] | [[factor-models]]
