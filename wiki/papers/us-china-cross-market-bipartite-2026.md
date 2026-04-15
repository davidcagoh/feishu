# A Bipartite Graph Approach to U.S.-China Cross-Market Return Forecasting

**Authors:** Jing Liu, Maria Grith, Xiaowen Dong, Mihai Cucuringu  
**Venue/Source:** arXiv q-fin  
**arXiv/DOI:** arXiv:2603.10559  
**Date:** March 11, 2026

---

## Core Claim
Non-overlapping trading hours between the U.S. and Chinese equity markets create an exploitable informational asymmetry: U.S. close-to-close returns (computed while Chinese markets are closed) contain substantial predictive information for Chinese open-to-close intraday returns the following session, but not the reverse. A sparse directed bipartite graph, whose edges are selected via rolling-window hypothesis testing, identifies which U.S. stocks predict which Chinese stocks, and this structured feature selection materially improves forecasting Sharpe ratios over unstructured baselines.

---

## Method
1. **Time-zone bridge**: For each Chinese trading day, the "predictor window" is the U.S. session that ends while Chinese markets are closed — specifically the U.S. close-to-close return on day _t−1_.
2. **Bipartite graph construction**: Fit a rolling-window Granger-causality / cross-correlation test for each (U.S. stock _u_, Chinese stock _c_) pair. Retain edges where the null of no predictability is rejected at a chosen significance level. This yields a sparse bipartite adjacency matrix with typically O(10–30) U.S. predictors per Chinese stock.
3. **Downstream ML**: For each Chinese stock, use the selected U.S.-stock returns as features in ridge regression, lasso, random forest, and gradient boosting models. Predictions target Chinese open-to-close return.
4. **Rolling regime**: The graph is re-estimated on a rolling window (not fixed), allowing structural breaks in cross-market linkages to propagate over time.

---

## Results
- Pronounced directional asymmetry: U.S. → China Sharpe ratios consistently exceed China → U.S.
- Graph-based feature selection contributes materially vs. full-feature (un-selected) baselines: sparsity forces interpretability and prevents overfitting to noisy cross-market correlations.
- Both the graph selection mechanism and the cross-market information itself contribute independently to predictive performance (ablation tested).
- Ensemble methods (gradient boosting, random forest) outperform linear regularisation, suggesting nonlinear cross-market effects.

No explicit numerical Sharpe ratio from abstract; paper reports consistently positive directional forecast performance with portfolio-level strategy validation.

---

## Implementable Signal
The U.S.-stock predictor set is **not directly available** in the Feishu dataset (no U.S. market data). However, the paper's insight translates into two actionable approximations using only our in-sample data:

**Approximation 1 — Market-factor lag signal:**
The cross-market channel is effectively "market-wide information transmitted overnight." A feasible proxy is to use the cross-sectional market return on day _t_ (computable as the equal-weight mean daily return across all assets) as a lagged predictor for the next day's individual stock returns, especially for stocks with high historical beta to the market factor:

```python
# Market-wide daily return (proxy for the systemic information)
mkt_ret = daily.groupby('trade_day_id')['ret'].mean()  # ret = adj_close pct_change

# Each stock's rolling beta vs market (60-day window)
# Use stocks with high market-beta as "transmission channel" stocks
# Predict: if mkt_ret[t] is very negative, high-beta stocks may overshoot more
#          → stronger reversal signal tomorrow for high-beta stocks
beta_scaled_reversal = -daily['ret'] * daily['rolling_beta']  # sign: reversal
```

**Approximation 2 — Sector / cluster lag:**
Sort assets into clusters by IC correlation (see `wiki/results/ic_correlation.md`). Use the prior-day average return of cluster _k_ as a predictor for the next-day return of assets in correlated clusters.

**Addresses hypothesis:** Hypothesis #4 — *Does cross-asset information help?* This paper provides direct evidence that it does, particularly when structured as a sparse graph rather than dense cross-asset features. The result also partially speaks to hypothesis #1 (are signals catching the same thing?): the cross-market information is orthogonal to within-asset signals.

---

## Relevance to Feishu Competition
The most immediate implication is not a new signal but a conceptual upgrade: **cross-sectional information within the Chinese universe (sector/cluster lagged returns) is worth testing as a feature**. The bipartite graph principle — sparse, rolling, hypothesis-tested edges — applies equally to cross-stock predictability within a single market. In our data, this would mean identifying which assets' prior-day returns Granger-predict which other assets' next-day returns, then using that sparse feature set in a linear model.

The practical limitation is data: we have 484 days and 2,270 assets, so the bipartite graph would need aggressive sparsification (likely ≤5 predictors per asset) to avoid overfitting. A simpler implementation using IC-correlated clusters (from `wiki/results/ic_correlation.md`) is more feasible within the competition timeline.

Secondary implication: the "overnight information" framing aligns with our confirmed fact that reversal alpha is concentrated in the overnight gap (close-to-open). The U.S.-to-China lag is structurally similar to what we already exploit with `low_vol` (information formed after China's close, traded at the next day's open).

---

## Concepts
→ [[statistical-arbitrage]] | [[factor-models]] | [[chinese-ashore-market]]
