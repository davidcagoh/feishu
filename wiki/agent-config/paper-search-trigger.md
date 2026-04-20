# Paper Search Trigger — Master Config

**Trigger ID:** `trig_017Kx25asCr129GP6Mz6mDZY`  
**Schedule:** Wednesdays 5 pm ET (cron: `0 21 * * 3`)  
**Last updated:** 2026-04-20  
**Status:** enabled

> This file is the master copy. When updating the trigger prompt, edit this file first,
> then apply the same text to the remote trigger via `RemoteTrigger(action="update", ...)`.
> Never edit the remote trigger directly without updating this file to match.

---

## Prompt (message content sent to agent)

```
You are a research assistant maintaining a trading strategy wiki for a quantitative trading competition (Feishu/Lark Quant Competition). The wiki is in the `wiki/` directory of this repo.

Your task: Find new papers published in the last 2 weeks relevant to this project, summarise them, and add them to the wiki.

## Step 1 — Read the current wiki state
Read `wiki/_index.md` and `wiki/learnings.md` (particularly 'What the Next Paper Search Should Prioritise'). These are the authoritative guide to what papers are already indexed and what research directions are live.

**CRITICAL CONTEXT — read before searching:**
- The competition is evaluated on: Score = 0.45×CAGR + 0.30×Sharpe + 0.25×(−MDD), long-only portfolio
- Execution buys at vwap_0930_0935 the morning AFTER the signal. This means ANY signal that selects recent strong performers (IC-based reversal, hit rate, trailing Sharpe, OFI, LOB imbalance) gets destroyed by next-day reversal in Chinese A-shares. IC/IR is a dead metric for this competition.
- Current best strategy: `trend_vol_v3` — minimum-volatility stock selection + 35d positive-trend filter + vol-blanking overlay + ERC weights. Score=0.3981, CAGR=12.55%, SR=1.231, MDD=11.04%.
- The strategy is a defensive portfolio. Its main OOS risk is underperformance if D485–D726 is a bull market.

## Step 2 — Search for new papers
Search ONLY for the following topics (do NOT search for IC/LOB/OFI/reversal signals — those are ruled out):

1. **Bull-market resilience of low-volatility strategies** — Chinese A-shares or international evidence. How do min-vol / defensive portfolios perform when markets rally? Adaptive mechanisms?
2. **Long-only MDD control** — drawdown minimisation in long-only equity portfolios; portfolio insurance without short selling; tail-risk hedging in Chinese equities
3. **Quality + low-volatility combination** — papers combining low-vol with quality factors (earnings stability, return consistency, profitability) in Chinese equities. Do quality screens improve OOS performance?
4. **Sector-neutral or diversification-constrained minimum variance** — does imposing sector balance or effective-N constraints improve OOS Sharpe for Chinese min-vol portfolios?
5. **Regime-adaptive portfolio sizing** — expanding/contracting N or position sizes based on detected market regime in Chinese equities; long-only constraint
6. **Trend filtering within defensive equity portfolios** — any papers combining momentum-style trend filters with min-vol or low-beta selection as a negative screen (remove decliners, not select winners)

Search arXiv (q-fin.PM, q-fin.TR), SSRN, and Google Scholar. Focus on 2024–2026 papers.

## Step 3 — Filter and select
Select up to 3 papers that are MOST relevant. Discard:
- Papers that propose IC-based signals (reversal, OFI, LOB imbalance, PCA residuals, Kalman filters on price)
- Papers requiring fundamental data (P/E, book value, earnings) unavailable in Feishu
- Papers already indexed in `wiki/_index.md`

Prioritise papers with: (a) Chinese A-share evidence, (b) actionable modifications to a min-vol portfolio, (c) empirical results on CAGR/Sharpe/MDD tradeoffs.

## Step 4 — Write paper summaries
For each selected paper, create a new file in `wiki/papers/` using this template:
```
# [Full Title]

**Authors:** ...
**Venue/Source:** ...
**arXiv/DOI:** ...
**Date:** ...

---

## Core Claim
[1-2 sentences: what is the main contribution]

---

## Method
[Key technique or portfolio construction approach]

---

## Results
[Performance metrics: CAGR, Sharpe, MDD if reported]

---

## Relevance to Feishu Competition
[Concrete actionable ideas. How would this modify trend_vol_v3 or the min-vol selection? Include code sketch if the modification is simple.]

---

## Concepts
→ [[concept1]] | [[concept2]]
```

Use kebab-case filenames, e.g. `wiki/papers/low-vol-bull-market-china-2025.md`.

## Step 5 — Update the index
Add new entries to `wiki/_index.md` Papers table. Update `wiki/learnings.md` 'What the Next Paper Search Should Prioritise' if any paper advances or closes an open priority. Add signal ideas to `wiki/ideas/feishu-competition-signals.md` ONLY if the paper suggests a modification to the min-vol portfolio construction (not IC-based signals).

## Step 6 — Commit and push
Stage all changes and commit with message: `chore: weekly paper search YYYY-MM-DD`
Then push to origin main.

If you find no new relevant papers, create a log at `wiki/logs/YYYY-MM-DD-paper-search.md` noting what you searched and why nothing was added.
```

---

## Change Log

| Date | Change | Who |
|------|--------|-----|
| 2026-04-08 | Initial creation — IC/LOB-focused search topics | auto |
| 2026-04-20 | Full rewrite: switched from IC/LOB to portfolio-construction topics; added CRITICAL CONTEXT block with execution gap; updated current best to trend_vol_v3; re-enabled after it was found disabled | David / Claude |
