# Volatility-Managed Portfolios in the Chinese Equity Market

**Authors:** Chuyu Wang, Junye Li  
**Year:** 2024  
**Venue/Source:** Pacific-Basin Finance Journal, Volume 88, December 2024  
**Link:** https://www.sciencedirect.com/science/article/abs/pii/S0927538X24003263 (SSRN preprint: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4623041)

## Summary

This paper applies the Moreira & Muir (2017) volatility-managed portfolio (VMP) framework to the Chinese A-share market, finding that scaling factor exposures inversely by recent realised variance consistently improves risk-adjusted performance. Outperformance concentrates in stocks with high arbitrage frictions (price-limit-constrained stocks, high sentiment periods) and the managed portfolios have substantially lower conditional systematic risk during market downturns, functioning as a structural hedge in bear regimes.

## Key Results

- Volatility-managed factor portfolios consistently outperform unmanaged counterparts in both in-sample and out-of-sample tests on Chinese A-shares (2000–2022)
- Multi-factor VMP achieves annualised OOS Sharpe ratio of ~1.50 vs ~0.99 for unmanaged multi-factor (≈52% improvement)
- Outperformance is significantly stronger in bear markets and periods of elevated investor sentiment
- China's ±10% price-limit mechanism amplifies VMP gains — stocks near the limit that revert contribute disproportionately
- Data from Shanghai and Shenzhen main boards, GEM, and STAR boards all show consistent results

## Relevance to Feishu Competition

This paper directly addresses our core problem: `low_vol.py` (CAGR=+9.32%, SR=0.85) underperforms in bull markets because it avoids high-beta growth stocks. The VMP mechanism provides a price-data-only switch to scale down exposure during high-volatility bear periods (where low-vol already shines) and scale up or switch to momentum/growth tilt in low-volatility bull periods. The mechanism requires only historical daily returns — all available in our dataset.

The bull-market hedge is the critical insight: the paper shows that realised variance (short lookback, e.g., 22 days) is the natural conditioning variable. When market-level realised variance is low, the VMP upscales — for our low-vol strategy this means being more aggressive in selecting from the lower-vol tail. When variance is high, the VMP downscales, which in our case is already what low-vol does naturally. The practical implication: augment the stock-selection signal by weighting holdings by `1/σ²_i` (per-stock variance inverse) rather than equal-weighting within the 100-stock portfolio.

## Implementable Signal

This is a **portfolio weighting overlay**, not a new stock-selection signal:

```python
import pandas as pd
import numpy as np

# daily: DataFrame with asset_id, trade_day_id, adj_close (= close * adj_factor)
daily['adj_close'] = daily['close'] * daily['adj_factor']
daily['ret'] = daily.groupby('asset_id')['adj_close'].pct_change()

# Step 1: per-asset realised variance over last 22 days
daily['var_22d'] = daily.groupby('asset_id')['ret'].transform(
    lambda x: x.rolling(22).var()
)

# Step 2: after low_vol selects the 100-stock portfolio for day t,
# weight each stock inversely proportional to its realised variance
# (replace equal-weight = 1/N with VMP weight)
def vmp_weights(selected_vars):
    """
    selected_vars: pd.Series of realised variances for the 100 selected stocks
    Returns: pd.Series of portfolio weights summing to 1
    """
    inv_var = 1.0 / (selected_vars + 1e-8)
    return inv_var / inv_var.sum()

# For each trade day, after computing low_vol selection:
# weights = vmp_weights(daily.loc[selected_mask, 'var_22d'])

# Step 3: regime-level scaling (market-wide VMP scale factor)
# c = target_vol² / realised_market_var_1m
# If c > 2, cap at 2; if c < 0.5, floor at 0.5
target_vol = 0.15  # 15% annualised target
market_var = daily.groupby('trade_day_id')['ret'].var()  # cross-sectional var proxy
market_var_22d = market_var.rolling(22).mean() * 252  # annualised
scale_factor = (target_vol**2 / (market_var_22d + 1e-8)).clip(0.5, 2.0)
# scale_factor > 1 → bull/calm market → hold more; scale_factor < 1 → vol spike → de-risk
```

Expected output: per-day portfolio weights for the 100 selected stocks. In calm markets (low realised vol) the scale factor exceeds 1 — use as a tilt signal toward higher N (e.g., 120 stocks). In turbulent markets the scale factor falls below 1 — tighten to 80 stocks or concentrate in the lowest-vol decile.

## Caveats

- Paper uses factor long-short portfolios; our competition is long-only with T+1 constraints — the scaling intuition transfers but not the shorting leg
- Sample 2000–2022 includes many distinct Chinese market regimes (2007 boom, 2015 crash, COVID); our dataset D001–D484 is a single bear-dominated period, so bull-market uplift cannot be verified in-sample
- Price-limit mechanism effect cannot be fully replicated without knowing which stocks hit limits on a given day (we have OHLC but not trading halt flags)
- The OOS Sharpe improvement (1.50 vs 0.99) is for multi-factor portfolios; single-factor (low-vol only) improvement may be smaller

## Related Concepts

[[mean-reversion]], [[chinese-ashore-market]], [[factor-models]], [[limit-order-book]]
