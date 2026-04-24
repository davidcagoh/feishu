# Trading Strategy Wiki

Knowledge base for the Feishu/Lark Quant Competition. All content written and maintained by Claude. Do not edit directly.

**Last updated:** 2026-04-24  
**Papers indexed:** 20  
**Concepts:** 7  
**Ideas:** 28 signals catalogued, 23 implemented  
**Current best:** `trend_vol_v4` Score=0.4024 (CAGR=11.75%, SR=1.207, MDD=7.98%)

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
| [factoring-low-volatility-factor-2025](papers/factoring-low-volatility-factor-2025.md) | Factoring in the Low-Volatility Factor (Soebhag, Baltussen, van Vliet, Jun 2025) | Long leg of low-vol generates genuine alpha (survives costs); short leg does not — asymmetry explains why factor is missing from standard models; Sharpe improves 13–17% | High — validates our long-only approach as the correct implementation; bull-market lag is real but manageable via N expansion |
| [dynamic-factor-allocation-regime-sjm-2025](papers/dynamic-factor-allocation-regime-sjm-2025.md) | Dynamic Factor Allocation Leveraging Regime-Switching Signals (Shu & Mulvey, JPM 2025) | Sparse Jump Model detects factor-specific bull/bear regimes; IR 0.05→0.4 for long-only multi-factor portfolio; low-vol explicitly one of 7 factors | High — direct blueprint for adaptive N expansion in OOS bull regime; addresses Priority 4 (regime detection) and Priority 1 |
| [adaptive-minimum-variance-arfima-figarch-2025](papers/adaptive-minimum-variance-arfima-figarch-2025.md) | Adaptive Minimum-Variance Portfolios via ARFIMA-FIGARCH (Jha, Shirvani, Rachev, Fabozzi, Jan 2025) | FIGARCH adaptive covariance reduces drawdowns during regime transitions vs. fixed rolling window; tested on equity and crypto | Medium — adaptive vol window (short in high-vol, long in calm) as drop-in improvement to low_vol.py; addresses Priority 2 (MDD reduction) |

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

## Introductory Course

Six-article series for non-finance readers. Covers the full arc from market basics → signal research → execution failure → what actually works → AI-assisted ideation and its limits.

| # | File | Summary |
|---|------|---------|
| 1 | [course/01-what-is-the-stock-market](course/01-what-is-the-stock-market.md) | Shares, OHLCV data, order book |
| 2 | [course/02-the-alpha-hunt](course/02-the-alpha-hunt.md) | What quants do; IC/IR; competition rules |
| 3 | [course/03-signals-we-built](course/03-signals-we-built.md) | 10+ signals from academic papers |
| 4 | [course/04-when-smart-strategies-fail](course/04-when-smart-strategies-fail.md) | IR 9.64 → CAGR −54%: the execution gap |
| 5 | [course/05-what-actually-works](course/05-what-actually-works.md) | Low-vol + trend filter + ERC: Score=0.3981 |
| 6 | [course/06-on-clean-slates](course/06-on-clean-slates.md) | AI as a research partner; context as constraint |

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
| [vol_managed_backtest](results/vol_managed_backtest.md) | Vol-managed overlay on low_vol: CAGR=9.04%, SR=0.981, MDD=9.38%, Score=0.3116 |
| [strategy_gaps](results/strategy_gaps.png) | Weakness analysis dashboard: equity curve, drawdown, score sensitivity, gap descriptions, regime scenarios |
| [strategy_presentation](results/strategy_presentation.png) | One-shot presentation anchor: competition goal, strategy pipeline, key metrics — David Goh |

**Archived (IC era — superseded):** `wiki/archive/` contains ic_correlation, pca_residual, ou_halflife, walk_forward, regime_analysis. All computed using IC/IR metric; do not use for portfolio decisions.

---

## IC Signal Leaderboard (archived — IC does not predict portfolio alpha)

> Full IC/IR results archived in `wiki/archive/ic_correlation.md`. IC metrics use close-to-close returns;
> execution buys at vwap_0930_0935 *after* the overnight gap has closed. All reversal signals fail in
> backtesting (CAGR ≈ −54%). See "Critical Discovery" section below. Do not build IC-based signals.


## Portfolio Backtest Leaderboard (2026-04-21, D001–D484, N=20, sell-at-open)

> IC metrics are misleading (close-to-close returns ≠ execution IC). Portfolio backtest is ground truth.

| Signal | CAGR | SR | MDD | Score | Notes |
|--------|------|----|-----|-------|-------|
| ★ **trend_vol_v4** ← **SUBMISSION** | **11.75%** | **1.207** | **7.98%** | **0.4024** | thresh=-0.025, ERC, N=20 |
| trend_vol_v3 | 12.55% | 1.231 | 11.04% | 0.3981 | thresh=0.00, ERC, N=20 |
| trend_vol_v2 | 12.29% | 1.202 | 11.21% | 0.3877 | thresh=0.00, equal weight |
| vol_managed_v2 (prior best) | 9.64% | 1.032 | 9.38% | 0.3296 | w=30, σ=2.0 |
| trend_filtered_low_vol | 11.07% | 1.097 | 11.21% | 0.3507 | tw=20 |
| erc_vol_managed | 9.54% | 1.024 | 9.30% | 0.3268 | 1/σ weights, same selection |
| vol_managed (prior) | 9.04% | 0.981 | 9.38% | 0.3116 | w=20, σ=3.0 |
| low_vol (N=20) | 8.81% | 0.961 | 9.38% | 0.3045 | baseline |
| hmm_regime_vol | 8.48% | 0.923 | 8.56% | 0.2937 | HMM over-blanks |
| vol_managed_120d | 8.03% | 0.904 | 11.23% | 0.2792 | 120d window too slow |
| cluster_low_vol | 5.18% | 0.441 | 10.76% | 0.1286 | K-means churn kills returns |
| quality_composite | 4.06% | 0.342 | 24.08% | 0.0606 | -vol+hit+(-beta) contaminated by momentum |
| low_vol (N=100, sell-close) | 9.32% | 0.850 | 13.30% | 0.2636 | original baseline |
| low_beta | −16.1% | −0.994 | 39.15% | −0.469 | hidden momentum → reversal |
| return_consistency | −28.7% | −1.408 | 52.63% | −0.683 | hit rate = momentum → reversal |
| rolling_sharpe | −42.2% | −1.725 | 67.95% | −0.877 | same problem |

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

### Winner: Trend-Vol v4 (2026-04-21, softened threshold)

`signals/trend_vol_v4.py` — same ERC weights as trend_vol_v3, but softened trend threshold from `> 0.00` to `> -0.025`. Allows stocks flat-to-slightly-down over 35 days into the eligible set; more candidates on bear-market days → better diversification → much lower MDD.

**Threshold sweep (ERC weights, N=20, D001–D484):**

| Threshold | CAGR | SR | MDD | Score |
|-----------|------|----|-----|-------|
| ★ **-0.025** | **11.75%** | **1.207** | **7.98%** | **0.4024** ← new best |
| -0.027 | 11.79% | 1.197 | 8.00% | 0.4050 |
| -0.030 | 11.82% | 1.252 | 7.97% | 0.4079 |
| **0.000 (trend_vol_v3)** | 12.55% | 1.231 | 11.04% | 0.3981 |
| -0.040 | 11.71% | 1.236 | 8.18% | 0.4075 |

Note: -0.030 is a local spike in equal-weight space (neighbours much lower); -0.025 chosen as most conservative improvement that clearly beats trend_vol_v3. The MDD improvement from ~11% to ~8% is robust across the entire -0.020 to -0.040 range — mechanism is clear: more eligible stocks on bear days → better diversification.

**Prior best portfolio configurations (sell-at-open, N=20, D001–D484):**

| Signal | CAGR | SR | MDD | Score |
|--------|------|----|-----|-------|
| trend_vol_v3 (thresh=0.00, ERC, N=20) | 12.55% | 1.231 | 11.04% | 0.3981 |
| trend_vol_v2 (thresh=0.00, equal, N=20) | 12.29% | 1.202 | 11.21% | 0.3877 |
| trend_vol_v2 (thresh=0.00, equal, N=18) | 12.25% | 1.214 | 10.30% | 0.3936 |
| vol_managed_v2 (prior best) | 9.64% | 1.032 | 9.38% | 0.3296 |
| low_vol (baseline) | 8.81% | 0.961 | 9.38% | 0.3045 |

**Other experiments from 2026-04-21 (failed):**
- counter_trend_low_vol (pullback -15% to -3%): Score=-0.1563, MDD=21.37% — quiet-pullback stocks keep declining in bear market IS period; execution gap avoided but direction wrong
- 50/50 blend trend_vol_v3 + counter_trend: Score=0.2475 — counter_trend drags the blend; correlation 0.51 too high for diversification benefit

**Max drawdown anatomy (trend_vol_v3, to correct prior wrong claim):**
- MDD peak: D265 (54.6% through IS), trough: D367 (75.7% through IS), duration 102 days
- Warmup window is D000–D035 only; the MDD is a mid-period sustained bear episode, not a warmup artifact

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
- `eval/backtest.py` — full competition-mechanics simulator (T+1, lot-size, costs, metrics); supports optional `weights=` param for custom allocation
- `signals/portfolio.py` — signal → buy/sell percentage converter
- `signals/low_vol.py` — minimum volatility signal with liquidity filter
- `signals/vol_managed.py` — Wang & Li (2024) vol-managed overlay on low_vol
- `signals/vol_managed_v2.py` — tuned vol_managed (w=30, σ=2.0)
- `signals/trend_vol_v3.py` — threshold=0.00, ERC weights (prior best, Score=0.3981)
- `signals/trend_vol_v4.py` — threshold=-0.025, ERC weights (current best, Score=0.4024)
- `signals/counter_trend_low_vol.py` — quiet-pullback variant (failed, Score=-0.1563)
- `signals/inv_var_vol.py` — 1/σ² allocation on vol_managed selection (no improvement)
- `signals/cluster_low_vol.py` — K-means cluster-constrained selection (failed)
- `signals/hmm_regime_vol.py` — HMM soft regime scaling (failed; too conservative)
- `signals/vol_managed_120d.py` — 120d base window variant (failed; too slow)
- `eval/generate_submission.py` — outputs competition CSV; needs update to use trend_vol_v4 before May 28
- `wiki/results/strategy_overview.png` — comprehensive dashboard of all signal backtests
- Repo: https://github.com/davidcagoh/feishu
- Weekly paper search trigger: `trig_0172Cps6UTTyFq5uSKY3e5UP` (Wednesdays 5pm ET)

## Remaining before June 1

1. ~~Update `eval/generate_submission.py` to use `trend_vol_v4`~~ — Done (2026-04-22)
2. (May 28) Run when OOS data releases:
   ```bash
   python eval/generate_submission.py \
       --daily data/daily_data_oos.parquet \
       --sell-mode open --n-stocks 20 \
       --output submissions/submission_v4_trend_vol.csv
   ```
3. Verify CSV format matches competition brief §4 exactly
4. Submit `submissions/submission_v4_trend_vol.csv`
5. Backup: `trend_vol_v3` (Score=0.3981) if v4 raises any concerns

**Optional if time permits:**
- Investigate why the 35d trend window helps: how many stocks are filtered out on an average day? Does it vary by market regime?
- ~~Test trend_vol_v2 with ERC weights~~ — Done (trend_vol_v3, Score=0.3981)
- ~~Consider MDD=11.21% vs vol_managed_v2~~ — Resolved: trend_vol_v4 achieves MDD=7.98% (Score=0.4024)

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
