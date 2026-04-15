# Intraday Factor Smoothing via Kalman Filtering and Tests of Pricing Ability: Evidence from China's A-Share Market

**Authors:** Xiao Wei  
**Venue/Source:** SSRN Working Paper  
**arXiv/DOI:** SSRN:5859882  
**Date:** December 4, 2025

---

## Core Claim
High-frequency intraday price data (1-minute) for Chinese A-shares contains a latent "efficient price" signal that is obscured by microstructure noise (bid-ask bounce, quote discreteness, short-lived disturbances). A Kalman filter applied to a local linear trend state-space model extracts this latent price, and the model's 4-day-ahead forecast, when down-sampled to a daily cross-sectional factor, shows statistically significant pricing ability (IC = 0.0077, annualised L/S return ~12.9%). The factor is modest as a standalone but complements existing daily signals.

---

## Method
**State-space model (local linear trend):**

The observed price at each intraday tick _t_ is:
```
P_t^obs = P_t^latent + η_t        (measurement equation; η_t ~ N(0, σ_meas²))
P_t^latent = P_{t-1}^latent + μ_{t-1} + ε_t  (state transition; ε_t ~ N(0, σ_state²))
μ_t = μ_{t-1} + ξ_t              (drift update; ξ_t ~ N(0, σ_drift²))
```
where:
- `P^latent` is the unobserved efficient price
- `μ_t` is the local trend (drift)
- `η_t` is microstructure noise
- `ε_t`, `ξ_t` are state disturbances

**Kalman filter pass:** Run the Kalman filter through each trading day's 1-minute prices (using OHLC mid-prices: `(H+L)/2`) to obtain the filtered state estimate `P̂_t^latent`.

**Forecast:** Use the Kalman smoother to forecast 4 days ahead:
```
P̂_{t+4}^latent = P̂_t^latent + 4 × μ̂_t
```

**Daily signal construction:**
```
signal_{i,t} = (P̂_{t+4}^latent - P̂_t^latent) / P̂_t^latent
```
This is the model-implied expected 4-day return. Down-sampled to daily frequency (one value per asset per day, computed from the last intraday snapshot of each day).

**Data:** 1-minute prices for CSI 1000 constituents, 2024 (approximately 250 trading days).

---

## Results
| Metric | Value |
|--------|-------|
| Daily IC (mean) | 0.0077 |
| IC-IR (annualised) | 0.07 |
| L/S annualised return | ~12.9% |
| L/S annualised volatility | ~16.9% |
| L/S Sharpe ratio | ~0.58 |

The paper concludes the factor is "more complementary than standalone" and cautions that its robustness across longer samples, different market regimes, and explicit transaction costs requires further investigation. The IC of 0.0077 is substantially below our best daily signals (IC~0.034 for `volume_reversal`) but adds orthogonal information.

---

## Implementable Signal

**LOB-adapted version (no 1-minute data required — uses our 23-24 daily LOB snapshots):**

The paper requires 1-minute data, which we don't have. However, the Kalman smoothing idea translates directly to our LOB mid-price snapshots (09:40, 10:00, ..., ~14:55), which are roughly 20-minute intervals rather than 1-minute.

```python
import numpy as np
import pandas as pd
from pykalman import KalmanFilter

def kalman_latent_price(mid_prices: np.ndarray) -> float:
    """
    Given T intraday mid-price observations, return the Kalman-smoothed
    4-step-ahead forecast return.
    mid_prices: array of LOB mid-prices in chronological order for one asset-day
    """
    if len(mid_prices) < 5:
        return np.nan

    # Local linear trend model
    # State vector: [latent_price, drift]
    # Observation: mid_price = latent_price + noise
    n = len(mid_prices)
    obs = mid_prices.reshape(-1, 1)

    # Transition: [[1, 1], [0, 1]]
    kf = KalmanFilter(
        transition_matrices=[[1, 1], [0, 1]],
        observation_matrices=[[1, 0]],
        initial_state_mean=[obs[0, 0], 0],
        n_dim_state=2,
        n_dim_obs=1,
    )
    kf = kf.em(obs, n_iter=5)  # estimate σ_state, σ_meas from data
    means, _ = kf.smooth(obs)

    latent_price = means[-1, 0]
    drift = means[-1, 1]

    # 4-step-ahead forecast (4 intervals ≈ 80 minutes in LOB cadence, or use as 1-day signal)
    forecast_price = latent_price + 4 * drift

    return (forecast_price - latent_price) / (latent_price + 1e-8)

# Apply per asset per day
lob['mid'] = (lob['ask_price_1'] + lob['bid_price_1']) / 2
signals = lob.sort_values('time').groupby(['asset_id', 'trade_day_id']).apply(
    lambda g: kalman_latent_price(g['mid'].values)
).reset_index(name='kalman_signal')

# Cross-sectional z-score → alpha
signals['alpha'] = signals.groupby('trade_day_id')['kalman_signal'].transform(
    lambda x: (x - x.mean()) / (x.std() + 1e-8)
)
```

**Addresses hypothesis:** Hypothesis #3 — *Does the LOB signal vary intraday (morning momentum vs afternoon reversal)?* Indirectly: the Kalman filter incorporates all intraday snapshots simultaneously rather than using only end-of-day. The drift term `μ_t` estimated from the full intraday trajectory captures whether price is trending vs. mean-reverting within the day, which is precisely the time-of-day information we want to exploit.

---

## Relevance to Feishu Competition
The most actionable aspect of this paper is not the exact IC numbers (which are low) but the **methodology for aggregating intraday LOB snapshots into a single daily signal**. Currently, our `lob_imbalance` signal uses only the EOD snapshot (or a simple mean). This paper suggests that fitting a state-space model to the full intraday trajectory — treating microstructure noise explicitly — could extract a stronger signal.

In the context of our confirmed findings:
- LOB signals are **negatively correlated** with daily signals (r = −0.24 to −0.57), giving high diversification value
- The IC of our current EOD `lob_imbalance` is 0.0045–0.0059 — lower than the paper's 0.0077 — suggesting the full-trajectory Kalman approach could improve our LOB component

However, the paper's IC-IR of 0.07 (vs. our LOB IC-IR ~2.40 after inversion) suggests the absolute signal strength is modest. The main benefit for our competition setup is potential improvement to the LOB component of `composite_full`, which already contributes to IR doubling via orthogonality with daily signals. Even a small IC improvement in the LOB component (0.005 → 0.008) would lift the composite's IC stability.

**Practical caution:** The `pykalman` EM estimation requires sufficient intraday variation to identify σ_state vs. σ_meas. On days with very low volume (few quotes updating), the EM may not converge well. Filter for days with ≥ 15 LOB snapshots.

---

## Concepts
→ [[limit-order-book]] | [[mean-reversion]] | [[chinese-ashore-market]]
