# Adaptive Window Selection for Financial Risk Forecasting

**Authors:** Yinhuan Li, Chenxin Lyu, Ruodu Wang  
**Venue/Source:** arXiv preprint (University of Waterloo)  
**arXiv/DOI:** arXiv:2603.01157  
**Date:** March 1, 2026

---

## Core Claim
Standard fixed rolling windows for financial risk modeling fail when the data-generating process has structural breaks. BAWS (Bootstrap-based Adaptive Window Selection) is a data-driven online method that adaptively selects the lookback window at each time step: it shrinks the window when a structural break is detected and expands it in stable regimes, outperforming both fixed windows and existing stability-based alternatives.

---

## Method
At each time step, the realized risk-model score (e.g. VaR exceedance indicator) is compared against a bootstrap-derived threshold. If the realised score exceeds the threshold, the window is shortened (regime change detected); otherwise, it is extended. The bootstrap avoids distributional assumptions. The method applies to any elicitable risk measure: VaR, Expected Shortfall, or their joint elicitation. Key properties: online, computationally light, no model-specification required.

Formally:
```
BAWS at time t:
  1. Compute risk-model score s_t for window W_{t-1}
  2. Draw bootstrap replications of s under null (window stable)
  3. If s_t > q_alpha (bootstrap quantile) → W_t = max(W_min, W_{t-1} - delta)
  4. Else → W_t = min(W_max, W_{t-1} + 1)
```

Simulation studies and empirical analyses on VaR/ES confirm BAWS outperforms the fixed rolling window and the stability-based adaptive window (SAWS) baseline, especially under structural change.

---

## Results
- BAWS outperforms fixed rolling window and stability-based alternatives on VaR and ES forecasting.
- Improvements are most pronounced when there are structural changes in the data-generating process.
- Tested via simulation and empirical financial data; no specific Sharpe/MDD numbers reported (risk-measure forecasting focus, not portfolio returns).

---

## Implementable Idea
Replace the fixed 60-day rolling vol window in `signals/low_vol.py` (and the `trend_vol_v4` selection loop) with a BAWS-adaptive window. Instead of hard-coding `W=60`, run BAWS on the cross-sectional market return std as the risk measure:

```python
def baws_window(market_ret_series, w_init=60, w_min=20, w_max=90,
                n_boot=200, alpha=0.1, delta=5):
    """
    Returns the current adaptive window size.
    market_ret_series: cross-sectional mean daily return series (pandas Series)
    """
    import numpy as np
    W = w_init
    for t in range(w_init, len(market_ret_series)):
        window_data = market_ret_series.iloc[t - W:t].values
        # Risk score: absolute standardised excess (simple VaR exceedance proxy)
        sigma_hat = window_data.std()
        s_t = abs(market_ret_series.iloc[t]) / (sigma_hat + 1e-8)
        # Bootstrap: resample window data, compute same score
        boot_scores = [abs(np.random.choice(window_data, size=W, replace=True).std())
                       for _ in range(n_boot)]
        q_alpha = np.quantile(boot_scores, 1 - alpha)
        if s_t > q_alpha:
            W = max(w_min, W - delta)  # break detected → shorten
        else:
            W = min(w_max, W + 1)      # stable → extend
    return W
```

Feed the resulting adaptive `W` into `signals/low_vol.py` as the `vol_window` parameter each day.

**Addresses priority:** Priority 2 — dynamic vol windows for MDD reduction. This is the principled replacement for the FIGARCH-heuristic in Signal #23 (adaptive vol window), using a bootstrap structural-break test instead of hard-coded vol-ratio thresholds.

---

## Relevance to Feishu Competition
Our current `trend_vol_v4` uses a fixed 60-day rolling vol window throughout the IS period. The IS period contains a 102-day drawdown episode (D265–D367) where the market was in a structural bear regime — a shorter window would have responded faster, excluding deteriorating stocks sooner. BAWS would have automatically shrunk the window at the onset of this bear episode and expanded it again during the subsequent recovery. Implementable as Signal #23b (BAWS variant), tested OOS-only as the IS parameter space is exhausted.

---

## Concepts
-> [[factor-models]] | [[chinese-ashore-market]]
