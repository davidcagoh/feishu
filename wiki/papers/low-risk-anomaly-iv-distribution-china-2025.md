# Low-risk anomaly: Idiosyncratic risk or return distribution

**Authors:** Li, Tianyang & Li, Yinzhu
**Venue/Source:** Finance Research Letters, Vol. 74 (2025)
**arXiv/DOI:** https://doi.org/10.1016/j.frl.2025.106xxx (pii S1544612325000200)
**Date:** 2025

---

## Core Claim
In Chinese A-shares, the low-risk anomaly is driven primarily by idiosyncratic volatility (IV), not by past returns. Crucially, the MAX effect (maximum single-day return over the past month) is orthogonal to IV in China — unlike the US, where MAX largely subsumes IV. This means both channels provide independent incremental information for portfolio selection in Chinese equities.

---

## Method
Long-short decile portfolio formation and Fama-MacBeth regressions on all common stocks listed on Shanghai and Shenzhen exchanges, January 2006 – December 2020. Low-risk variables divided into two categories:
1. **Volatility-based:** total volatility, idiosyncratic volatility (IV), systematic volatility
2. **Distribution-based:** MAX (maximum daily return in past month), SMAX (scaled MAX), co-skewness, idiosyncratic skewness, past returns

Double-sorts to test orthogonality between IV and distribution variables. Interaction regressions to identify sentiment- and volume-regime dependence.

---

## Results
- Hedged IV portfolios (long low-IV, short high-IV) significantly outperform past-return-sorted portfolios in both raw and risk-adjusted returns
- In China, MAX and IV are independent: controlling for IV does not eliminate MAX premium; controlling for MAX does not eliminate IV premium (contrast: in US, MAX largely absorbs IV)
- Distribution-variable pricing (MAX, skewness) concentrated in **low-investor-sentiment** periods
- Past-return pricing (short-term reversal) most active in **high-trading-volume** periods — consistent with our finding that reversal alpha is captured before our buy execution
- High-MAX stocks have substantially higher future IV (0.46% vs 0.29% for low-MAX), meaning they are only temporarily quiet after a spike before resuming elevated volatility

---

## Implementable Idea
Within the low-vol universe (already sorted on 60d realized vol ≈ total vol ≈ IV proxy), add a MAX filter as a secondary screen to remove "lottery-ticket" stocks that experienced a single large positive spike recently:

```python
# Compute MAX = maximum single-day return over the past 20 trading days per asset
daily['max_ret_20d'] = daily.groupby('asset_id')['ret'].transform(
    lambda x: x.rolling(20).max()
)

# In trend_vol_v4/v5 selection logic, after filtering by vol rank:
# Exclude top 25% by max_ret_20d within the eligible pool
def filter_max(eligible_df, quantile=0.75):
    threshold = eligible_df['max_ret_20d'].quantile(quantile)
    return eligible_df[eligible_df['max_ret_20d'] <= threshold]
```

**Why this helps:** Our current 60d-vol screen misses stocks that had a recent single-day spike (high MAX but temporarily suppressed vol post-spike). The paper shows these stocks revert to high IV promptly, creating MDD risk. Removing the top MAX quartile removes stocks with residual lottery risk not captured by rolling vol. The effect is orthogonal to IV sorting, so it adds true incremental screening.

**Caveat:** Should be tested only on OOS data (IS parameter space exhausted). The filter reduces the eligible pool before N=20 selection — in bear days with few eligible stocks, tighten the quantile threshold or disable the filter.

**Addresses priority:** Priority 3 — Stock selection within the low-vol universe (orthogonal secondary screen for Chinese A-shares, confirmed on SSE+SZSE 2006–2020).

---

## Relevance to Feishu Competition
Our trend_vol_v4 (Score=0.4024) selects the 20 lowest-vol stocks passing the trend filter. A subset of these will be "post-spike quiet" stocks — stocks where a recent large one-day move temporarily suppressed the 60d vol denominator while leaving a lottery-ticket risk profile. These are candidates for sudden reversal that contributes to MDD episodes (our binding constraint at 7.98%).

Adding a MAX filter to the selection logic is the natural next portfolio-construction experiment consistent with this paper. Unlike most ideas we've tested, it targets MDD rather than CAGR, and uses only daily price data already available.

**Status as OOS contingency:** If OOS MDD breaches 10% early in the OOS window, adding MAX filter may help — but this should not be pre-emptively implemented without OOS evidence.

---

## Concepts
-> [[chinese-ashore-market]] | [[factor-models]] | [[statistical-arbitrage]]
