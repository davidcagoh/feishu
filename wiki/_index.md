# Trading Strategy Wiki

Knowledge base for the Feishu/Lark Quant Competition. All content written and maintained by Claude. Do not edit directly.

**Last updated:** 2026-04-10  
**Papers indexed:** 9  
**Concepts:** 7  
**Ideas:** 12 signals catalogued, 9 implemented

---

## Papers

| File | Title | Key Result | Relevance |
|------|-------|-----------|-----------|
| [attention-factors-stat-arb](papers/attention-factors-stat-arb.md) | Attention Factors for Statistical Arbitrage (Epstein et al., ICAIF 2025) | Sharpe 2.3 net via joint factor+trading end-to-end model; weak factors matter | High — factor residual framework, directly maps to Feishu daily data |
| [drl-optimal-trading-partial-info](papers/drl-optimal-trading-partial-info.md) | Deep RL for Optimal Trading with Partial Information (Macrì, Jaimungal, Lillo, 2025) | prob-DDPG (regime probs as input) dominates; quality of info > architecture | High — OU signal model, regime conditioning, applies to LOB imbalance |
| [jump-start-control-scientist](papers/jump-start-control-scientist.md) | A Jump Start to Stock Trading Research (Barmish et al., CDC 2024) | Tutorial: LOB structure, Kelly betting, feedback control framing | Medium — foundational; LOB section directly relevant to Feishu data |
| [ai-asset-pricing-models](papers/ai-asset-pricing-models.md) | Artificial Intelligence Asset Pricing Models (Kelly et al., Dec 2024) | Nonlinear portfolio transformer achieves Sharpe 4.6 via cross-asset attention | Medium — requires characteristics; adaptable with price-based features |
| [ofi-matched-filter-normalization-2025](papers/ofi-matched-filter-normalization-2025.md) | Optimal Signal Extraction from Order Flow: A Matched Filter Perspective (Kang, Dec 2025) | Market-cap normalization of OFI yields t=9.65 vs next-day returns; 1.99× SNR vs standard volume norm | High — directly upgrades LOB imbalance signal; normalization recipe for Feishu LOB data |
| [cross-market-alpha191-lasso-2026](papers/cross-market-alpha191-lasso-2026.md) | Cross-Market Alpha: Testing Short-Term Trading Factors via Double-Selection LASSO (Jan 2026) | 17 of 191 Chinese Alpha191 factors survive in US market; factor 046 (mean reversion ratio) and 071 (24d deviation) most robust | High — identifies universal Chinese A-share short-term signals directly implementable with daily data |
| [csi300-ofi-ou-dynamics-2025](papers/csi300-ofi-ou-dynamics-2025.md) | Stochastic Price Dynamics in Response to Order Flow Imbalance: CSI 300 (Hu & Zhang, May 2025) | OU-Lévy model outperforms Hawkes for OFI dynamics; quasi-Sharpe ratio derived as principled trading trigger | High — Chinese futures data, upgrades LOB signal with OU parameter estimation and regime-adaptive confidence |
| [stable-turnover-momentum-2025](papers/stable-turnover-momentum-2025.md) | Innovative Alpha Strategies for Chinese A-Share: Stable Turnover Momentum Enhanced by IVOL (Zhang, Chen & Xu, 2025) | Filters noisy momentum by requiring price + turnover stability, scales by IVOL; survives transaction costs on CSI 300/1000 2019–2024 | High — all inputs available in daily dataset; addresses the known momentum decay in A-shares |
| [factor-models-chinese-ashares-2024](papers/factor-models-chinese-ashares-2024.md) | Factor Models for Chinese A-Shares (Hanauer, Jansen, Swinkels & Zhou, 2024) | After transaction costs, optimal model = MKT + SMB + E/P only; profitability/investment/B/M don't survive | Medium — E/P not directly available but guides factor selection; three-factor alpha is the right evaluation target |

---

## Concepts

| File | Summary |
|------|---------|
| [statistical-arbitrage](concepts/statistical-arbitrage.md) | Factor residual framework; IC/IR metrics; transaction cost impact |
| [mean-reversion](concepts/mean-reversion.md) | OU process; ADF test; half-life; regime-switching |
| [limit-order-book](concepts/limit-order-book.md) | LOB structure; imbalance formula; Feishu-specific loading code |
| [factor-models](concepts/factor-models.md) | PCA, IPCA, Attention Factors; weak factors; SDF connection |
| [transformer-in-finance](concepts/transformer-in-finance.md) | Cross-asset attention; linear vs nonlinear PT; implementation notes |
| [reinforcement-learning](concepts/reinforcement-learning.md) | DDPG; GRU; prob-DDPG recipe; when RL beats classical control |
| [kelly-betting](concepts/kelly-betting.md) | Kelly formula; fractional Kelly; Kelly = max-SR portfolio |
| [chinese-ashore-market](concepts/chinese-ashore-market.md) | T+1 settlement; ±10% price limits; retail dominance; what factors work in China |

---

## Competition Ideas

| File | Contents |
|------|---------|
| [feishu-competition-signals](ideas/feishu-competition-signals.md) | 9 alpha signal ideas, tiered by complexity; evaluation code; priority order |

---

## Cross-Paper Connections

```
AIPM (Kelly et al.)          Attention Factors (Epstein et al.)
    ↓                               ↓
Models systematic returns    Models idiosyncratic residuals
(factor β' F_t)              (ε_{i,t} = R_{i,t} - β' F_t)
    ↓                               ↓
Cross-asset attention        Cross-asset attention
for SDF estimation           for factor construction
         ↘                 ↙
          Both use attention for cross-asset information sharing
          Both achieve Sharpe ~4-5 on US equities

Deep RL Paper (Macrì et al.)         Control Tutorial (Barmish et al.)
    ↓                                       ↓
OU signal model                       LOB structure + Kelly sizing
Regime-switching params               Feedback control framing
prob-DDPG for latent filtering        Mathematical foundations
    ↓                                       ↓
Best for: conditioning signals        Best for: understanding data
on regime state                       and sizing positions

Matched Filter OFI (Kang 2025)       CSI 300 OU-OFI Model (Hu & Zhang 2025)
    ↓                                       ↓
HOW to normalize OFI                  HOW to model OFI dynamics
Market-cap norm → max IC              OU+Lévy → quasi-Sharpe trigger
    ↘                                 ↙
      Together: normalize by mktcap, model with OU,
      trade when quasi-Sharpe exceeds threshold

Cross-Market Alpha191 (2026)
    ↓
Which factors from Chinese A-shares survive in efficient US market?
Factor 046 (range ratio) + 071 (24d deviation) = most universal
→ These are enhanced short-term reversal signals for Feishu daily data
```

---

## Signal Leaderboard (2026-04-10, full 484-day eval)

| Signal | Mean IC | IC Std | IR (ann.) | Hit Rate |
|--------|---------|--------|-----------|----------|
| **composite_full** (LOB+daily) | 0.0341 | **0.056** | **9.64** | **74%** |
| composite_daily | 0.0361 | 0.113 | 5.08 | 66% |
| volume_reversal | 0.0339 | 0.107 | 5.01 | 64% |
| alpha191_071 | 0.0346 | 0.197 | 2.79 | 57% |
| price_to_vwap | 0.0270 | 0.166 | 2.58 | 58% |
| lob_imbalance | 0.0045 | 0.030 | 2.40 | 59% |
| alpha191_046 | 0.0267 | 0.178 | 2.38 | 56% |
| ofi_ou | 0.0081 | 0.072 | 1.77 | 55% |
| short_term_reversal | 0.0191 | 0.165 | 1.84 | 57% |
| ofi_matched_filter | 0.0059 | 0.089 | 1.05 | 53% |

**Key finding**: LOB IC series are **negatively correlated** with daily signal IC series (r = −0.24 to −0.57).
They capture orthogonal market regimes. Combining them collapses IC_std from ~0.11 to 0.056 → IR nearly doubles.

## Open Questions / Next Steps

- [x] Check IC correlation matrix across all 5 daily signals → 5 signals = 3 clusters; see `wiki/results/ic_correlation.md`
- [x] Combine volume_reversal + alpha191_071 → composite_daily IR=5.08 (optimal: 85% vol_rev + 15% ptv)
- [x] Full LOB eval for lob_imbalance (inverted) → IC=0.0045, IR=2.40
- [x] Fit rolling OU to per-asset end-of-day OFI; compute quasi-Sharpe ratio → ofi_ou IR=1.77
- [x] Implement matched-filter OFI (market-cap normalized) → IC=0.006, IR=1.05
- [x] Test Alpha191 factor 046 and 071 on full data → IC=0.027/IR=2.38, IC=0.035/IR=2.79 (2026-04-10)
- [x] Search for papers on Chinese A-share microstructure → [[chinese-ashore-market]] written
- [x] **Walk-forward validation** (2026-04-10): OOS IR=8.29; IS-fitted worse (6.22); negative LOB/daily correlation is structural
- [x] **Regime classification** (2026-04-10): up-market IR=9.97, down-market IR=6.49; vol-regimes symmetric (7.50/8.49)
- [x] **OU half-life per asset** (2026-04-10): median HL=0.31 days — daily OFI is i.i.d.; OU dynamics are intraday only
- [x] **PCA residual signal** (2026-04-10): vol_rev IR 5.01→11.04; composite_full 7.86→12.80 vs idiosyncratic target; LOB degrades (captures systematic flow)
- [x] Fetch "Innovative Alpha Strategies for Chinese A-Share" (2025) → [[stable-turnover-momentum-2025]] — **next: implement `stable_turnover_momentum` signal**
- [x] Fetch "Factor models for Chinese A-shares" (2024) → [[factor-models-chinese-ashares-2024]] — E/P+size+market; three-factor alpha = right eval target

---

## Adding New Papers

When a new paper is added:
1. Extract full text, write structured summary to `papers/` using the same template (includes `## Implementable Signal` section)
2. Add or update concept articles with new insights/connections
3. Update `ideas/feishu-competition-signals.md` with actionable ideas (mark status: `[ ] untested`)
4. Update `learnings.md` — confirm/refute open hypotheses, or add new ones
5. Add entry to this `_index.md`
