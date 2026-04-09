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

## Priority Order for Implementation

1. LOB imbalance (simplest, strong prior evidence)
2. Market-cap normalised OFI (#10) — trivial upgrade over #1, backed by strong theory
3. Short-term reversal (classic, well-documented)
4. Alpha191 f046 + f071 composite (#11) — multi-period reversal, cross-market validated
5. PCA residual OU signal (moderate complexity, high ceiling)
6. OU quasi-Sharpe OFI signal (#12) — highest information content, moderate complexity
7. Regime-conditional LOB signal (adds the regime insight from DRL paper)
8. Depth slope / shape signals (novel, exploratory)
