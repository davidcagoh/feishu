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

---

## Tier 1 Additions (from new papers, April 2026 — session 4)

### 19. Wasserstein HMM Soft Regime Overlay for vol_managed
**Source:** [[explainable-regime-aware-investing-2026]]  
**Idea:** Replace the current binary `variance > 3× median → skip rebalance` filter with a continuous regime-stress probability from a 2-state Wasserstein Hidden Markov Model. Scale rebalancing weight by `(1 − stress_prob)` instead of an on/off switch.

```python
from hmmlearn.hmm import GaussianHMM
import numpy as np

def compute_stress_prob(market_features, window=120, n_regimes=2):
    """
    market_features: np.array of shape (T, D) — e.g. [cross-sectional vol, market return]
    Returns the stress-regime probability for the latest observation.
    """
    if len(market_features) < window:
        return 0.5  # neutral if insufficient history
    hmm = GaussianHMM(n_components=n_regimes, covariance_type='full', n_iter=100)
    hmm.fit(market_features[-window:])
    posteriors = hmm.predict_proba(market_features[-window:])
    # Identify stress regime as highest-mean-vol component
    stress_idx = int(np.argmax([hmm.means_[i].mean() for i in range(n_regimes)]))
    return float(posteriors[-1, stress_idx])

# In vol_managed.py, replace:
#   if market_var > threshold: continue  (skip rebalance)
# With:
#   stress_p = compute_stress_prob(market_features[:t])
#   scale = max(0, 1 - stress_p)          # 0 = full stress → skip, 1 = calm → full weight
#   buy_pct *= scale
```

**Expected improvement over current vol_managed:** softer response on partial-stress days; self-calibrating stress detection; avoids cliff-edge around the fixed 3× threshold. Matches Boukardagha (2026) Sharpe improvement of 2.18 vs 1.59.  
**Status:** `[ ] untested`

---

### 20. Cluster-Constrained Low-Vol Selection
**Source:** [[clustering-augmented-reversal-china-2025]]  
**Idea:** After computing per-asset volatility, cluster stocks by volatility + return + turnover using K-means. Select the lowest-vol stocks while ensuring each cluster is represented. This fixes the sector concentration problem (currently: 12 core holdings, 7 effective bets, mean pairwise r=0.33–0.43).

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

def cluster_constrained_selection(daily, trade_day, N=20, n_clusters=10, lookback=60):
    """
    Select N stocks minimising volatility subject to cluster coverage constraint.
    """
    recent = daily[daily['trade_day_id'] <= trade_day].groupby('asset_id').tail(lookback)
    features = recent.groupby('asset_id').agg(
        vol=('ret', 'std'),
        mean_ret=('ret', 'mean'),
        log_turnover=('amount', lambda x: np.log(x.mean() + 1))
    ).dropna()

    if len(features) < n_clusters:
        return features.nsmallest(N, 'vol').index.tolist()

    scaler = StandardScaler()
    X = scaler.fit_transform(features[['vol', 'mean_ret', 'log_turnover']])
    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    features['cluster'] = km.fit_predict(X)

    # One lowest-vol stock per cluster (floor), remainder filled globally
    floor = max(1, N // n_clusters)
    selected = []
    for c in range(n_clusters):
        group = features[features['cluster'] == c].nsmallest(floor, 'vol')
        selected.extend(group.index.tolist())
    remaining = features[~features.index.isin(selected)].nsmallest(N - len(selected), 'vol')
    selected.extend(remaining.index.tolist())
    return list(dict.fromkeys(selected))[:N]
```

**Expected improvement:** higher effective number of independent bets (from ~7 toward N); lower pairwise correlation; potential MDD reduction. Score formula weighs MDD at 25% — a 1–2% MDD improvement is worth ~0.0025–0.005 Score points.  
**Status:** `[ ] untested`

---

---

## OOS Contingency Ideas (from April 2026 papers — session 5)

> IS parameter space is exhausted. These ideas cannot improve the IS Score and should NOT be tested on IS data. They are contingency plans to deploy when OOS data arrives May 28 if the OOS regime appears to be a bull market.

### 21. Dynamic N Expansion in Bull Regime
**Source:** [[factoring-low-volatility-factor-2025]]  
**Idea:** When market volatility is well below its long-run median (bull regime proxy), expand N from 20 to 30–35 to restore beta exposure and reduce low-vol underperformance drag.

```python
# In trend_vol_v4.py — compute before stock selection:
market_vol_22d = market_ret.rolling(22).std() * np.sqrt(252)
long_run_median_vol = market_vol_22d.rolling(120).median()

bull_regime = market_vol_22d.iloc[-1] < 0.75 * long_run_median_vol.iloc[-1]
N = 35 if bull_regime else 20
```

**When to use:** If OOS market vol is persistently below IS median → set N=35.  
**Risk:** In bear episodes within OOS, N=35 may widen MDD. Monitor first 30 OOS days.  
**Status:** `[ ] untested`

---

### 22. Sparse Jump Model Regime Overlay
**Source:** [[dynamic-factor-allocation-regime-sjm-2025]]  
**Idea:** Detect low-vol factor regime from cross-sectional market return history. In bull regime (market vol < long-run median), relax trend threshold and expand N. In bear, maintain trend_vol_v4 defaults.

```python
def detect_regime(market_ret, window=60):
    """Returns 'bull' or 'bear' using cross-sectional vol as SJM proxy."""
    vol_22d = market_ret.rolling(22).std().iloc[-1] * np.sqrt(252)
    vol_median = market_ret.rolling(22).std().rolling(120).median().iloc[-1] * np.sqrt(252)
    return 'bull' if vol_22d < vol_median else 'bear'

regime = detect_regime(market_ret)
params = {'N': 30, 'threshold': 0.0} if regime == 'bull' else {'N': 20, 'threshold': -0.025}
```

**Expected improvement:** IR of low-vol factor timing 0.05→0.4 from Shu & Mulvey (JPM 2025).  
**Implementation note:** Full SJM requires `jumpmodels` pip package; proxy above is sufficient for our daily rebalancing frequency.  
**Status:** `[ ] untested`

---

### 23. Adaptive Volatility Window (FIGARCH-Inspired)
**Source:** [[adaptive-minimum-variance-arfima-figarch-2025]]  
**Idea:** Replace fixed 60d rolling vol window with a regime-adaptive window: 20d in high-vol regimes (faster adaptation), 90d in calm regimes (more stable rankings).

```python
def adaptive_window(market_ret, base=60, short=20, long=90):
    vol_22d = market_ret.rolling(22).std().iloc[-1]
    vol_median = market_ret.rolling(22).std().rolling(120).median().iloc[-1]
    ratio = vol_22d / (vol_median + 1e-8)
    if ratio > 1.5:
        return short   # high-vol: shorten for faster response
    elif ratio < 0.75:
        return long    # low-vol/bull: lengthen for stability
    return base        # normal: use base
```

**Expected improvement:** Faster exclusion of deteriorating stocks at onset of bear episodes; more stable rankings in bull markets. Targets MDD reduction (Priority 2).  
**Risk:** More complex; adaptive window adds parameter sensitivity. Low risk: only 2 thresholds (1.5× and 0.75×) tied to long-run median, not IS-fitted.  
**Status:** `[ ] untested`

---

## Priority Order for Implementation

> Updated 2026-04-20. IC-era signals (1–12) are all complete and ruled out — IC does not predict portfolio alpha due to execution gap. Portfolio backtest is the only valid evaluation metric. Current best: `trend_vol_v2` Score=0.3877.

**COMPLETE / RULED OUT (IC era — do not revisit):**
- ~~1–9: LOB imbalance, OFI, short-term reversal, Alpha191, composites, PCA residual, OU OFI~~ ✅ All fail in portfolio execution (CAGR ≈ −54%)

**FAILED IN PORTFOLIO BACKTEST (tested 2026-04-18):**
- ~~13. Longer lookback (120d/252d)~~ ❌ Score collapsed to 0.054–negative; IS period too short for long lookbacks
- ~~14. VMP inverse-variance weighting~~ ❌ `inv_var_vol` Score=0.3113 ≈ vol_managed baseline; low-vol universe too homogeneous
- ~~19. Wasserstein HMM soft regime overlay~~ ❌ `hmm_regime_vol` Score=0.2937; over-blanks, loses CAGR
- ~~20. Cluster-constrained low-vol~~ ❌ `cluster_low_vol` Score=0.1286; K-means forces picks from weak clusters, high churn

**FAILED IN PORTFOLIO BACKTEST (tested 2026-04-20 battery):**
- ~~low_beta~~ ❌ Score=−0.469; hidden momentum → reversal at execution
- ~~return_consistency~~ ❌ Score=−0.683; hit rate = recent uptrend = momentum → reversal
- ~~rolling_sharpe~~ ❌ Score=−0.877; same execution-gap mechanism
- ~~quality_composite~~ ❌ Score=0.061; contaminated by momentum-biased components

**OPEN — 2 meaningful experiments remaining:**

1. **N-sweep on trend_vol_v2** — N=20 confirmed for vol_managed_v2 but trend filter narrows universe; optimal N may differ. Try N=10, 15, 20, 25, 30.

2. **ERC weights on trend_vol_v2** — Combine `trend_vol_v2.compute()` selection with `1/σ` allocation weights from `erc_vol_managed.compute_weights()`. The trend-filtered universe is more homogeneous, which might respond differently to ERC than the unfiltered universe.

**RULED OUT (do not implement, wrong objective):**
- 15 (regime N scaling), 16 (MTP2-GGM whitened PCA), 17 (Kalman LOB), 18 (cluster-lag) — all IC/signal-quality improvements; IC does not predict portfolio alpha.

---

## Signal Evaluation Note

IC/IR metrics are meaningless for this competition. Portfolio backtest with exact competition mechanics (`eval/backtest.py`) is the only valid evaluation. Do not build signals optimised for IC. See "Critical Discovery" in `wiki/_index.md`.
