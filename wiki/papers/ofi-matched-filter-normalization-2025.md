# Optimal Signal Extraction from Order Flow: A Matched Filter Perspective on Normalization and Market Microstructure

**Authors:** Sungwoo Kang  
**Venue/Source:** arXiv q-fin.TR  
**arXiv/DOI:** arXiv:2512.18648  
**Date:** December 2025

---

## Core Claim

Standard order flow imbalance (OFI) signals are degraded because the choice of normalization denominator introduces heteroskedastic noise. Framing normalization as a signal-processing matched filter problem shows that the *optimal* denominator depends on who is generating the informed signal: market-cap normalization for capacity-constrained institutional investors, trading-value normalization for volume-targeting (VWAP/TWAP) algorithms.

---

## Method

The paper applies matched filter theory to order flow normalization. The signal-generating process determines the correct normalization:

- **Institutional informed investors** scale positions by firm value (market capitalisation) → **market cap normalization (S^MC)** is the matched filter.
- **Noise traders / VWAP algorithms** scale by daily trading volume → **trading value normalization (S^TV)** is the matched filter.

Standard volume normalization `OFI / total_volume` is mismatched for institutional flows because it multiplies the signal by `1/turnover`, a highly volatile quantity, amplifying noise.

Monte Carlo simulations confirm the principle: matched filters achieve up to **1.99× higher signal-to-noise correlation** vs. mismatched normalizations.

Empirical validation uses **2.7 million stock-day observations from the Korean equity market (2020–2024)**, disaggregating flows by investor type (domestic institutional, foreign, retail).

---

## Results

| Flow type | Normalization | t-statistic for next-day return | 
|-----------|--------------|--------------------------------|
| Domestic institutional | Market cap (S^MC) | **9.65** |
| Foreign | Trading value (S^TV) | **16.35** |
| Retail | (noisy, no strong prediction) | — |

Both effects hold across long horizons with no sign reversal, indicating persistent private information rather than transient price impact.

---

## Relevance to Feishu Competition

The key actionable insight: the standard LOB imbalance signal `(bid_vol_1 - ask_vol_1) / (bid_vol_1 + ask_vol_1)` uses the wrong denominator. Normalizing by a market-cap proxy (total RMB amount outstanding, or daily `amount`) should significantly improve predictive IC vs. normalizing by raw volume.

In the Feishu data, `amount` (total RMB turnover) is the closest proxy to market cap * turnover rate. A better normalization:

```python
import pandas as pd

# Step 1: compute raw signed order flow per snapshot
lob['ofi_raw'] = lob['bid_volume_1'] - lob['ask_volume_1']

# Step 2: aggregate to daily total signed flow per asset
daily_ofi = (
    lob.groupby(['asset_id', 'trade_day_id'])['ofi_raw']
    .sum()
    .reset_index(name='daily_ofi_raw')
)

# Step 3: merge with daily data to get market-cap proxy (amount = RMB turnover)
daily_ofi = daily_ofi.merge(
    daily[['asset_id', 'trade_day_id', 'amount', 'close']],
    on=['asset_id', 'trade_day_id']
)

# Standard imbalance (mismatched): divide by total shares
# S^volume = daily_ofi_raw / total_traded_volume  ← noisy denominator

# Matched filter (S^MC): divide by market cap proxy
# amount ≈ price × volume = daily turnover; use close as price proxy
daily_ofi['ofi_mktcap'] = daily_ofi['daily_ofi_raw'] / daily_ofi['amount']

# Cross-sectional z-score → alpha signal
daily_ofi['ofi_signal'] = daily_ofi.groupby('trade_day_id')['ofi_mktcap'].transform(
    lambda x: (x - x.mean()) / (x.std() + 1e-8)
)
```

**Extension — multi-level matched OFI:** apply same principle across all 10 LOB levels, weighting each level by `1/k` (depth-decay) and normalizing the aggregated flow by `amount`:

```python
# Aggregate multi-level signed flow
ofi_cols = []
for k in range(1, 11):
    w = 1.0 / k  # depth decay
    lob[f'ofi_L{k}'] = w * (lob[f'bid_volume_{k}'] - lob[f'ask_volume_{k}'])
    ofi_cols.append(f'ofi_L{k}')

lob['ofi_multi'] = lob[ofi_cols].sum(axis=1)

# Then aggregate and normalize by amount as above
```

This extends existing Signal #1 (LOB Imbalance) in the ideas file with a theoretically-grounded normalization that should boost IC.

---

## Concepts
→ [[limit-order-book]] | [[statistical-arbitrage]] | [[chinese-ashore-market]]
