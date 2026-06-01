# Dissecting the Lottery-Like Anomaly: Evidence from China

**Authors:** Ming Gu, Yi Hu, Zhitao Xiong  
**Venue/Source:** Accounting & Finance, Vol. 65, No. 1, pp. 883–911  
**arXiv/DOI:** DOI: 10.1111/acfi.13354 | SSRN: 4433510  
**Date:** 2025 (Accounting & Finance Vol. 65)

---

## Core Claim
The lottery-like anomaly in Chinese A-share stocks — high-MAX stocks subsequently underperform — is **entirely driven by the overnight return component**, not intraday trading. Retail investors chase lottery stocks, pushing prices up overnight through T+1-constrained demand accumulation; intraday price discovery partially corrects this, but the net overnight drag is the dominant mechanism.

---

## Method
Decompose total Chinese A-share returns (2007–2020) into overnight and intraday components. Sort stocks by MAX (maximum daily return over trailing month) and form quintile portfolios. Measure the alpha of the resulting long-short portfolio separately for overnight and intraday legs.

Key moderating variables:
- **Gambling preference**: proxied by turnover concentration and investor attention measures; higher gambling preference → stronger overnight lottery drag
- **Limits to arbitrage**: short-sale difficulty amplifies the anomaly (consistent with demand-pressure over-pricing)

Robustness: controls for size, B/M, momentum, IVOL; Fama-MacBeth cross-sectional regressions.

---

## Results
- High-MAX quintile stocks earn strongly negative **overnight** returns: the lottery premium is earned by holding to close and selling at the next open, not within the trading day.
- Intraday alpha is small and partially reverses the overnight effect.
- Anomaly is most pronounced in small-cap, high-retail-attention, high-turnover-concentration stocks.
- The overnight component alone accounts for >90% of the MAX long-short spread.
- Published in peer-reviewed journal (Accounting & Finance) — not just a preprint.

---

## Implementable Idea
The existing MAX filter in Signal #24 (`max_ret_20d > 75th percentile → exclude`) already targets lottery-stock risk. This paper provides two enhancements:

1. **Use overnight return as the MAX signal instead of total daily return**: `max_overnight_ret_20d = max(open_t / close_{t-1} - 1)` over trailing 20 days. Since our daily data includes `open` and `close` fields, this is directly computable:

```python
daily['adj_open'] = daily['open'] * daily['adj_factor']
daily['adj_close'] = daily['close'] * daily['adj_factor']

# Overnight return: close_{t-1} → open_t
daily_sorted = daily.sort_values(['asset_id', 'trade_day_id'])
daily_sorted['prev_close'] = daily_sorted.groupby('asset_id')['adj_close'].shift(1)
daily_sorted['overnight_ret'] = daily_sorted['adj_open'] / daily_sorted['prev_close'] - 1

# MAX overnight: highest overnight return in trailing 20 days
daily_sorted['max_overnight_20d'] = daily_sorted.groupby('asset_id')['overnight_ret'].transform(
    lambda x: x.rolling(20).max()
)

# Exclude stocks in top quartile by max overnight return (lottery candidates)
def apply_overnight_max_filter(eligible_df, quantile=0.75):
    threshold = eligible_df['max_overnight_20d'].quantile(quantile)
    filtered = eligible_df[eligible_df['max_overnight_20d'] <= threshold]
    return filtered if len(filtered) >= 25 else eligible_df
```

2. **Execution alignment**: Our buy execution at `vwap_0930_0935` happens right after the overnight gap. Lottery stocks that spiked overnight are bought at their premium price; the paper confirms these stocks then suffer partial intraday reversal. The overnight MAX filter directly targets this: exclude stocks with a recent history of large overnight pops before we buy them.

**Addresses priority:** Priority 3 — stock selection within the low-vol universe. Provides Chinese market evidence (peer-reviewed) on the mechanism driving MAX anomaly, upgrading Signal #24 with a more targeted overnight-return variant. The overnight decomposition is new relative to Li & Li (2025, already indexed) which uses total-return MAX.

---

## Relevance to Feishu Competition
Li & Li (2025, indexed) established that MAX and IV are orthogonal in China. This paper explains WHY: the lottery premium is an overnight phenomenon, concentrated in retail demand and limits-to-arbitrage. For our strategy, this means:

1. The overnight MAX filter is directly aligned with our execution model — we buy at vwap_0930_0935 (morning auction, after the overnight gap). High-overnight-MAX stocks arrive at our buy price already inflated.
2. Using overnight rather than total daily MAX as the filter is more precise: the total-return MAX conflates intraday and overnight effects.

**OOS-only**: IS parameter space is exhausted. If we deploy the MAX filter for OOS submission, use the overnight variant from this paper rather than total-return MAX. Modify the `apply_max_filter` call in Signal #24 to use `max_overnight_20d`.

---

## Concepts
-> [[chinese-ashore-market]] | [[mean-reversion]]
