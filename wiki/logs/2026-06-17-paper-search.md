# Paper Search Log — 2026-06-17

## Context

`wiki/learnings.md` → "What the Next Paper Search Should Prioritise" (last updated 2026-06-10) marks Priorities 1, 3, and 4 as fully or substantially addressed, and Priority 2 (MDD reduction) as "substantially addressed" with only one explicitly low-priority open item remaining (direct Chinese A-share validation of the Xiong cash-overlay framework, vs. the US/global ETF data it currently uses). The competition submission (`T016_sell_open.csv`) was already filed 2026-06-01; this is now post-submission research, not pre-deadline tuning.

## Searched

- arXiv q-fin.PM / q-fin.RM / q-fin.TR recent listings (direct fetch blocked — see note below)
- WebSearch queries covering:
  - Chinese A-share minimum-variance / drawdown-control / cash-overlay papers (June 2026)
  - Low-volatility factor regime allocation (q-fin.PM, 2026)
  - Quality-factor proxies usable without fundamentals data (price/volume only)
  - Sector-neutral minimum-variance alternatives
  - T+1 / overnight-gap empirical validation for Chinese A-shares
  - Follow-ups to indexed authors (Xiong continuous-timing/cash-overlay series; Boukardagha regime HMM)

**Note:** `arxiv.org` (both `/abs/` and `/list/.../recent`) and `export.arxiv.org`'s API returned HTTP 403 / host-not-allowlisted for direct fetch in this environment, so results are based on WebSearch snippets rather than full abstracts/listings. This is a tooling limitation, not a finding.

## Candidates found, and why none were added

| Candidate | arXiv ID | Why excluded |
|---|---|---|
| Anticipatory Portfolio Optimization (Noguer i Alonso, Jun 2) | 2606.04258 | Pure decision-theoretic framework (information/forecast/impact gap); no implementable rule, no empirical results, not Chinese-market specific |
| Mean-Variance Optimization in Ambiguous Financial Markets with Learning | 2606.11318 | Continuous-time Black-Scholes theory; requires drift-ambiguity prior estimation not feasible with price/volume-only Feishu data |
| Regime-Adaptive Continual Learning for Portfolio Management | 2606.00143 | Could not retrieve abstract (fetch blocked); WebSearch snippet suggests generic ML continual-learning framework, not Chinese-market or low-vol specific — insufficient evidence of relevance to prioritize over already-indexed regime papers |
| Deep Learning Enhanced Multi-Day Turnover Trading (Chinese A-share) | 2506.06356 | Dated June **2025** (one year old) — outside the 2-week window; also already informally surfaced in a prior search per repeated appearance in results |

None of these speak to the one remaining open item (Chinese-specific cash-overlay validation) or introduce a new concrete portfolio-construction rule beyond what's already indexed (34 papers, Signals #1–#32 in `ideas/feishu-competition-signals.md`).

## Conclusion

No new papers added this cycle. The IS parameter space and paper-search priorities are both explicitly marked exhausted/closed in `learnings.md` as of 2026-06-10; this search confirms no qualifying new evidence has appeared in the most recent two weeks. Recommend the next search cycle continue to check specifically for:
1. Chinese A-share (not just US/global ETF) empirical validation of cash-overlay / vol-managed drawdown control
2. Any post-hoc analysis of 2025–2026 Chinese low-vol bull-market underperformance with a *correction* mechanism (not just confirmation — already closed)

No changes made to `wiki/learnings.md`, `wiki/_index.md`, or `wiki/ideas/feishu-competition-signals.md` this cycle.
