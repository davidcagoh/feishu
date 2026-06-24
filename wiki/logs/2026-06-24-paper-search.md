# Paper Search Log — 2026-06-24

## Context

`wiki/learnings.md` → "What the Next Paper Search Should Prioritise" (last updated 2026-06-10, reconfirmed unchanged by the 2026-06-17 search) marks Priorities 1, 3, and 4 as fully/substantially addressed and Priority 2 (MDD reduction) as substantially addressed with one explicitly low-priority remaining item. The 2026-06-17 log flagged two specific things for this cycle to check:
1. Chinese A-share (not just US/global ETF) empirical validation of cash-overlay / vol-managed drawdown control.
2. Any post-hoc analysis of 2025–2026 Chinese low-vol bull-market underperformance with a *correction* mechanism (not just confirmation).

The competition submission (`T016_sell_open.csv`) was filed 2026-06-01; this remains post-submission research.

## Searched

WebSearch queries covering (arXiv direct fetch/listing pages and papers.cool both returned HTTP 403 in this environment again, consistent with prior weeks — relying on WebSearch snippets):

- Chinese A-share cash-overlay / vol-managed drawdown control (2026)
- Low-volatility factor China bull-market correction mechanisms (2026)
- q-fin.PM / minimum-variance China A-share regime papers (June 2026)
- SSRN Chinese A-share min-vol drawdown overlay (2026)
- Broad arXiv 2606.xxxxx sweep for China A-share content (via site-restricted search)
- Defensive/low-vol factor timing blended with momentum to offset bull-market lag (2026)
- Targeted follow-up checks on already-indexed authors: Xiong (continuous timing / cash-overlay series), Boukardagha (Wasserstein HMM regime investing) — no new papers from either since the indexed ones

## Candidates found, and why none were added

| Candidate | ID | Why excluded |
|---|---|---|
| Regime-Adaptive Continual Learning for Portfolio Management (ReCAP, KDD 2026) | arXiv:2606.00143 | Abstract now retrievable (was blocked last week): deep-RL continual-learning framework with a policy library per detected regime. Not Chinese-market specific, requires RL training infrastructure we don't have, and is a generic regime-switching architecture already superseded for our purposes by Shu & Mulvey (SJM) and Boukardagha (Wasserstein HMM), both indexed and explicitly marked "do not search further" in learnings.md |
| Sharpe-Driven Stock Selection and Liquidity-Constrained Portfolio Optimization (Chinese equity market) | arXiv:2511.13251 | Submitted Nov 2025 — over 7 months old, well outside the 2-week window; would have surfaced in earlier cycles |
| Deep Learning Enhanced Multi-Day Turnover Quantitative Trading (Chinese A-share) | arXiv:2506.06356 | Same paper flagged and excluded in the 2026-06-17 log (June 2025, one year old) |

No paper found in this cycle provides Chinese A-share-specific empirical validation of cash-overlay/vol-managed drawdown control, nor a correction mechanism for Chinese low-vol bull-market underperformance. Both remain open but are low-priority (the competition submission is already filed; this is post-hoc robustness research only).

## Conclusion

No new papers added this cycle. Three consecutive search cycles (06-10 confirmed closed, 06-17 found nothing, 06-24 found nothing) now support the conclusion that the paper-search well for this strategy's open priorities has run dry — further weekly searches on the same priority list are unlikely to be productive unless the priorities themselves change (e.g. if competition results/feedback reopen a specific question).

No changes made to `wiki/learnings.md`, `wiki/_index.md`, or `wiki/ideas/feishu-competition-signals.md` this cycle.
