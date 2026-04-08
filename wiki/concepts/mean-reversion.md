# Mean Reversion

A time series is **mean-reverting** if it tends to return towards its long-run mean after deviating from it. This is the core assumption underlying most stat-arb and pairs trading strategies.

---

## Ornstein-Uhlenbeck Process

The canonical continuous-time mean-reverting model:

```
dS_t = κ(θ - S_t) dt + σ dW_t
```

Parameters:
- `θ` — long-run mean (level S reverts to)
- `κ` — mean-reversion speed (higher = faster reversion, shorter half-life)
- `σ` — volatility
- `W_t` — Brownian motion

**Half-life** of mean reversion: `t_{1/2} = ln(2) / κ`  
A half-life of 5 days means a deviation from `θ` decays by 50% in 5 days.

**Discrete-time equivalent (AR(1)):**
```
S_{t+1} = α + β S_t + ε_t
     where β = e^{-κΔt}
```
If `|β| < 1`, the process is mean-reverting. `β` near 1 → slow reversion; `β` near 0 → fast reversion.

---

## Testing for Mean Reversion

| Test | Null | Notes |
|------|------|-------|
| ADF (Augmented Dickey-Fuller) | Random walk (no MR) | p < 0.05 → evidence of MR |
| Hurst exponent | H=0.5 (RW), H<0.5 (MR), H>0.5 (trending) | 0.3–0.45 is good for MR signals |
| Variance ratio test | H=0.5 | |

---

## Regime-Switching Mean Reversion

From [[drl-optimal-trading-partial-info]]: the OU parameters `(θ, κ, σ)` are **not constant** — they switch between regimes via a Markov chain. This captures:
- Bull vs bear regimes (different `θ`)
- Fast vs slow reversion regimes (different `κ`)
- Low vs high volatility regimes (different `σ`)

**Key result from that paper:** knowing the posterior probability of which regime you're in substantially improves trading performance. A point estimate of `θ` (the current long-run mean) is far less useful.

---

## Half-Life and Signal Decay

For a mean-reverting spread with half-life `h` days, the signal has predictive power over roughly a `h`-day horizon. Optimal hold period is approximately `h/2`.

| Half-life | Signal type | Strategy |
|-----------|------------|----------|
| < 1 day | LOB imbalance, microstructure | HFT / intraday |
| 1–5 days | Short-term price reversal | Daily rebalance |
| 5–20 days | Pairs spread, idiosyncratic residual | Weekly rebalance |
| 20–60 days | Industry-relative momentum reversal | Monthly rebalance |

---

## Mean Reversion vs Momentum

These are **not opposites** — they operate at different timescales:
- **Very short term** (< 1 day): mean reversion dominates (bid-ask bounce, microstructure)
- **Short term** (1–12 months): momentum dominates (trend persistence)
- **Long term** (> 3 years): mean reversion returns (value effect, fundamental anchoring)

For the Feishu competition (484 days, daily bars + LOB snapshots), both short-term mean reversion and momentum are exploitable.

---

## Feishu Competition Notes

**Direct test you can run:**
```python
import pandas as pd
from statsmodels.tsa.stattools import adfuller

daily = pd.read_parquet("data/daily_sample.parquet")
# Compute adjusted returns
daily['adj_close'] = daily['close'] * daily['adj_factor']
# Test mean reversion for one asset
asset_prices = daily[daily['asset_id'] == 'A000651']['adj_close']
adf_result = adfuller(asset_prices)
print(f"ADF stat: {adf_result[0]:.3f}, p-value: {adf_result[1]:.3f}")
```

**LOB-based mean reversion:** The opening auction price vs `vwap_0930_0935` (first 5-min VWAP) spread often mean-reverts intraday.

---

## Papers in This Wiki
- [[drl-optimal-trading-partial-info]] — regime-switching OU model, RL trading
- [[statistical-arbitrage]] — factor residuals modelled as mean-reverting
- [[jump-start-control-scientist]] — mathematical framework for OU in a control context
