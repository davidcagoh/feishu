# Paper Search Log — 2026-07-22

## Context

This is the fifth consecutive weekly paper search since the competition submission (T016_sell_open.csv, filed 2026-06-01). The 2026-06-24 log concluded the paper-search well for the current open priorities had run dry. This cycle ran the search again given the 4-week gap since the last attempt, with the same priority framing.

The "What the Next Paper Search Should Prioritise" section of `wiki/learnings.md` (last updated 2026-05-27, reconfirmed unchanged through four prior search cycles) marks:
- Priority 1 (bull-market resilience): RESOLVED
- Priority 2 (MDD reduction): SUBSTANTIALLY ADDRESSED; remaining open item (Chinese-specific cash-overlay empirical validation) is low-priority post-competition
- Priority 3 (stock selection within low-vol): SUBSTANTIALLY ADDRESSED; remaining open items (quality factors from fundamentals, sector-neutral without labels) are not testable with price/volume-only data
- Priority 4 (OOS regime): CLOSED

## Searched

arXiv direct page listing and HTML pages returned HTTP 403 (consistent with all prior cycles). Relied on WebSearch snippets to enumerate recent papers.

Search queries covered:
- arXiv 2607.XXXXX sweep (July 2026 papers): q-fin.PM, q-fin.TR, q-fin.RM minimum variance, low volatility, drawdown, stock selection
- Chinese A-share portfolio papers July 2026 (arXiv and SSRN)
- Sector-neutral / correlation-based diversification without sector labels (2026)
- Low-vol / min-var turnover cost optimization (2026)
- Adaptive position sizing and drawdown control (2026 q-fin.PM)
- China market microstructure and rule changes (July 2026)
- Variable selection for minimum-variance portfolios (follow-up on previously surfaced paper arXiv:2508.14986)

## Papers Evaluated and Why None Were Added

| Candidate | ID / Source | Why excluded |
|---|---|---|
| Minimizing Benchmark-Relative Drawdown Duration via Occupation Time Penalization | arXiv:2607.11335 (Jul 13, 2026) | Theoretical (q-fin.MF, HJB equations). Penalizes *benchmark-relative* drawdown duration — not absolute MDD. Our strategy has no external benchmark. No implementable idea for our competition setup. |
| Portfolio Optimization under Heavy Tails and Asymmetric Volatility: Evidence from Taiwan-Exposed ETFs | arXiv:2607.16450 (Jul 2026) | Taiwan semiconductor ETFs; GJR-GARCH and CVaR on US-listed ETFs. Not Chinese A-shares; no new construction idea beyond what Fang & Ślepaczuk (already indexed) covers. |
| Gaussian Boson Sampling for Asset Clustering in Statistical Arbitrage Portfolios | arXiv:2607.19279 (Jul 21, 2026) | Quantum computing approach to correlation-based clustering for statistical arbitrage. Stat-arb is explicitly ruled out (execution gap). Exotic technology; not applicable. |
| SciPhy Reinforcement Learning for Portfolio Optimization | arXiv:2607.15195 (Jul 2026) | Continuous-time RL with HJB/PINN. No Chinese market focus; requires RL training infrastructure. RL approaches covered and deprioritised in learnings.md. |
| Variable selection for minimum-variance portfolios | arXiv:2508.14986 (Aug 2025) | Outside the 2-week window (12 months old); already surfaced and excluded in prior cycles. Uses 4,610 firm-level characteristics including fundamentals (earnings, B/M) unavailable in Feishu; price/volume subset (beta, rolling vol, momentum) is already captured by our existing ranking. |
| Cardinality-constrained portfolio optimization with clustering | Annals of Operations Research, Vol. 279, Apr 2026 | Hierarchical clustering on residual return correlations + cardinality-constrained MV. Relevant to sector concentration problem but: (a) we already tried K-means cluster selection (failed, Score=0.1286, excessive turnover); (b) hierarchical vs K-means may differ but the failure mode (high churn from cluster rotation) is structural, not algorithm-specific. No concrete advantage over current approach without sector labels. |

## Non-Paper Finding: China A-Share Market Structure Change (July 6, 2026)

Three trading rule changes took effect across China's three major exchanges on **6 July 2026** — outside and after our OOS period (D485–D726 data released 2026-05-28), so no impact on competition results, but worth documenting for future reference:

1. **After-hours fixed-price trading expanded to all A-shares**: Previously limited to SSE 50 / CSI 300 / CSI 500 constituents and selected ETFs, after-hours trading (15:05–15:30, fixed closing price) now covers the entire A-share universe including all ETFs. This creates a new lower-friction execution window for sell-at-close positions.

2. **ST/\*ST price limits widened from ±5% to ±10%**: Risk-warning stocks on the Shanghai and Shenzhen main boards now have the same daily trading limit as standard shares (±10%). Our strategy excludes illiquid stocks and would rarely hold ST names, but the change slightly reduces the divergence in limit-day frequency between ordinary and flagged stocks.

3. **Fund closing mechanism → closing call auction**: Public funds must now price off the closing call auction rather than continuous trading. The final three minutes of trading are a non-cancellable call auction, concentrating closing-price order flow. For sell-at-close strategies, this means the final execution quality improves for institutional-sized orders (auction vs. continuous close).

**Implication**: For any future competition using a sell-at-close mode, the call auction change (item 3) reduces adverse selection risk at close, partially closing the gap between sell-at-open and sell-at-close that we observed in IS data (Score 0.4024 vs. ~0.39 sell-close). Worth re-evaluating if a new OOS period falls entirely within this new regime.

Sources: National Law Review (July 16, 2026); BigGo Finance news summaries.

## Conclusion

No new academic papers were added this cycle. The 2026-06-24 conclusion holds: the paper-search well for this project's current open priorities is dry. The only new finding of note is the China market structure change documented above.

`wiki/learnings.md` updated with the market structure change note. No changes to `wiki/_index.md` or `wiki/ideas/feishu-competition-signals.md`.
