# Interpretable Factor Decomposition for Decision Intelligence in Large-Scale Financial Markets: Evidence from China's A-Share Market

**Authors:** Xiao Han, Yao Xiao, Zhen Zhang, Moxuan Zheng (Emory University, Georgia Institute of Technology, University of Pennsylvania, New York University)
**Venue/Source:** arXiv
**arXiv/DOI:** arXiv:2606.12843
**Date:** June 11, 2026

---

## Core Claim
An XGBoost model with TreeSHAP attribution applied to 3,632 Chinese A-share stocks (2009–2019) achieves a mean AUC of 0.547 and +2.38%/month long-short spread (Sharpe 2.23) over 55 months OOS; SHAP decomposition reveals that **behavioral signals — turnover and short-term momentum — account for 58.2% of predictive attribution**, dominating valuation ratios (10.7%) and other factor categories.

---

## Method
XGBoost classifier trained on ~100 factors (price-based, volume-based, turnover, fundamental where available) using 60-month rolling in-sample windows. TreeSHAP computes per-factor, per-stock, per-period marginal attribution, averaged across 55 OOS evaluation months. Test assets: all A-share stocks on Shanghai and Shenzhen exchanges 2009–2019. Carhart four-factor model used for risk-adjustment of L/S alpha.

---

## Results
| Metric | Value |
|--------|-------|
| Mean OOS AUC | 0.547 |
| L/S monthly return | +2.38% |
| L/S Sharpe (annualised) | 2.23 |
| Carhart-adjusted L/S alpha | +2.31%/month (NW t = 7.48) |
| SHAP: behavioral (turnover + momentum) | 58.2% of total attribution |
| SHAP: valuation ratios | 10.7% |
| SHAP: all other categories | 31.1% |

Alpha is persistent across all 55 OOS months, not concentrated in a few episodes.

---

## Implementable Idea
**Low-Turnover secondary filter within the trend-filtered low-vol universe.** SHAP attribution shows turnover is the single dominant class of predictor in Chinese A-shares. The causal mechanism is well-established: high daily turnover in Chinese A-shares reflects retail FOMO or crowding (T+1 amplification), which predicts next-day overreaction reversal — the opposite of what we want for low-vol selection. Stocks with elevated turnover have temporarily suppressed 60d vol but carry hidden reversal risk from retail crowding.

```python
daily['amount_per_share'] = daily['amount'] / (daily['volume'] + 1e-8)
daily['turnover_20d'] = daily.groupby('asset_id')['amount'].transform(
    lambda x: x.rolling(20).mean()
)

def apply_low_turnover_filter(eligible_df, quantile=0.75):
    """
    Remove top-quartile turnover stocks from the eligible pool.
    In Chinese A-shares: high recent turnover = retail crowding = reversal risk.
    Only applied within already-filtered low-vol/trend universe.
    """
    threshold = eligible_df['turnover_20d'].quantile(quantile)
    filtered = eligible_df[eligible_df['turnover_20d'] <= threshold]
    if len(filtered) < 25:   # safeguard: need ≥25 candidates for N=20
        return eligible_df
    return filtered

# In trend_vol_v4 selection loop, after trend filter, before vol ranking:
# eligible = apply_low_turnover_filter(eligible)
```

This is differentiated from the failed `stable_turnover_momentum` signal (Zhang et al. 2025) because: (1) it does not select by past momentum direction, only screens by turnover level; (2) the low-vol base ranking does the actual picking — turnover filter is purely a negative screen on retail-crowded stocks.

**Addresses priority:** Priority 3 — Stock selection within the low-vol universe. Specifically, the "quality factor" that IS available from price/volume data: turnover stability as a proxy for retail vs. institutional ownership.

---

## Relevance to Feishu Competition
The SHAP attribution confirms what the Chinese A-share microstructure literature predicts: turnover is the dominant behavioral signal, not valuation. For our `trend_vol_v4` (N=20, threshold=−0.025, ERC weights), a low-turnover secondary filter could exclude retail-crowded stocks that happen to sit in the low-vol eligible pool — a regime seen especially during bull market runs when retail rotates through "safe" sectors. Expected effect: slight reduction in portfolio concentration in retail-heavy days; potential MDD reduction if excluded stocks are the ones that subsequently get caught in sell-offs. Signal #33.

---

## Concepts
-> [[chinese-ashore-market]] | [[factor-models]] | [[statistical-arbitrage]]
