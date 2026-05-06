# Large-Scale Asset Selection via Metric Dependence with Enriched High Frequency Information

**Authors:** Yangzhou Chen, Shuaida He, Xin Chen
**Venue/Source:** arXiv q-fin.PM
**arXiv/DOI:** arXiv:2605.02326
**Date:** May 4, 2026

---

## Core Claim
Current asset selection rules rely on scalar returns or low-dimensional summaries and discard intraday risk dynamics. The authors propose Metric Dependence Screening (MDS), which treats each asset-day as a point-curve object (daily return + intraday risk state curve from 5-minute data) and ranks assets by how much a risk-adjusted target explains their metric dispersion, achieving better out-of-sample portfolio performance on Chinese A-shares.

---

## Method
**Metric Dependence Screening (MDS):**
1. Each asset-day is represented as a pair `(r_it, C_it)` where `r_it` is the daily return and `C_it` is the intraday risk curve (e.g., realised intraday volatility trajectory from 5-minute returns).
2. Assets are ranked by a Fréchet variation-based dependence score measuring how much a risk-adjusted benchmark target explains the metric (Wasserstein-style) dispersion of the asset's point-curve representations.
3. Two-stage procedure: MDS first screens the investable universe down to K candidates; standard mean-variance or minimum-variance allocation is then applied to the screened universe.

**Data:** 5-minute return data for 2,938 Chinese A-share stocks, July 2023 – December 2025.

**Benchmarks compared:** Return-based selection (rolling Sharpe, rolling IC) and scalar dependence screening (correlation of daily returns only).

---

## Results
MDS yields lower out-of-sample portfolio variance and higher Sharpe than both return-based and scalar dependence benchmarks, validating that intraday risk curve information contains selection-relevant content beyond daily scalar summaries. The improvement is attributed to the curse of dimensionality being mitigated through metric-space representations rather than high-dimensional covariance estimation. Specific Sharpe/MDD numbers are not given in the abstract; the improvement appears consistent across the full 2023–2025 test period.

---

## Implementable Idea
Our LOB data (23–24 snapshots per day) can serve as an approximate intraday risk curve. A practical adaptation for Feishu:

```python
# Step 1: construct per-asset intraday vol curve from LOB mid prices
lob['mid'] = (lob['ask_price_1'] + lob['bid_price_1']) / 2

def intraday_vol_curve(group):
    """Return per-snapshot mid-price return std within a trading day."""
    mids = group.sort_values('time')['mid'].values
    if len(mids) < 3:
        return np.nan
    # Compute intraday return volatility across snapshots
    snap_rets = np.diff(mids) / (mids[:-1] + 1e-8)
    return snap_rets.std()

intraday_vol = lob.groupby(['asset_id', 'trade_day_id']).apply(intraday_vol_curve).reset_index(name='intraday_vol')

# Step 2: MDS screening — select assets whose intraday vol is below market median
# (acts as an intraday risk screen complementary to 60d rolling vol)
daily = daily.merge(intraday_vol, on=['asset_id', 'trade_day_id'], how='left')
med_intrday = daily.groupby('trade_day_id')['intraday_vol'].transform('median')
daily['low_intraday_vol'] = daily['intraday_vol'] < med_intrday

# Combine with existing 60d rolling vol screen in trend_vol_v4:
# eligible = (rolling_vol low) AND (intraday_vol < median)
```

**Full MDS** requires a more elaborate Fréchet dependence computation, but the core idea — screen out stocks with abnormally high intraday risk curves relative to peers — is achievable with LOB snapshots.

**Addresses priority:** Priority 3 — Stock selection within the low-vol universe. The intraday risk screen provides an orthogonal dimension to the 60d rolling-vol ranking, potentially identifying stocks that appear low-vol in daily data but have elevated intraday risk (momentum crashes in progress).

---

## Relevance to Feishu Competition
Our current low-vol filter (60d rolling std) uses only daily returns and cannot see intraday risk spikes. In the Chinese A-share market, retail-driven intraday volatility can presage next-day limit-down events not visible in daily data. MDS-style intraday risk screening could reduce the incidence of sudden MDD events (currently bottleneck: MDD 7.98%). The LOB data covering July 2023–December 2025 overlaps significantly with the paper's test window, lending external validity to applying this on Feishu's dataset. This is an OOS-only idea — implementing it would require adding a LOB-derived intraday vol column to the selection step of trend_vol_v4, then running the backtest on D001–D484 for validation.

---

## Concepts
-> [[limit-order-book]] | [[chinese-ashore-market]] | [[factor-models]]
