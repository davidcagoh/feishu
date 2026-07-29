# Paper Search Log — 2026-07-29

## Context

Sixth consecutive weekly paper search since the competition submission (T016_sell_open.csv, filed 2026-06-01). The 2026-07-22 log documented five prior cycles with zero additions. Priority framing unchanged.

`wiki/learnings.md` search priorities (last updated 2026-05-27):
- Priority 1 (bull-market resilience): RESOLVED
- Priority 2 (MDD reduction): SUBSTANTIALLY ADDRESSED; remaining open item (Chinese-specific cash-overlay empirical validation) is low-priority post-competition
- Priority 3 (stock selection within low-vol): SUBSTANTIALLY ADDRESSED; remaining open items (quality factors from fundamentals, sector-neutral without labels) are not testable with price/volume-only data
- Priority 4 (OOS regime): CLOSED

## Searched

arXiv direct pages returned HTTP 403 (consistent with all prior cycles). Relied on WebSearch snippets and specific paper lookups.

Search queries covered:
- arXiv 2607.XXXXX sweep (July 15–29, 2026 papers): q-fin.PM, q-fin.TR minimum variance, low volatility, drawdown, Chinese equity
- SSRN Chinese A-share portfolio strategy July 2026
- Google Scholar Chinese A-share portfolio volatility regime July 2026
- Chinese ETF portfolio rebalancing (ScienceDirect 2026)
- Neural network minimum-variance portfolio July 2026
- Tail risk management trend following CVaR drawdown July 2026

## Papers Evaluated and Why None Were Added

| Candidate | ID / Source | Why excluded |
|---|---|---|
| Neural Network-Driven Volatility Drag Mitigation under Aggressive Leverage | arXiv:2607.23068 (ICAIF 2025 proceedings, uploaded to arXiv Jul 25, 2026) | Compact NN (2,175 vs 39,586 params) for global min-variance via hyperbolic EWMA + BiGRU eigencleaning. Achieves lowest OOS portfolio variance vs. nonlinear-shrinkage and risk-parity benchmarks. Excluded: focus is on *leveraged* portfolios — leverage amplifies variance drag, and the NN's advantage is in managing that amplification. Long-only Feishu competition uses no leverage; variance reduction from NN vs. rolling-window covariance is incremental and not validated in a Chinese A-share context. Implementation requires NN training infrastructure. BAWS (arXiv:2603.01157, already indexed) provides simpler, non-parametric adaptive window that is directly deployable. |
| Observable Matrix Dynamics of Stocks | arXiv:2607.19005 (Igor Halperin, Jul 21, 2026) | OMD framework: arccos distance matrix of rolling return correlations → spectrum tracks crisis regime. Applied to S&P 500 across 2001, 2008, 2020 crises. Identifies sector rotation sequences and crisis precursors (endogenous crises only; exogenous shocks like 2020 not predictable). Excluded: US equity focus; OMD is a visualisation/diagnosis tool, not a trading signal generator. No concrete formula for stock selection or portfolio weighting. Regime detection already addressed by vol-ratio detector and Pang & Lin 5-state classifier (both indexed). |
| Portfolio Optimization under Dynamic Rebalancing via Topological Data Analysis and News Sentiments | arXiv:2607.21170 (Jul 25, 2026) | TDA-based asset clustering + FinBERT sentiment scores → dynamic portfolio rebalancing. Excluded: requires financial news text data (not available in Feishu — only OHLCV + LOB). TDA clustering has higher complexity than K-means which already failed (Score=0.1286) due to turnover cost; news sentiment is a fundamentally different data source not in scope. |
| Empirical study of portfolio rebalancing strategies in the Chinese ETF market | Finance Research Letters (May 2026, DOI: 10.1016/j.frl.2026.110119) | Two-fund ETF portfolio rebalancing: short-cycle (≤10 days) delivers 49.1% higher relative excess return vs. long cycles; non-linear negative link between asset correlation and rebalancing benefit. Excluded: two-fund ETF context is far from our 20-stock equity selection problem; rebalancing frequency is already daily in our strategy (constrained by T+1 and signal update); the non-linear correlation finding is interesting but covered implicitly by ERC weighting (which reduces pairwise correlation drag). No concrete change to signal or construction warranted. |
| ESG portfolio performance across risk tiers and market conditions: New evidence from China | ScienceDirect / SSRN:5679157 (Jun 2026) | Mean-variance + stochastic dominance on CSI 300 / CSI 800 ESG-rated portfolios 2020–2025. Low-risk ESG portfolios consistently outperform market indices in crisis periods. Excluded: requires ESG ratings data (not available in Feishu — price/volume only). ESG ratings are fundamentals-based; no implementable idea with available data. |

## Market Commentary Note (July 27, 2026)

China Daily (July 27, 2026): "A-shares poised for steady higher-quality growth." Analyst consensus continues to point to a "slow bull" / measured upward trend in H2 2026. No dramatic regime shift reported. Consistent with the OOS regime check (D485–D726: 22.3% bull, 69% neutral) and the slow-bull characterisation from the 2026-05-28 analysis.

## Conclusion

No new academic papers were added this cycle. This is the sixth consecutive weekly search (2026-06-10 through 2026-07-29) returning zero additions. The paper-search well for this project's current open priorities is dry.

The most promising paper reviewed this cycle — arXiv:2607.23068 (NN min-variance, ICAIF'25) — is potentially useful for future min-variance infrastructure but is not directly actionable in the Feishu context and requires significant NN training overhead.

`wiki/learnings.md` streak counter updated. No changes to `wiki/_index.md` or `wiki/ideas/feishu-competition-signals.md`.
