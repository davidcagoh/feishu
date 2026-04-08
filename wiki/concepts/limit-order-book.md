# Limit Order Book (LOB)

The LOB is the centralised record of all outstanding buy and sell limit orders for an asset. It determines how trades are matched and is the primary data source for microstructure signals.

---

## Structure

```
Ask side (sellers, ascending price):
  Level 1: ask_price_1  ask_volume_1   ← best ask (lowest seller)
  Level 2: ask_price_2  ask_volume_2
  ...
  Level 10: ask_price_10 ask_volume_10

Bid side (buyers, descending price):
  Level 1: bid_price_1  bid_volume_1   ← best bid (highest buyer)
  Level 2: bid_price_2  bid_volume_2
  ...
  Level 10: bid_price_10 bid_volume_10
```

**Feishu column mapping:** `ask_price_1` … `ask_price_10`, `bid_price_1` … `bid_price_10`, `ask_volume_1` … `ask_volume_10`, `bid_volume_1` … `bid_volume_10` (all float32)

---

## Core Derived Quantities

| Quantity | Formula | Interpretation |
|----------|---------|----------------|
| Mid-price | `(ask_price_1 + bid_price_1) / 2` | Fair value estimate |
| Bid-ask spread | `ask_price_1 - bid_price_1` | Round-trip transaction cost |
| Level-1 imbalance | `(bid_vol_1 - ask_vol_1) / (bid_vol_1 + ask_vol_1)` | Buying vs selling pressure |
| Weighted mid-price | `(ask_vol_1 × bid_p_1 + bid_vol_1 × ask_p_1) / (ask_vol_1 + bid_vol_1)` | Volume-weighted fair value |
| Depth imbalance (all levels) | `(Σ bid_vol_k - Σ ask_vol_k) / (Σ bid_vol_k + Σ ask_vol_k)` | Multi-level order pressure |
| Order book slope | `ask_vol / (ask_price - mid)` | Liquidity provision curvature |

---

## LOB Imbalance as a Price Predictor

**Theory:** When bid volume > ask volume (positive imbalance), buyers are more aggressive. This predicts upward short-term price pressure, as market sell orders will be absorbed by deep bids and market buy orders will move the price up.

**Empirical strength:** LOB imbalance is one of the most robust microstructure predictors of short-term returns. Typically predictive over the next 1–30 minutes.

**Mean reversion of imbalance:** Imbalance itself is mean-reverting. Large positive imbalance at time t tends to revert as market orders are executed and new limit orders restore balance.

---

## Multi-Level Signals

Using depth beyond level 1 captures **hidden liquidity**:

```python
# Weighted imbalance across all 10 levels
weights = 1 / np.arange(1, 11)  # weight level k by 1/k
bid_weighted = sum(weights[k] * bid_volume_{k+1} for k in range(10))
ask_weighted = sum(weights[k] * ask_volume_{k+1} for k in range(10))
imbalance = (bid_weighted - ask_weighted) / (bid_weighted + ask_weighted)
```

Or exponential decay weights `e^{-α(price_k - mid)}` proportional to price distance from mid.

---

## LOB Dynamics

| Event | Effect on LOB |
|-------|--------------|
| Limit buy order | Adds to bid side |
| Limit sell order | Adds to ask side |
| Market buy order | Consumes ask_volume at levels until filled; price rises |
| Market sell order | Consumes bid_volume at levels until filled; price falls |
| Order cancellation | Removes from LOB |

**Order flow toxicity:** High ratio of market orders to limit orders → informed trading → larger price impact per trade.

---

## Feishu LOB Data Specifics

- **Snapshots**: ~23–24 per day per asset, from 09:40 to 15:00 (post-opening auction)
- **Timing**: The opening auction (09:25–09:30) is NOT in the LOB data. First snapshot is at 09:40.
- **Relationship to daily data**: `vwap_0930_0935` captures the opening 5-min period before LOB snapshots start.
- **Scale**: 24.8M rows total (full dataset). Filter by `trade_day_id` before loading.

**Snapshot-level signal construction:**
```python
lob_day = pd.read_parquet(
    "data/lob_data_in_sample.parquet",
    filters=[("trade_day_id", "==", "D001")]
)
lob_day['imbalance'] = (
    (lob_day['bid_volume_1'] - lob_day['ask_volume_1']) /
    (lob_day['bid_volume_1'] + lob_day['ask_volume_1'])
)
lob_day['mid'] = (lob_day['ask_price_1'] + lob_day['bid_price_1']) / 2
```

**Daily signal aggregation:**
```python
# Mean imbalance over the day → predicts next day open?
daily_imbalance = lob_day.groupby('asset_id')['imbalance'].mean()
# End-of-day imbalance → predicts overnight gap?
eod_imbalance = lob_day.groupby('asset_id').last()['imbalance']
```

---

## Papers in This Wiki
- [[jump-start-control-scientist]] — LOB structure and microstructure foundations (Section VII)
- [[drl-optimal-trading-partial-info]] — LOB-based pair trading as empirical application
- [[statistical-arbitrage]] — LOB signals as inputs to stat-arb strategies
