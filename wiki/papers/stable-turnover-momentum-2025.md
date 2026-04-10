# Innovative Alpha Strategies for the Chinese A-Share Market: Stable Turnover Momentum Enhanced by Idiosyncratic Volatility (Zhang, Chen & Xu, 2025)

**Source:** DOI: 10.54254/2755-2721/2025.22458 — *Applied and Computational Engineering* (EWA Publishing), 6 May 2025
**Keywords:** momentum, turnover rate, idiosyncratic volatility, Chinese A-shares, factor enhancement

## Summary

Classical price-momentum has decayed in A-shares: annualised excess return fell from ~8% to ~3% as average daily turnover doubled (0.8% → 1.5%) between 2020–2025. The paper addresses this with a "Stable Turnover Momentum" signal that (1) filters out noisy momentum episodes by requiring both price-trend stability and turnover-rate stability, then (2) scales signal strength by idiosyncratic volatility (FF residual) to up-weight high-information stocks. Backtested on CSI 300 and CSI 1000 constituents 2019–2024.

## Key Results

- Evaluated on CSI 300 and CSI 1000 (Jun 2019–Jul 2024) under daily rebalancing with transaction costs
- Three enhancements jointly contribute: remove unstable momentum, require stable turnover, weight by IVOL
- Performance holds across volatile and stable market regimes
- Robust compared to plain cross-sectional momentum benchmarks
- Specific annualised return figures not disclosed in publicly accessible content

## Implementable Signal

Using only daily OHLCV (`open`, `high`, `low`, `close`, `volume`, `amount`, `adj_factor`):

**Step 1 — Adjusted returns.** `adj_close = close * adj_factor`. 20-day (or 63-day) trailing return: `r_t = adj_close_t / adj_close_{t-L} - 1`.

**Step 2 — Price curve stability.** R² of a linear regression of `adj_close` on time over the lookback window. Keep only stocks with sufficiently monotone price path (high R²).

**Step 3 — Turnover stability.** `turnover = amount / rolling_20d_median_amount`. `stability = 1 / std(turnover over window)`.

**Step 4 — Idiosyncratic volatility scaling.** Cross-sectional FF-style regression (market + SMB-proxy + HML-proxy). IVOL = std of daily residuals over 20-day trailing window. `signal = r_t × stability_price × stability_turnover × IVOL`.

**Step 5 — Cross-sectional ranking.** Rank within each `trade_day_id`. Long top decile, short bottom decile.

*SMB proxy*: return spread bottom-30% vs top-30% by `amount`-implied market cap. *HML proxy*: trailing 12-month return reversal spread. Both computable from `adj_close` and `amount`.

## Relevance to Feishu Competition

High — signal uses only price, volume, and turnover proxies available in `daily_data_in_sample.parquet`. CSI 300/1000 universe (2019–2024) closely overlaps the competition's 484-day, 2,270-asset dataset. Stability filters address the known noisy momentum problem in Chinese markets and complement existing reversal signals. **Priority: implement as `stable_turnover_momentum` signal.**

## Status

`[ ] untested` — signal not yet implemented
