# MAX on Steroids: A New Measure of Investor Attraction to Lottery Stocks

**Authors:** Turan G. Bali (Georgetown University), Baris Ince (Ozyegin University), Han N. Ozsoylev (Ozyegin University)
**Venue/Source:** SSRN Working Paper
**arXiv/DOI:** SSRN 6065166
**Date:** January 12, 2026

---

## Core Claim
Standard MAX (average of the five highest daily returns in the past month) conflates idiosyncratic lottery-seeking with systematic risk. Purging the systematic (market-beta) component yields **MAXβ** — an idiosyncratic measure of extreme-return attraction that yields stronger and more robust abnormal return predictions than total MAX. In retail-dominated stocks, high MAXβ predicts underperformance; in institution-dominated stocks, low MAXβ predicts outperformance.

---

## Method
**Construction of MAXβ:**
1. Estimate each stock's market beta using a rolling 60-month window.
2. Compute daily idiosyncratic return: `ε_{i,t} = r_{i,t} − β_i × r_{m,t}`.
3. Average the top-5 idiosyncratic daily returns within each month: `MAXβ_i = mean(top-5 ε_{i,t})`.

**Evaluation:**
- Cross-sectional sorts and double-sorts against standard risk and mispricing factors.
- Sample: CRSP US equities; also tested in international markets (including China).
- Long-short portfolio sorted on MAXβ (value-weighted quintiles).

---

## Results
| Metric | Standard MAX | MAXβ |
|--------|-------------|------|
| Monthly L/S alpha (CAPM) | Significant | Stronger |
| Robust to Carhart 4-factor | Partially | Yes |
| Robust to mispricing factors | No | Yes |
| Depends on past return persistence | Yes | No |
| Retail-dominated stocks (driver) | High MAX underperforms | High MAXβ underperforms |
| Institution-dominated stocks (driver) | Weak | Low MAXβ outperforms |

The MAXβ anomaly is independent of past return persistence (unlike standard MAX which partially reflects momentum), making it more suitable as a secondary filter alongside momentum-agnostic low-vol selection.

---

## Implementable Idea
**Upgrade Signal #24 (MAX Filter) from total MAX to MAXβ (idiosyncratic MAX).** In Chinese A-shares where retail investors dominate and institutional ownership is low, the mechanism is almost entirely the retail-dominated channel (high MAXβ stocks underperform). Since we already buy at `vwap_0930_0935` — after the overnight gap — idiosyncratic spikes (not market-wide days) are what inflate our execution cost. MAXβ isolates exactly this dimension.

```python
# Compute daily market return (equal-weight cross-sectional mean)
market_ret = daily.groupby('trade_day_id')['ret'].transform('mean')
daily['idio_ret'] = daily['ret'] - market_ret  # simple beta=1 proxy

# Alternatively, use rolling beta per asset (more precise but slower):
def rolling_beta(asset_ret, mkt_ret, window=60):
    cov = asset_ret.rolling(window).cov(mkt_ret)
    var = mkt_ret.rolling(window).var()
    return cov / (var + 1e-8)

# daily['beta'] = ... (per asset, rolling 60d)
# daily['idio_ret'] = daily['ret'] - daily['beta'] * market_ret

# MAXβ: average top-5 idiosyncratic daily returns in trailing 20 days
# (using 20d instead of monthly to align with our execution horizon)
daily_sorted = daily.sort_values(['asset_id', 'trade_day_id'])

def top5_mean(x):
    x = x.dropna()
    if len(x) < 5:
        return np.nan
    return x.nlargest(5).mean()

daily_sorted['max_beta_20d'] = daily_sorted.groupby('asset_id')['idio_ret'].transform(
    lambda x: x.rolling(20).apply(top5_mean, raw=False)
)

# In trend_vol_v4 selection, after trend filter:
def apply_max_beta_filter(eligible_df, quantile=0.75):
    """
    Exclude top quartile by MAXβ — idiosyncratic lottery-seeking proxy.
    Better than total MAX: isolates retail demand not explained by market moves.
    """
    threshold = eligible_df['max_beta_20d'].quantile(quantile)
    filtered = eligible_df[eligible_df['max_beta_20d'] <= threshold]
    if len(filtered) < 25:
        return eligible_df
    return filtered
```

**Why this improves on Signal #24 (overnight MAX):** Overnight-return MAX (from Gu et al. 2025) targets the mechanism at T+1 / overnight gap. MAXβ targets idiosyncratic demand more broadly — it also captures intraday lottery-buying on individual stock news days, independent of the overnight gap. The two filters are complementary and could be combined (`max_overnight_20d ≤ threshold_A AND max_beta_20d ≤ threshold_B`).

**Addresses priority:** Priority 3 — Stock selection within low-vol universe. Specifically, the MAX filter upgrade path identified in learnings.md. This is an orthogonal improvement to Signal #24.

---

## Relevance to Feishu Competition
Chinese A-shares are nearly entirely retail-dominated by ownership structure, which is exactly the regime where MAXβ > MAX as a filter. Using MAXβ in place of total MAX removes the false positives (market-wide rally days that inflate total MAX but don't represent idiosyncratic lottery demand) and better targets the retail crowding mechanism. The β=1 proxy (equal-weight market return) is immediately computable from our dataset without a beta estimation step. A rolling-beta variant would be more precise but requires 60d warmup per asset. Signal #24 upgrade path; can test both simultaneously as Signal #33b.

---

## Concepts
-> [[chinese-ashore-market]] | [[mean-reversion]] | [[kelly-betting]]
