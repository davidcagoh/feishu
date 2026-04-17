# Trading Strategy Wiki

Knowledge base for the Feishu/Lark Quant Competition. All content written and maintained by Claude. Do not edit directly.

**Last updated:** 2026-04-17  
**Papers indexed:** 17  
**Concepts:** 7  
**Ideas:** 20 signals catalogued, 10 implemented

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
| [volatility-effect-china-ashare-2021](papers/volatility-effect-china-ashare-2021.md) | The Volatility Effect in China (Blitz, Hanauer, van Vliet, 2021) | D1–D10 alpha spread 16.1% annualised; VOL factor Sharpe 0.51 vs 0.00; robust in large-cap liquid subset | High — foundational empirical support for low_vol.py; motivates longer lookback windows (120–252d vs current 60d) |
| [vol-managed-portfolios-china-2024](papers/vol-managed-portfolios-china-2024.md) | Volatility-Managed Portfolios in the Chinese Equity Market (Wang & Li, 2024) | VMP OOS Sharpe ~1.50 vs ~0.99 unmanaged; bull-market scaling via 1/σ² weights; stronger in bear/high-sentiment regimes | High — provides price-only regime-conditioning overlay for low_vol; scale exposure by inverse realised variance to improve bull-market performance |
| [us-china-cross-market-bipartite-2026](papers/us-china-cross-market-bipartite-2026.md) | A Bipartite Graph Approach to U.S.-China Cross-Market Return Forecasting (Liu, Grith, Dong, Cucuringu, Mar 2026) | US close-to-close returns predict Chinese open-to-close returns via sparse bipartite graph; asymmetry confirmed; graph selection + cross-market info both contribute | High — confirms cross-asset information (hypothesis #4); suggests intra-universe cluster-lag signals for Feishu |
| [pca-mtp2-residual-factors-2026](papers/pca-mtp2-residual-factors-2026.md) | Uncovering Residual Factors in Financial Time Series via PCA and MTP2-constrained Gaussian Graphical Models (Feb 2026) | Hierarchical PCA + MTP2-GGM yields more orthogonal residuals; higher Sharpe + lower MDD/CVaR vs PCA-only on S&P 500 and TOPIX 500 (2012–2024) | High — directly upgrades our PCA residual signal; addresses hypothesis #4; Ledoit-Wolf whitening is a practical approximation |
| [intraday-kalman-factor-china-2025](papers/intraday-kalman-factor-china-2025.md) | Intraday Factor Smoothing via Kalman Filtering and Tests of Pricing Ability: Evidence from China's A-Share Market (Xiao Wei, Dec 2025) | Kalman filter on 1-min data extracts latent efficient price; 4-day forecast → IC=0.0077, L/S Sharpe=0.58; complementary not standalone | Medium — addresses hypothesis #3 (intraday → daily factor); methodology adapts to our LOB snapshots; modest standalone IC but orthogonal to daily signals |
| [explainable-regime-aware-investing-2026](papers/explainable-regime-aware-investing-2026.md) | Explainable Regime Aware Investing (Boukardagha, Feb/Mar 2026) | Wasserstein HMM + transaction-cost-aware MV optimization; Sharpe 2.18 vs 1.59 equal-weight; MDD −5.43% vs −14.62% SPX | High — soft HMM regime overlay replaces binary vol threshold in vol_managed; directly addresses hypothesis #6 |
| [dissecting-momentum-china-2025](papers/dissecting-momentum-china-2025.md) | Dissecting Momentum in China (Liu, Tan, Xu, Yuan, Zhu, Feb 2025) | Momentum absent in China: news-day gains reversed on non-news days (retail tug-of-war); explains absence at all horizons 3–12m | High — definitively closes hypothesis #2 (intermediate momentum); confirms our focus on reversal/low-vol is correct |
| [clustering-augmented-reversal-china-2025](papers/clustering-augmented-reversal-china-2025.md) | Clustering-Augmented Reversal Strategy: Chinese Stock Market (Jiao & Zheng, Nov 2025) | K-means clustering before reversal portfolios yields 2.28–2.50%/month alpha; clustering contributes 20–45% of returns; no risk-factor loadings | High — K-means cluster-constrained low-vol selection fixes sector concentration problem; could reduce MDD on OOS |

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
| [feishu-competition-signals](ideas/feishu-competition-signals.md) | 12 alpha signal ideas, tiered by complexity; evaluation code; priority order; full-sample results |

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

US-China Bipartite Graph (2026)         PCA+MTP2 Residual Factors (2026)
    ↓                                         ↓
US overnight returns predict             PCA residuals still contain latent
Chinese open-to-close returns            common structure → MTP2-GGM whitening
    ↓                                    produces cleaner idiosyncratic signal
Cross-market graph is sparse,                 ↓
rolling, hypothesis-tested            Directly extends our pca_residual result:
    ↘                                  vol_rev IR 5.01→11.04; whitening should
      Both papers confirm:              push further
      Cross-asset info helps (hyp. #4)

Intraday Kalman Factor (2025)
    ↓
Kalman filter on LOB mid-prices → latent efficient price
4-day ahead forecast → daily factor, IC=0.0077
    ↓
Methodology adapts to our 23-24 LOB snapshots/day
Potential uplift to LOB component of composite_full

Explainable Regime Aware Investing (2026)        Dissecting Momentum in China (2025)
    ↓                                                ↓
Wasserstein HMM regime probs                 News-day vs non-news-day return split
→ soft MV overlay (not binary threshold)     → retail tug-of-war kills momentum
    ↓                                                ↓
Replaces vol_managed 3× threshold            Closes hypothesis #2: intermediate
with continuous stress-prob weight           momentum doesn't work in A-shares

Clustering-Augmented Reversal (2025)
    ↓
K-means clustering by vol/return/turnover features
→ within-cluster reversal stronger than cross-cluster
    ↓
Adapt to low_vol: select stocks across clusters
→ reduces concentration from 7→~N effective bets
```

---

## Results

| File | Contents |
|------|---------|
| [sector_concentration](results/sector_concentration.md) | low_vol portfolio concentration: 12 core holdings, 7 effective independent bets, within-cluster r=0.43 |
| [ic_correlation](results/ic_correlation.md) | IC correlation matrix across daily signals; 3 clusters identified |
| [walk_forward](results/walk_forward.md) | Walk-forward validation: OOS IR=8.29 |
| [regime_analysis](results/regime_analysis.md) | Up-market IR=9.97, down-market IR=6.49 |
| [pca_residual](results/pca_residual.md) | PCA residual signal: vol_rev IR 5.01→11.04 |
| [ou_halflife](results/ou_halflife.md) | Median OU half-life = 0.31 days — daily OFI is i.i.d. |
| [vol_managed_backtest](results/vol_managed_backtest.md) | Vol-managed overlay on low_vol: CAGR=9.04%, SR=0.981, MDD=9.38%, Score=0.3116 (+2.3% vs baseline) |

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

## Competition Mechanics (Section 7 of brief)

Score = **0.45 × CAGR_pct + 0.30 × SR_pct + 0.25 × MDD_pct**

- Evaluated on **D485–D726** (OOS, ~242 days; data released May 28, 2026; submission deadline June 1)
- Long-only portfolio, RMB 50M initial capital, min 10 stocks at end of each day
- Buy at `vwap_0930_0935`; sell at `close` (sell-at-close mode chosen for submission)
- T+1: shares bought on day t not sellable until t+1
- Costs: buy = max(turnover × 0.0001, 5); sell = max(turnover × 0.0001, 5) + turnover × 0.0005
- Lot size: 100 shares minimum
- Submission: CSV with `trade_day_id, asset_id, buy_percentage, sell_percentage`

## Critical Discovery: IC ≠ Portfolio Alpha (2026-04-10)

**All reversal/IC-based signals fail in actual portfolio construction.** Root cause:

- IC metric uses **close-to-close adjusted returns** → captures overnight gap reversal
- Execution model forces **buy at vwap_0930_0935** → AFTER the overnight gap has happened
- Result: reversal stocks that gapped up are bought at premium; then they retrace → catastrophic losses

### Execution IC (signal[t-1] → vwap[t] → open[t+1]) vs IC Metric (close-to-close):

| Signal | IC metric (cc) | Execution IC | Full backtest CAGR |
|--------|---------------|--------------|-------------------|
| composite_full (IR=9.64) | +0.034 | +0.011 | **−54%** |
| volume_reversal (IR=5.01) | +0.034 | +0.011 | **−54%** |
| lob_imbalance (IR=2.40) | +0.005 | +0.012 | tested w/ sample only |
| **low_vol 60d (NEW)** | n/a | **+0.054** | **+9.32%** (with liq filter) |
| stable_turnover_momentum | n/a | **−0.023** | **−47%** (dead) |
| low_amount_20d | n/a | +0.038 | −3.74% (dead — illiquid tail) |

Market baseline (random selection, N=20): CAGR ≈ −18% (bear market period D001–D484).

### Winner: Vol-Managed Minimum Volatility Portfolio (2026-04-11 update)

`signals/vol_managed.py` — Wang & Li (2024) overlay on low_vol: blanks signal on days where 20-day rolling market variance exceeds 3× its in-sample median. Backtest skips rebalancing on those days, holding the current low-vol portfolio.

**Best portfolio configuration (sell-at-open, N=20, D001–D484):**

| Signal | CAGR | SR | MDD | Score |
|--------|------|----|-----|-------|
| **vol_managed** (w=20, th=3.0) | **9.04%** | **0.981** | **9.38%** | **0.3116** ← new best |
| low_vol (baseline) | 8.81% | 0.961 | 9.38% | 0.3045 |

- Score improvement: +0.0071 (+2.3% relative) over low_vol baseline
- MDD unchanged — the drawdown in this dataset is structural, not vol-spike driven
- SR improvement of +0.020 is the primary driver: fewer forced rebalances on bad days

### Previous best (sell-at-close, N=100, D001–D484):
- `low_vol`: CAGR=+9.32%, SR=0.850, MDD=13.28% (reported 2026-04-10)
- Note: sell-at-close N=100 and sell-at-open N=20 are different regimes; vol_managed does not improve the N=100 configuration meaningfully.

### Liquidity filter sweep (excl_illiq, N=100, sell-at-close, D001–D484):
| excl_illiq | CAGR | SR | MDD | Score |
|---|---|---|---|---|
| 0% | +8.63% | 0.79 | 12.80% | 0.244 |
| **5%** | **+9.32%** | **0.85** | **13.28%** | **0.263** ← best (close mode) |
| 10% | +8.22% | 0.76 | 14.02% | 0.230 |
| 20% | +8.53% | 0.79 | 14.78% | 0.238 |

### Signals Tested and Failed (with Execution IC):
| Signal | Reason for failure |
|---|---|
| stable_turnover_momentum | Price/turnover stability R² is correlated with past momentum, not forward alpha; execution IC = −0.023 |
| low_amount_20d | Selects most illiquid micro-caps; individual stock blowups dominate (MDD=39.6%) |

### Infrastructure Built:
- `eval/backtest.py` — full competition-mechanics simulator (T+1, lot-size, costs, metrics)
- `signals/portfolio.py` — signal → buy/sell percentage converter
- `signals/low_vol.py` — minimum volatility signal with liquidity filter
- `signals/vol_managed.py` — Wang & Li (2024) vol-managed overlay on low_vol (**current best signal**)
- `eval/generate_submission.py` — outputs competition CSV; ready for OOS run May 28
- Repo: https://github.com/davidcagoh/feishu
- Weekly paper search trigger: `trig_0172Cps6UTTyFq5uSKY3e5UP` (Wednesdays 5pm ET)

## Remaining before June 1

1. (May 28) Run `python eval/generate_submission.py --daily data/daily_data_oos.parquet` when OOS data releases
2. Verify CSV format matches competition brief §4 exactly
3. Submit `submissions/submission_sell_close.csv`

**Optional if time permits (diminishing returns):**
- Run full-data LOB backtest for `lob_imbalance` (execution IC=+0.012, orthogonal to low_vol) — could combine for marginal uplift
- Stress-test OOS regime: low_vol underperforms in bull markets (high-beta growth stocks dominate)
- Verify sector concentration of the 100-stock portfolio (likely overweight utilities/financials)

---

## Completed Work (archived 2026-04-11)

All items below were completed during the 2026-04-10 backtest session.

**Signal evaluation (IC metric):**
- IC correlation matrix computed → 5 daily signals form 3 clusters; see `wiki/results/ic_correlation.md`
- volume_reversal + alpha191_071 combined → composite_daily IR=5.08 (optimal: 85% vol_rev + 15% ptv)
- Full LOB eval for lob_imbalance (inverted) → IC=0.0045, IR=2.40
- OU quasi-Sharpe OFI → ofi_ou IR=1.77; median OU half-life=0.31d (daily OFI is effectively i.i.d.)
- Matched-filter OFI (market-cap normalized) → IC=0.006, IR=1.05
- Alpha191 factor 046 and 071 on full data → IC=0.027/IR=2.38, IC=0.035/IR=2.79
- Walk-forward validation: OOS IR=8.29; IS-fitted worse (6.22); LOB/daily negative correlation is structural
- Regime classification: up-market IR=9.97, down-market IR=6.49; vol-regimes symmetric (7.50/8.49)
- PCA residual signal: vol_rev IR 5.01→11.04 vs idiosyncratic target; LOB degrades (captures systematic flow)
- stable_turnover_momentum: implemented from Zhang et al. 2025; execution IC=−0.023, CAGR=−47% (failed)
- low_amount_20d: execution IC=+0.038 but CAGR=−3.74%, MDD=39.6% (selects illiquid micro-caps — wrong direction)
- Sector/cluster concentration (2026-04-11): 12 core holdings (>80% of days), 7 effective bets, mean pairwise r=0.33

**Portfolio construction:**
- Portfolio backtester built: `eval/backtest.py` with exact competition mechanics
- Critical discovery: IC-based signals fail in execution (reversal alpha is overnight gap, bought AFTER gap)
- Minimum volatility strategy: `signals/low_vol.py`, 60-day window, N=100, sell-at-close → CAGR=+9.32%, SR=0.85
- Liquidity filter sweep: 5% exclusion is optimal (CAGR=+9.32% vs 8.63% without)
- Submission generator: `eval/generate_submission.py` ready for OOS run May 28

**Research (papers + concepts):**
- Chinese A-share microstructure surveyed → `concepts/chinese-ashore-market.md`
- "Innovative Alpha Strategies for Chinese A-Share" (2025) indexed → `papers/stable-turnover-momentum-2025.md`
- "Factor Models for Chinese A-Shares" (2024) indexed → `papers/factor-models-chinese-ashares-2024.md`

---

## Adding New Papers

When a new paper is added:
1. Extract full text, write structured summary to `papers/` using the same template (includes `## Implementable Signal` section)
2. Add or update concept articles with new insights/connections
3. Update `ideas/feishu-competition-signals.md` with actionable ideas (mark status: `[ ] untested`)
4. Update `learnings.md` — confirm/refute open hypotheses, or add new ones
5. Add entry to this `_index.md`
