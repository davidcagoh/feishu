# Trading Strategy Wiki

Knowledge base for the Feishu/Lark Quant Competition. All content written and maintained by Claude. Do not edit directly.

**Last updated:** 2026-04-08  
**Papers indexed:** 4  
**Concepts:** 7  
**Ideas:** 9 signals catalogued

---

## Papers

| File | Title | Key Result | Relevance |
|------|-------|-----------|-----------|
| [attention-factors-stat-arb](papers/attention-factors-stat-arb.md) | Attention Factors for Statistical Arbitrage (Epstein et al., ICAIF 2025) | Sharpe 2.3 net via joint factor+trading end-to-end model; weak factors matter | High — factor residual framework, directly maps to Feishu daily data |
| [drl-optimal-trading-partial-info](papers/drl-optimal-trading-partial-info.md) | Deep RL for Optimal Trading with Partial Information (Macrì, Jaimungal, Lillo, 2025) | prob-DDPG (regime probs as input) dominates; quality of info > architecture | High — OU signal model, regime conditioning, applies to LOB imbalance |
| [jump-start-control-scientist](papers/jump-start-control-scientist.md) | A Jump Start to Stock Trading Research (Barmish et al., CDC 2024) | Tutorial: LOB structure, Kelly betting, feedback control framing | Medium — foundational; LOB section directly relevant to Feishu data |
| [ai-asset-pricing-models](papers/ai-asset-pricing-models.md) | Artificial Intelligence Asset Pricing Models (Kelly et al., Dec 2024) | Nonlinear portfolio transformer achieves Sharpe 4.6 via cross-asset attention | Medium — requires characteristics; adaptable with price-based features |

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
```

---

## Open Questions / Next Steps

- [ ] Run IC/IR evaluation of LOB imbalance signal on `data/lob_sample.parquet`
- [ ] Test short-term reversal IC on `data/daily_sample.parquet`
- [ ] Estimate OU half-life of LOB imbalance per asset
- [ ] Classify days into regimes (vol-based or HMM) and test regime-conditional IC
- [ ] Evaluate whether PCA residual signal improves over raw return signal
- [x] Search for papers on Chinese A-share microstructure → [[chinese-ashore-market]] written
- [ ] Fetch and read "Innovative Alpha Strategies for Chinese A-Share" (2025) — stable turnover momentum paper
- [ ] Fetch "Factor models for Chinese A-shares" (Int'l Review of Financial Analysis, 2024)

---

## Adding New Papers

When a new paper is added:
1. Extract full text, write structured summary to `papers/` using the same template
2. Add or update concept articles with new insights/connections
3. Update the `ideas/feishu-competition-signals.md` with actionable ideas
4. Add entry to this `_index.md`
