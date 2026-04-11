# The Volatility Effect in China

**Authors:** David Blitz, Matthias X. Hanauer, Pim van Vliet  
**Year:** 2021  
**Venue/Source:** Journal of Asset Management, Volume 22, pages 338–349 (2021)  
**Link:** https://link.springer.com/article/10.1057/s41260-021-00218-0 (SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3765625)

## Summary

Blitz, Hanauer, and van Vliet document a strong, pervasive low-volatility anomaly in Chinese A-shares using the MSCI China A Onshore universe. Low-risk stocks (sorted on 3-year realised volatility) significantly outperform high-risk stocks, and the effect is not explained by the Fama-French-Carhart factor set. The VOL factor exhibits excellent practical investability — low turnover and concentrated in the largest, most liquid stocks — making it the foundational empirical reference for any minimum-volatility strategy in this market.

## Key Results

- Lowest-volatility decile: annualised Sharpe of 0.51; highest-volatility decile: Sharpe of 0.00
- Risk-adjusted alpha for D1–D10 spread: 16.1% annualised (statistically significant, robust to sector and time-period subsamples)
- Fama-French style VOL factor has stronger stand-alone performance than MKT, SMB, HML, or MOM individually
- Effect holds for both equal-weighted and value-weighted sorts, and is robust within both large-cap and small-cap sub-universes
- Low turnover: the signal is stable enough that rebalancing costs do not destroy the anomaly
- The anomaly is strongest in the large/liquid stock subset — exactly the investable universe relevant to a competition portfolio

## Relevance to Feishu Competition

This is the academic foundation for `signals/low_vol.py`, which already outperforms all IC-based signals (CAGR=+9.32%, SR=0.85 on D001–D484). The paper confirms the mechanism is structural in the Chinese market specifically: retail-dominated trading drives overpricing of high-volatility "lottery" stocks, while low-volatility defensive names are neglected. This behavioural mechanism is persistent and does not depend on any fundamental data.

Key practical implication: the paper uses a **3-year volatility window** for ranking — significantly longer than our current 60-day window. Our `low_vol.py` may be over-responsive to short-term volatility spikes. Testing a 120-day or 252-day window may improve stability, particularly if the dataset spans multiple volatility regimes.

## Implementable Signal

The core recipe is already implemented in `signals/low_vol.py`. This paper suggests **testing longer lookback windows**:

```python
daily['adj_close'] = daily['close'] * daily['adj_factor']
daily['ret'] = daily.groupby('asset_id')['adj_close'].pct_change()

for window in [60, 120, 252]:
    col = f'vol_{window}d'
    daily[col] = daily.groupby('asset_id')['ret'].transform(
        lambda x: x.rolling(window).std()
    )
    # Rank: lower vol → higher rank (rank ascending=True means smallest vol gets rank 1)
    daily[f'rank_{window}d'] = daily.groupby('trade_day_id')[col].rank(ascending=True)
    # Select bottom N stocks by vol rank
```

Paper uses 3-year (≈756 trading days) window; our dataset has 484 days total, so the maximum feasible window is ~252 days (1 year). Testing 120-day vs 60-day is the priority.

No direct signal — use as conceptual framework confirming current strategy direction and motivating longer-window variants.

## Caveats

- Paper uses MSCI China A Onshore universe (top-cap stocks only); our dataset includes 2270 assets covering small/mid caps — the liquidity filter in `low_vol.py` partially addresses this but may need tightening
- 3-year lookback used in the paper is not achievable with 484 days of data; the effect's stability at shorter lookbacks is not verified in this paper specifically
- Sample period predates 2021 publication (roughly 2004–2020); our dataset may cover a different sub-regime
- Bull market underperformance is acknowledged ("low-volatility securities tend to lag during bull markets") but not quantified by regime in this paper — see [[vol-managed-portfolios-china-2024]] for the regime-conditioning complement

## Related Concepts

[[chinese-ashore-market]], [[factor-models]], [[mean-reversion]]
