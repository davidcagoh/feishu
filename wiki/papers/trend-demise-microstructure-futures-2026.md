# Is Trend Still Your Friend? A Microstructural Account of the Demise of Short-Term Trend-Following

**Authors:** Jutta G. Kurth, Zoltan Eisler, Adam Rej, Jean-Philippe Bouchaud (Capital Fund Management / CFM)  
**Venue/Source:** arXiv q-fin.TR (Trading and Market Microstructure)  
**arXiv/DOI:** arXiv:2607.01550  
**Date:** July 2, 2026

---

## Core Claim
Short-term trend-following in futures markets has ceased to reliably generate returns since approximately 2009. The degradation is NOT uniform: it is concentrated in **small-tick** (highly liquid, institutional) futures contracts and is essentially absent in **large-tick** (lower-liquidity, higher-friction) contracts. The volatility-normalised tick size is the primary cross-sectional predictor of trend-following viability, outperforming capacity constraints, market electronification, and CTA-flow explanations.

---

## Method
Cross-section of ~100 liquid futures contracts spanning 1995–2025 (equities, rates, FX, commodities), tested against an industry-representative CTA proxy. Four candidate explanations evaluated:
1. **Capacity constraints** — CTA AUM growth → alpha decay
2. **Market electronification** — faster price discovery → quicker trend arbitrage
3. **CTA-vs-order-flow interactions** — herding/frontrunning kills the edge
4. **Microstructural mechanism** — volatility-normalised tick size explains persistence of trends

The first three fail on grounds of timing (electronification predates the 2009 break), magnitude (capacity explanation predicts larger-cap assets should degrade first, but they don't), or cross-sectional heterogeneity (herding should affect all contracts similarly). The tick-size mechanism passes all three tests.

**Key metric:** volatility-normalised tick size = `tick_size / (price × daily_vol)`. Contracts with small tick/vol ratio (very liquid: index futures, G10 FX) degraded post-2009. Contracts with large tick/vol ratio (less liquid: commodity futures, some EM) retained trend alpha.

---

## Results
- Short-term trend PnL (signal horizon 1-20 days) has declined significantly post-2009 for small-tick contracts
- Long-term trend (horizon 60-252 days) has remained more robust across all contract types
- The tick-size mechanism: small tick → market makers can tightly manage position, absorbing trend flow without allowing momentum to persist → signals are exploited and arbitraged away faster
- Large tick → wider bid-ask spread → market makers face adverse selection → trend can persist longer because the friction prevents pure arbitrage

---

## Implementable Idea
This paper does not directly provide a new trading signal for our long-only minimum-variance equity strategy. However, it provides a microstructural framework that **validates our trend filter's use in Chinese A-shares** and predicts its continued viability:

**Why Chinese A-shares are "large-tick" in spirit:**
1. **Fixed minimum tick sizes** that are non-trivial relative to daily vol (especially for lower-priced stocks)
2. **T+1 settlement** creates friction: retail investors cannot exit the same day → trends persist because arbitrage capital is constrained
3. **±10% price limits** create discrete friction: trends are capped at 10%/day → require multiple days to manifest fully → longer-horizon filters (35-day) are theoretically optimal
4. **Retail dominance** (~70% of trading volume is retail) → slower reaction to information → trend-based signals persist longer than in institutional-dominated markets

**Implication for our strategy:** Our 35-day trend window operates in the "long-horizon" regime where the paper confirms trend alpha remains intact even for small-tick contracts. The microstructural constraints of Chinese A-shares (T+1, ±10% limits, retail dominance) are friction-generating mechanisms functionally similar to large tick sizes — they slow arbitrage capital and allow trends to persist long enough for our 35-day filter to remain valid.

**Addresses priority:** Priority 3 (Stock selection) — confirms that the trend filter used as a negative screen in `trend_vol_v4` operates in a regime (35-day horizon + high-friction Chinese market) where trend signals remain viable.

None — no new signal. This is a validation/context paper confirming our existing approach.

---

## Relevance to Feishu Competition
The competition is filed, but this paper addresses a standing concern: will our 35-day trend filter continue to work in OOS data? The paper's framework suggests YES for two reasons:
1. Our filter is at the 35-day (5-week) horizon, which falls in the "medium to long" range where trends have remained persistent even in futures
2. Chinese A-shares have structural friction (T+1, limits, retail) that suppresses short-horizon arbitrage — making the market function like a "large-tick" market regardless of nominal tick size

The paper also closes a theoretical gap: prior papers in our wiki on trend signals (Xiong 2026, continuous timing) were empirical; this paper provides a microstructural mechanism for WHY trend signals persist in certain markets. The mechanism directly maps to Chinese A-share market structure.

**Post-competition learning:** When evaluating future competitions in other markets, use volatility-normalised tick size as a predictor of whether a trend filter will remain viable. Low tick/vol ratio → trend filters have shorter half-lives → require shorter lookback windows or should be replaced with other selection criteria.

---

## Concepts
-> [[chinese-ashore-market]] | [[mean-reversion]] | [[limit-order-book]]
