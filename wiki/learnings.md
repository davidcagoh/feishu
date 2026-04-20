# What We've Learned

Running log of findings from experiments. Each entry is either a **confirmed fact**, an **open hypothesis**, or something **ruled out**. The open hypotheses drive what we look for next — in papers and in experiments.

---

## Confirmed Facts

### Mean-reversion dominates A-shares at daily frequency
All 5 daily signals are positive. IC range 0.019–0.035. This is consistent with the Chinese A-share literature: heavy retail participation → short-term overreaction → reliable next-day reversal. It is not a data artefact.

### Volume is a more stable predictor than price
`volume_reversal` (IC std 0.107) is substantially more day-to-day consistent than all price-based signals (IC std 0.165–0.197). This is likely because volume spikes are discrete, rare events — they mark a specific behavioural moment. Price deviations from a moving average or range are more continuous and noisy.
- **Implication:** when designing new signals, prefer signals that condition on discrete events or threshold crossings over smooth continuous measures.

### EOD LOB imbalance is contrarian, not momentum
Raw imbalance IC = −0.005, IR = −2.40 over 484 days. After inversion: small positive IC (~+0.006). Chinese retail investors pile into bids at end of day (FOMO / closing auction effect) — this is a crowded retail signal that predicts *against* itself. Post-inversion IC is weak, suggesting the contrarian effect is also noisy and may not be consistently exploitable alone.

### T+1 settlement + 10% price limits create specific dynamics
Stocks that hit the ±10% limit are uninvestable (we mask them as NaN). T+1 means retail can't daytrade on the same day, concentrating their activity into next-day opening — this amplifies opening-auction reversal signals.

---

## Open Hypotheses

These are the things we don't know yet, ranked roughly by how much they'd change what we do.

### 1. Are our 5 daily signals actually catching the same thing?
We haven't computed the IC cross-correlation matrix. If `volume_reversal`, `price_to_vwap`, `alpha191_046`, `alpha191_071`, and `short_term_reversal` are all highly correlated (>0.6), combining them won't help — they're all proxies for the same retail overreaction. If some pairs are <0.3, a composite could push IR meaningfully above 5.
- **Test:** compute pairwise IC correlation across 484 days. Do this before building any composite.
- **Search:** papers on signal combination under high IC correlation.

### 2. Does intermediate-horizon momentum exist here?
We've only built reversal signals (1–24 day lookbacks). Most markets show 1-month reversal *and* 12-month momentum. We haven't tested any momentum side. If Chinese A-shares have 3–12 month momentum (e.g. earnings surprise drift, which works even in retail-heavy markets), we're leaving an orthogonal source of IC on the table.
- **Test:** build a simple 3-month or 6-month momentum signal and check IC. Expectation is low or negative given strong reversal, but worth verifying.
- **Search:** Chinese A-share intermediate-horizon momentum, earnings momentum, post-earnings drift.

### 3. Does the LOB signal vary intraday? (Morning momentum vs afternoon reversal)
The EOD contrarian finding is about retail closing pressure. But institutions trade heavily in the morning session. The LOB signal computed on morning snapshots only (09:40–12:00) may behave differently — possibly momentum, not contrarian.
- **Test:** split LOB snapshots into morning (09:40–12:00) and afternoon (13:00–15:00), compute IC separately.
- **Paper evidence (2025-12):** Wei (2025, SSRN:5859882) applies a Kalman filter state-space model to 1-minute Chinese A-share data and extracts a latent "efficient price" signal with IC=0.0077. The paper confirms that full-trajectory intraday information improves on EOD snapshots, though IC is modest standalone. Methodology adapts to our 23-24 LOB snapshots. See signal idea #17.
- **Status:** Partially addressed by paper evidence; experiment (morning vs afternoon IC split) still open.

### 4. Does cross-asset information help?
All current signals are purely within-asset (each asset's own price/volume history). The attention factors paper shows that factor residuals — what's left after removing market-wide PCA factors — are more predictable than raw returns. We have now tested basic PCA residuals (vol_rev IR 5.01→11.04) and found strong improvement.
- **PCA residuals confirmed (2026-04-10):** Rolling K=5–10 PCA, residual z-score → vol_rev IR 5.01→11.04 (see `wiki/results/pca_residual.md`). LOB degrades in PCA residual space (captures systematic flow).
- **New paper evidence — cross-market bipartite (2026-03):** Liu et al. (arXiv:2603.10559) confirm that US overnight returns predict Chinese open-to-close returns via a sparse directed bipartite graph. Within our dataset, the analogous test is cluster-lagged returns (see signal #18).
- **New paper evidence — MTP2-GGM whitening (2026-02):** arXiv:2602.05580 shows that PCA residuals still contain latent common structure. Applying MTP2-constrained GGM whitening produces more orthogonal residuals with higher Sharpe ratios and lower CVaR on S&P 500 / TOPIX 500. This directly extends our pca_residual result — see signal #16 (Ledoit-Wolf whitening as practical approximation).
- **Revised status:** Partially confirmed (PCA residuals help). Whether additional MTP2 whitening improves further is an open experiment.

### 5. Why does volume_reversal decay less? Does it saturate on quiet days?
The low IC std of `volume_reversal` is great for IR, but there's a potential downside: on days when volume is normal (no spike), the signal is near-zero — it only fires when there's genuine excess volume. This could mean it covers fewer assets per day, and its capacity is limited.
- **Test:** on days where the top decile of the signal is flat (low signal dispersion), what's the IC? Does the signal concentrate its predictive power on fewer stocks?
- **Search:** volume-based alpha signals, capacity constraints in mean-reversion strategies.

### 6. Is there regime dependence in signal quality?
Signal IC likely varies with market conditions. In high-volatility regimes (e.g. market-wide stress), reversal may be stronger or weaker. The DRL paper shows regime-conditioning significantly improves OU-based strategies.
- **Test:** split days by cross-sectional return std (proxy for market vol). Compute IC of `volume_reversal` and `alpha191_071` per tercile.
- **New paper evidence — Wasserstein HMM (2026-02/03):** Boukardagha (arXiv:2603.04441) shows that a strictly causal Wasserstein HMM feeding regime probabilities into a transaction-cost-aware MV optimiser achieves Sharpe 2.18 vs 1.59 equal-weight, MDD −5.43% vs −14.62% SPX. The key insight is that soft (probabilistic) regime conditioning outperforms both binary thresholds and hard regime-switching. Regime inference stability (not just detection accuracy) is the first-order driver of drawdown reduction.
- **Revised status:** Partially addressed by paper evidence. Concrete next step: replace vol_managed's binary 3×-median threshold with a 2-state Wasserstein HMM stress probability (Signal #19). Still open: whether signal IC itself varies with regime (vs. just the portfolio sizing).

### Any selection signal with a hidden momentum component fails catastrophically (2026-04-20)
Full battery test of 6 new paradigms: `low_beta` (Score=−0.469), `return_consistency` (−0.683), `rolling_sharpe` (−0.877), `quality_composite` (0.061, contaminated by first two), all failed.
- Root cause: every signal that rewards "recent positive performance" has a hidden momentum bias. In Chinese A-shares with T+1 and retail dominance, momentum reverts. Buying at vwap_0930_0935 the day after a stock had high hit-rate / high Sharpe / low beta makes you a bag-holder for the reversal.
- **Rule**: any signal that would select stocks that recently went up is forbidden. Only direction-agnostic signals survive (low_vol, trend-filter as a negative screen, vol-blanking).
- `trend_vol_v2` works because the trend filter is a *negative screen* (remove declining stocks) not a *positive screen* (select recent winners). The low-vol selection does the actual picking; the trend filter only prunes.

### IC/IR metrics do not predict portfolio performance — execution gap is the root cause
**All IC-based reversal signals fail in actual portfolio construction.** Buy execution at `vwap_0930_0935` happens *after* the overnight gap has closed. Reversal alpha is earned close-to-open; by buy time the opportunity is gone. Improving IC (better signal decomposition, PCA whitening, LOB Kalman) does not fix this — it's a structural execution gap, not a signal quality problem.
- Confirmed 2026-04-10: composite_full (IR=9.64) → CAGR=−54%; volume_reversal (IR=5.01) → CAGR=−54%.
- **Implication:** IC/IR is a dead-end for this competition. Do not pursue reversal signal improvements.

### Minimum volatility (low_vol) is the only viable portfolio strategy found
`signals/low_vol.py` (60d rolling std, 5% illiquid exclusion, N=20, sell-at-open) beats the market and all IC-based signals. Baseline: CAGR=+8.81%, SR=0.961, MDD=9.38%, Score=0.3045.
- Mechanism: avoids limit-down spirals and sector blowups in the IS bear-market period. Low turnover → low cost drag.
- Vol-managed overlay (Wang & Li 2024) adds +0.0071 Score by skipping rebalance on top-5% variance days.

### trend_vol_v3 is the current best strategy (2026-04-20)
`signals/trend_vol_v3.py` — trend_vol_v2 selection (low-vol + 35d trend filter + vol-blanking) with 1/σ ERC allocation weights.
- CAGR=12.55%, SR=1.231, MDD=11.04%, Score=**0.3981** — +20.8% over vol_managed_v2.
- Selection mechanism (trend_vol_v2 base): removes "quiet decliners" from the low-vol universe. The 35d trend filter keeps only stocks that are at least holding their price level. Trend_window=35 chosen as robust plateau (30–40d range all beat vol_managed_v2; IS-peak at 37d excluded as noise spike).
- ERC weighting: 1/σᵢ allocation concentrates capital in the quietest holdings within the already-filtered universe. Adds +2.7% relative Score vs equal weight.
- N=20 optimal (N-sweep confirmed; equal-weight N=18 also competitive at Score=0.3936).
- MDD 9.38%→11.04%: trend filter reduces eligible universe on bear-market days → less diversification.

### vol_managed_v2 is the current best strategy (2026-04-18)
`signals/vol_managed_v2.py` — same mechanism as vol_managed but with overlay_window=30 (vs 20) and sigma_threshold=2.0 (vs 3.0), found via exhaustive 50+ combination grid search.
- CAGR=9.64%, SR=1.032, MDD=9.38%, Score=**0.3296** — first SR > 1.0.
- Score improvement: +0.0251 (+8.2%) over baseline low_vol; +0.0180 (+5.8%) over prior best vol_managed.
- Key insight: window=30 produces fewer spurious blanks during mild up-vol periods → more good rebalance days.
- MDD=9.38% is unchanged and structural (see below).

### vol-filter window is the most important overlay parameter; sigma threshold matters less
- window=30 (vs 20): larger rolling window → more stable market-vol estimate → fewer false-positive blanking triggers.
- sigma_threshold=2.0 blanks ~12% of high-vol days vs ~5% at σ=3.0. The higher blanking rate is net positive because the 30d estimate accurately identifies genuine stress.
- Longer windows (≥35) start degrading SR slightly; shorter windows (≤5) degrade MDD.

### All 4 PR signals (inv_var_vol, cluster_low_vol, hmm_regime_vol, vol_managed_120d) failed (2026-04-18)
- `inv_var_vol`: 1/σ² allocation weighting — Score=0.3113 (≈ baseline). Low-vol stocks are too homogeneous for variance-based weights to differentiate.
- `cluster_low_vol`: K-means cluster-constrained selection (K=10, 2/cluster) — Score=0.1286. K-means forces picks from weak clusters; high churn (5,686 trades vs ~1,000 for vol_managed).
- `hmm_regime_vol`: 2-state HMM soft regime scaling — Score=0.2937. Over-blanks: too conservative in detecting "normal" days, loses too much CAGR.
- `vol_managed_120d`: 120d base window — Score=0.2792. Too slow; introduces stale rankings, higher MDD=11.23%.

### 60-day lookback is optimal; longer windows (120–252d) collapse returns
Full sweep (2026-04-17, N=20, sell-at-open): the vol effect literature recommends 120–252d lookbacks, but on D001–D484 they are catastrophically worse. Score at 180d = 0.054, at 252d = −0.023. The IS period is only 484 days with concentrated bear-regime structure — a long lookback window captures stale cross-sectional vol rankings that no longer reflect current risk.

### Sell-at-open dominates sell-at-close for the N=20 vol_managed configuration
At N=20: sell-at-open Score=0.3116 vs sell-at-close Score=0.2826. Sell-at-open captures the post-overnight-gap open price, which for low-vol defensive stocks is more favourable (less adverse selection).

---

## Ruled Out

### LOB imbalance as a direct momentum signal
Raw IC is reliably negative over the full 484-day period. This isn't a small-sample artefact — it's consistent with the known retail FOMO mechanism in A-shares. We shouldn't keep re-testing this direction.

### Intermediate-horizon price momentum in Chinese A-shares (hypothesis #2, closed 2026-04-17)
Liu et al. (SSRN:5130681, Feb 2025) provides a definitive mechanism: Chinese stocks with high past news-day returns are reversed on subsequent non-news days, creating a "tug-of-war" that kills 3–12 month momentum. This is retail-driven (crowding on news events, unwinding on quiet days) and is not present in the US market. Without earnings/news calendar data (unavailable in Feishu), there is no feasible path to isolate the exploitable news-day component. **Do not pursue intermediate-horizon momentum signals.**

---

## What the Next Experiments Should Prioritise

Updated 2026-04-20. Current best: `trend_vol_v2` Score=0.3877. IC-era experiments are all complete or archived.

1. **N-sweep on trend_vol_v2** — The trend filter narrows the eligible universe on down-trending days. N=20 was confirmed optimal for vol_managed_v2 but should be re-confirmed with the trend filter active. Try N=10, 15, 20, 25, 30. Cheap, ~20 min.

2. **ERC weights on trend_vol_v2** — `erc_vol_managed` on `vol_managed_v2` base underperformed slightly (0.3268 vs 0.3296), but the trend filter changes portfolio composition. With a narrower, more homogeneous universe after filtering, ERC might behave differently. Combine `trend_vol_v2.compute()` with `erc_vol_managed.compute_weights()`. Cheap, ~10 min.

3. **Soften the trend threshold** — currently `trend > 0` (strictly positive 35d return). Try `trend > -0.03` (allow up to −3% drift). In deep bear-market periods many low-vol stocks fail the strict threshold → portfolio narrows → MDD rises. A softer threshold might recover diversification on bad days. Tests the 11.21% MDD penalty.

4. **Nothing else** — the main space (lookback, vol overlay, trend window, N, weighting) is exhausted. Further tuning is overfitting. The remaining OOS risk is structural (bear IS vs unknown OOS regime), not tunable from IS data.

---

## What the Next Paper Search Should Prioritise

Updated 2026-04-20. **Current best:** `trend_vol_v2` (Score=0.3877). IS parameter space is exhausted — further gains require structural improvements or OOS regime insight.

**Papers added this week (2026-04-17):**
- arXiv:2603.04441 (Wasserstein HMM regime investing) — regime detection for low-vol portfolio, Priority 4
- SSRN:5130681 (Dissecting Momentum in China) — closes hypothesis #2; confirms reversal-only focus
- Pacific-Basin Finance Journal (Clustering-Augmented Reversal, Nov 2025) — K-means diversification for low_vol, Priority 3

**Do NOT search for:**
- LOB imbalance signals, order flow, microstructure — IC-based, execution gap makes them useless
- Statistical arbitrage, mean-reversion signal construction
- PCA residuals, Kalman filters on LOB data — same problem

**Priority 1 — Bull-market resilience (HIGHEST IMPACT)**
Our biggest OOS risk: D485–D726 could be a bull market where low-vol dramatically underperforms. Search for:
- Low-volatility anomaly behaviour in bull vs bear markets (Chinese A-shares specifically)
- Adaptive minimum-variance portfolios that incorporate regime signals
- Methods for blending defensive and growth exposure based on market-wide signals
- Papers on low-vol strategy OOS degradation and how to mitigate it

**Fixed income analogy (Lec 02):** Our low_vol portfolio = "long duration" in equity terms. v₁ (parallel shift) in bonds = market beta in equity; both strategies earn a risk premium by being exposed to this factor. Duration management in fixed income (dynamic hedging of v₁ exposure) is the direct analogue of what we need: regime-conditional beta management. Key constraint: full hedging requires shorts (unavailable). Partial fix: in detected bull regime, expand N or relax volatility screen to include slightly higher-beta stocks. See [[factor-models]] for full analogy and Orange County warning (hedging one factor while concentrating in another).

**Priority 2 — MDD reduction in long-only portfolios**
MDD=11.21% with trend_vol_v2 (rose from 9.38% when trend filter narrows universe on down days). Search for:
- Drawdown control in long-only equity portfolios (position sizing, stop-loss overlays, tail-risk hedging)
- Portfolio insurance for long-only constraint (no leverage, no shorts)
- Maximum drawdown minimisation as a portfolio objective (not just variance)

**Priority 3 — Stock selection within the low-vol universe**
Are there characteristics that improve returns *within* a minimum-volatility stock screen? Search for:
- Quality factors (profitability, earnings stability) combined with low-volatility in Chinese equities
- Sector-neutral minimum variance construction — does forcing sector balance improve OOS Sharpe?
- Liquidity-adjusted low-vol: are there better illiquidity screens than 20d avg amount?

**Priority 4 — Regime detection without price data**
Can we detect whether OOS period is bull or bear *before* it happens, using macro signals available in the competition data? Search for:
- Market state classification from cross-sectional return dispersion or vol level
- Regime-switching overlays on low-vol strategies (not HMM on IC — HMM on portfolio-level signals)
- Breadth indicators (% of stocks above moving average) as regime proxies
