# Feishu Competition — Alpha Signal Ideas

Synthesised from the 7 papers + data structure in CLAUDE.md. Ordered roughly by expected implementability and relevance.

---

## Data Available

- **Daily**: 484 days × 2270 assets — `open`, `high`, `low`, `close`, `volume`, `amount`, `adj_factor`, `vwap_0930_0935`
- **LOB**: ~23–24 snapshots/day/asset, 09:40–15:00 — 10-level ask/bid prices + volumes
- No fundamental characteristics. No calendar mapping (D001–D484 are ordinal).

---

## Tier 1: High-Confidence, Directly Implementable

### 1. LOB Imbalance Signal
**Source:** [[limit-order-book]], [[jump-start-control-scientist]]  
**Idea:** End-of-day LOB imbalance predicts next-day return direction.

```python
# Per asset per day: mean or end-of-day LOB imbalance
imbalance = (bid_volume_1 - ask_volume_1) / (bid_volume_1 + ask_volume_1)
# Cross-sectional rank → alpha signal
```

**Variants to try:**
- Mean imbalance over full day
- End-of-day (last snapshot) imbalance
- Imbalance trend: end-of-day minus start-of-day
- Weighted multi-level: `Σ (1/k) × (bid_vol_k - ask_vol_k) / (bid_vol_k + ask_vol_k)`

---

### 2. Intraday Price-LOB Signal
**Source:** [[limit-order-book]]  
**Idea:** Divergence between opening VWAP and LOB mid-price trajectory predicts close.

```python
# Compute LOB mid prices through the day
lob['mid'] = (lob['ask_price_1'] + lob['bid_price_1']) / 2
# Compare first mid-price (09:40) to last mid-price (14:55)
# Also compare to vwap_0930_0935 (opening auction)
intraday_drift = (last_mid - first_mid) / first_mid
opening_gap = (first_mid - vwap_0930_0935) / vwap_0930_0935
```

---

### 3. Short-Term Reversal
**Source:** [[mean-reversion]], [[statistical-arbitrage]]  
**Idea:** Cross-sectional reversal: assets with high relative return today → negative return tomorrow.

```python
# Adjusted daily return
daily['ret'] = daily.groupby('asset_id')['adj_close'].pct_change()
# Cross-sectional z-score
daily['ret_z'] = daily.groupby('trade_day_id')['ret'].transform(
    lambda x: (x - x.mean()) / x.std()
)
# 1-day reversal signal (negative sign)
signal = -daily['ret_z']
```

**Horizon variants:** 1-day, 3-day, 5-day reversal. Test IC at each lag.

---

### 4. OU Residual Signal (PCA-Neutralised)
**Source:** [[statistical-arbitrage]], [[attention-factors-stat-arb]]  
**Idea:** Remove top K PCA factors from daily returns. Trade the residuals as a mean-reverting signal.

```python
from sklearn.decomposition import PCA

# Build returns matrix (days × assets), fill missing
R = daily.pivot('trade_day_id', 'asset_id', 'ret').fillna(0)

# Rolling PCA (train window = 120 days)
for t in range(120, len(R)):
    train = R.iloc[t-120:t]
    pca = PCA(n_components=10)
    pca.fit(train)
    factors = pca.transform(R.iloc[[t]])
    loadings = pca.components_.T
    residual = R.iloc[t].values - (factors @ pca.components_).flatten()
    # residual is the idiosyncratic mispricing signal
    # z-score across assets → today's alpha
```

**Based on:** Attention Factors paper (2510.11616) — the core insight is that residuals after factor extraction have predictable mean-reversion.

---

## Tier 2: Medium Complexity, Potentially Strong

### 5. Regime-Conditional LOB Signal
**Source:** [[drl-optimal-trading-partial-info]], [[mean-reversion]]  
**Idea:** LOB imbalance has different predictive power in different market regimes. Condition the signal on rolling volatility or trend regime.

```python
# Classify each day into regime based on market-level features
market_vol = R.std(axis=1).rolling(20).mean()  # cross-sectional vol

# Three regimes: low/medium/high vol
regime = pd.qcut(market_vol, 3, labels=['low_vol', 'med_vol', 'high_vol'])

# Compute IC of imbalance signal per regime
for reg in ['low_vol', 'med_vol', 'high_vol']:
    mask = regime == reg
    ic = signal[mask].corrwith(next_day_return[mask])
    print(f"Regime {reg}: mean IC = {ic.mean():.4f}")
```

**Motivation:** From prob-DDPG — knowing the regime dramatically improves strategy. Even a simple 3-regime HMM on the cross-sectional return distribution may be sufficient.

---

### 6. LOB Depth Slope Signal
**Source:** [[limit-order-book]]  
**Idea:** The "shape" of the order book — how quickly depth accumulates away from mid — reveals supply/demand balance.

```python
# Ask depth slope: volume per unit price distance from mid
for k in range(1, 11):
    ask_dist = lob[f'ask_price_{k}'] - lob['mid']
    bid_dist = lob['mid'] - lob[f'bid_price_{k}']

# Steeper ask curve = more sell resistance = bullish (buyers in control)
ask_slope = lob['ask_volume_1'] / (lob['ask_price_1'] - lob['mid'] + 1e-8)
bid_slope = lob['bid_volume_1'] / (lob['mid'] - lob['bid_price_1'] + 1e-8)
depth_asymmetry = (bid_slope - ask_slope) / (bid_slope + ask_slope)
```

---

### 7. Amihud Illiquidity with LOB Enhancement
**Source:** General microstructure  
**Idea:** Classic Amihud illiquidity `|ret|/volume` + LOB spread as liquidity proxy.

```python
daily['amihud'] = (daily['ret'].abs() / daily['volume']).replace([np.inf], np.nan)
# Low-illiquidity assets have more reliable LOB signals
# Weight LOB signals by inverse illiquidity
```

---

## Tier 3: Research-Grade, Longer to Implement

### 8. Linear Portfolio Transformer (Cross-Asset Attention)
**Source:** [[ai-asset-pricing-models]], [[transformer-in-finance]]  
**Idea:** Build price-based "characteristics" for each asset, then apply linear portfolio transformer for cross-asset prediction.

```python
# Characteristics: (T, N, D) tensor
# X_{i,t} = [mom_5d, mom_20d, vol_20d, lob_imbalance_mean, price_to_vwap, ...]

# Linear portfolio transformer:
# w_t = (X_t W X'_t) X_t λ
# Solve for W and λ by minimising negative Sharpe
```

Requires careful regularisation given only 484 days and 2270 assets.

---

### 9. Joint OU + LOB Signal
**Source:** [[drl-optimal-trading-partial-info]], [[limit-order-book]]  
**Idea:** Model LOB imbalance for each asset as an OU process. The mean-reversion level `θ` (estimated rolling) is itself predictive.

```python
# For each asset, fit rolling OU to LOB imbalance time series
# Estimate: κ (reversion speed), θ (long-run mean), σ (vol)
# Compute "deviation": S_t - θ̂_t → this is the trading signal
# High |S_t - θ̂_t| means imbalance is far from typical → expect reversion
```

---

## Signal Evaluation Framework

For each signal, compute:
```python
def evaluate_signal(signal_df, return_df, name):
    """
    signal_df: (days, assets) — cross-sectionally z-scored
    return_df: (days, assets) — next-day adjusted returns
    """
    # Align
    aligned_signal = signal_df.shift(1)  # predict next day
    
    # Daily IC (Spearman)
    ic_series = aligned_signal.corrwith(return_df, axis=1, method='spearman')
    ic_mean = ic_series.mean()
    ic_std = ic_series.std()
    ir = ic_mean / ic_std * np.sqrt(252)
    
    print(f"{name}: IC={ic_mean:.4f}, IC_std={ic_std:.4f}, IR={ir:.3f}")
    return ic_series
```

Target: IC > 0.02, IR > 0.3 on the sample data. Validate IC stability over time (no regime collapse).

---

---

## Tier 1 Additions (from new papers, April 2026)

### 10. Market-Cap Normalised OFI (Matched Filter)
**Source:** [[ofi-matched-filter-normalization-2025]]  
**Idea:** Normalise daily aggregate signed order flow by `amount` (RMB turnover proxy for market cap) instead of raw volume. Reduces heteroskedastic noise by ~2×.

```python
lob['ofi_raw'] = lob['bid_volume_1'] - lob['ask_volume_1']
daily_ofi = lob.groupby(['asset_id', 'trade_day_id'])['ofi_raw'].sum().reset_index()
daily_ofi = daily_ofi.merge(daily[['asset_id', 'trade_day_id', 'amount']], on=['asset_id', 'trade_day_id'])
daily_ofi['ofi_mktcap'] = daily_ofi['ofi_raw'] / daily_ofi['amount']
# Cross-sectional z-score → alpha
daily_ofi['signal'] = daily_ofi.groupby('trade_day_id')['ofi_mktcap'].transform(
    lambda x: (x - x.mean()) / (x.std() + 1e-8)
)
```

**Expected improvement over Signal #1:** higher IC (theoretical 1.99× SNR gain); same data, no extra complexity.

---

### 11. Alpha191 Mean-Reversion Factors (f046 + f071)
**Source:** [[cross-market-alpha191-lasso-2026]]  
**Idea:** Two Chinese short-term trading factors that survive double-selection LASSO in the US market — confirming cross-market robustness. Both are mean-reversion signals anchored to longer-horizon reference levels.

```python
daily['adj_close'] = daily['close'] * daily['adj_factor']

# Factor 046: price position in 20-day high/low range
daily['roll_max'] = daily.groupby('asset_id')['adj_close'].transform(lambda x: x.rolling(20).max())
daily['roll_min'] = daily.groupby('asset_id')['adj_close'].transform(lambda x: x.rolling(20).min())
daily['f046'] = (daily['adj_close'] - daily['roll_min']) / (daily['roll_max'] - daily['roll_min'] + 1e-8)
daily['alpha_046'] = daily.groupby('trade_day_id')['f046'].transform(lambda x: -(x - x.mean()) / (x.std() + 1e-8))

# Factor 071: % deviation from 24-day SMA
daily['sma24'] = daily.groupby('asset_id')['adj_close'].transform(lambda x: x.rolling(24).mean())
daily['f071'] = (daily['adj_close'] - daily['sma24']) / (daily['sma24'] + 1e-8)
daily['alpha_071'] = daily.groupby('trade_day_id')['f071'].transform(lambda x: -(x - x.mean()) / (x.std() + 1e-8))

# Composite
daily['alpha_composite_rev'] = (daily['alpha_046'] + daily['alpha_071']) / 2
```

**Advantage over Signal #3 (1-day reversal):** uses a multi-period anchor (20-day range / 24-day mean), reducing noise from single-day idiosyncratic jumps.

---

### 12. OU Quasi-Sharpe OFI Signal
**Source:** [[csi300-ofi-ou-dynamics-2025]]  
**Idea:** Model per-asset end-of-day OFI as an OU process (rolling 40-day window). The quasi-Sharpe ratio `ρ = (X_t − θ̂) / σ̂_OU` is a principled trading trigger: large |ρ| → OFI far from equilibrium → expect reversion.

```python
def fit_ou(series):
    x = series.dropna().values
    if len(x) < 10: return np.nan, np.nan, np.nan
    ac = np.clip(np.corrcoef(x[:-1], x[1:])[0, 1], 1e-6, 1-1e-6)
    kappa = -np.log(ac)
    theta = x.mean()
    sigma = x.std() * np.sqrt(2 * kappa)
    return kappa, theta, sigma

# End-of-day OFI per asset per day (standard imbalance)
eod_ofi = lob.sort_values('time').groupby(['asset_id', 'trade_day_id']).apply(
    lambda g: (g['bid_volume_1'].iloc[-1] - g['ask_volume_1'].iloc[-1]) /
              (g['bid_volume_1'].iloc[-1] + g['ask_volume_1'].iloc[-1] + 1e-8)
).reset_index(name='ofi')

# Rolling OU fit (40-day window)
signals = []
for asset, grp in eod_ofi.groupby('asset_id'):
    grp = grp.sort_values('trade_day_id').reset_index(drop=True)
    for i in range(40, len(grp)):
        window = grp['ofi'].iloc[i-40:i]
        kappa, theta, sigma = fit_ou(window)
        if np.isnan(kappa) or sigma < 1e-8: continue
        x_t = grp['ofi'].iloc[i]
        rho = (x_t - theta) / (sigma / np.sqrt(2 * kappa + 1e-8))
        signals.append({'asset_id': asset, 'trade_day_id': grp['trade_day_id'].iloc[i], 'quasi_sharpe': rho})

signal_df = pd.DataFrame(signals)
# Cross-sectional z-score and use as alpha (signal direction: large positive rho → OFI above equilibrium → price likely reverts)
signal_df['alpha'] = signal_df.groupby('trade_day_id')['quasi_sharpe'].transform(
    lambda x: -(x - x.mean()) / (x.std() + 1e-8)  # negate: high OFI → next-day reversal
)
```

**Advantage:** self-calibrating threshold — `|ρ|` automatically adapts to each asset's OFI volatility, avoiding fixed imbalance thresholds.

---

---

## Tier 1 Additions (from new papers, April 2026 — session 2)

### 13. Longer Lookback for Low-Vol Selection (60d → 120d / 252d)
**Source:** [[volatility-effect-china-ashare-2021]]  
**Idea:** Blitz et al. use a 3-year window; our 60-day window may be over-reactive to short-term vol spikes. Testing 120-day and 252-day lookbacks may improve portfolio stability and reduce turnover.

```python
daily['adj_close'] = daily['close'] * daily['adj_factor']
daily['ret'] = daily.groupby('asset_id')['adj_close'].pct_change()

for window in [120, 252]:
    daily[f'vol_{window}d'] = daily.groupby('asset_id')['ret'].transform(
        lambda x: x.rolling(window).std()
    )
# Then feed vol_120d or vol_252d into the existing low_vol.py selection logic
# (replace the 60-day rolling std)
```

**Expected benefit:** lower turnover → lower transaction cost drag; more stable portfolio composition.  
**Status:** `[ ] untested`

---

### 14. VMP Inverse-Variance Weighting Overlay
**Source:** [[vol-managed-portfolios-china-2024]]  
**Idea:** After low_vol selects the 100-stock portfolio, replace equal-weighting with inverse-realised-variance weights. Stocks with lower recent variance get larger weight. This is the Moreira-Muir (2017) VMP applied at the intra-portfolio level.

```python
# Within the selected 100 stocks for day t:
var_22d = daily.groupby('asset_id')['ret'].transform(lambda x: x.rolling(22).var())

def vmp_weights(selected_asset_ids, var_series, trade_day):
    vars_ = var_series.loc[(var_series.index.get_level_values('trade_day_id') == trade_day) &
                           (var_series.index.get_level_values('asset_id').isin(selected_asset_ids))]
    inv_var = 1.0 / (vars_ + 1e-8)
    return (inv_var / inv_var.sum()).rename('weight')
```

**Expected benefit:** OOS Sharpe improvement ~52% in the Chinese market context (Wang & Li 2024).  
**Caveat:** Competition's long-only T+1 constraint limits leverage; scale-up in bull markets requires increasing N, not leveraging weights.  
**Status:** `[ ] untested`

---

### 15. Market-Regime Scale Factor (VMP at Portfolio Level)
**Source:** [[vol-managed-portfolios-china-2024]]  
**Idea:** Compute a market-wide realised variance signal to determine whether to be more or less aggressive in stock count N. In low-vol (bull) periods, expand to N=120–150; in high-vol (bear) periods, contract to N=70–80. This addresses low_vol's known bull-market underperformance.

```python
# Market-level realised vol (cross-sectional mean of individual vols, or equal-weight portfolio vol)
market_ret = daily.groupby('trade_day_id')['ret'].mean()
market_vol_22d = market_ret.rolling(22).std() * np.sqrt(252)  # annualised

target_vol = 0.15  # 15% annualised target
scale = (target_vol / (market_vol_22d + 1e-8)).clip(0.5, 2.0)

# Map scale to N:
# scale >= 1.5 → N = 130 (bull market, diversify)
# 1.0 <= scale < 1.5 → N = 100 (baseline)
# scale < 1.0 → N = 75 (bear market, concentrate in lowest-vol)
```

**Status:** `[ ] untested`

---

---

## Tier 2 Additions (from new papers, April 2026 — session 3)

### 16. MTP2-GGM Whitened PCA Residual Signal
**Source:** [[pca-mtp2-residual-factors-2026]]  
**Idea:** After standard PCA de-factoring, apply Ledoit-Wolf precision-matrix whitening to residuals before using them as a contrarian signal. This removes latent common structure that PCA alone misses, producing more orthogonal idiosyncratic components.

```python
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.covariance import LedoitWolf

R = daily.pivot('trade_day_id', 'asset_id', 'ret').fillna(0)
WINDOW, K = 120, 10
signals = {}

for t in range(WINDOW, len(R)):
    train = R.iloc[t - WINDOW:t].values
    today = R.iloc[t].values

    # Step 1: PCA de-factor
    pca = PCA(n_components=K)
    pca.fit(train)
    resid_train = train - pca.inverse_transform(pca.transform(train))
    resid_today = today - pca.inverse_transform(pca.transform(today[np.newaxis, :]))[0]

    # Step 2: Ledoit-Wolf precision whitening (approximate MTP2-GGM)
    lw = LedoitWolf().fit(resid_train)
    resid_whitened = lw.precision_ @ resid_today

    # Contrarian signal
    signals[R.index[t]] = -resid_whitened

signal_df = pd.DataFrame(signals, index=R.columns).T
signal_df = signal_df.apply(lambda col: (col - col.mean()) / (col.std() + 1e-8), axis=1)
```

**Expected benefit vs. current PCA residual:** Vol_rev IR improved from 5.01→11.04 with PCA residuals; whitening should reduce residual cross-correlations further, potentially pushing IC std lower and IR higher.  
**Status:** `[ ] untested`

---

### 17. Kalman-Smoothed LOB Mid-Price Signal
**Source:** [[intraday-kalman-factor-china-2025]]  
**Idea:** Fit a local linear trend state-space model to the intraday LOB mid-price trajectory (using our ~23-24 snapshots/day). The Kalman-smoothed latent price trend and its 4-step forecast form a daily cross-sectional signal. This replaces our simple EOD imbalance with a full-trajectory model.

```python
from pykalman import KalmanFilter

def kalman_signal(mid_prices):
    if len(mid_prices) < 5:
        return np.nan
    obs = mid_prices.reshape(-1, 1)
    kf = KalmanFilter(
        transition_matrices=[[1, 1], [0, 1]],
        observation_matrices=[[1, 0]],
        initial_state_mean=[obs[0, 0], 0],
        n_dim_state=2, n_dim_obs=1,
    )
    kf = kf.em(obs, n_iter=5)
    means, _ = kf.smooth(obs)
    latent_p, drift = means[-1, 0], means[-1, 1]
    forecast = latent_p + 4 * drift
    return (forecast - latent_p) / (latent_p + 1e-8)

lob['mid'] = (lob['ask_price_1'] + lob['bid_price_1']) / 2
kalman_signals = lob.sort_values('time').groupby(['asset_id', 'trade_day_id']).apply(
    lambda g: kalman_signal(g['mid'].values)
).reset_index(name='kalman_signal')
```

**Expected impact:** Modest standalone IC (~0.008 based on paper; our current EOD lob_imbalance IC=0.005). Main value is as a replacement for the LOB component in `composite_full`, which benefits from orthogonality with daily signals.  
**Status:** `[ ] untested`

---

### 18. Cluster-Lag Cross-Asset Signal
**Source:** [[us-china-cross-market-bipartite-2026]]  
**Idea:** The bipartite graph paper shows that intra-universe cross-stock lag effects are exploitable when structured sparsely. Using our 3-cluster IC structure (from `wiki/results/ic_correlation.md`), compute the prior-day cluster-average return and use it as a lagged predictor for individual stock returns.

```python
# Assign assets to 3 IC clusters (from existing analysis)
# cluster_map: dict mapping asset_id → cluster_id (0, 1, 2)

daily['cluster'] = daily['asset_id'].map(cluster_map)

# Prior-day cluster average return
cluster_ret = daily.groupby(['trade_day_id', 'cluster'])['ret'].mean().reset_index(name='cluster_ret')
daily = daily.merge(cluster_ret.rename(columns={'trade_day_id': 'prev_day'}),
                    left_on=['prev_trade_day_id', 'cluster'],
                    right_on=['prev_day', 'cluster'], how='left')

# Signal: deviation from cluster mean return (idiosyncratic relative to cluster)
daily['cluster_lag_signal'] = -(daily['ret'] - daily['cluster_ret'].shift(1))
# Negative: stocks that underperformed cluster yesterday → expect catch-up
```

**Expected value:** Sparse, data-driven; tests hypothesis #4 with available data. May have modest standalone IC but diversifies vs. existing signals.  
**Status:** `[ ] untested`

---

## Priority Order for Implementation

1. ~~LOB imbalance~~ ✅ IC=0.005, IR=2.40 (full LOB eval, 2026-04-10)
2. ~~Market-cap normalised OFI~~ ✅ IC=0.006, IR=1.05 (full LOB eval, 2026-04-10)
3. ~~Short-term reversal~~ ✅ IC=0.019, IR=1.84
4. ~~Alpha191 f046 + f071~~ ✅ IC=0.027/IR=2.38 and IC=0.035/IR=2.79 (2026-04-10, full 484-day)
5. ~~Signal combination~~ ✅ composite_daily IR=5.08, composite_full IR=9.64 (LOB+daily; IC_std halved)
6. ~~PCA residual OU signal~~ ✅ vol_rev IR 5.01→11.04 vs idiosyncratic target; LOB degrades in PCA residual space
7. ~~OU quasi-Sharpe OFI signal (#12)~~ ✅ ofi_ou IR=1.77; median OU half-life=0.31d — OFI i.i.d. at daily frequency
8. Regime-conditional LOB signal — adds the regime insight from DRL paper (optional, diminishing returns)
9. Depth slope / shape signals — novel, exploratory (optional)
10. **Longer lookback low-vol (#13)** — `[ ] untested` — quick win; swap 60d for 120d in low_vol.py
11. **VMP inverse-variance weighting (#14)** — `[ ] untested` — replace equal-weight within portfolio
12. **Market-regime N scaling (#15)** — `[ ] untested` — expand/contract N based on market vol level
13. **MTP2-GGM whitened PCA residual (#16)** — `[ ] untested` — adds precision whitening after PCA; extends pca_residual result
14. **Kalman-smoothed LOB mid-price (#17)** — `[ ] untested` — full-trajectory intraday model for LOB component
15. **Cluster-lag cross-asset signal (#18)** — `[ ] untested` — within-universe bipartite graph proxy

---

## Full-Sample Eval Results (2026-04-10, 484 days)

| Signal | Mean IC | IC Std | IR (ann.) | Hit Rate |
|--------|---------|--------|-----------|----------|
| **composite_full** (LOB+daily) | 0.0341 | 0.056 | **9.64** | **74%** |
| composite_daily | 0.0361 | 0.113 | 5.08 | 66% |
| volume_reversal | 0.0339 | 0.1074 | 5.01 | 64% |
| alpha191_071 | 0.0346 | 0.1966 | 2.79 | 57% |
| price_to_vwap | 0.0270 | 0.1664 | 2.58 | 58% |
| lob_imbalance | 0.0045 | 0.030 | 2.40 | 59% |
| alpha191_046 | 0.0267 | 0.1781 | 2.38 | 56% |
| ofi_ou | 0.0081 | 0.072 | 1.77 | 55% |
| short_term_reversal | 0.0191 | 0.1652 | 1.84 | 57% |
| ofi_matched_filter | 0.0059 | 0.089 | 1.05 | 53% |

**Key observations:**
- LOB IC series are **negatively correlated** with daily signal IC series (r = −0.24 to −0.57) — they capture orthogonal market regimes
- Combining LOB + daily signals collapses IC_std from ~0.11 to 0.056 → IR nearly doubles (composite_full IR=9.64)
- **IC ≠ portfolio alpha**: all reversal/IC signals fail in execution (see Critical Discovery in `_index.md`). The winning portfolio strategy is `signals/low_vol.py` (min-volatility, CAGR=+9.32%, SR=0.85)
- `volume_reversal` has the highest daily-only IR (5.01) due to its low IC std — more consistent day-to-day
