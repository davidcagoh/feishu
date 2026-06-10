# Volatility Forecasting and Return Prediction under Market Regimes: Evidence from High-Frequency Chinese Equity Data

**Authors:** Xinyue Fang, Robert Ślepaczuk (Quantitative Finance Research Group, University of Warsaw)  
**Venue/Source:** arXiv q-fin  
**arXiv/DOI:** arXiv:2606.09478  
**Date:** June 8, 2026

---

## Core Claim
A two-stage framework combining regime-augmented HARQ volatility forecasting (Markov-switching GJR-GARCH) with XGBoost return prediction, tested on high-frequency CSI 300 Index data (2005–2023), consistently outperforms baseline HARQ models in both volatility forecast accuracy and economic return prediction quality under a strictly walk-forward OOS procedure.

---

## Method
**Stage 1 — Regime-augmented HARQ volatility model:**
- Realized volatility is modelled using a HARQ(1,1) specification that captures long-memory dynamics and incorporates a realized-quarticity correction for measurement noise
- Overlaid with Markov-switching GJR-GARCH to capture regime-specific asymmetric volatility dynamics (bull/bear) and structural market breaks
- Output: regime-conditional vol forecast (each day tagged with its Markov state and expected vol under that state)

**Stage 2 — XGBoost return prediction:**
- Features: Stage-1 vol forecasts, current regime indicator, return-related predictors (short-term momentum, price-to-MA ratios)
- Walk-forward estimation: training on expanding window, predict 1-step ahead
- Target: daily log-return direction or magnitude

**Data:** High-frequency intraday CSI 300 data 2005–2023, aggregated to daily realized volatility via standard 5-min subsampling.

**Evaluation:** Statistical forecasting metrics (RMSE, QLIKE for vol) and economic metrics (portfolio strategy Sharpe/annualised return).

---

## Results
- Regime-aware HARQ-MS-GJR-GARCH consistently outperforms baseline HARQ across all vol forecast metrics
- Incorporating regime indicators into XGBoost return prediction improves both out-of-sample directional accuracy and economic portfolio performance vs models without regime information
- Specific portfolio Sharpe numbers not available from abstract/snippet; confirmed: "regime-aware forecasting consistently outperforms baseline HARQ models across forecast evaluation metrics"

---

## Implementable Idea
Replace the simple 60d rolling standard deviation in `signals/low_vol.py` with a regime-conditional vol estimate. The regime-aware estimate distinguishes between (a) stocks temporarily elevated in a high-vol market regime (still fundamentally quiet — worth holding) and (b) stocks structurally high-vol (exclude).

```python
from arch import arch_model
import numpy as np
import pandas as pd

def regime_aware_vol(returns_series, window=252):
    """
    Estimate regime-conditional vol for a single asset.
    Returns expected next-period vol under current Markov regime.
    Falls back to rolling std if insufficient data.
    """
    if len(returns_series) < window:
        return returns_series.std()

    r = returns_series.iloc[-window:].values * 100  # scale for GARCH

    try:
        # GJR-GARCH(1,1) with Markov-switching: use simpler GJR-GARCH as proxy
        # (full MS-GJR-GARCH requires specialized library; this is the approximation)
        gjr = arch_model(r, vol='Garch', p=1, o=1, q=1, power=2.0)
        res = gjr.fit(disp='off', show_warning=False, options={'maxiter': 50})
        cond_vol = float(res.conditional_volatility.iloc[-1]) / 100
        return cond_vol
    except Exception:
        return returns_series.std()

# In low_vol.py stock-ranking step:
# Replace: daily['vol_60d'] = daily.groupby('asset_id')['ret'].transform(lambda x: x.rolling(60).std())
# With:
daily['vol_regime'] = daily.groupby('asset_id')['ret'].transform(
    lambda x: pd.Series([regime_aware_vol(x.iloc[:i+1]) for i in range(len(x))],
                        index=x.index)
)
```

For the XGBoost return prediction layer (Signal #31): train a daily cross-sectional rank prediction model using GJR-GARCH vol forecast + current Markov regime state as features alongside price-based predictors. This is the most direct path to adding a return-prediction layer to our selection.

**Addresses priority:** Priority 2 (better vol estimation reduces false-positive stock exclusions during temporary market-wide spikes → lower MDD) and Priority 3 (regime indicators + vol forecasts as additional stock-scoring features for the XGBoost layer).

---

## Relevance to Feishu Competition
Our 60d rolling std is a backward-looking blunt instrument. During sudden vol spikes (like our D265–D367 bear episode), it erroneously elevates all stocks' vol estimates simultaneously, causing the portfolio to hold its "least bad" options rather than its genuinely low-vol core. The regime-conditioned estimate would assign each stock a vol forecast conditional on the prevailing market state, filtering out regime-wide noise. The two-stage framework also provides a blueprint for Signal #31: an XGBoost return-prediction model using regime features, which could act as a secondary tiebreaker for stock selection within the trend-filtered low-vol universe.

---

## Concepts
-> [[factor-models]] | [[chinese-ashore-market]]
