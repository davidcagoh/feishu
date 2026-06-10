# Continuous Cash-Overlay Filters for a Static Growth-Defensive Risk Sleeve: Slow-Tail Compensation, V-Shape Crash Brakes, Walk-Forward Validation, and Max-Cash Combination

**Authors:** Zheli Xiong  
**Venue/Source:** arXiv q-fin.PM  
**arXiv/DOI:** arXiv:2606.09025  
**Date:** June 8, 2026

---

## Core Claim
Two complementary continuous cash-overlay filters — a slow-tail compensation filter for persistent bear regimes and a V-shape crash-brake filter for fast drawdown episodes — combined via a max-cash rule, nearly halve maximum drawdown (−33.6% → −16.8% IS, −33.6% → −22.1% OOS) while simultaneously improving CAGR (16.6% → 20.5% IS, 16.1% → 18.1% OOS) on a 2017–2026 walk-forward evaluation.

---

## Method
The risky sleeve is fixed as a 50/50 growth-defensive ETF basket, so the cash fraction is the only tuned variable — isolating the overlay from style-timing decisions (which were the focus of the companion paper arXiv:2605.20636).

**Slow-tail compensation filter:** Targets persistent regimes where the risk-adjusted compensation for holding the risky sleeve deteriorates gradually. Triggered by a combination of rising short-rate (cash yield increasing) and sustained risky-asset instability above baseline. Produces a continuous cash weight escalating toward 1 as conditions worsen.

**V-shape crash-brake filter:** Targets fast drawdown events (market drops >threshold over a short window). Triggers rapid de-risking (high cash weight); includes a V-shape re-entry rule that fades cash weight back down once the market begins recovering.

**Max-cash combination:** Daily cash weight = max(slow_filter_weight, crash_brake_weight). This ensures both slow-building bear regimes and sudden crashes are caught without needing to blend or calibrate the two signals against each other.

Walk-forward validation: filter parameters calibrated on 2004–2016; OOS evaluation 2017–2026 with an expanding-window variant.

---

## Results

| Configuration | CAGR | MDD | Source |
|---|---|---|---|
| Static 50/50 risky sleeve | 16.62% | −33.59% | Baseline |
| Max-cash combo (2017–2026 IS) | **20.45%** | **−16.77%** | Selected-weight walk-forward |
| Max-cash combo (OOS expanding) | **18.05%** | **−22.05%** | Walk-forward OOS |

---

## Implementable Idea
Replace the binary `vol_managed` skip rule in `signals/trend_vol_v4.py` with two continuous cash-weight signals combined via the max rule. The slow-tail maps onto our existing vol-ratio detector; the crash-brake adds a NEW fast-drawdown protection layer not currently in our strategy.

```python
import numpy as np
import pandas as pd

def slow_tail_weight(market_ret, vol_window=22, median_window=120):
    """Continuous cash weight [0,1] for persistent deterioration."""
    vol_22d = market_ret.rolling(vol_window).std()
    vol_med = vol_22d.rolling(median_window).median()
    ratio = (vol_22d / (vol_med + 1e-8)).iloc[-1]
    # tanh escalation: 0 at ratio=1.0, ~0.76 at ratio=2.0, →1 at extreme
    excess = max(ratio - 1.0, 0.0)
    return float(np.tanh(excess * 1.5))

def crash_brake_weight(portfolio_cum_ret, fast_window=5, threshold=0.04,
                       recovery_window=3):
    """Continuous cash weight [0,1] triggered by fast drawdown."""
    fast_draw = portfolio_cum_ret.diff(fast_window).iloc[-1]
    if fast_draw < -threshold:
        return 0.8  # rapid de-risk
    recovery = portfolio_cum_ret.diff(recovery_window).iloc[-1]
    if recovery > 0:
        # V-shape re-entry: fade back at 20% per positive recovery period
        return max(0.0, 0.8 - (recovery / threshold) * 0.4)
    return 0.0

def max_cash_overlay(market_ret, portfolio_cum_ret):
    slow = slow_tail_weight(market_ret)
    crash = crash_brake_weight(portfolio_cum_ret)
    cash_w = max(slow, crash)
    risky_scale = 1.0 - cash_w
    return risky_scale  # multiply target_weights by this
```

Signal #30 (see ideas file). Post-competition refinement only.

**Addresses priority:** Priority 2 — MDD reduction. This is the most complete continuous cash-overlay framework found, with both slow and fast regime protection. Directly extends Signal #29 (continuous tanh-regime detector from arXiv:2605.20636) with a complementary crash-brake that Signal #29 lacks.

**Note:** This paper is by the same author as the already-indexed continuous timing paper (arXiv:2605.20636). Companion contributions: 2605.20636 handles growth-defensive *style* timing; this paper handles the *cash fraction* overlay independently of style.

---

## Relevance to Feishu Competition
Our current vol_managed is binary (if σ > 2×median → skip). This paper shows that two continuous filters — one for slow deterioration, one for fast crashes — together halve MDD while improving CAGR. Given our current trend_vol_v4 MDD = 7.98%: applying the slow-tail filter during D265–D367 bear episode (our worst drawdown window) would likely reduce that episode's depth by 30–50%, potentially pushing Score from 0.4024 to ~0.43+. The crash-brake adds orthogonal protection for sudden sell-offs not preceded by gradual vol escalation. Recommend as first post-competition IS refinement experiment.

---

## Concepts
-> [[mean-reversion]] | [[chinese-ashore-market]]
