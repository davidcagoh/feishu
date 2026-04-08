# Statistical Arbitrage

Exploits **temporary price deviations** between assets expected to co-move, by going long the underperformer and short the outperformer, expecting convergence.

---

## The Three-Problem Decomposition

Every stat-arb strategy must answer:
1. **Portfolio construction**: which assets are "similar"? (similarity = same factor exposure)
2. **Signal extraction**: which residual patterns indicate temporary mispricing?
3. **Trading policy**: given signals, how to allocate to maximise risk-adjusted returns after costs?

Traditional approaches solve these independently (two-step). The joint approach in [[attention-factors-stat-arb]] solves all three simultaneously.

---

## Factor Residual Framework

```
R_{i,t} = β'_{i,t-1} F_t + ε_{i,t}

where:
  F_t          = systematic factors (tradable portfolios)
  β_{i,t-1}    = time-varying factor loadings
  ε_{i,t}      = idiosyncratic residual → the "mispricing" signal
```

Trading the residuals `ε` is mean-variance neutral to the factors by construction.

---

## Common Approaches

| Method | Factor model | Signal | Notes |
|--------|-------------|--------|-------|
| Pairs trading | Cointegration | Spread | Parametric, small universe |
| PCA stat-arb | PCA factors | OU model on residuals | Scalable but two-step |
| IPCA stat-arb | Conditional PCA (characteristics) | Same | Better factors, still two-step |
| Attention Factors | Attention-based conditional factors | LongConv sequence model | One-step, joint training |

---

## Key Performance Metrics

- **IC (Information Coefficient)**: Spearman correlation between signal and next-day return. IC > 0.03 is good for daily signals.
- **IR (Information Ratio)**: IC / IC_volatility. Target IR > 0.5.
- **Sharpe ratio**: annualised return / annualised volatility. Net Sharpe > 1.5 is strong for a single alpha.
- **Turnover**: fraction of portfolio replaced per period. High turnover kills net Sharpe.
- **Drawdown**: peak-to-trough decline in equity curve.

---

## Transaction Cost Considerations

- Round-trip cost per trade ≈ half-spread + market impact + commission
- For liquid equities: ~5–15bps round-trip
- A signal with gross IC=0.05 but daily turnover of 50% may have near-zero net IC
- **Key insight from [[attention-factors-stat-arb]]**: factors optimised for explained variance tend to have high turnover. Optimising factors for net Sharpe forces lower turnover.

---

## Papers in This Wiki
- [[attention-factors-stat-arb]] — joint factor + trading policy, Sharpe 2.3 net
- [[drl-optimal-trading-partial-info]] — RL trading of mean-reverting signal with latent regimes
- [[ai-asset-pricing-models]] — complementary: models the systematic component that stat-arb residualises out
- [[jump-start-control-scientist]] — foundational framework; LOB interaction with stat-arb strategies

---

## Feishu Competition Notes
- The competition provides 484 days × 2270 assets. This is a reasonable universe for stat-arb.
- The `adj_factor` column is critical: compute adjusted returns `close * adj_factor` before any cross-sectional work.
- Cross-sectional demeaning per `trade_day_id` is the minimal neutralisation step.
- LOB imbalance `(bid_vol_1 - ask_vol_1) / (bid_vol_1 + ask_vol_1)` is a microstructure stat-arb signal — see [[limit-order-book]].
